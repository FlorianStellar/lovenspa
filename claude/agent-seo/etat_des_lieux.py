#!/usr/bin/env python3
"""État des lieux GSC : 28 j finaux vs 28 j précédents. Sortie JSON + résumé texte."""
import json
import sys
from datetime import date, timedelta

from gsc_client import GSCClient
from kpi import (totals_by_segment, cannibalization, quick_wins, best_page, delta)

HEAD_QUERIES = ["love room", "love rooms", "loveroom", "love room spa",
                "love room jacuzzi", "chambre avec jacuzzi privatif",
                "love room definition"]


def periods(today: date, lag: int = 3, days: int = 28):
    end = today - timedelta(days=lag)
    start = end - timedelta(days=days - 1)
    p_end = start - timedelta(days=1)
    p_start = p_end - timedelta(days=days - 1)
    return (str(start), str(end)), (str(p_start), str(p_end))


def collect(c: GSCClient, start: str, end: str) -> dict:
    pages = c.search_analytics_all(start, end, dimensions=["page"])
    queries = c.search_analytics_all(start, end, dimensions=["query"], aggregate_type="auto")
    qp = c.search_analytics_all(start, end, dimensions=["query", "page"], aggregate_type="auto")
    return {"pages": pages, "queries": queries, "qp": qp}


def summarize(cur: dict, prev: dict) -> dict:
    seg_cur, seg_prev = totals_by_segment(cur["pages"]), totals_by_segment(prev["pages"])
    segments = {
        s: {**v, "impr_delta_pct": delta(v["impressions"], seg_prev.get(s, {}).get("impressions", 0)),
            "clicks_delta_pct": delta(v["clicks"], seg_prev.get(s, {}).get("clicks", 0))}
        for s, v in seg_cur.items()
    }
    lr_cluster = sorted([r for r in cur["queries"] if "love room" in r["keys"][0] or "loveroom" in r["keys"][0]],
                        key=lambda r: -r["impressions"])[:15]
    targets = {q: best_page(cur["qp"], q) for q in HEAD_QUERIES}
    targets.update({r["keys"][0]: best_page(cur["qp"], r["keys"][0]) for r in lr_cluster})
    return {
        "perimetre": {"requetes": len(cur["queries"]), "requetes_prev": len(prev["queries"]),
                      "urls": len(cur["pages"]), "urls_prev": len(prev["pages"])},
        "segments": segments,
        "cibles": targets,
        "cannibalisation": cannibalization(cur["qp"])[:25],
        "quick_wins": quick_wins(cur["queries"])[:30],
    }


def main(out_path: str):
    c = GSCClient()
    (cs, ce), (ps, pe) = periods(date.today())
    result = {"periode": [cs, ce], "periode_prev": [ps, pe],
              **summarize(collect(c, cs, ce), collect(c, ps, pe)),
              "sitemaps": [{"path": s.get("path"), "lastDownloaded": s.get("lastDownloaded"),
                            "errors": s.get("errors"), "warnings": s.get("warnings")}
                           for s in c.list_sitemaps()]}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: result[k] for k in ("periode", "periode_prev", "perimetre", "segments")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
