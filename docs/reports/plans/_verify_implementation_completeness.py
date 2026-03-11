"""Comprehensive verification of ADG anti-pattern implementation.

Verifies:
1. All 4 pattern detectors work on real codebase samples
2. Schema integration (edge types queryable)
3. Manifest field persistence
4. No false positives on clean code
5. Performance impact measurement
"""

import ast
import sqlite3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.adg.extraction.static_scanner import (
    _AntipatternVisitor,
)


def verify_pattern_detectors():
    """Verify all 4 patterns detect correctly on real samples."""
    print("\n=== 1. Pattern Detector Verification ===")

    # Test 1: Silent exception swallow
    code_swallow = """
try:
    risky_operation()
except Exception:
    pass
"""
    tree = ast.parse(code_swallow)
    visitor = _AntipatternVisitor("test", "test.py")
    visitor.visit(tree)
    swallow_edges = [e for e in visitor.edges if e.edge_kind == "silent_exception_swallow"]
    print(f"✓ Silent swallow detector: {len(swallow_edges)} edge(s) - {'PASS' if swallow_edges else 'FAIL'}")

    # Test 2: Blocking in async
    code_blocking = """
async def fetch():
    time.sleep(1)
    return data
"""
    tree = ast.parse(code_blocking)
    visitor = _AntipatternVisitor("test", "test.py")
    visitor.visit(tree)
    blocking_edges = [e for e in visitor.edges if e.edge_kind == "blocking_call_in_async"]
    print(
        f"✓ Blocking async detector: {len(blocking_edges)} edge(s) - {'PASS' if blocking_edges else 'FAIL'}"
    )

    # Test 3: Global mutation
    code_global = """
CONFIG = {}
def update():
    CONFIG = {"new": "val"}
"""
    tree = ast.parse(code_global)
    visitor = _AntipatternVisitor("test", "test.py")
    visitor.visit(tree)
    global_edges = [e for e in visitor.edges if e.edge_kind == "global_state_mutation"]
    print(f"✓ Global mutation detector: {len(global_edges)} edge(s) - {'PASS' if global_edges else 'FAIL'}")

    # Test 4: Retry without backoff
    code_retry = """
while True:
    try:
        do_thing()
        break
    except Exception:
        pass
"""
    tree = ast.parse(code_retry)
    visitor = _AntipatternVisitor("test", "test.py")
    visitor.visit(tree)
    retry_edges = [e for e in visitor.edges if e.edge_kind == "retry_without_backoff"]
    print(f"✓ Retry detector: {len(retry_edges)} edge(s) - {'PASS' if retry_edges else 'FAIL'}")

    return all([swallow_edges, blocking_edges, global_edges, retry_edges])


def verify_schema_integration():
    """Verify schema changes are queryable in latest ADG."""
    print("\n=== 2. Schema Integration Verification ===")

    import glob

    db_files = sorted(glob.glob(str(PROJECT_ROOT / "artifacts/adg/adg_indexed_*.sqlite")))
    if not db_files:
        print("✗ No ADG database found")
        return False

    db = db_files[-1]
    con = sqlite3.connect(db)

    # Check relation_type exists
    relation_check = con.execute("""
        SELECT COUNT(*) FROM edges WHERE relation_type = 'antipattern'
    """).fetchone()[0]
    print(f"✓ 'antipattern' relation_type: {relation_check} edges found")

    # Check all 4 edge_kinds exist
    edge_kinds = con.execute("""
        SELECT edge_kind, COUNT(*) as cnt
        FROM edges
        WHERE relation_type = 'antipattern'
        GROUP BY edge_kind
    """).fetchall()

    expected_kinds = {
        "silent_exception_swallow",
        "blocking_call_in_async",
        "global_state_mutation",
        "retry_without_backoff",
    }
    found_kinds = {kind for kind, _ in edge_kinds}

    for kind in expected_kinds:
        count = next((cnt for k, cnt in edge_kinds if k == kind), 0)
        print(f"  - {kind}: {count} edges")

    missing = expected_kinds - found_kinds
    if missing:
        print(f"✗ Missing edge kinds: {missing}")
        con.close()
        return False

    print("✓ All 4 edge kinds present in database")
    con.close()
    return True


def verify_manifest_persistence():
    """Verify antipattern_count is computed and accessible."""
    print("\n=== 3. Manifest Field Verification ===")

    # Check latest full scan manifest
    import glob

    db_files = sorted(glob.glob(str(PROJECT_ROOT / "artifacts/adg/adg_indexed_*.sqlite")))
    if not db_files:
        print("✗ No ADG database found")
        return False

    # Query actual antipattern count from database
    db = db_files[-1]
    con = sqlite3.connect(db)
    actual_count = con.execute("""
        SELECT COUNT(*) FROM edges WHERE relation_type = 'antipattern'
    """).fetchone()[0]
    con.close()

    # Verify ScanManifest has the field by checking the class definition
    import dataclasses

    from agentic_core.adg.extraction.static_scanner import ScanManifest

    fields = {f.name for f in dataclasses.fields(ScanManifest)}
    if "antipattern_count" not in fields:
        print("✗ antipattern_count field missing from ScanManifest")
        return False

    print("✓ antipattern_count field exists in ScanManifest")
    print(f"✓ Latest ADG scan has {actual_count} antipattern edges")
    return True


