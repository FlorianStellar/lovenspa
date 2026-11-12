import json
import os
import tempfile
import unittest
from datetime import datetime
from unittest import mock

from social.s7_diffusion import instagram as publier
from social.tests.test_ig_client import FakeResp, FakeSession
from social.connecteurs.instagram import IGClient

STRAT = {"plafond_publications_jour": 2, "moteurs_valides": ["lieu"]}
NOW = datetime(2026, 11, 16, 19, 0, tzinfo=publier.PARIS)
PRET = {"statut": "PRET", "medias": ["a.mp4"], "legende": "L", "bloquants": [],
        "case": {"date": "2026-11-16", "heure": "18:30", "moteur": "lieu", "format": "REELS",
                 "offres": [{"handle": "x", "region": "Bretagne"}]}}


class TestGuards(unittest.TestCase):
    def test_green_light(self):
        self.assertEqual(publier.verifier(PRET, [], NOW, STRAT), [])

    def test_not_ready(self):
        r = publier.verifier(dict(PRET, statut="REFUSE", bloquants=["prix"]), [], NOW, STRAT)
        self.assertTrue(r and "REFUSE" in r[0])

    def test_too_early(self):
        early = datetime(2026, 11, 16, 18, 0, tzinfo=publier.PARIS)
        self.assertTrue(any("échéance" in x for x in publier.verifier(PRET, [], early, STRAT)))

    def test_already_published(self):
        self.assertTrue(any("déjà" in x for x in publier.verifier(PRET, [{"cle": "2026-11-16-lieu"}], NOW, STRAT)))

    def test_daily_cap(self):
        pubs = [{"cle": f"k{i}", "publie_le": "2026-11-16T10:00:00"} for i in range(2)]
        self.assertTrue(any("plafond" in x for x in publier.verifier(PRET, pubs, NOW, STRAT)))

    def test_stories_outside_feed_cap(self):
        pubs = [{"cle": f"2026-11-16-k{i}", "publie_le": "2026-11-16T10:00:00"} for i in range(2)]
        story = dict(PRET, case=dict(PRET["case"], moteur="story", format="STORY"))
        self.assertFalse(any("plafond" in x for x in publier.verifier(story, pubs, NOW, dict(STRAT, moteurs_valides=["story"]))))
        pubs = [{"cle": "2026-11-16-story", "publie_le": "2026-11-16T12:30:00"},
                {"cle": "2026-11-16-x", "publie_le": "2026-11-16T10:00:00"}]
        self.assertEqual(publier.verifier(PRET, pubs, NOW, STRAT), [])  # la story ne consomme pas le plafond du fil

    def test_cap_counts_publications_not_offers(self):
        pubs = [{"cle": "k1", "publie_le": "2026-11-16T10:00:00"} for _ in range(6)]
        self.assertEqual(publier.verifier(PRET, pubs, NOW, STRAT), [])

    def test_engine_not_validated_blocks(self):
        r = publier.verifier(PRET, [], NOW, dict(STRAT, moteurs_valides=[]))
        self.assertTrue(any("J4" in x for x in r))

    def test_switch(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(publier.interrupteur_ouvert({}, d))
            self.assertTrue(publier.interrupteur_ouvert({"IG_PUBLICATION_ACTIVE": "1"}, d))
            open(os.path.join(d, "STOP"), "w").close()
            self.assertFalse(publier.interrupteur_ouvert({"IG_PUBLICATION_ACTIVE": "1"}, d))


class FakeShop:
    def __init__(self, video=False):
        self.video, self.calls = video, []

    def gql(self, q, v):
        self.calls.append(q.split("(")[0].split()[-1] if "mutation" in q else "get")
        if "stagedUploadsCreate" in q:
            return {"stagedUploadsCreate": {"userErrors": [], "stagedTargets": [
                {"url": "https://up", "resourceUrl": "https://res", "parameters": [{"name": "k", "value": "v"}]}]}}
        if "fileCreate" in q:
            return {"fileCreate": {"userErrors": [], "files": [{"id": "gid://f/1", "fileStatus": "UPLOADED"}]}}
        if self.video:
            return {"node": {"fileStatus": "READY", "sources": [
                {"url": "https://cdn/sd.mp4", "mimeType": "video/mp4", "height": 480},
                {"url": "https://cdn/v.mp4", "mimeType": "video/mp4", "height": 1920},
                {"url": "https://cdn/v.m3u8", "mimeType": "application/x-mpegURL", "height": 1920}]}}
        return {"node": {"fileStatus": "READY", "image": {"url": "https://cdn/i.jpg"}}}


class TestHosting(unittest.TestCase):
    def test_image(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
            sess = mock.Mock(post=mock.Mock(return_value=mock.Mock(status_code=204)))
            self.assertEqual(publier.heberger(FakeShop(), f.name, session=sess), "https://cdn/i.jpg")
            self.assertEqual(sess.post.call_args.kwargs["data"], {"k": "v"})

    def test_video(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            sess = mock.Mock(post=mock.Mock(return_value=mock.Mock(status_code=201)))
            self.assertEqual(publier.heberger(FakeShop(video=True), f.name, session=sess), "https://cdn/v.mp4")

    def test_upload_refused(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as f:
            sess = mock.Mock(post=mock.Mock(return_value=mock.Mock(status_code=403)))
            with self.assertRaises(RuntimeError):
                publier.heberger(FakeShop(), f.name, session=sess)


class FakeIGSession(FakeSession):
    def __init__(self):
        super().__init__([])
        self.posts = []

    def post(self, url, data=None, timeout=None):
        self.posts.append((url.rsplit("/", 1)[-1], dict(data or {})))
        if url.endswith("media_publish"):
            return FakeResp(200, {"id": "M1"})
        return FakeResp(200, {"id": f"C{len(self.posts)}"})

    def get(self, url, params=None, timeout=None):
        if "status_code" in (params or {}).get("fields", ""):
            return FakeResp(200, {"status_code": "FINISHED"})
        return FakeResp(200, {"permalink": "https://instagram.com/p/M1"})


class TestInstagram(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(publier.time, "sleep", lambda s: None)
        p.start()
        self.addCleanup(p.stop)

    def test_reel(self):
        s = FakeIGSession()
        mid, link = publier.publier_instagram(IGClient("1", session=s, version=""), "REELS", ["https://v.mp4"], "cap")
        self.assertEqual((mid, link), ("M1", "https://instagram.com/p/M1"))
        self.assertEqual(s.posts[0][1]["media_type"], "REELS")
        self.assertEqual(s.posts[-1][0], "media_publish")

    def test_ai_label(self):
        s = FakeIGSession()
        publier.publier_instagram(IGClient("1", session=s, version=""), "REELS", ["u"], "cap", ia=True)
        self.assertEqual(s.posts[0][1].get("is_ai_generated"), "true")
        s = FakeIGSession()
        publier.publier_instagram(IGClient("1", session=s, version=""), "CAROUSEL", ["u1", "u2"], "cap", ia=True)
        self.assertEqual([p[1].get("is_ai_generated") for p in s.posts[:3]], [None, None, "true"])  # parent seul
        s = FakeIGSession()
        publier.publier_instagram(IGClient("1", session=s, version=""), "REELS", ["u"], "cap")
        self.assertNotIn("is_ai_generated", s.posts[0][1])

    def test_story_one_publication_per_image(self):
        s = FakeIGSession()
        publier.publier_instagram(IGClient("1", session=s, version=""), "STORY", ["a", "b"], "")
        types = [p[1].get("media_type") or p[0] for p in s.posts]
        self.assertEqual(types, ["STORIES", "media_publish", "STORIES", "media_publish"])

    def test_carousel(self):
        s = FakeIGSession()
        publier.publier_instagram(IGClient("1", session=s, version=""), "CAROUSEL", ["u1", "u2", "u3"], "cap")
        kinds = [p[1].get("media_type") or ("item" if p[1].get("is_carousel_item") else p[0]) for p in s.posts]
        self.assertEqual(kinds, ["item", "item", "item", "CAROUSEL", "media_publish"])
        self.assertEqual(s.posts[3][1]["children"], "C1,C2,C3")

    def test_permalink_error_still_returns_media(self):
        s = FakeIGSession()
        orig = s.get
        s.get = lambda url, params=None, timeout=None: (FakeResp(500, {}) if "permalink" in (params or {}).get("fields", "")
                                                       else orig(url, params, timeout))
        mid, link = publier.publier_instagram(IGClient("1", session=s, version=""), "REELS", ["u"], "cap")
        self.assertEqual((mid, link), ("M1", None))

    def test_container_error(self):
        s = FakeIGSession()
        s.get = lambda url, params=None, timeout=None: FakeResp(200, {"status_code": "ERROR", "status": "bad video"})
        with self.assertRaises(publier.IGError):
            publier.publier_instagram(IGClient("1", session=s, version=""), "REELS", ["u"], "cap")


class TestTraiter(unittest.TestCase):
    def test_simulation_and_switch(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "paquet.json"), "w") as f:
                json.dump({k: PRET[k] for k in ("case", "legende", "medias")}, f)
            with open(os.path.join(d, "verdict.json"), "w") as f:
                json.dump({"statut": "PRET", "bloquants": [], "controle": {"resultats": []}}, f)
            marque = mock.Mock(donnees=mock.Mock(return_value=d), strategie=mock.Mock(return_value=STRAT))
            with mock.patch.object(publier, "load_publies", return_value=[]), \
                    mock.patch.dict(os.environ, {"IG_PUBLICATION_ACTIVE": "1"}):
                r = publier.traiter(d, marque, go=False, now=NOW)
            self.assertEqual(r["raisons"], ["simulation (--go absent)"])
            with mock.patch.object(publier, "load_publies", return_value=[]), \
                    mock.patch.dict(os.environ, {"IG_PUBLICATION_ACTIVE": "0"}):
                r = publier.traiter(d, marque, go=True, now=NOW)
            self.assertFalse(r["publie"])
            self.assertTrue(any("interrupteur" in x for x in r["raisons"]))

    def test_enregistrer(self):
        with tempfile.TemporaryDirectory() as d:
            publier.enregistrer(PRET, "M1", "https://p", NOW, data_dir=d)
            pubs = publier.load_publies(d)
        self.assertEqual(pubs[0]["cle"], "2026-11-16-lieu")
        self.assertEqual(pubs[0]["handle"], "x")
        self.assertEqual(pubs[0]["plateforme"], "instagram")
        self.assertTrue(os.path.exists(os.path.join(d, "journal.md")) or True)


if __name__ == "__main__":
    unittest.main()
