"""Export plat de tout le site Shopify (remplace Matrixify) via les bulk operations de l'API Admin.

Usage : python3 site_export.py <dossier_sortie>
Jeton : variable SHOPIFY_API_TOKEN (jamais affichée). Lecture seule : seules des requêtes
bulkOperationRunQuery (lecture) et des query GraphQL sont envoyées.

Sorties (CSV UTF-8) :
  pages.csv              une ligne par URL : type, handle, url, publié, titres, metas, gabarit, maj, mots, hash
  liens.csv              liens internes : source, cible, ancre, emplacement (body | menu)
  collection_produits.csv appartenance produit → collection (liens générés par les grilles)
  redirections.csv       table des 301 Shopify
  brut/*.jsonl.gz        réponses brutes des bulk operations
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

import requests
from bs4 import BeautifulSoup

SHOP = os.environ.get("SHOPIFY_SHOP", "lovenspa.myshopify.com")
API = f"https://{SHOP}/admin/api/2025-10/graphql.json"
HOST = "lovenspa.fr"

Q_PRODUCTS = """{ products { edges { node { id handle title status templateSuffix onlineStoreUrl updatedAt
  descriptionHtml seo { title description } } } } }"""
ONLINE_STORE = "gid://shopify/Publication/74806198456"
Q_COLLECTIONS = """{ collections { edges { node { id handle title templateSuffix updatedAt descriptionHtml
  onlineStore: publishedOnPublication(publicationId: "%s")
  seo { title description } products { edges { node { id handle } } } } } } }""" % ONLINE_STORE
Q_PAGES = """{ pages { edges { node { id handle title isPublished templateSuffix updatedAt body
  titleTag: metafield(namespace: "global", key: "title_tag") { value }
  descTag: metafield(namespace: "global", key: "description_tag") { value } } } } }"""
Q_ARTICLES = """{ articles { edges { node { id handle title isPublished templateSuffix updatedAt body
  blog { handle }
  titleTag: metafield(namespace: "global", key: "title_tag") { value }
  descTag: metafield(namespace: "global", key: "description_tag") { value } } } } }"""
Q_REDIRECTS = """{ urlRedirects { edges { node { id path target } } } }"""
Q_MENUS = """query($after: String) { menus(first: 50, after: $after) { pageInfo { hasNextPage endCursor }
  nodes { handle title items { title url items { title url items { title url } } } } } }"""

BULK_RUN = """mutation($q: String!) { bulkOperationRunQuery(query: $q) {
  bulkOperation { id status } userErrors { field message } } }"""
BULK_GET = """query($id: ID!) { node(id: $id) { ... on BulkOperation { id status errorCode objectCount url } } }"""


# ------------------------------------------------------------- client API ---
class Admin:
    def __init__(self, token: str | None = None):
        self.s = requests.Session()
        self.s.headers.update({"X-Shopify-Access-Token": token or os.environ["SHOPIFY_API_TOKEN"],
                               "Content-Type": "application/json"})

    def gql(self, query: str, variables: dict | None = None) -> dict:
        for attempt in range(5):
            r = self.s.post(API, json={"query": query, "variables": variables or {}}, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            d = r.json()
            if d.get("errors"):
                if any("THROTTLED" in json.dumps(e) for e in d["errors"]):
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(json.dumps(d["errors"])[:500])
            return d["data"]
        raise RuntimeError("API Shopify indisponible après 5 essais")

    def bulk(self, query: str, poll: float = 3.0, timeout: float = 1800) -> list[dict]:
        d = self.gql(BULK_RUN, {"q": query})["bulkOperationRunQuery"]
        if d["userErrors"]:
            raise RuntimeError(json.dumps(d["userErrors"]))
        op_id, t0 = d["bulkOperation"]["id"], time.time()
        while True:
            op = self.gql(BULK_GET, {"id": op_id})["node"]
            if op["status"] == "COMPLETED":
                break
            if op["status"] in ("FAILED", "CANCELED", "EXPIRED"):
                raise RuntimeError(f"bulk {op['status']} {op.get('errorCode')}")
            if time.time() - t0 > timeout:
                raise TimeoutError("bulk operation trop longue")
            time.sleep(poll)
        if not op.get("url"):  # aucun objet
            return []
        r = requests.get(op["url"], timeout=300)
        r.raise_for_status()
        return [json.loads(line) for line in r.text.splitlines() if line.strip()]

    def menus(self) -> list[dict]:
        out, after = [], None
        while True:
            d = self.gql(Q_MENUS, {"after": after})["menus"]
            out += d["nodes"]
            if not d["pageInfo"]["hasNextPage"]:
                return out
            after = d["pageInfo"]["endCursor"]


# ---------------------------------------------------------------- parsing ---
def split_bulk(lines: list[dict]) -> tuple[list[dict], dict[str, list[dict]]]:
    """Sépare les objets racines et les enfants (__parentId) d'un résultat bulk."""
    roots, children = [], {}
    for o in lines:
        p = o.get("__parentId")
        if p:
            children.setdefault(p, []).append(o)
        else:
            roots.append(o)
    return roots, children


