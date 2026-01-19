"""
Phase 4 Zero-Loss Verification Test Suite

This test suite ensures no legacy functionality is dropped during the Phase 4
performance hardening work. All 4 test cases must pass 100%.

Test Cases:
- TC-13: Cache Accuracy - Invalidate removes deleted files from cache
- TC-14: Exclusion Integrity - No backup files in cached results
- TC-15: Performance Delta - Cached version >90% faster than rglob
- TC-16: Refactor Parity - ssot_discovery returns same files as rglob

Author: Cascade
Date: January 19, 2026
Phase: 4 - Performance Hardening (rglob Elimination)
"""
import sys
import time
import tempfile
from pathlib import Path
from typing import Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_tc13_cache_accuracy():
    """
    TC-13: Cache Accuracy
    
    Verify that deleting a file and calling invalidate() results in the
    file being removed from the get_python_files() output.
    """
    print("\n" + "="*60)
    print("TC-13: Cache Accuracy")
    print("="*60)
    
    from agentic_core.utils.ssot_discovery import FileCache, get_python_files
    
    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        cache_path = tmpdir_path / ".file_cache.json"
        
        # Create test Python files
        test_file1 = tmpdir_path / "test_module1.py"
        test_file2 = tmpdir_path / "test_module2.py"
        test_file1.write_text("# Test file 1")
        test_file2.write_text("# Test file 2")
        
        # Create cache and populate it
        cache = FileCache(cache_path)
        files = get_python_files(tmpdir_path, include_tests=True)
        cache.update([str(f) for f in files])
        
        # Verify both files are in cache
        cached_files = cache.get_files()
        cached_names = [f.name for f in cached_files]
        
        if "test_module1.py" not in cached_names or "test_module2.py" not in cached_names:
            print(f"❌ FAIL: Initial cache should contain both test files")
            print(f"   Cached: {cached_names}")
            return False
        
        print(f"   Initial cache: {len(cached_files)} files")
        
        # Delete one file
        test_file1.unlink()
        
        # Invalidate cache
        cache.invalidate()
        
        # Verify cache is invalid
        if cache.is_valid():
            print("❌ FAIL: Cache should be invalid after invalidate()")
            return False
        
        # Re-scan and update cache
        files_after = get_python_files(tmpdir_path, include_tests=True)
        cache.update([str(f) for f in files_after])
        
        # Verify deleted file is not in new cache
        cached_after = cache.get_files()
        cached_names_after = [f.name for f in cached_after]
        
        if "test_module1.py" in cached_names_after:
            print("❌ FAIL: Deleted file should not be in cache after invalidate + rescan")
            return False
        
        if "test_module2.py" not in cached_names_after:
            print("❌ FAIL: Remaining file should still be in cache")
            return False
        
        print(f"   After delete + invalidate: {len(cached_after)} files")
        print("✅ PASS: Cache correctly reflects file deletion after invalidate()")
        return True


def test_tc14_exclusion_integrity():
    """
    TC-14: Exclusion Integrity
    
    Explicitly verify that NO files from .sovereign_healing_backup/
    are present in the cached results.
    """
    print("\n" + "="*60)
    print("TC-14: Exclusion Integrity")
    print("="*60)
    
    from agentic_core.utils.ssot_discovery import get_python_files, DEFAULT_EXCLUDE_DIRS
    
    # Get all Python files
    files = get_python_files(PROJECT_ROOT)
    
    # Check for backup directory files
    backup_files = []
    excluded_patterns = [".sovereign_healing_backup", "archives", "__pycache__", ".git"]
    
    for f in files:
        path_str = str(f)
        for pattern in excluded_patterns:
            if pattern in path_str:
                backup_files.append(f)
                break
    
    if backup_files:
        print(f"❌ FAIL: Found {len(backup_files)} files from excluded directories:")
        for f in backup_files[:5]:
            print(f"   - {f}")
        return False
    
    # Verify DEFAULT_EXCLUDE_DIRS contains expected patterns
    expected_excludes = {".sovereign_healing_backup", "archives", "__pycache__", ".git"}
    missing_excludes = expected_excludes - DEFAULT_EXCLUDE_DIRS
    
    if missing_excludes:
        print(f"❌ FAIL: DEFAULT_EXCLUDE_DIRS missing: {missing_excludes}")
        return False
    
    print(f"✅ PASS: No files from excluded directories in results")
    print(f"   Total files: {len(files)}")
    print(f"   Excluded patterns: {excluded_patterns}")
    return True


