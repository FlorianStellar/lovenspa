"""Candidats au rafraîchissement de contenu (détecteur déclin, filtré saisonnalité).

Usage : python refresh.py <hebdo_courant.json> <hebdo_semaine_precedente.json> <sortie.json>
Candidat = page en déclin (det_declin, ≤ -20 % sur 28 j) deux semaines de suite
ET en baisse d'au moins 20 % sur la même fenêtre de 28 j un an plus tôt (année N-1, GSC final),
hors /en/ (exclu de l'univers cible, décision du 10/11) et hors URL gelées.
"""
import json, re, sys
from datetime import date, timedelta

SEUIL_YOY = -20.0


def gelees(path="../lots/URL-GELEES.md"):
    try:
        return set(re.findall(r"^\| (/\S+) \|", open(path, encoding="utf-8").read(), re.M))
    except FileNotFoundError:
        return set()


def chemin(url):
    return re.sub(r"^https?://[^/]+", "", url)


def persistants(cur, prev, exclues=frozenset()):
    p = {d["page"] for d in prev.get("det_declin", [])}
    return [d for d in cur.get("det_declin", [])
            if d["page"] in p and "/en/" not in d["page"] and chemin(d["page"]) not in exclues]


def an_moins_un(periode):
    f = lambda s: str(date.fromisoformat(s) - timedelta(days=364))  # même jour de semaine
    return f(periode[0]), f(periode[1])


def filtrer_yoy(cands, clics_n1: dict):
    out = []
    for d in cands:
        n1 = clics_n1.get(d["page"], 0)
        yoy = round((d["clicks"] - n1) / n1 * 100, 1) if n1 else None
        d = {**d, "clicks_n1": n1, "yoy_pct": yoy}
        if yoy is not None and yoy <= SEUIL_YOY:
            out.append(d)
    return out


def main(argv):
    from gsc_client import GSCClient
    cur, prev = json.load(open(argv[1])), json.load(open(argv[2]))
    cands = persistants(cur, prev, gelees())
    s, e = an_moins_un(cur["periode"])
    rows = GSCClient().search_analytics_all(s, e, dimensions=["page"]) if cands else []
    n1 = {r["keys"][0]: r["clicks"] for r in rows}
    res = {"periode": cur["periode"], "periode_n1": [s, e], "persistants": len(cands),
           "candidats": filtrer_yoy(cands, n1)}
    json.dump(res, open(argv[3], "w"), ensure_ascii=False, indent=1)
    print(f"déclin persistant : {len(cands)} ; candidats après filtre N-1 : {len(res['candidats'])}")
    for c in res["candidats"]:
        print(" ", c["page"], c["delta_pct"], "% 28j ;", c["yoy_pct"], "% N-1")


if __name__ == "__main__":
    main(sys.argv)
