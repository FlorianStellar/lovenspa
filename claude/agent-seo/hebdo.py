#!/usr/bin/env python3
"""Cycle hebdo : KPI GSC 28 j finaux vs 28 j précédents + détecteurs (jeu complet, sans échantillonnage).

Usage : hebdo.py <sortie.json>
Détecteurs : cannibalisation (2 URL ≥ 20 % des impressions), positions 4-15 à volume,
CTR sous la courbe du site (par tranche de position), pages en déclin (clics -20 % sur 28 j).
"""
import json, sys
from collections import defaultdict
from datetime import date

from kpi import normalize_url, totals_by_segment, cannibalization, quick_wins, delta
from etat_des_lieux import periods, collect


def totals(rows):
    c = sum(r["clicks"] for r in rows); i = sum(r["impressions"] for r in rows)
    return {"clicks": c, "impressions": i, "ctr": round(c / i * 100, 2) if i else None}


def by_page(rows):
    out = defaultdict(lambda: {"clicks": 0, "impressions": 0})
    for r in rows:
        p = out[normalize_url(r["keys"][0])]; p["clicks"] += r["clicks"]; p["impressions"] += r["impressions"]
    return out


def declining_pages(cur, prev, drop=-20.0, min_prev_clicks=30):
    c, p = by_page(cur), by_page(prev)
    out = []
    for url, v in p.items():
        if v["clicks"] < min_prev_clicks:
            continue
        now = c.get(url, {"clicks": 0})["clicks"]; d = delta(now, v["clicks"])
        if d is not None and d <= drop:
            out.append({"page": url, "clicks_prev": v["clicks"], "clicks": now, "delta_pct": d})
    return sorted(out, key=lambda x: x["clicks"] - x["clicks_prev"])


def bucket(pos):
    return min(int(pos), 20) if pos >= 1 else 1


def ctr_curve(query_rows):
    agg = defaultdict(lambda: [0, 0])
    for r in query_rows:
        b = agg[bucket(r["position"])]; b[0] += r["clicks"]; b[1] += r["impressions"]
    return {k: round(v[0] / v[1], 4) for k, v in sorted(agg.items()) if v[1]}


def ctr_anomalies(query_rows, curve, min_impr=1000, ratio=0.5):
    out = []
    for r in query_rows:
        exp = curve.get(bucket(r["position"]))
        if r["impressions"] >= min_impr and exp and r["position"] <= 10:
            ctr = r["clicks"] / r["impressions"]
            if ctr < exp * ratio:
                out.append({"query": r["keys"][0], "impressions": r["impressions"], "clicks": r["clicks"],
                            "position": round(r["position"], 1), "ctr_pct": round(ctr * 100, 2),
                            "ctr_attendu_pct": round(exp * 100, 2),
                            "clics_manquants": round(r["impressions"] * exp - r["clicks"])})
    return sorted(out, key=lambda x: -x["clics_manquants"])


def main(out_path):
    from gsc_client import GSCClient
    c = GSCClient()
    (cs, ce), (ps, pe) = periods(date.today())
    cur, prev = collect(c, cs, ce), collect(c, ps, pe)
    tc, tp = totals(cur["pages"]), totals(prev["pages"])
    sc, sp = totals_by_segment(cur["pages"]), totals_by_segment(prev["pages"])
    curve = ctr_curve(cur["queries"])
    res = {
        "periode": [cs, ce], "periode_prev": [ps, pe],
        "global": {**tc, "clicks_prev": tp["clicks"], "impressions_prev": tp["impressions"], "ctr_prev": tp["ctr"],
                   "clicks_delta_pct": delta(tc["clicks"], tp["clicks"]),
                   "impressions_delta_pct": delta(tc["impressions"], tp["impressions"]),
                   "requetes": len(cur["queries"]), "requetes_prev": len(prev["queries"]),
                   "urls": len(cur["pages"]), "urls_prev": len(prev["pages"])},
        "segments": {s: {**v, "clicks_prev": sp.get(s, {}).get("clicks", 0),
                         "clicks_delta_pct": delta(v["clicks"], sp.get(s, {}).get("clicks", 0)),
                         "impr_delta_pct": delta(v["impressions"], sp.get(s, {}).get("impressions", 0))}
                     for s, v in sc.items()},
        "courbe_ctr": curve,
        "det_cannibalisation": cannibalization(cur["qp"])[:30],
        "det_quick_wins": quick_wins(cur["queries"], min_impr=500)[:40],
        "det_ctr_anormal": ctr_anomalies(cur["queries"], curve)[:30],
        "det_declin": declining_pages(cur["pages"], prev["pages"])[:40],
        "nb": {"cannibalisation": len(cannibalization(cur["qp"])),
               "quick_wins": len(quick_wins(cur["queries"], min_impr=500)),
               "ctr_anormal": len(ctr_anomalies(cur["queries"], curve)),
               "declin": len(declining_pages(cur["pages"], prev["pages"]))},
    }
    json.dump(res, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: res[k] for k in ("periode", "periode_prev", "global", "nb")}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
