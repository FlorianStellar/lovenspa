import unittest
from datetime import date, timedelta
import alerte_chute as a

FIN = date(2026, 11, 8)


def rows_for(page, clics_par_bloc, pos_par_bloc=None, impr=100):
    out = []
    for k, c in enumerate(clics_par_bloc):
        for j in range(7):
            d = FIN - timedelta(days=7 * k + j)
            pos = (pos_par_bloc or [5] * 5)[k]
            out.append({"keys": [str(d), page], "clicks": c / 7, "impressions": impr, "position": pos})
    return out


class T(unittest.TestCase):
    def test_blocs(self):
        b = a.blocs(FIN)
        self.assertEqual(b[0], (date(2026, 11, 2), FIN))
        self.assertEqual(len(b), 5)
        self.assertEqual(b[4][0], date(2026, 10, 5))

    def test_pas_alerte_stable(self):
        r = a.analyser(rows_for("/p", [100, 100, 98, 102, 100]), FIN)
        self.assertEqual(r["alertes"], [])
        self.assertFalse(r["alerte_site"])

    def test_chute_page_et_site(self):
        rows = rows_for("/p", [50, 100, 100, 100, 100]) + rows_for("/q", [100, 100, 100, 100, 100])
        r = a.analyser(rows, FIN)
        self.assertEqual([x["page"] for x in r["alertes"]], ["/p"])
        self.assertEqual(r["alertes"][0]["var_clics"], -50.0)
        self.assertTrue(r["alerte_site"])  # -25 %

    def test_base_trop_faible_ignoree(self):
        r = a.analyser(rows_for("/p", [2, 10, 10, 10, 10]), FIN)
        self.assertEqual(r["alertes"], [])

    def test_degradation_position(self):
        r = a.analyser(rows_for("/p", [100] * 5, pos_par_bloc=[9, 4, 4, 5, 4]), FIN)
        self.assertEqual(r["alertes"][0]["motifs"], ["position"])

    def test_top_n(self):
        rows = rows_for("/gros", [1000] * 5) + rows_for("/petit", [0, 30, 30, 30, 30])
        self.assertEqual(a.analyser(rows, FIN, top=1)["pages_cles"], 1)
        self.assertEqual(a.analyser(rows, FIN, top=1)["alertes"], [])


if __name__ == "__main__":
    unittest.main()
