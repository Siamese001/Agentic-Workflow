import json, re, os

base = "artifacts/apps_rg/runtime_proofs/executive_summary/real"
runs = sorted(r for r in os.listdir(base) if r.startswith("exec_summary_20260527"))
latest = runs[-1]
print("Run:", latest)
run_dir = f"{base}/{latest}"

# X2 gate results
x2 = json.load(open(f"{run_dir}/x2_gate_outputs.json"))
fails = [g for g in x2.get("gates", []) if not g.get("pass")]
if fails:
    print("X2 FAILS:")
    for g in fails:
        print(f"  {g.get('gate_id')}: {g.get('message', '')[:120]}")
else:
    print("X2: ALL PASS")

# X3 disposition
x3 = json.load(open(f"{run_dir}/x3_disposition.json"))
print("X3 code:", x3.get("x3_code"))
print("X3 pass:", x3.get("pass"))
print("Product quality:", x3.get("product_quality_status"))

# Judge results
judges = x3.get("x1d_judge_results") or {}
if judges:
    print("JUDGES:")
    for j, res in judges.items():
        if isinstance(res, dict):
            print(f"  {j}: score={res.get('score')} pass={res.get('pass')} findings={res.get('findings', [])}")

# Polish receipt
fch = json.load(open(f"{run_dir}/executive_summary_finalize_coherence.json"))
print("Polish actions:", fch.get("judge_polish", {}).get("actions", []))

# Display text
txt = open(f"{run_dir}/resume_display_text.txt").read()
wc = len(re.findall(r"\S+", txt))
print(f"\nDisplay ({wc} words):")
print(txt)
