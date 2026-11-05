#!/usr/bin/env python3
"""Audit d'indexation des fiches produit via l'API URL Inspection (jeu complet, même date).

Usage : audit_indexation.py <products.tsv> <sitemap_products.txt> <sortie.csv>
products.tsv : handle, status, templateSuffix, onlineStoreUrl (export Shopify complet).
Reprise : les URL déjà présentes dans le CSV de sortie sans erreur ne sont pas réinspectées.
"""
import csv, os, sys, time
from collections import Counter

BASE = "https://lovenspa.fr/products/"
COLS = ["handle", "shopify_status", "template", "in_sitemap", "url", "verdict", "coverageState",
        "indexingState", "pageFetchState", "robotsTxtState", "lastCrawlTime", "googleCanonical",
        "userCanonical", "canonical_ok", "error"]


def load_products(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if not p or not p[0]:
                continue
            p += [""] * (4 - len(p))
            rows.append({"handle": p[0], "shopify_status": p[1], "template": p[2]})
    return rows


def build_universe(products, sitemap_urls):
    """Une ligne par handle unique, URL canonique publique, appartenance au sitemap."""
    sm = {u.strip().rstrip("/") for u in sitemap_urls if u.strip()}
    seen, out = set(), []
    for p in products:
        if p["handle"] in seen:
            continue
        seen.add(p["handle"])
        url = BASE + p["handle"]
        out.append({**p, "url": url, "in_sitemap": "oui" if url in sm else "non"})
    return out


def flatten(base, res):
    r = {**base, **{k: res.get(k, "") for k in COLS if k in res}}
    gc, uc = res.get("googleCanonical", ""), res.get("userCanonical", "")
    r["canonical_ok"] = "" if not gc or not uc else ("oui" if gc.rstrip("/") == uc.rstrip("/") else "non")
    r["error"] = res.get("error", "")
    return {c: r.get(c, "") for c in COLS}


def summarize(rows):
    ok = [r for r in rows if not r["error"]]
    return {
        "total": len(rows),
        "erreurs_api": len(rows) - len(ok),
        "par_statut_shopify": Counter(r["shopify_status"] for r in rows),
        "par_coverage_actives": Counter(r["coverageState"] for r in ok if r["shopify_status"] == "ACTIVE"),
        "par_coverage_non_actives": Counter(r["coverageState"] for r in ok if r["shopify_status"] != "ACTIVE"),
        "actives_hors_sitemap": [r["handle"] for r in rows if r["shopify_status"] == "ACTIVE" and r["in_sitemap"] == "non"],
        "canonical_differents": [r["handle"] for r in ok if r["canonical_ok"] == "non"],
    }


def main(prod_path, sm_path, out_path):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from gsc_client import GSCClient
    uni = build_universe(load_products(prod_path), open(sm_path).read().split())
    done = {}
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            done = {r["url"]: r for r in csv.DictReader(f) if not r["error"]}
    c = GSCClient()
    rows = []
    for i, p in enumerate(uni):
        if p["url"] in done:
            rows.append(done[p["url"]]); continue
        rows.append(flatten(p, c.inspect_url(p["url"])))
        time.sleep(0.12)
        if (i + 1) % 100 == 0:
            print(f"{i+1}/{len(uni)}", flush=True)
            write(out_path, rows)
    write(out_path, rows)
    s = summarize(rows)
    for k, v in s.items():
        print(k, dict(v) if isinstance(v, Counter) else v)


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main(*sys.argv[1:4])
