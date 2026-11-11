"""Surveillance quotidienne : thème live (checksums), robots.txt, sitemaps GSC.

Usage : python surveillance_technique.py <dossier_etat> <sortie.json>
<dossier_etat> garde le dernier instantané (etat.json + contenu des fichiers SEO sensibles).
Lecture seule. Code 2 si un changement sensible est détecté.
"""
import hashlib, json, os, re, sys, time
from pathlib import Path

SENSIBLES = re.compile(r"^(layout/|templates/robots\.txt|snippets/.*(seo|meta|json|schema|canonical|head\.|breadcrumb|hreflang))", re.I)
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
    return sorted(l.strip() for l in (txt or "").splitlines()
                  if l.strip().lower().startswith(("disallow", "allow", "sitemap", "user-agent")))


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
            if SENSIBLES.match(f):
                alertes += risques(f, contenus_prec.get(f, ""), contenus_cur.get(f, ""))
    if prec.get("robots") is not None and prec["robots"] != cur["robots"]:
        rp, rc = set(prec["robots"]), set(cur["robots"])
        alertes.append(f"robots.txt modifié : +{sorted(rc - rp)} -{sorted(rp - rc)}")
    for sm, n in cur.get("sitemaps", {}).items():
        p = prec.get("sitemaps", {}).get(sm)
        if p and n["soumises"] < p["soumises"] * 0.9:
            alertes.append(f"sitemap {sm} : URL soumises {p['soumises']} → {n['soumises']}")
        if n["erreurs"] > (p or {}).get("erreurs", 0):
            alertes.append(f"sitemap {sm} : erreurs {(p or {}).get('erreurs', 0)} → {n['erreurs']}")
    return alertes, infos


def collecter(admin, gsc, http_get):
    t = admin.gql(Q_THEME)["themes"]["nodes"][0]
    fichiers, after = {}, None
    while True:
        r = admin.gql(Q_FILES, {"id": t["id"], "after": after})["theme"]["files"]
        fichiers.update({n["filename"]: n["checksumMd5"] for n in r["nodes"]})
        if not r["pageInfo"]["hasNextPage"]:
            break
        after = r["pageInfo"]["endCursor"]
    sens = sorted(f for f in fichiers if SENSIBLES.match(f))
    contenus = {}
    for i in range(0, len(sens), 50):
        for n in admin.gql(Q_BODY, {"id": t["id"], "f": sens[i:i + 50]})["theme"]["files"]["nodes"]:
            contenus[n["filename"]] = (n.get("body") or {}).get("content", "")
    sitemaps = {s["path"]: {"soumises": sum(int(c.get("submitted", 0)) for c in s.get("contents", [])),
                            "erreurs": int(s.get("errors", 0))} for s in gsc.list_sitemaps()}
    return {"theme_id": t["id"], "theme_name": t["name"], "fichiers": fichiers,
            "robots": robots_regles(http_get("https://lovenspa.fr/robots.txt")),
            "sitemaps": sitemaps}, contenus


def http_get(url, essais=4):
    import requests
    for i in range(essais):
        r = requests.get(url, timeout=30, headers={"User-Agent": "lovenspa-seo-monitor"})
        if r.status_code == 200 and "Verifying your connection" not in r.text:
            return r.text
        time.sleep(20 * (i + 1))
    raise RuntimeError(f"{url}: HTTP {r.status_code}")


def main(argv):
    from site_export import Admin
    from gsc_client import GSCClient
    etat_dir, sortie = Path(argv[1]), argv[2]
    etat_dir.mkdir(parents=True, exist_ok=True)
    cur, contenus = collecter(Admin(), GSCClient(), http_get)
    fe, fc = etat_dir / "etat.json", etat_dir / "contenus.json"
    prec = json.loads(fe.read_text()) if fe.exists() else {}
    cprec = json.loads(fc.read_text()) if fc.exists() else {}
    alertes, infos = comparer(prec, cur, cprec, contenus) if prec else ([], ["premier instantané"])
    fe.write_text(json.dumps(cur, ensure_ascii=False, indent=1))
    fc.write_text(json.dumps(contenus, ensure_ascii=False))
    res = {"theme": cur["theme_name"], "fichiers": len(cur["fichiers"]), "sensibles": len(contenus),
           "robots_regles": len(cur["robots"]), "sitemaps": cur["sitemaps"], "alertes": alertes, "infos": infos}
    json.dump(res, open(sortie, "w"), ensure_ascii=False, indent=1)
    print(f"thème {res['theme']} : {res['fichiers']} fichiers ({res['sensibles']} sensibles), robots {res['robots_regles']} règles, "
          f"{len(cur['sitemaps'])} sitemaps ; alertes {len(alertes)}, infos {len(infos)}")
    for a in alertes:
        print("  ALERTE", a)
    return 2 if alertes else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
