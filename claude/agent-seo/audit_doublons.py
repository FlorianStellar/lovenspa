#!/usr/bin/env python3
"""Audit de paires d'URL en doublon : trafic GSC (16 mois), requêtes, indexation, contenu.
Usage : python3 audit_doublons.py sortie.json
"""
import json, re, sys, time, html as htmlmod, urllib.request, urllib.error
from datetime import date, timedelta

PAIRES = [
    ("collections/cote-d-or", "collections/cote-dor"),
    ("collections/val-d-oise", "collections/val-doise"),
    ("blogs/magazine/week-end-en-amoureux-bretagne", "pages/guide-week-end-amoureux-bretagne"),
    ("blogs/magazine/creer-sa-love-room-l-amour-comme-modele-economique", "pages/creer-sa-love-room-l-amour-comme-modele-economique"),
    ("pages/sauna-recap", "pages/sauna-guide-choisir-utiliser-sauna"),
]
BASE = "https://lovenspa.fr/"

def texte_principal(h):
    """Texte visible du <main> (ou du body), sans scripts/styles/nav/header/footer."""
    m = re.search(r"<main\b.*?</main>", h, re.S | re.I)
    h = m.group(0) if m else h
    h = re.sub(r"<(script|style|noscript|nav|header|footer|svg)\b.*?</\1>", " ", h, flags=re.S | re.I)
    t = htmlmod.unescape(re.sub(r"<[^>]+>", " ", h))
    return re.sub(r"\s+", " ", t).strip()

def mots(t):
    return re.findall(r"[a-zà-öø-ÿœæ0-9']+", t.lower())

def shingles(ws, k=5):
    return {tuple(ws[i:i + k]) for i in range(max(0, len(ws) - k + 1))}

def jaccard(a, b):
    return round(len(a & b) / len(a | b), 3) if (a or b) else 0.0

def agreger(rows):
    """rows GSC (dimension page) -> clics, impressions, position moyenne pondérée par impressions."""
    c = sum(r["clicks"] for r in rows); i = sum(r["impressions"] for r in rows)
    p = round(sum(r["position"] * r["impressions"] for r in rows) / i, 1) if i else None
    return {"clics": c, "impressions": i, "position_ponderee": p}

def balises(h):
    g = lambda p: (re.search(p, h, re.S | re.I) or [None, None])[1]
    return {"title": htmlmod.unescape(g(r"<title>(.*?)</title>") or "").strip(),
            "description": htmlmod.unescape(g(r'<meta name="description" content="([^"]*)"') or ""),
            "h1": [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x)).strip() for x in re.findall(r"<h1\b[^>]*>(.*?)</h1>", h, re.S | re.I)],
            "canonical": g(r'<link rel="canonical" href="([^"]*)"'),
            "robots": g(r'<meta name="robots" content="([^"]*)"')}

def fetch(url):
    for essai in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "lovenspa-seo-audit"}), timeout=30) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After") or 10) * (essai + 1)); continue
            return e.code, ""
    return 429, ""

def main(out):
    sys.path.insert(0, __import__("os").path.dirname(__file__))
    from gsc_client import GSCClient
    g = GSCClient()
    end = (date.today() - timedelta(days=3)).isoformat()
    start = (date.today() - timedelta(days=3 + 486)).isoformat()
    res = {"periode": [start, end], "paires": []}
    for a, b in PAIRES:
        paire = {}
        textes = {}
        for u in (a, b):
            url = BASE + u
            st, h = fetch(url)
            t = texte_principal(h)
            textes[u] = shingles(mots(t))
            flt = [{"dimension": "page", "operator": "equals", "expression": url}]
            pages = g.search_analytics_all(start, end, ["page"], filters=flt)
            reqs = g.search_analytics_all(start, end, ["query"], filters=flt)
            reqs.sort(key=lambda r: -r["impressions"])
            ins = g.inspect_url(url)
            paire[u] = {"http": st, "mots": len(mots(t)), **balises(h), **agreger(pages),
                        "nb_requetes": len(reqs),
                        "top_requetes": [{"q": r["keys"][0], "clics": r["clicks"], "impr": r["impressions"], "pos": round(r["position"], 1)} for r in reqs[:8]],
                        "indexation": {k: ins.get(k) for k in ("coverageState", "googleCanonical", "userCanonical", "lastCrawlTime", "verdict")}}
            time.sleep(2)
        paire["similarite_jaccard_5mots"] = jaccard(textes[a], textes[b])
        res["paires"].append(paire)
        print(a, "|", b, "OK", file=sys.stderr)
    json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main(sys.argv[1])
