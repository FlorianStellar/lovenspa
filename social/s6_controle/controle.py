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
Avertissements (statut A_REVOIR) :
  LONGUEUR      hors de la plage cible de caractères
  OUVERTURE     ouverture maison usée (« Parfois », « Il y a des »…)
  CONCLUSION    morale finale usée (« Parce que… »)
  TICS          mots maison surutilisés dans ce texte
  REPETITION    trop proche des dernières légendes publiées (mêmes tics)
  TYPO          espace avant : ; ! ? (insécable), « » sans insécables, guillemets droits
  AUTRE_MONTANT un montant en euros qui n'est pas le prix du logement

Usage :
  python3 -m social.s6_controle.controle legende.txt --offre escale-spa-dinard [--marque <id>] [--historique snapshot.json]
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

    « L'Escale Dinard - L'Escale Spa » -> « l'escale dinard », « l'escale »."""
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


def verdict(paquet, rules=None, history=None):
    """Verdict d'un Paquet : texte contrôlé contre les Offres de sa case.

    Le moteur « couple » ne porte aucune offre par construction : le critère LOGEMENT ne s'y applique pas."""
    case = paquet["case"]
    offres = [f for f in case.get("offres") or [] if f]
    r = check(paquet["legende"], offres or None, history or [], rules)
    bloquants = [x for x in r["resultats"] if x["niveau"] == "bloquant"
                 and not (case["moteur"] == "couple" and x["code"] == "LOGEMENT")]
    if not paquet.get("medias"):
        bloquants.append({"code": "MEDIAS", "niveau": "bloquant", "message": "aucun média"})
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
