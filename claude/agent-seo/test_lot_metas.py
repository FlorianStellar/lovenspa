"""Contrôles d'un lot titles/metas avant écriture : longueurs, requête présente, unicité, changement réel."""
import json, sys, unicodedata, unittest

PATH = sys.argv.pop(1) if len(sys.argv) > 1 and sys.argv[1].endswith(".json") else "claude/lots/L8_valeurs.json"

def norm(s): return unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()

class T(unittest.TestCase):
    rows = json.load(open(PATH, encoding="utf-8"))
    def test_count(self): self.assertLessEqual(len(self.rows), 30)
    def test_lengths(self):
        for r in self.rows:
            self.assertLessEqual(len(r["new_title"]), 60, r["url"]); self.assertGreaterEqual(len(r["new_title"]), 30, r["url"])
            self.assertTrue(120 <= len(r["new_desc"]) <= 158, (r["url"], len(r["new_desc"])))
    def test_query_head_in_title(self):
        for r in self.rows:
            head = norm(r["requete"]).replace("felation", "fellation").replace("dayuse", "dayuse").split()[0]
            self.assertIn(head[:5], norm(r["new_title"]), r["url"])
    def test_changed_and_unique(self):
        self.assertEqual(len({r["new_title"] for r in self.rows}), len(self.rows))
        for r in self.rows:
            self.assertNotEqual(r["new_title"], r["old_title"]); self.assertNotEqual(r["new_desc"], r["old_desc"])
    def test_no_price_or_booking_promise(self):
        for r in self.rows:
            for w in ("€", "réserv", "prix"):
                self.assertNotIn(w, (r["new_title"] + r["new_desc"]).lower().replace("quand réserver", ""), r["url"])

if __name__ == "__main__":
    unittest.main()