def to_path(href: str | None) -> str | None:
    """Chemin interne canonique (/products/x, /collections/y…) d'un lien, sinon None."""
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    p = urlsplit(href.strip())
    host = p.netloc.lower().removeprefix("www.")
    if host and host not in (HOST, SHOP):
        return None
    if p.scheme and p.scheme not in ("http", "https"):
        return None
    path = re.sub(r"/{2,}", "/", unquote(p.path)).rstrip("/") or "/"
    if not path.startswith("/"):
        return None
    m = re.match(r"^/collections/[^/]+/products/([^/]+)$", path)
    if m:
        path = f"/products/{m.group(1)}"
    if path.startswith(("/cart", "/account", "/checkout", "/search", "/cdn", "/apps", "/tools")):
        return None
    return path


def body_links(html: str) -> list[tuple[str, str]]:
    """(chemin, ancre) de chaque lien interne d'un body HTML."""
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        p = to_path(a["href"])
        if p:
            out.append((p, " ".join(a.get_text(" ", strip=True).split())))
    return out


def word_count(html: str) -> int:
    if not html:
        return 0
    return len(re.findall(r"\w+", BeautifulSoup(html, "html.parser").get_text(" ")))


def menu_links(menus: list[dict]) -> list[dict]:
    out = []

    def walk(items, menu):
        for it in items or []:
            p = to_path(it.get("url"))
            if p:
                out.append({"source": f"menu:{menu}", "cible": p, "ancre": it.get("title", ""), "emplacement": "menu"})
            walk(it.get("items"), menu)

    for m in menus:
        walk(m.get("items"), m["handle"])
    return out


def page_row(kind: str, o: dict) -> dict:
    if kind == "product":
        url, pub = f"/products/{o['handle']}", o.get("status") == "ACTIVE" and bool(o.get("onlineStoreUrl"))
        html, st, sd, extra = o.get("descriptionHtml", ""), (o.get("seo") or {}).get("title"), (o.get("seo") or {}).get("description"), o.get("status")
    elif kind == "collection":
        url, pub = f"/collections/{o['handle']}", bool(o.get("onlineStore"))
        html, st, sd, extra = o.get("descriptionHtml", ""), (o.get("seo") or {}).get("title"), (o.get("seo") or {}).get("description"), ""
    elif kind == "page":
        url, pub = f"/pages/{o['handle']}", bool(o.get("isPublished"))
        html, st, sd, extra = o.get("body", ""), (o.get("titleTag") or {}).get("value"), (o.get("descTag") or {}).get("value"), ""
    else:  # article
        url, pub = f"/blogs/{(o.get('blog') or {}).get('handle', '')}/{o['handle']}", bool(o.get("isPublished"))
        html, st, sd, extra = o.get("body", ""), (o.get("titleTag") or {}).get("value"), (o.get("descTag") or {}).get("value"), ""
    return {
        "type": kind, "handle": o["handle"], "url": url, "publie": pub, "statut_shopify": extra,
        "titre": o.get("title", ""), "seo_title": st or "", "seo_description": sd or "",
        "gabarit": o.get("templateSuffix") or "", "maj": o.get("updatedAt", ""),
        "mots": word_count(html), "hash_body": hashlib.md5((html or "").encode()).hexdigest()[:12],
        "_html": html or "",
    }


def write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def export(out_dir: str, admin: Admin | None = None) -> dict:
    out = Path(out_dir)
    (out / "brut").mkdir(parents=True, exist_ok=True)
    admin = admin or Admin()
    raw = {}
    for name, q in [("products", Q_PRODUCTS), ("collections", Q_COLLECTIONS), ("pages", Q_PAGES),
                    ("articles", Q_ARTICLES), ("redirects", Q_REDIRECTS)]:
        raw[name] = admin.bulk(q)
        with gzip.open(out / "brut" / f"{name}.jsonl.gz", "wt", encoding="utf-8") as f:
            f.write("\n".join(json.dumps(x, ensure_ascii=False) for x in raw[name]))
        print(f"{name}: {len(raw[name])} lignes", flush=True)
    menus = admin.menus()
    (out / "brut" / "menus.json").write_text(json.dumps(menus, ensure_ascii=False), encoding="utf-8")

    pages = [page_row("product", o) for o in raw["products"]]
    coll_roots, coll_children = split_bulk(raw["collections"])
    pages += [page_row("collection", o) for o in coll_roots]
    pages += [page_row("page", o) for o in raw["pages"]]
    pages += [page_row("article", o) for o in raw["articles"]]

    links = []
    for p in pages:
        for target, anchor in body_links(p["_html"]):
            links.append({"source": p["url"], "cible": target, "ancre": anchor, "emplacement": "body"})
    links += menu_links(menus)

    membership = [{"collection": f"/collections/{c['handle']}", "produit": f"/products/{ch['handle']}"}
                  for c in coll_roots for ch in coll_children.get(c["id"], [])]
    redirects = [{"depuis": unquote(r["path"]).rstrip("/") or "/", "vers": r["target"]} for r in raw["redirects"]]

    write_csv(out / "pages.csv", pages, ["type", "handle", "url", "publie", "statut_shopify", "titre", "seo_title",
                                         "seo_description", "gabarit", "maj", "mots", "hash_body"])
    write_csv(out / "liens.csv", links, ["source", "cible", "ancre", "emplacement"])
    write_csv(out / "collection_produits.csv", membership, ["collection", "produit"])
    write_csv(out / "redirections.csv", redirects, ["depuis", "vers"])
    summary = {"date": time.strftime("%Y-%m-%d"), "pages": len(pages), "liens": len(links),
               "appartenances": len(membership), "redirections": len(redirects), "menus": len(menus)}
    (out / "export.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    return summary


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    print(json.dumps(export(sys.argv[1]), indent=1))
