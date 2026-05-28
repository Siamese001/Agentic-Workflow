import json, re, os

run_dir = "artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_225447"

# Check synthesis regen provider responses
for fname in sorted(os.listdir(run_dir)):
    if "synthesis_regen" in fname and "provider_response" in fname:
        fpath = f"{run_dir}/{fname}"
        d = json.load(open(fpath))
        raw = d.get("raw_model_output", "")
        if raw:
            try:
                parsed = json.loads(raw)
                rdt = parsed.get("resume_display_text", "")
                wc = len(re.findall(r"\S+", rdt))
                from apps_rg.runtime.validators.executive_summary_x2 import split_sentences
                sentences = split_sentences(rdt)
                print(f"{fname}: wc={wc} sentences={len(sentences)}")
                for i, s in enumerate(sentences):
                    print(f"  S{i+1}: {s[:90]}")
            except Exception as e:
                print(f"{fname}: parse error {e}")
        print()

# Check synthesis regen receipt for why accepted candidate wasn't used
sr = json.load(open(f"{run_dir}/synthesis_regen_receipt.json"))
print("Synthesis regen final state:")
print("  triggered:", sr.get("triggered"))
print("  final_reject_reason:", sr.get("final_reject_reason"))
print("  result_text:", (sr.get("result_resume_display_text") or sr.get("final_resume_display_text") or "")[:200])
# Look for the chosen output
for k, v in sr.items():
    if isinstance(v, str) and "enterprise" in v.lower() and len(v) > 100:
        wc = len(re.findall(r"\S+", v))
        print(f"  Found '{k}' wc={wc}: {v[:200]}")
