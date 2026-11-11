#!/usr/bin/env python3
"""
S3 Catalogue : transforme les produits de la boutique en Offres (contrat contrats/offre.schema.json).

La correspondance des champs vient de marques/<marque>/catalogue.json ; les exclusions de
marques/<marque>/regles.json. Une Offre ne contient que ce qu'un contenu peut citer :
jamais d'e-mail, de téléphone, d'adresse ni de coordonnées du partenaire.

Usage :
  python3 -m social.s3_catalogue.offres <handle> [--marque <id>]
  python3 -m social.s3_catalogue.offres --chercher "tag:'Equipements|Sauna'" [--marque <id>]
"""
import argparse
import json
import sys
import time

from social.connecteurs.shopify import Shopify
from social.marque import charger


def _champ_gql(alias, spec):
    if "metafield" in spec:
        ns, key = spec["metafield"].split(".", 1)
        return f'{alias}: metafield(namespace: "{ns}", key: "{key}") {{ value }}'
    return ""


def champs_gql(marque):
    base = ("handle title status productType onlineStoreUrl tags "
            "priceRangeV2 { minVariantPrice { amount currencyCode } } mediaCount { count }")
    extra = [_champ_gql(k, v) for k, v in marque.catalogue["champs"].items()]
    return base + "\n  " + "\n  ".join(x for x in extra if x)


def tag_values(tags, prefix):
    """Valeurs des tags « prefix|valeur » (ex. Equipements|Sauna -> Sauna), ordre conservé, sans doublon."""
    out = []
    for t in tags or []:
        if t.startswith(prefix + "|"):
            v = t.split("|", 1)[1].strip()
            if v and v not in out:
                out.append(v)
    return out


def _valeur(node, nom, spec):
    v = None
    if "metafield" in spec:
        v = ((node.get(nom) or {}).get("value") or "").strip() or None
    if v is None and (spec.get("tag") or spec.get("repli_tag")):
        v = next(iter(tag_values(node.get("tags"), spec.get("tag") or spec.get("repli_tag"))), None)
    if v is not None and spec.get("type") == "int":
        try:
            v = int(v)
        except ValueError:
            v = None
    return v


def offre(node, marque):
    """Produit Shopify -> Offre. Pur : testable sans réseau."""
    if not node:
        return None
    cat, regles = marque.catalogue, marque.regles
    exclus = {e.lower() for e in regles["equipements_exclus_instagram"]}
    sans_interet = {e.lower() for e in regles["equipements_sans_interet"]}
    equip = tag_values(node.get("tags"), cat["tag_equipements"])
    price = (node.get("priceRangeV2") or {}).get("minVariantPrice") or {}
    amount = price.get("amount")
    vals = {k: _valeur(node, k, spec) for k, spec in cat["champs"].items()}
    amb = vals.get("ambiance")
    return {
        "handle": node["handle"],
        "nom": node["title"],
        "type": node.get("productType") or None,
        "ville": vals.get("ville"),
        "ville_reference": vals.get("ville_reference"),
        "region": vals.get("region"),
        "equipements": [e for e in equip if e.lower() not in exclus and e.lower() not in sans_interet],
        "equipements_non_citables": [e for e in equip if e.lower() in exclus],
        "prix_a_partir_de": float(amount) if amount not in (None, "") else None,
        "unite_prix": cat["unite_prix"],
        "devise": price.get("currencyCode"),
        "on_aime": vals.get("on_aime"),
        "ambiance": amb,
        "ambiance_libelle": cat["ambiances"].get(str(amb)) if amb is not None else None,
        "url": node.get("onlineStoreUrl") or f"{marque.site}/products/{node['handle']}",
        "actif": node.get("status") == "ACTIVE",
        "medias": (node.get("mediaCount") or {}).get("count", 0),
    }


Q_IMAGES = """query($q: String!) { products(first: 1, query: $q) { nodes { handle
  media(first: 12) { nodes { ... on MediaImage { image { url altText } } } } } } }"""


class Catalogue:
    def __init__(self, marque, connecteur=None):
        self.marque = marque
        self.c = connecteur or Shopify(marque)
        f = champs_gql(marque)
        self.q_un = "query($q: String!) { products(first: 1, query: $q) { nodes { %s } } }" % f
        self.q_cherche = "query($q: String!) { products(first: 10, query: $q) { nodes { %s } } }" % f
        self.q_tout = ("query($a: String) { products(first: 250, after: $a, query: \"%s\") { "
                       "pageInfo { hasNextPage endCursor } nodes { %s } } }") % (marque.catalogue["statut_actif"], f)

    def une(self, handle):
        nodes = self.c.gql(self.q_un, {"q": f"handle:{handle}"})["products"]["nodes"]
        return offre(nodes[0], self.marque) if nodes and nodes[0]["handle"] == handle else None

    def chercher(self, texte):
        q = f"{self.marque.catalogue['statut_actif']} {texte}".strip()
        return [offre(n, self.marque) for n in self.c.gql(self.q_cherche, {"q": q})["products"]["nodes"]]

    def toutes(self, pause=0.3):
        """Catalogue actif complet (toutes les pages)."""
        out, cursor = [], None
        while True:
            d = self.c.gql(self.q_tout, {"a": cursor})["products"]
            out += [offre(n, self.marque) for n in d["nodes"]]
            if not d["pageInfo"]["hasNextPage"]:
                return out
            cursor = d["pageInfo"]["endCursor"]
            time.sleep(pause)

    def images(self, handle, n=6):
        """URL des photos réelles de l'offre, dans l'ordre de la boutique."""
        nodes = self.c.gql(Q_IMAGES, {"q": f"handle:{handle}"})["products"]["nodes"]
        if not nodes or nodes[0]["handle"] != handle:
            return []
        return [m["image"]["url"] for m in nodes[0]["media"]["nodes"] if m.get("image")][:n]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("handle", nargs="?")
    ap.add_argument("--chercher")
    ap.add_argument("--marque")
    a = ap.parse_args(argv)
    cat = Catalogue(charger(a.marque))
    if a.chercher:
        res = cat.chercher(a.chercher)
    elif a.handle:
        res = cat.une(a.handle)
        if res is None:
            sys.exit(f"offre introuvable : {a.handle}")
    else:
        sys.exit(__doc__)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
