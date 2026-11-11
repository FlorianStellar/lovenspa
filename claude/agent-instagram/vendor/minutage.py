#!/usr/bin/env python3
"""
minutage.py - transforme un script de Reel ou de TikTok en conducteur minuté,
avant de tourner ou de générer la voix off.

Estime le temps de chaque ligne, empile les timecodes et signale les quatre
choses qui tuent une vidéo courte au montage : un hook qui dépasse 3 secondes,
un plan assez long pour que le spectateur parte, une suite de lignes sans rien
de concret, et une durée qui ne colle pas à la cible.

Deux modes :
- parlé (défaut) : la durée vient du débit en mots par minute. 160 par défaut
  en français. Mesure ton propre débit ou celui de ta voix off IA et passe-le
  avec --mpm.
- --lecture : pour les vidéos sans voix (texte à l'écran + musique). Chaque
  ligne est un carton à lire : environ 3 mots par seconde + 0,5 s, et jamais
  moins de 1,5 s à l'écran.

Les durées sont une estimation, pas un remplacement de l'enregistrement.

Usage
  python3 minutage.py script.txt
  python3 minutage.py script.txt --cible 30
  python3 minutage.py script.txt --mpm 175 --cible 45
  python3 minutage.py cartons.txt --lecture --cible 15
  python3 minutage.py script.txt --json
"""

import argparse
import json
import re
import sys

AP = "'’"
WORD_RE = re.compile(r"[\wÀ-ÿœŒ$€%+'’-]+", re.UNICODE)
SENT_RE = re.compile(r"[^.!?…]+[.!?…]*")
CONCRETE_RE = re.compile(
    r"\d|(?<!^)(?<![.!?]\s)\b[A-ZÀ-Ý][a-zà-ÿ]{2,}\b|\b[A-Z]{2,5}\b"
    r"|(?i:\b(?:zéro|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|quinze|vingt"
    r"|trente|quarante|cinquante|soixante|cent|mille|million|euros?|balles|smic|cdi|cdd)\b)",
    re.MULTILINE)
STOPWORDS = {
    "le", "la", "les", "l", "un", "une", "des", "de", "du", "d", "et", "ou",
    "mais", "si", "à", "au", "aux", "en", "dans", "sur", "pour", "par", "avec",
    "sans", "ce", "cet", "cette", "ces", "ça", "c", "est", "sont", "était",
    "a", "as", "ai", "ont", "être", "avoir", "tu", "te", "t", "toi", "ton",
    "ta", "tes", "vous", "votre", "vos", "je", "j", "me", "m", "moi", "mon",
    "ma", "mes", "on", "nous", "notre", "nos", "ils", "elles", "il", "elle",
    "se", "s", "qui", "que", "qu", "quoi", "ne", "n", "pas", "plus", "y",
    "fait", "fais", "faire", "peux", "peut", "tout", "tous", "bien", "là",
    "alors", "donc", "comme", "aussi", "très", "juste",
}

HOOK_WINDOW = 3.0        # secondes. Au-delà, le pouce a déjà décidé.
MAX_BEAT = 4.0           # secondes sur une idée sans changement à l'écran.
ABSTRACT_RUN = 3         # lignes d'affilée sans rien de vérifiable.



def read_file(path):
    """[lovenspa] lecture UTF-8 avec fermeture du fichier."""
    with open(path, encoding="utf-8") as f:
        return f.read()

def words(text):
    # "2 400 €" se dit d'un bloc, donc un mot ici aussi.
    t = re.sub(r"(?<=\d)[\s.,\u00a0\u202f](?=\d{3}\b)", "", text)
    return WORD_RE.findall(t)


def norm(w):
    w = w.lower().strip(AP)
    m = re.match(r"^(?:[ldjmtsnc]|qu|jusqu|lorsqu|puisqu)['’](.+)$", w)
    return m.group(1) if m else w


def tc(seconds):
    m, s = divmod(round(seconds, 1), 60)  # [lovenspa] évite « 0:60.0 »
    return f"{int(m)}:{s:04.1f}"


def duration(text, wps, lecture):
    n = len(words(text))
    if lecture:
        return max(1.5, n / 3.0 + 0.5)
    return n / wps


def split_beats(raw, wps, lecture):
    """Une ligne = un plan, sauf si elle est trop longue pour en être un."""
    beats = []
    for line in [l.strip() for l in raw.splitlines()]:
        if not line:
            continue
        if duration(line, wps, lecture) <= MAX_BEAT * 1.5:
            beats.append(line)
            continue
        parts = [p.strip() for p in SENT_RE.findall(line) if p.strip()]
        buf = ""
        for part in parts:
            candidate = (buf + " " + part).strip()
            if buf and duration(candidate, wps, lecture) > MAX_BEAT:
                beats.append(buf)
                buf = part
            else:
                buf = candidate
        if buf:
            beats.append(buf)
    return beats


