"""Show the active_usage context windows from W3.2 consumers."""

import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
data = json.loads((REPO / "artifacts/agent_deprecation/w3_2_consumer_usage.json").read_text(encoding="utf-8"))
actives = [r for r in data["items"] if r["category"] == "active_usage"]

for r in actives:
    print("=" * 80)
    print(f"{r['agent']} -> {r['replacement_util']}")
    print(f"  consumer: {r['consumer']}")
    text = (REPO / r["consumer"]).read_text(encoding="utf-8", errors="replace").splitlines()
    refs = [ln_no for ln_no, _ in r["body_refs"]]
    imp_lines = [ln for ln, _ in r["import_lines"]]
    hot_lines = sorted(set(refs + imp_lines))
    for ln in hot_lines:
        ctx_start = max(1, ln - 2)
        ctx_end = min(len(text), ln + 3)
        print(f"  --- around line {ln} ---")
        for i in range(ctx_start, ctx_end + 1):
            marker = ">>>" if i == ln else "   "
            print(f"  {marker} {i:4d}: {text[i - 1]}")
    print()
