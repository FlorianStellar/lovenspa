"""Vérifie en live que chaque URL de redirections.tsv répond 301 vers sa cible, et que la cible répond 200."""
import csv, sys, time, urllib.parse, urllib.request, urllib.error

BASE = "https://lovenspa.fr"

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None

def charger(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def encoder(p):
    return urllib.parse.quote(p, safe="/-_.~%")

def normaliser_location(loc):
    """Ramène une Location absolue ou relative à un chemin décodé."""
    p = urllib.parse.urlsplit(loc).path
    return urllib.parse.unquote(p)

def evaluer(row, statut_src, location, statut_cible):
    erreurs = []
    if statut_src != 301:
        erreurs.append(f"source {statut_src} (attendu 301)")
    elif normaliser_location(location or "") != row["target"]:
        erreurs.append(f"cible {location} (attendu {row['target']})")
    if statut_cible != 200:
        erreurs.append(f"cible répond {statut_cible} (chaîne ou cible morte)")
    return erreurs

def statut(url, suivre):
    opener = urllib.request.build_opener() if suivre else urllib.request.build_opener(NoRedirect)
    for essai in range(5):
        try:
            r = opener.open(urllib.request.Request(url, method="GET", headers={"User-Agent": "lovenspa-seo-check"}), timeout=30)
            return r.status, r.headers.get("Location")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After") or 5) * (essai + 1)); continue
            return e.code, e.headers.get("Location")
    return 429, None

def main(path):
    ko = 0
    for row in charger(path):
        s, loc = statut(BASE + encoder(row["path"]), False)
        c, _ = statut(BASE + encoder(row["target"]), False)  # sans suivre : une cible en 301 = chaîne = KO
        err = evaluer(row, s, loc, c)
        ko += bool(err)
        print(("KO " if err else "OK ") + row["path"], "; ".join(err))
        time.sleep(1)
    return ko

if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1] if len(sys.argv) > 1 else "redirections.tsv") else 0)
