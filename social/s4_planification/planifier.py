#!/usr/bin/env python3
"""
S4 Planification : plan de la semaine pour une marque et une plateforme, déduit de la stratégie validée
(marques/<marque>/strategie_<plateforme>.json) et du catalogue (S3).

5 cases : 3 Reels « le lieu », 1 carrousel « sélection » (ou concours), 1 carrousel couple.
Choix déterministes et explicables :
  - région de chaque Reel : poids de strategie.json divisé par (1 + passages récents) ;
  - logement : actif, prix connu, au moins 3 médias, un équipement phare, pas publié depuis 56 jours ;
  - sélection : thème suivant dans la liste, 6 logements qui passent le filtre ;
  - concours : si une date de concours tombe dans la semaine et qu'un hébergeur a donné son accord
    (donnees/<marque>/<plateforme>/partenaires.json), sinon la case reste une sélection et le plan le signale.
Sortie : contrat Plan (cases conformes à contrats/case.schema.json).

Usage :
  python3 -m social.s4_planification.planifier [--marque <id>] [--plateforme instagram] [--semaine 2026-11-16]
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import date, datetime, timedelta

from social.contrats.valider import valider
from social.marque import charger
from social.s3_catalogue.offres import Catalogue


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def monday(d):
    return d - timedelta(days=d.weekday())


def week_index(d):
    return monday(d).toordinal() // 7


def stable(*parts):
    """Entier déterministe pour départager sans hasard non reproductible."""
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def temps_fort(d, strat):
    md = d.strftime("%m-%d")
    for t in strat["temps_forts"]:
        a, b = t["debut"], t["fin"]
        if (a <= md <= b) if a <= b else (md >= a or md <= b):
            return t
    return None


def concours_dates(strat, year):
    out = []
    for t in strat["temps_forts"]:
        c = t.get("concours")
        for md in ([c] if isinstance(c, str) else (c or [])):
            for y in (year - 1, year, year + 1):
                out.append(date.fromisoformat(f"{y}-{md}"))
    return out


def eligible(f, strat, recent):
    # Un logement équipé de matériel non citable (BDSM…) est écarté : ses photos pourraient le montrer.
    return (f["actif"] and f["prix_a_partir_de"] is not None and f["medias"] >= 3 and f["region"]
            and (f.get("ville") or f.get("ville_reference"))
            and f.get("ambiance") in strat["ambiances_autorisees"]
            and not f["equipements_non_citables"] and f["handle"] not in recent
            and any(e in strat["equipements_phares"] for e in f["equipements"]))


def score(f, strat, seed):
    phares = sum(1 for e in f["equipements"] if e in strat["equipements_phares"])
    return (phares, stable(seed, f["handle"]))


def recent_handles(history, d, days):
    limit = (d - timedelta(days=days)).isoformat()
    return {h["handle"] for h in history if h.get("handle") and h["date"] >= limit}


def pick_region(strat, used_regions, available):
    best = None
    for r, w in strat["regions_poids"].items():
        if r not in available:
            continue
        val = (w / (1 + used_regions.count(r)), -sorted(strat["regions_poids"]).index(r))
        if best is None or val > best[0]:
            best = (val, r)
    return best[1] if best else None


def match_selection(f, filtre, region):
    if filtre.get("region") and f["region"] != region:
        return False
    if filtre.get("prix_max") and (f["prix_a_partir_de"] or 1e9) > filtre["prix_max"]:
        return False
    if filtre.get("equipement") and filtre["equipement"] not in f["equipements"]:
        return False
    if filtre.get("type") and f.get("type") != filtre["type"]:
        return False
    return True


def utm(strat, url, moteur, d):
    sep = "&" if "?" in url else "?"
    return url + sep + strat["utm"].format(moteur=moteur, date=d.isoformat())


def plan_week(start, catalogue, history, strat, partenaires=None, site=""):
    """Plan pur (testable) : renvoie le dict du plan."""
    start = monday(start)
    wk = week_index(start)
    recent = recent_handles(history, start, strat["rotation_logement_jours"])
    used_regions = [h.get("region") for h in history if h.get("region") and h["date"] >= (start - timedelta(weeks=8)).isoformat()]
    taken = set()
    pool = [f for f in catalogue if eligible(f, strat, recent)]
    regions_avail = {f["region"] for f in pool}
    week_conc = [c for c in concours_dates(strat, start.year) if start <= c <= start + timedelta(days=6)]
    volontaires = [p for p in (partenaires or []) if p.get("accord_concours") and p.get("nuits_offertes", 0) > 0]
    slots, alerts = [], []

    for s in strat["semaine"]:
        d = start + timedelta(days=s["jour"])
        tf = temps_fort(d, strat)
        slot = {"date": d.isoformat(), "heure": strat["heure_publication"], "plateforme": strat["plateforme"],
                "moteur": s["moteur"], "format": s["format"],
                "temps_fort": tf["theme"] if tf else None, "statut": "A_PRODUIRE"}
        if s["moteur"] == "lieu":
            region = pick_region(strat, used_regions, {f["region"] for f in pool if f["handle"] not in taken})
            cands = sorted([f for f in pool if f["region"] == region and f["handle"] not in taken],
                           key=lambda f: score(f, strat, wk), reverse=True)
            if not cands:
                slot["statut"] = "BLOQUE"
                alerts.append(f"{d}: aucun logement éligible")
            else:
                f = cands[0]
                taken.add(f["handle"])
                used_regions.append(region)
                slot.update(offres=[f], region=region, lien=utm(strat, f["url"], "lieu", d))
        elif s["moteur"] == "selection" and week_conc:
            if volontaires:
                p = volontaires[stable(wk) % len(volontaires)]
                f = next((x for x in catalogue if x["handle"] == p["handle"]), None)
                slot.update(moteur="concours", offres=[f] if f else [], partenaire=p,
                            lien=utm(strat, f["url"], "concours", d) if f else None)
                if not f:
                    slot["statut"] = "BLOQUE"
                    alerts.append(f"{d}: offre du partenaire {p['handle']} introuvable")
                elif not eligible(f, strat, set()):
                    # mêmes critères que les autres cases (ambiance, équipements, photos, prix), sans la rotation
                    slot["statut"] = "BLOQUE"
                    alerts.append(f"{d}: offre du partenaire {p['handle']} non éligible (ambiance, équipements, photos ou prix)")
            else:
                alerts.append(f"{d}: concours prévu le {week_conc[0]} mais aucun hébergeur volontaire "
                              f"(donnees/<marque>/<plateforme>/partenaires.json) : sélection publiée à la place")
        if slot["moteur"] == "selection":
            themes = strat["selections"]
            for k in range(len(themes)):
                th = themes[(wk + k) % len(themes)]
                region = pick_region(strat, used_regions, regions_avail) if th["filtre"].get("region") else None
                cands = sorted([f for f in pool if f["handle"] not in taken and match_selection(f, th["filtre"], region)],
                               key=lambda f: score(f, strat, wk), reverse=True)
                if len(cands) >= strat["taille_selection"]:
                    chosen = cands[: strat["taille_selection"]]
                    taken.update(f["handle"] for f in chosen)
                    slot.update(theme=th["titre"].format(n=len(chosen), region=region,
                                                         prix=th["filtre"].get("prix_max")),
                                offres=chosen, region=region,
                                lien=utm(strat, site + strat["liens"]["selection"], "selection", d))
                    break
            else:
                slot["statut"] = "BLOQUE"
                alerts.append(f"{d}: aucune sélection de {strat['taille_selection']} logements possible")
        elif slot["moteur"] == "couple":
            slot.update(theme=strat["couple"][wk % len(strat["couple"])], offres=[],
                        lien=utm(strat, site + strat["liens"]["couple"], "couple", d))
        slots.append(slot)
    return {"semaine": start.isoformat(), "plateforme": strat["plateforme"], "genere_le": datetime.now().isoformat(timespec="seconds"),
            "catalogue_eligible": len(pool), "cases": slots, "alertes": alerts}


def to_markdown(plan):
    out = [f"# Plan {plan['plateforme']}, semaine du {plan['semaine']}", "",
           f"{plan['catalogue_eligible']} offres éligibles après rotation.", "",
           "| Date | Moteur | Format | Contenu | Logement(s) | Statut |", "|---|---|---|---|---|---|"]
    for s in plan["cases"]:
        logs = ", ".join(f"{f['nom'].split(' - ')[0]} ({f['ville_reference'] or f['ville']}, dès {f['prix_a_partir_de']:g} €)"
                         for f in s.get("offres") or [] if f)
        contenu = s.get("theme") or (s.get("region") or "")
        out.append(f"| {s['date']} {s['heure']} | {s['moteur']} | {s['format']} | {contenu} | {logs or '-'} | {s['statut']} |")
    if plan["alertes"]:
        out += ["", "Alertes :"] + [f"- {a}" for a in plan["alertes"]]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--semaine", help="lundi de la semaine (défaut : lundi prochain)")
    ap.add_argument("--marque")
    ap.add_argument("--plateforme", default="instagram")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    m = charger(a.marque)
    start = date.fromisoformat(a.semaine) if a.semaine else monday(date.today()) + timedelta(days=7)
    strat = m.strategie(a.plateforme)
    history = load_json(m.donnees(a.plateforme, "publies.json"), [])
    partners = load_json(m.donnees(a.plateforme, "partenaires.json"), [])
    plan = valider(plan_week(start, Catalogue(m).toutes(), history, strat, partners, site=m.site), "plan")
    out = a.out or m.donnees(a.plateforme, "plans", f"plan-{plan['semaine']}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)
    with open(out.replace(".json", ".md"), "w", encoding="utf-8") as f:
        f.write(to_markdown(plan))
    print(to_markdown(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
