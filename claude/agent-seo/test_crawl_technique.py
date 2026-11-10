import unittest

import crawl_technique as ct

SM_INDEX = """<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<sitemap><loc>https://lovenspa.fr/sitemap_products_1.xml</loc></sitemap></sitemapindex>"""
SM_URLS = """<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://lovenspa.fr/products/a</loc></url><url><loc>https://lovenspa.fr/collections/b</loc></url></urlset>"""

HTML = """<html><head><title>Love room Paris</title><meta name="description" content="Desc">
<link rel="canonical" href="https://lovenspa.fr/products/a"><meta name="robots" content="index,follow">
<script type="application/ld+json">{"@type":"Product","offers":{"price":"200","availability":"https://schema.org/InStock"}}</script>
<script type="application/ld+json">{bad json</script></head>
<body><h1>A</h1><a href="/collections/b?page=2">b</a><a href="https://www.lovenspa.fr/pages/c/">c</a>
<a href="https://autre.fr/x">x</a><a href="/cart">panier</a><a href="mailto:a@b.c">m</a>
<div data-lvn-churn></div></body></html>"""


class TestParse(unittest.TestCase):
    def test_sitemap_index(self):
        subs, urls = ct.parse_sitemap(SM_INDEX)
        self.assertEqual(subs, ["https://lovenspa.fr/sitemap_products_1.xml"])
        self.assertEqual(urls, [])

    def test_sitemap_urls(self):
        self.assertEqual(ct.parse_sitemap(SM_URLS)[1], ["https://lovenspa.fr/products/a", "https://lovenspa.fr/collections/b"])

    def test_normalize(self):
        base = "https://lovenspa.fr/products/a"
        self.assertEqual(ct.normalize("/collections/b?page=2#x", base), "https://lovenspa.fr/collections/b")
        self.assertEqual(ct.normalize("https://www.lovenspa.fr/pages/c/", base), "https://lovenspa.fr/pages/c")
        self.assertIsNone(ct.normalize("https://autre.fr/x", base))
        self.assertIsNone(ct.normalize("/cart", base))
        self.assertIsNone(ct.normalize("mailto:a@b.c", base))
        self.assertEqual(ct.normalize("/", base), "https://lovenspa.fr/")

    def test_analyze_html(self):
        r = ct.analyze_html("https://lovenspa.fr/products/a", HTML, {})
        self.assertEqual(r["canonical"], "https://lovenspa.fr/products/a")
        self.assertEqual(r["h1_count"], 1)
        self.assertEqual((r["offer_price"], r["offer_availability"]), ("200", "InStock"))
        self.assertIn("__INVALIDE__", r["jsonld_types"])
        self.assertTrue(r["is_churn"])
        self.assertEqual(r["_links"], {"https://lovenspa.fr/collections/b", "https://lovenspa.fr/pages/c"})


class TestRobots(unittest.TestCase):
    TXT = "User-agent: *\nDisallow: /cart\n\nUser-agent: GPTBot\nUser-agent: CCBot\nDisallow: /\n"

    def test_rules(self):
        r = ct.robots_rules(self.TXT)
        self.assertEqual(r["*"], ["/cart"])
        self.assertEqual(r["gptbot"], ["/"])
        self.assertEqual(r["ccbot"], ["/"])

    def test_blocked(self):
        r = ct.robots_rules(self.TXT)
        self.assertTrue(ct.bot_blocked_root(r, "GPTBot"))
        self.assertFalse(ct.bot_blocked_root(r, "ClaudeBot"))  # retombe sur *


class TestGraph(unittest.TestCase):
    def test_depth(self):
        g = {"h": {"a", "b"}, "a": {"c"}, "c": {"d"}, "d": {"e"}}
        d = ct.click_depth(g, "h")
        self.assertEqual(d, {"h": 0, "a": 1, "b": 1, "c": 2, "d": 3, "e": 4})


class TestLinkIssues(unittest.TestCase):
    def test_rows(self):
        g = {"h": {"a", "x"}, "a": {"x", "y"}, "y": set()}
        st = {"a": (200, ""), "x": (404, ""), "y": (301, "/z")}
        rows = ct.link_issue_rows(g, st)
        self.assertEqual([(r["source"], r["cible"], r["statut"]) for r in rows],
                         [("a", "x", 404), ("h", "x", 404), ("a", "y", 301)])
        self.assertEqual(rows[2]["redirige_vers"], "/z")

    def test_unknown_target_is_ok(self):
        self.assertEqual(ct.link_issue_rows({"h": {"q"}}, {}), [])


class TestRetry(unittest.TestCase):
    def test_retry_after(self):
        self.assertEqual(ct.retry_after("3", 0), 3.0)
        self.assertEqual(ct.retry_after("120", 0), 60.0)
        self.assertEqual(ct.retry_after(None, 0), 5.0)
        self.assertEqual(ct.retry_after("x", 2), 20.0)
        self.assertEqual(ct.retry_after(None, 9), 60.0)


class TestClassify(unittest.TestCase):
    def base(self, **kw):
        row = {"url": "https://lovenspa.fr/products/a", "status": 200, "in_sitemap": True,
               "canonical": "https://lovenspa.fr/products/a", "meta_robots": "", "x_robots": "",
               "h1_count": 1, "hreflang": "", "jsonld_types": "Product", "is_churn": False,
               "offer_availability": "", "n_links_internal": 10, "depth": 2}
        row.update(kw)
        return row

    def test_clean(self):
        self.assertEqual(ct.classify(self.base()), [])

    def test_anomalies(self):
        a = ct.classify(self.base(canonical="https://lovenspa.fr/products/b", meta_robots="noindex",
                                  h1_count=2, hreflang="en=https://lovenspa.fr/en/products/a",
                                  is_churn=True, offer_availability="InStock", n_links_internal=150, depth=5))
        for x in ["canonical_autre_url", "noindex_dans_sitemap", "h1_2", "hreflang_en",
                  "churn_offer_instock", "plus_de_100_liens", "profondeur_4_plus"]:
            self.assertIn(x, a)

    def test_status(self):
        self.assertEqual(ct.classify(self.base(status=301)), ["redirection_dans_sitemap"])
        self.assertEqual(ct.classify(self.base(status=404)), ["http_404"])
        self.assertIn("non_atteinte_depuis_accueil", ct.classify(self.base(depth="")))


if __name__ == "__main__":
    unittest.main()
