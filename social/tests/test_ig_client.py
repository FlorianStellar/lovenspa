import os
import unittest
from unittest import mock

from social.connecteurs import instagram as ig_client
from social.connecteurs.instagram import IGClient, IGError, invalid_metric


class FakeResp:
    def __init__(self, status, data):
        self.status_code = status
        self._data = data

    def json(self):
        return self._data


class FakeSession:
    """Répond selon (chemin, metric) ; enregistre les appels."""

    def __init__(self, routes):
        self.routes = routes
        self.headers = {}
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params))
        for key, resp in self.routes:
            if key(url, params or {}):
                return resp(url, params or {}) if callable(resp) else resp
        return FakeResp(404, {"error": {"message": "no route", "code": 803}})


class TestInvalidMetric(unittest.TestCase):
    def test_not_supported_form(self):
        e = IGError("(#100) The Media Insights API does not support the follows metric for this media product type.")
        self.assertEqual(invalid_metric(e, ["reach", "follows", "saved"]), "follows")

    def test_must_be_one_of_form(self):
        e = IGError("(#100) metric[1] must be one of the following values: reach, saved, likes")
        self.assertEqual(invalid_metric(e, ["reach", "views", "saved"]), "views")

    def test_unknown(self):
        self.assertIsNone(invalid_metric(IGError("Invalid OAuth access token"), ["reach"]))


class TestClient(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.object(ig_client.time, "sleep", lambda s: None)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_url_versioning(self):
        s = FakeSession([])
        self.assertEqual(IGClient("1", session=s, version="").url("me"), "https://graph.facebook.com/me")
        self.assertEqual(IGClient("1", session=s, version="v24.0").url("/me"), "https://graph.facebook.com/v24.0/me")
        self.assertEqual(IGClient("1", session=s, version="").url("https://x/y"), "https://x/y")

    def test_auth_header_never_needs_token(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            s = FakeSession([])
            IGClient("1", session=s)
            self.assertTrue(s.headers["Authorization"].startswith("Bearer "))

    def test_discover_user_id(self):
        pages = {"data": [
            {"name": "Autre", "instagram_business_account": {"id": "9", "username": "autre"}},
            {"name": "Love'nSpa", "instagram_business_account": {"id": "178", "username": "lovenspa.fr"}},
            {"name": "Sans IG"}]}
        s = FakeSession([(lambda u, p: u.endswith("me/accounts"), FakeResp(200, pages))])
        c = IGClient(session=s, version="")
        c.user_id = None
        self.assertEqual(c.discover_user_id("lovenspa.fr"), "178")

    def test_discover_missing_raises(self):
        s = FakeSession([(lambda u, p: u.endswith("me/accounts"), FakeResp(200, {"data": []}))])
        c = IGClient(session=s, version="")
        c.user_id = None
        with self.assertRaises(IGError):
            c.discover_user_id("lovenspa.fr")

    def test_pagination_complete(self):
        p1 = {"data": [{"id": "a"}, {"id": "b"}], "paging": {"next": "https://graph.facebook.com/next2"}}
        p2 = {"data": [{"id": "c"}], "paging": {}}
        s = FakeSession([(lambda u, p: u.endswith("next2"), FakeResp(200, p2)),
                         (lambda u, p: u.endswith("1/media"), FakeResp(200, p1))])
        self.assertEqual([m["id"] for m in IGClient("1", session=s, version="").media()], ["a", "b", "c"])

    def test_rate_limit_retry(self):
        seq = [FakeResp(400, {"error": {"code": 4, "message": "limit"}}), FakeResp(200, {"id": "1", "username": "lovenspa.fr"})]
        s = FakeSession([(lambda u, p: True, lambda u, p: seq.pop(0))])
        self.assertEqual(IGClient("1", session=s, version="").get("1")["username"], "lovenspa.fr")

    def test_auth_error_raises(self):
        s = FakeSession([(lambda u, p: True, FakeResp(400, {"error": {"code": 190, "message": "Invalid OAuth access token"}}))])
        with self.assertRaises(IGError) as ctx:
            IGClient("1", session=s, version="").get("1")
        self.assertEqual(ctx.exception.code, 190)

    def test_media_insights_drops_refused_metric(self):
        def route(u, p):
            if "follows" in p["metric"]:
                return FakeResp(400, {"error": {"code": 100, "message": "does not support the follows metric"}})
            names = p["metric"].split(",")
            return FakeResp(200, {"data": [{"name": n, "values": [{"value": 10}]} for n in names]})
        s = FakeSession([(lambda u, p: u.endswith("/insights"), route)])
        vals, refused = IGClient("1", session=s, version="").media_insights({"id": "m1", "media_product_type": "FEED"})
        self.assertEqual(refused, ["follows"])
        self.assertEqual(vals["reach"], 10)
        self.assertNotIn("follows", vals)

    def test_reels_ask_watch_time(self):
        seen = {}

        def route(u, p):
            seen["m"] = p["metric"]
            return FakeResp(200, {"data": []})
        s = FakeSession([(lambda u, p: u.endswith("/insights"), route)])
        IGClient("1", session=s, version="").media_insights({"id": "r1", "media_product_type": "REELS"})
        self.assertIn("ig_reels_avg_watch_time", seen["m"])

    def test_total_value_shape(self):
        data = {"data": [{"name": "views", "total_value": {"value": 42}}]}
        s = FakeSession([(lambda u, p: u.endswith("/insights"), FakeResp(200, data))])
        vals, _ = IGClient("1", session=s, version="").media_insights({"id": "m"})
        self.assertEqual(vals["views"], 42)

    def test_reach_by_follow_type(self):
        data = {"data": [{"name": "reach", "total_value": {"breakdowns": [{"results": [
            {"dimension_values": ["FOLLOWER"], "value": 300}, {"dimension_values": ["NON_FOLLOWER"], "value": 700}]}]}}]}
        s = FakeSession([(lambda u, p: u.endswith("1/insights"), FakeResp(200, data))])
        out = IGClient("1", session=s, version="").account_reach_by_follow_type("2026-10-01", "2026-10-30")
        self.assertEqual(out, {"FOLLOWER": 300, "NON_FOLLOWER": 700})


if __name__ == "__main__":
    unittest.main()
