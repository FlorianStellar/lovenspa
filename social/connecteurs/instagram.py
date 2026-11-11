#!/usr/bin/env python3
"""
Connecteur Instagram Graph API (lecture, et publication pour S7) pour le compte d'une marque.
Compte et variable du jeton : marques/<marque>/marque.json, clé comptes.instagram.

Connexion permanente : jeton d'un utilisateur système Meta Business (n'expire pas),
enregistré comme secret réseau de l'environnement pour graph.facebook.com.
Le proxy l'injecte dans l'en-tête Authorization : le code n'a jamais le jeton.
En local, on peut aussi définir IG_ACCESS_TOKEN.

Variables optionnelles :
  IG_USER_ID        identifiant du compte Instagram professionnel (sinon découvert via /me/accounts)
  IG_USERNAME       impose le nom du compte (sinon celui de la marque)
  IG_GRAPH_VERSION  version d'API, ex. "v24.0" (défaut : version par défaut de l'app Meta)

Aucune écriture : ce client ne publie, ne commente et n'envoie rien.
"""
import os
import re
import time

import requests

HOST = "https://graph.facebook.com"
DEFAULT_USERNAME = None

MEDIA_FIELDS = ("id,caption,media_type,media_product_type,timestamp,permalink,"
                "like_count,comments_count")

# Métriques demandées par post. Celles que l'API refuse pour un post donné sont
# retirées une par une et notées dans post["metriques_indisponibles"].
MEDIA_METRICS = ("reach", "views", "saved", "shares", "likes", "comments",
                 "total_interactions", "follows", "profile_visits")
REEL_METRICS = ("ig_reels_avg_watch_time", "ig_reels_video_view_total_time")


class IGError(RuntimeError):
    def __init__(self, message, code=None, payload=None):
        super().__init__(message)
        self.code = code
        self.payload = payload or {}


def invalid_metric(err, requested):
    """Métrique à retirer de `requested` d'après le message d'erreur de l'API, ou None.

    Deux formes connues :
      « metric[3] must be one of the following values: reach, saved, ... » -> la première
        métrique demandée absente de la liste autorisée ;
      « ... does not support the follows metric for this media product type » -> la
        métrique demandée citée dans le message.
    """
    msg = str(err)
    m = re.search(r"must be one of the following values:\s*(.+)", msg)
    if m:
        allowed = set(re.findall(r"[a-z][a-z_]+", m.group(1)))
        for name in requested:
            if name not in allowed:
                return name
        return None
    words = set(re.findall(r"\b([a-z][a-z_]+)\b", msg))
    for name in requested:
        if name in words:
            return name
    return None


