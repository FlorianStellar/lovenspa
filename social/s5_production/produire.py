#!/usr/bin/env python3
"""
S5 Production : fabrique le Paquet d'une case (contrat contrats/paquet.schema.json) à partir des textes
rédigés par l'agent, puis demande le Verdict à S6 (contrats/verdict.schema.json).

Entrée : donnees/<marque>/<plateforme>/production/<date>-<moteur>/contenu.json
  {
    "case": { ... case du plan (date, plateforme, moteur, format, offres, lien) ... },
    "legende": "texte complet de la légende",
    "reel_lignes": ["accroche à l'écran", "ligne 2", ...],          # moteur lieu
    "reel_photos": [3, 1, 7, ...],                                  # rang (1 = première) de la photo de la boutique
                                                                    # choisie pour chaque ligne, après l'avoir regardée
    "couverture": {"titre": "...", "sous_titre": "...", "photo": 2},  # sélection / concours ; photo = rang (option)
    "couple": {"titre": "...", "diapos": [{"titre": "...", "texte": "..."}], "cta": "..."},
    "fin": {"titre": "...", "texte": "..."}                          # dernière diapositive (sélection / concours)
  }
Sorties dans le même dossier : médias, paquet.json, verdict.json.

Usage : python3 -m social.s5_production.produire <dossier> [--marque <id>]
"""
import argparse
import json
import os
import sys

from social.contrats.valider import valider
from social.marque import charger
from social.s3_catalogue.offres import Catalogue
from social.s5_production import visuels
from social.s6_controle import controle

MAX_DIAPOS = 10  # choix éditorial (décision du 12/11/2026) ; Instagram en accepte 20 (IG-R05, IG-R06)


def typo_fr(texte):
    """Espaces insécables de la typographie française : avant « : », guillemets intérieurs (espace fine avant ; ! ?).
    Les URL et heures (« 18:30 ») ne sont pas touchées : seule une espace déjà présente est remplacée."""
    import re
    t = re.sub(r"(?<=\S) :(?=\s|$)", "\u00a0:", texte)
    t = re.sub(r"(?<=\S) ([;!?])(?=\s|$)", "\u202f\\1", t)
    t = re.sub(r"« ", "«\u00a0", t)
    return re.sub(r" »", "\u00a0»", t)


def lieu_txt(f):
    ref = f.get("ville_reference") or f.get("ville")
    return f"{f['ville']}" + (f" · près de {ref}" if ref and ref != f["ville"] else "")


def nom_court(f):
    return f["nom"].split(" - ")[0]


