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

    def test_gelees_independant_du_repertoire(self):
        import os, tempfile
        cwd = os.getcwd()
        try:
            os.chdir(tempfile.gettempdir())
            self.assertIn("/collections/love-room", r.gelees())
        finally:
            os.chdir(cwd)

    def test_gelees_absent_erreur(self):
        with self.assertRaises(FileNotFoundError):
            r.gelees("/nexiste/pas.md")

    def test_publiees(self):
        import tempfile, os
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("type,url,publie\npage,/pages/a,True\npage,/pages/b,False\n")
        try:
            self.assertEqual(r.publiees(f.name), {"/pages/a"})
        finally:
            os.unlink(f.name)

    def test_meme_fichier_refuse(self):
        with self.assertRaises(SystemExit):
            r.main(["x", __file__, __file__, "/tmp/o.json"])

    def test_chemin(self):
        self.assertEqual(r.chemin("https://lovenspa.fr/pages/x"), "/pages/x")

    def test_apparier(self):
        c = [{"page": p, "clicks_prev": n} for p, n in [("a", 10), ("b", 40), ("c", 30), ("d", 20), ("e", 5)]]
        lot, tem = r.apparier(c)
        self.assertEqual([d["page"] for d in lot], ["b", "d", "e"])
        self.assertEqual([d["page"] for d in tem], ["c", "a"])


if __name__ == "__main__":
    unittest.main()
