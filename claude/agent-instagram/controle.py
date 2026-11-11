#!/usr/bin/env python3
"""
Contrôle maison d'une légende Instagram Love'nSpa, avant validation humaine.

Bloquants (statut REFUSE) :
  ACCROCHE      la première ligne dépasse la zone visible (125 car.) ou est vide
  APPEL         zéro ou plusieurs appels à l'action (il en faut exactement un)
  LOGEMENT      aucun logement réel nommé (nom ou ville de la fiche Shopify)
  PRIX          un prix cité différent du « à partir de » de la fiche
  EXCLUS        un équipement non citable sur Instagram (regles.json)
  HASHTAGS      plus de 5 hashtags, ou #lovenspa absent
  A_COMPLETER   un {{trou}} reste dans le texte
Avertissements (statut A_REVOIR) :
  LONGUEUR      hors de la plage cible de caractères
  OUVERTURE     ouverture maison usée (« Parfois », « Il y a des »…)
  CONCLUSION    morale finale usée (« Parce que… »)
  TICS          mots maison surutilisés dans ce texte
  REPETITION    trop proche des dernières légendes publiées (mêmes tics)
  TYPO          espace manquante avant : ; ! ? ou guillemets droits

Usage :
  python3 controle.py legende.txt --logement escale-spa-dinard [--historique data/snapshot.json]
  python3 controle.py legende.txt --fiche fiche.json
Sortie : rapport texte, ou --json. Code de sortie 0 = OK, 1 = A_REVOIR, 2 = REFUSE.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
NBSP = "  "


def load_rules():
    with open(os.path.join(HERE, "regles.json"), encoding="utf-8") as f:
        return json.load(f)


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


def count_ctas(body, rules):
    n = norm(body)
    found = []
    for cta in rules["appels_a_l_action"]:
        pat = r"(?<![\w])" + re.escape(norm(cta)) + r"(?![\w])"
        if re.search(pat, n):
            found.append(cta)
    # « commente » et « commentez » désignent le même appel : on dédoublonne par racine
    roots, kept = set(), []
    for f in found:
        r = norm(f)[:6]
        if r not in roots:
            roots.add(r)
            kept.append(f)
    return kept


def prices_in(text):
    """Montants en euros cités : « 190 € », « 190€ », « 190 euros »."""
    vals = []
    for m in re.finditer(r"(\d{2,4}(?:[.,]\d{1,2})?)[\s  ]?(?:€|euros?\b)", text):
        vals.append(float(m.group(1).replace(",", ".")))
    return vals


def tics_in(body, rules):
    n = norm(body)
    return {t: n.count(norm(t)) for t in rules["tics_maison"] if n.count(norm(t))}


def repetition(body, history, rules):
    """Part des légendes récentes qui partagent au moins 3 tics avec celle-ci."""
    mine = set(tics_in(body, rules))
    if len(mine) < 3 or not history:
        return 0.0
    recent = history[: rules["fenetre_repetition"]]
    close = sum(1 for h in recent if len(mine & set(tics_in(split_caption(h)[0], rules))) >= 3)
    return close / len(recent)


def typo_issues(body):
    issues = []
    for m in re.finditer(r"(\S)([;:!?])", body):
        prev = m.group(1)
        if prev in NBSP or prev == " " or prev in "!?:;" or re.match(r"https?", body[max(0, m.start() - 6):m.start() + 1]):
            continue
        if m.group(2) == ":" and body[m.end():m.end() + 2] == "//":
            continue
        issues.append(f"espace manquante avant « {m.group(2)} » : …{body[max(0, m.start() - 12):m.end()]}")
    if '"' in body:
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
    if fiche is None:
        add("LOGEMENT", "bloquant", "aucune fiche logement fournie : impossible de vérifier un logement réel")
    else:
        n = norm(body)
        nom_court = norm(fiche["nom"].split(" - ")[0])
        villes = [norm(v) for v in (fiche.get("ville"), fiche.get("ville_reference")) if v]
        if nom_court not in n and not any(v in n for v in villes):
            add("LOGEMENT", "bloquant", f"ni « {fiche['nom'].split(' - ')[0]} » ni sa ville ne sont cités")
        for p in prices_in(body):
            if fiche.get("prix_a_partir_de") is None or abs(p - fiche["prix_a_partir_de"]) > 0.01:
                add("PRIX", "bloquant", f"prix cité {p:g} € ≠ fiche {fiche.get('prix_a_partir_de')}")
        for e in fiche.get("equipements_non_citables", []):
            if norm(e) in n:
                add("EXCLUS", "bloquant", f"équipement non citable sur Instagram : {e}")
    for e in rules["equipements_exclus_instagram"]:
        if norm(e) in norm(body) and not any(r["code"] == "EXCLUS" and e in r["message"] for r in res):
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
    last = [p for p in body.split("\n") if p.strip()]
    if last and any(last[-1].strip().startswith(c) for c in rules["conclusions_interdites"]):
        add("CONCLUSION", "avertissement", f"conclusion usée : « {last[-1].strip()[:40]}… »")
    t = tics_in(body, rules)
    if sum(t.values()) >= 3:
        add("TICS", "avertissement", "tics maison : " + ", ".join(f"{k} ×{v}" for k, v in t.items()))
    rep = repetition(body, history or [], rules)
    if rep >= rules["seuil_repetition"]:
        add("REPETITION", "avertissement", f"{rep:.0%} des dernières légendes partagent au moins 3 de ses tics")
    for i in typo_issues(body):
        add("TYPO", "avertissement", i)

    status = "REFUSE" if any(r["niveau"] == "bloquant" for r in res) else ("A_REVOIR" if res else "OK")
    return {"statut": status, "caracteres": len(body), "premiere_ligne": len(line1), "hashtags": tags,
            "appels": ctas, "resultats": res}


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
    ap.add_argument("--logement", help="handle Shopify (lecture en direct)")
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
    elif a.logement:
        from logements import Shop
        fiche = Shop().logement(a.logement)
    hist = history_from_snapshot(a.historique) if a.historique else []
    r = check(text, fiche, hist)
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else report(r))
    return {"OK": 0, "A_REVOIR": 1, "REFUSE": 2}[r["statut"]]


if __name__ == "__main__":
    sys.exit(main())
