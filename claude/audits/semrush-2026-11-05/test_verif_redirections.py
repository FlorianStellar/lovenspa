import unittest, os
from verif_redirections import evaluer, normaliser_location, charger, encoder

R = {"path": "/products/x", "target": "/collections/lyon"}

class T(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(evaluer(R, 301, "https://lovenspa.fr/collections/lyon", 200), [])
    def test_relative_location(self):
        self.assertEqual(evaluer(R, 301, "/collections/lyon", 200), [])
    def test_pas_redirige(self):
        self.assertIn("source 404 (attendu 301)", evaluer(R, 404, None, 200))
    def test_mauvaise_cible(self):
        self.assertTrue(evaluer(R, 301, "/collections/paris", 200))
    def test_cible_morte(self):
        self.assertIn("cible répond 404 (chaîne ou cible morte)", evaluer(R, 301, "/collections/lyon", 404))
    def test_chaine(self):
        self.assertTrue(evaluer(R, 301, "/collections/lyon", 301))
    def test_unicode(self):
        self.assertEqual(normaliser_location("https://lovenspa.fr/pages/a-c%C5%93ur"), "/pages/a-cœur")
        self.assertEqual(encoder("/pages/a-cœur"), "/pages/a-c%C5%93ur")
    def test_fichier(self):
        rows = charger(os.path.join(os.path.dirname(__file__), "redirections.tsv"))
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({r["path"] for r in rows}), 10)
        for r in rows:
            self.assertTrue(r["path"].startswith("/") and r["target"].startswith("/"))
            self.assertNotEqual(r["path"], r["target"])

if __name__ == "__main__":
    unittest.main()
