import json, os, sys, time, urllib.request
from segments import definitions
H = {"Authorization": f"Klaviyo-API-Key {os.environ['KLAVIYO_TOKEN']}", "revision": "2025-10-15",
     "accept": "application/json", "content-type": "application/json"}
def call(method, path, body=None):
    req = urllib.request.Request("https://a.klaviyo.com/api/" + path, method=method, headers=H,
                                 data=json.dumps(body).encode() if body else None)
    for i in range(6):
        try:
            with urllib.request.urlopen(req) as r: return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(2 ** i); continue
            return e.code, json.loads(e.read() or b"{}")
out = {}
for name, groups in definitions().items():
    st, r = call("POST", "segments/", {"data": {"type": "segment", "attributes": {
        "name": name, "definition": {"condition_groups": groups}, "is_starred": True}}})
    out[name] = r["data"]["id"] if st in (200, 201) else None
    print(st, name, out[name] or json.dumps(r.get("errors"), ensure_ascii=False)[:600])
json.dump(out, open("segments_ids.json", "w"), ensure_ascii=False, indent=1)
