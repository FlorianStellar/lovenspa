"""Candidats au rafraîchissement de contenu (détecteur déclin, filtré saisonnalité).

Usage : python refresh.py <hebdo_courant.json> <hebdo_semaine_precedente.json> <sortie.json> [pages.csv]
pages.csv (export plat) : seules les URL publiées y figurant restent candidates (exclut non publiées, redirigées, 404).
Candidat = page en déclin (det_declin, ≤ -20 % sur 28 j) deux semaines de suite
ET en baisse d'au moins 20 % sur la même fenêtre de 28 j un an plus tôt (année N-1, GSC final),
hors /en/ (exclu de l'univers cible, décision du 10/11) et hors URL gelées.
"""
import json, re, sys
from pathlib import Path
from datetime import date, timedelta

SEUIL_YOY = -20.0


GELEES = Path(__file__).resolve().parent.parent / "lots" / "URL-GELEES.md"


def gelees(path=GELEES):
    """URL gelées ; erreur si le registre manque (jamais d'exclusion silencieusement vide)."""
    texte = Path(path).read_text(encoding="utf-8")
    urls = set(re.findall(r"^\| (/\S+) \|", texte, re.M))
    if not urls:
        raise ValueError(f"registre des URL gelées vide ou illisible : {path}")
    return urls


def chemin(url):
    return re.sub(r"^https?://[^/]+", "", url)


def persistants(cur, prev, exclues=frozenset()):
    p = {d["page"] for d in prev.get("det_declin", [])}
    return [d for d in cur.get("det_declin", [])
            if d["page"] in p and "/en/" not in d["page"] and chemin(d["page"]) not in exclues]


def an_moins_un(periode):
    f = lambda s: str(date.fromisoformat(s) - timedelta(days=364))  # même jour de semaine
    return f(periode[0]), f(periode[1])


def publiees(pages_csv):
    import csv
    with open(pages_csv, encoding="utf-8") as f:
        return {r["url"] for r in csv.DictReader(f) if r.get("publie") == "True"}


def apparier(cands):
    """Répartit les candidats en lot / témoin équilibrés : tri par clics N-1 décroissants, alternance."""
    tri = sorted(cands, key=lambda d: -d["clicks_prev"])
    return tri[0::2], tri[1::2]


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
    if Path(argv[1]).resolve() == Path(argv[2]).resolve():
        raise SystemExit("hebdo courant et précédent identiques : persistance non mesurable")
    with open(argv[1]) as f1, open(argv[2]) as f2:
        cur, prev = json.load(f1), json.load(f2)
    cands = persistants(cur, prev, gelees())
    exclues_pub = []
    if len(argv) > 4:
        pub = publiees(argv[4])
        exclues_pub = [d["page"] for d in cands if chemin(d["page"]) not in pub]
        cands = [d for d in cands if chemin(d["page"]) in pub]
    s, e = an_moins_un(cur["periode"])
    rows = GSCClient().search_analytics_all(s, e, dimensions=["page"]) if cands else []
    n1 = {r["keys"][0]: r["clicks"] for r in rows}
    retenus = filtrer_yoy(cands, n1)
    lot, temoin = apparier(retenus)
    res = {"periode": cur["periode"], "periode_n1": [s, e], "persistants": len(cands),
           "non_publiees_exclues": exclues_pub,
           "sans_historique_n1": [d["page"] for d in cands if not n1.get(d["page"])],
           "candidats": retenus, "lot_propose": lot, "temoin_propose": temoin}
    with open(argv[3], "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f"déclin persistant : {len(cands)} (dont {len(res['sans_historique_n1'])} sans N-1, écartés), {len(exclues_pub)} non publiées exclues ; "
          f"candidats : {len(retenus)} ; lot {len(lot)} / témoin {len(temoin)}")
    for c in retenus:
        print(" ", c["page"], c["delta_pct"], "% 28j ;", c["yoy_pct"], "% N-1")
    return 0 if retenus else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