def test_tc15_performance_delta():
    """
    TC-15: Performance Delta
    
    Compare the time for 10 consecutive calls of get_python_files() (cached)
    vs 10 rglob calls. The cached version must be >90% faster.
    """
    print("\n" + "="*60)
    print("TC-15: Performance Delta")
    print("="*60)
    
    from agentic_core.utils.ssot_discovery import (
        get_python_files, 
        get_cached_python_files,
        invalidate_cache,
        DEFAULT_EXCLUDE_DIRS
    )
    
    # Warm up the LRU cache
    invalidate_cache()
    _ = get_cached_python_files(str(PROJECT_ROOT))
    
    # Time 10 cached calls (LRU cache)
    start_cached = time.perf_counter()
    for _ in range(10):
        files_cached = get_cached_python_files(str(PROJECT_ROOT))
    end_cached = time.perf_counter()
    cached_time = end_cached - start_cached
    
    # Time 10 rglob calls (with same exclusions for fair comparison)
    start_rglob = time.perf_counter()
    for _ in range(10):
        rglob_files = []
        for py_file in PROJECT_ROOT.rglob("*.py"):
            path_parts = py_file.parts
            skip = False
            for part in path_parts:
                if part in DEFAULT_EXCLUDE_DIRS or part.startswith('.'):
                    skip = True
                    break
            if not skip:
                rglob_files.append(py_file)
    end_rglob = time.perf_counter()
    rglob_time = end_rglob - start_rglob
    
    # Calculate speedup
    if rglob_time > 0:
        speedup = ((rglob_time - cached_time) / rglob_time) * 100
    else:
        speedup = 100
    
    print(f"   Cached (10 calls): {cached_time:.4f}s")
    print(f"   rglob (10 calls):  {rglob_time:.4f}s")
    print(f"   Speedup: {speedup:.1f}%")
    
    if speedup < 90:
        print(f"❌ FAIL: Cached version should be >90% faster, got {speedup:.1f}%")
        return False
    
    print(f"✅ PASS: Cached version is {speedup:.1f}% faster than rglob")
    return True


def test_tc16_refactor_parity():
    """
    TC-16: Refactor Parity
    
    Verify that ssot_discovery returns the same files as rglob
    (with the same exclusions applied).
    """
    print("\n" + "="*60)
    print("TC-16: Refactor Parity")
    print("="*60)
    
    from agentic_core.utils.ssot_discovery import compare_with_rglob
    
    result = compare_with_rglob(PROJECT_ROOT)
    
    print(f"   SSOT Discovery: {result['ssot_count']} files")
    print(f"   rglob (filtered): {result['rglob_count']} files")
    print(f"   Delta: {result['delta']}")
    
    if result['delta'] != 0:
        print(f"❌ FAIL: Delta should be 0, got {result['delta']}")
        if result.get('only_in_ssot'):
            print(f"   Only in SSOT: {result['only_in_ssot'][:3]}")
        if result.get('only_in_rglob'):
            print(f"   Only in rglob: {result['only_in_rglob'][:3]}")
        return False
    
    print("✅ PASS: ssot_discovery returns same files as filtered rglob")
    return True


def test_scan_guard():
    """
    Bonus Test: Verify scan_guard utilities work correctly.
    """
    print("\n" + "="*60)
    print("BONUS: Scan Guard Utilities")
    print("="*60)
    
    import warnings
    from agentic_core.utils.scan_guard import guarded_rglob, audit_rglob_usage
    
    # Test guarded_rglob emits warning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Call guarded_rglob
        result = list(guarded_rglob(PROJECT_ROOT / "agentic_core" / "utils", "*.py"))
        
        if len(w) == 0:
            print("❌ FAIL: guarded_rglob should emit DeprecationWarning")
            return False
        
        if not issubclass(w[-1].category, DeprecationWarning):
            print(f"❌ FAIL: Expected DeprecationWarning, got {w[-1].category}")
            return False
        
        if "ssot_discovery" not in str(w[-1].message):
            print("❌ FAIL: Warning should mention ssot_discovery")
            return False
    
    # Test audit_rglob_usage
    audit = audit_rglob_usage(PROJECT_ROOT / "agentic_core")
    
    print(f"   guarded_rglob warning: ✓")
    print(f"   audit_rglob_usage: {audit['total_rglob_calls']} rglob calls in {audit['files_with_rglob']} files")
    
    print("✅ PASS: Scan guard utilities working correctly")
    return True


def main():
    """Run all Phase 4 Zero-Loss test cases."""
    print("\n" + "="*70)
    print("PHASE 4 ZERO-LOSS VERIFICATION TEST SUITE")
    print("="*70)
    print(f"Project Root: {PROJECT_ROOT}")
    
    tests = [
        ("TC-13: Cache Accuracy", test_tc13_cache_accuracy),
        ("TC-14: Exclusion Integrity", test_tc14_exclusion_integrity),
        ("TC-15: Performance Delta", test_tc15_performance_delta),
        ("TC-16: Refactor Parity", test_tc16_refactor_parity),
        ("BONUS: Scan Guard Utilities", test_scan_guard),
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
    
    # Core tests (TC-13 to TC-16)
    core_tests = results[:4]
    core_passed = sum(1 for _, passed in core_tests if passed)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*70)
    print(f"CORE TESTS: {core_passed}/4 passed")
    print(f"TOTAL: {passed_count}/{total_count} tests passed")
    
    if core_passed == 4:
        print("✅ 100% PASS - All Phase 4 Zero-Loss tests passed!")
        print("\nPhase 4 Performance Hardening is verified.")
        return 0
    else:
        print(f"❌ FAIL - {4 - core_passed} core test(s) failed")
        print("\nReview failures before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
