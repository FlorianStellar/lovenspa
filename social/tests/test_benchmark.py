import unittest
from datetime import date

from social.s2_connaissance import benchmark
from social.tests.test_ig_client import FakeResp, FakeSession
from social.connecteurs.instagram import IGClient


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


class TestHygiene(unittest.TestCase):
    TODAY = date(2026, 11, 12)

    def post(self, i, eng, day, kind="FEED", mtype="IMAGE", cap="Une nuit pour vous deux avec le spa et la vue"):
        return {"timestamp": f"{day}T10:00:00+0000", "media_product_type": kind, "media_type": mtype,
                "like_count": eng, "comments_count": 0, "caption": cap, "permalink": f"p{i}"}

    def test_langue_fr(self):
        self.assertTrue(benchmark.langue_fr("Une nuit pour vous deux avec le spa"))
        self.assertFalse(benchmark.langue_fr("A night for the two of you"))

    def test_hors_organique(self):
        self.assertTrue(benchmark.HORS_ORGANIQUE.search("🎁 JEU CONCOURS : 2 nuits à gagner"))
        self.assertTrue(benchmark.HORS_ORGANIQUE.search("En partenariat avec @x"))
        self.assertFalse(benchmark.HORS_ORGANIQUE.search("Une cabane au bord de l'eau"))

    def test_pinned_post_set_aside(self):
        posts = [self.post(i, 10, f"2026-10-{i + 1:02d}") for i in range(10)]
        posts.sort(key=lambda p: p["timestamp"], reverse=True)
        posts.insert(0, self.post(55, 999, "2026-06-01"))  # ancien succès épinglé en tête
        r = benchmark.analyser({"username": "x", "media": posts}, today=self.TODAY)
        self.assertEqual(r["a_part"][0]["motif"], "épinglée")
        self.assertEqual(r["signaux"], [])

    def test_epinglees(self):
        media = [{"timestamp": "2025-01-01"}, {"timestamp": "2026-11-01"}, {"timestamp": "2026-10-01"}]
        self.assertEqual(benchmark.epinglees(media), {0})
        self.assertEqual(benchmark.epinglees(media[1:]), set())

    def test_analyser(self):
        posts = [self.post(i, 10, f"2026-10-{i + 1:02d}") for i in range(12)]
        posts.insert(0, self.post(99, 500, "2026-10-20"))                       # signal 50x
        posts.append(self.post(98, 900, "2026-10-21", cap="JEU CONCOURS : à gagner"))  # mis à part
        posts.append(self.post(97, 10, "2026-11-10"))                           # trop récent (< 7 j)
        posts.append(self.post(96, 10, "2026-01-10"))                           # trop ancien (> 180 j)
        posts += [self.post(50 + i, 30, f"2026-09-{i + 1:02d}", kind="REELS", mtype="VIDEO") for i in range(4)]
        posts.sort(key=lambda p: p["timestamp"], reverse=True)  # ordre de l'API : du plus récent au plus ancien
        r = benchmark.analyser({"username": "x", "media": posts}, today=self.TODAY)
        self.assertEqual(r["groupes"]["IMAGE"], {"n": 13, "mediane": 10, "statut": "classé"})
        self.assertEqual(r["groupes"]["REELS"]["statut"], "échantillon trop petit")
        self.assertEqual([s["permalink"] for s in r["signaux"]], ["p99"])
        self.assertEqual(r["signaux"][0]["multiple"], 50.0)
        self.assertEqual([p["motif"] for p in r["a_part"]], ["hors organique (concours, partenariat)"])
        self.assertEqual(r["a_part"][0]["multiple_indicatif"], 90.0)

    def test_hidden_likes_set_aside(self):
        posts = [self.post(i, 10, f"2026-10-{i + 1:02d}") for i in range(10)] + [
            dict(self.post(77, 0, "2026-10-15"), like_count=None)]
        posts.sort(key=lambda p: p["timestamp"], reverse=True)
        r = benchmark.analyser({"username": "x", "media": posts}, today=self.TODAY)
        self.assertEqual(r["a_part"][0]["motif"], "interactions masquées")


class TestPagination(unittest.TestCase):
    def test_two_pages(self):
        calls = []

        def route(u, p):
            calls.append(p["fields"])
            if "after(" in p["fields"]:
                return FakeResp(200, {"business_discovery": {"username": "a", "media": {"data": [media(3, 1)]}}})
            return FakeResp(200, {"business_discovery": {"username": "a", "media": {
                "data": [media(1, 1), media(2, 1)], "paging": {"cursors": {"after": "C1"}, "next": "n"}}}})
        s = FakeSession([(lambda u, p: True, route)])
        acc = benchmark.discover(IGClient("1", session=s, version=""), "a", n=3, page=2)
        self.assertEqual(len(acc["media"]), 3)
        self.assertIn("media.after(C1).limit(1)", calls[1])


if __name__ == "__main__":
    unittest.main()
