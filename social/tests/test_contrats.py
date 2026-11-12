"""Chaque objet échangé entre sous-systèmes respecte son contrat ; aucune donnée de marque dans le code."""
import glob
import json
import os
import re
import tempfile
import unittest
from datetime import date, datetime
from unittest import mock

from social.contrats.valider import SCHEMAS, erreurs
from social.marque import RACINE, charger
from social.s3_catalogue import offres
from social.s4_planification import planifier
from social.s6_controle import controle
from social.s7_diffusion import instagram as diffusion
from social.s8_mesure import audit

M = charger("lovenspa")
NODE = {"handle": "le-nid", "title": "Le Nid - Spa", "status": "ACTIVE", "productType": "Gîte",
        "onlineStoreUrl": None, "tags": ["Equipements|Spa", "Equipements|Sauna", "region|Bretagne", "ville|Vannes"],
        "priceRangeV2": {"minVariantPrice": {"amount": "150.0", "currencyCode": "EUR"}}, "mediaCount": {"count": 6},
        "ville": {"value": "Vannes"}, "ambiance": {"value": "1"}}


def catalogue():
    out = []
    for r in M.strategie("instagram")["regions_poids"]:
        for i in range(8):
            n = dict(NODE, handle=f"{r[:3]}-{i}", tags=["Equipements|Spa", f"region|{r}", "ville|X"],
                     priceRangeV2={"minVariantPrice": {"amount": str(100 + 10 * i), "currencyCode": "EUR"}})
            out.append(offres.offre(n, M))
    return out


class TestSchemas(unittest.TestCase):
    def test_ten_schemas_load(self):
        self.assertEqual(len(SCHEMAS), 10)

    def test_offre(self):
        self.assertEqual(erreurs(offres.offre(NODE, M), "offre"), [])

    def test_city_spelling_fixed_by_brand_config(self):
        n = dict(NODE, ville={"value": "Saint Etienne"})
        self.assertEqual(offres.offre(n, M)["ville"], "Saint-Étienne")

    def test_offre_rejects_private_data(self):
        self.assertTrue(erreurs(dict(offres.offre(NODE, M), email="a@b.fr"), "offre"))

    def test_plan_and_cases(self):
        p = planifier.plan_week(date(2026, 11, 16), catalogue(), [], M.strategie("instagram"), site=M.site)
        self.assertEqual(erreurs(p, "plan"), [])
        self.assertTrue(all(c["lien"].startswith(M.site) for c in p["cases"] if c["format"] != "STORY"))
        self.assertTrue(all(c["lien"] is None for c in p["cases"] if c["format"] == "STORY"))  # pas de lien en story (API)

    def test_case_rejects_unknown_engine(self):
        p = planifier.plan_week(date(2026, 11, 16), catalogue(), [], M.strategie("instagram"), site=M.site)
        self.assertTrue(erreurs(dict(p["cases"][0], moteur="inconnu"), "case"))

    def test_paquet_and_verdict(self):
        p = planifier.plan_week(date(2026, 11, 16), catalogue(), [], M.strategie("instagram"), site=M.site)
        paquet = {"case": p["cases"][0], "legende": "Texte", "medias": ["reel.mp4"], "notes": []}
        self.assertEqual(erreurs(paquet, "paquet"), [])
        self.assertEqual(erreurs(controle.verdict(paquet, M.regles), "verdict"), [])

    def test_publication(self):
        p = planifier.plan_week(date(2026, 11, 16), catalogue(), [], M.strategie("instagram"), site=M.site)
        pret = {"case": p["cases"][0], "legende": "x", "medias": ["a"]}
        with tempfile.TemporaryDirectory() as d:
            diffusion.enregistrer(pret, "M1", "https://instagram.com/p/M1",
                                  datetime(2026, 11, 16, 19, tzinfo=diffusion.PARIS), data_dir=d)
            with open(os.path.join(d, "publies.json"), encoding="utf-8") as f:
                pubs = json.load(f)
        self.assertEqual(erreurs(pubs[0], "publication"), [])

    def test_mesure(self):
        post = {"id": "1", "timestamp": "2026-10-01T10:00:00+0000", "media_type": "IMAGE",
                "insights": {"views": 100, "reach": 80, "shares": 2, "saved": 1}}
        row = audit.enrich([post])[0]
        mesure = {"id": row["id"], "plateforme": "instagram", "format": row["format"], "timestamp": row["timestamp"],
                  "insights": row["insights"], "multiple": row["multiple"],
                  "partages_portee": row["partages_portee"], "enregistrements_portee": row["enregistrements_portee"],
                  "abonnements_portee": row["abonnements_portee"]}
        self.assertEqual(erreurs(mesure, "mesure"), [])

    def test_strategie_and_kit_files(self):
        self.assertEqual(erreurs(M.strategie("instagram"), "strategie"), [])
        self.assertEqual(erreurs(M.config, "kit_marque"), [])

    def test_fiche_format(self):
        fiche = {"id": "ig-reel-lieu", "nom": "Reel « le lieu »", "plateforme": "instagram", "objectif": "portee",
                 "structure": ["accroche", "plans du lieu", "nom et prix"], "preuve": "B",
                 "sources": ["benchmark 11/11/2026"]}
        self.assertEqual(erreurs(fiche, "fiche_format"), [])
        self.assertTrue(erreurs(dict(fiche, preuve="Z"), "fiche_format"))


