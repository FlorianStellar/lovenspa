#!/usr/bin/env python3
"""
S2 Connaissance : benchmark de comptes Instagram professionnels via l'API officielle (Business Discovery,
lecture seule). Liste des comptes : marques/<marque>/comptes_reference_instagram.txt.

Pour chaque compte : abonnés, nombre de posts, et ses N dernières publications
(date, format, likes, commentaires, légende). Les vues ne sont pas exposées par cette API :
l'engagement se mesure en likes + commentaires, rapporté aux abonnés et à la médiane du compte.
Les comptes qui masquent leurs likes renvoient like_count absent : exclus du calcul, signalés.

Usage :
  python3 -m social.s2_connaissance.benchmark [--marque <id>] [--comptes fichier.txt] [--n 50] [--md rapport.md]
"""
import argparse
import re
import json
import os
import statistics
import sys
import time
from datetime import date, datetime, timedelta

from social.connecteurs.instagram import IGClient, IGError
from social.marque import charger

MEDIA = "timestamp,media_type,media_product_type,like_count,comments_count,caption,permalink"


def discover(client, username, n=100, page=50):
    """Profil et jusqu'à n publications récentes (pagination de Business Discovery)."""
    uid = client.ensure_user()
    media, after, acc = [], None, {}
    while len(media) < n:
        lim = min(page, n - len(media))
        sel = f"media.after({after}).limit({lim})" if after else f"media.limit({lim})"
        fields = (f"business_discovery.username({username})"
                  f"{{username,name,followers_count,media_count,{sel}{{{MEDIA}}}}}")
        acc = client.get(uid, {"fields": fields}).get("business_discovery", {})
        bloc = acc.get("media") or {}
        media += bloc.get("data", [])
        after = (bloc.get("paging") or {}).get("cursors", {}).get("after")
        if not after or not bloc.get("data") or not (bloc.get("paging") or {}).get("next"):
            break
    acc["media"] = media
    return acc


def fmt(m):
    if m.get("media_product_type") == "REELS":
        return "REELS"
    return {"CAROUSEL_ALBUM": "CAROUSEL"}.get(m.get("media_type"), m.get("media_type") or "?")


def engagement(m):
    if not isinstance(m.get("like_count"), int):
        return None
    return m["like_count"] + (m.get("comments_count") or 0)


def summarize(acc, today=None):
    """Indicateurs d'un compte à partir de ses dernières publications (aucune extrapolation)."""
    today = today or date.today()
    media = acc.get("media", [])
    eng = [engagement(m) for m in media]
    eng_ok = [e for e in eng if e is not None]
    med = statistics.median(eng_ok) if eng_ok else None
    dates = sorted(m["timestamp"][:10] for m in media if m.get("timestamp"))
    weeks = None
    if len(dates) >= 2:
        span = (datetime.fromisoformat(dates[-1]) - datetime.fromisoformat(dates[0])).days
        weeks = max(span / 7, 1 / 7)
    formats = {}
    for m in media:
        formats[fmt(m)] = formats.get(fmt(m), 0) + 1
    followers = acc.get("followers_count")
    outliers = []
    if med:
        for m, e in zip(media, eng):
            if e is not None and e >= 3 * med:
                outliers.append({"multiple": round(e / med, 1), "format": fmt(m), "date": m["timestamp"][:10],
                                 "engagement": e, "accroche": (m.get("caption") or "").strip().split("\n")[0][:140],
                                 "permalink": m.get("permalink")})
    outliers.sort(key=lambda o: o["multiple"], reverse=True)
    last = dates[-1] if dates else None
    return {
        "username": acc.get("username"),
        "abonnes": followers,
        "posts_total": acc.get("media_count"),
        "posts_analyses": len(media),
        "likes_masques": len(media) - len(eng_ok),
        "periode": [dates[0], dates[-1]] if dates else None,
        "posts_par_semaine": round(len(media) / weeks, 2) if weeks else None,
        "part_reels": round(formats.get("REELS", 0) / len(media), 2) if media else None,
        "formats": formats,
        "engagement_median": med,
        "taux_engagement_median": round(med / followers * 100, 3) if med is not None and followers else None,
        "dernier_post_jours": (today - date.fromisoformat(last)).days if last else None,
        "outliers": outliers[:10],
    }


