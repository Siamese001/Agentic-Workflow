"""Show context windows for the 11 low-risk W3.2 touches."""
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
data = json.loads((REPO / "artifacts/agent_deprecation/w3_2_consumer_usage.json").read_text(encoding="utf-8"))

low_risk = [r for r in data["items"] if r["category"] in ("typehint_only", "class_reference_only")]

for r in low_risk:
    print("=" * 80)
    print(f"[{r['category']}] {r['agent']} -> {r['replacement_util']}")
    print(f"  consumer: {r['consumer']}")
    text = (REPO / r["consumer"]).read_text(encoding="utf-8", errors="replace").splitlines()
    imp_lines = [ln for ln, _ in r["import_lines"]]
    refs = [ln_no for ln_no, _ in r["body_refs"]]
    hot_lines = sorted(set(refs + imp_lines))
    for ln in hot_lines:
        ctx_start = max(1, ln - 1)
        ctx_end = min(len(text), ln + 1)
        for i in range(ctx_start, ctx_end + 1):
            marker = ">>>" if i == ln else "   "
            print(f"  {marker} {i:4d}: {text[i-1][:180]}")
        print()
