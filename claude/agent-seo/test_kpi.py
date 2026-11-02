import unittest
from kpi import (normalize_url, segment, totals_by_segment, cannibalization,
                 quick_wins, best_page, delta)


def row(keys, clicks=0, impressions=0, position=1.0):
    return {"keys": keys, "clicks": clicks, "impressions": impressions, "position": position}


class TestNormalize(unittest.TestCase):
    def test_www_removed(self):
        self.assertEqual(normalize_url("https://www.lovenspa.fr/products/a"), "https://lovenspa.fr/products/a")

    def test_fragment_removed(self):
        self.assertEqual(normalize_url("https://lovenspa.fr/products/a#calendar"), "https://lovenspa.fr/products/a")


class TestSegment(unittest.TestCase):
    def test_segments(self):
        cases = {
            "https://lovenspa.fr/": "home",
            "https://lovenspa.fr/products/x": "fiche",
            "https://www.lovenspa.fr/collections/love-room": "collection",
            "https://lovenspa.fr/pages/guide": "page",
            "https://lovenspa.fr/blogs/news/a": "blog",
            "https://lovenspa.fr/en/pages/guide": "en",
            "https://lovenspa.fr/search": "autre",
        }
        for url, expected in cases.items():
            self.assertEqual(segment(url), expected, url)


class TestTotals(unittest.TestCase):
    def test_aggregates(self):
        t = totals_by_segment([row(["https://lovenspa.fr/products/a"], 2, 10),
                               row(["https://lovenspa.fr/products/b"], 1, 5)])
        self.assertEqual(t["fiche"], {"clicks": 3, "impressions": 15, "urls": 2})


class TestCannibalization(unittest.TestCase):
    def test_detects_two_strong_pages(self):
        rows = [row(["love room", "https://lovenspa.fr/collections/love-room"], impressions=600, position=9),
                row(["love room", "https://lovenspa.fr/pages/guide"], impressions=400, position=11)]
        res = cannibalization(rows)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["pages"][0]["share"], 0.6)

    def test_ignores_dominant_page(self):
        rows = [row(["q", "https://lovenspa.fr/a"], impressions=950),
                row(["q", "https://lovenspa.fr/b"], impressions=50)]
        self.assertEqual(cannibalization(rows), [])

    def test_ignores_low_volume(self):
        rows = [row(["q", "https://lovenspa.fr/a"], impressions=50),
                row(["q", "https://lovenspa.fr/b"], impressions=50)]
        self.assertEqual(cannibalization(rows), [])


class TestQuickWins(unittest.TestCase):
    def test_filters_range_and_volume(self):
        rows = [row(["a"], impressions=500, position=7), row(["b"], impressions=500, position=2),
                row(["c"], impressions=50, position=7), row(["d"], impressions=900, position=12)]
        self.assertEqual([w["query"] for w in quick_wins(rows)], ["d", "a"])


class TestBestPage(unittest.TestCase):
    def test_best_and_none(self):
        rows = [row(["q", "https://www.lovenspa.fr/a"], 1, 100, 8), row(["q", "https://lovenspa.fr/b"], 0, 20, 30)]
        self.assertEqual(best_page(rows, "q")["page"], "https://lovenspa.fr/a")
        self.assertEqual(best_page(rows, "q")["impressions"], 120)
        self.assertIsNone(best_page(rows, "absent"))


class TestDelta(unittest.TestCase):
    def test_delta(self):
        self.assertEqual(delta(110, 100), 10.0)
        self.assertIsNone(delta(5, 0))


if __name__ == "__main__":
    unittest.main()