# ------------------------------------------------------------------ hygiène (S2-M01 à S2-M03)
HORS_ORGANIQUE = re.compile(
    r"concours|giveaway|jeu[- ]concours|à gagner|a gagner|tirage au sort|gagnez|sorteo|"
    r"#ad\b|#sponsoris|sponsoris|sponsored|partenariat|paid partnership|in partnership|#partner|"
    r"collaboration commerciale|collaboration avec|en collab|#partenaire|partenaire|affili|"
    r"#gifted|code promo|offert par|en association avec|s.associe|presented by|"
    r"\b[a-z][\w.]* x [\w.]*[a-z]|-\d{1,2} ?%|envoie le lien", re.I)
# Limite : la mention « Collaboration commerciale » d'Instagram est un libellé d'interface, absent de la légende
# lue par l'API ; seuls les partenariats écrits dans la légende sont détectés.
MOTS_FR = {"le", "la", "les", "des", "une", "un", "et", "pour", "avec", "vous", "nous", "dans", "sur", "est",
           "pas", "qui", "que", "votre", "notre", "plus", "au", "aux", "du", "ce", "cette", "à", "il", "elle",
           "en", "on", "mais", "ou", "donc", "quoi", "très", "tout", "tous", "sans", "chez"}
MOTS_EN = {"the", "and", "to", "of", "is", "for", "you", "your", "this", "with", "it", "in", "on", "are", "our"}
ELISION_FR = re.compile(r"\b[dljnmtsc]['’][a-zàâçéèêëîïôûùüÿœ]", re.I)
ACCENTS_FR = re.compile(r"[éèêàçùâîôûœ]", re.I)


def langue_fr(texte):
    """Repérage du français (pas un détecteur de langue) : mots outils, élisions (d’, j’, l’…) et accents
    français, à condition de l'emporter sur les mots outils anglais."""
    t = (texte or "").lower()
    mots = re.findall(r"[a-zàâçéèêëîïôûùüÿœ]+", t)
    fr = sum(1 for m in mots if m in MOTS_FR) + len(ELISION_FR.findall(t)) + (1 if ACCENTS_FR.search(t) else 0)
    en = sum(1 for m in mots if m in MOTS_EN)
    return fr >= 2 and fr > en


def anglais(texte):
    """Ligne dominée par les mots outils anglais (accroche anglaise d'une légende bilingue)."""
    mots = re.findall(r"[a-zàâçéèêëîïôûùüÿœ]+", (texte or "").lower())
    en = sum(1 for m in mots if m in MOTS_EN)
    return en >= 2 and en > sum(1 for m in mots if m in MOTS_FR)


def epinglees(media):
    """Indices des publications épinglées : en tête de liste mais plus anciennes qu'une publication suivante.
    L'API ne donne pas ce champ : repérage par l'ordre, documenté comme tel."""
    out = set()
    for i, m in enumerate(media[:3]):
        ts = m.get("timestamp") or ""
        if any((x.get("timestamp") or "") > ts for x in media[i + 1:]):
            out.add(i)
    return out


