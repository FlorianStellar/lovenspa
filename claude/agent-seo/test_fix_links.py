import unittest

import fix_links as fl


class TestRewrite(unittest.TestCase):
    M = {"/collections/love-room-sauna-privatif": "/collections/sauna-privatif",
         "/pages/guide-quel-type-love-room-choisir ": "/pages/guide-quel-type-love-room-choisir"}

    def test_rewrite_variants(self):
        html = ('<p>Voir <a href="https://lovenspa.fr/collections/love-room-sauna-privatif" class="x">sauna</a>, '
                "<a href='/collections/love-room-sauna-privatif/'>bis</a>, "
                '<a href="/pages/guide-quel-type-love-room-choisir%C2%A0">guide</a> et '
                '<a href="/collections/paris">Paris</a>.</p>')
        new, n = fl.rewrite_hrefs(html, self.M)
        self.assertEqual(n, 3)
        self.assertIn('href="/collections/sauna-privatif" class="x">sauna</a>', new)
        self.assertIn("href='/collections/sauna-privatif'>bis", new)
        self.assertIn('href="/pages/guide-quel-type-love-room-choisir">guide', new)
        self.assertIn('href="/collections/paris"', new)
        # le texte et les autres attributs sont intacts
        self.assertEqual(new.replace("/collections/sauna-privatif", "").count("sauna"), 1)

    def test_no_change(self):
        html = '<a href="/collections/paris">Paris</a>'
        self.assertEqual(fl.rewrite_hrefs(html, self.M), (html, 0))
        self.assertEqual(fl.rewrite_hrefs("", self.M), ("", 0))

    def test_idempotent(self):
        once, _ = fl.rewrite_hrefs('<a href="/collections/love-room-sauna-privatif">s</a>', self.M)
        self.assertEqual(fl.rewrite_hrefs(once, self.M), (once, 0))


class TestEligible(unittest.TestCase):
    def test_rules(self):
        self.assertTrue(fl.eligible("/collections/a", "/collections/b"))
        self.assertFalse(fl.eligible("/products/fiche-supprimee", "/collections/lyon"))
        self.assertTrue(fl.eligible("/products/ancien-handle", "/products/nouveau-handle"))
        self.assertFalse(fl.eligible("/products/abonnement", "/"))
        self.assertFalse(fl.eligible("/pages/x", ""))


if __name__ == "__main__":
    unittest.main()
