#!/usr/bin/env python3
"""
S6 Contrôle qualité : vérifie le texte d'un Paquet contre les règles de la marque (marques/<marque>/regles.json)
et les faits des Offres, puis rend un Verdict (contrats/verdict.schema.json).

Bloquants (statut REFUSE) :
  ACCROCHE      la première ligne dépasse la zone visible (125 car.) ou est vide
  APPEL         zéro ou plusieurs appels à l'action (il en faut exactement un)
  LOGEMENT      le logement de la fiche Shopify n'est pas nommé
  PRIX          un prix de logement (« dès X € », « X € la nuit ») différent du « à partir de » de la fiche
  EXCLUS        un équipement non citable sur Instagram (regles.json)
  HASHTAGS      plus de hashtags que la limite, ou hashtag de marque absent
  A_COMPLETER   un {{trou}} reste dans le texte
  EXPLICITE     un terme du lexique explicite de la marque (regles.json : lexique_explicite)
  AMBIANCE      une offre de la case hors des ambiances autorisées par la stratégie (verdict)
  FAIT_CHIFFRE  un chiffre avec unité (°C, cm, m, m², h, personnes…) absent de la fiche du logement (verdict)
  REVUE         revue visuelle absente ou faite sur une autre version du contenu (verdict)
  CONCOURS      mention obligatoire de concours absente (IG-R28, verdict)
  MEDIAS        aucun média (verdict)
Avertissements (statut A_REVOIR) :
  LONGUEUR      hors de la plage cible de caractères
  OUVERTURE     ouverture maison usée (« Parfois », « Il y a des »…)
  CONCLUSION    morale finale usée (« Parce que… »)
  TICS          mots maison surutilisés dans ce texte
  REPETITION    trop proche des dernières légendes publiées (mêmes tics)
  TYPO          espace avant : ; ! ? (insécable), « » sans insécables, guillemets droits
  AUTRE_MONTANT un montant en euros qui n'est pas le prix du logement
  EMOJI         plus d'emojis que la limite de la marque (regles.json : max_emojis_legende)
  TEMPS_FORT    le temps fort de la case n'est évoqué ni dans la légende ni à l'écran (verdict)

Usage :
  python3 -m social.s6_controle.controle legende.txt --offre <handle> [--marque <id>] [--historique snapshot.json]
  python3 -m social.s6_controle.controle legende.txt --fiche fiche.json
Sortie : rapport texte, ou --json. Code de sortie 0 = OK, 1 = A_REVOIR, 2 = REFUSE.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

NBSP = "  "


def load_rules(marque=None):
    from social.marque import charger
    return charger(marque).regles


def norm(s):
    """Minuscules, apostrophes unifiées, sans accents : pour les comparaisons seulement."""
    s = s.replace("’", "'").lower()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def split_caption(text):
    """(corps sans hashtags finaux, liste des hashtags)."""
    tags = re.findall(r"#[\wÀ-ſ]+", text)
    body = re.sub(r"(\s*#[\wÀ-ſ]+)+\s*$", "", text.strip()).strip()
    return body, tags


def first_line(body):
    for line in body.split("\n"):
        if line.strip():
            return line.strip()
    return ""


def word_in(needle, hay):
    """needle présent en mot entier dans hay (tous deux déjà normalisés)."""
    return re.search(r"(?<![\w])" + re.escape(needle) + r"(?![\w])", hay) is not None


def count_ctas(body, rules):
    """Familles d'appels à l'action présentes (lien, commentaire, enregistrer, partager, message).

    « Réservez via le lien en bio » = une seule famille (lien)."""
    n = norm(body)
    return [fam for fam, phrases in rules["appels_a_l_action"].items() if any(word_in(norm(p), n) for p in phrases)]


AMOUNT = r"(\d{1,3}(?:[ \u00a0\u202f]\d{3})*(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)[ \u00a0\u202f]?(?:€|euros?\b)"


def prices_in(text, rules=None):
    """Montants en euros : liste de (valeur, est_un_prix_de_logement).

    Prix de logement = précédé de « dès » / « à partir de » ou suivi de « la nuit », « par nuit »…"""
    ctx = (rules or load_rules())["contexte_prix_logement"]
    out = []
    for m in re.finditer(AMOUNT, text):
        val = float(re.sub(r"[ \u00a0\u202f]", "", m.group(1)).replace(",", "."))
        before, after = norm(text[max(0, m.start() - 20):m.start()]), norm(text[m.end():m.end() + 12])
        lodging = (any(re.search(re.escape(norm(b)) + r"\s*$", before) for b in ctx["avant"])
                   or any(after.strip().startswith(norm(a)) for a in ctx["apres"]))
        out.append((val, lodging))
    return out


def name_variants(nom):
    """Façons acceptées de nommer le logement : nom court (avant « - ») et ses débuts d'au moins 5 lettres utiles.

    Exemple : « Le Grand Chalet Alpin - Suite » -> « le grand chalet alpin », « le grand chalet », « le grand »."""
    short = norm(nom.split(" - ")[0]).strip()
    words = short.split()
    out = [short]
    for i in range(len(words) - 1, 0, -1):
        prefix = " ".join(words[:i])
        useful = re.sub(r"^(l'|le |la |les |au |aux |un |une |d'|du )", "", prefix)
        if len(re.sub(r"\W", "", useful)) >= 5:
            out.append(prefix)
    return out


def tics_in(body, rules):
    n = norm(body)
    out = {}
    for t in rules["tics_maison"]:
        c = len(re.findall(r"(?<![\w])" + re.escape(norm(t)) + r"(?![\w])", n))
        if c:
            out[t] = c
    return out


def repetition(body, history, rules):
    """Part des légendes récentes qui partagent au moins `tics_communs_min` tics avec celle-ci."""
    k = rules.get("tics_communs_min", 2)
    mine = set(tics_in(body, rules))
    if len(mine) < k or not history:
        return 0.0
    recent = history[: rules["fenetre_repetition"]]
    close = sum(1 for h in recent if len(mine & set(tics_in(split_caption(h)[0], rules))) >= k)
    return close / len(recent)


EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]")


def emojis_in(text):
    """Nombre d'emojis (pictogrammes) ; les sélecteurs de variante ne comptent pas."""
    return len(EMOJI_RE.findall(text))


