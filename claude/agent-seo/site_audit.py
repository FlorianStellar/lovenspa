"""Audit SEO hors ligne d'un export plat (site_export.py) : liens, maillage, metas, contenu, diff.

Usage : python3 site_audit.py <dossier_export> [--precedent <dossier_export_precedent>]
Sorties dans <dossier_export>/audit/ : resume.json, liens_a_corriger.csv, liens_entrants.csv,
metas.csv, contenu_mince.csv, ancres_generiques.csv, diff.csv (si --precedent).
Aucun appel réseau : tout est calculé depuis les CSV de l'export.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

GENERIC_ANCHORS = {"ici", "cliquez ici", "en savoir plus", "lire la suite", "voir", "voir plus", "ce lien",
                   "lien", "découvrir", "decouvrir", "plus", "suite", "cliquer ici", "this", "here"}
MIN_WORDS = {"collection": 150, "page": 300, "article": 300, "product": 100}
TITLE_MAX, DESC_MAX, DESC_MIN = 60, 160, 70


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def is_true(v) -> bool:
    return str(v).lower() in ("true", "1", "oui")


def resolve(target: str, published: set[str], existing: set[str], redirects: dict[str, str],
            blogs: set[str], hops: int = 0) -> tuple[str, str]:
    """Statut d'une cible de lien : ok | redirection | non_publiee | introuvable | hors_perimetre."""
    if target not in published and target.lower() in published:  # Shopify résout les handles sans casse
        target = target.lower()
    if target == "/" or target in published:
        return ("ok", target) if hops == 0 else ("redirection", target)
    if target in redirects and hops < 5:
        dest = redirects[target]
        dest_path = re.sub(r"^https?://[^/]+", "", dest).rstrip("/") or "/"
        st, final = resolve(dest_path, published, existing, redirects, blogs, hops + 1)
        return ("redirection", final) if st in ("ok", "redirection") else (st, final)
    parts = target.strip("/").split("/")
    if parts[0] == "collections" and len(parts) == 2 and parts[1] in ("all", "vendors", "types"):
        return ("ok", target)
    if parts[0] == "collections" and len(parts) == 3 and f"/collections/{parts[1]}" in published:
        return ("ok", target)  # collection filtrée par tag
    if parts[0] == "blogs" and len(parts) >= 2 and parts[1] in blogs and (len(parts) == 2 or parts[2] == "tagged"):
        return ("ok", target)
    if parts[0] not in ("products", "collections", "pages", "blogs"):
        return ("hors_perimetre", target)
    if target in existing:
        return ("non_publiee", target)
    return ("introuvable", target)


