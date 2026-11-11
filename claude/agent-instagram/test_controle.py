import collections
import io
from contextlib import redirect_stdout
import json
import os
import sys
import unittest

import controle

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "vendor"))
import minutage  # noqa: E402
import score_hook  # noqa: E402

FICHE = {"nom": "L'Escale Dinard - L'Escale Spa", "ville": "Tréméreuc", "ville_reference": "Saint-Malo",
         "prix_a_partir_de": 190.0, "equipements": ["Sauna", "Spa", "Cheminée"],
         "equipements_non_citables": ["Barre de Pole Dance"]}

BONNE = """Sauna, spa privatif et cheminée à 15 min de Saint-Malo : L'Escale, dès 190 € la nuit.

Le gîte est à Tréméreuc, entre Dinard et Dinan. Arrivée autonome : vous récupérez la clé et la soirée vous appartient.

Le sauna chauffe pendant que vous ouvrez le champagne. Le spa est à vous seuls, sans horaire.

Commentez « ESCALE » et on vous envoie le lien des disponibilités de décembre.

#lovenspa #saintmalo #spaprivatif #weekendamoureux"""


def codes(r):
    return {x["code"] for x in r["resultats"]}


class TestHelpers(unittest.TestCase):
    def test_split_caption(self):
        body, tags = controle.split_caption("Texte\n\n#lovenspa #spa")
        self.assertEqual((body, tags), ("Texte", ["#lovenspa", "#spa"]))

    def test_first_line_skips_blank(self):
        self.assertEqual(controle.first_line("\n\n Bonjour \nsuite"), "Bonjour")

    def test_norm(self):
        self.assertEqual(controle.norm("L’Écrin"), "l'ecrin")

    def test_prices(self):
        self.assertEqual(controle.prices_in("dès 190 € ou 245,50€ et 99 euros"),
                         [(190.0, True), (245.5, False), (99.0, False)])
        self.assertEqual(controle.prices_in("2 personnes, 3 nuits"), [])

    def test_ctas_dedup_by_root(self):
        rules = controle.load_rules()
        self.assertEqual(len(controle.count_ctas("Commente ou commentez", rules)), 1)
        self.assertEqual(len(controle.count_ctas("Enregistrez ce post et lien en bio", rules)), 2)
        self.assertEqual(len(controle.count_ctas("Réservez via le lien en bio", rules)), 1)
        self.assertEqual(controle.count_ctas("Une soirée douce", rules), [])

    def test_typo(self):
        self.assertTrue(controle.typo_issues("Vraiment!"))
        self.assertFalse(controle.typo_issues("Vraiment ! Et ici : ok https://x.fr"))
        self.assertTrue(any("guillemets" in i for i in controle.typo_issues('Il dit "oui"')))


class TestCheck(unittest.TestCase):
    def test_good_caption_passes(self):
        r = controle.check(BONNE, FICHE)
        self.assertNotEqual(r["statut"], "REFUSE", r["resultats"])
        self.assertEqual(len(r["appels"]), 1)

    def test_no_fiche_is_blocking(self):
        self.assertIn("LOGEMENT", codes(controle.check(BONNE, None)))

    def test_several_lodgings(self):
        f2 = dict(FICHE, nom="Le Nid - x", prix_a_partir_de=130.0, ville="Vannes", ville_reference=None)
        ok = BONNE.replace("dès 190 € la nuit.", "dès 190 € la nuit. Et Le Nid, dès 130 € la nuit.")
        self.assertNotIn("PRIX", codes(controle.check(ok, [FICHE, f2])))
        self.assertNotIn("LOGEMENT", codes(controle.check(ok, [FICHE, f2])))
        self.assertIn("LOGEMENT", codes(controle.check(BONNE, [FICHE, f2])))

    def test_wrong_price_blocked(self):
        r = controle.check(BONNE.replace("190 €", "150 €"), FICHE)
        self.assertIn("PRIX", codes(r))

    def test_excluded_equipment_blocked(self):
        r = controle.check(BONNE.replace("cheminée à", "barre de pole dance à"), FICHE)
        self.assertIn("EXCLUS", codes(r))

    def test_too_many_hashtags(self):
        r = controle.check(BONNE + " #a #b", FICHE)
        self.assertIn("HASHTAGS", codes(r))

    def test_missing_brand_tag(self):
        self.assertIn("HASHTAGS", codes(controle.check(BONNE.replace("#lovenspa ", ""), FICHE)))

    def test_placeholder_blocked(self):
        self.assertIn("A_COMPLETER", codes(controle.check(BONNE + "\n{{prix décembre}}", FICHE)))

    def test_long_hook_blocked(self):
        r = controle.check("x" * 130 + "\n\nCommentez ESCALE à Saint-Malo\n\n#lovenspa", FICHE)
        self.assertIn("ACCROCHE", codes(r))

    def test_exit_codes(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p, f = os.path.join(d, "c.txt"), os.path.join(d, "f.json")
            with open(p, "w", encoding="utf-8") as h:
                h.write(BONNE)
            with open(f, "w", encoding="utf-8") as h:
                json.dump(FICHE, h)
            with redirect_stdout(io.StringIO()):
                self.assertIn(controle.main([p, "--fiche", f]), (0, 1))
                self.assertEqual(controle.main([p]), 2)


class TestBaseline(unittest.TestCase):
    """Les 12 légendes publiques du 30/09 au 08/11/2026 : mesures relevées à la main le 11/11."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(HERE, "data", "baseline-public-2026-11-11.json"), encoding="utf-8") as f:
            cls.caps = [p["caption"] for p in json.load(f)["publications"]]
        cls.results = [controle.check(c, None, cls.caps[i + 1:]) for i, c in enumerate(cls.caps)]
        cls.count = collections.Counter(c for r in cls.results for c in codes(r))

    def test_all_refused(self):
        self.assertEqual({r["statut"] for r in self.results}, {"REFUSE"})

    def test_hook_cut_7_of_12(self):
        self.assertEqual(self.count["ACCROCHE"], 7)

    def test_cta_missing_10_of_12(self):
        self.assertEqual(self.count["APPEL"], 10)

    def test_house_tics_12_of_12(self):
        self.assertEqual(self.count["TICS"], 12)

    def test_repetition_detected(self):
        self.assertGreaterEqual(self.count["REPETITION"], 9)


class TestVendorFixes(unittest.TestCase):
    def test_proper_noun_regex_matches(self):
        self.assertIsNotNone(score_hook.PROPER_RE.match("Paris"))

    def test_mpm_zero_no_crash(self):
        score_hook.run("Un gîte à Saint-Malo", mpm=0)
        minutage.analyse("Ligne une.\nLigne deux.", mpm=0)

    def test_tc_rounding(self):
        self.assertEqual(minutage.tc(59.96), "1:00.0")

    def test_hook_scores_concrete_higher(self):
        weak = score_hook.run("Parfois il suffit d'une nuit pour se retrouver")[1]
        strong = score_hook.run("Sauna et spa privatif à Saint-Malo dès 190 € la nuit")[1]
        self.assertGreater(strong, weak)


if __name__ == "__main__":
    unittest.main()
