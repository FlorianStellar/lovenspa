import json, os, time, urllib.request, sys
H = {"Authorization": f"Klaviyo-API-Key {os.environ['KLAVIYO_TOKEN']}", "revision": "2025-10-15", "accept": "application/json", "content-type": "application/json"}
def call(method, path, body=None):
    req = urllib.request.Request("https://a.klaviyo.com/api/" + path, method=method, headers=H, data=json.dumps(body).encode() if body else None)
    for i in range(6):
        try:
            with urllib.request.urlopen(req) as r: b = r.read(); return r.status, (json.loads(b) if b else {})
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(2**i); continue
            return e.code, json.loads(e.read() or b"{}")
def count(sid):
    for _ in range(30):
        st, r = call("GET", f"segments/{sid}/?additional-fields[segment]=profile_count&fields[segment]=is_processing,profile_count".replace("[","%5B").replace("]","%5D"))
        a = r["data"]["attributes"]
        if not a["is_processing"]: return a["profile_count"]
        time.sleep(5)
def patch(sid, groups, name=None):
    attrs = {"definition": {"condition_groups": groups}}
    if name: attrs["name"] = name
    return call("PATCH", f"segments/{sid}/", {"data": {"type": "segment", "id": sid, "attributes": attrs}})