def typo_issues(body):
    """Typographie française : espace avant ; : ! ? (insécable conseillée), « » avec espaces, guillemets droits."""
    text = re.sub(r"https?://\S+|www\.\S+", " ", body)
    issues = []
    for m in re.finditer(r"(.)([;:!?])", text):
        prev, sign = m.group(1), m.group(2)
        if prev in NBSP or prev in "!?:;" or prev == "\n":
            continue
        if sign == ":" and prev.isdigit() and text[m.end():m.end() + 1].isdigit():
            continue  # heure 16:00
        where = text[max(0, m.start() - 12):m.end()].replace("\n", " ")
        if prev == " ":
            issues.append(f"espace ordinaire avant « {sign} » (insécable conseillée) : …{where}")
        else:
            issues.append(f"espace manquante avant « {sign} » : …{where}")
    for m in re.finditer(r"«(.)|(.)»", text):
        c = m.group(1) if m.group(1) is not None else m.group(2)
        if c not in NBSP:
            issues.append("« » sans espace insécable à l'intérieur")
            break
    if '"' in text:
        issues.append("guillemets droits : utiliser « »")
    return issues


def check(text, fiche=None, history=None, rules=None):
    rules = rules or load_rules()
    L = rules["legende"]
    body, tags = split_caption(text)
    line1 = first_line(body)
    res = []

    def add(code, level, msg):
        res.append({"code": code, "niveau": level, "message": msg})

    if not line1:
        add("ACCROCHE", "bloquant", "première ligne vide")
    elif len(line1) > L["max_visible"]:
        add("ACCROCHE", "bloquant", f"première ligne de {len(line1)} caractères, coupée à {L['max_visible']} : "
                                    f"« {line1[:L['max_visible']]}… »")
    ctas = count_ctas(body, rules)
    if len(ctas) != 1:
        add("APPEL", "bloquant", f"{len(ctas)} appel(s) à l'action ({', '.join(ctas) or 'aucun'}) : il en faut un seul")
    if "{{" in text:
        add("A_COMPLETER", "bloquant", "texte à compléter : " + ", ".join(re.findall(r"\{\{[^}]*\}\}", text)))
    fiches = [f for f in (fiche if isinstance(fiche, list) else [fiche]) if f]
    if not fiches:
        add("LOGEMENT", "bloquant", "aucune fiche logement fournie : impossible de vérifier un logement réel")
    else:
        n = norm(body)
        missing = [f["nom"].split(" - ")[0] for f in fiches if not any(word_in(v, n) for v in name_variants(f["nom"]))]
        if missing:
            add("LOGEMENT", "bloquant", "logement(s) non nommé(s) : " + ", ".join(f"« {m} »" for m in missing))
        allowed = [f["prix_a_partir_de"] for f in fiches if f.get("prix_a_partir_de") is not None]
        for p, lodging in prices_in(body, rules):
            if not lodging:
                add("AUTRE_MONTANT", "avertissement", f"montant {p:g} € cité hors prix du logement : vérifier sa source")
            elif not any(abs(p - x) <= 0.01 for x in allowed):
                add("PRIX", "bloquant", f"prix cité {p:g} € absent des fiches ({', '.join(f'{x:g}' for x in allowed) or 'aucun prix'})")
        for f in fiches:
            for e in f.get("equipements_non_citables", []):
                if word_in(norm(e), n):
                    add("EXCLUS", "bloquant", f"équipement non citable sur Instagram : {e}")
    for terme in rules.get("lexique_explicite", []):
        if word_in(norm(terme), norm(text)):
            add("EXPLICITE", "bloquant", f"terme explicite : « {terme} » (ton de la marque : jamais explicite)")
    max_emo = rules.get("max_emojis_legende")
    if max_emo is not None and emojis_in(body) > max_emo:
        add("EMOJI", "avertissement", f"{emojis_in(body)} emojis (maximum de la marque : {max_emo})")
    for e in rules["equipements_exclus_instagram"]:
        if word_in(norm(e), norm(body)) and not any(r["code"] == "EXCLUS" and e in r["message"] for r in res):
            add("EXCLUS", "bloquant", f"équipement non citable sur Instagram : {e}")
    if len(tags) > L["max_hashtags"]:
        add("HASHTAGS", "bloquant", f"{len(tags)} hashtags (max {L['max_hashtags']})")
    if L["hashtag_marque"].lower() not in [t.lower() for t in tags]:
        add("HASHTAGS", "bloquant", f"{L['hashtag_marque']} absent")
    lo, hi = L["cible_caracteres"]
    if not lo <= len(body) <= hi:
        add("LONGUEUR", "avertissement", f"{len(body)} caractères (cible {lo} à {hi})")
    if any(line1.startswith(o) for o in rules["ouvertures_interdites"]):
        add("OUVERTURE", "avertissement", f"ouverture usée : « {line1[:40]}… »")
    paras = [p.strip() for p in body.split("\n") if p.strip()]
    for p in paras[-2:]:  # dernier paragraphe, ou celui juste avant l'appel à l'action
        if any(p.startswith(c) for c in rules["conclusions_interdites"]):
            add("CONCLUSION", "avertissement", f"conclusion usée : « {p[:40]}… »")
            break
    t = tics_in(body, rules)
    if sum(t.values()) >= 3:
        add("TICS", "avertissement", "tics maison : " + ", ".join(f"{k} ×{v}" for k, v in t.items()))
    rep = repetition(body, history or [], rules)
    if rep >= rules["seuil_repetition"]:
        add("REPETITION", "avertissement", f"{rep:.0%} des dernières légendes partagent au moins {rules.get('tics_communs_min', 2)} de ses tics")
    for i in typo_issues(body):
        add("TYPO", "avertissement", i)

    status = "REFUSE" if any(r["niveau"] == "bloquant" for r in res) else ("A_REVOIR" if res else "OK")
    return {"statut": status, "caracteres": len(body), "premiere_ligne": len(line1), "hashtags": tags,
            "appels": ctas, "resultats": res}


