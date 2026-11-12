#!/usr/bin/env python3
"""
S7 Diffusion : page « lien en bio » du site de la marque (ex. /pages/instagram).

Instagram n'accepte qu'un lien en bio : chaque publication pointe vers cette page, qui liste les logements
des dernières publications, chacun avec le lien tracé (UTM) de sa case. S8 sait ainsi quelle publication
a amené la visite (utm_content = date de la case).

Entrée : paquets (contrat paquet) des dernières publications, du plus récent au plus ancien.
Sortie : corps HTML de la page ; création ou mise à jour de la page Shopify (pageCreate / pageUpdate).
La page est créée NON publiée : la mise en ligne est une décision humaine (charte S7).

Usage : python3 -m social.s7_diffusion.page_bio --marque <id> <dossier_paquet> [...] [--ecrire]
"""
import argparse
import html
import json
import os
import sys

from social.marque import charger

MAX_ENTREES = 9


def entrees(paquets):
    """Une entrée par logement, dans l'ordre des publications, sans doublon ; moteur couple sans offre ignoré."""
    out, vus = [], set()
    for p in paquets:
        case = p["case"]
        for o in case.get("offres") or []:
            if not o or o["handle"] in vus:
                continue
            vus.add(o["handle"])
            lien = case.get("lien")
            if lien and len(case.get("offres") or []) > 1:  # sélection : URL du logement + suivi de la publication
                q = lien.split("?", 1)[1] if "?" in lien else ""
                lien = o["url"] + ("?" + q if q else "")
            out.append({"nom": o["nom"].split(" - ")[0], "ville": o.get("ville"), "prix": o.get("prix_a_partir_de"),
                        "unite": o.get("unite_prix"), "lien": lien or o["url"], "date": case["date"]})
    return out[:MAX_ENTREES]


def corps_html(items, titre="Les logements de nos dernières publications", en_tete=None):
    """en_tete : [(texte, url)] mis en avant au-dessus de la liste (ex. carte cadeau pendant un temps fort)."""
    e = html.escape
    lignes = [f'<p><a href="{e(u, quote=True)}"><strong>{e(x)}</strong></a></p>' for x, u in (en_tete or [])]
    lignes += [f"<p>{e(titre)}</p>", "<ul>"]
    for it in items:
        prix = f" · dès {it['prix']:g} € {e(it['unite'] or '')}" if it.get("prix") is not None else ""
        lignes.append(f'<li><a href="{e(it["lien"], quote=True)}">{e(it["nom"])}</a>'
                      f"{' · ' + e(it['ville']) if it.get('ville') else ''}{prix}</li>")
    lignes.append("</ul>")
    return "\n".join(lignes)


Q_PAGE = 'query($q: String!) { pages(first: 1, query: $q) { nodes { id handle isPublished } } }'
M_CREER = """mutation($p: PageCreateInput!) { pageCreate(page: $p) { page { id handle isPublished } userErrors { field message } } }"""
M_MAJ = """mutation($id: ID!, $p: PageUpdateInput!) { pageUpdate(id: $id, page: $p) { page { id handle isPublished }
  userErrors { field message } } }"""


def ecrire_page(shopify, handle, titre, corps):
    """Crée la page non publiée, ou met à jour son contenu sans toucher à son état de publication."""
    nodes = shopify.gql(Q_PAGE, {"q": f"handle:{handle}"})["pages"]["nodes"]
    if nodes:
        r = shopify.gql(M_MAJ, {"id": nodes[0]["id"], "p": {"body": corps}})["pageUpdate"]
    else:
        r = shopify.gql(M_CREER, {"p": {"title": titre, "handle": handle, "body": corps, "isPublished": False}})["pageCreate"]
    if r["userErrors"]:
        raise RuntimeError(f"page {handle} : {r['userErrors']}")
    return r["page"]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("dossiers", nargs="+", help="dossiers contenant paquet.json, du plus récent au plus ancien")
    ap.add_argument("--marque")
    ap.add_argument("--ecrire", action="store_true", help="écrire la page dans la boutique (non publiée)")
    ap.add_argument("--en-tete", action="append", default=[], help="« texte|url » mis en avant (répétable)")
    a = ap.parse_args(argv)
    m = charger(a.marque)
    paquets = []
    for d in a.dossiers:
        with open(os.path.join(d, "paquet.json"), encoding="utf-8") as f:
            paquets.append(json.load(f))
    cfg = m.config.get("page_bio", {"handle": "instagram", "titre": "Instagram"})
    corps = corps_html(entrees(paquets), en_tete=[tuple(x.split("|", 1)) for x in a.en_tete])
    print(corps)
    if a.ecrire:
        from social.connecteurs.shopify import Shopify
        print(ecrire_page(Shopify(m), cfg["handle"], cfg["titre"], corps))
    return 0


if __name__ == "__main__":
    sys.exit(main())
