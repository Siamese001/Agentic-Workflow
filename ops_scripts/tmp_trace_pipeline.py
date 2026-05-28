import json, re

run_dir = "artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_225447"

def wc(txt):
    return len(re.findall(r"\S+", txt or ""))

# 1. Original LLM output (before synthesis regen)
l2 = json.load(open(f"{run_dir}/l2_output.json"))
l2_rdt = l2.get("resume_display_text") or ""
print(f"L2 output (original LLM): wc={wc(l2_rdt)}")
print(f"  {l2_rdt[:200]}")

# 2. Synthesis regen output
sr = json.load(open(f"{run_dir}/synthesis_regen_receipt.json"))
sr_best = next((a for a in sr.get("attempts", []) if a.get("best_candidate")), None)
if sr_best:
    print(f"\nSynthesis regen best candidate: wc={sr_best.get('regen_resume_word_count')}")
    # Get the actual text from the provider response
    call_id = sr_best.get("call_id", "")
    import os
    for f in os.listdir(run_dir):
        if call_id and call_id[:20] in f and "response" in f:
            d = json.load(open(f"{run_dir}/{f}"))
            txt = d.get("resume_display_text") or ""
            if txt:
                print(f"  From {f}: wc={wc(txt)}")
                print(f"  {txt[:300]}")

# 3. Graph only repair
gr = json.load(open(f"{run_dir}/graph_only_generation_quality_repair.json"))
print(f"\nGraph only repair:")
print(f"  applied: {gr.get('applied')}")
print(f"  repair_kind: {gr.get('repair_kind')}")
print(f"  before wc: {wc(gr.get('before_resume_display_text', ''))}")
print(f"  after wc: {wc(gr.get('after_resume_display_text', ''))}")
print(f"  before: {(gr.get('before_resume_display_text') or '')[:200]}")

# 4. Final display text
rdt_txt = open(f"{run_dir}/resume_display_text.txt").read()
print(f"\nFinal display text: wc={wc(rdt_txt)}")
print(f"  {rdt_txt[:300]}")

# 5. Executive summary finalize coherence
fch = json.load(open(f"{run_dir}/executive_summary_finalize_coherence.json"))
print(f"\nFinalize coherence judge_polish:")
print(f"  {fch.get('judge_polish')}")
