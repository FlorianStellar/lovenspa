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
    "reel_plans": [{"photo": 3, "texte": "≤ 6 mots" | null, "duree": 1.2, "cadrage": "auto"}, ...],
                                                                    # moteur lieu, rendu plein cadre (remplace les deux
                                                                    # champs précédents) ; cadrage : auto, entier, haut…
    "musique": "<id>",                                              # option : morceau de marques/<id>/musique/ 
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


def textes_ecran(c):
    """Tout texte affiché dans les médias (contrôlé par S6 comme la légende)."""
    out = [p.get("texte") for p in c.get("reel_plans") or []] + list(c.get("reel_lignes") or [])
    for k in ("couverture", "fin"):
        out += [v for kk, v in (c.get(k) or {}).items() if kk != "photo"]
    cp = c.get("couple") or {}
    out += [cp.get("titre"), cp.get("sous_titre"), cp.get("cta"), cp.get("question")]
    out += [x for d in cp.get("diapos") or [] for x in (d.get("titre"), d.get("texte"))]
    out += [e.get("texte") for e in c.get("photos_supplementaires") or []]
    out += [im.get("texte") for im in (c.get("story") or {}).get("images") or []]
    rc = c.get("recrutement") or {}
    out += [(rc.get("couverture") or {}).get(k) for k in ("titre", "sous_titre")] + [rc.get("cta"), rc.get("texte_cta")]
    out += [x for d in rc.get("diapos") or [] for x in (d.get("titre"), d.get("texte"))]
    return [x for x in out if isinstance(x, str) and x.strip()]


def nom_court(f):
    return f["nom"].split(" - ")[0]


DUREE_REEL_MIN = 15  # s (S5-19, skill social-production)
MOTS_STORY_MAX = 12  # une idée par image (S5-31), lisible en 2 s : règle maison, à mesurer (S8)


def musiques(marque):
    chemin = os.path.join(marque.dossier, "musique", "licences.json")
    if not os.path.exists(chemin):
        return []
    with open(chemin, encoding="utf-8") as fh:
        return json.load(fh)


def choisir_musique(c, marque):
    """Morceau demandé (« musique ») ou, sinon, choisi de façon stable par la date de la case.
    Aucune musique disponible : erreur (un Reel ne part jamais muet, IG-R33 et revue J4)."""
    lib = musiques(marque)
    if not lib:
        raise RuntimeError("aucune musique sous licence dans marques/<id>/musique/licences.json")
    if c.get("musique"):
        m = next((x for x in lib if x["id"] == c["musique"]), None)
        if not m:
            raise RuntimeError(f"musique inconnue : {c['musique']}")
    else:
        libres = [x for x in lib if not x.get("attribution")] or lib  # sans crédit à afficher d'abord
        m = libres[sum(map(ord, c["case"]["date"])) % len(libres)]
    return m, os.path.join(marque.dossier, "musique", m["fichier"])


def verifier_plans(plans):
    """Règles F01 et S5-19 : plans de 0,5 à 1,5 s, 6 mots au plus par carton, accroche au premier plan, 15 s au moins."""
    err = []
    for i, p in enumerate(plans, 1):
        if not visuels.PLAN_MIN <= p["duree"] <= visuels.PLAN_MAX:
            err.append(f"plan {i} : {p['duree']} s hors de {visuels.PLAN_MIN} à {visuels.PLAN_MAX} s")
        if p.get("texte") and len(p["texte"].split()) > visuels.MOTS_CARTON_MAX:
            err.append(f"plan {i} : {len(p['texte'].split())} mots (6 au plus) : « {p['texte']} »")
    if not plans or not plans[0].get("texte"):
        err.append("plan 1 : accroche à l'écran manquante")
    total = sum(p["duree"] for p in plans)
    if total < DUREE_REEL_MIN:
        err.append(f"durée {total:.1f} s, {DUREE_REEL_MIN} s au moins")
    return err


