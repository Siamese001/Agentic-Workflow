import json, re, os

run_dir = "artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260527_225447"

# Check the graph_only repair fields more carefully
gr = json.load(open(f"{run_dir}/graph_only_generation_quality_repair.json"))
print("=== Graph only repair ===")
before = gr.get("before_resume_display_text") or ""
after = gr.get("after_resume_display_text") or ""
print("applied:", gr.get("applied"))
print("repaired:", gr.get("repaired"))
print("repair_kind:", gr.get("repair_kind"))
print("before wc:", len(re.findall(r"\S+", before)))
print("after wc:", len(re.findall(r"\S+", after)))
print("before:", before[:200])
print("after:", after[:200])

# Check synthesis regen attempt 1 response
fname = "provider_response_synthesis_regen_cycle00_attempt01_synthesis_regen-00-01-01f0f866.json"
fpath = f"{run_dir}/{fname}"
if os.path.exists(fpath):
    d = json.load(open(fpath))
    # Find display text
    rdt = d.get("resume_display_text") or ""
    if not rdt:
        # Look for nested response
        rdt = (d.get("output") or {}).get("resume_display_text") or ""
    if not rdt:
        # Look in choices
        for k, v in d.items():
            if isinstance(v, str) and len(v) > 100:
                print(f"\nKey {k} ({len(v)} chars):", v[:200])
    wc = len(re.findall(r"\S+", rdt))
    print(f"\nSynthesis regen attempt 1 display ({wc} wc): {rdt[:400]}")
else:
    print(f"\nFile not found: {fname}")
    
# Check l2_output.json 
l2 = json.load(open(f"{run_dir}/l2_output.json"))
rdt = l2.get("resume_display_text") or ""
wc = len(re.findall(r"\S+", rdt))
print(f"\nL2 output display ({wc} wc): {rdt[:400]}")

# Check executive_summary_finalize_coherence.json  
fcp = f"{run_dir}/executive_summary_finalize_coherence.json"
if os.path.exists(fcp):
    fc = json.load(open(fcp))
    print("\nFinalize coherence keys:", list(fc.keys())[:15])
    fdt = fc.get("post_display_text") or fc.get("result_display_text") or fc.get("resume_display_text") or ""
    if fdt:
        print("Finalize display:", fdt[:300])
