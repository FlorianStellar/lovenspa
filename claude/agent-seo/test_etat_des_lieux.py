import json
import os
import tempfile
import unittest
from datetime import date
from unittest.mock import patch

import etat_des_lieux as edl


def row(keys, clicks=0, impressions=0, position=1.0):
    return {"keys": keys, "clicks": clicks, "impressions": impressions, "position": position}


DATA = {
    "pages": [row(["https://lovenspa.fr/collections/love-room"], 10, 1000, 9)],
    "queries": [row(["love room"], 10, 1000, 9), row(["love room lyon"], 1, 300, 6)],
    "qp": [row(["love room", "https://lovenspa.fr/collections/love-room"], 10, 1000, 9),
           row(["love room lyon", "https://lovenspa.fr/collections/lyon"], 1, 300, 6)],
}


class FakeClient:
    def search_analytics_all(self, start, end, dimensions=("page",), **kw):
        key = {"page": "pages", "query": "queries"}.get(dimensions[0]) if len(dimensions) == 1 else "qp"
        return DATA[key]

    def list_sitemaps(self):
        return [{"path": "https://lovenspa.fr/sitemap.xml", "errors": "0"}]


class TestPeriods(unittest.TestCase):
    def test_contiguous_28_days(self):
        (cs, ce), (ps, pe) = edl.periods(date(2026, 11, 2))
        self.assertEqual((cs, ce), ("2026-10-03", "2026-10-30"))
        self.assertEqual((ps, pe), ("2026-09-05", "2026-10-02"))


class TestSummarize(unittest.TestCase):
    def test_targets_and_quick_wins(self):
        s = edl.summarize(DATA, DATA)
        self.assertEqual(s["cibles"]["love room"]["position"], 9)
        self.assertIsNone(s["cibles"]["love rooms"])
        self.assertEqual([w["query"] for w in s["quick_wins"]], ["love room", "love room lyon"])
        self.assertEqual(s["segments"]["collection"]["impr_delta_pct"], 0.0)


class TestEndToEnd(unittest.TestCase):
    def test_main_writes_json(self):
        with tempfile.TemporaryDirectory() as d, patch.object(edl, "GSCClient", FakeClient):
            out = os.path.join(d, "out.json")
            edl.main(out)
            with open(out, encoding="utf-8") as f:
                res = json.load(f)
        self.assertEqual(res["perimetre"]["requetes"], 2)
        self.assertEqual(res["sitemaps"][0]["errors"], "0")


if __name__ == "__main__":
    unittest.main()