def fabriquer(c, folder, catalogue, strat, session=None, marque=None):
    """Médias d'une case. Renvoie (medias, notes)."""
    case, notes = c["case"], []
    offres = [f for f in case.get("offres") or [] if f]
    phares = strat["equipements_phares"]
    if case["moteur"] == "lieu" and c.get("reel_plans"):
        f, plans = offres[0], c["reel_plans"]
        err = verifier_plans(plans)
        if err:
            raise RuntimeError("Reel refusé : " + " ; ".join(err))
        urls = catalogue.images(f["handle"], n=max(p["photo"] for p in plans))
        if max(p["photo"] for p in plans) > len(urls):
            raise RuntimeError(f"reel_plans : rang hors des {len(urls)} photos de la boutique")
        cache = {}
        for p in plans:
            if p["photo"] not in cache:
                cache[p["photo"]] = visuels.fetch(urls[p["photo"] - 1], session)
        m, chemin = choisir_musique(c, marque)
        out = visuels.render_reel_plans(
            [{"image": cache[p["photo"]], "texte": p.get("texte"), "duree": p["duree"],
              "cadrage": p.get("cadrage", "auto"), "haut": i == 0 or p.get("position") == "haut"}
             for i, p in enumerate(plans)],
            os.path.join(folder, "reel.mp4"), musique=chemin)
        info = visuels.probe(out)
        v = next(s for s in info["streams"] if s["codec_type"] == "video")
        if (v["width"], v["height"]) != visuels.REEL:
            raise RuntimeError(f"format vidéo inattendu {v['width']}x{v['height']}")
        notes.append(f"durée {float(info['format']['duration']):.1f} s · {len(plans)} plans · musique {m['id']} ({m['licence']})")
        if m.get("attribution"):
            notes.append("attribution musicale : " + m["attribution"])
        return [out], notes
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
        if case["moteur"] == "selection":
            offres = sorted(offres, key=lambda o: o["prix_a_partir_de"])  # classées par prix (revue J4, F03)
        extra = c.get("photos_supplementaires") or []  # [{"photo": rang, "texte": "..."}] (concours : montrer le lot)
        n = len(offres) + len(extra)
        # couverture : photo choisie (« couverture.photo », rang dans la boutique) ou, à défaut, la 2e photo de la
        # première offre, pour ne pas répéter la diapositive 2
        rang = c["couverture"].get("photo", 2)
        # photo de couverture : logement choisi (« couverture.handle »), sinon le favori, sinon le premier
        h_couv = c["couverture"].get("handle") or c.get("favori") or offres[0]["handle"]
        urls = catalogue.images(h_couv, rang)
        if len(urls) < rang:
            raise RuntimeError(f"couverture.photo : rang {rang} hors des {len(urls)} photos de la boutique")
        first = visuels.fetch(urls[rang - 1], session)
        slides = [visuels.slide_cover(first, c["couverture"]["titre"], c["couverture"]["sous_titre"], f"1/{n + 2}")]
        for i, f in enumerate(offres, 2):
            rang = (c.get("photos_logements") or {}).get(f["handle"], 1)
            photo = visuels.fetch(catalogue.images(f["handle"], rang)[rang - 1], session)
            slides.append(visuels.slide_lodging(photo, (c.get("noms_courts") or {}).get(f["handle"], nom_court(f)),
                                                lieu_txt(f), f["prix_a_partir_de"],
                                                visuels.order_equipements(f["equipements"], phares), f"{i}/{n + 2}",
                                                badge="Notre favori" if f["handle"] == c.get("favori") else None))
        if extra:
            urls = catalogue.images(offres[0]["handle"], max(e["photo"] for e in extra))
            for j, e in enumerate(extra, len(offres) + 2):
                slides.append(visuels.slide_photo(visuels.fetch(urls[e["photo"] - 1], session), e.get("texte"),
                                                  f"{j}/{n + 2}"))
        fin = c["fin"]
        slides.append(visuels.slide_grand_texte(fin["titre"], fin["texte"], f"{n + 2}/{n + 2}", cta=fin["bouton"])
                      if fin.get("bouton") else visuels.slide_text(fin["titre"], fin["texte"], f"{n + 2}/{n + 2}", cta=True))
        return visuels.save_slides(slides, folder, "diapo"), notes
    if case["moteur"] == "story":
        imgs = c["story"]["images"]
        if not 1 <= len(imgs) <= 7:
            raise RuntimeError("story : 1 à 7 images (S5-30)")
        for i, im in enumerate(imgs, 1):
            if im.get("texte") and len(im["texte"].split()) > MOTS_STORY_MAX:
                raise RuntimeError(f"story image {i} : {len(im['texte'].split())} mots ({MOTS_STORY_MAX} au plus)")
        rendus = []
        for i, im in enumerate(imgs):
            if im.get("repartage"):
                # contenu d'un client ou d'un hébergeur : accord écrit obligatoire (doc de stratégie, S9), crédit affiché
                rp = im["repartage"]
                if not rp.get("accord_le") or not rp.get("auteur"):
                    raise RuntimeError(f"story image {i + 1} : repartage sans accord daté de l'auteur")
                photo = visuels.fetch(rp["url"], session)
                texte = ((im.get("texte") or "") + f" · Merci {rp['auteur']}").strip(" ·")
                rendus.append(visuels.story_image(photo, texte, haut=i == 0, cadrage=im.get("cadrage", "auto")))
                notes.append(f"repartage de {rp['auteur']} (accord du {rp['accord_le']}) : identifier le compte à la publication")
                continue
            h = im.get("handle") or offres[0]["handle"]
            url = catalogue.images(h, im["photo"])[im["photo"] - 1]
            rendus.append(visuels.story_image(visuels.fetch(url, session), im.get("texte"), haut=i == 0,
                                              cadrage=im.get("cadrage", "auto")))
        return visuels.save_stories(rendus, folder), notes
    if case["moteur"] == "recrutement":
        rc = c["recrutement"]
        total = len(rc["diapos"]) + 2
        couv = rc["couverture"]
        h = couv.get("handle") or offres[0]["handle"]
        photo = visuels.fetch(catalogue.images(h, couv.get("photo", 1))[couv.get("photo", 1) - 1], session)
        slides = [visuels.slide_cover(photo, couv["titre"], couv["sous_titre"], f"1/{total}")]
        slides += [visuels.slide_grand_texte(d["titre"], d["texte"], f"{i}/{total}") for i, d in enumerate(rc["diapos"], 2)]
        slides.append(visuels.slide_grand_texte(rc["cta"], rc.get("texte_cta", ""), f"{total}/{total}",
                                                cta=rc.get("bouton", "Lien en bio")))
        return visuels.save_slides(slides, folder, "diapo"), notes
    if case["moteur"] == "couple":
        cp = c["couple"]
        fin = offres[0] if offres else None  # logement en dernière diapositive (revue J4) : piste de réservation
        total = len(cp["diapos"]) + 2 + (1 if fin else 0)
        slides = [visuels.slide_grand_texte(cp["titre"], cp.get("sous_titre", ""), f"1/{total}")]
        slides += [visuels.slide_grand_texte(d["titre"], d["texte"], f"{i}/{total}") for i, d in enumerate(cp["diapos"], 2)]
        slides.append(visuels.slide_grand_texte(cp["cta"], cp.get("question", ""), f"{len(cp['diapos']) + 2}/{total}"))
        if fin:
            rang = cp.get("photo_logement", 1)
            photo = visuels.fetch(catalogue.images(fin["handle"], rang)[rang - 1], session)
            slides.append(visuels.slide_lodging(photo, (c.get("noms_courts") or {}).get(fin["handle"], nom_court(fin)),
                                                lieu_txt(fin), fin["prix_a_partir_de"],
                                                visuels.order_equipements(fin["equipements"], phares),
                                                f"{total}/{total}", badge=cp.get("badge_logement"),
                                                mention=cp.get("mention_logement")))
        return visuels.save_slides(slides, folder, "diapo"), notes
    raise ValueError(f"moteur inconnu : {case['moteur']}")


