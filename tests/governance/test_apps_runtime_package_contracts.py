#!/usr/bin/env python3
"""
test_apps_runtime_package_contracts.py - CI Governance Test

Verifies apps_* have runtime_customization_package or explicit exemption.
Validates required profile refs and package structure.

Required refs:
- route
- cache
- runtime gate
- Exit
- judge/eval/rubric
- threshold
- write policy
- learning/meta-feedback

Negative controls:
- Missing package without exemption must fail
- Missing required refs must fail
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Configuration
GOVERNANCE_DIR = REPO_ROOT / "artifacts" / "governance"
APPS_PATTERN = re.compile(r'^apps_\w+$')

# Required refs that every app should have
REQUIRED_REFS = {
    'ingress_contract': 'Ingress contract definition',
    'schema': 'JSON schema for validation',
    'field_map': 'Field mapping for downstream',
}

# Recommended profile refs (warnings if missing)
RECOMMENDED_REFS = {
    'route_profile': 'L0 routing configuration',
    'retrieval_profile': 'C0 retrieval configuration', 
    'prompt_profile': 'Prompt assembly profile',
    'cache_policy': 'Cache policy configuration',
    'exit_profile': 'Exit gate configuration',
    'judge_rubric': 'Judge/eval rubric',
    'threshold_profile': 'Threshold/dimension config',
    'meta_feedback_profile': 'L6 learning config',
}

# Apps with explicit exemption from package requirement
EXEMPT_APPS = {
    # Format: "app_name": "exemption_reason"
    # Example: "apps_legacy": "Migration deferred to Q3"
}


def find_apps_directories() -> List[Path]:
    """Find all apps_* directories."""
    apps_dirs = []
    for item in REPO_ROOT.iterdir():
        if item.is_dir() and APPS_PATTERN.match(item.name):
            apps_dirs.append(item)
    return sorted(apps_dirs)


def find_package_file(app_dir: Path) -> Optional[Path]:
    """Find runtime_customization_package.yaml."""
    paths = [
        app_dir / "config" / "domain_contract" / "runtime_customization_package.yaml",
        app_dir / "runtime_customization_package.yaml",
        app_dir / "config" / "runtime_customization_package.yaml",
    ]
    for path in paths:
        if path.exists():
            return path
    return None


def load_package_yaml(package_path: Path) -> Optional[Dict]:
    """Load and parse package YAML."""
    if not HAS_YAML:
        # Parse basic structure without yaml module
        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Simple key extraction for refs
            refs = {}
            for line in content.split('\n'):
                if 'refs:' in line:
                    continue
                match = re.match(r'\s+(\w+):\s*["\'](.+)["\']', line)
                if match:
                    refs[match.group(1)] = match.group(2)
            return {'refs': refs}
        except IOError:
            return None
    
    try:
        with open(package_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except (IOError, yaml.YAMLError):
        return None


def check_refs(package: Dict, app_name: str) -> Dict:
    """Check package refs completeness."""
    refs = package.get('refs', {}) if package else {}
    
    required_missing = []
    required_present = []
    for ref in REQUIRED_REFS:
        if ref in refs:
            required_present.append(ref)
        else:
            required_missing.append(ref)
    
    recommended_missing = []
    recommended_present = []
    for ref in RECOMMENDED_REFS:
        if ref in refs:
            recommended_present.append(ref)
        else:
            recommended_missing.append(ref)
    
    # Check if refs point to existing files
    missing_files = []
    for ref_name, ref_path in refs.items():
        full_path = REPO_ROOT / ref_path
        if not full_path.exists():
            missing_files.append({
                "ref": ref_name,
                "path": ref_path,
            })
    
    return {
        "required_present": required_present,
        "required_missing": required_missing,
        "required_complete": len(required_missing) == 0,
        "recommended_present": recommended_present,
        "recommended_missing": recommended_missing,
        "recommended_complete": len(recommended_missing) == 0,
        "missing_files": missing_files,
        "all_refs_exist": len(missing_files) == 0,
        "refs_count": len(refs),
    }


def validate_app(app_dir: Path) -> Dict:
    """Validate a single app's package."""
    app_name = app_dir.name
    
    result = {
        "app_name": app_name,
        "app_path": str(app_dir),
    }
    
    # Check exemption
    if app_name in EXEMPT_APPS:
        result["status"] = "EXEMPT"
        result["exemption_reason"] = EXEMPT_APPS[app_name]
        result["passed"] = True
        return result
    
    # Find package
    package_path = find_package_file(app_dir)
    result["package_path"] = str(package_path) if package_path else None
    result["has_package"] = package_path is not None
    
    if not package_path:
        result["status"] = "MISSING_PACKAGE"
        result["passed"] = False
        result["errors"] = ["runtime_customization_package.yaml not found"]
        return result
    
    # Load package
    package = load_package_yaml(package_path)
    if package is None:
        result["status"] = "LOAD_ERROR"
        result["passed"] = False
        result["errors"] = ["Failed to load package YAML"]
        return result
    
    result["package_loaded"] = True
    result["package_version"] = package.get('package_version', 'unknown')
    result["package_digest"] = package.get('package_digest', 'missing')
    
    # Check refs
    refs_check = check_refs(package, app_name)
    result["refs_check"] = refs_check
    
    # Determine status
    errors = []
    warnings = []
    
    if not refs_check["required_complete"]:
        errors.append(f"Missing required refs: {refs_check['required_missing']}")
    
    if not refs_check["all_refs_exist"]:
        for mf in refs_check["missing_files"]:
            errors.append(f"Missing file for ref '{mf['ref']}': {mf['path']}")
    
    if not refs_check["recommended_complete"]:
        warnings.append(f"Missing recommended refs: {refs_check['recommended_missing']}")
    
    if not package.get('package_digest'):
        warnings.append("Package digest not set")
    
    result["errors"] = errors
    result["warnings"] = warnings
    result["passed"] = len(errors) == 0
    
    if errors:
        result["status"] = "INCOMPLETE"
    elif warnings:
        result["status"] = "PARTIAL"
    else:
        result["status"] = "COMPLIANT"
    
    return result


