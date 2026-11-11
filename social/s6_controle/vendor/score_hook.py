#!/usr/bin/env python3
"""
score_hook.py - note la première ligne d'un Reel ou d'un TikTok sur les cinq
propriétés que partagent les hooks qui retiennent, et classe un lot de hooks
entre eux. Version française.

Ce que c'est : cinq heuristiques locales, calculées sur ta machine, à partir du
texte seul. Elles mesurent ce que les hooks qui retiennent ont souvent en
commun : une longueur qui se dit en moins de trois secondes, un élément
concret, un enjeu, l'info importante au début plutôt qu'à la fin, et une
personne à qui on s'adresse.

Ce que ce n'est PAS : un prédicteur de vues. L'outil d'origine (en anglais)
sépare bien un vrai hook d'un hook raté exprès, mais ne départage presque pas
deux bons hooks d'un même créateur. Cette version française n'a pas été
re-mesurée sur un corpus français. Utilise-la pour ce qu'elle fait bien :
repérer les salutations, les préambules, les hooks sans rien de concret et
ceux qui mettent cinq secondes à se dire. Pour départager deux bons hooks, fie
toi à ta courbe de rétention.

Chaque contrôle renvoie 0 à 100. Plus haut, c'est mieux.

Usage
  python3 score_hook.py hooks.txt              # un hook par ligne, classés
  python3 score_hook.py --hook "J'ai perdu 2 400 € sur une ligne oubliée."
  python3 score_hook.py hooks.txt --json
"""

import argparse
import json
import re
import statistics
import sys

AP = "'’"
WORD_RE = re.compile(r"[\wÀ-ÿœŒ$€%+'’-]+", re.UNICODE)
NUMBER_RE = re.compile(
    r"\d[\d\s.,]*\s?(?:€|k€|euros?|balles)"                 # argent
    r"|\b\d[\d.,]*\s?"                                      # un chiffre, avec
    r"(?:%|k\b|x\b|h\b|heures?\b|min\b|minutes?\b|s\b|sec\b|secondes?\b"
    r"|jours?\b|semaines?\b|mois\b|ans?\b|années?\b|e\b|ème\b)?",
    re.IGNORECASE)
PROPER_RE = re.compile(r"(?<![.!?]\s)\b[A-ZÀ-Ý][a-zà-ÿ]{2,}\b")
ACRONYM_RE = re.compile(r"\b[A-Z]{2,5}\b")              # CV, RH, CDI, SMIC
HASHTAG_RE = re.compile(r"(?:^|\s)#\w+")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")

# On dit les chiffres à voix haute. "Zéro euro" est aussi concret que "0 €".
# "un" et "premier" sont absents exprès : ce sont des mots de remplissage bien
# plus souvent que des quantités.
SPOKEN_NUMBERS = {
    "zéro", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf",
    "dix", "onze", "douze", "quinze", "vingt", "trente", "quarante",
    "cinquante", "soixante", "cent", "cents", "mille", "million", "millions",
    "milliard", "milliards", "douzaine", "moitié", "double", "triple",
    "deuxième", "troisième", "quatrième", "cinquième", "dixième",
}
MONEY_WORDS = {
    "euros", "euro", "balles", "smic", "salaire", "brut", "net", "loyer",
    "pourcent", "chiffre", "bénéfice", "facture", "devis", "prime",
}
# Les signes concrets propres à l'emploi et au quotidien en France.
CONCRETE_WORDS = {"cdi", "cdd", "bac", "bac+2", "bac+3", "bac+5", "rh", "cv"}

