"""Breakdown of Section 2 gaps for convergence report."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
raw = json.load(open(ROOT / "artifacts" / "adg" / "_convergence_analysis_raw.json"))
gaps = raw["s2"]["gaps"]

# By missing relation
by_missing = Counter(g["missing"] for g in gaps)
print("By missing relation:")
for k, v in by_missing.most_common():
    print(f"  {k}: {v}")

# By risk type
by_risk = Counter(g["risk_type"] for g in gaps)
print("\nBy risk type:")
for k, v in by_risk.most_common():
    print(f"  {k}: {v}")

# Categorize gaps by module type
init_gaps = [g for g in gaps if "__init__" in g["module"]]
config_gaps = [g for g in gaps if "config" in g["module"].lower() and "__init__" not in g["module"]]
test_gaps = [g for g in gaps if g["module"].startswith("tests/")]
data_gaps = [g for g in gaps if any(x in g["module"].lower() for x in ["data/", "artifacts/", "golden/"])]

# Functional gaps = everything else
non_functional_modules = set(g["module"] for g in init_gaps + config_gaps + test_gaps + data_gaps)
functional_gaps = [g for g in gaps if g["module"] not in non_functional_modules]

print(f"\n__init__.py gaps: {len(init_gaps)}")
print(f"config file gaps: {len(config_gaps)}")
print(f"test file gaps: {len(test_gaps)}")
print(f"data/artifact gaps: {len(data_gaps)}")
print(f"Functional module gaps: {len(functional_gaps)}")

# Show unique functional modules with critical gaps
func_critical = [g for g in functional_gaps if g["severity"] == "Critical"]
func_crit_modules = sorted(set(g["module"] for g in func_critical))
print(f"\nFunctional Critical gap modules: {len(func_crit_modules)}")
for m in func_crit_modules[:30]:
    missing = sorted(set(g["missing"] for g in func_critical if g["module"] == m))
    print(f"  {m} — missing: {', '.join(missing)}")
if len(func_crit_modules) > 30:
    print(f"  ... and {len(func_crit_modules) - 30} more")

# Dominant missing relation in functional critical
func_crit_missing = Counter(g["missing"] for g in func_critical)
print("\nDominant missing in functional critical:")
for k, v in func_crit_missing.most_common():
    print(f"  {k}: {v}")

# Root cause: agent_executes_agent is missing from almost everything because
# only 112 edges exist in the whole ADG for it
print("\n--- Root Cause Analysis ---")
print(f"agent_executes_agent total edges in ADG: {raw['s1']['runs'][0]['agent_executes_agent']}")
print(f"calls total edges in ADG: {raw['s1']['runs'][0]['calls']}")
print(f"dispatches_healing_run total edges in ADG: {raw['s1']['runs'][0]['dispatches_healing_run']}")

# How many unique modules have agent_executes_agent?
# Check gap vs total modules matched
total_risk_modules = len(set(g["module"] for g in gaps))
print(f"\nTotal high-risk modules analyzed: {total_risk_modules}")
print(f"Total gap entries: {len(gaps)} (multiple gaps per module)")
print(f"Unique modules with gaps: {len(set(g['module'] for g in gaps))}")

# Most important: what percentage of gaps are from agent_executes_agent alone?
axa_gaps = [g for g in gaps if g["missing"] == "agent_executes_agent"]
print(f"\nagent_executes_agent gaps: {len(axa_gaps)} ({len(axa_gaps)/len(gaps)*100:.1f}% of all gaps)")
print(f"Non-agent_executes_agent gaps: {len(gaps) - len(axa_gaps)}")