# Concours Instagram (IG-R28, help.instagram.com/179379842258600 ; décision du 12/11/2026 : bloquant).
MENTIONS_CONCOURS = {
    "REGLEMENT": (r"r[èe]glement", "lien ou mention du règlement du jeu"),
    "EXONERATION": (r"(d[ée]gag|exon[èée]r|d[ée]charg)\w*[^.\n]{0,80}instagram", "exonération d'Instagram par les participants"),
    "NON_PARRAINAGE": (r"(ni|pas|non)[^.\n]{0,30}(parrain|sponsoris)[^.\n]{0,80}instagram",
                       "mention « ni parrainé, ni approuvé, ni administré par Instagram »"),
}


def mentions_concours_manquantes(legende):
    return [m for code, (rx, m) in MENTIONS_CONCOURS.items() if not re.search(rx, legende, re.I)]


UNITES = r"(?:°\s?C|degrés|cm|m²|m2|mètres?|m|km|minutes?|min|heures?|h|personnes?|places?)"


def _nombres(texte):
    return {x.replace(",", ".").lstrip("0") or "0" for x in re.findall(r"\d+(?:[.,]\d+)?", texte or "")}


def check_ecran(textes, offres, rules):
    """Contrôle d'une story (pas de légende publiée) : lexique explicite, équipements exclus, prix des logements."""
    res = []
    corps = norm(" ".join(textes))
    for terme in rules.get("lexique_explicite", []):
        if word_in(norm(terme), corps):
            res.append({"code": "EXPLICITE", "niveau": "bloquant", "message": f"terme explicite : « {terme} »"})
    for e in rules["equipements_exclus_instagram"] + [x for o in offres for x in o.get("equipements_non_citables", [])]:
        if word_in(norm(e), corps):
            res.append({"code": "EXCLUS", "niveau": "bloquant", "message": f"équipement non citable sur Instagram : {e}"})
    allowed = [o["prix_a_partir_de"] for o in offres if o.get("prix_a_partir_de") is not None]
    for p, lodging in prices_in(" ".join(textes), rules):
        if lodging and not any(abs(p - x) <= 0.01 for x in allowed):
            res.append({"code": "PRIX", "niveau": "bloquant", "message": f"prix cité {p:g} € absent des fiches"})
    statut = "REFUSE" if any(r["niveau"] == "bloquant" for r in res) else "OK"
    return {"statut": statut, "caracteres": sum(len(t) for t in textes), "premiere_ligne": len(textes[0]) if textes else 0,
            "hashtags": [], "appels": [], "resultats": res}


