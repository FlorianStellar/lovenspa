from segments import definitions, EXCL_GROUPS, RESERVANTS, HOST_STATUTS
D = definitions()
def groups_with(defn, pred): return [g for g in defn["condition_groups"] if any(pred(c) for c in g["conditions"])] if "condition_groups" in defn else [g for g in defn if any(pred(c) for c in g["conditions"])]
def test_four_segments(): assert len(D) == 4
def test_all_require_consent():
    for d in D.values(): assert groups_with(d, lambda c: c["type"] == "profile-marketing-consent")
def test_all_exclude_hosts_suspects_archives():
    for d in D.values():
        excl = {c["group_ids"][0] for g in d for c in g["conditions"] if c["type"]=="profile-group-membership" and not c["is_member"]}
        assert set(EXCL_GROUPS) <= excl
def test_disjoint_on_reservants():
    m = {n: [g["conditions"][0]["is_member"] for g in d if len(g["conditions"])==1 and g["conditions"][0].get("group_ids")==[RESERVANTS]] for n,d in D.items()}
    assert m["[Pilotage] 1. Clients consentants"] == [True]
    for n in list(D)[1:]: assert m[n] == [False]
def test_tiedes_exclude_engages():
    d = D["[Pilotage] 3. Tièdes 91-180 j"]
    zeros90 = [c for g in d for c in g["conditions"] if c.get("measurement_filter",{}).get("operator")=="equals" and c["timeframe_filter"]["quantity"]==90]
    assert len(zeros90) == 4
def test_reactiver_skips_new_subscribers():
    d = D["[Pilotage] 4. À réactiver"]
    ids = {c["metric_id"] for g in d for c in g["conditions"] if c["type"]=="profile-metric"}
    assert {"RkNKyc","UHqvsa"} <= ids
def test_no_timeframe_on_non_member():
    for d in D.values():
        for g in d:
            for c in g["conditions"]:
                if c["type"]=="profile-group-membership" and not c["is_member"]: assert "timeframe_filter" not in c

def test_hosts_and_archives_excluded():
    for d in D.values():
        assert not [c for g in d for c in g["conditions"] if c["type"]=="profile-property"]
        assert any(c.get("group_ids")==["SAxEa3"] and not c["is_member"] for g in d for c in g["conditions"] if c["type"]=="profile-group-membership")
def test_archives_rule_keeps_reservants():
    for d in D.values():
        g = [g for g in d if any(c.get("group_ids")==["SAxEa3"] for c in g["conditions"])][0]
        assert any(c.get("group_ids")==[RESERVANTS] and c["is_member"] for c in g["conditions"])
