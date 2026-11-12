import unittest

from social.s5_production.produire import typo_fr


class TestTypoFr(unittest.TestCase):
    def test_insecables(self):
        self.assertEqual(typo_fr("Concours : gagnez ! Vraiment ?"), "Concours : gagnez ! Vraiment ?")
        self.assertEqual(typo_fr("« Garde ton samedi »"), "« Garde ton samedi »")

    def test_untouched(self):
        for s in ("https://lovenspa.fr/a?b=1", "à 18:30", "Concours : déjà bon", "#lovenspa"):
            self.assertEqual(typo_fr(s), s)


if __name__ == "__main__":
    unittest.main()
