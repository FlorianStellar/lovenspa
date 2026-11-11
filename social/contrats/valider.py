"""Validation des objets échangés entre sous-systèmes contre leurs schémas (contrats/*.schema.json)."""
import json
import os

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ICI = os.path.dirname(os.path.abspath(__file__))


def _schemas():
    out = {}
    for f in os.listdir(ICI):
        if f.endswith(".schema.json"):
            with open(os.path.join(ICI, f), encoding="utf-8") as fh:
                out[f] = json.load(fh)
    return out


SCHEMAS = _schemas()
REGISTRY = Registry().with_resources((k, Resource.from_contents(v)) for k, v in SCHEMAS.items())


def erreurs(objet, contrat):
    """Liste des erreurs de l'objet pour le contrat (« offre », « case »…) ; vide = conforme."""
    v = Draft202012Validator(SCHEMAS[f"{contrat}.schema.json"], registry=REGISTRY)
    return [f"{'/'.join(map(str, e.path)) or '(racine)'} : {e.message}" for e in v.iter_errors(objet)]


def valider(objet, contrat):
    errs = erreurs(objet, contrat)
    if errs:
        raise ValueError(f"contrat {contrat} non respecté : " + " ; ".join(errs[:5]))
    return objet
