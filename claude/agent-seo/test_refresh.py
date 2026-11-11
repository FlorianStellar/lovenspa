import unittest
import refresh as r

D = lambda p, c=50: {"page": p, "clicks_prev": 100, "clicks": c, "delta_pct": -50.0}


class T(unittest.TestCase):
    def test_persistants(self):
        cur = {"det_declin": [D("https://lovenspa.fr/a"), D("https://lovenspa.fr/b"), D("https://lovenspa.fr/en/c"), D("https://lovenspa.fr/g")]}
        prev = {"det_declin": [D("https://lovenspa.fr/a"), D("https://lovenspa.fr/en/c"), D("https://lovenspa.fr/g")]}
        out = r.persistants(cur, prev, {"/g"})
        self.assertEqual([d["page"] for d in out], ["https://lovenspa.fr/a"])

    def test_yoy(self):
        c = [D("x", 50), D("y", 50), D("z", 50)]
        out = r.filtrer_yoy(c, {"x": 100, "y": 55})  # z sans historique : écarté
        self.assertEqual([d["page"] for d in out], ["x"])
        self.assertEqual(out[0]["yoy_pct"], -50.0)

    def test_an_moins_un_meme_jour(self):
        from datetime import date
        s, e = r.an_moins_un(["2026-10-10", "2026-11-06"])
        self.assertEqual(date.fromisoformat(s).weekday(), date(2026, 10, 10).weekday())
        self.assertEqual(e, "2025-11-07")

    def test_gelees(self):
        g = r.gelees()
        self.assertIn("/collections/love-room", g)


if __name__ == "__main__":
    unittest.main()
