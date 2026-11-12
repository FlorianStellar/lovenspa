import unittest

from social.contrats.valider import erreurs
from social.s2_connaissance import bibliotheque as b

FICHE = {"id": "F01", "nom": "Reel lieu", "plateforme": "instagram", "objectif": "portee",
         "structure": ["a"], "preuve": "B", "sources": ["compilation"], "exemples": ["ancien"]}


def sig(compte, fiche="F01", mult=4.0, fr=True, acc="Une cabane rien qu'à vous"):
    return {"compte": compte, "fiche_format": fiche, "multiple": mult, "permalink": f"p-{compte}-{mult}",
            "langue_fr": fr, "accroche": acc, "format": "REELS", "date": "2026-10-01",
            "formule_accroche": "A01", "pertinence_marque": "directe"}


class TestBibliotheque(unittest.TestCase):
    def test_amorce_parses_skill_fiches(self):
        fiches = b.fiches_amorce()
        self.assertGreaterEqual(len(fiches), 8)
        self.assertTrue(all("id" in f for f in fiches))

    def test_level_b_needs_three_accounts(self):
        self.assertEqual(b.niveau(3, "F01"), "B")
        self.assertEqual(b.niveau(2, "F01"), "C")
        self.assertEqual(b.niveau(9, "F02"), "C")  # concours : jamais de preuve organique

    def test_construire_recomputes_and_validates(self):
        out = b.construire([FICHE], [sig("a"), sig("b", mult=9.0), sig("a", mult=5.0)], "2026-11-12")[0]
        self.assertEqual(out["preuve"], "C")
        self.assertIn("2 compte(s)", out["observe"])
        self.assertTrue(out["exemples"][0].startswith("p-b-9.0"))
        self.assertIn("benchmark Business Discovery du 2026-11-12", out["sources"])
        self.assertEqual(erreurs(out, "fiche_format"), [])
        out = b.construire([FICHE], [sig("a"), sig("b"), sig("c")], "2026-11-12")[0]
        self.assertEqual(out["preuve"], "B")

    def test_no_signal_keeps_old_examples(self):
        out = b.construire([FICHE], [], "2026-11-12")[0]
        self.assertEqual((out["preuve"], out["exemples"]), ("C", ["ancien"]))

    def test_accroches_french_only_sorted(self):
        acc = b.accroches_observees([sig("a", mult=4), sig("b", mult=8), sig("c", fr=False), sig("d", acc="  ")])
        self.assertEqual([a["compte"] for a in acc], ["b", "a"])
        self.assertIn("pas l'accroche parlée", acc[0]["nature"])
        self.assertEqual(acc[0]["pertinence"], "directe")

    def test_rafraichir_and_exclude_partnerships(self):
        bench = {"comptes": {"x": {"media": [
            {"permalink": "p-a-4.0", "caption": "Une cabane rien qu’à vous, avec le spa"},
            {"permalink": "p-b-4.0", "caption": "Collaboration commerciale avec @marque : une nuit pour vous"},
            {"permalink": "p-c-4.0", "caption": "A cabin for the two of you"},
            {"permalink": "p-d-4.0", "caption": "Which of these villages will you add to your list?\n7 villages que vous allez aimer"}]}}}
        s = b.rafraichir([sig("a"), sig("b"), sig("c"), sig("d", acc="Which of these villages will you add to your list?")], bench)
        self.assertEqual([x["hors_organique"] for x in s], [False, True, False, False])
        self.assertEqual([x["langue_fr"] for x in s], [True, True, False, False])  # d : accroche anglaise
        out = b.construire([FICHE], s, "2026-11-12")[0]
        self.assertIn("3 compte(s) avec au moins un signal à 3x ou plus : a, c, d.", out["observe"])  # b (partenariat) exclu
        self.assertEqual([a["compte"] for a in b.accroches_observees(s)], ["a"])

    def test_synthese(self):
        f = b.construire([FICHE], [sig("a")], "2026-11-12")
        md = b.synthese_md(f, b.accroches_observees([sig("a")]), "2026-11-12")
        self.assertIn("| F01 | Reel lieu | C |", md)
        self.assertIn("Accroches réelles en français (1)", md)


if __name__ == "__main__":
    unittest.main()