# Les mots qui mettent quelque chose en jeu. Un hook sans aucun d'eux est une
# affirmation ; avec un, c'est une raison de rester.
STAKES = {
    "arrête", "arrêtez", "stop", "jamais", "plus", "faux", "erreur", "erreurs",
    "perdu", "perdre", "perds", "coûté", "coûte", "coûter", "raté", "rater",
    "échec", "échoué", "personne", "rien", "aucun", "aucune", "pas", "sans",
    "viré", "licencié", "refusé", "refus", "supprimé", "supprime", "tué",
    "remplacé", "remplace", "gratuit", "payé", "payer", "embauché", "recruté",
    "rappelé", "ignoré", "interdit", "pire", "déteste", "gâché", "arnaque",
    "mensonge", "menti", "vérité", "secret", "caché", "volé", "avant",
    "jusqu", "mais", "sauf", "problème", "risque", "danger", "attention",
    "regret", "regrette", "dois", "devrais", "encore", "déjà", "seul",
    "seule", "seulement", "contre", "vs", "vraiment", "piège", "zéro",
    "maintenant", "désormais", "fini", "mort",
}

# Les ouvertures qui passent la première seconde à ne rien dire.
WEAK_OPENERS = [
    "alors", "bon", "ok", "okay", "salut", "coucou", "bonjour", "hello",
    "yo", "hey", "bienvenue", "aujourd'hui", "aujourd’hui", "donc", "en gros",
    "honnêtement", "écoute", "écoutez", "euh", "bref", "voilà", "juste",
    "je voulais", "je vais", "je veux", "est-ce que", "vous savez",
    "tu sais", "dans cette", "dans cette vidéo", "il y a beaucoup",
    "c'est quoi", "c’est quoi", "petite vidéo", "on va", "on se retrouve",
    "en tant que", "quand on", "le truc", "il faut", "il est",
]

# Les impératifs qui méritent la première place.
IMPERATIVES = {
    "arrête", "arrêtez", "stop", "pique", "vole", "copie", "supprime",
    "essaie", "essaye", "regarde", "regardez", "lis", "enregistre",
    "sauvegarde", "utilise", "construis", "fais", "faites", "écris",
    "envoie", "envoyez", "prends", "commence", "lâche", "ne", "n'",
    "mets", "vérifie", "change", "oublie", "oubliez", "teste",
}

ADDRESS_YOU = re.compile(
    r"\b(?:tu|toi|ton|ta|tes|te|t[" + AP + r"]|vous|votre|vos)\b", re.IGNORECASE)
ADDRESS_ME = re.compile(
    r"\b(?:je|j[" + AP + r"]|moi|mon|ma|mes|me|m[" + AP + r"]|on|nous|notre|nos)\b",
    re.IGNORECASE)

DEALBREAKERS = [
    (re.compile(r"(?i)^\s*(?:arrête[sz]? de scroller|arrêtez de scroller|stop(?:pe)? (?:ton|le) scroll|ne scrolle pas)"),
     "Commence par « arrête de scroller ». Réclamer l'attention prouve que tu ne l'as pas gagnée."),
    (re.compile(r"(?i)\b(?:dans (?:cette|la) (?:vidéo|vidéo d'aujourd'hui)|dans ce (?:reel|tiktok)|je vais (?:vous |te )?montrer|je vous montre comment|aujourd['’]hui on (?:va|parle))\b"),
     "Préambule de vidéo. Supprime-le et commence par le gain."),
    (re.compile(r"(?i)^\s*(?:salut|coucou|bonjour|hello|hey|yo|bienvenue)\b"),
     "Salutation. Personne n'est venu dans le fil pour qu'on lui dise bonjour."),
    (HASHTAG_RE,
     "Hashtag dans le hook. Les hashtags vont en bas de la légende, si quelque part."),
    (EMOJI_RE,
     "Emoji dans le hook. Le texte à l'écran en taille hook a la place pour des mots ou pour un emoji, pas les deux."),
]



def read_file(path):
    """[lovenspa] lecture UTF-8 avec fermeture du fichier."""
    with open(path, encoding="utf-8") as f:
        return f.read()

def clamp(n):
    return max(0.0, min(100.0, n))


def words(text):
    # "2 400 €" se dit en un bloc, donc un mot ici aussi.
    t = re.sub(r"(?<=\d)[\s.,\u00a0\u202f](?=\d{3}\b)", "", text)
    return WORD_RE.findall(t)


