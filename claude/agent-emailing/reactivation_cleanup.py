"""Sortie du segment 5 : archive puis suppression. Étapes (boucle mensuelle) :
  1. python3 reactivation_cleanup.py export      -> lot_<date>.json + lot_<date>.sql (INSERT klaviyo_audience_archive)
  2. exécuter le .sql dans Supabase, vérifier : select count(*) from klaviyo_audience_archive where segment_id='X8Wwag' and archived_at::date=current_date
  3. python3 reactivation_cleanup.py suppress lot_<date>.json --archived <n> --confirm   (refusé si n != taille du lot)
Sans --confirm : simulation, rien n'est supprimé."""
import json, sys, datetime
from probe import call
SEG, LABEL = "X8Wwag", "[Pilotage] 5. À supprimer (réactivation sans clic)"
F = "fields%5Bprofile%5D=email,phone_number,first_name,last_name,location,created"

def q(v): return "NULL" if v in (None, "") else "'" + str(v).replace("'", "''") + "'"

def to_row(p):
    a, loc = p["attributes"], p["attributes"].get("location") or {}
    return {"profile_id": p["id"], "email": a.get("email"), "phone": a.get("phone_number"), "first_name": a.get("first_name"),
            "last_name": a.get("last_name"), "country": loc.get("country"), "zip": loc.get("zip"), "profile_created_at": a.get("created")}

def to_sql(rows):
    cols = ["profile_id", "email", "phone", "first_name", "last_name", "country", "zip", "segment_id", "segment_label", "profile_created_at", "archived_at"]
    vals = [f"({', '.join(q(r[c]) for c in cols[:7])}, {q(SEG)}, {q(LABEL)}, {q(r['profile_created_at'])}, now())" for r in rows]
    return "" if not rows else f"insert into klaviyo_audience_archive ({', '.join(cols)}) values\n" + ",\n".join(vals) + ";\n"

def check_suppress(rows, archived, confirm):
    if archived != len(rows): return f"REFUS : archive {archived} != lot {len(rows)}"
    return "OK" if confirm else "SIMULATION"

def export():
    rows, url = [], f"segments/{SEG}/profiles/?{F}&page%5Bsize%5D=100"
    while url:
        st, r = call("GET", url); rows += [to_row(p) for p in r["data"]]
        nxt = r["links"].get("next"); url = nxt.split("/api/", 1)[1] if nxt else None
    d = datetime.date.today().isoformat()
    json.dump(rows, open(f"lot_{d}.json", "w"), ensure_ascii=False); open(f"lot_{d}.sql", "w").write(to_sql(rows))
    print(f"{len(rows)} profils -> lot_{d}.json / lot_{d}.sql")

def suppress(path, archived, confirm):
    rows = [r for r in json.load(open(path)) if r["email"]]
    verdict = check_suppress(rows, archived, confirm); print(verdict, len(rows))
    if verdict != "OK": return
    for i in range(0, len(rows), 100):
        st, r = call("POST", "profile-suppression-bulk-create-jobs/", {"data": {"type": "profile-suppression-bulk-create-job", "attributes": {
            "profiles": {"data": [{"type": "profile", "attributes": {"email": x["email"]}} for x in rows[i:i + 100]]}}}})
        print("lot", i // 100, st)

if __name__ == "__main__":
    if sys.argv[1] == "export": export()
    elif sys.argv[1] == "suppress":
        suppress(sys.argv[2], int(sys.argv[sys.argv.index("--archived") + 1]), "--confirm" in sys.argv)
