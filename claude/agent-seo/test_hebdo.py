import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hebdo import totals, declining_pages, ctr_curve, ctr_anomalies, bucket

def r(k, c, i, p=5.0): return {"keys": [k], "clicks": c, "impressions": i, "position": p}

class T(unittest.TestCase):
    def test_totals(self):
        self.assertEqual(totals([r("a", 10, 100), r("b", 0, 100)]), {"clicks": 10, "impressions": 200, "ctr": 5.0})
        self.assertIsNone(totals([])["ctr"])
    def test_decline_threshold_and_www(self):
        prev = [r("https://www.lovenspa.fr/a", 100, 1), r("https://lovenspa.fr/b", 100, 1), r("https://lovenspa.fr/c", 10, 1)]
        cur = [r("https://lovenspa.fr/a", 70, 1), r("https://lovenspa.fr/b", 90, 1)]
        d = declining_pages(cur, prev)
        self.assertEqual([x["page"] for x in d], ["https://lovenspa.fr/a"]); self.assertEqual(d[0]["delta_pct"], -30.0)
    def test_disappeared_page_counts(self):
        self.assertEqual(declining_pages([], [r("https://lovenspa.fr/x", 50, 1)])[0]["clicks"], 0)
    def test_bucket(self):
        self.assertEqual((bucket(0.5), bucket(1.9), bucket(7.2), bucket(55)), (1, 1, 7, 20))
    def test_ctr(self):
        rows = [r("q1", 100, 1000, 2.1), r("q2", 10, 1000, 2.5), r("q3", 0, 500, 2.2)]
        curve = ctr_curve(rows); self.assertAlmostEqual(curve[2], 110 / 2500)
        an = ctr_anomalies(rows, curve, min_impr=1000)
        self.assertEqual([a["query"] for a in an], ["q2"])

if __name__ == "__main__":
    unittest.main()
