#!/usr/bin/env python3
"""
S7 Diffusion, adaptateur Instagram : publie un Paquet validé par l'API officielle (Content Publishing)
et produit une Publication (contrats/publication.schema.json).

Chaîne : médias locaux -> hébergement public Shopify Files -> conteneur Instagram -> publication
-> vérification (permalien) -> data/publies.json + journal.

Garde-fous (tous obligatoires) :
  1. interrupteur : IG_PUBLICATION_ACTIVE=1 dans l'environnement ET pas de fichier data/STOP ;
  2. verdict.json au statut PRET (S6 sans bloquant) ;
  3. date et heure de la case atteintes (heure de Paris) ;
  4. pas déjà publié (data/publies.json) ;
  5. au plus 2 publications par jour et quota API non atteint (content_publishing_limit).
Sans --go : simulation, rien n'est envoyé.

Usage :
  python3 -m social.s7_diffusion.instagram <dossier de production> [--marque <id>] [--go]
  python3 -m social.s7_diffusion.instagram --dues [--marque <id>] [--go]
"""
import argparse
import glob
import json
import mimetypes
import os
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from social.connecteurs.instagram import IGClient, IGError
from social.connecteurs.shopify import Shopify
from social.marque import charger
PARIS = ZoneInfo("Europe/Paris")

STAGED = """mutation($input: [StagedUploadInput!]!) { stagedUploadsCreate(input: $input) {
  stagedTargets { url resourceUrl parameters { name value } } userErrors { field message } } }"""
FILE_CREATE = """mutation($files: [FileCreateInput!]!) { fileCreate(files: $files) {
  files { id fileStatus } userErrors { field message } } }"""
FILE_GET = """query($id: ID!) { node(id: $id) { ... on MediaImage { fileStatus image { url } }
  ... on Video { fileStatus sources { url mimeType height } } } }"""


# ------------------------------------------------------------------ garde-fous
def interrupteur_ouvert(env=None, data_dir="."):
    env = os.environ if env is None else env
    return env.get("IG_PUBLICATION_ACTIVE") == "1" and not os.path.exists(os.path.join(data_dir, "STOP"))


def load_publies(data_dir="."):
    p = os.path.join(data_dir, "publies.json")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def echeance(case):
    return datetime.fromisoformat(f"{case['date']}T{case['heure']}").replace(tzinfo=PARIS)


def verifier(pret, publies, now, strat):
    """Liste des raisons de ne pas publier (vide = feu vert). Pure, testable."""
    case = pret["case"]
    raisons = []
    if pret.get("statut") != "PRET":
        raisons.append(f"statut {pret.get('statut')} : " + "; ".join(pret.get("bloquants", [])))
    if now < echeance(case):
        raisons.append(f"échéance non atteinte ({echeance(case):%d/%m %H:%M})")
    cle = f"{case['date']}-{case['moteur']}"
    if any(p.get("cle") == cle for p in publies):
        raisons.append(f"déjà publié ({cle})")
    # une publication à plusieurs offres compte pour une seule (clé unique par case)
    plafond = strat["plafond_publications_jour"]
    # le plafond vaut pour le fil : les stories du jour n'y comptent pas
    if case["format"] != "STORY" and len({p.get("cle") for p in publies if p.get("publie_le", "")[:10] == now.date().isoformat()
                                          and not p.get("cle", "").endswith("-story")}) >= plafond:
        raisons.append(f"plafond de {plafond} publications par jour atteint")
    if case["moteur"] not in strat.get("moteurs_valides", []):
        raisons.append(f"rendus du moteur « {case['moteur']} » non validés par un humain (jalon J4)")
    if not pret.get("medias"):
        raisons.append("aucun média")
    return raisons


