"""Surveillance quotidienne : thème live (checksums), robots.txt, sitemaps GSC.

Usage : python surveillance_technique.py <dossier_etat> <sortie.json>
<dossier_etat> garde le dernier instantané (etat.json + contenu des fichiers SEO sensibles).
Lecture seule. Code 2 si un changement sensible est détecté.
"""
import hashlib, json, os, re, sys, time
from pathlib import Path

SENSIBLES = re.compile(r"^(layout/|templates/robots\.txt|snippets/.*(seo|meta|json|schema|canonical|head\.|breadcrumb|hreflang))", re.I)
# Fichiers surveillés seulement sur les motifs SEO (édités souvent : pas d'alerte sur simple modification)
SURVEILLES = re.compile(r"^(sections/.*\.liquid|templates/.*\.(json|liquid)|config/settings_data\.json)$", re.I)
MOTIFS_RISQUE = {
    "noindex": re.compile(r"noindex", re.I),
    "canonical": re.compile(r"rel=[\"']canonical", re.I),
    "ld_json": re.compile(r"application/ld\+json", re.I),
    "meta_description": re.compile(r"name=[\"']description", re.I),
    "hreflang": re.compile(r"hreflang", re.I),
}

Q_THEME = "{ themes(first:5, roles:[MAIN]){ nodes{ id name } } }"
Q_FILES = """query($id:ID!,$after:String){ theme(id:$id){ files(first:250, after:$after){
  nodes{ filename checksumMd5 } pageInfo{ hasNextPage endCursor } } } }"""
Q_BODY = """query($id:ID!,$f:[String!]){ theme(id:$id){ files(filenames:$f, first:50){
  nodes{ filename body{ ... on OnlineStoreThemeFileBodyText{ content } } } } } }"""


def compter(texte):
    return {k: len(r.findall(texte or "")) for k, r in MOTIFS_RISQUE.items()}


def diff_fichiers(avant: dict, apres: dict):
    ajoutes = sorted(set(apres) - set(avant))
    supprimes = sorted(set(avant) - set(apres))
    modifies = sorted(f for f in set(avant) & set(apres) if avant[f] != apres[f])
    return ajoutes, supprimes, modifies


def risques(f, contenu_avant, contenu_apres):
    """Écarts de motifs SEO dans un fichier sensible : noindex ajouté, canonical/ld+json/description retirés."""
    a, b = compter(contenu_avant), compter(contenu_apres)
    out = []
    if b["noindex"] > a["noindex"]:
        out.append(f"{f}: noindex ajouté ({a['noindex']}→{b['noindex']})")
    for k in ("canonical", "ld_json", "meta_description", "hreflang"):
        if b[k] < a[k]:
            out.append(f"{f}: {k} retiré ({a[k]}→{b[k]})")
    return out


def robots_regles(txt):
    """Règles robots.txt rattachées à leur groupe User-agent (« agent | règle »), triées."""
    out, agents, dans_regles = [], [], False
    for l in (txt or "").splitlines():
        l = l.split("#", 1)[0].strip()
        if not l or ":" not in l:
            continue
        k, v = (x.strip() for x in l.split(":", 1))
        k = k.lower()
        if k == "user-agent":
            if dans_regles:
                agents, dans_regles = [], False
            agents.append(v)
        elif k == "sitemap":
            out.append(f"* | Sitemap: {v}")
        elif k in ("allow", "disallow", "crawl-delay"):
            dans_regles = True
            for a in agents or ["?"]:
                out.append(f"{a} | {k}: {v}")
    return sorted(set(out))