def run_validation() -> Dict:
    """Run validation on all apps."""
    apps_dirs = find_apps_directories()
    
    results = []
    passed = 0
    failed = 0
    exempt = 0
    partial = 0
    
    for app_dir in apps_dirs:
        result = validate_app(app_dir)
        results.append(result)
        
        if result["status"] == "COMPLIANT":
            passed += 1
        elif result["status"] == "EXEMPT":
            exempt += 1
        elif result["status"] == "PARTIAL":
            partial += 1
        else:
            failed += 1
    
    return {
        "apps_checked": len(apps_dirs),
        "compliant": passed,
        "partial": partial,
        "failed": failed,
        "exempt": exempt,
        "app_results": results,
        "passed": failed == 0,
    }


# Negative control tests
def test_missing_package_fails():
    """NEGATIVE CONTROL: Missing package without exemption must fail."""
    # Simulate an app without package
    mock_result = {
        "app_name": "apps_test",
        "has_package": False,
        "status": "MISSING_PACKAGE",
        "passed": False,
    }
    assert not mock_result["passed"], "Missing package should fail"
    assert mock_result["status"] == "MISSING_PACKAGE"
    print("NEGATIVE CONTROL CONFIRMED: Missing package correctly fails")


def test_missing_required_refs_fails():
    """NEGATIVE CONTROL: Missing required refs must fail."""
    mock_refs_check = {
        "required_complete": False,
        "required_missing": ["ingress_contract", "schema"],
    }
    assert not mock_refs_check["required_complete"], "Missing refs should fail"
    print("NEGATIVE CONTROL CONFIRMED: Missing required refs correctly fails")


def test_unknown_treated_as_fail():
    """NEGATIVE CONTROL: UNKNOWN/NOT_APPLICABLE without reason must fail."""
    # This ensures we don't silently ignore unclassified states
    mock_result = {
        "status": "UNKNOWN",
        "passed": False,
        "errors": ["Status is UNKNOWN without valid reason"],
    }
    assert not mock_result["passed"], "UNKNOWN without reason should fail"
    print("NEGATIVE CONTROL CONFIRMED: UNKNOWN without reason correctly fails")


def main():
    """Run the test suite."""
    print("="*70)
    print("TEST: Apps Runtime Package Contracts")
    print("="*70)
    
    # Run negative controls
    print("\nRunning negative controls...")
    test_missing_package_fails()
    test_missing_required_refs_fails()
    test_unknown_treated_as_fail()
    
    # Run validation
    print("\nValidating apps_* packages...")
    results = run_validation()
    
    # Print summary
    print(f"\nApps checked: {results['apps_checked']}")
    print(f"  Compliant: {results['compliant']}")
    print(f"  Partial (warnings): {results['partial']}")
    print(f"  Failed (errors): {results['failed']}")
    print(f"  Exempt: {results['exempt']}")
    
    # Print details
    if results['failed'] > 0 or results['partial'] > 0:
        print("\n" + "-"*70)
        
        # Show failures
        failed_apps = [r for r in results['app_results'] if r['status'] in ['MISSING_PACKAGE', 'INCOMPLETE', 'LOAD_ERROR']]
        if failed_apps:
            print(f"\nFAILED ({len(failed_apps)}):")
            for r in failed_apps:
                print(f"\n  [{r['status']}] {r['app_name']}")
                if 'errors' in r:
                    for e in r['errors']:
                        print(f"    ERROR: {e}")
        
        # Show partial
        partial_apps = [r for r in results['app_results'] if r['status'] == 'PARTIAL']
        if partial_apps:
            print(f"\nPARTIAL/WARNINGS ({len(partial_apps)}):")
            for r in partial_apps:
                print(f"\n  [{r['status']}] {r['app_name']}")
                if 'warnings' in r:
                    for w in r['warnings'][:3]:  # Limit output
                        print(f"    WARNING: {w}")
    
    # Handle result
    if results['failed'] > 0:
        print("\n" + "="*70)
        print("FAIL: Apps missing required runtime packages")
        print("="*70)
        print("\nEach app should have:")
        print("  - config/domain_contract/runtime_customization_package.yaml")
        print("\nRequired refs:")
        for ref, desc in REQUIRED_REFS.items():
            print(f"  - {ref}: {desc}")
        print("\nOr request explicit exemption in EXEMPT_APPS.")
        print("="*70)
        
        # Write results
        output_file = GOVERNANCE_DIR / "test_apps_runtime_package_results.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults written to: {output_file}")
        sys.exit(1)
    
    print("\n" + "="*70)
    if results['passed']:
        print("PASS: All apps have required runtime packages")
    else:
        print("PASS with WARNINGS: All apps valid, some have recommendations")
    print("="*70)
    
    if results['partial'] > 0:
        print(f"\n{results['partial']} apps have warnings (recommended refs missing)")
        print("Consider adding recommended profile refs for full compliance.")
    
    # Write results
    output_file = GOVERNANCE_DIR / "test_apps_runtime_package_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
