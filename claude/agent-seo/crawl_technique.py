"""Crawl technique de lovenspa.fr (T6) : codes HTTP, redirections, canonicals, robots,
hreflang, JSON-LD, liens internes, profondeur de clic, robots IA.

Usage : python3 crawl_technique.py <dossier_sortie> [--workers 6]
Sorties : crawl.csv (une ligne par URL), resume.json (agrégats).
Périmètre : toutes les URL des sitemaps + accueil ; les liens internes découverts hors sitemap
sont relevés (sans être crawlés) pour repérer les cibles hors sitemap.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import time
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup

HOST = "lovenspa.fr"
BASE = f"https://{HOST}"
UA = "LovenspaSEOAudit/1.0 (+crawl technique interne)"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
           "Claude-User", "PerplexityBot", "Perplexity-User", "Google-Extended", "Bingbot", "Googlebot"]
SKIP_PREFIXES = ("/cart", "/account", "/checkout", "/search", "/policies", "/cdn", "/apps", "/tools")


# ---------------------------------------------------------------- parsing ---
def parse_sitemap(xml_text: str) -> tuple[list[str], list[str]]:
    """Retourne (sous-sitemaps, url) d'un document sitemap."""
    root = ET.fromstring(xml_text)
    subs = [e.text.strip() for e in root.findall("sm:sitemap/sm:loc", NS) if e.text]
    urls = [e.text.strip() for e in root.findall("sm:url/sm:loc", NS) if e.text]
    return subs, urls


def normalize(href: str | None, base: str) -> str | None:
    """URL interne normalisée (https, sans www, sans query ni fragment, sans / final), sinon None."""
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    p = urlsplit(urljoin(base, href))
    host = p.netloc.lower().removeprefix("www.")
    if p.scheme not in ("http", "https") or host != HOST:
        return None
    path = re.sub(r"/{2,}", "/", p.path) or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    if path.startswith(SKIP_PREFIXES):
        return None
    return urlunsplit(("https", HOST, path, "", ""))


def jsonld_blocks(soup: BeautifulSoup) -> list:
    out = []
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "")
        except (json.JSONDecodeError, TypeError):
            out.append({"@type": "__INVALIDE__"})
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data]) if isinstance(data, dict) else []
        out.extend(i for i in items if isinstance(i, dict))
    return out


def offers_summary(blocks: list) -> tuple[str, str]:
    """(prix, disponibilité) du premier Product du JSON-LD."""
    for b in blocks:
        t = b.get("@type")
        if t == "Product" or (isinstance(t, list) and "Product" in t):
            o = b.get("offers")
            o = o[0] if isinstance(o, list) and o else o
            if isinstance(o, dict):
                return str(o.get("price", o.get("lowPrice", ""))), str(o.get("availability", "")).rsplit("/", 1)[-1]
            return "", ""
    return "", ""


def analyze_html(url: str, html: str, headers: dict) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    canon = soup.find("link", rel="canonical")
    robots = soup.find("meta", attrs={"name": "robots"})
    title = soup.title.get_text(strip=True) if soup.title else ""
    desc = soup.find("meta", attrs={"name": "description"})
    hreflang = [l.get("hreflang") + "=" + (l.get("href") or "") for l in soup.find_all("link", rel="alternate") if l.get("hreflang")]
    blocks = jsonld_blocks(soup)
    types = sorted({(t if isinstance(t, str) else "+".join(t)) for t in (b.get("@type", "?") for b in blocks)})
    price, avail = offers_summary(blocks)
    links = set()
    for a in soup.find_all("a", href=True):
        n = normalize(a["href"], url)
        if n:
            links.add(n)
    return {
        "canonical": canon.get("href", "") if canon else "",
        "meta_robots": (robots.get("content", "") if robots else "").lower(),
        "x_robots": headers.get("X-Robots-Tag", "").lower(),
        "title_len": len(title),
        "desc_len": len((desc.get("content", "") if desc else "").strip()),
        "h1_count": len(soup.find_all("h1")),
        "hreflang": "|".join(hreflang),
        "jsonld_types": "|".join(types),
        "offer_price": price,
        "offer_availability": avail,
        "is_churn": "data-lvn-churn" in html,
        "n_links_internal": len(links),
        "_links": links,
    }


def robots_rules(txt: str) -> dict[str, list[str]]:
    """Disallow par user-agent (groupes consécutifs de User-agent partagent les règles)."""
    rules: dict[str, list[str]] = {}
    agents: list[str] = []
    last_was_agent = False
    for raw in txt.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        k, v = (x.strip() for x in line.split(":", 1))
        k = k.lower()
        if k == "user-agent":
            if not last_was_agent:
                agents = []
            agents.append(v.lower())
            rules.setdefault(v.lower(), [])
            last_was_agent = True
        else:
            last_was_agent = False
            if k == "disallow" and v:
                for a in agents:
                    rules[a].append(v)
    return rules


def bot_blocked_root(rules: dict[str, list[str]], bot: str) -> bool:
    """Vrai si le robot (ou * à défaut de groupe dédié) a Disallow: /."""
    group = rules.get(bot.lower(), rules.get("*", []))
    return "/" in group


def click_depth(graph: dict[str, set[str]], start: str) -> dict[str, int]:
    depth = {start: 0}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in graph.get(u, ()):
            if v not in depth:
                depth[v] = depth[u] + 1
                q.append(v)
    return depth


