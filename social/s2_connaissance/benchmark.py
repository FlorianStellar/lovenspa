#!/usr/bin/env python3
"""
S2 Connaissance : benchmark de comptes Instagram professionnels via l'API officielle (Business Discovery,
lecture seule). Liste des comptes : marques/<marque>/comptes_reference_instagram.txt.

Pour chaque compte : abonnés, nombre de posts, et ses N dernières publications
(date, format, likes, commentaires, légende). Les vues ne sont pas exposées par cette API :
l'engagement se mesure en likes + commentaires, rapporté aux abonnés et à la médiane du compte.
Les comptes qui masquent leurs likes renvoient like_count absent : exclus du calcul, signalés.

Usage :
  python3 -m social.s2_connaissance.benchmark [--marque <id>] [--comptes fichier.txt] [--n 50] [--md rapport.md]
"""
import argparse
import json
import os
import statistics
import sys
import time
from datetime import date, datetime, timedelta

from social.connecteurs.instagram import IGClient, IGError
from social.marque import charger

MEDIA = "timestamp,media_type,media_product_type,like_count,comments_count,caption,permalink"


def discover(client, username, n=50):
    uid = client.ensure_user()
    fields = (f"business_discovery.username({username})"
              f"{{username,name,followers_count,media_count,media.limit({n}){{{MEDIA}}}}}")
    data = client.get(uid, {"fields": fields}).get("business_discovery", {})
    data["media"] = (data.get("media") or {}).get("data", [])
    return data


def fmt(m):
    if m.get("media_product_type") == "REELS":
        return "REELS"
    return {"CAROUSEL_ALBUM": "CAROUSEL"}.get(m.get("media_type"), m.get("media_type") or "?")


def engagement(m):
    if not isinstance(m.get("like_count"), int):
        return None
    return m["like_count"] + (m.get("comments_count") or 0)


def summarize(acc, today=None):
    """Indicateurs d'un compte à partir de ses dernières publications (aucune extrapolation)."""
    today = today or date.today()
    media = acc.get("media", [])
    eng = [engagement(m) for m in media]
    eng_ok = [e for e in eng if e is not None]
    med = statistics.median(eng_ok) if eng_ok else None
    dates = sorted(m["timestamp"][:10] for m in media if m.get("timestamp"))
    weeks = None
    if len(dates) >= 2:
        span = (datetime.fromisoformat(dates[-1]) - datetime.fromisoformat(dates[0])).days
        weeks = max(span / 7, 1 / 7)
    formats = {}
    for m in media:
        formats[fmt(m)] = formats.get(fmt(m), 0) + 1
    followers = acc.get("followers_count")
    outliers = []
    if med:
        for m, e in zip(media, eng):
            if e is not None and e >= 3 * med:
                outliers.append({"multiple": round(e / med, 1), "format": fmt(m), "date": m["timestamp"][:10],
                                 "engagement": e, "accroche": (m.get("caption") or "").strip().split("\n")[0][:140],
                                 "permalink": m.get("permalink")})
    outliers.sort(key=lambda o: o["multiple"], reverse=True)
    last = dates[-1] if dates else None
    return {
        "username": acc.get("username"),
        "abonnes": followers,
        "posts_total": acc.get("media_count"),
        "posts_analyses": len(media),
        "likes_masques": len(media) - len(eng_ok),
        "periode": [dates[0], dates[-1]] if dates else None,
        "posts_par_semaine": round(len(media) / weeks, 2) if weeks else None,
        "part_reels": round(formats.get("REELS", 0) / len(media), 2) if media else None,
        "formats": formats,
        "engagement_median": med,
        "taux_engagement_median": round(med / followers * 100, 3) if med is not None and followers else None,
        "dernier_post_jours": (today - date.fromisoformat(last)).days if last else None,
        "outliers": outliers[:10],
    }


def to_markdown(rows, errors):
    def v(x, suf=""):
        return "-" if x is None else f"{x}{suf}"
    out = ["| Compte | Abonnés | Posts | Posts/sem. | Part Reels | Engagement médian | Taux méd. | Dernier post (j) |",
           "|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["abonnes"] or 0, reverse=True):
        out.append(f"| {r['username']} | {v(r['abonnes'])} | {v(r['posts_total'])} | {v(r['posts_par_semaine'])} | "
                   f"{v(None if r['part_reels'] is None else round(r['part_reels'] * 100), ' %')} | "
                   f"{v(r['engagement_median'])} | {v(r['taux_engagement_median'], ' %')} | {v(r['dernier_post_jours'])} |")
    if errors:
        out += ["", "Comptes non lus (personnels, inexistants ou renommés) : " + ", ".join(f"{u} ({e[:60]})" for u, e in errors)]
    out += ["", "## Publications à plus de 3 fois l'engagement médian du compte", ""]
    for r in rows:
        if r["outliers"]:
            out.append(f"### {r['username']}")
            out += [f"- {o['multiple']}x · {o['format']} · {o['date']} · [{o['accroche'] or '(sans légende)'}]({o['permalink']})"
                    for o in r["outliers"][:5]]
            out.append("")
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--marque")
    ap.add_argument("--comptes", help="fichier : un nom d'utilisateur par ligne (défaut : liste de la marque)")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--out")
    ap.add_argument("--md")
    a = ap.parse_args(argv)
    m = charger(a.marque)
    if a.comptes:
        with open(a.comptes, encoding="utf-8") as f:
            users = [l.strip().lstrip("@") for l in f if l.strip() and not l.startswith("#")]
    else:
        users = m.comptes_reference("instagram")
    client = IGClient(marque=m)
    raw, rows, errors = {}, [], []
    for u in users:
        try:
            acc = discover(client, u, a.n)
            raw[u] = acc
            rows.append(summarize(acc))
        except IGError as e:
            errors.append((u, str(e)))
        time.sleep(1)
    today = date.today().isoformat()
    out = a.out or m.donnees("instagram", f"benchmark-{today}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"date": today, "comptes": raw, "erreurs": errors}, f, ensure_ascii=False, indent=1)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(to_markdown(rows, errors))
    print(f"{len(rows)} comptes lus, {len(errors)} non lus -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