def reverdict(folder, marque=None, history=None):
    """Nouveau verdict sans nouveau rendu (après la revue visuelle) : médias et notes du paquet existant,
    textes et revue relus dans contenu.json. Refuse si le contenu a changé depuis le rendu."""
    marque = marque or charger()
    with open(os.path.join(folder, "contenu.json"), encoding="utf-8") as fh:
        c = json.load(fh)
    with open(os.path.join(folder, "paquet.json"), encoding="utf-8") as fh:
        paquet = json.load(fh)
    if paquet.get("empreinte_contenu") != controle.empreinte(c):
        raise RuntimeError("le contenu a changé depuis le rendu : relancer la production")
    paquet["revue_visuelle"] = c.get("revue_visuelle")
    paquet["sources_montants"] = c.get("sources_montants") or {}
    strat = marque.strategie(paquet["case"].get("plateforme", "instagram"))
    verdict = valider(controle.verdict(paquet, marque.regles, history or [], strat["ambiances_autorisees"]), "verdict")
    for nom, obj in (("paquet.json", paquet), ("verdict.json", verdict)):
        with open(os.path.join(folder, nom), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=1)
    return paquet, verdict


def produce(folder, marque=None, catalogue=None, session=None, history=None):
    marque = marque or charger()
    visuels.appliquer_kit(marque)
    with open(os.path.join(folder, "contenu.json"), encoding="utf-8") as fh:
        c = json.load(fh)
    case = c["case"]
    strat = marque.strategie(case.get("plateforme", "instagram"))
    medias, notes = fabriquer(c, folder, catalogue or Catalogue(marque), strat, session, marque)
    if len(medias) > MAX_DIAPOS:
        raise RuntimeError(f"{len(medias)} diapositives : {MAX_DIAPOS} au maximum")
    if case["format"] != "STORY" and case.get("lien") and case["lien"].split("?")[0] not in c["legende"] \
            and case["moteur"] != "lieu":
        notes.append("lien UTM à mettre en bio ou en message (non présent dans la légende)")
    legende = c["legende"]
    attribution = next((n.split(" : ", 1)[1] for n in notes if n.startswith("attribution musicale")), None)
    if attribution and attribution not in legende:
        legende += "\n\n" + attribution  # licence CC BY : crédit dans la publication
    paquet = {"case": case, "legende": typo_fr(legende), "medias": medias, "notes": notes,
              "textes_ecran": textes_ecran(c), "empreinte_contenu": controle.empreinte(c),
              # montant cité hors prix de logement, avec sa source publique (ex. {"30": "<url de la page>"})
              "sources_montants": c.get("sources_montants") or {},
              # revue visuelle (texte cohérent avec chaque photo, aucun logo tiers, aucun équipement exclu visible) :
              # faite après le rendu, inscrite dans contenu.json avec l'empreinte du contenu revu
              "revue_visuelle": c.get("revue_visuelle")}
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
    ap.add_argument("--verdict-seul", action="store_true", help="nouveau verdict après la revue visuelle, sans rendu")
    a = ap.parse_args(argv)
    paquet, v = (reverdict if a.verdict_seul else produce)(a.dossier, charger(a.marque))
    print(f"{v['statut']} · {len(paquet['medias'])} média(s) · " + "; ".join(v["bloquants"] + paquet["notes"]))
    return 0 if v["statut"] == "PRET" else 2


if __name__ == "__main__":
    sys.exit(main())
