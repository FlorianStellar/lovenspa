"""Inspection GSC de toutes les fiches du sitemap (réconciliation de l'audit d'indexation)."""
import csv, sys
from collections import Counter
sys.path.insert(0, "/home/user/lovenspa/claude/agent-seo")
import requests
from crawl_technique import parse_sitemap, BASE
from gsc_client import GSCClient
out = sys.argv[1]
s = requests.Session(); s.headers["User-Agent"] = "LovenspaSEOAudit/1.0"
todo, urls = [f"{BASE}/sitemap.xml"], []
while todo:
    subs, u = parse_sitemap(s.get(todo.pop(), timeout=30).text); todo += subs; urls += u
prod = sorted({u for u in urls if "/products/" in u})
print(len(prod), "fiches dans le sitemap", flush=True)
res = GSCClient().inspect_urls_batch(prod, delay=0.12, progress_every=200)
cols = ["url","verdict","coverageState","indexingState","pageFetchState","lastCrawlTime","googleCanonical","userCanonical","robotsTxtState","error"]
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(res)
c = Counter(r.get("coverageState") or ("ERREUR " + r.get("error","")[:40]) for r in res)
for k, v in c.most_common(): print(v, k)
