#!/usr/bin/env python3
"""
Audit des publications Instagram à partir d'un instantané (ig_client.py).

Classe chaque post par :
  multiple   = vues du post / médiane des vues du compte (même format si --par-format)
  partages / portée, enregistrements / portée, abonnements / portée

Règle : aucun chiffre inventé. Un post sans la métrique requise est exclu du calcul
concerné et compté dans la section « complétude ».

Usage :
  python3 audit.py data/snapshot-2026-11-11.json [--depuis 2026-08-01] [--par-format] [--md sortie.md]
"""
import argparse
import json
import statistics
import sys


def metric(post, name):
    v = (post.get("insights") or {}).get(name)
    return v if isinstance(v, (int, float)) else None


def fmt(post):
    """REELS, CAROUSEL, IMAGE ou VIDEO (format de la publication)."""
    if post.get("media_product_type") == "REELS":
        return "REELS"
    return {"CAROUSEL_ALBUM": "CAROUSEL"}.get(post.get("media_type"), post.get("media_type") or "?")


def ratio(num, den):
    if num is None or den in (None, 0):
        return None
    return num / den


def median_of(posts, name):
    vals = [metric(p, name) for p in posts]
    vals = [v for v in vals if v is not None]
    return statistics.median(vals) if vals else None


def enrich(posts, base="views", par_format=False):
    """Ajoute à chaque post : multiple, partages_portee, enregistrements_portee, abonnements_portee."""
    medians = {}
    if par_format:
        for f in {fmt(p) for p in posts}:
            medians[f] = median_of([p for p in posts if fmt(p) == f], base)
    overall = median_of(posts, base)
    out = []
    for p in posts:
        reach = metric(p, "reach")
        med = medians.get(fmt(p)) if par_format else overall
        out.append({
            **p,
            "format": fmt(p),
            "mediane_ref": med,
            "multiple": ratio(metric(p, base), med),
            "partages_portee": ratio(metric(p, "shares"), reach),
            "enregistrements_portee": ratio(metric(p, "saved"), reach),
            "abonnements_portee": ratio(metric(p, "follows"), reach),
        })
    return out


def completeness(posts, names=("views", "reach", "shares", "saved", "follows")):
    return {n: sum(1 for p in posts if metric(p, n) is not None) for n in names}


def rank(rows, key, top=5):
    valid = [r for r in rows if r.get(key) is not None]
    valid.sort(key=lambda r: r[key], reverse=True)
    return valid[:top], valid[-top:][::-1] if len(valid) > top else []


def filter_since(posts, since):
    return [p for p in posts if not since or (p.get("timestamp") or "")[:10] >= since]


def to_markdown(rows, total, since=None):
    def pct(x):
        return "-" if x is None else f"{x * 100:.2f} %"

    def mult(x):
        return "-" if x is None else f"{x:.2f}x"

    def line(r):
        cap = (r.get("caption") or "").split("\n")[0][:70].replace("|", "/")
        return (f"| {r['timestamp'][:10]} | {r['format']} | {mult(r['multiple'])} | {pct(r['partages_portee'])} | "
                f"{pct(r['enregistrements_portee'])} | {metric(r, 'views') or '-'} | {metric(r, 'reach') or '-'} | "
                f"[{cap}]({r.get('permalink', '')}) |")

    head = "| Date | Format | Multiple | Partages/portée | Enreg./portée | Vues | Portée | Post |\n|---|---|---|---|---|---|---|---|"
    comp = completeness(rows)
    out = [f"# Audit Instagram @lovenspa.fr", "",
           f"Périmètre : {len(rows)} publications" + (f" depuis le {since}" if since else "") + f" (compte : {total}).",
           "Complétude des métriques : " + ", ".join(f"{k} {v}/{len(rows)}" for k, v in comp.items()), ""]
    for key, title in (("multiple", "multiple sur la médiane"), ("partages_portee", "partages par portée")):
        top, bottom = rank(rows, key)
        out += [f"## Top 5 par {title}", "", head] + [line(r) for r in top] + [""]
        if bottom:
            out += [f"## 5 derniers par {title}", "", head] + [line(r) for r in bottom] + [""]
    by_fmt = {}
    for r in rows:
        by_fmt.setdefault(r["format"], []).append(r)
    out += ["## Par format (médianes)", "", "| Format | Posts | Vues | Partages/portée | Enreg./portée |", "|---|---|---|---|---|"]
    for f, rs in sorted(by_fmt.items()):
        def med(k):
            v = [r[k] for r in rs if r.get(k) is not None]
            return statistics.median(v) if v else None
        out.append(f"| {f} | {len(rs)} | {median_of(rs, 'views') or '-'} | {pct(med('partages_portee'))} | {pct(med('enregistrements_portee'))} |")
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("snapshot")
    ap.add_argument("--depuis")
    ap.add_argument("--par-format", action="store_true")
    ap.add_argument("--md")
    a = ap.parse_args(argv)
    with open(a.snapshot, encoding="utf-8") as f:
        snap = json.load(f)
    posts = filter_since(snap["publications"], a.depuis)
    rows = enrich(posts, par_format=a.par_format)
    md = to_markdown(rows, len(snap["publications"]), a.depuis)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(md)
    else:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
