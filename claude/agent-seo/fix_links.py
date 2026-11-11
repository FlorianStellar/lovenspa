"""Correction des liens internes qui passent par une redirection (agent du mercredi, niveau Auto).

Usage : python3 fix_links.py <dossier_export> <dossier_sauvegarde> [--plafond 28] [--appliquer]
Sans --appliquer : plan seulement (aucune écriture Shopify).
Règles : claude/agent-seo/BUGS-TECHNIQUES.md. Seuls les liens « redirection » depuis une page publiée
sont traités, si la chaîne de redirection vérifiée en direct aboutit en 200 à l'URL attendue.
Exclus : cibles /products/* redirigées vers autre chose qu'une fiche (ancre au nom d'un hébergement)
et redirections vers l'accueil.
"""
from __future__ import annotations

import csv
import gzip
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from site_export import Admin, to_path  # noqa: E402

BASE = "https://lovenspa.fr"
HREF_RE = re.compile(r'(href\s*=\s*)(["\'])(.*?)\2', re.I | re.S)


def rewrite_hrefs(html: str, mapping: dict[str, str]) -> tuple[str, int]:
    """Remplace la valeur des href dont le chemin normalisé est dans mapping. Le reste du HTML est intact."""
    n = 0

    def sub(m):
        nonlocal n
        path = to_path(m.group(3))
        if path in mapping:
            n += 1
            return f"{m.group(1)}{m.group(2)}{mapping[path]}{m.group(2)}"
        return m.group(0)

    return HREF_RE.sub(sub, html or ""), n


def eligible(cible: str, vers: str) -> bool:
    if not vers or vers == "/":
        return False
    if cible.startswith("/products/") and not vers.startswith("/products/"):
        return False
    return True


def live_final(path: str, session: requests.Session) -> tuple[int, str]:
    """(code final, chemin final) en suivant les redirections en direct."""
    r = session.get(BASE + requests.utils.quote(path, safe="/%!.-_~"), allow_redirects=True, timeout=30)
    return r.status_code, (to_path(r.url) or "/")


def load_ids(export_dir: Path) -> dict[str, tuple[str, str]]:
    """url → (type, gid) depuis les réponses brutes de l'export."""
    ids = {}
    for name, kind in [("products", "product"), ("collections", "collection"), ("pages", "page"), ("articles", "article")]:
        with gzip.open(export_dir / "brut" / f"{name}.jsonl.gz", "rt", encoding="utf-8") as f:
            for line in f:
                o = json.loads(line)
                if o.get("__parentId"):
                    continue
                if kind == "article":
                    url = f"/blogs/{(o.get('blog') or {}).get('handle', '')}/{o['handle']}"
                else:
                    url = f"/{kind}s/{o['handle']}"
                ids[url] = (kind, o["id"])
    return ids


def plan(export_dir: Path, cap: int) -> tuple[list[dict], dict[str, str], list[dict]]:
    pages = {p["url"]: p for p in csv.DictReader(open(export_dir / "pages.csv", encoding="utf-8"))}
    rows = [r for r in csv.DictReader(open(export_dir / "audit" / "liens_a_corriger.csv", encoding="utf-8"))
            if r["emplacement"] == "body" and r["verdict"] == "redirection" and pages.get(r["source"], {}).get("publie") == "True"]
    excluded = [r for r in rows if not eligible(r["cible"], r["vers"])]
    rows = [r for r in rows if eligible(r["cible"], r["vers"])]
    s = requests.Session()
    s.headers["User-Agent"] = "LovenspaSEOAudit/1.0"
    mapping, refused = {}, []
    for cible, vers in sorted({(r["cible"], r["vers"]) for r in rows}):
        code, final = live_final(cible, s)
        if code == 200 and final == vers:
            mapping[cible] = vers
        else:
            refused.append({"cible": cible, "vers_export": vers, "direct": f"{code} {final}"})
        time.sleep(0.3)
    by_src = defaultdict(list)
    for r in rows:
        if r["cible"] in mapping:
            by_src[r["source"]].append(r)
    order = sorted(by_src, key=lambda u: (-len(by_src[u]), u))[:cap]
    work = [{"source": u, "liens": len(by_src[u])} for u in order]
    return work, mapping, excluded + [{"refus_direct": x} for x in refused]


GET = {
    "product": "query($id: ID!) { node(id: $id) { ... on Product { descriptionHtml } } }",
    "collection": "query($id: ID!) { node(id: $id) { ... on Collection { descriptionHtml } } }",
    "page": "query($id: ID!) { node(id: $id) { ... on Page { body } } }",
    "article": "query($id: ID!) { node(id: $id) { ... on Article { body } } }",
}
FIELD = {"product": "descriptionHtml", "collection": "descriptionHtml", "page": "body", "article": "body"}
SET = {
    "product": ("mutation($id: ID!, $h: String!) { productUpdate(product: {id: $id, descriptionHtml: $h}) "
                "{ product { id } userErrors { field message } } }", "productUpdate"),
    "collection": ("mutation($id: ID!, $h: String!) { collectionUpdate(input: {id: $id, descriptionHtml: $h}) "
                   "{ collection { id } userErrors { field message } } }", "collectionUpdate"),
    "page": ("mutation($id: ID!, $h: String!) { pageUpdate(id: $id, page: {body: $h}) "
             "{ page { id } userErrors { field message } } }", "pageUpdate"),
    "article": ("mutation($id: ID!, $h: String!) { articleUpdate(id: $id, article: {body: $h}) "
                "{ article { id } userErrors { field message } } }", "articleUpdate"),
}


def apply(export_dir: Path, backup_dir: Path, work: list[dict], mapping: dict[str, str]) -> list[dict]:
    admin, ids, out = Admin(), load_ids(export_dir), []
    backup_dir.mkdir(parents=True, exist_ok=True)
    for w in work:
        kind, gid = ids[w["source"]]
        html = admin.gql(GET[kind], {"id": gid})["node"][FIELD[kind]] or ""
        new, n = rewrite_hrefs(html, mapping)
        res = {"source": w["source"], "type": kind, "id": gid, "attendus": w["liens"], "remplaces": n}
        if n == 0:
            res["statut"] = "rien a faire (deja corrige)"
            out.append(res)
            continue
        safe = re.sub(r"[^a-z0-9-]+", "_", w["source"].strip("/"))
        (backup_dir / f"{safe}.html").write_text(html, encoding="utf-8")
        q, key = SET[kind]
        r = admin.gql(q, {"id": gid, "h": new})[key]
        if r["userErrors"]:
            res["statut"] = "erreur " + json.dumps(r["userErrors"], ensure_ascii=False)
        else:
            after = admin.gql(GET[kind], {"id": gid})["node"][FIELD[kind]] or ""
            left = rewrite_hrefs(after, mapping)[1]
            res["statut"] = "corrige" if left == 0 else f"verification: {left} lien(s) restant(s)"
        out.append(res)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    cap = int(a[a.index("--plafond") + 1]) if "--plafond" in a else 28
    exp, bak = Path(a[0]), Path(a[1])
    work, mapping, excluded = plan(exp, cap)
    report = {"plan": work, "correspondances": mapping, "exclus": excluded}
    if "--appliquer" in a:
        report["resultats"] = apply(exp, bak, work, mapping)
    bak.mkdir(parents=True, exist_ok=True)
    (bak / "rapport_fix_links.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"sources": len(work), "liens": sum(w["liens"] for w in work), "correspondances": len(mapping),
                      "exclus": len(excluded), "resultats": dict(Counter(r["statut"].split(" ")[0] for r in report.get("resultats", [])))},
                     ensure_ascii=False, indent=1))