def audit(export_dir: str, previous: str | None = None) -> dict:
    d = Path(export_dir)
    out = d / "audit"
    out.mkdir(exist_ok=True)
    pages = read_csv(d / "pages.csv")
    links = read_csv(d / "liens.csv")
    member = read_csv(d / "collection_produits.csv")
    redirects = {r["depuis"]: r["vers"] for r in read_csv(d / "redirections.csv")}

    published = {p["url"] for p in pages if is_true(p["publie"])}
    existing = {p["url"] for p in pages}
    blogs = {p["url"].split("/")[2] for p in pages if p["type"] == "article"}

    # 1. Liens à corriger (avec leur source)
    to_fix, inbound = [], Counter()
    for l in links:
        st, final = resolve(l["cible"], published, existing, redirects, blogs)
        if st == "ok":
            inbound[l["cible"]] += 1
        elif st == "redirection":
            inbound[final] += 1
            to_fix.append({**l, "verdict": st, "vers": final})
        elif st in ("non_publiee", "introuvable"):
            to_fix.append({**l, "verdict": st, "vers": ""})
    for m in member:  # grilles de collection : liens générés par le thème
        if m["collection"] in published:
            inbound[m["produit"]] += 1

    # 2. Liens entrants par page publiée (orphelines = 0)
    inbound_rows = sorted(({"url": u, "type": next(p["type"] for p in pages if p["url"] == u), "liens_entrants": inbound.get(u, 0)}
                           for u in published), key=lambda r: (r["liens_entrants"], r["url"]))

    # 3. Metas (pages publiées)
    pub_pages = [p for p in pages if is_true(p["publie"])]
    t_count = Counter(p["seo_title"].strip().lower() for p in pub_pages if p["seo_title"].strip())
    d_count = Counter(p["seo_description"].strip().lower() for p in pub_pages if p["seo_description"].strip())
    metas = []
    for p in pub_pages:
        t, ds, issues = p["seo_title"].strip(), p["seo_description"].strip(), []
        if not t:
            issues.append("title_par_defaut")
        elif len(t) > TITLE_MAX:
            issues.append("title_trop_long")
        if t and t_count[t.lower()] > 1:
            issues.append("title_duplique")
        if not ds:
            issues.append("description_absente")
        elif len(ds) > DESC_MAX:
            issues.append("description_trop_longue")
        elif len(ds) < DESC_MIN:
            issues.append("description_trop_courte")
        if ds and d_count[ds.lower()] > 1:
            issues.append("description_dupliquee")
        if issues:
            metas.append({"url": p["url"], "type": p["type"], "problemes": "|".join(issues),
                          "seo_title": t, "seo_description": ds})

    # 4. Contenu mince
    thin = [{"url": p["url"], "type": p["type"], "mots": p["mots"]} for p in pub_pages
            if int(p["mots"] or 0) < MIN_WORDS.get(p["type"], 0)]

    # 5. Ancres génériques (liens éditoriaux)
    generic = [l for l in links if l["emplacement"] == "body" and l["ancre"].strip().lower() in GENERIC_ANCHORS]

    # 6. Diff avec l'export précédent
    diff = []
    if previous:
        old = {p["url"]: p for p in read_csv(Path(previous) / "pages.csv")}
        new = {p["url"]: p for p in pages}
        for u in sorted(set(old) | set(new)):
            a, b = old.get(u), new.get(u)
            if a is None:
                diff.append({"url": u, "changement": "ajoutee", "champs": ""})
            elif b is None:
                diff.append({"url": u, "changement": "supprimee", "champs": ""})
            else:
                ch = [k for k in ("publie", "titre", "seo_title", "seo_description", "gabarit", "hash_body") if a.get(k) != b.get(k)]
                if ch:
                    diff.append({"url": u, "changement": "modifiee", "champs": "|".join(ch)})

    def w(name, rows, cols):
        with open(out / name, "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            wr.writeheader()
            wr.writerows(rows)

    w("liens_a_corriger.csv", to_fix, ["source", "cible", "ancre", "emplacement", "verdict", "vers"])
    w("liens_entrants.csv", inbound_rows, ["url", "type", "liens_entrants"])
    w("metas.csv", metas, ["url", "type", "problemes", "seo_title", "seo_description"])
    w("contenu_mince.csv", thin, ["url", "type", "mots"])
    w("ancres_generiques.csv", generic, ["source", "cible", "ancre"])
    if previous:
        w("diff.csv", diff, ["url", "changement", "champs"])

    by_type = defaultdict(int)
    for r in inbound_rows:
        if r["liens_entrants"] == 0:
            by_type[r["type"]] += 1
    summary = {
        "pages_publiees": len(published),
        "pages_par_type": dict(Counter(p["type"] for p in pub_pages)),
        "liens_editoriaux": sum(1 for l in links if l["emplacement"] == "body"),
        "liens_menu": sum(1 for l in links if l["emplacement"] == "menu"),
        "liens_a_corriger": dict(Counter(r["verdict"] for r in to_fix)),
        "cibles_a_corriger": len({r["cible"] for r in to_fix}),
        "sans_lien_entrant_par_type": dict(by_type),  # éditorial, menu ou grille de collection ; hors listes de blog générées par le thème
        "metas": dict(Counter(i for m in metas for i in m["problemes"].split("|"))),
        "contenu_mince_par_type": dict(Counter(t["type"] for t in thin)),
        "ancres_generiques": len(generic),
        "diff": dict(Counter(x["changement"] for x in diff)) if previous else None,
    }
    (out / "resume.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    return summary


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    prev = a[a.index("--precedent") + 1] if "--precedent" in a else None
    print(json.dumps(audit(a[0], prev), ensure_ascii=False, indent=1))
