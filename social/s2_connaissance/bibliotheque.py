#!/usr/bin/env python3
"""
S2 Connaissance : construit la bibliothèque d'une plateforme à partir du benchmark nettoyé et classé.

Entrées :
  - fiches d'amorce (blocs JSON de la skill social-veille, references/formats.md) ;
  - signaux classés (bibliotheque/<plateforme>/signaux_classes.json : publications à 3x et plus de la médiane
    de leur compte, chacune rattachée à une fiche et à une formule d'accroche, avec sa justification).
Sorties (bibliotheque/<plateforme>/) :
  - formats/<id>.json : une fiche par format, contrat fiche_format, niveau de preuve recalculé ;
  - accroches_observees.json : premières lignes réelles des publications françaises qui surperforment ;
  - synthese.md : tableau de relecture humaine.

Niveaux de preuve (S2, skill social-veille) :
  A : nos propres publications le confirment (au moins 4 essais au-dessus de la médiane du compte) — non calculé ici ;
  B : au moins 3 comptes distincts avec un signal à 3x ou plus dans la fiche ;
  C : moins de 3 comptes.
Les publications hors organique (concours, partenariats) ne comptent jamais pour un niveau B.

Usage : python3 -m social.s2_connaissance.bibliotheque [--plateforme instagram] [--skill-formats <chemin>]
"""
import argparse
import json
import os
import re
import sys

from social.contrats.valider import erreurs

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE_DEPOT = os.path.dirname(os.path.dirname(ICI))
FORMATS_SKILL = os.path.join(RACINE_DEPOT, ".claude", "skills", "social-veille", "references", "formats.md")
SEUIL_B = 3


def fiches_amorce(chemin=FORMATS_SKILL):
    """Blocs ```json``` du fichier de formats de la skill (fiches F01…)."""
    with open(chemin, encoding="utf-8") as f:
        texte = f.read()
    return [json.loads(b) for b in re.findall(r"```json\n(.*?)\n```", texte, re.S)]


def rafraichir(signaux, benchmark_json):
    """Recalcule langue et caractère hors organique de chaque signal sur sa légende complète
    (filtres de benchmark.py), sans toucher au classement humain ou agent."""
    from social.s2_connaissance.benchmark import HORS_ORGANIQUE, anglais, langue_fr
    legendes = {m.get("permalink"): m.get("caption") or ""
                for acc in benchmark_json["comptes"].values() for m in acc.get("media", [])}
    out = []
    for s in signaux:
        cap = legendes.get(s["permalink"], s.get("accroche") or "")
        out.append({**s, "langue_fr": langue_fr(cap) and not anglais(s.get("accroche")),
                    "hors_organique": bool(HORS_ORGANIQUE.search(cap))})
    return out


def organiques(signaux):
    return [s for s in signaux if not s.get("hors_organique")]


def preuves(signaux):
    """fiche -> {comptes: [...], signaux: [...]} pour les signaux organiques classés."""
    out = {}
    for s in signaux:
        fid = s.get("fiche_format")
        if not fid:
            continue
        e = out.setdefault(fid, {"comptes": set(), "signaux": []})
        e["comptes"].add(s["compte"])
        e["signaux"].append(s)
    return out


def niveau(nb_comptes, fiche_id, hors_organique_ids=("F02",)):
    if fiche_id in hors_organique_ids:
        return "C"  # mécanique de concours : jamais de preuve organique (S2-M03, point 5)
    return "B" if nb_comptes >= SEUIL_B else "C"


def construire(fiches, signaux, date_benchmark):
    """Fiches mises à jour (pur, testable)."""
    p = preuves(organiques(signaux))
    out = []
    for f in fiches:
        e = p.get(f["id"], {"comptes": set(), "signaux": []})
        sig = sorted(e["signaux"], key=lambda s: s["multiple"], reverse=True)
        comptes = sorted(e["comptes"])
        nf = dict(f)
        nf["preuve"] = niveau(len(comptes), f["id"])
        nf["observe"] = (f"Benchmark du {date_benchmark} (hygiène S2-M03, multiple d'interactions) : "
                         f"{len(comptes)} compte(s) avec au moins un signal à 3x ou plus"
                         + (f" : {', '.join(comptes)}." if comptes else "."))
        nf["exemples"] = [f"{s['permalink']} ({s['compte']}, {s['multiple']:g}x)" for s in sig[:5]] or f.get("exemples", [])
        if f["id"] == "F02":
            nf["observe"] += " Concours : publications mises à part (hors organique), aucune preuve organique possible."
        if not nf.get("sources"):
            nf["sources"] = []
        src = f"benchmark Business Discovery du {date_benchmark}"
        if src not in nf["sources"]:
            nf["sources"] = nf["sources"] + [src]
        out.append(nf)
    return out


