import json
import os
import tempfile
import unittest
from datetime import datetime
from unittest import mock

import publier
from test_ig_client import FakeResp, FakeSession
from ig_client import IGClient

NOW = datetime(2026, 11, 16, 19, 0, tzinfo=publier.PARIS)
PRET = {"statut": "PRET", "medias": ["a.mp4"], "legende": "L", "bloquants": [],
        "case": {"date": "2026-11-16", "heure": "18:30", "moteur": "lieu", "format": "REELS",
                 "logements": [{"handle": "x", "region": "Bretagne"}]}}


class TestGuards(unittest.TestCase):
    def test_green_light(self):
        self.assertEqual(publier.verifier(PRET, [], NOW), [])

    def test_not_ready(self):
        r = publier.verifier(dict(PRET, statut="REFUSE", bloquants=["prix"]), [], NOW)
        self.assertTrue(r and "REFUSE" in r[0])

    def test_too_early(self):
        early = datetime(2026, 11, 16, 18, 0, tzinfo=publier.PARIS)
        self.assertTrue(any("échéance" in x for x in publier.verifier(PRET, [], early)))

    def test_already_published(self):
        self.assertTrue(any("déjà" in x for x in publier.verifier(PRET, [{"cle": "2026-11-16-lieu"}], NOW)))

    def test_daily_cap(self):
        pubs = [{"cle": f"k{i}", "publie_le": "2026-11-16T10:00:00"} for i in range(2)]
        self.assertTrue(any("plafond" in x for x in publier.verifier(PRET, pubs, NOW)))

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

    def test_carousel(self):
        s = FakeIGSession()
        publier.publier_instagram(IGClient("1", session=s, version=""), "CAROUSEL", ["u1", "u2", "u3"], "cap")
        kinds = [p[1].get("media_type") or ("item" if p[1].get("is_carousel_item") else p[0]) for p in s.posts]
        self.assertEqual(kinds, ["item", "item", "item", "CAROUSEL", "media_publish"])
        self.assertEqual(s.posts[3][1]["children"], "C1,C2,C3")

    def test_container_error(self):
        s = FakeIGSession()
        s.get = lambda url, params=None, timeout=None: FakeResp(200, {"status_code": "ERROR", "status": "bad video"})
        with self.assertRaises(publier.IGError):
            publier.publier_instagram(IGClient("1", session=s, version=""), "REELS", ["u"], "cap")


class TestTraiter(unittest.TestCase):
    def test_simulation_and_switch(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "pret.json"), "w") as f:
                json.dump(PRET, f)
            with mock.patch.object(publier, "load_publies", return_value=[]), \
                    mock.patch.dict(os.environ, {"IG_PUBLICATION_ACTIVE": "1"}):
                r = publier.traiter(d, go=False, now=NOW)
            self.assertEqual(r["raisons"], ["simulation (--go absent)"])
            with mock.patch.object(publier, "load_publies", return_value=[]), \
                    mock.patch.dict(os.environ, {"IG_PUBLICATION_ACTIVE": "0"}):
                r = publier.traiter(d, go=True, now=NOW)
            self.assertFalse(r["publie"])
            self.assertTrue(any("interrupteur" in x for x in r["raisons"]))

    def test_enregistrer(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(publier, "HERE", d):
            publier.enregistrer(PRET, "M1", "https://p", NOW, data_dir=d)
            pubs = publier.load_publies(d)
        self.assertEqual(pubs[0]["cle"], "2026-11-16-lieu")
        self.assertEqual(pubs[0]["handle"], "x")


if __name__ == "__main__":
    unittest.main()
