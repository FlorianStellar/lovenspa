"""
Connecteur Shopify Admin GraphQL (lecture, plus l'hébergement de fichiers pour S7).

Interface commune des connecteurs : une classe avec gql(query, variables) -> dict.
Dans Stellar Fleet, cette classe est remplacée par un appel Nango sans changer les sous-systèmes.
"""
import json
import os
import time

import requests


class Shopify:
    def __init__(self, marque, token=None, session=None):
        b = marque.config["boutique"]
        domaine = os.environ.get(b["domaine_env"]) or b["domaine_defaut"]
        self.api = f"https://{domaine}/admin/api/{b['api_version']}/graphql.json"
        self.s = session or requests.Session()
        self.s.headers.update({"X-Shopify-Access-Token": token or os.environ.get(b["jeton_env"], ""),
                               "Content-Type": "application/json"})

    def gql(self, query, variables=None):
        for attempt in range(5):
            r = self.s.post(self.api, json={"query": query, "variables": variables or {}}, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            d = r.json()
            if d.get("errors"):
                if any("THROTTLED" in json.dumps(e) for e in d["errors"]):
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(json.dumps(d["errors"])[:300])
            return d["data"]
        raise RuntimeError("Shopify : trop d'essais")