def norm(w):
    w = w.lower().strip(AP)
    # "l'erreur" -> "erreur", "d'argent" -> "argent", "n'a" -> "a"
    m = re.match(r"^(?:[ldjmtsnc]|qu|jusqu|lorsqu|puisqu)['’](.+)$", w)
    return m.group(1) if m else w


def check_length(text, mpm=160):
    """Un hook doit tomber avant que le pouce bouge. Environ deux secondes."""
    w = words(text)
    n = len(w)
    secs = n / (max(mpm, 1.0) / 60.0)  # [lovenspa] garde mpm <= 0
    chars = len(text.strip())
    if 5 <= n <= 12:
        score = 100.0
    elif n < 5:
        score = clamp(100 - (5 - n) * 20)
    else:
        score = clamp(100 - (n - 12) * 11)
    if chars > 65:                       # le français est plus long que l'anglais
        score -= 12
    return clamp(score), f"{n} mots, {chars} car., ~{secs:.1f} s à l'oral (vise 5 à 12 mots)"


def check_specificity(text):
    """Une chose concrète bat trois choses abstraites."""
    nums = [n.strip() for n in NUMBER_RE.findall(text) if n.strip() and re.search(r"\d", n)]
    propers = set(PROPER_RE.findall(text)) | set(ACRONYM_RE.findall(text))
    low = [norm(w) for w in words(text)]
    spoken = [w for w in low if w in SPOKEN_NUMBERS or w in MONEY_WORDS or w in CONCRETE_WORDS]
    seen, found_list = set(), []
    for item in nums + sorted(propers) + spoken:
        key = item.lower()
        if key not in seen and not any(key in s or s in key for s in seen):
            seen.add(key)
            found_list.append(item)
    hits = len(found_list)
    score = 15.0 if hits == 0 else clamp(45 + hits * 30)
    found = ", ".join(found_list[:4])
    return score, (f"{hits} élément(s) concret(s)" + (f" : {found}" if found else
                   " - pas de chiffre, pas de nom, rien de vérifiable"))


def check_stakes(text):
    """Tension, coût, négation. Quelque chose que le spectateur peut perdre."""
    w = [norm(x) for x in words(text)]
    hits = [x for x in w if x in STAKES]
    markers = sorted(set(hits))
    if re.search(r"\d\s?(?:€|k€|euros?)", text):
        markers.append("un prix")
    n = len(markers)
    score = {0: 20.0, 1: 70.0}.get(n, 100.0)
    detail = f"{n} marqueur(s) de tension" + (f" : {', '.join(markers[:4])}" if markers else
                                              " - rien n'est en jeu dans cette ligne")
    return clamp(score), detail


def check_frontload(text):
    """Le mot intéressant ne peut pas être en neuvième position."""
    w = words(text)
    if not w:
        return 0.0, "vide"
    low = [norm(x) for x in w]
    raw_low = text.strip().lower()
    penalty = 0
    hit_opener = None
    for weak in sorted(WEAK_OPENERS, key=len, reverse=True):
        if re.match(r"^\W*" + re.escape(weak) + r"\b", raw_low):
            penalty, hit_opener = 30, weak
            break
    payload = None
    for i, token in enumerate(low):
        if (token in STAKES or token in SPOKEN_NUMBERS or token in MONEY_WORDS
                or token in CONCRETE_WORDS or re.match(r"^\d", w[i])
                or (i and (PROPER_RE.match(w[i]) or ACRONYM_RE.match(w[i])))):
            payload = i
            break
    if payload is None:
        base, where = 30.0, "aucun mot fort dans la ligne"
    elif payload <= 3:
        base, where = 100.0, f"mot fort en position {payload + 1}"
    elif payload <= 6:
        base, where = 70.0, f"mot fort en position {payload + 1}, peut avancer"
    else:
        base, where = 40.0, f"mot fort en position {payload + 1}, trop tard"
    detail = where + (f" ; ouverture faible « {hit_opener} »" if hit_opener else "")
    return clamp(base - penalty), detail


