"""
Configuration d'une marque : tout ce qui est propre à une marque vit dans social/marques/<id>/,
jamais dans le code. Le code reçoit un objet Marque.

Fichiers d'une marque :
  marque.json                    identité, boutique, comptes, kit graphique, ton
  catalogue.json                 correspondance des champs de la boutique vers le contrat Offre
  regles.json                    règles de contrôle des textes (S6)
  strategie_<plateforme>.json    stratégie validée par plateforme (S1)
  comptes_reference_<plateforme>.txt   comptes de référence pour la veille (S2)
"""
import json
import os

RACINE = os.path.dirname(os.path.abspath(__file__))
MARQUES = os.path.join(RACINE, "marques")
DONNEES = os.path.join(RACINE, "donnees")


def _lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


class Marque:
    def __init__(self, identifiant, dossier=None):
        self.id = identifiant
        self.dossier = dossier or os.path.join(MARQUES, identifiant)
        if not os.path.isdir(self.dossier):
            raise FileNotFoundError(f"marque inconnue : {identifiant} ({self.dossier})")
        self.config = _lire(os.path.join(self.dossier, "marque.json"))
        self.catalogue = _lire(os.path.join(self.dossier, "catalogue.json"))
        self.regles = _lire(os.path.join(self.dossier, "regles.json"))

    # -- accès simples
    @property
    def site(self):
        return self.config["site"].rstrip("/")

    @property
    def kit(self):
        return self.config["kit"]

    def compte(self, plateforme):
        return self.config["comptes"][plateforme]

    def strategie(self, plateforme):
        return _lire(os.path.join(self.dossier, f"strategie_{plateforme}.json"))

    def comptes_reference(self, plateforme):
        chemin = os.path.join(self.dossier, f"comptes_reference_{plateforme}.txt")
        with open(chemin, encoding="utf-8") as f:
            return [l.strip().lstrip("@") for l in f if l.strip() and not l.startswith("#")]

    def police(self, role):
        return os.path.join(self.dossier, self.kit["dossier_polices"], self.kit["polices"][role])

    def couleur(self, nom):
        h = self.kit["couleurs"][nom].lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def donnees(self, plateforme, *parties):
        """Dossier de données d'exécution de la marque pour une plateforme (créé au besoin)."""
        chemin = os.path.join(DONNEES, self.id, plateforme, *parties)
        os.makedirs(chemin if not os.path.splitext(chemin)[1] else os.path.dirname(chemin), exist_ok=True)
        return chemin

    def env(self, noms):
        for n in ([noms] if isinstance(noms, str) else noms):
            if os.environ.get(n):
                return os.environ[n]
        return None


def charger(identifiant=None):
    """Marque donnée en argument, sinon variable d'environnement SOCIAL_MARQUE (aucune marque par défaut)."""
    ident = identifiant or os.environ.get("SOCIAL_MARQUE")
    if not ident:
        raise ValueError("marque non précisée : --marque <id> ou variable SOCIAL_MARQUE")
    return Marque(ident)
