#!/usr/bin/env python3
"""
Produit une publication à partir d'une case du plan et des textes rédigés par l'agent.

Entrée : data/production/<date>-<moteur>/contenu.json
  {
    "case": { ... case du plan (date, moteur, format, logements, lien) ... },
    "legende": "texte complet de la légende",
    "reel_lignes": ["accroche à l'écran", "ligne 2", ...],          # moteur lieu
    "couverture": {"titre": "...", "sous_titre": "..."},             # sélection / concours
    "couple": {"titre": "...", "diapos": [{"titre": "...", "texte": "..."}], "cta": "..."},
    "fin": {"titre": "...", "texte": "..."}                          # dernière diapositive (sélection / concours)
  }
Sortie : médias dans le même dossier + pret.json (statut PRET seulement si le contrôle des légendes passe
sans bloquant et que les médias sont valides).
"""
import argparse
import json
import os
import sys

import controle
import logements
import visuels

HERE = os.path.dirname(os.path.abspath(__file__))


def lieu_txt(f):
    ref = f.get("ville_reference") or f.get("ville")
    return f"{f['ville']}" + (f" · près de {ref}" if ref and ref != f["ville"] else "")


def produce(folder, shop=None, session=None, history=None):
    with open(os.path.join(folder, "contenu.json"), encoding="utf-8") as fh:
        c = json.load(fh)
    case, shop = c["case"], shop or logements.Shop()
    with open(os.path.join(HERE, "strategie.json"), encoding="utf-8") as fh:
        phares = json.load(fh)["equipements_phares"]
    medias, notes = [], []
    lodgings = [f for f in case.get("logements") or [] if f]

    if case["moteur"] == "lieu":
        f = lodgings[0]
        photos = [visuels.fetch(u, session) for u in visuels.image_urls(shop, f["handle"], n=len(c["reel_lignes"]))]
        if len(photos) < 3:
            raise RuntimeError(f"{f['handle']} : moins de 3 photos")
        lines = (c["reel_lignes"] + [""] * len(photos))[: len(photos)]
        frames = [visuels.reel_frame(p, l, first=(i == 0)) for i, (p, l) in enumerate(zip(photos, lines))]
        out = visuels.render_reel(frames, os.path.join(folder, "reel.mp4"))
        info = visuels.probe(out)
        v = next(s for s in info["streams"] if s["codec_type"] == "video")
        if (v["width"], v["height"]) != visuels.REEL:
            raise RuntimeError(f"format vidéo inattendu {v['width']}x{v['height']}")
        medias = [out]
        notes.append(f"durée {float(info['format']['duration']):.1f} s")
        fiche = f
    elif case["moteur"] in ("selection", "concours"):
        n = len(lodgings)
        # couverture : 2e photo du premier logement, pour ne pas répéter la diapositive 2
        cover_urls = visuels.image_urls(shop, lodgings[0]["handle"], 2)
        first = visuels.fetch(cover_urls[-1], session)
        slides = [visuels.slide_cover(first, c["couverture"]["titre"], c["couverture"]["sous_titre"], f"1/{n + 2}")]
        for i, f in enumerate(lodgings, 2):
            urls = visuels.image_urls(shop, f["handle"], 1)
            slides.append(visuels.slide_lodging(visuels.fetch(urls[0], session), f["nom"].split(" - ")[0], lieu_txt(f),
                                                f["prix_a_partir_de"],
                                                visuels.order_equipements(f["equipements"], phares), f"{i}/{n + 2}"))
        slides.append(visuels.slide_text(c["fin"]["titre"], c["fin"]["texte"], f"{n + 2}/{n + 2}", cta=True))
        medias = visuels.save_slides(slides, folder, "diapo")
        fiche = lodgings
    elif case["moteur"] == "couple":
        cp = c["couple"]
        total = len(cp["diapos"]) + 2
        slides = [visuels.slide_text(cp["titre"], "", f"1/{total}")]
        slides += [visuels.slide_text(d["titre"], d["texte"], f"{i}/{total}") for i, d in enumerate(cp["diapos"], 2)]
        slides.append(visuels.slide_text(cp["cta"], "", f"{total}/{total}", cta=True))
        medias = visuels.save_slides(slides, folder, "diapo")
        fiche = None
    else:
        raise ValueError(f"moteur inconnu : {case['moteur']}")

    if len(medias) > 10:
        raise RuntimeError(f"{len(medias)} diapositives : Instagram en accepte 10 au maximum")
    # Le contrôle exige un logement nommé sauf pour le moteur couple (pas de logement par construction)
    check = controle.check(c["legende"], fiche, history or [])
    blocking = [r for r in check["resultats"] if r["niveau"] == "bloquant"
                and not (case["moteur"] == "couple" and r["code"] == "LOGEMENT")]
    if case.get("lien") and case["lien"].split("?")[0] not in c["legende"] and case["moteur"] != "lieu":
        notes.append("lien UTM à mettre en bio ou en message (non présent dans la légende)")
    pret = {"case": case, "medias": medias, "legende": c["legende"], "controle": check, "notes": notes,
            "statut": "PRET" if not blocking else "REFUSE",
            "bloquants": [r["message"] for r in blocking]}
    with open(os.path.join(folder, "pret.json"), "w", encoding="utf-8") as fh:
        json.dump(pret, fh, ensure_ascii=False, indent=1)
    return pret


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier")
    a = ap.parse_args(argv)
    p = produce(a.dossier)
    print(f"{p['statut']} · {len(p['medias'])} média(s) · " + "; ".join(p["bloquants"] + p["notes"]))
    return 0 if p["statut"] == "PRET" else 2


if __name__ == "__main__":
    sys.exit(main())