class IGClient:
    def __init__(self, user_id=None, session=None, version=None, pause=0.2, marque=None):
        self.version = version if version is not None else os.environ.get("IG_GRAPH_VERSION", "")
        self.user_id = user_id or os.environ.get("IG_USER_ID")
        self.s = session or requests.Session()
        compte = marque.compte("instagram") if marque else {}
        self.username = os.environ.get("IG_USERNAME") or compte.get("username")
        token = marque.env(compte["jeton_env"]) if marque else (
            os.environ.get("META_INSIGHT_API_KEY") or os.environ.get("IG_ACCESS_TOKEN"))
        # Sans jeton local, le proxy remplace cette valeur par le secret enregistré.
        self.s.headers.update({"Authorization": f"Bearer {token or 'proxy-injected'}"})
        self.pause = pause

    # ------------------------------------------------------------------ #
    def url(self, path):
        base = f"{HOST}/{self.version}" if self.version else HOST
        return path if path.startswith("http") else f"{base}/{path.lstrip('/')}"

    def get(self, path, params=None, retries=3):
        for attempt in range(retries + 1):
            r = self.s.get(self.url(path), params=params, timeout=60)
            try:
                data = r.json()
            except ValueError:
                data = {}
            if r.status_code == 200 and "error" not in data:
                return data
            err = data.get("error", {}) if isinstance(data, dict) else {}
            code = err.get("code")
            # 4 / 17 / 32 / 613 : limites de débit ; 1 / 2 : erreur transitoire
            if (code in (1, 2, 4, 17, 32, 613) or r.status_code >= 500) and attempt < retries:
                time.sleep(2 ** attempt * 5)
                continue
            raise IGError(err.get("message") or f"HTTP {r.status_code}", code, data)
        raise IGError("nombre d'essais dépassé")

    def post(self, path, data=None, retries=2):
        """POST (publication). Mêmes règles de nouvel essai que get(), sauf erreurs de contenu."""
        for attempt in range(retries + 1):
            r = self.s.post(self.url(path), data=data, timeout=120)
            try:
                payload = r.json()
            except ValueError:
                payload = {}
            if r.status_code == 200 and "error" not in payload:
                return payload
            err = payload.get("error", {}) if isinstance(payload, dict) else {}
            if (err.get("code") in (1, 2, 4, 17, 32, 613) or r.status_code >= 500) and attempt < retries:
                time.sleep(2 ** attempt * 5)
                continue
            raise IGError(err.get("message") or f"HTTP {r.status_code}", err.get("code"), payload)
        raise IGError("nombre d'essais dépassé")

    def paginate(self, path, params=None, limit_pages=1000):
        data = self.get(path, params)
        out = list(data.get("data", []))
        pages = 1
        while data.get("paging", {}).get("next") and pages < limit_pages:
            time.sleep(self.pause)
            data = self.get(data["paging"]["next"])
            out.extend(data.get("data", []))
            pages += 1
        return out

    # ------------------------------------------------------------------ #
    def discover_user_id(self, username=None):
        """Trouve l'ID du compte Instagram relié aux pages accessibles au jeton."""
        username = username or self.username
        if not username:
            raise IGError("nom du compte Instagram inconnu (marque ou IG_USERNAME)")
        pages = self.paginate("me/accounts", {"fields": "name,instagram_business_account{id,username}"})
        found = [p["instagram_business_account"] for p in pages if p.get("instagram_business_account")]
        for acc in found:
            if acc.get("username") == username:
                self.user_id = acc["id"]
                return acc["id"]
        names = [a.get("username") for a in found]
        raise IGError(f"compte {username} introuvable parmi {names}")

    def ensure_user(self):
        if not self.user_id:
            self.discover_user_id()
        return self.user_id

    def profile(self):
        uid = self.ensure_user()
        return self.get(uid, {"fields": "username,name,followers_count,follows_count,media_count,biography,website"})

    def media(self):
        """Toutes les publications du compte (jeu complet, toutes pages)."""
        uid = self.ensure_user()
        return self.paginate(f"{uid}/media", {"fields": MEDIA_FIELDS, "limit": 50})

    def media_insights(self, media):
        """Métriques d'un post. Retire les métriques refusées au lieu d'échouer."""
        metrics = list(MEDIA_METRICS)
        if media.get("media_product_type") == "REELS":
            metrics += list(REEL_METRICS)
        refused = []
        while metrics:
            try:
                data = self.get(f"{media['id']}/insights", {"metric": ",".join(metrics)})
                values = {d["name"]: (d.get("values") or [{}])[0].get("value", d.get("total_value", {}).get("value"))
                          for d in data.get("data", [])}
                return values, refused
            except IGError as e:
                bad = invalid_metric(e, metrics)
                if e.code == 100 and bad in metrics:
                    metrics.remove(bad)
                    refused.append(bad)
                    continue
                raise
        return {}, refused

    def account_reach_by_follow_type(self, since, until):
        """Portée du compte ventilée abonnés / non-abonnés (période de 30 jours max)."""
        uid = self.ensure_user()
        data = self.get(f"{uid}/insights", {
            "metric": "reach", "period": "day", "metric_type": "total_value",
            "breakdown": "follow_type", "since": since, "until": until})
        out = {}
        for d in data.get("data", []):
            for b in d.get("total_value", {}).get("breakdowns", []):
                for r in b.get("results", []):
                    out[r["dimension_values"][0]] = r["value"]
        return out

    def snapshot(self, with_insights=True):
        """Profil + toutes les publications + leurs métriques."""
        from datetime import date, timedelta
        prof = self.profile()
        posts = self.media()
        until = date.today()
        try:
            prof["portee_30j_par_type"] = self.account_reach_by_follow_type(
                (until - timedelta(days=29)).isoformat(), until.isoformat())
        except IGError as e:
            prof["portee_30j_par_type"] = {"erreur": str(e)}
        if with_insights:
            for p in posts:
                time.sleep(self.pause)
                try:
                    p["insights"], p["metriques_indisponibles"] = self.media_insights(p)
                except IGError as e:
                    p["insights"], p["erreur_insights"] = {}, str(e)
        return {"profil": prof, "publications": posts}
