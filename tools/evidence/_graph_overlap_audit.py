"""Graph-accurate overlap audit using covers edges from ADG scanner.

Classifies every production module by whether it is covered by:
  - ADG-derived tests only (_adg.py files)
  - Foundational tests only (non-_adg test files)
  - Both
  - Neither
Also produces fan_in threshold analysis.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner


def is_prod(p: str) -> bool:
    p2 = p.replace("\\", "/")
    return (
        not p2.startswith("tests/")
        and not p2.startswith("tools/")
        and "ops_scripts" not in p2
        and "__pycache__" not in p2
        and p2.endswith(".py")
    )


def adg_to_dotted(name: str) -> str:
    for pfx in ("ADG::Symbol::", "ADG::Module::", "Symbol::", "Module::"):
        if name.startswith(pfx):
            name = name[len(pfx):]
    return name.removesuffix(".py")


def layer_from(path: str) -> str:
    p = path.replace("\\", "/")
    for prefix, label in [
        ("agentic_core/L0", "L0"), ("agentic_core/L1", "L1"),
        ("agentic_core/L2", "L2"), ("agentic_core/L3", "L3"),
        ("agentic_core/L4", "L4"), ("agentic_core/L5", "L5"),
        ("agentic_core/L6", "L6"), ("apps_rg", "L_APP"),
        ("apps_shared", "L_SHARED"), ("system_learning", "L_SL"),
        ("agentic_core/runtime", "L_RUNTIME"),
        ("agentic_core/enforcement", "L_ENF"),
        ("agentic_core/utils", "L_UTILS"),
        ("agentic_core/adg", "L_ADG"),
    ]:
        if p.startswith(prefix):
            return label
    return "OTHER"


print("[AUDIT] Scanning ADG...")
scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True)
result = scanner.scan()
print(f"[AUDIT] Done: {len(result.modules)} modules, {len(result.edges)} edges")

prod_set = {m for m in result.modules if is_prod(m)}

# Build prod dotted->path lookup
prod_dotted_to_path: dict[str, str] = {}
for m in prod_set:
    d = m.replace("\\", "/").removesuffix(".py").replace("/", ".")
    prod_dotted_to_path[d] = m

# Build fan_in from imports edges
fan_in: dict[str, int] = defaultdict(int)
for e in result.edges:
    if e.relation_type != "imports":
        continue
    to = adg_to_dotted(e.to_name)
    if to in prod_dotted_to_path:
        fan_in[prod_dotted_to_path[to]] += 1
    else:
        parent = ".".join(to.rsplit(".", 1)[:-1])
        if parent in prod_dotted_to_path:
            fan_in[prod_dotted_to_path[parent]] += 1

# Build covers map from covers edges
# from_name = test module, to_name = prod module
covered_by_adg: dict[str, list[str]] = defaultdict(list)
covered_by_foundational: dict[str, list[str]] = defaultdict(list)

for e in result.edges:
    if e.relation_type != "covers":
        continue
    from_d = adg_to_dotted(e.from_name)
    to_d = adg_to_dotted(e.to_name)
    if to_d not in prod_dotted_to_path:
        continue
    prod_path = prod_dotted_to_path[to_d]
    # Determine if the test file is an ADG-derived stub or foundational
    from_last = from_d.split(".")[-1]  # e.g. "test_foo_adg" or "test_foo"
    if from_last.endswith("_adg"):
        covered_by_adg[prod_path].append(from_d)
    else:
        covered_by_foundational[prod_path].append(from_d)

both = sorted(p for p in prod_set if covered_by_adg[p] and covered_by_foundational[p])
adg_only = sorted(p for p in prod_set if covered_by_adg[p] and not covered_by_foundational[p])
found_only = sorted(p for p in prod_set if not covered_by_adg[p] and covered_by_foundational[p])
neither = sorted(p for p in prod_set if not covered_by_adg[p] and not covered_by_foundational[p])

print()
print("=== GRAPH-ACCURATE OVERLAP AUDIT (covers edges) ===")
print(f"  Both ADG + Foundational : {len(both)}")
print(f"  ADG only                : {len(adg_only)}")
print(f"  Foundational only       : {len(found_only)}")
print(f"  Neither (uncovered!)    : {len(neither)}")
print(f"  Total production        : {len(prod_set)}")

print()
print("=== OVERLAP BREAKDOWN BY LAYER ===")
layer_stats: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
for p in prod_set:
    la = layer_from(p)
    if p in set(both):
        layer_stats[la]["both"] += 1
    elif covered_by_adg[p]:
        layer_stats[la]["adg_only"] += 1
    elif covered_by_foundational[p]:
        layer_stats[la]["found_only"] += 1
    else:
        layer_stats[la]["neither"] += 1

print(f"  {'layer':>12}  {'both':>6}  {'adg_only':>9}  {'found_only':>11}  {'neither':>8}")
for la in sorted(layer_stats):
    s = layer_stats[la]
    print(f"  {la:>12}  {s['both']:>6}  {s['adg_only']:>9}  {s['found_only']:>11}  {s['neither']:>8}")

print()
print("=== FAN_IN THRESHOLD ANALYSIS ===")
print(f"  Modules with fan_in>0 : {len(fan_in)}")
print()
print(f"  {'thresh':>8}  {'#above':>8}  {'adg_only':>9}  {'found':>7}  {'both':>6}  {'gap_needing_found':>18}")
total = len(prod_set)
for t in [1, 2, 3, 5, 10, 20]:
    above = [p for p in prod_set if fan_in.get(p, 0) >= t]
    adg_o = [p for p in above if covered_by_adg[p] and not covered_by_foundational[p]]
    f_o = [p for p in above if covered_by_foundational[p] and not covered_by_adg[p]]
    bt = [p for p in above if covered_by_adg[p] and covered_by_foundational[p]]
    gap = len(adg_o)  # these need a foundational test
    pct = 100 * len(above) / total
    print(f"  {t:>8}  {len(above):>8} ({pct:4.1f}%)  {len(adg_o):>9}  {len(f_o):>7}  {len(bt):>6}  {gap:>18}")

print()
print("=== TOP 40 HIGH-FAN_IN ADG-ONLY MODULES (priority for foundational tests) ===")
top_gap = sorted(adg_only, key=lambda p: -fan_in.get(p, 0))[:40]
for p in top_gap:
    print(f"  fan_in={fan_in.get(p, 0):>4}  layer={layer_from(p):>12}  {p}")

print()
print("=== TRUE OVERLAP: Both ADG + Foundational (top 30 by fan_in) ===")
top_both = sorted(both, key=lambda p: -fan_in.get(p, 0))[:30]
for p in top_both:
    n_adg = len(covered_by_adg[p])
    n_found = len(covered_by_foundational[p])
    print(f"  fan_in={fan_in.get(p, 0):>4}  adg_tests={n_adg:>2}  found_tests={n_found:>2}  {p}")

print()
print("=== NEITHER (uncovered modules) ===")
print(f"  Total: {len(neither)}")
for p in neither[:20]:
    print(f"  fan_in={fan_in.get(p, 0):>4}  {p}")

# Save output
out = {
    "summary": {
        "total_production": len(prod_set),
        "both": len(both),
        "adg_only": len(adg_only),
        "foundational_only": len(found_only),
        "neither": len(neither),
    },
    "top_adg_only_high_fanin": [
        {"module": p, "fan_in": fan_in.get(p, 0), "layer": layer_from(p)}
        for p in top_gap
    ],
    "true_overlap_both": [
        {
            "module": p,
            "fan_in": fan_in.get(p, 0),
            "adg_test_count": len(covered_by_adg[p]),
            "foundational_test_count": len(covered_by_foundational[p]),
        }
        for p in top_both
    ],
    "neither": [
        {"module": p, "fan_in": fan_in.get(p, 0)} for p in neither
    ],
    "fan_in_threshold": {
        str(t): {
            "modules_above": len([p for p in prod_set if fan_in.get(p, 0) >= t]),
            "adg_only_gap": len([p for p in prod_set if fan_in.get(p, 0) >= t and covered_by_adg[p] and not covered_by_foundational[p]]),
        }
        for t in [1, 2, 3, 5, 10, 20]
    },
}
out_path = ROOT / "tools" / "evidence" / "graph_overlap_audit.json"
out_path.write_text(json.dumps(out, indent=2))
print(f"\n[AUDIT] Saved -> {out_path.relative_to(ROOT)}")
