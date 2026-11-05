"""Définitions des segments de pilotage emailing LSPA (Klaviyo YdW2ER).
Groupes = ET, conditions d'un groupe = OU."""
RESERVANTS = "VKKfEV"
# Listes hébergeurs / internes / prospects + segments hébergeurs, suspects, messages archivés
EXCL_GROUPS = ["QSSnkN", "RQA8Yp", "Rd7hsv", "SnFD8P", "Tk7C3f", "TvwutC", "WmwJig", "SynY9V",
               ]
# Segments non référençables dans un segment : exclus au niveau des audiences de campagne / filtres de flow
EXCL_SEGMENTS_AT_SEND = ["VcAH9Z", "SveZQc", "WZBQGQ", "XaSmpC", "VcHMMw", "Xra8N9", "TbY7GX"]
HOST_STATUTS = ["abonne", "churn", "sans_abonnement", "en_grace"]
WUFOO_CONTACT = "SAxEa3"  # messages sans réservation archivés = SAxEa3 sans commande
SIGNALS = ["RShN5q", "W6aBGZ", "YrUaU6", "TEHFzT"]  # Clicked Email, Active on Site x2, Viewed Product
NEW_SUB = ["RkNKyc", "UHqvsa"]  # Subscribed to Email Marketing, Subscribed to List

def _member(gid, yes):
    c = {"type": "profile-group-membership", "is_member": yes, "group_ids": [gid]}
    if yes:
        c["timeframe_filter"] = None
    return c

def _metric(mid, op, val, days):
    return {"type": "profile-metric", "metric_id": mid, "measurement": "count",
            "measurement_filter": {"type": "numeric", "operator": op, "value": val},
            "timeframe_filter": {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": days},
            "metric_filters": None}

CONSENT = {"conditions": [{"type": "profile-marketing-consent", "consent": {
    "channel": "email", "can_receive_marketing": True, "consent_status": {"subscription": "any", "filters": None}}}]}

def _g(*conds):
    return {"conditions": list(conds)}

def _base():
    # NB : un filtre négatif sur lns_statut exclut aussi les profils sans la propriété (testé le 05/11) :
    # les hébergeurs sont donc exclus à l'envoi via EXCL_SEGMENTS_AT_SEND.
    archives = _g(_member(WUFOO_CONTACT, False), _member(RESERVANTS, True), {"type": "profile-metric", "metric_id": "RWV4qN", "measurement": "count",
                  "measurement_filter": {"type": "numeric", "operator": "greater-than-or-equal", "value": 1},
                  "timeframe_filter": {"type": "date", "operator": "alltime"}, "metric_filters": None})
    return [CONSENT, archives] + [_g(_member(x, False)) for x in EXCL_GROUPS]

def definitions():
    any_signal = lambda d: _g(*[_metric(m, "greater-than-or-equal", 1, d) for m in SIGNALS])
    no_signal = lambda d: [_g(_metric(m, "equals", 0, d)) for m in SIGNALS]
    return {
        "[Pilotage] 1. Clients consentants": _base() + [_g(_member(RESERVANTS, True))],
        "[Pilotage] 2. Engagés 90 j": _base() + [_g(_member(RESERVANTS, False)), any_signal(90)],
        "[Pilotage] 3. Tièdes 91-180 j": _base() + [_g(_member(RESERVANTS, False)), any_signal(180)] + no_signal(90),
        "[Pilotage] 4. À réactiver": _base() + [_g(_member(RESERVANTS, False))] + no_signal(180)
                                     + [_g(_metric(m, "equals", 0, 180)) for m in NEW_SUB],
    }
