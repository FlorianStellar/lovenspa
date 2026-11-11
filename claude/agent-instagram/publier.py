#!/usr/bin/env python3
"""
Publication autonome sur @lovenspa.fr par l'API officielle (Instagram Content Publishing).

Chaîne : médias locaux -> hébergement public Shopify Files -> conteneur Instagram -> publication
-> vérification (permalien) -> data/publies.json + journal.

Garde-fous (tous obligatoires) :
  1. interrupteur : IG_PUBLICATION_ACTIVE=1 dans l'environnement ET pas de fichier data/STOP ;
  2. pret.json au statut PRET (contrôle des légendes sans bloquant) ;
  3. date et heure de la case atteintes (heure de Paris) ;
  4. pas déjà publié (data/publies.json) ;
  5. au plus 2 publications par jour et quota API non atteint (content_publishing_limit).
Sans --go : simulation, rien n'est envoyé.

Usage :
  python3 publier.py data/production/2026-11-16-lieu [--go]
  python3 publier.py --dues [--go]        # toutes les cases prêtes dont l'heure est passée
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

import logements
from ig_client import IGClient, IGError

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
PARIS = ZoneInfo("Europe/Paris")
MAX_PAR_JOUR = 2

STAGED = """mutation($input: [StagedUploadInput!]!) { stagedUploadsCreate(input: $input) {
  stagedTargets { url resourceUrl parameters { name value } } userErrors { field message } } }"""
FILE_CREATE = """mutation($files: [FileCreateInput!]!) { fileCreate(files: $files) {
  files { id fileStatus } userErrors { field message } } }"""
FILE_GET = """query($id: ID!) { node(id: $id) { ... on MediaImage { fileStatus image { url } }
  ... on Video { fileStatus sources { url mimeType height } } } }"""


# ------------------------------------------------------------------ garde-fous
def interrupteur_ouvert(env=None, data_dir=DATA):
    env = os.environ if env is None else env
    return env.get("IG_PUBLICATION_ACTIVE") == "1" and not os.path.exists(os.path.join(data_dir, "STOP"))


def load_publies(data_dir=DATA):
    p = os.path.join(data_dir, "publies.json")
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def echeance(case):
    return datetime.fromisoformat(f"{case['date']}T{case.get('heure', '18:30')}").replace(tzinfo=PARIS)


def verifier(pret, publies, now):
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
    if sum(1 for p in publies if p.get("publie_le", "")[:10] == now.date().isoformat()) >= MAX_PAR_JOUR:
        raisons.append(f"plafond de {MAX_PAR_JOUR} publications par jour atteint")
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


def publier_instagram(ig, fmt, urls, caption):
    uid = ig.ensure_user()
    if fmt == "REELS":
        cid = ig.post(f"{uid}/media", {"media_type": "REELS", "video_url": urls[0], "caption": caption,
                                       "share_to_feed": "true"})["id"]
    elif len(urls) == 1:
        cid = ig.post(f"{uid}/media", {"image_url": urls[0], "caption": caption})["id"]
    else:
        children = [ig.post(f"{uid}/media", {"image_url": u, "is_carousel_item": "true"})["id"] for u in urls]
        for c in children:
            attendre_conteneur(ig, c)
        cid = ig.post(f"{uid}/media", {"media_type": "CAROUSEL", "children": ",".join(children),
                                       "caption": caption})["id"]
    attendre_conteneur(ig, cid)
    mid = ig.post(f"{uid}/media_publish", {"creation_id": cid})["id"]
    info = ig.get(mid, {"fields": "permalink,timestamp,media_product_type"})
    return mid, info.get("permalink")


def quota_ok(ig):
    uid = ig.ensure_user()
    d = ig.get(f"{uid}/content_publishing_limit", {"fields": "quota_usage,config"}).get("data", [{}])[0]
    total = (d.get("config") or {}).get("quota_total")
    return total is None or d.get("quota_usage", 0) < total


def enregistrer(pret, mid, permalink, now, data_dir=DATA):
    case = pret["case"]
    publies = load_publies(data_dir)
    for f in case.get("logements") or [{}]:
        publies.append({"cle": f"{case['date']}-{case['moteur']}", "date": case["date"], "moteur": case["moteur"],
                        "handle": (f or {}).get("handle"), "region": (f or {}).get("region"),
                        "media_id": mid, "permalink": permalink, "publie_le": now.isoformat(timespec="seconds")})
    with open(os.path.join(data_dir, "publies.json"), "w", encoding="utf-8") as fh:
        json.dump(publies, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "journal.md"), "a", encoding="utf-8") as fh:
        fh.write(f"- {now:%d/%m/%Y %H:%M} publié · {case['moteur']} · {case['format']} · {permalink}\n")


def traiter(folder, go=False, ig=None, shop=None, now=None):
    now = now or datetime.now(PARIS)
    with open(os.path.join(folder, "pret.json"), encoding="utf-8") as fh:
        pret = json.load(fh)
    raisons = verifier(pret, load_publies(), now)
    if not interrupteur_ouvert():
        raisons.append("interrupteur fermé (IG_PUBLICATION_ACTIVE≠1 ou data/STOP présent)")
    if raisons:
        return {"dossier": folder, "publie": False, "raisons": raisons}
    if not go:
        return {"dossier": folder, "publie": False, "raisons": ["simulation (--go absent)"], "medias": pret["medias"]}
    ig, shop = ig or IGClient(), shop or logements.Shop()
    if not quota_ok(ig):
        return {"dossier": folder, "publie": False, "raisons": ["quota de publication de l'API atteint"]}
    urls = [heberger(shop, m) for m in pret["medias"]]
    mid, permalink = publier_instagram(ig, pret["case"]["format"], urls, pret["legende"])
    enregistrer(pret, mid, permalink, now)
    return {"dossier": folder, "publie": True, "media_id": mid, "permalink": permalink}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier", nargs="?")
    ap.add_argument("--dues", action="store_true", help="toutes les cases prêtes dont l'heure est passée")
    ap.add_argument("--go", action="store_true", help="publier réellement")
    a = ap.parse_args(argv)
    folders = sorted(glob.glob(os.path.join(DATA, "production", "*", "pret.json"))) if a.dues else \
        [os.path.join(a.dossier, "pret.json")]
    code = 0
    for p in folders:
        try:
            r = traiter(os.path.dirname(p), go=a.go)
        except (IGError, RuntimeError) as e:
            r, code = {"dossier": os.path.dirname(p), "publie": False, "raisons": [f"ERREUR {e}"]}, 1
        print(json.dumps(r, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