def _pertinence(s):
    """Pertinence pour la marque, quel que soit le nom du champ (« pertinence_<marque> » ou « pertinence »)."""
    return next((v for k, v in s.items() if k.startswith("pertinence")), None)


def accroches_observees(signaux):
    """Premières lignes réelles en français, classées par multiple (aucune réécriture)."""
    out = [{"accroche": s["accroche"], "compte": s["compte"], "format": s["format"], "multiple": s["multiple"],
            "date": s["date"], "permalink": s["permalink"], "fiche_format": s.get("fiche_format"),
            "formule_accroche": s.get("formule_accroche"), "pertinence": _pertinence(s),
            "nature": "première ligne de légende (pas l'accroche parlée, S2-M06)"}
           for s in organiques(signaux) if s.get("langue_fr") and (s.get("accroche") or "").strip()]
    return sorted(out, key=lambda a: a["multiple"], reverse=True)


def synthese_md(fiches, accroches, date_benchmark):
    lignes = [f"# Bibliothèque Instagram, version 1 (benchmark du {date_benchmark})", "",
              "| Fiche | Format | Preuve | Comptes | Meilleur exemple |", "|---|---|---|---|---|"]
    for f in fiches:
        lignes.append(f"| {f['id']} | {f['nom']} | {f['preuve']} | {f['observe'].split(':')[1].split('compte')[0].strip()} | "
                      f"{(f.get('exemples') or ['-'])[0]} |")
    lignes += ["", f"## Accroches réelles en français ({len(accroches)})", "",
               "| Multiple | Compte | Format | Première ligne | Fiche | Formule |", "|---|---|---|---|---|---|"]
    for a in accroches:
        txt = a["accroche"].replace("|", "/")[:120]
        lignes.append(f"| {a['multiple']:g}x | {a['compte']} | {a['format']} | [{txt}]({a['permalink']}) | "
                      f"{a['fiche_format'] or '-'} | {a['formule_accroche'] or '-'} |")
    return "\n".join(lignes) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--plateforme", default="instagram")
    ap.add_argument("--skill-formats", default=FORMATS_SKILL)
    ap.add_argument("--date-benchmark", required=True)
    ap.add_argument("--benchmark", required=True, help="fichier JSON du benchmark (légendes complètes)")
    a = ap.parse_args(argv)
    dossier = os.path.join(ICI, "bibliotheque", a.plateforme)
    with open(os.path.join(dossier, "signaux_classes.json"), encoding="utf-8") as f:
        signaux = json.load(f)
    with open(a.benchmark, encoding="utf-8") as f:
        signaux = rafraichir(signaux, json.load(f))
    with open(os.path.join(dossier, "signaux_classes.json"), "w", encoding="utf-8") as f:
        json.dump(signaux, f, ensure_ascii=False, indent=1)
    fiches = construire(fiches_amorce(a.skill_formats), signaux, a.date_benchmark)
    os.makedirs(os.path.join(dossier, "formats"), exist_ok=True)
    for f in fiches:
        errs = erreurs(f, "fiche_format")
        if errs:
            raise SystemExit(f"{f['id']} hors contrat : {errs}")
        with open(os.path.join(dossier, "formats", f"{f['id']}.json"), "w", encoding="utf-8") as h:
            json.dump(f, h, ensure_ascii=False, indent=2)
    acc = accroches_observees(signaux)
    with open(os.path.join(dossier, "accroches_observees.json"), "w", encoding="utf-8") as h:
        json.dump(acc, h, ensure_ascii=False, indent=1)
    with open(os.path.join(dossier, "synthese.md"), "w", encoding="utf-8") as h:
        h.write(synthese_md(fiches, acc, a.date_benchmark))
    nb = {k: sum(1 for f in fiches if f["preuve"] == k) for k in "ABC"}
    print(f"{len(fiches)} fiches (A {nb['A']}, B {nb['B']}, C {nb['C']}), {len(acc)} accroches réelles FR -> {dossier}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
