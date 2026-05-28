import json, re, os

run_dir = "artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_225447"

# Load the synthesis regen receipt to understand flow
sr = json.load(open(f"{run_dir}/synthesis_regen_receipt.json"))
print("=== SYNTHESIS REGEN RECEIPT ===")
print("first_pass_wc:", sr.get("first_pass_resume_word_count"))
print("triggered:", sr.get("triggered"))
print("reject_reason:", (sr.get("reject_reason") or "")[:200])
print("chosen_candidate wc:", next((a.get("regen_resume_word_count") for a in sr.get("attempts", []) if a.get("best_candidate")), "?"))
print("chosen_candidate facts:", next((a.get("monotonicity", {}).get("post_unique_source_fact_ids") for a in sr.get("attempts", []) if a.get("best_candidate")), "?"))

# Get synthesis regen output text
sr_out = sr.get("regen_resume_display_text") or sr.get("result_resume_display_text") or ""
if not sr_out:
    # Find in the JSON keys
    for k, v in sr.items():
        if isinstance(v, str) and "enterprise" in v.lower() and len(v) > 100:
            print(f"Found in key '{k}': {v[:200]}")
            sr_out = v
            break
if sr_out:
    wc = len(re.findall(r"\S+", sr_out))
    print(f"\nSynthesis regen output ({wc} wc):")
    print(sr_out[:600])

# Check stage_sequence.json or pipeline stages
for fname in ["stage_sequence.json", "pipeline_stages.json", "runtime_exhaust_receipt.json"]:
    fpath = f"{run_dir}/{fname}"
    if os.path.exists(fpath):
        d = json.load(open(fpath))
        print(f"\n=== {fname} ===")
        if isinstance(d, list):
            for item in d[:10]:
                print(" ", item.get("stage") or item.get("name") or item)
        elif isinstance(d, dict):
            print(json.dumps({k: v for k, v in d.items() if k != "details"}, indent=2)[:500])
        break
