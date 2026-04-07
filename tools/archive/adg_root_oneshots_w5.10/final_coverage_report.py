"""Final coverage report after stub cleanup and new stub generation."""

import argparse
import glob
import sqlite3
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

db = sorted(glob.glob(str(PROJECT_ROOT / "artifacts/adg/adg_indexed_*.sqlite")))[-1]
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

# Source modules (unique .py files only, no ::ClassName variants)
src_rows = list(
    conn.execute(
        "SELECT DISTINCT resolved_path FROM nodes "
        "WHERE entity_type='module' "
        "AND resolved_path LIKE 'agentic_core/%' "
        "AND resolved_path NOT LIKE '%__pycache__%' "
        "AND resolved_path NOT LIKE '%::%'",
    ),
)
src_mods = {r["resolved_path"] for r in src_rows}

# Covered src modules (any test imports them)
cov_rows = list(
    conn.execute(
        "SELECT DISTINCT n2.resolved_path as src_file "
        "FROM edges e "
        "JOIN nodes n1 ON e.src_id=n1.id "
        "JOIN nodes n2 ON e.dst_id=n2.id "
        "WHERE e.relation_type='imports' "
        "AND n1.resolved_path LIKE 'tests/%' "
        "AND n2.resolved_path LIKE 'agentic_core/%' "
        "AND n2.resolved_path NOT LIKE '%__pycache__%'",
    ),
)
covered_raw = {r["src_file"].split("::")[0] for r in cov_rows}
covered = covered_raw & src_mods

# Coverage split by test type
test_to_covered = defaultdict(set)
for r in conn.execute(
    "SELECT DISTINCT n1.resolved_path as test_file, n2.resolved_path as src_file "
    "FROM edges e "
    "JOIN nodes n1 ON e.src_id=n1.id "
    "JOIN nodes n2 ON e.dst_id=n2.id "
    "WHERE e.relation_type='imports' "
    "AND n1.resolved_path LIKE 'tests/%' "
    "AND n2.resolved_path LIKE 'agentic_core/%' "
    "AND n2.resolved_path NOT LIKE '%__pycache__%'",
):
    src = r["src_file"].split("::")[0]
    if src in src_mods:
        test_to_covered[r["test_file"]].add(src)

stub_files = [tf for tf in test_to_covered if Path(tf).stem.endswith("_adg")]
non_stub_files = [tf for tf in test_to_covered if not Path(tf).stem.endswith("_adg")]

non_stub_covered = set()
for tf in non_stub_files:
    non_stub_covered |= test_to_covered[tf]

stub_only_covered = covered - non_stub_covered
uncovered = src_mods - covered

# Stub redundancy
redundant_stubs = [tf for tf in stub_files if test_to_covered[tf] <= non_stub_covered]
useful_stubs = [tf for tf in stub_files if test_to_covered[tf] - non_stub_covered]


# Layer breakdown
def layer_of(path):
    """Extract layer name from a module path.

    Args:
        path: Module path like 'agentic_core/L1_cognition/module.py'

    Returns:
        Layer name (e.g., 'L1_cognition') or 'unknown' if not found.
    """
    parts = path.split("/")
    if len(parts) >= 2:
        return parts[1]
    return "unknown"


uncovered_by_layer = defaultdict(list)
for m in sorted(uncovered):
    uncovered_by_layer[layer_of(m)].append(m)

stub_only_by_layer = defaultdict(list)
for m in sorted(stub_only_covered):
    stub_only_by_layer[layer_of(m)].append(m)

print("=" * 60)
print("FINAL COVERAGE REPORT (post stub cleanup + new stubs)")
print("=" * 60)
print(f"ADG DB: {Path(db).name}")
print()
print("SOURCE MODULES")
print(f"  Total unique .py files:          {len(src_mods)}")
pct_covered = 100 * len(covered) / len(src_mods)
print(f"  Covered by any test:             {len(covered)}  ({pct_covered:.1f}%)")
print(
    f"  Covered behavioral only:         {len(non_stub_covered)}  "
    f"({100 * len(non_stub_covered) / len(src_mods):.1f}%)",
)
print(
    f"  Covered by stubs only:           {len(stub_only_covered)}  "
    f"({100 * len(stub_only_covered) / len(src_mods):.1f}%)",
)
pct_uncovered = 100 * len(uncovered) / len(src_mods)
print(f"  Uncovered (no test):             {len(uncovered)}  ({pct_uncovered:.1f}%)")
print()
print("TEST FILES")
print(f"  Total ADG stub files:            {len(stub_files)}")
print(f"    Redundant (safe to delete):    {len(redundant_stubs)}")
print(f"    Useful (unique coverage):      {len(useful_stubs)}")
print(f"  Total behavioral test files:     {len(non_stub_files)}")
print()
print(f"UNCOVERED MODULES BY LAYER ({len(uncovered)} total):")
for layer, mods in sorted(uncovered_by_layer.items(), key=lambda x: -len(x[1])):
    print(f"  {layer}: {len(mods)}")
print()
print(f"STUB-ONLY MODULES BY LAYER ({len(stub_only_covered)} total - need behavioral tests):")
for layer, mods in sorted(stub_only_by_layer.items(), key=lambda x: -len(x[1])):
    print(f"  {layer}: {len(mods)}")

conn.close()


def main():
    """Main entry point for CLI usage."""
    parser = argparse.ArgumentParser(description="Generate final ADG coverage report")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.parse_args()

    # Report is already generated above at module load time


if __name__ == "__main__":
    main()
