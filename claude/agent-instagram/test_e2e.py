"""Bout en bout : fiche Shopify réelle -> légende -> contrôle -> note d'accroche -> détecteur ;
instantané -> audit. Les appels Shopify sont en lecture seule et sautés sans jeton."""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

import audit
import controle
import logements

HERE = os.path.dirname(os.path.abspath(__file__))
HANDLE = "escale-spa-dinard"
LIVE = bool(os.environ.get("SHOPIFY_API_TOKEN"))


def legende_depuis(f):
    """Légende minimale construite uniquement avec les faits de la fiche (aucun fait ajouté)."""
    nom = f["nom"].split(" - ")[0]
    lieu = f["ville_reference"] or f["ville"]
    equip = " et ".join([e.lower() for e in f["equipements"] if e in ("Sauna", "Spa", "Cheminée", "Hammam")][:2])
    return (f"{equip.capitalize()} près de {lieu} : {nom}, dès {f['prix_a_partir_de']:g} € la nuit.\n\n"
            f"Un {f['type'].lower()} à {f['ville']}, en {f['region']}. On aime : {f['on_aime'] or 'le calme'}.\n\n"
            f"Le soir, vous avez le {equip} pour vous seuls, sans horaire et sans voisins. "
            f"Le matin, personne ne vous attend : vous partez quand vous voulez.\n\n"
            f"Enregistrez ce post pour votre prochain week-end à deux.\n\n"
            f"#lovenspa #weekendamoureux #spaprivatif")


@unittest.skipUnless(LIVE, "SHOPIFY_API_TOKEN absent")
class TestCaptionPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fiche = logements.Shop().logement(HANDLE)
        cls.text = legende_depuis(cls.fiche)

    def test_fiche_live(self):
        self.assertTrue(self.fiche["actif"])
        self.assertIsNotNone(self.fiche["prix_a_partir_de"])

    def test_controle_live_not_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "l.txt")
            with open(p, "w", encoding="utf-8") as h:
                h.write(self.text)
            with redirect_stdout(io.StringIO()) as out:
                code = controle.main([p, "--logement", HANDLE,
                                      "--historique", os.path.join(HERE, "data", "baseline-public-2026-11-11.json")])
        self.assertIn(code, (0, 1), out.getvalue())

    def test_altered_price_refused(self):
        r = controle.check(self.text.replace(f"{self.fiche['prix_a_partir_de']:g}", "99"), self.fiche)
        self.assertEqual(r["statut"], "REFUSE")

    def test_vendor_tools_run_isolated(self):
        with tempfile.TemporaryDirectory() as d:
            hooks, cap = os.path.join(d, "h.txt"), os.path.join(d, "c.txt")
            with open(hooks, "w", encoding="utf-8") as h:
                h.write(self.text.split("\n")[0] + "\nParfois il suffit d'une nuit\n")
            with open(cap, "w", encoding="utf-8") as h:
                h.write(self.text)
            for args in (["vendor/score_hook.py", hooks], ["vendor/detecter.py", cap]):
                r = subprocess.run([sys.executable, "-I", *args], cwd=HERE, capture_output=True, text=True)
                self.assertIn(r.returncode, (0, 1), r.stderr)
                self.assertTrue(r.stdout.strip())


class TestAuditPipeline(unittest.TestCase):
    def test_snapshot_to_report(self):
        posts = [{"id": str(i), "timestamp": f"2026-10-{i:02d}T10:00:00+0000", "media_type": "IMAGE",
                  "media_product_type": "REELS" if i % 3 == 0 else "FEED", "caption": f"Post {i}",
                  "permalink": f"https://instagram.com/p/{i}",
                  "insights": {"views": 100 * i, "reach": 80 * i, "shares": i % 4, "saved": i % 5}}
                 for i in range(1, 22)]
        with tempfile.TemporaryDirectory() as d:
            src, md = os.path.join(d, "s.json"), os.path.join(d, "a.md")
            with open(src, "w", encoding="utf-8") as h:
                json.dump({"profil": {}, "publications": posts}, h)
            self.assertEqual(audit.main([src, "--par-format", "--depuis", "2026-10-05", "--md", md]), 0)
            with open(md, encoding="utf-8") as h:
                text = h.read()
        self.assertIn("Périmètre : 17 publications depuis le 2026-10-05", text)
        self.assertIn("| REELS |", text)


if __name__ == "__main__":
    unittest.main()
