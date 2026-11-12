import unittest
from datetime import date

from social.marque import charger
from social.s4_planification import planifier

STRAT = charger("lovenspa").strategie("instagram")


def lodging(h, region="Bretagne", prix=150.0, equip=("Spa",), medias=5, exclus=(), typ="Gîte", ambiance=1):
    return {"handle": h, "nom": f"Nom {h} - x", "type": typ, "ville": "V", "ville_reference": None, "region": region,
            "equipements": list(equip), "equipements_non_citables": list(exclus), "prix_a_partir_de": prix,
            "url": f"https://www.lovenspa.fr/products/{h}", "actif": True, "medias": medias, "ambiance": ambiance}


def catalogue():
    out = []
    for r in STRAT["regions_poids"]:
        for i in range(8):
            out.append(lodging(f"{r[:3]}-{i}", region=r, prix=100 + 10 * i, equip=("Spa", "Sauna") if i % 2 else ("Spa",)))
    return out


class TestHelpers(unittest.TestCase):
    def test_monday_and_week(self):
        self.assertEqual(planifier.monday(date(2026, 11, 19)), date(2026, 11, 16))
        self.assertEqual(planifier.week_index(date(2026, 11, 16)), planifier.week_index(date(2026, 11, 22)))

    def test_stable(self):
        self.assertEqual(planifier.stable("a", 1), planifier.stable("a", 1))
        self.assertNotEqual(planifier.stable("a", 1), planifier.stable("a", 2))

    def test_temps_fort_wraps_year(self):
        self.assertIn("Hiver", planifier.temps_fort(date(2027, 1, 5), STRAT)["theme"])
        self.assertIn("carte cadeau", planifier.temps_fort(date(2026, 11, 20), STRAT)["theme"])

    def test_concours_dates(self):
        self.assertIn(date(2026, 12, 1), planifier.concours_dates(STRAT, 2026))
        self.assertIn(date(2026, 10, 15), planifier.concours_dates(STRAT, 2026))

    def test_eligible(self):
        self.assertTrue(planifier.eligible(lodging("a"), STRAT, set()))
        self.assertFalse(planifier.eligible(lodging("a", medias=2), STRAT, set()))
        self.assertFalse(planifier.eligible(lodging("a", prix=None), STRAT, set()))
        self.assertFalse(planifier.eligible(lodging("a", exclus=("BDSM",)), STRAT, set()))
        self.assertFalse(planifier.eligible(lodging("a", ambiance=3), STRAT, set()))
        self.assertFalse(planifier.eligible(lodging("a", ambiance=None), STRAT, set()))
        self.assertFalse(planifier.eligible(lodging("a", equip=("wifi",)), STRAT, set()))
        self.assertFalse(planifier.eligible(lodging("a"), STRAT, {"a"}))

    def test_recent(self):
        hist = [{"date": "2026-11-01", "handle": "a"}, {"date": "2026-08-01", "handle": "b"}]
        self.assertEqual(planifier.recent_handles(hist, date(2026, 11, 16), 56), {"a"})

    def test_pick_region_prefers_weight_then_unused(self):
        avail = set(STRAT["regions_poids"])
        self.assertEqual(planifier.pick_region(STRAT, [], avail), "Île-de-France")
        self.assertNotEqual(planifier.pick_region(STRAT, ["Île-de-France"] * 3, avail), "Île-de-France")

    def test_match_selection(self):
        f = lodging("a", prix=140, equip=("Spa",))
        self.assertTrue(planifier.match_selection(f, {"prix_max": 150, "equipement": "Spa"}, None))
        self.assertFalse(planifier.match_selection(f, {"equipement": "Sauna"}, None))
        self.assertFalse(planifier.match_selection(f, {"region": True}, "Occitanie"))

    def test_utm(self):
        self.assertTrue(planifier.utm(STRAT, "https://x/p", "lieu", date(2026, 11, 16)).endswith(
            "?utm_source=instagram&utm_medium=social&utm_campaign=lieu&utm_content=2026-11-16"))


