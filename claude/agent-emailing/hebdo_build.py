"""Construit l'email hebdo depuis le relevé, écrit copy/data pour le lint ; avec --push met à jour template + objet de campagne."""
import json, re, sys, os
from hebdo import construire
from render import render
ven, rdir = sys.argv[1], sys.argv[2]
e = construire(f"runs/dispos_{ven}.json")
if len(e["rooms"]) < 6: sys.exit(f"Seulement {len(e['rooms'])} love rooms libres : pas d'email")
h = render(e)
json.dump(e, open(f"runs/hebdo-{ven}.json", "w"), ensure_ascii=False, indent=1); open(f"out/hebdo-{ven}.html", "w").write(h)
if "--push" not in sys.argv:
    os.makedirs(rdir, exist_ok=True)
    corps = [re.sub(r"\{%.*?%\}.*?\{%.*?%\}", " [prénom]", p) for p in e["corps"]]
    L = ["# Ce week-end, encore libre", ""] + [f"objet {l} : {o}" for l, o in zip("ABC", e["objets"])] + [f"preheader : {e['preheader']}", "", e["titre"]] + corps
    L += [f"- {r['titre']}, {r['ville']} : {r['nuits']}, {r['prix']} € la nuit" for r in e["rooms"]] + [f"cta : {e['cta'][0]}", f"P.-S. {e['ps']}"]
    open(f"{rdir}/copy.md", "w").write("\n".join(L) + "\n")
    d = json.load(open(f"runs/dispos_{ven}.json"))
    D = [f"- {c['titre']} ({c['ville'].strip()}) : nuits {list(c['libres'])}, prix {[v/100 for v in c['libres'].values()]} € — booking-availability, relevé {d['releve'][:16]}Z" for c in d["choix"]]
    import datetime, zoneinfo
    t = datetime.datetime.fromisoformat(d["releve"]).astimezone(zoneinfo.ZoneInfo("Europe/Paris"))
    j = [datetime.date.fromisoformat(x) for x in d["dates"]]
    D += [f"- {j[0].day} et {j[1].day} novembre : nuits du vendredi et du samedi relevées", f"- {t.day} novembre, {t.hour} h {t.minute:02d} : date et heure du relevé (Paris)"]
    D += ["- 6 love rooms, nuits du vendredi et du samedi — même relevé", "- 2 clics, jamais partagé — brief lovenspa.fr 2026-10-20", f"- heure du relevé — {d['releve']}"]
    open(f"{rdir}/data.md", "w").write("\n".join(D) + "\n")
    print("OK", [(r["titre"], r["nuits"], r["prix"]) for r in e["rooms"]])
else:
    from probe import call
    ck, tk = sys.argv[sys.argv.index("--push") + 1:][:2]
    T = json.load(open("templates_ids.json")); C = json.load(open("campaigns_ids.json"))
    print("template", call("PATCH", f"templates/{T[tk]}/", {"data": {"type": "template", "id": T[tk], "attributes": {"html": h}}})[0])
    st, r = call("GET", f"campaigns/{C[ck]}/campaign-messages/"); mid = r["data"][0]["id"]
    print("assign", call("POST", "campaign-message-assign-template/", {"data": {"type": "campaign-message", "id": mid, "relationships": {"template": {"data": {"type": "template", "id": T[tk]}}}}})[0])
    print("objet", call("PATCH", f"campaign-messages/{mid}/", {"data": {"type": "campaign-message", "id": mid, "attributes": {"definition": {"channel": "email", "content": {"subject": e["objets"][0], "preview_text": ""}}}}})[0])
