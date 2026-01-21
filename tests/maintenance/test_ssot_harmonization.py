#!/usr/bin/env python3
"""
SSOT Harmonization Verification Tests
======================================

Validates that folder definitions are centralized and harmonized:
1. GLOBAL_EXCLUDED_DIRS is the single source of truth
2. is_path_allowed correctly handles subdirectories
3. All consumers use the SSOT instead of hardcoded values
4. No false positives for valid paths like agentic_core/utils/

Success Criteria:
- sovereign_index.py should NOT be flagged as a violation
- agentic_core/utils/* paths should be allowed
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


# ============================================================================
# Test 1: GLOBAL_EXCLUDED_DIRS exists and contains required entries
# ============================================================================

def test_global_excluded_dirs():
    """Verify GLOBAL_EXCLUDED_DIRS is properly defined."""
    print("\n" + "=" * 60)
    print("Test 1: GLOBAL_EXCLUDED_DIRS SSOT")
    print("=" * 60)

    try:
        from agentic_core.L5_safety.validators.structure_blueprint import GLOBAL_EXCLUDED_DIRS

        required_entries = [
            '__pycache__', '.pytest_cache', '.git', '.venv', 'venv',
            'node_modules', 'archives', '.sovereign_healing_backup', 'tests'
        ]

        for entry in required_entries:
            if entry in GLOBAL_EXCLUDED_DIRS:
                test_pass(f"ENTRY_{entry}", f"'{entry}' in GLOBAL_EXCLUDED_DIRS")
            else:
                test_fail(f"ENTRY_{entry}", f"'{entry}' NOT in GLOBAL_EXCLUDED_DIRS")

    except ImportError as e:
        test_fail("IMPORT", f"Cannot import GLOBAL_EXCLUDED_DIRS: {e}")


# ============================================================================
# Test 2: is_path_allowed handles subdirectories correctly
# ============================================================================

def test_is_path_allowed():
    """Verify is_path_allowed correctly handles nested paths."""
    print("\n" + "=" * 60)
    print("Test 2: is_path_allowed Subdirectory Handling")
    print("=" * 60)

    try:
        from agentic_core.L5_safety.validators.structure_blueprint import is_path_allowed

        # These paths should ALL be allowed (no false positives)
        valid_paths = [
            'agentic_core/utils/sovereign_index.py',
            'agentic_core/utils/terminal_colors.py',
            'agentic_core/L2_execution/ToolRegistry/L2ExecutionBaseAgent.py',
            'agentic_core/L5_safety/validators/LocationAgent.py',
            'agentic_core/config/blueprint_sovereign/structure_blueprint.py',
            'agentic_core/L3_orchestration/UnifiedOrchestratorAgent.py',
            'apps_rg/engines/resume_engine.py',
            'apps_lic/engines/outreach_engine.py',
        ]

        for path in valid_paths:
            if is_path_allowed(path):
                test_pass(f"VALID_{path.split('/')[-1]}", f"'{path}' correctly allowed")
            else:
                test_fail(f"VALID_{path.split('/')[-1]}", f"'{path}' INCORRECTLY rejected (FALSE POSITIVE)")

        # These paths should be rejected (invalid roots)
        invalid_paths = [
            'random_folder/file.py',
            'unknown_root/subdir/file.py',
        ]

        for path in invalid_paths:
            if not is_path_allowed(path):
                test_pass(f"INVALID_{path.split('/')[0]}", f"'{path}' correctly rejected")
            else:
                test_fail(f"INVALID_{path.split('/')[0]}", f"'{path}' INCORRECTLY allowed")

    except ImportError as e:
        test_fail("IMPORT", f"Cannot import is_path_allowed: {e}")


# ============================================================================
# Test 3: SovereignIndex uses SSOT
# ============================================================================

def test_sovereign_index_ssot():
    """Verify SovereignIndex imports from SSOT."""
    print("\n" + "=" * 60)
    print("Test 3: SovereignIndex SSOT Usage")
    print("=" * 60)

    index_path = PROJECT_ROOT / "agentic_core/utils/sovereign_index.py"
    if not index_path.exists():
        test_fail("FILE", "sovereign_index.py not found")
        return

    content = index_path.read_text(encoding='utf-8')

    if 'from agentic_core.L5_safety.validators.structure_blueprint import GLOBAL_EXCLUDED_DIRS' in content:
        test_pass("IMPORT", "Imports GLOBAL_EXCLUDED_DIRS from SSOT")
    else:
        test_fail("IMPORT", "Does NOT import GLOBAL_EXCLUDED_DIRS from SSOT")

    if '_SSOT_EXCLUSIONS_AVAILABLE' in content:
        test_pass("FALLBACK", "Has fallback mechanism for SSOT unavailability")
    else:
        test_fail("FALLBACK", "No fallback mechanism")


# ============================================================================
# Test 4: HygieneGuardianAgent uses SSOT
# ============================================================================

def test_hygiene_guardian_ssot():
    """Verify HygieneGuardianAgent imports from SSOT."""
    print("\n" + "=" * 60)
    print("Test 4: HygieneGuardianAgent SSOT Usage")
    print("=" * 60)

    agent_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/HygieneGuardianAgent.py"
    if not agent_path.exists():
        test_fail("FILE", "HygieneGuardianAgent.py not found")
        return

    content = agent_path.read_text(encoding='utf-8')

    if 'GLOBAL_EXCLUDED_DIRS' in content:
        test_pass("IMPORT", "References GLOBAL_EXCLUDED_DIRS")
    else:
        test_fail("IMPORT", "Does NOT reference GLOBAL_EXCLUDED_DIRS")

    if 'SKIP_DIRS = set(GLOBAL_EXCLUDED_DIRS)' in content:
        test_pass("USAGE", "SKIP_DIRS uses GLOBAL_EXCLUDED_DIRS")
    else:
        test_fail("USAGE", "SKIP_DIRS does NOT use GLOBAL_EXCLUDED_DIRS")


# ============================================================================
# Test 5: DuplicateCodeDetectorAgent uses SSOT
# ============================================================================

def test_duplicate_detector_ssot():
    """Verify DuplicateCodeDetectorAgent imports from SSOT."""
    print("\n" + "=" * 60)
    print("Test 5: DuplicateCodeDetectorAgent SSOT Usage")
    print("=" * 60)

    agent_path = PROJECT_ROOT / "apps_shared/utils/DuplicateCodeDetectorAgent.py"
    if not agent_path.exists():
        test_fail("FILE", "DuplicateCodeDetectorAgent.py not found")
        return

    content = agent_path.read_text(encoding='utf-8')

    if 'GLOBAL_EXCLUDED_DIRS' in content:
        test_pass("IMPORT", "References GLOBAL_EXCLUDED_DIRS")
    else:
        test_fail("IMPORT", "Does NOT reference GLOBAL_EXCLUDED_DIRS")

    if 'EXCLUDE_DIRS = set(GLOBAL_EXCLUDED_DIRS)' in content:
        test_pass("USAGE", "EXCLUDE_DIRS uses GLOBAL_EXCLUDED_DIRS")
    else:
        test_fail("USAGE", "EXCLUDE_DIRS does NOT use GLOBAL_EXCLUDED_DIRS")


# ============================================================================
# Test 6: LocationAgent uses is_path_allowed
# ============================================================================

def test_location_agent_ssot():
    """Verify LocationAgent uses is_path_allowed for validation."""
    print("\n" + "=" * 60)
    print("Test 6: LocationAgent SSOT Usage")
    print("=" * 60)

    agent_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/LocationAgent.py"
    if not agent_path.exists():
        test_fail("FILE", "LocationAgent.py not found")
        return

    content = agent_path.read_text(encoding='utf-8')

    if 'is_path_allowed' in content:
        test_pass("IMPORT", "References is_path_allowed")
    else:
        test_fail("IMPORT", "Does NOT reference is_path_allowed")

    if '_validate_root_whitelist' in content and 'is_path_allowed' in content:
        test_pass("USAGE", "_validate_root_whitelist uses is_path_allowed")
    else:
        test_fail("USAGE", "_validate_root_whitelist does NOT use is_path_allowed")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    print("=" * 60)
    print("SSOT HARMONIZATION VERIFICATION")
    print("=" * 60)
    print("Validating folder definitions are centralized and harmonized")

    test_global_excluded_dirs()
    test_is_path_allowed()
    test_sovereign_index_ssot()
    test_hygiene_guardian_ssot()
    test_duplicate_detector_ssot()
    test_location_agent_ssot()

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"  Total Checks: {PASSED + FAILED}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {PASSED / (PASSED + FAILED) * 100:.1f}%")
    print()

    if FAILED == 0:
        print("  ✅ SSOT HARMONIZATION VERIFIED - NO SPLIT BRAIN")
        return 0
    else:
        print(f"  ❌ {FAILED} CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
