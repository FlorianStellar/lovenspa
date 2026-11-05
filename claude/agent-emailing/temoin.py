"""Groupe témoin : 10 % des clients, tirage reproductible par hash de l'identifiant Klaviyo."""
import hashlib
def is_temoin(profile_id: str) -> bool:
    return int(hashlib.sha256(profile_id.encode()).hexdigest(), 16) % 10 == 0
