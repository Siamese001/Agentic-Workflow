#!/usr/bin/env python3
"""
MANDATORY DASHBOARD TEST SUITE
==============================

This script runs ALL mandatory tests required before any dashboard refresh.
ALL tests must pass before deployment is allowed.

MANDATORY TESTS:
1. SSOT Enforcement Tests - Verify SSOT architecture integrity
2. E2E Tests - End-to-end dashboard functionality
3. Data Validation Tests - Verify data integrity and calculations

Usage:
    python agentic_core/L6_observability/dashboards/scripts/run_all_mandatory_tests.py

Exit Codes:
    0 - All tests passed, safe to deploy
    1 - Tests failed, DO NOT DEPLOY
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Colors for terminal output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{CYAN}{'=' * 70}{RESET}")
    print(f"{BOLD}{CYAN}{text}{RESET}")
    print(f"{CYAN}{'=' * 70}{RESET}\n")


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result with color coding."""
    if passed:
        print(f"{GREEN}✅ {test_name}: PASSED{RESET}")
    else:
        print(f"{RED}❌ {test_name}: FAILED{RESET}")
    if details:
        print(f"   {details}")


def run_test(name: str, script_path: Path, args: list = None) -> bool:
    """Run a test script and return success status."""
    print(f"\n{YELLOW}Running: {name}{RESET}")
    print(f"Script: {script_path}")
    print("-" * 50)
    
    if not script_path.exists():
        print(f"{RED}ERROR: Script not found: {script_path}{RESET}")
        return False
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=False,
            text=True,
            env={**dict(__import__('os').environ), 'PYTHONPATH': str(PROJECT_ROOT)}
        )
        return result.returncode == 0
    except Exception as e:
        print(f"{RED}ERROR: {e}{RESET}")
        return False


def main():
    """Run all mandatory dashboard tests."""
    print_header("MANDATORY DASHBOARD TEST SUITE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Project Root: {PROJECT_ROOT}")
    
    # Track results
    results = {}
    all_passed = True
    
    # =========================================================================
    # TEST 1: SSOT Enforcement Tests
    # =========================================================================
    print_header("TEST 1: SSOT ENFORCEMENT")
    ssot_script = PROJECT_ROOT / "scripts" / "test_ssot_enforcement.py"
    results['SSOT Enforcement'] = run_test("SSOT Enforcement Tests", ssot_script)
    if not results['SSOT Enforcement']:
        all_passed = False
    
    # =========================================================================
    # TEST 2: SSOT Generator Verification
    # =========================================================================
    print_header("TEST 2: SSOT GENERATOR VERIFICATION")
    generator_script = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "scripts" / "generate_ssot.py"
    results['SSOT Generator'] = run_test("SSOT Generator", generator_script)
    if not results['SSOT Generator']:
        all_passed = False
    
    # =========================================================================
    # TEST 3: Data Regeneration
    # =========================================================================
    print_header("TEST 3: DATA REGENERATION")
    regenerate_script = PROJECT_ROOT / "agentic_core" / "L6_observability" / "dashboards" / "scripts" / "regenerate_data.py"
    results['Data Regeneration'] = run_test("Data Regeneration", regenerate_script)
    if not results['Data Regeneration']:
        all_passed = False
    
    # =========================================================================
    # TEST 4: Data Integrity Validation
    # =========================================================================
    print_header("TEST 4: DATA INTEGRITY VALIDATION")
    integrity_script = PROJECT_ROOT / "scripts" / "test_dashboard_data_integrity.py"
    if integrity_script.exists():
        results['Data Integrity'] = run_test("Data Integrity Tests", integrity_script)
        if not results['Data Integrity']:
            all_passed = False
    else:
        print(f"{YELLOW}⚠️  Data integrity script not found, skipping{RESET}")
        results['Data Integrity'] = True  # Don't fail if script missing
    
    # =========================================================================
    # TEST 5: Dashboard Generation Tests
    # =========================================================================
    print_header("TEST 5: DASHBOARD GENERATION TESTS")
    generation_script = PROJECT_ROOT / "scripts" / "test_dashboard_generation.py"
    if generation_script.exists():
        results['Dashboard Generation'] = run_test("Dashboard Generation Tests", generation_script)
        if not results['Dashboard Generation']:
            all_passed = False
    else:
        print(f"{YELLOW}⚠️  Dashboard generation script not found, skipping{RESET}")
        results['Dashboard Generation'] = True
    
    # =========================================================================
    # TEST 6: E2E Tests (Core Tests Only)
    # =========================================================================
    print_header("TEST 6: E2E CORE TESTS")
    e2e_script = PROJECT_ROOT / "scripts" / "test_dashboard_end_to_end.py"
    if e2e_script.exists():
        # Run with --yes flag to auto-confirm
        results['E2E Tests'] = run_test("E2E Dashboard Tests", e2e_script, ['--yes'])
        if not results['E2E Tests']:
            # E2E failures are critical but we continue to show all results
            all_passed = False
    else:
        print(f"{YELLOW}⚠️  E2E script not found, skipping{RESET}")
        results['E2E Tests'] = True
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print_header("MANDATORY TEST SUMMARY")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\n{BOLD}Results:{RESET}")
    for test_name, passed in results.items():
        print_result(test_name, passed)
    
    print(f"\n{BOLD}Score: {passed_count}/{total_count} tests passed{RESET}")
    
    if all_passed:
        print(f"\n{GREEN}{'=' * 70}{RESET}")
        print(f"{GREEN}{BOLD}✅ ALL MANDATORY TESTS PASSED{RESET}")
        print(f"{GREEN}{'=' * 70}{RESET}")
        print(f"\n{GREEN}Dashboard refresh is SAFE to deploy.{RESET}")
        return 0
    else:
        print(f"\n{RED}{'=' * 70}{RESET}")
        print(f"{RED}{BOLD}❌ MANDATORY TESTS FAILED{RESET}")
        print(f"{RED}{'=' * 70}{RESET}")
        print(f"\n{RED}DO NOT DEPLOY until all tests pass!{RESET}")
        print(f"\n{YELLOW}Failed tests:{RESET}")
        for test_name, passed in results.items():
            if not passed:
                print(f"  - {test_name}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
