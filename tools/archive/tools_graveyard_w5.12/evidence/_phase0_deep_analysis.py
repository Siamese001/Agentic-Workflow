"""Phase 0 Deep Analysis: Classify the 'other' bucket and agreed true gaps."""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

accel = json.loads((ROOT / "docs/reports/plans/adg_coverage_report_03122026.json").read_text(encoding="utf-8"))
gap_summary = accel["gap_summary"]
accel_covered = set(gap_summary["covered_modules"])

sqlite_gaps_raw = json.loads((ROOT / "tools/evidence/coverage_gaps.json").read_text(encoding="utf-8"))

def strip(s):
    return s.replace("ADG::Module::", "")

sqlite_gap_paths = set(strip(e[1]) for e in sqlite_gaps_raw)
layer_map = {strip(e[1]): e[0] for e in sqlite_gaps_raw}

# ── Agreed true gaps (in SQLite gap AND not in accel covered) ─────────────────
agreed_true_gaps = sqlite_gap_paths - accel_covered
# False gaps in SQLite (SQLite called gap but accel covers them = covered modules)
false_gaps = sqlite_gap_paths & accel_covered

print(f"Agreed true gaps: {len(agreed_true_gaps)}")
print(f"False gaps (SQLite wrong): {len(false_gaps)}")

# ── Deep classify all SQLite gap paths ───────────────────────────────────────
PATTERNS = [
    ("l0_scripts_util",      re.compile(r'L0_routing/scripts/.*_util\.py$')),
    ("l0_scripts_runner",    re.compile(r'L0_routing/scripts/run_')),
    ("l0_scripts_verify",    re.compile(r'L0_routing/scripts/verify_')),
    ("l0_scripts_other",     re.compile(r'L0_routing/scripts/')),
    ("l0_utils",             re.compile(r'L0_routing/utils/')),
    ("l0_types",             re.compile(r'L0_routing/types/')),
    ("l0_seams",             re.compile(r'L0_routing/seams/')),
    ("l0_enforcement",       re.compile(r'L0_routing/enforcement/')),
    ("l0_engines",           re.compile(r'L0_routing/engines/')),
    ("l0_meta_control",      re.compile(r'L0_routing/meta_control/')),
    ("l0_reasoning",         re.compile(r'L0_routing/reasoning/')),
    ("l0_other",             re.compile(r'agentic_core/L0')),
    ("l1_all",               re.compile(r'agentic_core/L1')),
    ("l2_all",               re.compile(r'agentic_core/L2')),
    ("l3_all",               re.compile(r'agentic_core/L3')),
    ("l4_all",               re.compile(r'agentic_core/L4')),
    ("l5_all",               re.compile(r'agentic_core/L5')),
    ("l6_all",               re.compile(r'agentic_core/L6')),
    ("adg_all",              re.compile(r'agentic_core/adg')),
    ("adg_cache_runtime",    re.compile(r'agentic_core/(cache|runtime)')),
    ("adg_enforcement",      re.compile(r'agentic_core/enforcement')),
    ("adg_utils_types",      re.compile(r'agentic_core/(utils|types)')),
    ("apps_lic_reasoning",   re.compile(r'apps_lic/reasoning/')),
    ("apps_lic_other",       re.compile(r'apps_lic/')),
    ("apps_rg_reasoning",    re.compile(r'apps_rg/reasoning/')),
    ("apps_rg_engines",      re.compile(r'apps_rg/engines/')),
    ("apps_rg_other",        re.compile(r'apps_rg/')),
    ("apps_shared",          re.compile(r'apps_shared/')),
    ("system_learning",      re.compile(r'system_learning/')),
    ("ops_scripts",          re.compile(r'ops_scripts/')),
    ("tools",                re.compile(r'^tools/')),
    ("data",                 re.compile(r'^data/')),
    ("root_level",           re.compile(r'^[^/]+\.py$')),
]

def classify(path):
    for label, pat in PATTERNS:
        if pat.search(path):
            return label
    return "unclassified"

# Classify all SQLite gaps
cat_counts = defaultdict(int)
cat_examples = defaultdict(list)
for p in sorted(sqlite_gap_paths):
    c = classify(p)
    cat_counts[c] += 1
    if len(cat_examples[c]) < 8:
        cat_examples[c].append(p)

print("\n=== ALL SQLITE GAPS CLASSIFIED ===")
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
    print(f"  {cat:<30} {count:>4}")

# ── Classify agreed true gaps (actionable) ────────────────────────────────────
true_gap_cats = defaultdict(int)
true_gap_examples = defaultdict(list)
for p in sorted(agreed_true_gaps):
    c = classify(p)
    true_gap_cats[c] += 1
    if len(true_gap_examples[c]) < 8:
        true_gap_examples[c].append(p)

