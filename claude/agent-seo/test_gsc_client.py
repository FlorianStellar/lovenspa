#!/usr/bin/env python3
"""16 tests unitaires pour gsc_client.py — pas d'appels réseau."""
import sys, os, json, base64, unittest
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.dirname(__file__))
from gsc_client import GSCClient, SITE

SA_STUB = json.dumps({
    "type": "service_account",
    "project_id": "test",
    "private_key_id": "k1",
    "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA0Z3VS5JJcds3xHn/ygWep4PAtEsHAEFGHIJKLMNOPQRSTU\n-----END RSA PRIVATE KEY-----\n",
    "client_email": "test@test.iam.gserviceaccount.com",
    "client_id": "1",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
})
SA_B64 = base64.b64encode(SA_STUB.encode()).decode()

INSPECT_RESP = {
    "inspectionResult": {
        "indexStatusResult": {
            "verdict": "PASS",
            "coverageState": "Submitted and indexed",
            "robotsTxtState": "ALLOWED",
            "indexingState": "INDEXING_ALLOWED",
            "lastCrawlTime": "2026-10-26T10:00:00Z",
            "pageFetchState": "SUCCESSFUL",
            "googleCanonical": "https://www.lovenspa.fr/products/test",
            "userCanonical": "https://www.lovenspa.fr/products/test",
            "referringUrls": ["https://www.lovenspa.fr/collections/love-room"],
            "sitemap": ["https://www.lovenspa.fr/sitemap.xml"],
            "crawledAs": "DESKTOP",
        }
    }
}

ANALYTICS_RESP = {
    "rows": [
        {"keys": ["https://www.lovenspa.fr/"], "clicks": 100, "impressions": 1000, "ctr": 0.1, "position": 5.0},
        {"keys": ["https://www.lovenspa.fr/collections/love-room"], "clicks": 200, "impressions": 5000, "ctr": 0.04, "position": 3.2},
    ]
}


def make_client(env_var="GSC_SA_JSON_B64"):
    os.environ[env_var] = SA_B64
    return GSCClient()


class TestGSCClientInit(unittest.TestCase):
    def test_01_default_site(self):
        c = GSCClient()
        self.assertEqual(c.site, SITE)

    def test_02_custom_site(self):
        c = GSCClient(site="sc-domain:example.com")
        self.assertEqual(c.site, "sc-domain:example.com")

    def test_03_service_cached(self):
        c = make_client()
        with patch("gsc_client.build") as mock_build, \
             patch("gsc_client.service_account.Credentials.from_service_account_info"):
            mock_build.return_value = MagicMock()
            svc1 = c._get_service()
            svc2 = c._get_service()
            self.assertIs(svc1, svc2)
            mock_build.assert_called_once()

    def test_04_missing_env_raises(self):
        os.environ.pop("GSC_SA_JSON_B64", None)
        os.environ.pop("GSC_SA_JSON", None)
        c = GSCClient()
        with self.assertRaises(EnvironmentError):
            c._get_service()

    def test_05_raw_json_env_accepted(self):
        os.environ.pop("GSC_SA_JSON_B64", None)
        os.environ["GSC_SA_JSON"] = SA_STUB
        c = GSCClient()
        with patch("gsc_client.build") as mock_build, \
             patch("gsc_client.service_account.Credentials.from_service_account_info"):
            mock_build.return_value = MagicMock()
            c._get_service()
            mock_build.assert_called_once()


class TestSearchAnalytics(unittest.TestCase):
    def _mock_client(self):
        c = make_client()
        mock_svc = MagicMock()
        mock_svc.searchanalytics().query().execute.return_value = ANALYTICS_RESP
        c._service = mock_svc
        return c, mock_svc

    def test_06_returns_rows(self):
        c, _ = self._mock_client()
        rows = c.search_analytics("2026-10-01", "2026-10-28")
        self.assertEqual(len(rows), 2)

    def test_07_empty_response(self):
        c, mock_svc = self._mock_client()
        mock_svc.searchanalytics().query().execute.return_value = {}
        rows = c.search_analytics("2026-10-01", "2026-10-28")
        self.assertEqual(rows, [])

    def test_08_pagination_stops_on_short_batch(self):
        c = make_client()
        mock_svc = MagicMock()
        mock_svc.searchanalytics().query().execute.return_value = ANALYTICS_RESP
        c._service = mock_svc
        rows = c.search_analytics_all("2026-10-01", "2026-10-28")
        self.assertEqual(len(rows), 2)

    def test_09_row_limit_capped_at_25000(self):
        c, mock_svc = self._mock_client()
        c.search_analytics("2026-10-01", "2026-10-28", row_limit=99_999)
        call_body = mock_svc.searchanalytics().query.call_args[1]["body"]
        self.assertEqual(call_body["rowLimit"], 25_000)

    def test_10_filters_passed_through(self):
        c, mock_svc = self._mock_client()
        filters = [{"dimension": "page", "operator": "contains", "expression": "/products/"}]
        c.search_analytics("2026-10-01", "2026-10-28", filters=filters)
        call_body = mock_svc.searchanalytics().query.call_args[1]["body"]
        self.assertIn("dimensionFilterGroups", call_body)


class TestInspectUrl(unittest.TestCase):
    def _mock_client(self):
        c = make_client()
        mock_svc = MagicMock()
        mock_svc.urlInspection().index().inspect().execute.return_value = INSPECT_RESP
        c._service = mock_svc
        return c, mock_svc

    def test_11_pass_verdict_returned(self):
        c, _ = self._mock_client()
        r = c.inspect_url("https://www.lovenspa.fr/products/test")
        self.assertEqual(r["verdict"], "PASS")

    def test_12_coverage_state_returned(self):
        c, _ = self._mock_client()
        r = c.inspect_url("https://www.lovenspa.fr/products/test")
        self.assertEqual(r["coverageState"], "Submitted and indexed")

    def test_13_lastCrawlTime_truncated(self):
        c, _ = self._mock_client()
        r = c.inspect_url("https://www.lovenspa.fr/products/test")
        self.assertEqual(r["lastCrawlTime"], "2026-10-26")

    def test_14_http_error_returns_error_dict(self):
        from googleapiclient.errors import HttpError
        c = make_client()
        mock_svc = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status = 400
        mock_svc.urlInspection().index().inspect().execute.side_effect = HttpError(mock_resp, b"bad")
        c._service = mock_svc
        r = c.inspect_url("https://www.lovenspa.fr/products/test", retries=1)
        self.assertIn("error", r)


class TestHelpers(unittest.TestCase):
    def test_15_window_respects_lag(self):
        from datetime import date, timedelta
        start, end = GSCClient.window(28, lag=3)
        expected_end = date.today() - timedelta(days=3)
        self.assertEqual(end, str(expected_end))

    def test_16_week_window_correct_span(self):
        from datetime import date
        start, end = GSCClient.week_window("2026-10-19")
        self.assertEqual(start, "2026-10-19")
        self.assertEqual(end, "2026-10-25")


if __name__ == "__main__":
    unittest.main(verbosity=2)
