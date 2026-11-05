"""Définitions des flows LSPA (API Klaviyo create flow). Tous créés en draft."""
import json
from emails import EMAILS
T = json.load(open("templates_ids.json"))
E = {e["id"]: e for e in EMAILS}
CLICKED, PLACED_ORDER = "RShN5q", "RWV4qN"
M_START, M_CONF, M_END, VIEWED = "S8ypgR", "U6Q3wu", "XFFNxs", "TEHFzT"
SEG4 = "TTygHG"

def email(aid, eid, nxt=None):
    e = E[eid]
    return {"temporary_id": aid, "type": "send-email", "links": {"next": nxt}, "data": {"message": {
        "from_email": "contact@lovenspa.fr", "from_label": "Love'nSpa", "reply_to_email": "contact@lovenspa.fr",
        "cc_email": None, "bcc_email": None, "subject_line": e["objets"][0], "preview_text": "",
        "template_id": T[eid], "smart_sending_enabled": True, "transactional": False,
        "add_tracking_params": True, "custom_tracking_params": None, "additional_filters": None,
        "name": f"{e['flow']} · {eid}"}, "status": "draft"}}

def delay(aid, value, unit, nxt):
    return {"temporary_id": aid, "type": "time-delay", "links": {"next": nxt},
            "data": {"unit": unit, "value": value, "secondary_value": None, "timezone": "profile",
                     "delay_until_time": None, "delay_until_weekdays": None}}

def split_no(aid, metric, nxt_if_false):
    """Continue seulement si l'événement n'a PAS eu lieu depuis l'entrée dans le flow."""
    return {"temporary_id": aid, "type": "conditional-split", "links": {"next_if_true": None, "next_if_false": nxt_if_false},
            "data": {"profile_filter": {"condition_groups": [{"conditions": [{"type": "profile-metric", "metric_id": metric,
                     "measurement": "count", "measurement_filter": {"type": "numeric", "operator": "greater-than", "value": 0},
                     "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": None}]}]}}}

def no_event_since_start(metric):
    return {"conditions": [{"type": "profile-metric", "metric_id": metric, "measurement": "count",
            "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0},
            "timeframe_filter": {"type": "date", "operator": "flow-start"}, "metric_filters": None}]}

def flow(name, trigger, actions, profile_filter=None):
    return {"name": name, "definition": {"triggers": [trigger], "profile_filter": profile_filter,
            "actions": actions, "entry_action_id": actions[0]["temporary_id"]}}

from segments import EXCL_GROUPS
SUBSCRIBED = {"conditions": [{"type": "profile-marketing-consent", "consent": {"channel": "email", "can_receive_marketing": True,
              "consent_status": {"subscription": "subscribed", "filters": None}}}]}
NOT_HOST_LISTS = [{"conditions": [{"type": "profile-group-membership", "is_member": False, "group_ids": [g]}]} for g in EXCL_GROUPS]

def guard(*extra):
    """Filtre commun : abonné explicitement + hors listes hébergeurs/internes/prospects + conditions de sortie."""
    return {"condition_groups": [SUBSCRIBED] + NOT_HOST_LISTS + list(extra)}

FLOWS = [
  flow("[Pilotage] 9. Réactivation (segment 4)", {"type": "segment", "id": SEG4},
       [email("a1", "f9-e1", "a2"), delay("a2", 14, "days", "a3"), split_no("a3", CLICKED, "a4"), email("a4", "f9-e2")]),
  flow("[Pilotage] 3. Le souvenir et la suite (J+30)", {"type": "metric", "id": M_END},
       [delay("a1", 29, "days", "a2"), email("a2", "f3-e1")], guard(no_event_since_start(M_CONF))),
  flow("[Pilotage] 4. Fenêtre de retour (J+90, J+110)", {"type": "metric", "id": M_END},
       [delay("a1", 89, "days", "a2"), email("a2", "f4-e1", "a3"), delay("a3", 20, "days", "a4"), email("a4", "f4-e2")],
       guard(no_event_since_start(M_CONF))),
  flow("[Pilotage] 5. Anniversaire du séjour (~J-21)", {"type": "metric", "id": M_END},
       [delay("a1", 343, "days", "a2"), email("a2", "f5-e1")], guard(no_event_since_start(M_CONF))),
  flow("[Pilotage] 6. Abandon de réservation (H+1, J+1)", {"type": "metric", "id": M_START},
       [delay("a1", 1, "hours", "a2"), email("a2", "f6-e1", "a3"), delay("a3", 23, "hours", "a4"), email("a4", "f6-e2")],
       guard(no_event_since_start(M_CONF))),
  flow("[Pilotage] 7. Abandon de navigation (H+4)", {"type": "metric", "id": VIEWED},
       [delay("a1", 4, "hours", "a2"), email("a2", "f7-e1")],
       guard(no_event_since_start(M_START), no_event_since_start(M_CONF), no_event_since_start(PLACED_ORDER))),
  flow("[Pilotage] 8. Bienvenue (J0, J+3, J+7)", {"type": "list", "id": "VWMYkS"},
       [email("a1", "f8-e1", "a2"), delay("a2", 3, "days", "a3"), email("a3", "f8-e2", "a4"), delay("a4", 4, "days", "a5"), email("a5", "f8-e3")],
       guard(no_event_since_start(M_CONF))),
]