class TestBrandIsolation(unittest.TestCase):
    """Aucune donnée propre à une marque dans le code : tout vient de marques/<id>/."""
    MOTIFS = [r"lovenspa", r"love'?n'?spa", r"accentuate", r"spicy", r"#?E83F4E", r"FBF6F2", r"Poppins",
              r"escale", r"\b\d{2}:\d{2}'\)", r"_\d{2}_\d{2}_\d{4}", r"MAX_PAR_JOUR\s*=\s*\d", r"cible\s*=\s*\d"]

    def test_no_brand_data_in_code(self):
        fichiers = [f for f in glob.glob(os.path.join(RACINE, "**", "*.py"), recursive=True)
                    if not any(p in f for p in (os.sep + "tests" + os.sep, os.sep + "vendor" + os.sep,
                                                os.sep + "marques" + os.sep, os.sep + "donnees" + os.sep))]
        trouves = []
        for f in fichiers:
            with open(f, encoding="utf-8") as h:
                for i, ligne in enumerate(h, 1):
                    code = ligne.split("#")[0] if not ligne.lstrip().startswith(('"', "'")) else ligne
                    for m in self.MOTIFS:
                        if re.search(m, code, re.I) and "SOCIAL_MARQUE" not in code and "charger(" not in code:
                            trouves.append(f"{os.path.relpath(f, RACINE)}:{i}: {ligne.strip()[:80]}")
        self.assertEqual(trouves, [])

    def test_no_brand_values_in_contracts(self):
        import glob as g
        for f in g.glob(os.path.join(RACINE, "contrats", "*.json")):
            with open(f, encoding="utf-8") as h:
                self.assertNotRegex(h.read(), r"_\d{2}_\d{2}_\d{4}", f)

    def test_brand_switch_by_folder(self):
        with tempfile.TemporaryDirectory() as d:
            for f in ("marque.json", "catalogue.json", "regles.json"):
                with open(os.path.join(M.dossier, f), encoding="utf-8") as src, \
                        open(os.path.join(d, f), "w", encoding="utf-8") as dst:
                    data = json.load(src)
                    if f == "marque.json":
                        data.update(id="autre", site="https://exemple.fr")
                    json.dump(data, dst)
            autre = type(M)("autre", dossier=d)
            self.assertEqual(offres.offre(NODE, autre)["url"], "https://exemple.fr/products/le-nid")


if __name__ == "__main__":
    unittest.main()
