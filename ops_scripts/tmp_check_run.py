import os, json

base = "artifacts/apps_rg/runtime_proofs/executive_summary/real"
runs = sorted(os.listdir(base))
latest = runs[-1]
print("Run:", latest)

x3_path = f"{base}/{latest}/x3_disposition.json"
if not os.path.exists(x3_path):
    print("No x3_disposition.json found")
else:
    x3 = json.load(open(x3_path))
    print("X3 pass:", x3.get("pass"))
    print("X3 code:", x3.get("x3_code"))
    print("Product quality (X2):", x3.get("product_quality_status"))

    x2 = x3.get("x2_gate_results") or {}
    if isinstance(x2, dict):
        for k, v in x2.items():
            if v is False or (isinstance(v, dict) and not v.get("pass", True)):
                print("  X2 FAIL:", k)
    elif isinstance(x2, list):
        for item in x2:
            if not item.get("pass", True):
                print("  X2 FAIL:", item.get("name", item.get("gate_id", "?")))

    judges = x3.get("x1d_judge_results") or x3.get("judge_panel_results") or {}
    if isinstance(judges, dict):
        for judge, res in judges.items():
            if isinstance(res, dict):
                score = res.get("score") or res.get("overall_score")
                passed = res.get("pass")
                print(f"  Judge {judge}: score={score} pass={passed}")
    elif isinstance(judges, list):
        for j in judges:
            if isinstance(j, dict):
                print(f"  Judge {j.get('judge_id','?')}: score={j.get('score')} pass={j.get('pass')}")

# Show display text
for fname in ["publish_payload.json", "post_runtime/publish_payload.json"]:
    fpath = f"{base}/{latest}/{fname}"
    if os.path.exists(fpath):
        d = json.load(open(fpath))
        txt = d.get("resume_display_text") or ""
        print("\nDisplay text:", txt[:500])
        wc = len(txt.split())
        print("Word count:", wc)
        break

# Show X2 gate detail
for fname in ["x2_gate_report.json", "post_runtime/x2_gate_report.json", "x2_results.json"]:
    fpath = f"{base}/{latest}/{fname}"
    if os.path.exists(fpath):
        d = json.load(open(fpath))
        print("\nX2 gate detail:")
        gates = d.get("gates") or d.get("results") or d
        if isinstance(gates, dict):
            for k, v in gates.items():
                if isinstance(v, dict) and v.get("pass") is False:
                    print(f"  FAIL {k}: {v.get('message','')}")
                elif v is False:
                    print(f"  FAIL {k}")
        break
