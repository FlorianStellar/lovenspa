import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from veille import product_urls, watch_urls, sitemap_locs, build_universe, compare, KEYS, OK

def row(u, cs, **kw):
    r = {k: "" for k in KEYS}; r.update(url=u, coverageState=cs, **kw); return r

class T(unittest.TestCase):
    def test_product_urls(self):
        self.assertEqual(product_urls(" a  b\nc "), [f"https://lovenspa.fr/products/{h}" for h in "abc"])
    def test_watch_only_unindexed_products(self):
        prev = [row("x/products/a", OK), row("x/products/b", "Not found (404)"), row("x/collections/c", "Crawled")]
        self.assertEqual(watch_urls(prev), ["x/products/b"])
    def test_sitemap_locs(self):
        xml = "<loc>https://l/sitemap_collections_1.xml?a=1&amp;b=2</loc><loc>https://l/sitemap_products_1.xml</loc>"
        self.assertEqual(sitemap_locs(xml, "sitemap_collections"), ["https://l/sitemap_collections_1.xml?a=1&b=2"])
    def test_universe_order_dedup(self):
        self.assertEqual(build_universe(["p1", "p2"], ["p2", "w"], ["c"]), ["p1", "p2", "w", "c"])
    def test_compare(self):
        prev = [row("w", "Not found (404)"), row("k", "Crawled"), row("n", OK)]
        cur = [row("w", OK), row("k", "Crawled"), row("n", "Excluded by noindex", lastCrawlTime="2026-11-05"),
               row("z", "URL is unknown"), row("e", "", error="x"),
               row("c", OK, googleCanonical="a/", userCanonical="b")]
        s = compare(cur, prev, {"w"})
        self.assertEqual(s["erreurs"], 1); self.assertEqual(s["suivi"][("Not found (404)", OK)], 1)
        self.assertEqual([a[0] for a in s["nouvelles_anomalies"]], ["n", "z"])
        self.assertEqual(s["anomalies_connues"], 1); self.assertEqual(s["canonical_diff"], ["c"])

if __name__ == "__main__":
    unittest.main()
