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


def cadence(posts, weeks=4, today=None):
    """Publications par semaine et par format sur les `weeks` dernières semaines complètes (lundi-dimanche)."""
    from datetime import date, timedelta
    today = today or date.today()
    start = today - timedelta(days=today.weekday() + 7 * weeks)
    end = today - timedelta(days=today.weekday())
    counts = {}
    for p in posts:
        d = (p.get("timestamp") or "")[:10]
        if d and start.isoformat() <= d < end.isoformat():
            counts[fmt(p)] = counts.get(fmt(p), 0) + 1
    return {"debut": start.isoformat(), "fin": (end - timedelta(days=1)).isoformat(), "semaines": weeks,
            "par_semaine": {k: v / weeks for k, v in sorted(counts.items())}}


def filter_since(posts, since):
    return [p for p in posts if not since or (p.get("timestamp") or "")[:10] >= since]


def show(v):
    return "-" if v is None else v


def to_markdown(rows, total, since=None, reels_cible=3, today=None):
    def pct(x):
        return "-" if x is None else f"{x * 100:.2f} %"

    def mult(x):
        return "-" if x is None else f"{x:.2f}x"

    def line(r):
        cap = (r.get("caption") or "").split("\n")[0][:70].replace("|", "/")
        return (f"| {r['timestamp'][:10]} | {r['format']} | {mult(r['multiple'])} | {pct(r['partages_portee'])} | "
                f"{pct(r['enregistrements_portee'])} | {show(metric(r, 'views'))} | {show(metric(r, 'reach'))} | "
                f"[{cap}]({r.get('permalink', '')}) |")

    head = "| Date | Format | Multiple | Partages/portée | Enreg./portée | Vues | Portée | Post |\n|---|---|---|---|---|---|---|---|"
    comp = completeness(rows)
    out = [f"# Audit Instagram @lovenspa.fr", "",
           f"Périmètre : {len(rows)} publications" + (f" depuis le {since}" if since else "") + f" (compte : {total}).",
           "Complétude des métriques : " + ", ".join(f"{k} {v}/{len(rows)}" for k, v in comp.items()), ""]
    for key, title in (("multiple", "multiple sur la médiane"), ("partages_portee", "partages par portée")):
        n_ok = sum(1 for r in rows if r.get(key) is not None)
        if n_ok * 2 < len(rows):
            out += [f"## Classement par {title} : non publié", "",
                    f"Métrique disponible pour {n_ok}/{len(rows)} publications, moins de la moitié : aucune conclusion.", ""]
            continue
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
        out.append(f"| {f} | {len(rs)} | {show(median_of(rs, 'views'))} | {pct(med('partages_portee'))} | {pct(med('enregistrements_portee'))} |")
    c = cadence(rows, today=today)
    reels = c["par_semaine"].get("REELS", 0)
    out += ["", f"## Cadence ({c['debut']} au {c['fin']}, {c['semaines']} semaines)", "",
            "| Format | Publications par semaine |", "|---|---|"]
    out += [f"| {k} | {v:.2f} |" for k, v in c["par_semaine"].items()]
    out += ["", f"Reels : {reels:.2f} par semaine pour une cible de {reels_cible} "
                f"({'atteinte' if reels >= reels_cible else 'non atteinte'})."]
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
