#!/usr/bin/env python3
"""
Fiche d'un logement Love'nSpa pour une publication Instagram (lecture seule, Admin API Shopify).

Ne renvoie que ce qu'une légende peut citer : nom, type, ville, région, équipements
(hors liste d'exclusion de regles.json), prix « à partir de », « on aime », URL publique.
Jamais : e-mail, téléphone, adresse postale, coordonnées du partenaire.

Usage :
  python3 logements.py escale-spa-dinard            # fiche JSON
  python3 logements.py --chercher "sauna bretagne"  # 10 candidats actifs
"""
import json
import os
import sys
import time

import requests

SHOP = os.environ.get("SHOPIFY_FLAG_STORE") or os.environ.get("SHOPIFY_SHOP", "lovenspa.myshopify.com")
API = f"https://{SHOP}/admin/api/2025-10/graphql.json"
SITE = "https://www.lovenspa.fr"
HERE = os.path.dirname(os.path.abspath(__file__))

FIELDS = """handle title status productType onlineStoreUrl tags
  priceRangeV2 { minVariantPrice { amount currencyCode } }
  ville: metafield(namespace: "accentuate", key: "ville") { value }
  region: metafield(namespace: "accentuate", key: "region") { value }
  onAime: metafield(namespace: "accentuate", key: "on_aime") { value }"""
Q_ONE = "query($h: String!) { productByHandle(handle: $h) { %s } }" % FIELDS
Q_SEARCH = "query($q: String!) { products(first: 10, query: $q) { nodes { %s } } }" % FIELDS


def regles():
    with open(os.path.join(HERE, "regles.json"), encoding="utf-8") as f:
        return json.load(f)


def tag_values(tags, prefix):
    """Valeurs des tags « prefix|valeur » (ex. Equipements|Sauna -> Sauna), ordre conservé, sans doublon."""
    out = []
    for t in tags or []:
        if t.startswith(prefix + "|"):
            v = t.split("|", 1)[1].strip()
            if v and v not in out:
                out.append(v)
    return out


def fiche(node, rules=None):
    """Transforme un produit Shopify en faits citables. Pur : testable sans réseau."""
    if not node:
        return None
    rules = rules or regles()
    exclus = {e.lower() for e in rules["equipements_exclus_instagram"]}
    sans_interet = {e.lower() for e in rules["equipements_sans_interet"]}
    equip = tag_values(node.get("tags"), "Equipements")
    citables = [e for e in equip if e.lower() not in exclus and e.lower() not in sans_interet]
    price = (node.get("priceRangeV2") or {}).get("minVariantPrice") or {}
    ville = (node.get("ville") or {}).get("value") or next(iter(tag_values(node.get("tags"), "ville")), None)
    region = (node.get("region") or {}).get("value") or next(iter(tag_values(node.get("tags"), "region")), None)
    amount = price.get("amount")
    return {
        "handle": node["handle"],
        "nom": node["title"],
        "type": node.get("productType") or None,
        "ville": ville.strip() if ville else None,
        "region": region.strip() if region else None,
        # ville de rattachement des collections (souvent la grande ville proche : « près de Saint-Malo »)
        "ville_reference": next(iter(tag_values(node.get("tags"), "ville")), None),
        "equipements": citables,
        "equipements_non_citables": [e for e in equip if e.lower() in exclus],
        "prix_a_partir_de": float(amount) if amount not in (None, "") else None,
        "devise": price.get("currencyCode"),
        "on_aime": ((node.get("onAime") or {}).get("value") or "").strip() or None,
        "url": node.get("onlineStoreUrl") or f"{SITE}/products/{node['handle']}",
        "actif": node.get("status") == "ACTIVE",
    }


class Shop:
    def __init__(self, token=None, session=None):
        self.s = session or requests.Session()
        self.s.headers.update({"X-Shopify-Access-Token": token or os.environ.get("SHOPIFY_API_TOKEN", ""),
                               "Content-Type": "application/json"})

    def gql(self, query, variables):
        for attempt in range(5):
            r = self.s.post(API, json={"query": query, "variables": variables}, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            d = r.json()
            if d.get("errors"):
                raise RuntimeError(json.dumps(d["errors"])[:300])
            return d["data"]
        raise RuntimeError("Shopify : trop d'essais")

    def logement(self, handle):
        return fiche(self.gql(Q_ONE, {"h": handle}).get("productByHandle"))

    def chercher(self, texte):
        q = f"status:active {texte}".strip()
        return [fiche(n) for n in self.gql(Q_SEARCH, {"q": q})["products"]["nodes"]]


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    shop = Shop()
    if args[0] == "--chercher":
        res = shop.chercher(" ".join(args[1:]))
    else:
        res = shop.logement(args[0])
        if res is None:
            sys.exit(f"logement introuvable : {args[0]}")
    print(json.dumps(res, ensure_ascii=False, indent=1))
