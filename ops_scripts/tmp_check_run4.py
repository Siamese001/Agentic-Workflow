import json, re

run_dir = "artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_225447"

gr = json.load(open(f"{run_dir}/graph_only_generation_quality_repair.json"))
print("triggered:", gr.get("triggered"))
print("repair_applied:", gr.get("repair_applied"))
print("reject_reason:", gr.get("reject_reason"))
print("pre_display_wc:", len(re.findall(r"\S+", gr.get("pre_repair_resume_display_text") or "")))
print("post_display_wc:", len(re.findall(r"\S+", gr.get("post_repair_resume_display_text") or "")))

# Keys in the receipt
print("\nKeys:", list(gr.keys()))

# Try to find the synthesis regen output to understand what happened
sr = json.load(open(f"{run_dir}/synthesis_regen_receipt.json"))
best = next((a for a in sr.get("attempts", []) if a.get("best_candidate")), None)
if best:
    print("\nSynthesis regen best candidate:")
    print("  attempt:", best.get("attempt"))
    print("  wc:", best.get("regen_resume_word_count"))
    print("  ledger_rows:", best.get("regen_claim_ledger_rows"))
    print("  accepted:", best.get("monotonicity", {}).get("accepted"))

# Check the synthesis regen provider response directly
for f in ["provider_response_synthesis_regen.json", "provider_response_synthesis_regen_cycle00_attempt01_synthesis_regen-00-01-01f0f866.json"]:
    import os
    fpath = f"{run_dir}/{f}"
    if os.path.exists(fpath):
        d = json.load(open(fpath))
        txt = d.get("resume_display_text") or d.get("output", {}).get("resume_display_text") or ""
        if txt:
            wc = len(re.findall(r"\S+", txt))
            print(f"\nSynthesis regen output ({f}) wc={wc}:")
            print(txt[:400])

# Check parsed output (after synthesis regen but before finalize)
po = json.load(open(f"{run_dir}/parsed_output.json"))
pt = po.get("resume_display_text") or ""
wc = len(re.findall(r"\S+", pt))
print(f"\nParsed output wc={wc}:")
print(pt[:600])
