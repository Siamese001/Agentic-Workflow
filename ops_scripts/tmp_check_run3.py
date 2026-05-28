import json, re

run_dir = "artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_225447"

# X2 gate outputs
x2 = json.load(open(f"{run_dir}/x2_gate_outputs.json"))
print("=== X2 GATES ===")
for gate in x2.get("gates", []):
    status = "PASS" if gate.get("pass") else "FAIL"
    gid = gate.get("gate_id", gate.get("name", "?"))
    msg = gate.get("message", "") or gate.get("detail", "")
    print(f"  {status} {gid}: {msg[:120]}")

# Display text
txt = open(f"{run_dir}/resume_display_text.txt").read().strip()
wc = len(re.findall(r"\S+", txt))
print(f"\n=== DISPLAY TEXT ({wc} words) ===")
print(txt)

# Claim ledger
ledger = json.load(open(f"{run_dir}/claim_ledger.json"))
print("\n=== CLAIM LEDGER ===")
for row in ledger:
    print(f"  {row.get('source_fact_ids')}: {str(row.get('claim_text',''))[:80]}")

# Judge results
try:
    x3 = json.load(open(f"{run_dir}/x3_disposition.json"))
    judges = x3.get("x1d_judge_results") or {}
    if judges:
        print("\n=== JUDGE RESULTS ===")
        for judge, res in judges.items():
            if isinstance(res, dict):
                print(f"  {judge}: score={res.get('score')} pass={res.get('pass')}")
                for f in res.get("findings", []):
                    print(f"    - {f}")
except Exception as e:
    print(f"Could not load x3_disposition: {e}")
