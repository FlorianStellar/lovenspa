#!/usr/bin/env python3
"""
S8 Mesure : instantané complet d'un compte (profil, toutes les publications et leurs métriques),
écrit dans donnees/<marque>/<plateforme>/snapshot-AAAA-MM-JJ.json.

Usage :
  python3 -m social.s8_mesure.instantane [--marque <id>] [--check]
"""
import argparse
import json
import sys
from datetime import date

from social.connecteurs.instagram import IGClient, IGError
from social.marque import charger


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--marque")
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true", help="teste seulement la connexion")
    a = ap.parse_args(argv)
    m = charger(a.marque)
    c = IGClient(marque=m)
    if a.check:
        try:
            p = c.profile()
        except IGError as e:
            hint = " (jeton absent ou révoqué)" if e.code in (190, None) else ""
            raise SystemExit(f"ÉCHEC connexion Instagram : {e}{hint}")
        print(f"OK @{p.get('username')} · {p.get('followers_count')} abonnés · {p.get('media_count')} publications")
        return 0
    snap = c.snapshot()
    snap["date"] = date.today().isoformat()
    out = a.out or m.donnees("instagram", f"snapshot-{snap['date']}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(snap, f, ensure_ascii=False, indent=1)
    print(f"{len(snap['publications'])} publications -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