print("\n=== AGREED TRUE GAPS (966) CLASSIFIED ===")
for cat, count in sorted(true_gap_cats.items(), key=lambda x: -x[1]):
    print(f"  {cat:<30} {count:>4}")
    for ex in true_gap_examples[cat][:3]:
        print(f"    {ex}")

# ── Production-criticality check on true gaps ─────────────────────────────────
# Check actual file existence on disk for true gaps
print("\n=== TRUE GAPS: FILE EXISTS ON DISK? (sample 30) ===")
exists_count = 0
missing_count = 0
missing_samples = []
for p in sorted(agreed_true_gaps)[:100]:
    full = ROOT / p
    if full.exists():
        exists_count += 1
    else:
        missing_count += 1
        missing_samples.append(p)

print(f"  First 100 true gaps: {exists_count} exist on disk, {missing_count} missing")
if missing_samples:
    print("  Missing (phantom modules):")
    for m in missing_samples[:10]:
        print(f"    {m}")

# Check all true gaps for disk existence
all_exist = sum(1 for p in agreed_true_gaps if (ROOT / p).exists())
all_missing = len(agreed_true_gaps) - all_exist
print(f"\n  ALL {len(agreed_true_gaps)} true gaps: {all_exist} exist, {all_missing} phantom/missing")

# ── False gap analysis: what did SQLite miss that accel found covered? ─────────
print("\n=== WHY SQLITE PRODUCED FALSE GAPS (1031 modules it called uncovered) ===")
false_gap_cats = defaultdict(int)
for p in sorted(false_gaps):
    c = classify(p)
    false_gap_cats[c] += 1

print("  Category breakdown of false gaps:")
for cat, count in sorted(false_gap_cats.items(), key=lambda x: -x[1]):
    print(f"    {cat:<30} {count:>4}")

# Root cause: SQLite counts DISTINCT dst_id from GT_covers edges
# Accelerator may use import-graph coverage (if A imports B, B is transitively covered)
# OR accelerator uses a different edge type / scans test file imports directly
print("\n  HYPOTHESIS: SQLite uses only direct 'covers' edges.")
print("  Accelerator likely includes TRANSITIVE coverage via import chains.")
print("  → A test that imports path_constants.py transitively covers all its imports.")

# ── apps_lic/reasoning agents — are they production? ─────────────────────────
print("\n=== apps_lic/reasoning AGENTS (production check) ===")
lic_reasoning = [p for p in agreed_true_gaps if "apps_lic/reasoning/" in p]
print(f"  Count: {len(lic_reasoning)}")
for p in sorted(lic_reasoning)[:15]:
    full = ROOT / p
    print(f"  {'EXISTS' if full.exists() else 'MISSING':<8} {p}")

# ── system_learning gaps ──────────────────────────────────────────────────────
print("\n=== system_learning TRUE GAPS ===")
sl_gaps = [p for p in agreed_true_gaps if p.startswith("system_learning/")]
print(f"  Count: {len(sl_gaps)}")
for p in sorted(sl_gaps)[:15]:
    full = ROOT / p
    print(f"  {'EXISTS' if full.exists() else 'MISSING':<8} {p}")

# ── L5 gaps (323 total in SQLite) ─────────────────────────────────────────────
print("\n=== L5 TRUE GAPS (sample) ===")
l5_true = [p for p in agreed_true_gaps if "agentic_core/L5" in p]
print(f"  Count: {len(l5_true)}")
for p in sorted(l5_true)[:15]:
    full = ROOT / p
    print(f"  {'EXISTS' if full.exists() else 'MISSING':<8} {p}")

# ── Save deep findings ────────────────────────────────────────────────────────
deep = {
    "agreed_true_gaps_total": len(agreed_true_gaps),
    "false_gaps_total": len(false_gaps),
    "true_gap_categories": dict(sorted(true_gap_cats.items(), key=lambda x: -x[1])),
    "true_gap_category_samples": {k: v for k, v in true_gap_examples.items()},
    "false_gap_categories": dict(sorted(false_gap_cats.items(), key=lambda x: -x[1])),
    "disk_existence": {
        "exist_on_disk": all_exist,
        "phantom_missing": all_missing,
    },
    "apps_lic_reasoning_true_gaps": sorted(lic_reasoning),
    "system_learning_true_gaps": sorted(sl_gaps),
    "l5_true_gaps_count": len(l5_true),
    "l5_true_gaps_sample": sorted(l5_true)[:20],
    "hypothesis_false_gap_root_cause": (
        "SQLite counts only direct ADG 'covers' edges. "
        "Accelerator likely uses transitive import-graph coverage or "
        "broader edge types, causing 1,031 modules to appear covered "
        "in accelerator but uncovered in SQLite."
    ),
}

out = ROOT / "docs/reports/plans/phase0_deep_analysis.json"
out.write_text(json.dumps(deep, indent=2), encoding="utf-8")
print(f"\nDeep analysis saved → {out}")
