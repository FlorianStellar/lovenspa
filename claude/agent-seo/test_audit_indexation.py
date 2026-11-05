import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_indexation import load_products, build_universe, flatten, summarize, write, COLS


class T(unittest.TestCase):
    def test_load_products_pads_and_skips_empty(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("a\tACTIVE\t\thttps://x\n\nb\tDRAFT\n")
        r = load_products(f.name)
        self.assertEqual([x["handle"] for x in r], ["a", "b"])
        self.assertEqual(r[1]["template"], "")

    def test_universe_dedup_and_sitemap(self):
        p = [{"handle": "a", "shopify_status": "ACTIVE", "template": ""},
             {"handle": "a", "shopify_status": "ACTIVE", "template": ""},
             {"handle": "b", "shopify_status": "DRAFT", "template": ""}]
        u = build_universe(p, ["https://lovenspa.fr/products/a/"])
        self.assertEqual(len(u), 2)
        self.assertEqual(u[0]["in_sitemap"], "oui"); self.assertEqual(u[1]["in_sitemap"], "non")

    def test_flatten_canonical(self):
        b = {"handle": "a", "shopify_status": "ACTIVE", "template": "", "url": "u", "in_sitemap": "oui"}
        self.assertEqual(flatten(b, {"googleCanonical": "x/", "userCanonical": "x"})["canonical_ok"], "oui")
        self.assertEqual(flatten(b, {"googleCanonical": "x", "userCanonical": "y"})["canonical_ok"], "non")
        self.assertEqual(flatten(b, {"error": "e"})["error"], "e")
        self.assertEqual(list(flatten(b, {}).keys()), COLS)

    def test_summarize(self):
        b = {"handle": "a", "shopify_status": "ACTIVE", "template": "", "url": "u", "in_sitemap": "non"}
        rows = [flatten(b, {"coverageState": "Submitted and indexed"}),
                flatten({**b, "handle": "z", "shopify_status": "DRAFT"}, {"coverageState": "Not found (404)"}),
                flatten(b, {"error": "x"})]
        s = summarize(rows)
        self.assertEqual(s["total"], 3); self.assertEqual(s["erreurs_api"], 1)
        self.assertEqual(s["par_coverage_non_actives"]["Not found (404)"], 1)
        self.assertEqual(s["actives_hors_sitemap"], ["a", "a"])

    def test_write_roundtrip(self):
        import csv
        b = {"handle": "a", "shopify_status": "ACTIVE", "template": "", "url": "u", "in_sitemap": "oui"}
        p = tempfile.mktemp(suffix=".csv"); write(p, [flatten(b, {"verdict": "PASS"})])
        self.assertEqual(next(csv.DictReader(open(p)))["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
