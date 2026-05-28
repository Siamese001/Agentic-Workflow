import os, json

base = "artifacts/apps_rg/runtime_proofs/executive_summary/real"
run_id = "exec_summary_20260527_225447"
run_dir = os.path.join(base, run_id)
print("Run:", run_id)
print("Exists:", os.path.exists(run_dir))

files = os.listdir(run_dir) if os.path.exists(run_dir) else []
print("Files:", sorted(files))

# Load x3_disposition
x3_path = os.path.join(run_dir, "x3_disposition.json")
if os.path.exists(x3_path):
    x3 = json.load(open(x3_path))
    print("\nX3 pass:", x3.get("pass"))
    print("X3 code:", x3.get("x3_code"))
    print("Product quality (X2):", x3.get("product_quality_status"))
    
    # X2 gate results
    x2 = x3.get("x2_gate_results") or {}
    if isinstance(x2, dict):
        for k, v in x2.items():
            status = v if not isinstance(v, dict) else v.get("pass", True)
            if status is False:
                print("  X2 FAIL:", k, v if not isinstance(v, dict) else v.get("message", ""))
    
    # Judge results  
    judges = x3.get("x1d_judge_results") or {}
    if isinstance(judges, dict):
        for judge, res in judges.items():
            if isinstance(res, dict):
                print(f"  Judge {judge}: score={res.get('score')} pass={res.get('pass')} findings={res.get('findings', [])}")
else:
    print("No x3_disposition.json")

# Show display text from finalized output
for fname in ["finalized_executive_summary.json", "publish_payload.json", "post_runtime/finalized_executive_summary.json"]:
    fpath = os.path.join(run_dir, fname)
    if os.path.exists(fpath):
        d = json.load(open(fpath))
        txt = d.get("resume_display_text") or ""
        import re
        wc = len(re.findall(r"\S+", txt))
        print(f"\n[{fname}] words={wc}")
        print(txt)
        break
