import json
import os
import tempfile
import unittest

import audit


def post(i, views=None, reach=None, shares=None, saved=None, follows=None, kind="FEED", mtype="IMAGE", day="2026-10-01"):
    ins = {k: v for k, v in dict(views=views, reach=reach, shares=shares, saved=saved, follows=follows).items() if v is not None}
    return {"id": str(i), "timestamp": f"{day}T10:00:00+0000", "media_product_type": kind, "media_type": mtype,
            "caption": f"Légende {i}\nsuite", "permalink": f"https://instagram.com/p/{i}", "insights": ins}


class TestBasics(unittest.TestCase):
    def test_fmt(self):
        self.assertEqual(audit.fmt(post(1, kind="REELS", mtype="VIDEO")), "REELS")
        self.assertEqual(audit.fmt(post(1, mtype="CAROUSEL_ALBUM")), "CAROUSEL")
        self.assertEqual(audit.fmt(post(1)), "IMAGE")

    def test_ratio(self):
        self.assertEqual(audit.ratio(5, 10), 0.5)
        self.assertIsNone(audit.ratio(5, 0))
        self.assertIsNone(audit.ratio(None, 10))

    def test_metric_ignores_non_numbers(self):
        p = post(1)
        p["insights"]["views"] = "n/a"
        self.assertIsNone(audit.metric(p, "views"))

    def test_zero_views_with_reach_is_unmeasured(self):
        self.assertIsNone(audit.metric(post(1, views=0, reach=100), "views"))
        self.assertEqual(audit.metric(post(1, views=0, reach=0), "views"), 0)

    def test_median_skips_missing(self):
        ps = [post(1, views=100), post(2, views=300), post(3)]
        self.assertEqual(audit.median_of(ps, "views"), 200)
        self.assertIsNone(audit.median_of([post(4)], "views"))


class TestEnrich(unittest.TestCase):
    def test_multiple_overall(self):
        rows = audit.enrich([post(1, views=100), post(2, views=200), post(3, views=600)])
        self.assertEqual([r["multiple"] for r in rows], [0.5, 1.0, 3.0])

    def test_multiple_by_format(self):
        ps = [post(1, views=100), post(2, views=300), post(3, views=1000, kind="REELS"), post(4, views=3000, kind="REELS")]
        rows = audit.enrich(ps, par_format=True)
        self.assertEqual(rows[0]["mediane_ref"], 200)
        self.assertEqual(rows[2]["mediane_ref"], 2000)
        self.assertEqual(rows[3]["multiple"], 1.5)

    def test_rates(self):
        r = audit.enrich([post(1, views=10, reach=200, shares=4, saved=10, follows=2)])[0]
        self.assertEqual((r["partages_portee"], r["enregistrements_portee"], r["abonnements_portee"]), (0.02, 0.05, 0.01))

    def test_missing_reach_gives_none(self):
        r = audit.enrich([post(1, views=10, shares=4)])[0]
        self.assertIsNone(r["partages_portee"])

    def test_completeness(self):
        self.assertEqual(audit.completeness([post(1, views=1), post(2)], ("views",)), {"views": 1})

    def test_rank_excludes_none(self):
        rows = [{"k": 3}, {"k": None}, {"k": 1}]
        top, bottom = audit.rank(rows, "k", top=5)
        self.assertEqual([r["k"] for r in top], [3, 1])
        self.assertEqual(bottom, [])

    def test_rank_bottom(self):
        rows = [{"k": i} for i in range(12)]
        top, bottom = audit.rank(rows, "k", top=5)
        self.assertEqual([r["k"] for r in bottom], [0, 1, 2, 3, 4])

    def test_filter_since(self):
        ps = [post(1, day="2026-07-01"), post(2, day="2026-09-01")]
        self.assertEqual([p["id"] for p in audit.filter_since(ps, "2026-08-01")], ["2"])


class TestEndToEnd(unittest.TestCase):
    def test_cli_markdown(self):
        snap = {"profil": {}, "publications": [post(i, views=100 * i, reach=1000, shares=i, saved=2 * i) for i in range(1, 13)]
                + [post(99)]}
        with tempfile.TemporaryDirectory() as d:
            src, out = os.path.join(d, "s.json"), os.path.join(d, "a.md")
            with open(src, "w") as f:
                json.dump(snap, f)
            self.assertEqual(audit.main([src, "--md", out]), 0)
            with open(out, encoding="utf-8") as f:
                md = f.read()
        self.assertIn("Périmètre : 13 publications", md)
        self.assertIn("views 12/13", md)
        self.assertIn("| 2026-10-01 | IMAGE | 1.85x |", md)  # 1200 / médiane 650
        self.assertIn("## Par format", md)


if __name__ == "__main__":
    unittest.main()
