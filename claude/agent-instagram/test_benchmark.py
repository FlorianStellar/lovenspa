import unittest
from datetime import date

import benchmark
from test_ig_client import FakeResp, FakeSession
from ig_client import IGClient


def media(i, likes, comments=0, kind="FEED", mtype="IMAGE", day=1):
    return {"timestamp": f"2026-10-{day:02d}T10:00:00+0000", "media_product_type": kind, "media_type": mtype,
            "like_count": likes, "comments_count": comments, "caption": f"Accroche {i}\nsuite", "permalink": f"p{i}"}


class TestSummary(unittest.TestCase):
    def test_engagement_hidden_likes(self):
        self.assertIsNone(benchmark.engagement({"comments_count": 3}))
        self.assertEqual(benchmark.engagement({"like_count": 10, "comments_count": 2}), 12)

    def test_fmt(self):
        self.assertEqual(benchmark.fmt({"media_product_type": "REELS"}), "REELS")
        self.assertEqual(benchmark.fmt({"media_type": "CAROUSEL_ALBUM"}), "CAROUSEL")

    def test_summarize(self):
        acc = {"username": "x", "followers_count": 1000, "media_count": 300,
               "media": [media(1, 10, day=1), media(2, 20, day=8), media(3, 100, kind="REELS", mtype="VIDEO", day=15)]}
        s = benchmark.summarize(acc, today=date(2026, 10, 20))
        self.assertEqual(s["engagement_median"], 20)
        self.assertEqual(s["taux_engagement_median"], 2.0)
        self.assertEqual(s["posts_par_semaine"], 1.5)   # 3 posts sur 14 jours
        self.assertEqual(s["part_reels"], 0.33)
        self.assertEqual(s["dernier_post_jours"], 5)
        self.assertEqual([o["multiple"] for o in s["outliers"]], [5.0])
        self.assertEqual(s["outliers"][0]["accroche"], "Accroche 3")

    def test_summarize_hidden_likes_and_empty(self):
        acc = {"username": "y", "followers_count": 10, "media": [{"timestamp": "2026-10-01T00:00:00", "media_type": "IMAGE"}]}
        s = benchmark.summarize(acc, today=date(2026, 10, 2))
        self.assertEqual(s["likes_masques"], 1)
        self.assertIsNone(s["engagement_median"])
        self.assertIsNone(s["posts_par_semaine"])
        self.assertEqual(benchmark.summarize({"username": "z"})["posts_analyses"], 0)

    def test_markdown(self):
        acc = {"username": "x", "followers_count": 1000, "media_count": 3,
               "media": [media(1, 10), media(2, 10, day=2), media(3, 90, day=3)]}
        md = benchmark.to_markdown([benchmark.summarize(acc, today=date(2026, 10, 5))], [("perso", "not a business")])
        self.assertIn("| x | 1000 | 3 |", md)
        self.assertIn("Comptes non lus", md)
        self.assertIn("9.0x", md)


class TestDiscover(unittest.TestCase):
    def test_query_and_flatten(self):
        seen = {}

        def route(u, p):
            seen["fields"] = p["fields"]
            return FakeResp(200, {"business_discovery": {"username": "abracadaroom", "followers_count": 5,
                                                         "media": {"data": [media(1, 1)]}}})
        s = FakeSession([(lambda u, p: True, route)])
        acc = benchmark.discover(IGClient("1", session=s, version=""), "abracadaroom", n=20)
        self.assertIn("business_discovery.username(abracadaroom)", seen["fields"])
        self.assertIn("media.limit(20)", seen["fields"])
        self.assertEqual(len(acc["media"]), 1)


if __name__ == "__main__":
    unittest.main()
