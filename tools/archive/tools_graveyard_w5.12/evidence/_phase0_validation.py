"""Phase 0 Validation: Compare accelerator report vs SQLite coverage gaps."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

# ── Load accelerator report ───────────────────────────────────────────────────
accel_path = ROOT / "docs/reports/plans/adg_coverage_report_03122026.json"
accel = json.loads(accel_path.read_text(encoding="utf-8"))

gap_summary = accel.get("gap_summary", {})
accel_covered = set(gap_summary.get("covered_modules", []))
accel_covered_count = gap_summary.get("covered_count", 0)
accel_rate = gap_summary.get("coverage_rate", 0)

# Infer total and uncovered
accel_total_inferred = round(accel_covered_count / accel_rate) if accel_rate else 0
accel_gap_inferred = accel_total_inferred - accel_covered_count

print("=== ACCELERATOR REPORT ===")
print(f"  Covered modules:       {accel_covered_count}")
print(f"  Coverage rate:         {accel_rate:.4f} ({accel_rate * 100:.2f}%)")
print(f"  Inferred total:        {accel_total_inferred}")
print(f"  Inferred gap:          {accel_gap_inferred}")

# ── Load SQLite coverage gaps ─────────────────────────────────────────────────
sqlite_path = ROOT / "tools/evidence/coverage_gaps.json"
sqlite_gaps_raw = json.loads(sqlite_path.read_text(encoding="utf-8"))


# Each entry: [layer, "ADG::Module::path/to/file.py"]
def strip_prefix(s):
    return s.replace("ADG::Module::", "")


sqlite_gap_paths = set(strip_prefix(entry[1]) for entry in sqlite_gaps_raw)
sqlite_gap_count = len(sqlite_gap_paths)

print("\n=== SQLITE ANALYSIS ===")
print(f"  Uncovered modules:     {sqlite_gap_count}")

# ── Cross-comparison ──────────────────────────────────────────────────────────
# Modules in SQLite gaps but NOT in accelerator covered (i.e., also gaps in accelerator)
# We need accelerator's UNCOVERED list — we can only infer it from what's NOT in covered
# Instead, compare: SQLite gaps vs accelerator covered
# If a module is in SQLite gaps AND in accelerator covered → accelerator found coverage for it
# If a module is in SQLite gaps AND NOT in accelerator covered → both agree it's a gap

sqlite_gaps_also_covered_by_accel = sqlite_gap_paths & accel_covered
sqlite_gaps_not_in_accel_covered = sqlite_gap_paths - accel_covered

print("\n=== CROSS-COMPARISON ===")
print(f"  SQLite gaps also in accelerator covered:      {len(sqlite_gaps_also_covered_by_accel)}")
print("    → These are FALSE GAPS in SQLite (accelerator found coverage)")
print(f"  SQLite gaps NOT in accelerator covered:       {len(sqlite_gaps_not_in_accel_covered)}")
print("    → Potential true gaps (both agree)")

# ── Modules SQLite calls gaps but accelerator covers ─────────────────────────
print("\n=== FALSE GAPS IN SQLITE (sample 20) ===")
for p in sorted(sqlite_gaps_also_covered_by_accel)[:20]:
    print(f"  {p}")
if len(sqlite_gaps_also_covered_by_accel) > 20:
    print(f"  ... and {len(sqlite_gaps_also_covered_by_accel) - 20} more")

# ── Layer breakdown of SQLite gaps ───────────────────────────────────────────
layer_buckets: dict[str, list] = {}
for layer, raw in sqlite_gaps_raw:
    layer_buckets.setdefault(layer, []).append(strip_prefix(raw))

print("\n=== SQLITE GAPS BY LAYER ===")
for lyr in sorted(layer_buckets, key=lambda k: -len(layer_buckets[k])):
    items = layer_buckets[lyr]
    print(f"  {lyr:<15} {len(items):>4} gaps")

# ── Categorize excluded modules ───────────────────────────────────────────────
# SQLite gaps NOT covered by accelerator — these are the "real" gaps
# Now analyze what patterns appear in SQLite gaps that are NOT production-critical

util_pattern = re.compile(r"L0_routing/scripts/.*_util\.py$")
config_pattern = re.compile(r".*_config\.py$")
data_pattern = re.compile(r"^(data/|artifacts/|archives/|\.backup/|\.healing_backups/)")
ops_pattern = re.compile(r"^ops_scripts/")
tool_pattern = re.compile(r"^tools/")

categories = {
    "l0_scripts_util": [],
    "config_modules": [],
    "data_artifacts": [],
    "ops_scripts": [],
    "tools": [],
    "other": [],
}

for p in sqlite_gap_paths:
    if util_pattern.search(p):
        categories["l0_scripts_util"].append(p)
    elif config_pattern.search(p):
        categories["config_modules"].append(p)
    elif data_pattern.match(p):
        categories["data_artifacts"].append(p)
    elif ops_pattern.match(p):
        categories["ops_scripts"].append(p)
    elif tool_pattern.match(p):
        categories["tools"].append(p)
    else:
        categories["other"].append(p)

print("\n=== SQLITE GAPS CATEGORIZED ===")
total_cat = 0
for cat, items in sorted(categories.items(), key=lambda x: -len(x[1])):
    print(f"  {cat:<25} {len(items):>4}")
    total_cat += len(items)
print(f"  {'TOTAL':<25} {total_cat:>4}")

# ── Production-critical check among excluded ─────────────────────────────────
# Flag L0 util scripts that are imported by production code
# Check for _util.py files that are known critical
critical_utils = [
    "subprocess_runner_util.py",
    "timeout_decorator_util.py",
    "path_util.py",
    "project_root_util.py",
    "core_integrity_util.py",
    "ssot_discovery_util.py",
    "scan_util.py",
    "json_formatter_util.py",
]

print("\n=== CRITICAL UTILS CHECK (are they in SQLite gaps?) ===")
for cu in sorted(critical_utils):
    in_sqlite_gap = any(cu in p for p in sqlite_gap_paths)
    in_accel_covered = any(cu in p for p in accel_covered)
    status = []
    if in_sqlite_gap:
        status.append("IN_SQLITE_GAP")
    if in_accel_covered:
        status.append("IN_ACCEL_COVERED")
    if not status:
        status.append("NOT_TRACKED")
    print(f"  {cu:<45} {' | '.join(status)}")

# ── apps_rg/config check ──────────────────────────────────────────────────────
print("\n=== apps_rg/config MODULES IN SQLITE GAPS ===")
apps_rg_gaps = [
    p
    for p in sqlite_gap_paths
    if p.startswith("apps_rg/") or p.startswith("apps_shared/") or p.startswith("apps_lic/")
]
for p in sorted(apps_rg_gaps)[:20]:
    in_accel = p in accel_covered
    print(f"  {'[ACCEL_COVERED]' if in_accel else '[GAP]':<18} {p}")
if len(apps_rg_gaps) > 20:
    print(f"  ... and {len(apps_rg_gaps) - 20} more")
print(f"  Total apps_*/system_learning gaps: {len(apps_rg_gaps)}")

# ── Guardian reference check ──────────────────────────────────────────────────
print("\n=== HARDCODED COVERAGE THRESHOLDS (from grep results) ===")
print("  coverage_rate 0.4976 found in:")
print("    docs/reports/plans/adg_coverage_report_03122026.json")
print("    docs/reports/plans/ssot_healing_detailed_report.json")
print("    docs/reports/plans/ssot_healing_run_report.json")
print("  → None in .github/workflows/ or tests/ (safe to change definitions)")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n=== PHASE 0 SUMMARY ===")
print(f"  SQLite gap count:                  {sqlite_gap_count}")
print(f"  Accelerator covered count:         {accel_covered_count}")
print(f"  Accelerator inferred gap:          {accel_gap_inferred}")
print(f"  SQLite gaps = FALSE (accel covers):{len(sqlite_gaps_also_covered_by_accel)}")
print(f"  Agreed true gaps (both):           {len(sqlite_gaps_not_in_accel_covered)}")
delta = sqlite_gap_count - accel_gap_inferred
print(f"  Delta (SQLite - Accel inferred):   {delta}")

# Save findings
findings = {
    "sqlite_gap_count": sqlite_gap_count,
    "accel_covered_count": accel_covered_count,
    "accel_coverage_rate": accel_rate,
    "accel_total_inferred": accel_total_inferred,
    "accel_gap_inferred": accel_gap_inferred,
    "false_gaps_in_sqlite": len(sqlite_gaps_also_covered_by_accel),
    "false_gaps_sample": sorted(sqlite_gaps_also_covered_by_accel)[:50],
    "agreed_true_gaps": len(sqlite_gaps_not_in_accel_covered),
    "delta": delta,
    "categories": {k: len(v) for k, v in categories.items()},
    "category_samples": {k: sorted(v)[:10] for k, v in categories.items()},
    "apps_rg_gaps_count": len(apps_rg_gaps),
    "apps_rg_gaps_sample": sorted(apps_rg_gaps)[:20],
    "critical_utils_status": {
        cu: {
            "in_sqlite_gap": any(cu in p for p in sqlite_gap_paths),
            "in_accel_covered": any(cu in p for p in accel_covered),
        }
        for cu in critical_utils
    },
    "ci_cd_references": "NONE - safe to modify",
    "test_references": "NONE - safe to modify",
    "hardcoded_thresholds_in_workflows": "NONE",
}

out_path = ROOT / "docs/reports/plans/phase0_validation_findings.json"
out_path.write_text(json.dumps(findings, indent=2), encoding="utf-8")
print(f"\nFindings saved → {out_path}")
