"""Alerte de chute quotidienne (GSC, données finales).

Usage : python alerte_chute.py <sortie.json> [--top 40]
Compare les 7 derniers jours finaux à la médiane des 4 blocs de 7 jours précédents,
pour le site entier et pour les pages clés (top N par clics sur les 28 jours précédents,
sur le jeu complet). Sortie : JSON + résumé ; code 2 si au moins une alerte.
"""
import json, sys
from collections import defaultdict
from datetime import date, timedelta
from statistics import median

SEUIL_SITE = -15.0     # % clics site
SEUIL_PAGE = -30.0     # % clics page
MIN_CLICS_PAGE = 20    # base 7 j minimale pour juger une page
SEUIL_POS = 3.0        # dégradation de position moyenne pondérée
MIN_IMPR_POS = 200
SEUIL_POS_CLICS = -10.0  # la dégradation de position doit s'accompagner de -10 % de clics
JOURS = 35


def blocs(fin: date):
    """5 blocs de 7 jours se terminant à `fin` : [courant, -1, -2, -3, -4]."""
    return [(fin - timedelta(days=7 * k + 6), fin - timedelta(days=7 * k)) for k in range(5)]


def agreger(rows, b):
    """rows GSC (keys=[date,page]) -> {page: [ (clics, impr, pos*impr) par bloc ]}."""
    out = defaultdict(lambda: [[0, 0, 0.0] for _ in b])
    for r in rows:
        d, page = date.fromisoformat(r["keys"][0]), r["keys"][1]
        for i, (s, e) in enumerate(b):
            if s <= d <= e:
                x = out[page][i]
                x[0] += r.get("clicks", 0); x[1] += r.get("impressions", 0)
                x[2] += r.get("position", 0) * r.get("impressions", 0)
    return out


def pct(cur, base):
    return None if not base else round((cur - base) / base * 100, 1)


def juger(serie, seuil, min_base):
    """serie = 5 blocs ; renvoie dict ou None."""
    cur = serie[0]
    base_clics = median(x[0] for x in serie[1:])
    base_impr = median(x[1] for x in serie[1:])
    pos_cur = cur[2] / cur[1] if cur[1] else None
    pos_prev = [x[2] / x[1] for x in serie[1:] if x[1]]
    pos_base = median(pos_prev) if pos_prev else None
    res = {"clics": cur[0], "clics_base": base_clics, "var_clics": pct(cur[0], base_clics),
           "impr": cur[1], "impr_base": base_impr, "var_impr": pct(cur[1], base_impr),
           "pos": round(pos_cur, 1) if pos_cur else None,
           "pos_base": round(pos_base, 1) if pos_base else None, "motifs": []}
    if base_clics >= min_base and res["var_clics"] is not None and res["var_clics"] <= seuil:
        res["motifs"].append("clics")
    # position : seulement si les clics baissent aussi (sinon élargissement de la longue traîne)
    if (pos_cur and pos_base and base_impr >= MIN_IMPR_POS and pos_cur - pos_base >= SEUIL_POS
            and res["var_clics"] is not None and res["var_clics"] <= SEUIL_POS_CLICS):
        res["motifs"].append("position")
    return res


def complet(dates_site, fin: date):
    """Vrai si les 35 jours se terminant à `fin` sont tous présents (données finales)."""
    attendu = {str(fin - timedelta(days=k)) for k in range(JOURS)}
    return attendu <= set(dates_site)


def site_blocs(site_rows, b):
    """Total site depuis une requête dimension date en agrégation byProperty."""
    out = [[0, 0, 0.0] for _ in b]
    for r in site_rows:
        d = date.fromisoformat(r["keys"][0])
        for i, (s, e) in enumerate(b):
            if s <= d <= e:
                out[i][0] += r.get("clicks", 0); out[i][1] += r.get("impressions", 0)
                out[i][2] += r.get("position", 0) * r.get("impressions", 0)
    return out


def analyser(rows, fin: date, top=40, site_rows=None):
    b = blocs(fin)
    pages = agreger(rows, b)
    if site_rows is not None:
        site = site_blocs(site_rows, b)
    else:  # repli (tests) : somme des pages
        site = [[0, 0, 0.0] for _ in b]
        for s in pages.values():
            for i, x in enumerate(s):
                for j in range(3):
                    site[i][j] += x[j]
    base28 = {p: sum(x[0] for x in s[1:]) for p, s in pages.items()}
    cles = sorted(base28, key=lambda p: -base28[p])[:top]
    site_res = juger(site, SEUIL_SITE, 1)
    alertes = []
    for p in cles:
        r = juger(pages[p], SEUIL_PAGE, MIN_CLICS_PAGE)
        if r["motifs"]:
            alertes.append({"page": p, **r})
    return {"fenetre": [str(b[0][0]), str(b[0][1])], "base": [str(b[4][0]), str(b[1][1])],
            "pages_cles": len(cles), "site": site_res, "alertes": alertes,
            "alerte_site": bool(site_res["motifs"])}


def main(argv):
    from gsc_client import GSCClient
    top = int(argv[argv.index("--top") + 1]) if "--top" in argv else 40
    c = GSCClient()
    # dernier jour final disponible : on part de J-2 et on recule jusqu'à 35 jours complets
    debut_large = date.today() - timedelta(days=JOURS + 6)
    site_rows = c.search_analytics_all(str(debut_large), str(date.today() - timedelta(days=2)),
                                       dimensions=["date"], aggregate_type="byProperty")
    dates = sorted(r["keys"][0] for r in site_rows)
    fin = date.fromisoformat(dates[-1]) if dates else None
    if not fin or not complet(dates, fin):
        res = {"statut": "incomplet", "dates_recues": len(dates), "derniere": dates[-1] if dates else None}
        json.dump(res, open(argv[1], "w"), ensure_ascii=False, indent=1)
        print("données GSC incomplètes : pas de jugement", res)
        return 3
    rows = c.search_analytics_all(str(fin - timedelta(days=JOURS - 1)), str(fin), dimensions=["date", "page"])
    res = analyser(rows, fin, top, site_rows=site_rows)
    res["statut"] = "complet"
    res["lignes_gsc"] = len(rows)
    json.dump(res, open(argv[1], "w"), ensure_ascii=False, indent=1)
    s = res["site"]
    print(f"site {res['fenetre']}: clics {s['clics']} vs {s['clics_base']} ({s['var_clics']}%), "
          f"alerte_site={res['alerte_site']}, alertes pages={len(res['alertes'])}/{res['pages_cles']}")
    for a in res["alertes"]:
        print(" ", a["page"], a["motifs"], a["var_clics"], a["pos_base"], "->", a["pos"])
    return 2 if res["alerte_site"] or res["alertes"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
