import json

data = json.load(open("artifacts/b5r_proof_raw.json", encoding="utf-8"))
for r in data["family_results"]:
    fid = r["family"]["id"]
    if fid not in ("F08", "F06", "F12", "F13", "F14", "F17"):
        continue
    print(f"\n=== {fid} ===")
    print(f"dist@1={r['dist_at_1']}  rel={r['n_relevant_lt050']}/5")
    for h in r["hits"]:
        rk = h["rank"]
        d = h["distance"]
        url = h["source_url"]
        hp = h.get("heading_path", "")
        tb = h.get("topic_bucket", "")
        snip = (h.get("doc_snippet") or "")[:120]
        print(f"  [{rk}] d={d:.4f}  tb={tb}  head={hp[:60]}")
        print(f"       url={url}")
        print(f"       snip={snip}")
