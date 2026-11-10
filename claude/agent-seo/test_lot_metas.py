"""Contrôles d'un lot titles/metas avant écriture : longueurs, requête présente, unicité, changement réel."""
import json, sys, unicodedata, unittest

SUFFIXE = " | Love’nSpa"  # ajouté par le thème au <title>

PATH = sys.argv.pop(1) if len(sys.argv) > 1 and sys.argv[1].endswith(".json") else "claude/lots/L8_valeurs.json"

STOP = {"le", "la", "les", "l", "de", "des", "du", "un", "une"}

def norm(s): return unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()

class T(unittest.TestCase):
    rows = json.load(open(PATH, encoding="utf-8"))
    def test_count(self): self.assertLessEqual(len(self.rows), 30)
    def test_lengths(self):
        for r in self.rows:
            self.assertLessEqual(len(r["new_title"] + SUFFIXE), 60, (r["url"], len(r["new_title"] + SUFFIXE))); self.assertGreaterEqual(len(r["new_title"]), 30, r["url"])
            self.assertTrue(120 <= len(r["new_desc"]) <= 158, (r["url"], len(r["new_desc"])))
    def test_query_head_in_title(self):
        for r in self.rows:
            head = [w for w in norm(r["requete"]).replace("felation", "fellation").split() if w not in STOP][0]
            self.assertIn(head[:5], norm(r["new_title"]), r["url"])
    def test_changed_and_unique(self):
        self.assertEqual(len({r["new_title"] for r in self.rows}), len(self.rows))
        for r in self.rows:
            self.assertNotEqual(r["new_title"], r["old_title"]); self.assertNotEqual(r["new_desc"], r["old_desc"])
    def test_no_price_or_booking_promise(self):
        for r in self.rows:
            txt = (r["new_title"] + r["new_desc"]).lower()
            for w in ("€", "prix", "réservez", "réservation en ligne", "réserver en ligne"):
                self.assertNotIn(w, txt, r["url"])

if __name__ == "__main__":
    unittest.main()