# ------------------------------------------------------------------ hébergement
def heberger(shop, path, session=None, timeout=300):
    """Envoie un fichier dans Shopify Files et renvoie son URL publique (CDN)."""
    session = session or requests
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    is_video = mime.startswith("video/")
    size = os.path.getsize(path)
    st = shop.gql(STAGED, {"input": [{"filename": os.path.basename(path), "mimeType": mime, "httpMethod": "POST",
                                      "resource": "VIDEO" if is_video else "IMAGE", "fileSize": str(size)}]})
    st = st["stagedUploadsCreate"]
    if st["userErrors"]:
        raise RuntimeError(f"stagedUploadsCreate : {st['userErrors']}")
    target = st["stagedTargets"][0]
    with open(path, "rb") as fh:
        r = session.post(target["url"], data={p["name"]: p["value"] for p in target["parameters"]},
                         files={"file": (os.path.basename(path), fh, mime)}, timeout=300)
    if r.status_code >= 300:
        raise RuntimeError(f"envoi Shopify refusé : HTTP {r.status_code}")
    fc = shop.gql(FILE_CREATE, {"files": [{"originalSource": target["resourceUrl"],
                                           "contentType": "VIDEO" if is_video else "IMAGE"}]})["fileCreate"]
    if fc["userErrors"]:
        raise RuntimeError(f"fileCreate : {fc['userErrors']}")
    fid, t0 = fc["files"][0]["id"], time.time()
    while time.time() - t0 < timeout:
        node = shop.gql(FILE_GET, {"id": fid})["node"] or {}
        if node.get("fileStatus") == "READY":
            if is_video:
                mp4 = [s for s in node.get("sources") or [] if "mp4" in (s.get("mimeType") or "")]
                if mp4:  # plus haute définition disponible (Shopify propose 480p à 1080p)
                    return max(mp4, key=lambda s: s.get("height") or 0)["url"]
            elif (node.get("image") or {}).get("url"):
                return node["image"]["url"]
        if node.get("fileStatus") == "FAILED":
            raise RuntimeError(f"Shopify n'a pas pu traiter {path}")
        time.sleep(5)
    raise RuntimeError(f"délai dépassé pour l'hébergement de {path}")