def fabriquer(c, folder, catalogue, strat, session=None):
    """Médias d'une case. Renvoie (medias, notes)."""
    case, notes = c["case"], []
    offres = [f for f in case.get("offres") or [] if f]
    phares = strat["equipements_phares"]
    if case["moteur"] == "lieu":
        f = offres[0]
        choix = c.get("reel_photos")
        if choix and len(choix) != len(c["reel_lignes"]):
            raise RuntimeError("reel_photos : une photo par ligne")
        urls = catalogue.images(f["handle"], n=max(choix) if choix else len(c["reel_lignes"]))
        if choix:
            if max(choix) > len(urls) or min(choix) < 1:
                raise RuntimeError(f"reel_photos : rang hors des {len(urls)} photos de la boutique")
            urls = [urls[i - 1] for i in choix]
        else:
            notes.append("photos prises dans l'ordre de la boutique, sans choix par ligne (reel_photos absent)")
        photos = [visuels.fetch(u, session) for u in urls]
        if len(photos) < 3:
            raise RuntimeError(f"{f['handle']} : moins de 3 photos")
        lines = (c["reel_lignes"] + [""] * len(photos))[: len(photos)]
        frames = [visuels.reel_frame(p, l, first=(i == 0)) for i, (p, l) in enumerate(zip(photos, lines))]
        out = visuels.render_reel(frames, os.path.join(folder, "reel.mp4"))
        info = visuels.probe(out)
        v = next(s for s in info["streams"] if s["codec_type"] == "video")
        if (v["width"], v["height"]) != visuels.REEL:
            raise RuntimeError(f"format vidéo inattendu {v['width']}x{v['height']}")
        notes.append(f"durée {float(info['format']['duration']):.1f} s")
        return [out], notes
    if case["moteur"] in ("selection", "concours"):
        n = len(offres)
        # couverture : photo choisie (« couverture.photo », rang dans la boutique) ou, à défaut, la 2e photo de la
        # première offre, pour ne pas répéter la diapositive 2
        rang = c["couverture"].get("photo", 2)
        urls = catalogue.images(offres[0]["handle"], rang)
        if len(urls) < rang:
            raise RuntimeError(f"couverture.photo : rang {rang} hors des {len(urls)} photos de la boutique")
        first = visuels.fetch(urls[rang - 1], session)
        slides = [visuels.slide_cover(first, c["couverture"]["titre"], c["couverture"]["sous_titre"], f"1/{n + 2}")]
        for i, f in enumerate(offres, 2):
            photo = visuels.fetch(catalogue.images(f["handle"], 1)[0], session)
            slides.append(visuels.slide_lodging(photo, nom_court(f), lieu_txt(f), f["prix_a_partir_de"],
                                                visuels.order_equipements(f["equipements"], phares), f"{i}/{n + 2}"))
        slides.append(visuels.slide_text(c["fin"]["titre"], c["fin"]["texte"], f"{n + 2}/{n + 2}", cta=True))
        return visuels.save_slides(slides, folder, "diapo"), notes
    if case["moteur"] == "couple":
        cp = c["couple"]
        total = len(cp["diapos"]) + 2
        slides = [visuels.slide_text(cp["titre"], "", f"1/{total}")]
        slides += [visuels.slide_text(d["titre"], d["texte"], f"{i}/{total}") for i, d in enumerate(cp["diapos"], 2)]
        slides.append(visuels.slide_text(cp["cta"], "", f"{total}/{total}", cta=True))
        return visuels.save_slides(slides, folder, "diapo"), notes
    raise ValueError(f"moteur inconnu : {case['moteur']}")


def produce(folder, marque=None, catalogue=None, session=None, history=None):
    marque = marque or charger()
    visuels.appliquer_kit(marque)
    with open(os.path.join(folder, "contenu.json"), encoding="utf-8") as fh:
        c = json.load(fh)
    case = c["case"]
    strat = marque.strategie(case.get("plateforme", "instagram"))
    medias, notes = fabriquer(c, folder, catalogue or Catalogue(marque), strat, session)
    if len(medias) > MAX_DIAPOS:
        raise RuntimeError(f"{len(medias)} diapositives : {MAX_DIAPOS} au maximum")
    if case.get("lien") and case["lien"].split("?")[0] not in c["legende"] and case["moteur"] != "lieu":
        notes.append("lien UTM à mettre en bio ou en message (non présent dans la légende)")
    paquet = {"case": case, "legende": typo_fr(c["legende"]), "medias": medias, "notes": notes}
    valider(paquet, "paquet")
    verdict = valider(controle.verdict(paquet, marque.regles, history or [], strat["ambiances_autorisees"]), "verdict")
    for nom, obj in (("paquet.json", paquet), ("verdict.json", verdict)):
        with open(os.path.join(folder, nom), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=1)
    return paquet, verdict


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier")
    ap.add_argument("--marque")
    a = ap.parse_args(argv)
    paquet, v = produce(a.dossier, charger(a.marque))
    print(f"{v['statut']} · {len(paquet['medias'])} média(s) · " + "; ".join(v["bloquants"] + paquet["notes"]))
    return 0 if v["statut"] == "PRET" else 2


if __name__ == "__main__":
    sys.exit(main())
