#!/usr/bin/env python3
"""
Archives Quarantine Verification Test
======================================
Verifies that the archives/ directory is properly quarantined from all system components.

Success Criteria:
1. GLOBAL_EXCLUDED_DIRS contains 'archives'
2. SOVEREIGN_EXCLUDED_FOLDERS contains 'archives'
3. SovereignIndex excludes archives
4. DuplicateCodeDetectorAgent excludes archives
5. conftest.py has quarantine helpers
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PASSED = 0
FAILED = 0


def test_pass(test_id: str, msg: str):
    global PASSED
    PASSED += 1
    print(f"  ✅ {test_id}: {msg}")


def test_fail(test_id: str, msg: str):
    global FAILED
    FAILED += 1
    print(f"  ❌ {test_id}: {msg}")


def test_ssot_global_excluded_dirs():
    """Verify GLOBAL_EXCLUDED_DIRS contains archives."""
    print("\n" + "=" * 60)
    print("Test 1: SSOT GLOBAL_EXCLUDED_DIRS")
    print("=" * 60)
    
    try:
        from agentic_core.L5_safety.validators.structure_blueprint import GLOBAL_EXCLUDED_DIRS
        
        if 'archives' in GLOBAL_EXCLUDED_DIRS:
            test_pass("ARCHIVES", "'archives' in GLOBAL_EXCLUDED_DIRS")
        else:
            test_fail("ARCHIVES", "'archives' NOT in GLOBAL_EXCLUDED_DIRS")
        
        if '.sovereign_healing_backup' in GLOBAL_EXCLUDED_DIRS:
            test_pass("BACKUP", "'.sovereign_healing_backup' in GLOBAL_EXCLUDED_DIRS")
        else:
            test_fail("BACKUP", "'.sovereign_healing_backup' NOT in GLOBAL_EXCLUDED_DIRS")
            
    except ImportError as e:
        test_fail("IMPORT", f"Cannot import GLOBAL_EXCLUDED_DIRS: {e}")


def test_ssot_sovereign_excluded_folders():
    """Verify SOVEREIGN_EXCLUDED_FOLDERS contains archives."""
    print("\n" + "=" * 60)
    print("Test 2: SSOT SOVEREIGN_EXCLUDED_FOLDERS")
    print("=" * 60)
    
    try:
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_EXCLUDED_FOLDERS
        
        if 'archives' in SOVEREIGN_EXCLUDED_FOLDERS:
            test_pass("ARCHIVES", "'archives' in SOVEREIGN_EXCLUDED_FOLDERS")
        else:
            test_fail("ARCHIVES", "'archives' NOT in SOVEREIGN_EXCLUDED_FOLDERS")
        
        if '.sovereign_healing_backup' in SOVEREIGN_EXCLUDED_FOLDERS:
            test_pass("BACKUP", "'.sovereign_healing_backup' in SOVEREIGN_EXCLUDED_FOLDERS")
        else:
            test_fail("BACKUP", "'.sovereign_healing_backup' NOT in SOVEREIGN_EXCLUDED_FOLDERS")
            
    except ImportError as e:
        test_fail("IMPORT", f"Cannot import SOVEREIGN_EXCLUDED_FOLDERS: {e}")


def test_sovereign_index_exclusion():
    """Verify SovereignIndex excludes archives."""
    print("\n" + "=" * 60)
    print("Test 3: SovereignIndex DEFAULT_EXCLUDED_DIRS")
    print("=" * 60)
    
    # Static analysis
    index_path = PROJECT_ROOT / "agentic_core/utils/sovereign_index.py"
    if not index_path.exists():
        test_fail("FILE", "sovereign_index.py not found")
        return
    
    content = index_path.read_text(encoding='utf-8')
    
    if "'archives'" in content and 'DEFAULT_EXCLUDED_DIRS' in content:
        test_pass("ARCHIVES", "'archives' in DEFAULT_EXCLUDED_DIRS")
    else:
        test_fail("ARCHIVES", "'archives' NOT in DEFAULT_EXCLUDED_DIRS")
    
    if "'.sovereign_healing_backup'" in content:
        test_pass("BACKUP", "'.sovereign_healing_backup' in exclusions")
    else:
        test_fail("BACKUP", "'.sovereign_healing_backup' NOT in exclusions")


def test_duplicate_detector_exclusion():
    """Verify DuplicateCodeDetectorAgent excludes archives."""
    print("\n" + "=" * 60)
    print("Test 4: DuplicateCodeDetectorAgent EXCLUDE_DIRS")
    print("=" * 60)
    
    # Static analysis
    detector_path = PROJECT_ROOT / "apps_shared/utils/DuplicateCodeDetectorAgent.py"
    if not detector_path.exists():
        test_fail("FILE", "DuplicateCodeDetectorAgent.py not found")
        return
    
    content = detector_path.read_text(encoding='utf-8')
    
    if 'ARCHIVES_DIR' in content and 'EXCLUDE_DIRS' in content:
        test_pass("ARCHIVES", "ARCHIVES_DIR in EXCLUDE_DIRS")
    else:
        test_fail("ARCHIVES", "ARCHIVES_DIR NOT in EXCLUDE_DIRS")
    
    if "GLOBAL_EXCLUDED_DIRS" in content:
        test_pass("BACKUP", "Uses GLOBAL_EXCLUDED_DIRS (includes .sovereign_healing_backup)")
    else:
        test_fail("BACKUP", "Does NOT use GLOBAL_EXCLUDED_DIRS")


def test_conftest_quarantine():
    """Verify conftest.py has quarantine helpers."""
    print("\n" + "=" * 60)
    print("Test 5: conftest.py Quarantine Helpers")
    print("=" * 60)
    
    conftest_path = PROJECT_ROOT / "tests/conftest.py"
    if not conftest_path.exists():
        test_fail("FILE", "conftest.py not found")
        return
    
    content = conftest_path.read_text(encoding='utf-8')
    
    if 'QUARANTINED_DIRS' in content:
        test_pass("CONSTANT", "QUARANTINED_DIRS constant defined")
    else:
        test_fail("CONSTANT", "QUARANTINED_DIRS constant NOT defined")
    
    if 'is_quarantined_path' in content:
        test_pass("FUNCTION", "is_quarantined_path function defined")
    else:
        test_fail("FUNCTION", "is_quarantined_path function NOT defined")
    
    if "'archives'" in content:
        test_pass("ARCHIVES", "'archives' in quarantine list")
    else:
        test_fail("ARCHIVES", "'archives' NOT in quarantine list")


def test_canon_validator_no_archives_import():
    """Verify canon_validator doesn't import from archives."""
    print("\n" + "=" * 60)
    print("Test 6: canon_validator No Archives Import")
    print("=" * 60)
    
    validator_path = PROJECT_ROOT / "canon_validator_agentic_v2_thin.py"
    if not validator_path.exists():
        test_fail("FILE", "canon_validator_agentic_v2_thin.py not found")
        return
    
    content = validator_path.read_text(encoding='utf-8')
    
    # Check for imports from archives (should NOT exist)
    if 'from archives.' in content or 'import archives.' in content:
        test_fail("NO_ARCHIVES_IMPORT", "Still imports from archives/")
    else:
        test_pass("NO_ARCHIVES_IMPORT", "No imports from archives/")
    
    # Check for correct terminal_colors import
    if 'from agentic_core.utils.terminal_colors import' in content:
        test_pass("TERMINAL_COLORS", "terminal_colors imported from correct location")
    else:
        test_fail("TERMINAL_COLORS", "terminal_colors NOT imported from correct location")


def main():
    print("=" * 60)
    print("ARCHIVES QUARANTINE VERIFICATION")
    print("=" * 60)
    print("Verifying archives/ is excluded from all system components")
    
    test_ssot_global_excluded_dirs()
    test_ssot_sovereign_excluded_folders()
    test_sovereign_index_exclusion()
    test_duplicate_detector_exclusion()
    test_conftest_quarantine()
    test_canon_validator_no_archives_import()
    
    # Summary
    print("\n" + "=" * 60)
    print("QUARANTINE VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"  Total Checks: {PASSED + FAILED}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {PASSED / (PASSED + FAILED) * 100:.1f}%")
    print()
    
    if FAILED == 0:
        print("  ✅ ARCHIVES QUARANTINE VERIFIED - NO LEAKS DETECTED")
        return 0
    else:
        print(f"  ❌ {FAILED} QUARANTINE CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