def classify(row: dict) -> list[str]:
    """Anomalies techniques d'une URL crawlée."""
    a = []
    st = row["status"]
    if st >= 400:
        a.append(f"http_{st}")
    elif 300 <= st < 400:
        a.append("redirection_dans_sitemap" if row["in_sitemap"] else "redirection")
    if st == 200:
        c = row.get("canonical", "")
        if not c:
            a.append("canonical_absent")
        elif normalize(c, row["url"]) != row["url"]:
            a.append("canonical_autre_url")
        if "noindex" in row.get("meta_robots", "") or "noindex" in row.get("x_robots", ""):
            a.append("noindex" + ("_dans_sitemap" if row["in_sitemap"] else ""))
        if row.get("h1_count") != 1:
            a.append(f"h1_{row.get('h1_count')}")
        if "/en" in row.get("hreflang", ""):
            a.append("hreflang_en")
        if "__INVALIDE__" in row.get("jsonld_types", ""):
            a.append("jsonld_invalide")
        if row.get("is_churn") and row.get("offer_availability") in ("InStock", "PreOrder"):
            a.append("churn_offer_instock")
        if row.get("n_links_internal", 0) > 100:
            a.append("plus_de_100_liens")
        d = row.get("depth")
        if d is None or d == "":
            a.append("non_atteinte_depuis_accueil")
        elif d >= 4:
            a.append("profondeur_4_plus")
    return a


# ------------------------------------------------------------------ fetch ---
def fetch(session: requests.Session, url: str) -> dict:
    for attempt in range(3):
        try:
            r = session.get(url, allow_redirects=False, timeout=30)
            break
        except requests.RequestException as e:
            if attempt == 2:
                return {"url": url, "status": 0, "error": str(e)[:120]}
            time.sleep(2 ** attempt)
    row = {"url": url, "status": r.status_code, "location": r.headers.get("Location", ""),
           "ttfb_ms": int(r.elapsed.total_seconds() * 1000)}
    if r.status_code == 429:
        time.sleep(5)
    if r.status_code == 200 and "text/html" in r.headers.get("Content-Type", ""):
        row.update(analyze_html(url, r.text, r.headers))
    return row


def main(out_dir: str, workers: int = 6) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = UA

    sitemap_urls, todo, seen_sm = [], [f"{BASE}/sitemap.xml"], set()
    while todo:
        sm = todo.pop()
        if sm in seen_sm:
            continue
        seen_sm.add(sm)
        subs, urls = parse_sitemap(s.get(sm, timeout=30).text)
        todo.extend(subs)
        sitemap_urls.extend(urls)
    in_sitemap = {normalize(u, BASE) or u for u in sitemap_urls}
    targets = sorted(in_sitemap | {f"{BASE}/"})
    print(f"{len(targets)} URL à crawler", flush=True)

    with ThreadPoolExecutor(workers) as ex:
        rows = list(ex.map(lambda u: fetch(s, u), targets))

    graph = {r["url"]: r.pop("_links", set()) for r in rows}
    home = f"{BASE}/"
    depth = click_depth(graph, home if home in graph else targets[0])
    inbound = Counter(v for links in graph.values() for v in links)
    discovered_out = sorted({v for links in graph.values() for v in links} - set(graph))

    robots_txt = s.get(f"{BASE}/robots.txt", timeout=30).text
    rules = robots_rules(robots_txt)
    bots = {b: ("bloqué sur /" if bot_blocked_root(rules, b) else "autorisé sur /") for b in AI_BOTS}
    en_in_sitemap = sorted(u for u in in_sitemap if urlsplit(u).path.startswith("/en/"))

    for r in rows:
        r["in_sitemap"] = r["url"] in in_sitemap
        r["depth"] = depth.get(r["url"], "")
        r["inbound_internal"] = inbound.get(r["url"], 0)
        r["anomalies"] = "|".join(classify(r)) if r.get("status") else "fetch_error"

    cols = ["url", "status", "location", "ttfb_ms", "in_sitemap", "depth", "inbound_internal", "canonical",
            "meta_robots", "x_robots", "title_len", "desc_len", "h1_count", "hreflang", "jsonld_types",
            "offer_price", "offer_availability", "is_churn", "n_links_internal", "anomalies", "error"]
    with open(out / "crawl.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    anomalies = Counter(a for r in rows for a in r["anomalies"].split("|") if a)
    by_type = Counter(urlsplit(r["url"]).path.split("/")[1] or "accueil" for r in rows)
    summary = {
        "date": time.strftime("%Y-%m-%d"),
        "urls_crawlees": len(rows),
        "urls_sitemap": len(in_sitemap),
        "par_type": dict(by_type),
        "statuts": dict(Counter(r["status"] for r in rows)),
        "anomalies": dict(anomalies.most_common()),
        "profondeur": dict(Counter(str(d) for d in (r["depth"] for r in rows))),
        "liens_vers_hors_sitemap": len(discovered_out),
        "exemples_hors_sitemap": discovered_out[:30],
        "robots_ia": bots,
        "urls_en_dans_sitemap": len(en_in_sitemap),
        "ttfb_ms_median": sorted(r.get("ttfb_ms", 0) for r in rows)[len(rows) // 2],
    }
    (out / "resume.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "liens_hors_sitemap.txt").write_text("\n".join(discovered_out), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    w = int(args[args.index("--workers") + 1]) if "--workers" in args else 6
    main(args[0], w)
