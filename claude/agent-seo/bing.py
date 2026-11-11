"""Collecteur Bing Webmaster Tools (E7).

Usage : python bing.py <dossier_sortie> [site_url]
Lit BING_API_KEY dans l'environnement. Écrit queries.csv, pages.csv, trafic.csv.
"""
import csv, json, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

BASE = "https://ssl.bing.com/webmaster/api.svc/json/"
SITE = "https://lovenspa.fr/"


def parse_date(v):
    """'/Date(1699999999000)/' ou '/Date(1699999999000-0800)/' -> 'YYYY-MM-DD' (UTC)."""
    m = re.search(r"/Date\((-?\d+)", v or "")
    if not m:
        return ""
    return datetime.fromtimestamp(int(m.group(1)) / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def call(method, key, opener=urllib.request.urlopen, **params):
    q = urllib.parse.urlencode({"apikey": key, **params})
    with opener(f"{BASE}{method}?{q}", timeout=60) as r:
        data = json.loads(r.read().decode("utf-8"))
    if isinstance(data, dict) and "ErrorCode" in data:
        raise RuntimeError(f"{method}: {data.get('Message')}")
    return data.get("d", data) if isinstance(data, dict) else data


def rows_stats(items, cle):
    """Normalise GetQueryStats/GetPageStats -> lignes triées (date, cle)."""
    out = [{
        "date": parse_date(it.get("Date")),
        cle: it.get("Query", ""),
        "impressions": int(it.get("Impressions") or 0),
        "clics": int(it.get("Clicks") or 0),
        "pos_impression": it.get("AvgImpressionPosition"),
        "pos_clic": it.get("AvgClickPosition"),
    } for it in items or []]
    return sorted(out, key=lambda r: (r["date"], r[cle]))


def rows_trafic(items):
    out = [{"date": parse_date(it.get("Date")),
            "impressions": int(it.get("Impressions") or 0),
            "clics": int(it.get("Clicks") or 0)} for it in items or []]
    return sorted(out, key=lambda r: r["date"])


def ecrire(path, rows, champs):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(rows)


def main(argv, opener=urllib.request.urlopen):
    key = os.environ.get("BING_API_KEY")
    if not key:
        sys.exit("BING_API_KEY absente")
    out = argv[1]
    site = argv[2] if len(argv) > 2 else SITE
    os.makedirs(out, exist_ok=True)
    sites = [s.get("Url") for s in call("GetUserSites", key, opener)]
    if site not in sites:
        sys.exit(f"site {site} absent du compte Bing : {sites}")
    q = rows_stats(call("GetQueryStats", key, opener, siteUrl=site), "requete")
    p = rows_stats(call("GetPageStats", key, opener, siteUrl=site), "page")
    t = rows_trafic(call("GetRankAndTrafficStats", key, opener, siteUrl=site))
    base = ["date", "impressions", "clics", "pos_impression", "pos_clic"]
    ecrire(os.path.join(out, "queries.csv"), q, ["date", "requete"] + base[1:])
    ecrire(os.path.join(out, "pages.csv"), p, ["date", "page"] + base[1:])
    ecrire(os.path.join(out, "trafic.csv"), t, base[:3])
    print(f"bing {site} : {len(q)} requetes, {len(p)} pages, {len(t)} jours, "
          f"clics {sum(r['clics'] for r in t)}, impressions {sum(r['impressions'] for r in t)}")


if __name__ == "__main__":
    main(sys.argv)
