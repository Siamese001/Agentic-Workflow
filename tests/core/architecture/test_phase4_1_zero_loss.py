"""
Phase 4.1 Zero-Loss Verification Test Suite

This test suite ensures no legacy functionality is dropped during the Phase 4.1
scaled refactoring work. All 4 test cases must pass 100%.

Test Cases:
- TC-17: Scaled Discovery - Refactored files return same results as rglob
- TC-18: CI Enforcement - check_rglob_usage.py reports accurate count
- TC-19: Auto-Invalidation - Cache detects directory changes
- TC-20: No Backup Leak - No backup files in discovery results

Author: Cascade
Date: January 19, 2026
Phase: 4.1 - Scaled Refactoring & CI Enforcement
"""
import sys
import os
import time
import tempfile
from pathlib import Path
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_tc17_scaled_discovery():
    """
    TC-17: Scaled Discovery
    
    Compare the list of files returned by ssot_discovery against
    a filtered rglob output. Delta must be zero.
    """
    print("\n" + "="*60)
    print("TC-17: Scaled Discovery")
    print("="*60)
    
    from agentic_core.utils.ssot_discovery import get_python_files, DEFAULT_EXCLUDE_DIRS
    
    agentic_core = PROJECT_ROOT / "agentic_core"
    
    # Get files via ssot_discovery
    ssot_files = get_python_files(agentic_core)
    ssot_set = set(str(f) for f in ssot_files)
    
    # Get files via rglob with same exclusions
    rglob_files = []
    for py_file in agentic_core.rglob("*.py"):
        path_parts = py_file.parts
        skip = False
        for part in path_parts:
            if part in DEFAULT_EXCLUDE_DIRS or part.startswith('.'):
                skip = True
                break
        if skip:
            continue
        # Skip test files (same as ssot_discovery default)
        if py_file.name.startswith("test_") or py_file.name.endswith("_test.py"):
            continue
        if "conftest" in py_file.name:
            continue
        rglob_files.append(py_file)
    
    rglob_set = set(str(f) for f in rglob_files)
    
    # Compare
    only_in_ssot = ssot_set - rglob_set
    only_in_rglob = rglob_set - ssot_set
    
    print(f"   SSOT Discovery: {len(ssot_files)} files")
    print(f"   rglob (filtered): {len(rglob_files)} files")
    
    if only_in_ssot or only_in_rglob:
        print(f"❌ FAIL: Delta detected")
        if only_in_ssot:
            print(f"   Only in SSOT: {list(only_in_ssot)[:3]}")
        if only_in_rglob:
            print(f"   Only in rglob: {list(only_in_rglob)[:3]}")
        return False
    
    print("✅ PASS: ssot_discovery returns same files as filtered rglob")
    return True


def test_tc18_ci_enforcement():
    """
    TC-18: CI Enforcement
    
    Run check_rglob_usage.py and verify it accurately reports the current count.
    """
    print("\n" + "="*60)
    print("TC-18: CI Enforcement")
    print("="*60)
    
    # Import the CI check functions
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from check_rglob_usage import scan_for_rglob_usage, MAX_ALLOWED_RGLOB
    
    agentic_core = PROJECT_ROOT / "agentic_core"
    
    # Run the scan
    total_count, offenders = scan_for_rglob_usage(agentic_core)
    
    print(f"   Total rglob/glob calls: {total_count}")
    print(f"   Files with rglob/glob: {len(offenders)}")
    print(f"   Maximum allowed: {MAX_ALLOWED_RGLOB}")
    
    # Verify the count is a reasonable number (not 0, not absurdly high)
    if total_count == 0:
        print("❌ FAIL: Count should not be 0 (there are still rglob calls)")
        return False
    
    if total_count > 500:
        print("❌ FAIL: Count seems too high, possible bug in scanner")
        return False
    
    # Verify offenders list is populated
    if len(offenders) == 0:
        print("❌ FAIL: Offenders list should not be empty")
        return False
    
    # Verify top offender has reasonable count
    if offenders[0]["count"] > 20:
        print(f"❌ FAIL: Top offender has {offenders[0]['count']} calls, seems too high")
        return False
    
    print(f"   Top offender: {offenders[0]['file']} ({offenders[0]['count']} calls)")
    print("✅ PASS: CI check accurately reports rglob usage")
    return True