# ------------------------------------------------------------------ Instagram
def attendre_conteneur(ig, cid, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        st = ig.get(cid, {"fields": "status_code,status"})
        if st.get("status_code") == "FINISHED":
            return
        if st.get("status_code") in ("ERROR", "EXPIRED"):
            raise IGError(f"conteneur {cid} : {st.get('status')}")
        time.sleep(10)
    raise IGError(f"conteneur {cid} : délai dépassé")


def publier_instagram(ig, fmt, urls, caption, ia=False):
    """ia : média photoréaliste généré ou modifié par IA -> is_ai_generated (IG-R31 ; carrousel : parent seul)."""
    uid = ig.ensure_user()
    label = {"is_ai_generated": "true"} if ia else {}
    if fmt == "STORY":
        # une story par image (IG-R17) ; on renvoie la dernière publiée
        mid = None
        for u in urls:
            cid = ig.post(f"{uid}/media", {"media_type": "STORIES", "image_url": u, **label})["id"]
            attendre_conteneur(ig, cid)
            mid = ig.post(f"{uid}/media_publish", {"creation_id": cid})["id"]
        return mid, None
    if fmt == "REELS":
        cid = ig.post(f"{uid}/media", {"media_type": "REELS", "video_url": urls[0], "caption": caption,
                                       "share_to_feed": "true", **label})["id"]
    elif len(urls) == 1:
        cid = ig.post(f"{uid}/media", {"image_url": urls[0], "caption": caption, **label})["id"]
    else:
        children = [ig.post(f"{uid}/media", {"image_url": u, "is_carousel_item": "true"})["id"] for u in urls]
        for c in children:
            attendre_conteneur(ig, c)
        cid = ig.post(f"{uid}/media", {"media_type": "CAROUSEL", "children": ",".join(children),
                                       "caption": caption, **label})["id"]
    attendre_conteneur(ig, cid)
    mid = ig.post(f"{uid}/media_publish", {"creation_id": cid})["id"]
    # Le post est en ligne : une erreur de lecture du permalien ne doit pas faire croire à un échec
    # (sinon une relance publierait un doublon). Le permalien manquant est relu par S8.
    try:
        permalink = ig.get(mid, {"fields": "permalink,timestamp,media_product_type"}).get("permalink")
    except IGError:
        permalink = None
    return mid, permalink


def quota_ok(ig):
    uid = ig.ensure_user()
    d = ig.get(f"{uid}/content_publishing_limit", {"fields": "quota_usage,config"}).get("data", [{}])[0]
    total = (d.get("config") or {}).get("quota_total")
    return total is None or d.get("quota_usage", 0) < total


def enregistrer(pret, mid, permalink, now, data_dir="."):
    case = pret["case"]
    publies = load_publies(data_dir)
    for f in case.get("offres") or [{}]:
        publies.append({"cle": f"{case['date']}-{case['moteur']}", "date": case["date"], "moteur": case["moteur"],
                        "plateforme": case.get("plateforme", "instagram"), "format": case["format"],
                        "handle": (f or {}).get("handle"), "region": (f or {}).get("region"),
                        "media_id": mid, "permalink": permalink, "publie_le": now.isoformat(timespec="seconds")})
    with open(os.path.join(data_dir, "publies.json"), "w", encoding="utf-8") as fh:
        json.dump(publies, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(data_dir, "journal.md"), "a", encoding="utf-8") as fh:
        fh.write(f"- {now:%d/%m/%Y %H:%M} publié · {case['moteur']} · {case['format']} · {permalink}\n")


def charger_pret(folder):
    """Paquet (S5) et Verdict (S6) réunis pour les contrôles de diffusion."""
    with open(os.path.join(folder, "paquet.json"), encoding="utf-8") as fh:
        paquet = json.load(fh)
    with open(os.path.join(folder, "verdict.json"), encoding="utf-8") as fh:
        v = json.load(fh)
    return {**paquet, "statut": v["statut"], "bloquants": v.get("bloquants", [])}


def traiter(folder, marque, go=False, ig=None, shop=None, now=None):
    now = now or datetime.now(PARIS)
    data_dir = marque.donnees("instagram")
    pret = charger_pret(folder)
    raisons = verifier(pret, load_publies(data_dir), now, marque.strategie("instagram"))
    if not interrupteur_ouvert(data_dir=data_dir):
        raisons.append("interrupteur fermé (IG_PUBLICATION_ACTIVE≠1 ou STOP présent)")
    if raisons:
        return {"dossier": folder, "publie": False, "raisons": raisons}
    if not go:
        return {"dossier": folder, "publie": False, "raisons": ["simulation (--go absent)"], "medias": pret["medias"]}
    ig, shop = ig or IGClient(marque=marque), shop or Shopify(marque)
    if not quota_ok(ig):
        return {"dossier": folder, "publie": False, "raisons": ["quota de publication de l'API atteint"]}
    urls = [heberger(shop, m) for m in pret["medias"]]
    mid, permalink = publier_instagram(ig, pret["case"]["format"], urls, pret["legende"],
                                        ia=bool(pret.get("ia_photorealiste")))
    enregistrer(pret, mid, permalink, now, data_dir)
    return {"dossier": folder, "publie": True, "media_id": mid, "permalink": permalink}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier", nargs="?")
    ap.add_argument("--marque")
    ap.add_argument("--dues", action="store_true", help="toutes les cases prêtes dont l'heure est passée")
    ap.add_argument("--go", action="store_true", help="publier réellement")
    a = ap.parse_args(argv)
    m = charger(a.marque)
    prod = m.donnees("instagram", "production")
    folders = sorted(os.path.dirname(p) for p in glob.glob(os.path.join(prod, "*", "verdict.json"))) if a.dues \
        else [a.dossier]
    code = 0
    for d in folders:
        try:
            r = traiter(d, m, go=a.go)
        except (IGError, RuntimeError) as e:
            r, code = {"dossier": d, "publie": False, "raisons": [f"ERREUR {e}"]}, 1
        print(json.dumps(r, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
