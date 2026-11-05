import re
from render import render, link
from emails import EMAILS, CAMPAIGNS
EMAILS = EMAILS + CAMPAIGNS
from event_schema import EVENTS, PROFILE_PROPS
def test_link_static_gets_utm(): assert link("https://x/?utm_campaign={c}&utm_content={k}", "a", "b") == "https://x/?utm_campaign=a&utm_content=b"
def test_link_dynamic_untouched(): assert link("{{ event.URL }}", "a", "b") == "{{ event.URL }}"
def test_every_email_has_unsubscribe_and_one_cta_label():
    for e in EMAILS:
        h = render(e); assert "{% unsubscribe_link %}" in h; assert h.count(e["cta"][0]) == 1
def test_no_unformatted_placeholders():
    for e in EMAILS: assert "{c}" not in render(e) and "{k}" not in render(e)
def test_mobile_body_font_enlarged():
    assert ".body{font-size:17px!important" in render(EMAILS[0])
def test_limits_objet_preheader():
    for e in EMAILS:
        assert len(e["preheader"]) <= 100
        for o in e["objets"]: assert len(re.sub(r"\{\{.*?\}\}", "XXXXXXXXXXXXXXXXXXXX", o)) <= 60, o
def test_event_vars_respect_contract():
    allowed = set(sum(EVENTS.values(), [])) | {"ProductName", "URL", "ImageURL"}
    for e in EMAILS:
        for v in re.findall(r"event\.(\w+)", render(e) + " ".join(e["objets"])): assert v in allowed, (e["id"], v)
def test_profile_lookups_respect_contract():
    for e in EMAILS:
        for v in re.findall(r"lookup:'(\w+)'", render(e) + " ".join(e["objets"])): assert v in PROFILE_PROPS
def test_no_false_urgency_words():
    for e in EMAILS:
        t = (render(e) + " ".join(e["objets"])).lower()
        for w in ["dernières places", "plus que", "vite", "derniere chance", "dernière chance", "expire"]: assert w not in t, (e["id"], w)

def test_flows_definitions():
    from flows import FLOWS
    for f in FLOWS:
        acts = f["definition"]["actions"]; ids = {a["temporary_id"] for a in acts}
        assert f["definition"]["entry_action_id"] in ids
        for a in acts:
            for v in a["links"].values(): assert v is None or v in ids
            if a["type"] == "send-email": assert a["data"]["status"] == "draft" and a["data"]["message"]["template_id"]
def test_french_nbsp():
    from render import fr
    assert fr("Une question ?") == "Une question&nbsp;?" and fr("{{ x|default:'a' }}") == "{{ x|default:'a' }}"
    import re
    for e in EMAILS:
        for p in re.findall(r'<(?:p class="body"|h1)[^>]*>(.*?)</(?:p|h1)>', render(e), re.S):
            assert " ?" not in p and " :" not in p, (e["id"], p[:80])
def test_flows_guards():
    from flows import FLOWS
    assert len(FLOWS) == 7
    for f in FLOWS[1:]:
        g = f["definition"]["profile_filter"]["condition_groups"]
        assert g[0]["conditions"][0]["consent"]["consent_status"]["subscription"] == "subscribed"
        assert any(c["conditions"][0].get("group_ids") == ["QSSnkN"] for c in g)
def test_no_utm_hardcoded():
    for e in EMAILS: assert "utm_" not in render(e)
def test_temoin_excluded_from_flows_3_to_5_only():
    from flows import FLOWS, NOT_TEMOIN
    for f in FLOWS[1:]:
        has = NOT_TEMOIN in f["definition"]["profile_filter"]["condition_groups"]
        assert has == any(k in f["name"] for k in ["3.", "4.", "5."]), f["name"]