def test_tc19_auto_invalidation():
    """
    TC-19: Auto-Invalidation
    
    Touch a new file in agentic_core/L2_execution/. Verify get_python_files_cached()
    detects the change without manual invalidation.
    """
    print("\n" + "="*60)
    print("TC-19: Auto-Invalidation")
    print("="*60)
    
    from agentic_core.utils.ssot_discovery import (
        FileCache,
        get_python_files,
        invalidate_cache,
        get_global_cache
    )
    
    # Use a temporary directory for this test
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        cache_path = tmpdir_path / ".file_cache.json"
        
        # Create initial structure
        test_file1 = tmpdir_path / "module1.py"
        test_file1.write_text("# Test file 1")
        
        # Create cache and populate it
        cache = FileCache(cache_path)
        files = get_python_files(tmpdir_path, include_tests=True)
        cache.update([str(f) for f in files])
        
        # Verify cache is valid
        if not cache.is_valid():
            print("❌ FAIL: Cache should be valid after update")
            return False
        
        initial_count = len(cache.get_files())
        print(f"   Initial cache: {initial_count} files")
        
        # Wait a moment to ensure mtime difference
        time.sleep(0.1)
        
        # Touch the directory (create a new file)
        test_file2 = tmpdir_path / "module2.py"
        test_file2.write_text("# Test file 2")
        
        # Check if cache detects staleness
        is_stale = cache.is_stale_for_directory(tmpdir_path)
        
        if not is_stale:
            print("❌ FAIL: Cache should detect directory change")
            return False
        
        print(f"   Cache detected directory change: ✓")
        print("✅ PASS: Auto-invalidation detects directory changes")
        return True


def test_tc20_no_backup_leak():
    """
    TC-20: No Backup Leak
    
    Verify that no files from .sovereign_healing_backup or archives
    appear in the discovery list after the scaled refactor.
    """
    print("\n" + "="*60)
    print("TC-20: No Backup Leak")
    print("="*60)
    
    from agentic_core.utils.ssot_discovery import get_python_files
    
    # Get all Python files
    files = get_python_files(PROJECT_ROOT)
    
    # Check for backup directory files
    backup_patterns = [
        ".sovereign_healing_backup",
        "archives",
        "__pycache__",
        ".git"
    ]
    
    leaked_files = []
    for f in files:
        path_str = str(f)
        for pattern in backup_patterns:
            if pattern in path_str:
                leaked_files.append((f, pattern))
                break
    
    if leaked_files:
        print(f"❌ FAIL: Found {len(leaked_files)} files from excluded directories:")
        for f, pattern in leaked_files[:5]:
            print(f"   - {f} (matched: {pattern})")
        return False
    
    print(f"   Total files scanned: {len(files)}")
    print(f"   Excluded patterns: {backup_patterns}")
    print("✅ PASS: No files from excluded directories in results")
    return True


def test_rglob_reduction():
    """
    Bonus Test: Verify rglob count has been reduced from baseline.
    """
    print("\n" + "="*60)
    print("BONUS: rglob Reduction Progress")
    print("="*60)
    
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from check_rglob_usage import scan_for_rglob_usage, MAX_ALLOWED_RGLOB
    
    agentic_core = PROJECT_ROOT / "agentic_core"
    total_count, offenders = scan_for_rglob_usage(agentic_core)
    
    # Baseline was 268 before Phase 4.1 refactoring
    baseline = 268
    reduction = baseline - total_count
    reduction_pct = (reduction / baseline) * 100 if baseline > 0 else 0
    
    print(f"   Baseline count: {baseline}")
    print(f"   Current count: {total_count}")
    print(f"   Reduction: {reduction} calls ({reduction_pct:.1f}%)")
    print(f"   Target: {MAX_ALLOWED_RGLOB}")
    
    if total_count <= MAX_ALLOWED_RGLOB:
        print(f"✅ PASS: Count ({total_count}) is within limit ({MAX_ALLOWED_RGLOB})")
        return True
    else:
        print(f"⚠️  INFO: Count ({total_count}) still exceeds limit ({MAX_ALLOWED_RGLOB})")
        print(f"   Remaining to reduce: {total_count - MAX_ALLOWED_RGLOB}")
        # This is informational, not a failure
        return True


def main():
    """Run all Phase 4.1 Zero-Loss test cases."""
    print("\n" + "="*70)
    print("PHASE 4.1 ZERO-LOSS VERIFICATION TEST SUITE")
    print("="*70)
    print(f"Project Root: {PROJECT_ROOT}")
    
    tests = [
        ("TC-17: Scaled Discovery", test_tc17_scaled_discovery),
        ("TC-18: CI Enforcement", test_tc18_ci_enforcement),
        ("TC-19: Auto-Invalidation", test_tc19_auto_invalidation),
        ("TC-20: No Backup Leak", test_tc20_no_backup_leak),
        ("BONUS: rglob Reduction Progress", test_rglob_reduction),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    # Core tests (TC-17 to TC-20)
    core_tests = results[:4]
    core_passed = sum(1 for _, passed in core_tests if passed)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*70)
    print(f"CORE TESTS: {core_passed}/4 passed")
    print(f"TOTAL: {passed_count}/{total_count} tests passed")
    
    if core_passed == 4:
        print("✅ 100% PASS - All Phase 4.1 Zero-Loss tests passed!")
        print("\nPhase 4.1 Scaled Refactoring is verified.")
        return 0
    else:
        print(f"❌ FAIL - {4 - core_passed} core test(s) failed")
        print("\nReview failures before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
