"""Love rooms disponibles le vendredi ou le samedi : source = endpoint public booking-availability (celui du widget)."""
import json, re, sys, urllib.request, datetime, html
ENDPOINT = "https://igthraqyjiadzclkkixn.supabase.co/functions/v1/booking-availability"

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "lovenspa-emailing"}), timeout=30) as r:
        return r.read().decode()

def fiche(handle):
    s = get(f"https://lovenspa.fr/products/{handle}")
    m = re.search(r"data-loven-booking-config[^>]*>(.*?)</script>", s, re.S)
    img = re.search(r'<meta property="og:image" content="([^"]+)"', s)
    titre = re.search(r'<meta property="og:title" content="([^"]+)"', s)
    return (json.loads(m.group(1))["widget"] if m else None,
            img.group(1).replace("http://", "https://", 1) if img else None, html.unescape(titre.group(1)) if titre else handle)

def nuits_libres(widget, dates):
    d = json.loads(get(f"{ENDPOINT}?widget={widget}&from={dates[0]}&to={dates[-1]}"))
    out = {n["date"]: n for n in d.get("nights", []) if n.get("available") and n.get("check_in_ok")}
    return {k: out[k]["price_cents"] for k in dates if k in out}, d.get("generated_at"), d.get("stale")

def choisir(candidats, n=6, max_par_ville=2):
    """Ordre = réservations 90 j décroissantes ; au plus 2 love rooms par ville."""
    pris, villes = [], {}
    for c in candidats:
        v = c["ville"].strip().lower()
        if c["libres"] and villes.get(v, 0) < max_par_ville:
            pris.append(c); villes[v] = villes.get(v, 0) + 1
        if len(pris) == n: break
    return pris

if __name__ == "__main__":
    lignes, dates = sys.argv[1].split(";"), sys.argv[2].split(",")
    res = []
    for l in lignes:
        h, n, ville, prix = l.split("|")
        try:
            w, img, titre = fiche(h)
            if not w: continue
            libres, gen, stale = nuits_libres(w, dates)
            res.append({"handle": h, "titre": titre, "ville": ville, "resa_90j": int(n), "image": img, "libres": libres, "generated_at": gen, "stale": stale})
        except Exception as e:
            print("ERR", h, e, file=sys.stderr)
    choix = choisir(res)
    out = {"releve": datetime.datetime.now(datetime.timezone.utc).isoformat(), "dates": dates, "candidats": res, "choix": choix}
    json.dump(out, open(f"runs/dispos_{dates[0]}.json", "w"), ensure_ascii=False, indent=1)
    print(len(res), "candidats,", sum(1 for r in res if r["libres"]), "avec une nuit libre")
    for c in choix: print(c["titre"], "|", c["ville"], "|", c["libres"], "| stale", c["stale"])
