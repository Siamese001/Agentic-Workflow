"""Extract detailed results for key families from proof JSON."""

import json

data = json.load(open("artifacts/b5r_proof_raw.json", encoding="utf-8"))
focus = {"F05", "F06", "F08", "F09", "F12", "F13", "F14", "F17", "F21", "F22", "F25", "F27", "F28"}

for r in data["family_results"]:
    fid = r["family"]["id"]
    if fid not in focus:
        continue
    claim = r["family"]["grade_claim"]
    live = r["live_grade"]
    d1 = r["dist_at_1"]
    rel = r["n_relevant_lt050"]
    strong = r["n_strong_lt040"]
    name = r["family"]["name"]
    print(f"\n=== {fid}: {name} ===")
    print(f"  claim={claim:<14}  live={live:<22}  dist@1={d1}  rel={rel}/5  strong={strong}/5")
    for h in r["hits"]:
        sc = h["source_collection"]
        tb = h.get("topic_bucket", "")
        hp = (h.get("heading_path") or "")[:65]
        url = (h.get("source_url") or "")[-55:]
        band = h.get("source_band", "")
        tier = h.get("authority_tier", "")
        d = h["distance"]
        print(f"  [{h['rank']}] d={d:.4f}  band={band:<20}  tier={tier:<12}  tb={tb:<14}  sc={sc}")
        print(f"       url=...{url}")
        print(f"       head={hp}")