def analyser(acc, today=None, fenetre=(7, 180), seuil=3.0, minimum=10):
    """Multiple d'interactions par compte et par format, avec l'hygiène S2-M03.

    Renvoie les groupes (format -> taille de l'échantillon, médiane, statut), les publications mises à part
    (épinglées, hors organique) et les publications au-dessus du seuil, sans rien estimer."""
    today = today or date.today()
    media = acc.get("media", [])
    pin = epinglees(media)
    debut, fin = (today - timedelta(days=fenetre[1])).isoformat(), (today - timedelta(days=fenetre[0])).isoformat()
    a_part, propres = [], {}
    for i, m in enumerate(media):
        d = (m.get("timestamp") or "")[:10]
        if not d or not (debut <= d <= fin):
            continue
        cap = m.get("caption") or ""
        base = {"date": d, "format": fmt(m), "engagement": engagement(m), "permalink": m.get("permalink"),
                "accroche": cap.strip().split("\n")[0][:200], "langue_fr": langue_fr(cap)}
        if i in pin:
            a_part.append({**base, "motif": "épinglée"})
        elif HORS_ORGANIQUE.search(cap):
            a_part.append({**base, "motif": "hors organique (concours, partenariat)"})
        elif base["engagement"] is None:
            a_part.append({**base, "motif": "interactions masquées"})
        else:
            propres.setdefault(base["format"], []).append(base)
    groupes, signaux = {}, []
    for f, items in propres.items():
        if len(items) < minimum:
            groupes[f] = {"n": len(items), "mediane": None, "statut": "échantillon trop petit"}
            continue
        med = statistics.median(i["engagement"] for i in items)
        groupes[f] = {"n": len(items), "mediane": med, "statut": "classé"}
        if not med:
            continue
        for it in items:
            mult = it["engagement"] / med
            if mult >= seuil:
                signaux.append({**it, "compte": acc.get("username"), "multiple": round(mult, 2), "mediane_ref": med})
    for p in a_part:  # multiple indicatif des publications mises à part, contre la médiane organique du format
        med = (groupes.get(p["format"]) or {}).get("mediane")
        p["multiple_indicatif"] = round(p["engagement"] / med, 2) if med and p["engagement"] is not None else None
    signaux.sort(key=lambda s: s["multiple"], reverse=True)
    return {"username": acc.get("username"), "abonnes": acc.get("followers_count"), "fenetre": [debut, fin],
            "groupes": groupes, "a_part": a_part, "signaux": signaux, "metrique": "likes + commentaires (S2-M02)"}


def to_markdown(rows, errors):
    def v(x, suf=""):
        return "-" if x is None else f"{x}{suf}"
    out = ["| Compte | Abonnés | Posts | Posts/sem. | Part Reels | Engagement médian | Taux méd. | Dernier post (j) |",
           "|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["abonnes"] or 0, reverse=True):
        out.append(f"| {r['username']} | {v(r['abonnes'])} | {v(r['posts_total'])} | {v(r['posts_par_semaine'])} | "
                   f"{v(None if r['part_reels'] is None else round(r['part_reels'] * 100), ' %')} | "
                   f"{v(r['engagement_median'])} | {v(r['taux_engagement_median'], ' %')} | {v(r['dernier_post_jours'])} |")
    if errors:
        out += ["", "Comptes non lus (personnels, inexistants ou renommés) : " + ", ".join(f"{u} ({e[:60]})" for u, e in errors)]
    out += ["", "## Publications à plus de 3 fois l'engagement médian du compte", ""]
    for r in rows:
        if r["outliers"]:
            out.append(f"### {r['username']}")
            out += [f"- {o['multiple']}x · {o['format']} · {o['date']} · [{o['accroche'] or '(sans légende)'}]({o['permalink']})"
                    for o in r["outliers"][:5]]
            out.append("")
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--marque")
    ap.add_argument("--comptes", help="fichier : un nom d'utilisateur par ligne (défaut : liste de la marque)")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--out")
    ap.add_argument("--md")
    a = ap.parse_args(argv)
    m = charger(a.marque)
    if a.comptes:
        with open(a.comptes, encoding="utf-8") as f:
            users = [l.strip().lstrip("@") for l in f if l.strip() and not l.startswith("#")]
    else:
        users = m.comptes_reference("instagram")
    client = IGClient(marque=m)
    raw, rows, errors, analyses = {}, [], [], []
    for u in users:
        try:
            acc = discover(client, u, a.n)
            raw[u] = acc
            rows.append(summarize(acc))
            analyses.append(analyser(acc))
        except IGError as e:
            errors.append((u, str(e)))
        time.sleep(1)
    today = date.today().isoformat()
    out = a.out or m.donnees("instagram", f"benchmark-{today}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"date": today, "comptes": raw, "erreurs": errors, "analyses": analyses}, f, ensure_ascii=False, indent=1)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(to_markdown(rows, errors))
    print(f"{len(rows)} comptes lus, {len(errors)} non lus -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
