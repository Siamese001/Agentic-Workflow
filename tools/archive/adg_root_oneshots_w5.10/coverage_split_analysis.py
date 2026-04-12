"""
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_1")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_2")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_3")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_4")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_5")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_6")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_7")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_8")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_9")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_10")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_11")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_12")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_13")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_14")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_15")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_16")
_emit_reads_through("l4", "coverage_split_analysis", "urg_read_17")
ADG Coverage Split Analysis
============================
Detailed breakdown of:
1. Which test files are _adg vs non-_adg
2. What each category covers
3. Which _adg tests cover things ONLY because they import the module to check importability
4. Whether the ADG/non-ADG split is sensible
5. Full uncovered module list by layer
"""

from __future__ import annotations

import glob
import sqlite3
from collections import defaultdict
from pathlib import Path


def main() -> None:
    db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    # -----------------------------------------------------------------------
    # Source modules
    # -----------------------------------------------------------------------
    src_mods = {
        r["resolved_path"]
        for r in conn.execute(
            "SELECT resolved_path FROM nodes "
            "WHERE entity_type='module' "
            "AND resolved_path LIKE 'agentic_core/%' "
            "AND resolved_path NOT LIKE '%__pycache__%' ",
        )
    }
    print(f"Total agentic_core source modules: {len(src_mods)}")

    # -----------------------------------------------------------------------
    # All test files + what they import from agentic_core
    # -----------------------------------------------------------------------
    cov_rows = list(
        conn.execute(
            "SELECT DISTINCT n1.resolved_path as test_file, n2.resolved_path as src_file "
            "FROM edges e "
            "JOIN nodes n1 ON e.src_id=n1.id "
            "JOIN nodes n2 ON e.dst_id=n2.id "
            "WHERE e.relation_type='imports' "
            "AND n1.resolved_path LIKE 'tests/%' "
            "AND n2.resolved_path LIKE 'agentic_core/%' "
            "AND n2.resolved_path NOT LIKE '%__pycache__%' ",
        ),
    )

    # Map: test_file -> set of src modules (strip ::ClassName suffixes)
    test_to_covered: dict[str, set[str]] = defaultdict(set)
    for r in cov_rows:
        sf = r["src_file"].split("::")[0]
        if sf in src_mods:
            test_to_covered[r["test_file"]].add(sf)

    # -----------------------------------------------------------------------
    # Split test files by category
    # -----------------------------------------------------------------------
    def category(tf: str) -> str:
        p = tf.lower()
        if "_adg" in Path(tf).stem:
            return "adg_stub"
        if "tests/guardian/" in tf:
            return "guardian"
        if "tests/unit/" in tf:
            return "unit"
        if "tests/integration/" in tf:
            return "integration"
        return "other"

    by_cat: dict[str, list[str]] = defaultdict(list)
    for tf in test_to_covered:
        by_cat[category(tf)].append(tf)

    print("\n=== Test file categories ===")
    for cat, files in sorted(by_cat.items()):
        covered_srcs = set()
        for tf in files:
            covered_srcs |= test_to_covered[tf]
        print(f"  {cat:20s}: {len(files):4d} files  |  {len(covered_srcs):5d} unique src modules covered")

    # -----------------------------------------------------------------------
    # ADG stubs: how many cover src modules NOT covered by non-stub tests?
    # -----------------------------------------------------------------------
    stub_files = by_cat["adg_stub"]
    non_stub_files = [tf for tf in test_to_covered if category(tf) != "adg_stub"]

    stub_covered: set[str] = set()
    non_stub_covered: set[str] = set()
    for tf in stub_files:
        stub_covered |= test_to_covered[tf]
    for tf in non_stub_files:
        non_stub_covered |= test_to_covered[tf]

    stub_only = stub_covered - non_stub_covered
    print("\n=== ADG stub analysis ===")
    print(f"  Stub-only coverage (modules ONLY covered by _adg stubs): {len(stub_only)}")
    print(
        f"  Also covered by behavioral tests:                        {len(stub_covered & non_stub_covered)}",
    )

    # Are stubs redundant? (stub covers something already covered by behavioral)
    redundant_stubs = [tf for tf in stub_files if test_to_covered[tf] <= non_stub_covered]
    useful_stubs = [tf for tf in stub_files if test_to_covered[tf] - non_stub_covered]
    print(f"  Stub files that add ZERO unique coverage:                {len(redundant_stubs)}")
    print(f"  Stub files that add unique coverage:                     {len(useful_stubs)}")

    if redundant_stubs:
        print("\n  Fully-redundant ADG stubs (sample):")
        for tf in sorted(redundant_stubs)[:20]:
            print(f"    {tf}")

    # -----------------------------------------------------------------------
    # Modules only covered by stubs — these need real tests
    # -----------------------------------------------------------------------
    print(f"\n=== Stub-only covered modules (need real behavioral tests): {len(stub_only)} ===")
    by_layer: dict[str, list[str]] = defaultdict(list)
    for p in sorted(stub_only):
        layer = p.split("/")[1] if "/" in p else "?"
        by_layer[layer].append(p)
    for layer in sorted(by_layer):
        mods = by_layer[layer]
        print(f"  [{layer}] {len(mods)}")
        for m in mods[:8]:
            print(f"    {m}")
        if len(mods) > 8:
            print(f"    ... +{len(mods) - 8} more")

    # -----------------------------------------------------------------------
    # Fully uncovered modules
    # -----------------------------------------------------------------------
    all_covered = stub_covered | non_stub_covered
    uncovered = src_mods - all_covered
    print(f"\n=== Fully uncovered modules: {len(uncovered)} ===")
    by_layer2: dict[str, list[str]] = defaultdict(list)
    for p in sorted(uncovered):
        layer = p.split("/")[1] if "/" in p else "?"
        by_layer2[layer].append(p)
    for layer in sorted(by_layer2):
        mods = by_layer2[layer]
        print(f"  [{layer}] {len(mods)}")
        for m in mods[:15]:
            print(f"    {m}")
        if len(mods) > 15:
            print(f"    ... +{len(mods) - 15} more")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    pct_total = 100.0 * len(all_covered) / len(src_mods)
    pct_behavioral = 100.0 * len(non_stub_covered) / len(src_mods)
    print("\n=== COVERAGE SUMMARY ===")
    print(f"  Total source modules:           {len(src_mods)}")
    print(f"  Covered (any test):             {len(all_covered):5d}  ({pct_total:.1f}%)")
    print(f"  Covered (behavioral only):      {len(non_stub_covered):5d}  ({pct_behavioral:.1f}%)")
    print(f"  Covered by stubs only:          {len(stub_only):5d}")
    print(f"  Uncovered (no test at all):     {len(uncovered):5d}  ({100 - pct_total:.1f}%)")

    conn.close()


if __name__ == "__main__":
    main()


def analyze_split():
    return {}
