"""E2E : la meta description servie en live = celle du lot, pour chaque fiche."""
import csv, html, re, sys, time, urllib.request, urllib.error, os
D = os.path.dirname(os.path.abspath(__file__))
COL = "Metafield: description_tag [string]"
def meta(h):
    m = re.search(r'<meta name="description" content="([^"]*)"', h)
    return html.unescape(m.group(1)) if m else None
def get(u):
    for i in range(6):
        try:
            return urllib.request.urlopen(urllib.request.Request(u + "?nocache=" + str(time.time()), headers={"User-Agent": "lovenspa-seo-check"}), timeout=30).read().decode()
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(10 * (i + 1))
def main():
    rows = list(csv.DictReader(open(os.path.join(D, "metas_lot.csv"), encoding="utf-8")))
    ko = 0
    for r in rows:
        m = meta(get("https://lovenspa.fr/products/" + r["Handle"]))
        ok = m == r[COL]; ko += not ok
        print("OK" if ok else "KO", r["Handle"], "" if ok else f"-> {m}")
    return ko
if __name__ == "__main__":
    sys.exit(1 if main() else 0)
