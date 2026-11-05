import unittest
from audit_doublons import texte_principal, mots, shingles, jaccard, agreger, balises

class T(unittest.TestCase):
    def test_texte_main(self):
        h = "<header>menu</header><main><h1>Titre</h1><script>x=1</script><p>Bonjour&nbsp;toi</p><nav>n</nav></main><footer>f</footer>"
        self.assertNotIn("menu", texte_principal(h)); self.assertNotIn("x=1", texte_principal(h)); self.assertIn("Bonjour", texte_principal(h))
    def test_mots(self):
        self.assertEqual(mots("Côte-d'Or Œuvre 2"), ["côte", "d'or", "œuvre", "2"])
    def test_jaccard(self):
        a = shingles(mots("un deux trois quatre cinq six"))
        self.assertEqual(jaccard(a, a), 1.0)
        self.assertEqual(jaccard(a, shingles(mots("a b c d e f"))), 0.0)
        self.assertEqual(jaccard(set(), set()), 0.0)
    def test_agreger(self):
        r = agreger([{"clicks": 1, "impressions": 10, "position": 2}, {"clicks": 0, "impressions": 30, "position": 6}])
        self.assertEqual(r, {"clics": 1, "impressions": 40, "position_ponderee": 5.0})
        self.assertIsNone(agreger([])["position_ponderee"])
    def test_balises(self):
        b = balises('<title> T </title><meta name="description" content="D &amp; E"><h1 class="x">A <b>B</b></h1><link rel="canonical" href="https://x/y">')
        self.assertEqual((b["title"], b["description"], b["h1"], b["canonical"], b["robots"]), ("T", "D & E", ["A B"], "https://x/y", None))

if __name__ == "__main__":
    unittest.main()
