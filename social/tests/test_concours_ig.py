"""Concours Instagram : trois mentions obligatoires, bloquantes (IG-R28, décision du 12/11/2026)."""
import unittest

from social.s6_controle import controle

OK = ("Gagnez une nuit pour deux. Règlement complet : lien en bio. Chaque participant dégage Instagram de toute "
      "responsabilité. Ce concours n'est ni parrainé, ni approuvé, ni administré par Instagram.")


class TestConcours(unittest.TestCase):
    def test_all_mentions(self):
        self.assertEqual(controle.mentions_concours_manquantes(OK), [])

    def test_missing_each(self):
        self.assertEqual(len(controle.mentions_concours_manquantes("Gagnez une nuit pour deux !")), 3)
        sans_regl = OK.replace("Règlement complet : lien en bio. ", "")
        self.assertEqual(controle.mentions_concours_manquantes(sans_regl), ["lien ou mention du règlement du jeu"])

    def test_verdict_blocks_only_concours(self):
        case = {"moteur": "concours", "offres": []}
        v = controle.verdict({"case": case, "legende": "Gagnez une nuit pour deux !", "medias": ["a.jpg"]})
        self.assertEqual(sum("IG-R28" in b for b in v["bloquants"]), 3)
        v = controle.verdict({"case": {"moteur": "couple", "offres": []}, "legende": "Gagnez une nuit !", "medias": ["a"]})
        self.assertFalse(any("IG-R28" in b for b in v["bloquants"]))


if __name__ == "__main__":
    unittest.main()