def chiffres_non_sources(textes, offres):
    """Chiffres avec unité cités (légende et écran) qui ne figurent dans aucune source de l'offre
    (nom, description publique, équipements, ville). Les prix sont contrôlés à part (PRIX)."""
    source = " ".join(" ".join([o.get("nom") or "", o.get("description") or "", " ".join(o.get("equipements") or []),
                                o.get("ville") or ""]) for o in offres)
    connus = _nombres(source)
    out = []
    for t in textes:
        for m in re.finditer(rf"(\d+(?:[.,]\d+)?)\s?{UNITES}\b", t or "", re.I):
            n = m.group(1).replace(",", ".").lstrip("0") or "0"
            if n not in connus and m.group(0) not in out:
                out.append(m.group(0))
    return out


def evoque_temps_fort(theme, textes):
    """Le temps fort est évoqué si un mot significatif (5 lettres ou plus) de son intitulé apparaît."""
    if not theme:
        return True
    mots = [m for m in re.findall(r"[\wÀ-ÿ'-]+", theme.lower()) if len(m) >= 5 and m not in ("finit", "dans", "jusqu")]
    corps = norm(" ".join(textes))
    return not mots or any(norm(m) in corps for m in mots)


def empreinte(contenu):
    """Empreinte du contenu revu (textes, photos, cadrages), hors revue elle-même."""
    import hashlib
    c = {k: v for k, v in contenu.items() if k != "revue_visuelle"}
    return hashlib.sha256(json.dumps(c, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def verdict(paquet, rules=None, history=None, ambiances=None):
    """Verdict d'un Paquet : texte contrôlé contre les Offres de sa case.

    Le moteur « couple » ne porte aucune offre par construction : le critère LOGEMENT ne s'y applique pas."""
    case = paquet["case"]
    offres = [f for f in case.get("offres") or [] if f]
    if case.get("format") == "STORY":
        r = check_ecran(paquet.get("textes_ecran") or [], offres, rules or load_rules())
    else:
        r = check(paquet["legende"], offres or None, history or [], rules)
    # couple et recrutement ne présentent pas un logement : la règle LOGEMENT est sans objet
    # sans objet : LOGEMENT pour couple et recrutement ; montant repris du thème de la case (seuil d'une sélection)
    theme = case.get("theme") or ""
    r["resultats"] = [x for x in r["resultats"]
                      if not (case["moteur"] in ("couple", "recrutement") and x["code"] == "LOGEMENT")
                      and not (x["code"] == "AUTRE_MONTANT" and re.search(r"(\d+(?:[.,]\d+)?)", x["message"])
                               and (re.search(r"(\d+(?:[.,]\d+)?)", x["message"]).group(1) in theme
                                    or re.search(r"(\d+(?:[.,]\d+)?)", x["message"]).group(1)
                                    in (paquet.get("sources_montants") or {})))]
    bloquants = [x for x in r["resultats"] if x["niveau"] == "bloquant"]
    if not paquet.get("medias"):
        bloquants.append({"code": "MEDIAS", "niveau": "bloquant", "message": "aucun média"})
    textes = [paquet["legende"]] + list(paquet.get("textes_ecran") or [])
    if offres:
        # moteur couple : les diapositives sont des conseils, pas des faits sur le logement ; seule la légende est vérifiée
        for x in chiffres_non_sources(textes[:1] if case["moteur"] == "couple" else textes, offres):
            bloquants.append({"code": "FAIT_CHIFFRE", "niveau": "bloquant",
                              "message": f"« {x} » absent de la fiche du logement (nom, description, équipements)"})
    if "revue_visuelle" in paquet:
        rv = paquet["revue_visuelle"] or {}
        if rv.get("empreinte") != paquet.get("empreinte_contenu"):
            bloquants.append({"code": "REVUE", "niveau": "bloquant",
                              "message": "revue visuelle absente ou faite sur une autre version du contenu"})
        elif rv.get("statut") != "OK":
            bloquants.append({"code": "REVUE", "niveau": "bloquant", "message": "revue visuelle : " + rv.get("remarques", "")})
    if not evoque_temps_fort(case.get("temps_fort"), textes):
        r["resultats"].append({"code": "TEMPS_FORT", "niveau": "avertissement",
                               "message": f"temps fort non évoqué : « {case['temps_fort']} »"})
        if r["statut"] == "OK":
            r["statut"] = "A_REVOIR"
    if case["moteur"] == "concours":
        for m in mentions_concours_manquantes(paquet["legende"]):
            bloquants.append({"code": "CONCOURS", "niveau": "bloquant", "message": f"concours sans {m} (IG-R28)"})
    if ambiances is not None:
        for f in offres:
            if f.get("ambiance") not in ambiances:
                bloquants.append({"code": "AMBIANCE", "niveau": "bloquant",
                                  "message": f"« {f['nom']} » : ambiance {f.get('ambiance')} hors des ambiances autorisées {ambiances}"})
    # statut du contrôle aligné sur le verdict (plus de « PRET » à côté d'un contrôle « REFUSE »)
    r["statut"] = "REFUSE" if bloquants else ("A_REVOIR" if r["resultats"] else "OK")
    return {"statut": "PRET" if not bloquants else "REFUSE", "controle": r,
            "bloquants": [x["message"] for x in bloquants]}


def history_from_snapshot(path):
    with open(path, encoding="utf-8") as f:
        snap = json.load(f)
    posts = sorted(snap.get("publications", []), key=lambda p: p.get("timestamp", ""), reverse=True)
    return [p.get("caption") or "" for p in posts]


def report(r):
    out = [f"STATUT {r['statut']} · {r['caracteres']} caractères · 1re ligne {r['premiere_ligne']} · "
           f"{len(r['hashtags'])} hashtags · appel(s) : {', '.join(r['appels']) or 'aucun'}"]
    for x in r["resultats"]:
        out.append(f"  {'BLOQUE' if x['niveau'] == 'bloquant' else 'REVOIR'}  {x['code']:<11} {x['message']}")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("legende")
    ap.add_argument("--offre", help="handle de l'offre (lecture en direct dans la boutique)")
    ap.add_argument("--marque")
    ap.add_argument("--fiche", help="fiche JSON déjà extraite")
    ap.add_argument("--historique", help="instantané JSON (ig_client.py) pour le contrôle de répétition")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    with open(a.legende, encoding="utf-8") as f:
        text = f.read()
    fiche = None
    if a.fiche:
        with open(a.fiche, encoding="utf-8") as f:
            fiche = json.load(f)
    elif a.offre:
        from social.marque import charger
        from social.s3_catalogue.offres import Catalogue
        fiche = Catalogue(charger(a.marque)).une(a.offre)
    hist = history_from_snapshot(a.historique) if a.historique else []
    r = check(text, fiche, hist, load_rules(a.marque))
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else report(r))
    return {"OK": 0, "A_REVOIR": 1, "REFUSE": 2}[r["statut"]]


if __name__ == "__main__":
    sys.exit(main())