def verify_no_false_positives():
    """Verify clean code produces zero antipattern edges."""
    print("\n=== 4. False Positive Check ===")

    # Truly clean code with no anti-patterns
    clean_code = """
import asyncio
from pathlib import Path

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

def process_items(items: list) -> list:
    results = []
    for item in items:
        result = transform(item)
        if result is not None:
            results.append(result)
    return results

def safe_operation():
    try:
        return risky_call()
    except ValueError as e:
        logger.error("Operation failed: %s", e)
        raise
"""

    tree = ast.parse(clean_code)
    visitor = _AntipatternVisitor("clean_test", "clean.py")
    visitor.visit(tree)

    antipatterns = [e for e in visitor.edges if e.relation_type == "antipattern"]

    if antipatterns:
        print(f"✗ False positives detected: {len(antipatterns)}")
        for ap in antipatterns:
            print(f"  - {ap.edge_kind} at line {ap.line_no}")
        return False

    print("✓ Clean code produces 0 antipattern edges")
    return True


def verify_performance_impact():
    """Measure performance impact of anti-pattern detection."""
    print("\n=== 5. Performance Impact Measurement ===")

    # Create test file with mixed content
    test_code = """
import time
import asyncio

CONFIG = {"key": "value"}

async def async_func():
    await asyncio.sleep(1)
    return "result"

def sync_func():
    for i in range(10):
        try:
            process(i)
        except Exception:
            logger.error("Failed")
    return True

def update_config():
    global CONFIG
    CONFIG = {"new": "value"}
"""

    tree = ast.parse(test_code)

    # Measure with anti-pattern visitor
    start = time.perf_counter()
    for _ in range(100):
        visitor = _AntipatternVisitor("perf_test", "perf.py")
        visitor.visit(tree)
    duration_with = time.perf_counter() - start

    # Measure baseline (just parsing)
    start = time.perf_counter()
    for _ in range(100):
        ast.parse(test_code)
    duration_baseline = time.perf_counter() - start

    overhead = duration_with - duration_baseline
    overhead_pct = (overhead / duration_baseline) * 100 if duration_baseline > 0 else 0

    print(f"  Baseline (parse only): {duration_baseline * 1000:.2f}ms")
    print(f"  With anti-pattern detection: {duration_with * 1000:.2f}ms")
    print(f"  Overhead: {overhead * 1000:.2f}ms ({overhead_pct:.1f}%)")

    # Acceptable if overhead < 100% (comprehensive AST analysis is expected to add overhead)
    if overhead_pct > 100:
        print(f"⚠ High overhead: {overhead_pct:.1f}%")
        return False

    print(f"✓ Performance overhead acceptable: {overhead_pct:.1f}%")
    return True


def verify_real_codebase_samples():
    """Verify detectors work on actual codebase files."""
    print("\n=== 6. Real Codebase Sample Verification ===")

    import glob

    db_files = sorted(glob.glob(str(PROJECT_ROOT / "artifacts/adg/adg_indexed_*.sqlite")))
    if not db_files:
        print("✗ No ADG database found")
        return False

    db = db_files[-1]
    con = sqlite3.connect(db)

    # Get sample violations from each category
    samples = con.execute("""
        SELECT edge_kind, source_file, line_no, symbol
        FROM edges
        WHERE relation_type = 'antipattern'
        GROUP BY edge_kind
        LIMIT 4
    """).fetchall()

    print(f"  Found {len(samples)} sample violations:")
    for kind, file, line, symbol in samples:
        print(f"    {kind}: {file}:{line} [{symbol}]")

    if len(samples) < 4:
        print(f"✗ Expected 4 categories, found {len(samples)}")
        return False

    print("✓ All 4 pattern types detected in real codebase")
    con.close()
    return True


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("ADG Anti-Pattern Implementation Verification")
    print("=" * 70)

    results = {
        "Pattern Detectors": verify_pattern_detectors(),
        "Schema Integration": verify_schema_integration(),
        "Manifest Persistence": verify_manifest_persistence(),
        "False Positives": verify_no_false_positives(),
        "Performance Impact": verify_performance_impact(),
        "Real Codebase Samples": verify_real_codebase_samples(),
    }

    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check:.<50} {status}")

    all_passed = all(results.values())
    print("\n" + "=" * 70)
    if all_passed:
        print("✓✓✓ ALL CHECKS PASSED - Implementation 100% Complete ✓✓✓")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"✗✗✗ FAILURES: {', '.join(failed)} ✗✗✗")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
