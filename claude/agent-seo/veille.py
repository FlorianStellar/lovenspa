#!/usr/bin/env python3
"""Veille d'indexation quotidienne.

Usage : veille.py <handles_modifies.txt> <veille_precedente.csv> <sortie.csv>
- handles_modifies.txt : handles des fiches actives modifiées depuis 48 h (un par ligne ou séparés par des espaces).
- veille_precedente.csv : la veille précédente ; ses fiches non indexées sont suivies jusqu'à indexation.
- Collections : toutes celles du sitemap public (leur updated_at Shopify bouge avec leurs produits).
S'arrête proprement sur « Quota exceeded » ; relancer complète les URL manquantes ou en erreur.
"""
import csv, os, re, sys, time, urllib.request
from collections import Counter

BASE = "https://lovenspa.fr"
KEYS = ["url", "verdict", "coverageState", "indexingState", "pageFetchState", "lastCrawlTime",
        "googleCanonical", "userCanonical", "error"]
OK = "Submitted and indexed"


def product_urls(text):
    return [f"{BASE}/products/{h}" for h in re.split(r"\s+", text.strip()) if h]


def watch_urls(prev_rows):
    return [r["url"] for r in prev_rows if "/products/" in r["url"] and r["coverageState"] != OK]


def sitemap_locs(xml, part):
    return [u.replace("&amp;", "&") for u in re.findall(r"<loc>([^<]+)</loc>", xml) if part in u]


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8")


def collection_urls():
    out = []
    for sm in sitemap_locs(fetch(f"{BASE}/sitemap.xml"), "sitemap_collections"):
        out += sitemap_locs(fetch(sm), "/collections/")
    return out


def build_universe(prods, watch, colls):
    """Fiches d'abord (prioritaires si le quota s'épuise), sans doublon."""
    seen, out = set(), []
    for u in list(prods) + list(watch) + list(colls):
        if u not in seen:
            seen.add(u); out.append(u)
    return out


def compare(cur, prev, watch):
    p = {r["url"]: r["coverageState"] for r in prev}
    ok = [r for r in cur if not r["error"]]
    return {
        "inspectees": len(ok), "erreurs": len(cur) - len(ok),
        "suivi": Counter((p.get(r["url"], "?"), r["coverageState"]) for r in ok if r["url"] in watch),
        "nouvelles_anomalies": [(r["url"], p.get(r["url"], "(nouvelle)"), r["coverageState"], r["lastCrawlTime"])
                                for r in ok if r["url"] not in watch and r["coverageState"] != OK
                                and p.get(r["url"]) != r["coverageState"]],
        "canonical_diff": [r["url"] for r in ok if r["googleCanonical"] and r["userCanonical"]
                           and r["googleCanonical"].rstrip("/") != r["userCanonical"].rstrip("/")],
        "anomalies_connues": sum(1 for r in ok if r["url"] not in watch and r["coverageState"] != OK
                                 and p.get(r["url"]) == r["coverageState"]),
    }


def main(handles_path, prev_path, out_path):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from gsc_client import GSCClient
    prev = list(csv.DictReader(open(prev_path, encoding="utf-8")))
    watch = set(watch_urls(prev))
    uni = build_universe(product_urls(open(handles_path).read()), sorted(watch), collection_urls())
    done = {}
    if os.path.exists(out_path):
        done = {r["url"]: r for r in csv.DictReader(open(out_path, encoding="utf-8")) if not r["error"]}
    c, rows, stop = GSCClient(), [], False
    for u in uni:
        if u in done or stop:
            rows.append(done.get(u, {k: "" for k in KEYS} | {"url": u, "error": "non inspectée"})); continue
        r = c.inspect_url(u)
        if "Quota exceeded" in (r.get("error") or ""):
            stop = True; print("QUOTA", time.strftime("%H:%M UTC", time.gmtime()))
        rows.append({k: r.get(k, "") for k in KEYS}); time.sleep(0.12)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KEYS); w.writeheader(); w.writerows(rows)
    s = compare(rows, prev, watch)
    print("univers", len(uni), "fiches", sum('/products/' in u for u in uni), "suivies", len(watch))
    for k, v in s.items():
        print(k, v.most_common() if isinstance(v, Counter) else v)


if __name__ == "__main__":
    main(*sys.argv[1:4])