class TestPlanWeek(unittest.TestCase):
    def test_five_slots_three_reels_distinct_lodgings(self):
        p = planifier.plan_week(date(2026, 11, 18), catalogue(), [], STRAT)
        self.assertEqual(p["semaine"], "2026-11-16")
        self.assertEqual([s["format"] for s in p["cases"]].count("REELS"), 3)
        handles = [f["handle"] for s in p["cases"] if s["format"] != "STORY" for f in s.get("offres") or []]
        self.assertEqual(len(handles), len(set(handles)))

    def test_couple_gets_unseen_lodging(self):
        p = planifier.plan_week(date(2026, 11, 18), catalogue(), [], STRAT)
        c = next(x for x in p["cases"] if x["moteur"] == "couple")
        autres = {o["handle"] for x in p["cases"] if x["moteur"] in ("lieu", "selection", "concours") for o in x.get("offres") or []}
        self.assertEqual(len(c["offres"]), 1)
        self.assertNotIn(c["offres"][0]["handle"], autres)

    def test_support_cases_stories_and_monthly_recruitment(self):
        p = planifier.plan_week(date(2026, 11, 30), catalogue(), [], STRAT)  # semaine du 30/11 : mercredi 2 décembre
        stories = [c for c in p["cases"] if c["moteur"] == "story"]
        self.assertEqual(len(stories), 7)
        self.assertTrue(all(c["format"] == "STORY" and c["offres"] for c in stories))
        rec = [c for c in p["cases"] if c["moteur"] == "recrutement"]
        self.assertEqual([c["date"] for c in rec], ["2026-12-02"])
        self.assertIn("/pages/devenir-partenaire", rec[0]["lien"])
        feed = {o["handle"] for c in p["cases"] if c["moteur"] not in ("story", "recrutement") for o in c.get("offres") or []}
        self.assertNotIn(rec[0]["offres"][0]["handle"], feed)
        p = planifier.plan_week(date(2026, 11, 16), catalogue(), [], STRAT)
        self.assertFalse([c for c in p["cases"] if c["moteur"] == "recrutement"])  # pas en milieu de mois
        regions = [s["region"] for s in p["cases"] if s["moteur"] == "lieu"]
        self.assertEqual(len(set(regions)), 3)

    def test_rotation_excludes_recent(self):
        hist = [{"date": "2026-11-10", "handle": f["handle"]} for f in catalogue() if f["region"] == "Île-de-France"]
        p = planifier.plan_week(date(2026, 11, 16), catalogue(), hist, STRAT)
        lieux = [s["offres"][0]["handle"] for s in p["cases"] if s["moteur"] == "lieu"]
        self.assertFalse(any(h.startswith("Île") for h in lieux))

    def test_concours_without_partner_falls_back(self):
        p = planifier.plan_week(date(2026, 11, 30), catalogue(), [], STRAT)  # concours le 01/12
        self.assertTrue(any("aucun hébergeur volontaire" in a for a in p["alertes"]))
        self.assertTrue(any(s["moteur"] == "selection" for s in p["cases"]))

    def test_concours_with_partner(self):
        cat = catalogue()
        partners = [{"handle": cat[0]["handle"], "accord_concours": True, "nuits_offertes": 1}]
        p = planifier.plan_week(date(2026, 11, 30), cat, [], STRAT, partners)
        conc = [s for s in p["cases"] if s["moteur"] == "concours"]
        self.assertEqual(len(conc), 1)
        self.assertEqual(conc[0]["offres"][0]["handle"], cat[0]["handle"])

    def test_concours_partner_not_eligible(self):
        cat = catalogue()
        cat[0] = dict(cat[0], ambiance=4)
        partners = [{"handle": cat[0]["handle"], "accord_concours": True, "nuits_offertes": 1}]
        p = planifier.plan_week(date(2026, 11, 30), cat, [], STRAT, partners)
        conc = [s for s in p["cases"] if s["moteur"] == "concours"]
        self.assertEqual(conc[0]["statut"], "BLOQUE")
        self.assertTrue(any("non éligible" in a for a in p["alertes"]))

    def test_blocked_when_empty(self):
        p = planifier.plan_week(date(2026, 11, 16), [], [], STRAT)
        self.assertTrue(all(s["statut"] == "BLOQUE" for s in p["cases"] if s["moteur"] != "couple"))

    def test_markdown(self):
        md = planifier.to_markdown(planifier.plan_week(date(2026, 11, 16), catalogue(), [], STRAT))
        self.assertIn("| 2026-11-16 18:30 | lieu | REELS |", md)


if __name__ == "__main__":
    unittest.main()