def analyse(raw, mpm=160, target=None, lecture=False):
    wps = max(mpm, 1.0) / 60.0  # [lovenspa] garde mpm <= 0
    beats = split_beats(raw, wps, lecture)
    if not beats:
        return None

    rows, clock = [], 0.0
    for i, text in enumerate(beats):
        dur = duration(text, wps, lecture)
        rows.append({
            "n": i + 1,
            "start": round(clock, 2),
            "dur": round(dur, 2),
            "words": len(words(text)),
            "text": text,
            "concrete": len(CONCRETE_RE.findall(text)),
            "label": "",
            "flags": [],
        })
        clock += dur
    total = clock

    for r in rows:
        if r["n"] == 1 or r["start"] + r["dur"] <= HOOK_WINDOW:
            r["label"] = "HOOK"
    rows[-1]["label"] = "CTA" if rows[-1]["label"] != "HOOK" else "HOOK/CTA"
    half = total / 2
    for r in rows:
        if not r["label"] and r["start"] <= half < r["start"] + r["dur"]:
            r["label"] = "MILIEU"

    notes = []
    if rows[0]["dur"] > HOOK_WINDOW:
        rows[0]["flags"].append(f"le hook dure {rows[0]['dur']:.1f} s, au-delà des {HOOK_WINDOW:.0f} s")
        max_words = int((HOOK_WINDOW - 0.5) * 3) if lecture else int(HOOK_WINDOW * wps)
        notes.append(f"La ligne 1 prend {rows[0]['dur']:.1f} s. Descends à {max_words} mots "
                     "max, sinon le hook arrive après que la décision est prise.")
    if rows[0]["concrete"] == 0:
        notes.append("La ligne 1 n'a ni chiffre ni nom. Les hooks sans rien de vérifiable "
                     "sont ceux qu'on fait défiler.")

    for r in rows:
        if r["dur"] > MAX_BEAT:
            r["flags"].append(f"{r['dur']:.1f} s sur un seul plan")
    long_beats = [r["n"] for r in rows if r["dur"] > MAX_BEAT]
    if long_beats:
        notes.append(f"Ligne(s) {', '.join(map(str, long_beats))} au-delà de {MAX_BEAT:.0f} s. "
                     "Coupe la ligne ou change ce qu'il y a à l'écran pendant. "
                     "Un plan fixe, c'est là que les gens partent.")

    run, start = 0, None
    for r in rows:
        if r["concrete"] == 0:
            run += 1
            start = start if start is not None else r["n"]
            if run == ABSTRACT_RUN:
                notes.append(f"Lignes {start} à {r['n']} : rien de concret. "
                             "Mets un chiffre, un nom ou un prix dans l'une d'elles.")
        else:
            run, start = 0, None

    first = {norm(w) for w in words(rows[0]["text"])} - STOPWORDS
    last = {norm(w) for w in words(rows[-1]["text"])} - STOPWORDS
    loop = sorted(first & last)
    if loop:
        notes.append(f"Boucle : la dernière ligne reprend « {', '.join(loop[:3])} » du hook. "
                     "Les revisionnages, c'est de la portée gratuite.")
    else:
        notes.append("Pas de boucle. La dernière ligne ne partage aucun mot avec le hook, "
                     "la vidéo finit à plat. Reprendre un mot de la ligne 1, c'est le "
                     "revisionnage le moins cher.")

    if target:
        delta = total - target
        unit = "secondes de carton" if lecture else "mots"
        qty = (lambda d: f"{d:.1f}") if lecture else (lambda d: str(int(d * wps)))
        if abs(delta) <= target * 0.1:
            notes.append(f"Durée dans la cible ({total:.1f} s pour {target:g} s).")
        elif delta > 0:
            notes.append(f"{delta:.1f} s de trop. Coupe environ {qty(delta)} {unit}.")
        else:
            notes.append(f"{-delta:.1f} s sous la cible. Ajoute {qty(-delta)} {unit} "
                         "ou garde-la courte. Court, c'est souvent mieux.")

    return {
        "mode": "lecture" if lecture else "parlé",
        "mpm": mpm, "target": target,
        "total_seconds": round(total, 2),
        "total_words": sum(r["words"] for r in rows),
        "beats": rows,
        "notes": notes,
    }


def render(a, out=sys.stdout):
    rate = "cartons à lire" if a["mode"] == "lecture" else f"à {a['mpm']:g} mots/min"
    head = (f"CONDUCTEUR  ·  {a['total_words']} mots  ·  ~{a['total_seconds']:.1f} s "
            f"{rate}" + (f"  ·  cible {a['target']:g} s" if a["target"] else ""))
    print("\n" + head, file=out)
    print("=" * max(len(head), 72), file=out)
    for r in a["beats"]:
        label = f"{r['label']:<9}" if r["label"] else " " * 9
        print(f"  {tc(r['start'])}  {r['dur']:4.1f}s  {label}{r['text']}", file=out)
        for f in r["flags"]:
            print(f"  {'':>6}  {'':>5}  {'':<9}^ {f}", file=out)
    print("-" * max(len(head), 72), file=out)
    for n in a["notes"]:
        print(f"  - {n}", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Minute un script de vidéo courte.")
    ap.add_argument("input", nargs="?", default="-", help="fichier script, ou - pour stdin")
    ap.add_argument("--mpm", "--wpm", dest="mpm", type=float, default=160,
                    help="débit en mots par minute (défaut 160)")
    ap.add_argument("--cible", "--target", dest="cible", type=float, help="durée visée en secondes")
    ap.add_argument("--lecture", action="store_true",
                    help="vidéo sans voix : chaque ligne est un carton à lire")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else read_file(args.input)
    a = analyse(raw, mpm=args.mpm, target=args.cible, lecture=args.lecture)
    if not a:
        print("script vide", file=sys.stderr)
        sys.exit(2)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0)


if __name__ == "__main__":
    main()
