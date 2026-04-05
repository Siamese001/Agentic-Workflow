"""Step 11: Denominator lock enforcement gate.

Run this BEFORE and AFTER any governance wave to ensure denominators
do not increase. Aborts if any denominator grows.

Usage:
    python tools/denominator_lock_gate.py [--baseline PATH]

Defaults to: artifacts/governance/post_normalization_baseline.json
"""
import argparse
import glob
import json
import os
import sqlite3
import sys

ADG_DIR = r"C:\Git\Agentic-Workflow\artifacts\adg"
GOV_DIR = r"C:\Git\Agentic-Workflow\artifacts\governance"
DEFAULT_BASELINE = os.path.join(GOV_DIR, "post_normalization_baseline.json")

DENOMINATOR_TYPES = ("writes_to", "reads_from", "records_execution_trace", "calls")


def main() -> int:
    parser = argparse.ArgumentParser(description="Denominator lock enforcement gate")
    parser.add_argument("--baseline", default=DEFAULT_BASELINE, help="Baseline JSON path")
    args = parser.parse_args()

    # Load baseline
    if not os.path.exists(args.baseline):
        print(f"ERROR: Baseline not found: {args.baseline}")
        return 1
    with open(args.baseline) as f:
        baseline = json.load(f)

    # Find latest SQLite
    pattern = os.path.join(ADG_DIR, "adg_indexed_*.sqlite")
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"ERROR: No SQLite found matching {pattern}")
        return 1
    db_path = files[-1]

    conn = sqlite3.connect(db_path)
    current = dict(conn.execute(
        "SELECT relation_type, COUNT(*) FROM edges WHERE relation_type IN (?, ?, ?, ?) GROUP BY relation_type",
        DENOMINATOR_TYPES,
    ).fetchall())
    conn.close()

    print(f"Baseline: {args.baseline}")
    print(f"Current:  {db_path}")
    print()

    violations = []
    for rt in DENOMINATOR_TYPES:
        denom_key = "denominators" if "denominators" in baseline else "base_denominators"
        base_val = baseline[denom_key].get(rt, 0)
        curr_val = current.get(rt, 0)
        delta = curr_val - base_val
        status = "OK" if delta <= 0 else "VIOLATION"
        if delta > 0:
            violations.append((rt, base_val, curr_val, delta))
        print(f"  {rt:<30} baseline={base_val:>8,}  current={curr_val:>8,}  delta={delta:>+8,}  {status}")

    print()
    if violations:
        print("DENOMINATOR LOCK FAILED — the following denominators increased:")
        for rt, base, curr, delta in violations:
            print(f"  {rt}: {base:,} -> {curr:,} (+{delta:,})")
        print("\nABORT: Do not proceed with governance wave until denominators are stable.")
        return 1
    else:
        print("DENOMINATOR LOCK PASSED — all denominators stable or reduced.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
