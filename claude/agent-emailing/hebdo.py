"""Campagne hebdomadaire « Ce week-end, encore libre » construite depuis runs/dispos_<date>.json."""
import json, datetime
from emails import FN, LASTMIN
JOURS = {4: "vendredi", 5: "samedi"}

def libelle_nuits(libres):
    js = [JOURS[datetime.date.fromisoformat(d).weekday()] + " " + str(datetime.date.fromisoformat(d).day) for d in sorted(libres)]
    return "Libre " + " et ".join(js)

def prix_min(libres):
    """Prix exact payé par le voyageur (price_cents), jamais arrondi vers le bas."""
    return f"{min(libres.values()) / 100:.2f}".replace(".", ",").removesuffix(",00")

def construire(releve_path, releve_txt=None):
    d = json.load(open(releve_path))
    if releve_txt is None:
        import zoneinfo
        t = datetime.datetime.fromisoformat(d["releve"]).astimezone(zoneinfo.ZoneInfo("Europe/Paris"))
        jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        releve_txt = f"{jours[t.weekday()]} {t.day} novembre à {t.hour} h {t.minute:02d}"
    ch = d["choix"]
    rooms = [{"titre": c["titre"], "ville": c["ville"].strip(), "image": (c["image"] or "") + ("&" if "?" in (c["image"] or "") else "?") + "width=480",
              "url": f"https://lovenspa.fr/products/{c['handle']}", "nuits": libelle_nuits(c["libres"]), "prix": prix_min(c["libres"])} for c in ch]
    j1, j2 = [datetime.date.fromisoformat(x) for x in d["dates"]]
    return dict(id=f"hebdo-{d['dates'][0]}", flow="Ce week-end, encore libre", camp=f"weekend-{d['dates'][0]}", kicker="Ce week-end",
        objets=[f"Ce week-end, encore libre : {len(rooms)} love rooms", f"Vendredi ou samedi : {len(rooms)} love rooms avec une nuit libre", f"{rooms[0]['titre']}, {rooms[1]['titre']} et {len(rooms)-2} autres ce week-end"],
        preheader=f"{rooms[0]['titre']} à {rooms[0]['ville']}, {rooms[1]['titre']} à {rooms[1]['ville']} et {len(rooms)-2} autres, libres ce week-end.",
        titre="Ce week-end, encore libre",
        corps=[f"Bonjour{FN},",
               f"Ce vendredi {j1.day} ou ce samedi {j2.day} novembre, ces {len(rooms)} love rooms ont encore une nuit libre. Chacune a son spa, son jacuzzi, son sauna ou sa piscine privatif, jamais partagé, et se réserve en 2 clics sur Love'nSpa."],
        rooms=rooms, cta=("Voir toutes les dispos", LASTMIN),
        ps=f"Disponibilités et prix relevés le {releve_txt}. Une nuit peut être réservée par un autre couple d'ici votre visite.")