def lire_html(texte, entetes, statut):
    """Signaux SEO d'une page rendue."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(texte or "", "html.parser")
    mr = soup.find("meta", attrs={"name": re.compile("^robots$", re.I)})
    can = soup.find("link", rel=lambda v: v and "canonical" in v)
    desc = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    return {"statut": statut, "meta_robots": (mr.get("content") or "").lower() if mr else "",
            "x_robots": (entetes.get("X-Robots-Tag") or "").lower(),
            "canonical": can.get("href") if can else None,
            "ld_json": len(soup.find_all("script", type="application/ld+json")),
            "description": bool(desc and (desc.get("content") or "").strip())}


def comparer(prec: dict, cur: dict, contenus_prec: dict, contenus_cur: dict):
    alertes, infos = [], []
    if prec.get("theme_id") and prec["theme_id"] != cur["theme_id"]:
        alertes.append(f"thème live changé : {prec.get('theme_name')} → {cur['theme_name']}")
    else:
        aj, sup, mod = diff_fichiers(prec.get("fichiers", {}), cur["fichiers"])
        for f in aj + sup + mod:
            (alertes if SENSIBLES.match(f) else infos).append(
                f"{'ajouté' if f in aj else 'supprimé' if f in sup else 'modifié'} : {f}")
        for f in mod + aj:
            if SENSIBLES.match(f) or SURVEILLES.match(f):
                alertes += risques(f, contenus_prec.get(f, ""), contenus_cur.get(f, ""))
        for f in sup:
            if SURVEILLES.match(f) and not SENSIBLES.match(f):
                alertes += risques(f, contenus_prec.get(f, ""), "")
    if cur.get("robots") is None:
        infos.append("robots.txt non lu (anti-robot ou réseau) : comparaison reportée")
    elif prec.get("robots") is not None and prec["robots"] != cur["robots"]:
        rp, rc = set(prec["robots"]), set(cur["robots"])
        alertes.append(f"robots.txt modifié : +{sorted(rc - rp)} -{sorted(rp - rc)}")
    for sm in set(prec.get("sitemaps", {})) - set(cur.get("sitemaps", {})):
        alertes.append(f"sitemap retiré de GSC : {sm}")
    for url, h in cur.get("html", {}).items():
        p = prec.get("html", {}).get(url)
        if h is None:
            infos.append(f"HTML non lu : {url}")
            continue
        if h.get("statut") != 200:
            alertes.append(f"{url} : HTTP {h.get('statut')}")
        if "noindex" in (h.get("meta_robots") or "") + (h.get("x_robots") or ""):
            alertes.append(f"{url} : noindex (meta {h.get('meta_robots')!r}, en-tête {h.get('x_robots')!r})")
        if p:
            if p.get("canonical") and h.get("canonical") != p.get("canonical"):
                alertes.append(f"{url} : canonical {p.get('canonical')} → {h.get('canonical')}")
            if h.get("ld_json", 0) < p.get("ld_json", 0):
                alertes.append(f"{url} : blocs JSON-LD {p.get('ld_json')} → {h.get('ld_json')}")
            if p.get("description") and not h.get("description"):
                alertes.append(f"{url} : meta description disparue")
    for sm, n in cur.get("sitemaps", {}).items():
        p = prec.get("sitemaps", {}).get(sm)
        if p and n["soumises"] < p["soumises"] * 0.9:
            alertes.append(f"sitemap {sm} : URL soumises {p['soumises']} → {n['soumises']}")
        if n["erreurs"] > (p or {}).get("erreurs", 0):
            alertes.append(f"sitemap {sm} : erreurs {(p or {}).get('erreurs', 0)} → {n['erreurs']}")
    return alertes, infos


def collecter(admin, gsc, http_get, pages=(), page_get=None):
    t = admin.gql(Q_THEME)["themes"]["nodes"][0]
    fichiers, after = {}, None
    while True:
        r = admin.gql(Q_FILES, {"id": t["id"], "after": after})["theme"]["files"]
        fichiers.update({n["filename"]: n["checksumMd5"] for n in r["nodes"]})
        if not r["pageInfo"]["hasNextPage"]:
            break
        after = r["pageInfo"]["endCursor"]
    sens = sorted(f for f in fichiers if SENSIBLES.match(f) or SURVEILLES.match(f))
    contenus = {}
    for i in range(0, len(sens), 50):
        for n in admin.gql(Q_BODY, {"id": t["id"], "f": sens[i:i + 50]})["theme"]["files"]["nodes"]:
            contenus[n["filename"]] = (n.get("body") or {}).get("content", "")
    sitemaps = {s["path"]: {"soumises": sum(int(c.get("submitted", 0)) for c in s.get("contents", []) if c.get("type") == "web"),
                            "images": sum(int(c.get("submitted", 0)) for c in s.get("contents", []) if c.get("type") == "image"),
                            "erreurs": int(s.get("errors", 0))} for s in gsc.list_sitemaps()}
    rob = http_get("https://lovenspa.fr/robots.txt")
    html = {}
    for i, u in enumerate(pages):
        r = page_get(u) if page_get else None
        html[u] = lire_html(*r) if r else None
    return {"theme_id": t["id"], "theme_name": t["name"], "fichiers": fichiers,
            "robots": robots_regles(rob) if rob else None, "sitemaps": sitemaps, "html": html}, contenus


ANTI_ROBOT = ("Verifying your connection", "Just a moment", "cf-chl", "challenge-platform")


def page_get(url, essais=4, attendu=None, pause=8):
    """(texte, entêtes, statut) ou None si anti-robot / réseau persistant (jamais une page vide)."""
    import requests
    for i in range(essais):
        try:
            r = requests.get(url, timeout=30, headers={"User-Agent": "lovenspa-seo-monitor"}, allow_redirects=False)
        except requests.RequestException:
            time.sleep(20 * (i + 1)); continue
        bloque = r.status_code == 429 or any(m in r.text for m in ANTI_ROBOT)
        if not bloque and (attendu is None or attendu in r.text):
            time.sleep(pause)
            return r.text, r.headers, r.status_code
        time.sleep(20 * (i + 1))
    return None


def http_get(url):
    r = page_get(url, attendu="User-agent", pause=0)
    return r[0] if r else None


def prec_robots(etat_dir):
    fe = Path(etat_dir) / "etat.json"
    return json.loads(fe.read_text()).get("robots") if fe.exists() else None


def main(argv):
    from site_export import Admin
    from gsc_client import GSCClient
    etat_dir, sortie = Path(argv[1]), argv[2]
    etat_dir.mkdir(parents=True, exist_ok=True)
    pages = [l.strip() for l in open(Path(__file__).with_name("pages_cles.txt")) if l.startswith("http")]
    cur, contenus = collecter(Admin(), GSCClient(), http_get, pages, page_get)
    fe, fc = etat_dir / "etat.json", etat_dir / "contenus.json"
    prec = json.loads(fe.read_text()) if fe.exists() else {}
    cprec = json.loads(fc.read_text()) if fc.exists() else {}
    alertes, infos = comparer(prec, cur, cprec, contenus) if prec else ([], ["premier instantané"])
    # lecture impossible : on garde la référence précédente pour la comparaison suivante
    if cur["robots"] is None:
        cur["robots"] = prec.get("robots")
    for u, h in list(cur["html"].items()):
        if h is None and prec.get("html", {}).get(u):
            cur["html"][u] = prec["html"][u]
    fe.write_text(json.dumps(cur, ensure_ascii=False, indent=1))
    fc.write_text(json.dumps(contenus, ensure_ascii=False))
    res = {"theme": cur["theme_name"], "fichiers": len(cur["fichiers"]), "sensibles": len(contenus),
           "pages_html": sum(1 for v in cur["html"].values() if v), "pages_html_non_lues": sum(1 for v in cur["html"].values() if not v),
           "robots_regles": len(cur["robots"]), "sitemaps": cur["sitemaps"], "alertes": alertes, "infos": infos}
    json.dump(res, open(sortie, "w"), ensure_ascii=False, indent=1)
    print(f"thème {res['theme']} : {res['fichiers']} fichiers ({res['sensibles']} sensibles), robots {res['robots_regles']} règles, "
          f"{len(cur['sitemaps'])} sitemaps ; alertes {len(alertes)}, infos {len(infos)}")
    for a in alertes:
        print("  ALERTE", a)
    return 2 if alertes else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
