#!/usr/bin/env python
"""
Dashboard Migration Validation Script
Verifies that the sovereign healing migration was successful
"""

import sys
import os
from pathlib import Path
import json

def check_directory_structure():
    """Verify dashboard directory structure is correct"""
    print("Checking directory structure...")
    
    dashboard_dir = Path(__file__).parent
    required_files = [
        "__init__.py",
        "dashboard_server.py",
        "run_tests.sh",
        "MIGRATION_SUMMARY.md"
    ]
    
    required_dirs = [
        "static"
    ]
    
    all_good = True
    
    for file in required_files:
        file_path = dashboard_dir / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_good = False
    
    for dir_name in required_dirs:
        dir_path = dashboard_dir / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ - MISSING")
            all_good = False
    
    return all_good

def check_test_structure():
    """Verify test directory structure is correct"""
    print("\nChecking test structure...")
    
    project_root = Path(__file__).parent.parent.parent.parent.parent
    test_dirs = [
        "tests/unit/observability/metrics/dashboard",
        "tests/integration/dashboard",
        "tests/regression/dashboard",
        "tests/e2e/dashboard"
    ]
    
    all_good = True
    
    for test_dir in test_dirs:
        test_path = project_root / test_dir
        if test_path.exists():
            print(f"  ✓ {test_dir}/")
        else:
            print(f"  ✗ {test_dir}/ - MISSING")
            all_good = False
    
    return all_good

def check_ssot_update():
    """Verify SSOT was updated with dashboard location"""
    print("\nChecking SSOT update...")
    
    blueprint_path = Path(__file__).parent.parent.parent.parent / "config" / "blueprint_sovereign" / "structure_blueprint.py"
    
    if not blueprint_path.exists():
        print(f"  ✗ structure_blueprint.py not found at {blueprint_path}")
        return False
    
    with open(blueprint_path, "r") as f:
        content = f.read()
    
    if "'dashboard'" in content and "'observability'" in content:
        print("  ✓ Dashboard added to observability in SSOT")
        return True
    else:
        print("  ✗ Dashboard not found in SSOT")
        return False

def check_test_files():
    """Verify test files exist and are readable"""
    print("\nChecking test files...")
    
    project_root = Path(__file__).parent.parent.parent.parent.parent
    test_files = [
        "tests/unit/observability/metrics/dashboard/test_dashboard_server.py",
        "tests/integration/dashboard/test_dashboard_integration.py",
        "tests/regression/dashboard/test_dashboard_regression.py",
        "tests/regression/dashboard/regression_baseline.json",
        "tests/e2e/dashboard/test_dashboard_e2e.py"
    ]
    
    all_good = True
    
    for test_file in test_files:
        test_path = project_root / test_file
        if test_path.exists():
            print(f"  ✓ {test_file}")
        else:
            print(f"  ✗ {test_file} - MISSING")
            all_good = False
    
    return all_good

def check_regression_baseline():
    """Verify regression baseline is valid JSON"""
    print("\nChecking regression baseline...")
    
    project_root = Path(__file__).parent.parent.parent.parent.parent
    baseline_path = project_root / "tests/regression/dashboard/regression_baseline.json"
    
    if not baseline_path.exists():
        print(f"  ✗ regression_baseline.json not found")
        return False
    
    try:
        with open(baseline_path, "r") as f:
            baseline = json.load(f)
        
        required_keys = ["description", "expected_structure", "required_fields", "required_layers"]
        for key in required_keys:
            if key in baseline:
                print(f"  ✓ {key} present in baseline")
            else:
                print(f"  ✗ {key} missing from baseline")
                return False
        
        return True
    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON in regression_baseline.json: {e}")
        return False

def check_dashboard_server():
    """Verify dashboard server can be imported"""
    print("\nChecking dashboard server...")
    
    try:
        from agentic_core.observability.metrics.dashboard.dashboard_server import app
        print("  ✓ dashboard_server.py can be imported")
        print("  ✓ FastAPI app created successfully")
        return True
    except ImportError as e:
        print(f"  ✗ Failed to import dashboard_server: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error creating app: {e}")
        return False

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("Dashboard Migration Validation")
    print("=" * 60)
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Test Structure", check_test_structure),
        ("SSOT Update", check_ssot_update),
        ("Test Files", check_test_files),
        ("Regression Baseline", check_regression_baseline),
        ("Dashboard Server", check_dashboard_server),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"  ✗ Error during check: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {check_name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ All validation checks passed!")
        print("\nNext steps:")
        print("1. Move autonomy_dashboard.html to static/")
        print("2. Run: bash agentic_core/observability/metrics/dashboard/run_tests.sh")
        print("3. Start server: python agentic_core/observability/metrics/dashboard/dashboard_server.py")
        return 0
    else:
        print(f"\n✗ {total - passed} validation check(s) failed")
        print("Please fix the issues above before proceeding")
        return 1

if __name__ == "__main__":
    sys.exit(main())
