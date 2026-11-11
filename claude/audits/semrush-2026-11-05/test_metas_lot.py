import csv, os, unittest
D = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(D, "metas_lot.csv"), encoding="utf-8")))
avant = {r["handle"]: r["meta_live_avant_2026-11-05"] for r in csv.DictReader(open(os.path.join(D, "metas_avant.tsv"), encoding="utf-8"), delimiter="\t")}
COL = "Metafield: description_tag [string]"
class T(unittest.TestCase):
    def test_six_fiches_sauvegardees(self):
        self.assertEqual(len(rows), 6); self.assertEqual({r["Handle"] for r in rows}, set(avant))
    def test_uniques(self):
        self.assertEqual(len({r[COL] for r in rows}), 6)
    def test_longueur(self):
        for r in rows: self.assertTrue(110 <= len(r[COL]) <= 155, (r["Handle"], len(r[COL])))
    def test_differente_de_avant(self):
        for r in rows: self.assertNotEqual(r[COL], avant[r["Handle"]])
    def test_commande(self):
        for r in rows: self.assertEqual(r["Command"], "UPDATE")
if __name__ == "__main__": unittest.main()
