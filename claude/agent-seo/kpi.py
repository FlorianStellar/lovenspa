"""Fonctions pures de calcul des KPI SEO (aucun appel réseau)."""
from collections import defaultdict
from urllib.parse import urlparse

CANON_HOST = "lovenspa.fr"


def normalize_url(url: str) -> str:
    return url.replace("://www.lovenspa.fr", "://lovenspa.fr").split("#")[0]


def segment(url: str) -> str:
    path = urlparse(normalize_url(url)).path or "/"
    if path.startswith("/en/") or path == "/en":
        return "en"
    if path == "/":
        return "home"
    for prefix, name in (("/products/", "fiche"), ("/collections/", "collection"),
                         ("/pages/", "page"), ("/blogs/", "blog")):
        if path.startswith(prefix):
            return name
    return "autre"


def totals_by_segment(page_rows: list[dict]) -> dict:
    out = defaultdict(lambda: {"clicks": 0, "impressions": 0, "urls": 0})
    for r in page_rows:
        s = out[segment(r["keys"][0])]
        s["clicks"] += r["clicks"]
        s["impressions"] += r["impressions"]
        s["urls"] += 1
    return dict(out)


def cannibalization(query_page_rows: list[dict], min_impr: int = 200,
                    min_share: float = 0.2) -> list[dict]:
    by_q = defaultdict(list)
    for r in query_page_rows:
        by_q[r["keys"][0]].append(r)
    found = []
    for q, rows in by_q.items():
        total = sum(r["impressions"] for r in rows)
        if total < min_impr:
            continue
        strong = [r for r in rows if r["impressions"] / total >= min_share]
        if len(strong) >= 2:
            found.append({
                "query": q,
                "impressions": total,
                "pages": sorted(
                    [{"page": normalize_url(r["keys"][1]),
                      "share": round(r["impressions"] / total, 2),
                      "position": round(r["position"], 1)} for r in strong],
                    key=lambda p: -p["share"]),
            })
    return sorted(found, key=lambda f: -f["impressions"])


def quick_wins(query_rows: list[dict], pos_min: float = 4, pos_max: float = 15,
               min_impr: int = 100) -> list[dict]:
    wins = [
        {"query": r["keys"][0], "impressions": r["impressions"],
         "clicks": r["clicks"], "position": round(r["position"], 1)}
        for r in query_rows
        if pos_min <= r["position"] <= pos_max and r["impressions"] >= min_impr
    ]
    return sorted(wins, key=lambda w: -w["impressions"])


def best_page(query_page_rows: list[dict], query: str) -> dict | None:
    rows = [r for r in query_page_rows if r["keys"][0] == query]
    if not rows:
        return None
    top = max(rows, key=lambda r: r["impressions"])
    return {"page": normalize_url(top["keys"][1]),
            "position": round(top["position"], 1),
            "impressions": sum(r["impressions"] for r in rows),
            "clicks": sum(r["clicks"] for r in rows)}


def delta(cur: float, prev: float) -> float | None:
    if not prev:
        return None
    return round((cur - prev) / prev * 100, 1)
