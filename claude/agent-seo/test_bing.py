import io, json, os, tempfile, unittest
from unittest import mock
import bing


class FakeResp(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *a): return False


def fake_opener(payloads):
    def op(url, timeout=60):
        for k, v in payloads.items():
            if f"/{k}?" in url:
                return FakeResp(json.dumps(v).encode())
        raise AssertionError(url)
    return op


D1, D2 = "/Date(1762732800000)/", "/Date(1762819200000-0800)/"  # 2025-11-10, 2025-11-11


class T(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(bing.parse_date(D1), "2025-11-10")
        self.assertEqual(bing.parse_date(D2), "2025-11-11")
        self.assertEqual(bing.parse_date(None), "")

    def test_rows_stats_tri_et_types(self):
        r = bing.rows_stats([{"Date": D2, "Query": "b", "Impressions": "3", "Clicks": 1},
                             {"Date": D1, "Query": "a", "Impressions": 5, "Clicks": None}], "requete")
        self.assertEqual([x["requete"] for x in r], ["a", "b"])
        self.assertEqual(r[0]["clics"], 0)
        self.assertEqual(r[1]["impressions"], 3)

    def test_erreur_api(self):
        with self.assertRaises(RuntimeError):
            bing.call("GetUserSites", "k", fake_opener({"GetUserSites": {"ErrorCode": 3, "Message": "InvalidApiKey"}}))

    def test_e2e_main(self):
        op = fake_opener({
            "GetUserSites": {"d": [{"Url": "https://lovenspa.fr/"}]},
            "GetQueryStats": {"d": [{"Date": D1, "Query": "love room", "Impressions": 10, "Clicks": 2,
                                     "AvgImpressionPosition": 3, "AvgClickPosition": 2}]},
            "GetPageStats": {"d": [{"Date": D1, "Query": "https://lovenspa.fr/", "Impressions": 7, "Clicks": 1}]},
            "GetRankAndTrafficStats": {"d": [{"Date": D2, "Impressions": 4, "Clicks": 1},
                                              {"Date": D1, "Impressions": 6, "Clicks": 2}]},
        })
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"BING_API_KEY": "k"}):
            bing.main(["x", d], opener=op)
            t = open(os.path.join(d, "trafic.csv")).read().splitlines()
            self.assertEqual(t[0], "date,impressions,clics")
            self.assertEqual(t[1], "2025-11-10,6,2")
            self.assertIn("love room", open(os.path.join(d, "queries.csv")).read())

    def test_site_absent(self):
        op = fake_opener({"GetUserSites": {"d": [{"Url": "https://autre.fr/"}]}})
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"BING_API_KEY": "k"}):
            with self.assertRaises(SystemExit):
                bing.main(["x", d], opener=op)

    def test_cle_absente(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit):
                bing.main(["x", "/tmp/x"])


if __name__ == "__main__":
    unittest.main()