def check_address(text):
    """Visé sur une personne, ou dans le vide."""
    w = [norm(x) for x in words(text)]
    if ADDRESS_YOU.search(text):
        return 100.0, "parle au spectateur (tu / vous)"
    if w and w[0] in IMPERATIVES:
        return 90.0, f"commence par un impératif (« {w[0]} »)"
    if ADDRESS_ME.search(text):
        return 70.0, "première personne, aucun spectateur nommé"
    return 35.0, "troisième personne, personne dans la pièce"


CHECKS = ["LONGUEUR", "PRÉCISION", "ENJEU", "ATTAQUE", "ADRESSE"]


def run(text, mpm=160):
    results = {
        "LONGUEUR": check_length(text, mpm),
        "PRÉCISION": check_specificity(text),
        "ENJEU": check_stakes(text),
        "ATTAQUE": check_frontload(text),
        "ADRESSE": check_address(text),
    }
    flags = [msg for pattern, msg in DEALBREAKERS if pattern.search(text)]
    scores = [results[c][0] for c in CHECKS]
    # La propriété la plus faible plafonne le hook : une seule suffit pour que
    # le pouce continue de défiler.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4 - len(flags) * 15
    overall = clamp(overall)
    verdict = "FORT" if overall >= 70 and min(scores) >= 55 and not flags else (
        "CORRECT" if overall >= 50 else "FAIBLE")
    return results, overall, verdict, flags


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render_one(text, results, overall, verdict, flags, out=sys.stdout):
    print("\nSCORE DU HOOK", file=out)
    print("=" * 62, file=out)
    print(f"  \"{text.strip()}\"\n", file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<13} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<13} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'SCORE':<13} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    for f in flags:
        print(f"\n  RÉDHIBITOIRE  {f}", file=out)
    if verdict != "FORT":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Point faible : {weakest}. Corrige celui-là et relance.", file=out)
    print("", file=out)


def render_table(rows, out=sys.stdout):
    print("\nCLASSEMENT DES HOOKS\n" + "=" * 78, file=out)
    for i, r in enumerate(rows, 1):
        mark = "->" if i == 1 else "  "
        hook = r["hook"] if len(r["hook"]) <= 62 else r["hook"][:59] + "..."
        print(f"{mark} {r['score']:5.1f} {r['verdict']:<8} {hook}", file=out)
        print(f"         point faible : {r['weakest']} ({r['checks'][r['weakest']]['score']:.0f})", file=out)
        for f in r["flags"]:
            print(f"         rédhibitoire : {f}", file=out)
    print("\nTourne le premier. Si le premier est sous 50, aucun de ceux-là n'est le hook.\n",
          file=out)


def main():
    ap = argparse.ArgumentParser(description="Note un hook de Reel ou de TikTok sur cinq propriétés.")
    ap.add_argument("input", nargs="?", default="-", help="fichier avec un hook par ligne, ou -")
    ap.add_argument("--hook", help="note un seul hook passé en ligne de commande")
    ap.add_argument("--mpm", type=float, default=160.0, help="débit en mots par minute (défaut 160)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.hook:
        lines = [args.hook]
    else:
        raw = sys.stdin.read() if args.input == "-" else read_file(args.input)
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
    if not lines:
        print("rien à noter", file=sys.stderr)
        sys.exit(2)

    payload = []
    for line in lines:
        results, overall, verdict, flags = run(line, args.mpm)
        payload.append({
            "hook": line,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "weakest": min(CHECKS, key=lambda c: results[c][0]),
            "flags": flags,
            "score": round(overall, 1),
            "verdict": verdict,
        })

    if args.json:
        print(json.dumps(payload if len(payload) > 1 else payload[0], indent=2, ensure_ascii=False))
        return

    if len(payload) == 1:
        results, overall, verdict, flags = run(lines[0], args.mpm)
        render_one(lines[0], results, overall, verdict, flags)
    else:
        render_table(sorted(payload, key=lambda r: -r["score"]))

    sys.exit(0 if max(p["score"] for p in payload) >= 70 else 1)


if __name__ == "__main__":
    main()
