#!/usr/bin/env python3
"""
detecter.py - cinq contrôles qui notent à quel point un brouillon en français
a l'air écrit par une machine.

Ce que c'est : cinq heuristiques locales, sur le modèle des signaux que
regardent les détecteurs d'IA publics : variation de longueur des phrases,
concret, vocabulaire tout fait, empreinte typographique, et voix. Tout est
calculé sur ta machine, à partir du texte. Rien n'est envoyé.

Ce que ce n'est PAS : GPTZero, Originality, Copyleaks, Winston ou Turnitin.
Aucun appel à leurs API, aucune promesse sur leur verdict.

Spécificités du français : l'espace insécable devant ; : ! ?, les guillemets
« » et l'apostrophe courbe (tapée par défaut sur iPhone) sont normaux et ne
comptent pas. Le contrôle VOIX regarde les tournures orales (« t'as », « y'a »,
« c'est pas », « ça ») au lieu des contractions anglaises.

Chaque contrôle renvoie un score HUMAIN de 0 à 100. Plus haut, c'est mieux.

Usage
  python3 detecter.py brouillon.txt
  python3 detecter.py avant.txt apres.txt
  python3 detecter.py brouillon.txt --json
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "lexique.json")

SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
WORD_RE = re.compile(r"[A-Za-zÀ-ÿœŒ'’-]+")
AP = "['’]"
# Tournures orales du français : élisions familières, négation sans "ne",
# "ça", mots du quotidien. Le texte écrit par une machine n'en a presque pas.
ORAL = re.compile(
    r"\bt" + AP + r"(?:as|es|étais|avais)\b|\by" + AP + r"a\b|\bj" + AP + r"(?:sais|suis|peux|crois)\b"
    r"|\b(?:c" + AP + r"est|j" + AP + r"ai|t" + AP + r"as|y a|on a|je sais|je peux|ça marche) pas\b"
    r"|\bfaut\b|\bça\b|\btruc\b|\bgenre\b|\bdu coup\b|\bbref\b|\ben vrai\b|\bouais\b|\bpote\b",
    re.IGNORECASE)
PRONOUNS = re.compile(r"\b(je|j|moi|mon|ma|mes|on|nous|notre|nos|tu|toi|ton|ta|tes|vous|votre|vos)\b",
                      re.IGNORECASE)
NUMBERS = re.compile(r"\b\d[\d,.]*\s?(?:%|€)?|€\s?\d")
PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b[A-ZÀ-Ý][a-zà-ÿ]{2,}\b|\b[A-Z]{2,5}\b", re.MULTILINE)



def read_file(path):
    """[lovenspa] lecture UTF-8 avec fermeture du fichier."""
    with open(path, encoding="utf-8") as f:
        return f.read()

def clamp(n):
    return max(0.0, min(100.0, n))


def scale(value, human, machine):
    """Map value onto 0-100 where `human` -> 100 and `machine` -> 0."""
    if human == machine:
        return 50.0
    return clamp((value - machine) / (human - machine) * 100)


def sentences(text):
    return [s.strip() for s in SENT_RE.findall(text) if len(s.split()) > 2]


def words(text):
    return WORD_RE.findall(text)


def check_burstiness(text):
    """Humans vary sentence length hard. Models write even."""
    lens = [len(s.split()) for s in sentences(text)]
    if len(lens) < 4:
        return 50.0, "trop court pour juger"
    mean = statistics.mean(lens)
    cv = statistics.pstdev(lens) / mean if mean else 0
    score = scale(cv, human=0.70, machine=0.22)
    return score, f"variation {cv:.2f} sur {len(lens)} phrases (vise 0,55+)"


def check_specificity(text):
    """Numbers, names and concrete nouns. Slop is abstract."""
    w = words(text)
    if len(w) < 25:
        return 50.0, "trop court pour juger"
    per100 = 100 / len(w)
    hits = len(NUMBERS.findall(text)) + len(set(PROPER.findall(text)))
    density = hits * per100
    score = scale(density, human=6.0, machine=0.5)
    return score, f"{hits} éléments concrets, {density:.1f} pour 100 mots (vise 4+)"


def check_slop(text, lex):
    """Stock vocabulary density against the lexicon."""
    w = words(text)
    if not w:
        return 50.0, "vide"
    hits, found = 0, []
    for entry in lex["words"] + lex["phrases"]:
        pattern = re.compile(r"\b" + re.escape(entry["find"]).replace(r"\ ", r"\s+") + r"\b",
                             re.IGNORECASE)
        n = len(pattern.findall(text))
        if n:
            hits += n
            found.append(entry["find"])
    density = hits * 100 / len(w)
    score = scale(density, human=0.0, machine=4.0)
    detail = f"{hits} cliché(s), {density:.1f} pour 100 mots"
    if found:
        detail += " (" + ", ".join(sorted(found)[:4]) + (", ..." if len(found) > 4 else "") + ")"
    return score, detail


def check_fingerprint(text):
    """Characters a phone keyboard does not produce."""
    invisible = sum(1 for c in text if unicodedata.category(c) == "Cf")
    em = text.count("—")
    em += text.count("–")
    curly = sum(text.count(c) for c in "“”")   # ’ et « » sont normaux en français
    ellip = 0  # [lovenspa] « … » est correct en français
    odd_space = sum(text.count(c) for c in "\u2009\u2007\u2003\u2002")  # hors insécables FR
    total = invisible * 4 + em * 2 + curly + ellip + odd_space
    per1k = total * 1000 / max(len(text), 1)
    score = scale(per1k, human=0.0, machine=12.0)
    detail = (f"{invisible} invisible(s), {em} tiret(s) long(s), {curly} guillemet(s) anglais, "
              f"{ellip} points de suspension en 1 car., {odd_space} espace(s) spéciale(s)")
    return score, detail


def check_voice(text, lex):
    """Contractions, person, and the shapes models default to."""
    w = words(text)
    if len(w) < 25:
        return 50.0, "trop court pour juger"
    per100 = 100 / len(w)
    contractions = len(ORAL.findall(text)) * per100
    person = len(PRONOUNS.findall(text)) * per100
    tells = 0
    names = []
    for s in lex["structures"]:
        try:
            n = len(re.compile(s["regex"], re.MULTILINE).findall(text))
        except re.error:
            continue
        if n:
            tells += n
            names.append(s["id"])
    bullets = [len(b.split()) for b in re.findall(r"(?m)^\s*[-*•]\s+(.+)$", text)]
    uniform = (len(bullets) >= 3 and statistics.pstdev(bullets) < 1.6)
    score = (scale(contractions, human=3.0, machine=0.0) * 0.35
             + scale(person, human=8.0, machine=1.0) * 0.35
             + clamp(100 - tells * 22) * 0.30)
    if uniform:
        score -= 12
        names.append("puces-uniformes")
    detail = (f"{contractions:.1f} tournures orales, {person:.1f} pronoms personnels "
              f"pour 100 mots, {tells} tic(s) de structure")
    if names:
        detail += " [" + ", ".join(names[:4]) + "]"
    return clamp(score), detail


CHECKS = ["RAFALE", "PRÉCISION", "DENSITÉ CLICHÉS", "EMPREINTE", "VOIX"]


def run(text, lex):
    results = {}
    results["RAFALE"] = check_burstiness(text)
    results["PRÉCISION"] = check_specificity(text)
    results["DENSITÉ CLICHÉS"] = check_slop(text, lex)
    results["EMPREINTE"] = check_fingerprint(text)
    results["VOIX"] = check_voice(text, lex)
    scores = [results[c][0] for c in CHECKS]
    # The weakest check drags the verdict: a detector only needs one signal.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4
    verdict = "OK" if overall >= 70 and min(scores) >= 55 else (
        "À REVOIR" if overall >= 50 else "SIGNALÉ")
    return results, overall, verdict


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render(results, overall, verdict, label=None, out=sys.stdout):
    title = "CONTRÔLE IA" + (f"  -  {label}" if label else "")
    print("\n" + title, file=out)
    print("=" * max(len(title), 62), file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<16} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<16} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'SCORE HUMAIN':<16} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    if verdict != "OK":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Signal le plus faible : {weakest}. Corrige-le d'abord.", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Note à quel point un brouillon a l'air écrit par une machine.")
    ap.add_argument("input", nargs="?", default="-", help="fichier, ou - pour stdin")
    ap.add_argument("compare", nargs="?", help="second fichier, pour avant / après")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lexique", "--lexicon", dest="lexicon", default=LEX)
    args = ap.parse_args()

    lex = json.loads(read_file(args.lexicon))
    read = lambda p: sys.stdin.read() if p == "-" else read_file(p)

    targets = [(args.input, read(args.input))]
    if args.compare:
        targets.append((args.compare, read(args.compare)))

    payload = []
    for name, text in targets:
        results, overall, verdict = run(text, lex)
        payload.append({
            "source": name,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "human_score": round(overall, 1),
            "verdict": verdict,
        })

    if args.json:
        print(json.dumps(payload if args.compare else payload[0], indent=2, ensure_ascii=False))
        return

    for (name, text), p in zip(targets, payload):
        results, overall, verdict = run(text, lex)
        render(results, overall, verdict, label=os.path.basename(name) if args.compare else None)
    if args.compare:
        a, b = payload
        delta = b["human_score"] - a["human_score"]
        print(f"  {a['human_score']:.1f} {a['verdict']}  ->  "
              f"{b['human_score']:.1f} {b['verdict']}   ({delta:+.1f})\n")

    sys.exit(0 if payload[-1]["verdict"] == "OK" else 1)


if __name__ == "__main__":
    main()
