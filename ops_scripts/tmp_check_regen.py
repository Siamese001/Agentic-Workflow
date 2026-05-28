import json, re

run_dir = "artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_230359"

# Check judge regen cycles
for cycle in [1, 2, 3]:
    fpath = f"{run_dir}/judge_remediation_receipt_cycle_{cycle}.json"
    try:
        d = json.load(open(fpath))
        print(f"\n=== Regen cycle {cycle} ===")
        print("  x2_pass:", d.get("x2_pass"))
        print("  accepted:", d.get("accepted"))
        print("  reject_reason:", d.get("reject_reason", "")[:150])
        judges = d.get("judge_results") or {}
        for j, r in judges.items():
            if isinstance(r, dict):
                print(f"  Judge {j}: score={r.get('score')} pass={r.get('pass')}")
        rdt = d.get("resume_display_text") or d.get("regen_display_text") or ""
        if rdt:
            wc = len(re.findall(r"\S+", rdt))
            print(f"  Regen display ({wc} wc): {rdt[:200]}")
    except FileNotFoundError:
        pass

# Check same_authority_regen_receipt
sa = json.load(open(f"{run_dir}/same_authority_regen_receipt.json"))
print("\n=== Same authority regen receipt ===")
print("triggered:", sa.get("triggered"))
print("final_accepted:", sa.get("final_accepted"))
print("cycles_completed:", sa.get("cycles_completed"))
print("final_disposition:", sa.get("final_disposition"))
rdt = sa.get("final_resume_display_text") or sa.get("final_display_text") or ""
if rdt:
    wc = len(re.findall(r"\S+", rdt))
    print(f"Final regen display ({wc} wc): {rdt[:300]}")
