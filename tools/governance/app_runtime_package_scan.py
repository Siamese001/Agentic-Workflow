#!/usr/bin/env python3
"""
app_runtime_package_scan.py - Post-cascade response hook.

Scans apps_* directories to verify runtime_customization_package requirements.
Warns or fails when apps lack required package structure.

Exit codes:
  0 - All apps compliant
  1 - Warnings (missing optional refs)
  2 - Errors (missing required package or critical refs)
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Optional

# Configuration
REPO_ROOT = Path("C:\\Git\\Agentic-Workflow-FRESH")
APPS_PATTERN = re.compile(r'^apps_\w+$')
GOVERNANCE_DIR = REPO_ROOT / "artifacts" / "governance"
SCAN_OUTPUT_DIR = GOVERNANCE_DIR / "scans"

# Required package refs
REQUIRED_REFS = [
    'ingress_contract',
    'schema',
    'field_map',
]

# Recommended package refs (generate warning if missing)
RECOMMENDED_REFS = [
    'route_profile',
    'retrieval_profile',
    'prompt_profile',
    'cache_policy',
    'exit_profile',
    'judge_rubric',
    'threshold_profile',
    'meta_feedback_profile',
]

# Apps with explicit exemption
EXEMPT_APPS = {
    # Add apps here if they have explicit exemption from package requirement
    # e.g., "apps_legacy": "Migration deferred to Q3"
}


def find_apps_directories() -> List[Path]:
    """Find all apps_* directories in repo root."""
    apps_dirs = []
    
    if not REPO_ROOT.exists():
        return apps_dirs
    
    for item in REPO_ROOT.iterdir():
        if item.is_dir() and APPS_PATTERN.match(item.name):
            apps_dirs.append(item)
    
    return sorted(apps_dirs)


def has_runtime_package(app_dir: Path) -> bool:
    """Check if app has runtime_customization_package.yaml."""
    package_paths = [
        app_dir / "config" / "domain_contract" / "runtime_customization_package.yaml",
        app_dir / "runtime_customization_package.yaml",
        app_dir / "config" / "runtime_customization_package.yaml",
    ]
    
    for path in package_paths:
        if path.exists():
            return True
    
    return False


def get_package_path(app_dir: Path) -> Optional[Path]:
    """Get path to runtime_customization_package.yaml."""
    package_paths = [
        app_dir / "config" / "domain_contract" / "runtime_customization_package.yaml",
        app_dir / "runtime_customization_package.yaml",
        app_dir / "config" / "runtime_customization_package.yaml",
    ]
    
    for path in package_paths:
        if path.exists():
            return path
    
    return None


def load_package(app_dir: Path) -> Optional[Dict]:
    """Load runtime_customization_package.yaml."""
    import yaml
    
    package_path = get_package_path(app_dir)
    if not package_path:
        return None
    
    try:
        with open(package_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except (IOError, yaml.YAMLError) as e:
        return {"error": f"Cannot load package: {e}"}


def check_package_refs(package: Dict, app_name: str) -> Dict:
    """Check package refs completeness."""
    refs = package.get('refs', {})
    
    required_missing = []
    for ref in REQUIRED_REFS:
        if ref not in refs:
            required_missing.append(ref)
    
    recommended_missing = []
    for ref in RECOMMENDED_REFS:
        if ref not in refs:
            recommended_missing.append(ref)
    
    # Check if refs point to existing files
    missing_files = []
    for ref_name, ref_path in refs.items():
        full_path = REPO_ROOT / ref_path
        if not full_path.exists():
            missing_files.append({
                "ref": ref_name,
                "path": ref_path
            })
    
    return {
        "required_present": len(required_missing) == 0,
        "required_missing": required_missing,
        "recommended_present": len(recommended_missing) == 0,
        "recommended_missing": recommended_missing,
        "all_refs_exist": len(missing_files) == 0,
        "missing_files": missing_files,
        "refs_count": len(refs),
    }


def scan_app(app_dir: Path) -> Dict:
    """Scan a single app for package compliance."""
    app_name = app_dir.name
    
    result = {
        "app_name": app_name,
        "app_path": str(app_dir),
        "exempt": app_name in EXEMPT_APPS,
        "exemption_reason": EXEMPT_APPS.get(app_name),
    }
    
    if result["exempt"]:
        result["status"] = "EXEMPT"
        return result
    
    # Check for package
    has_package = has_runtime_package(app_dir)
    result["has_package"] = has_package
    
    if not has_package:
        result["status"] = "MISSING_PACKAGE"
        result["severity"] = "ERROR"
        result["message"] = f"{app_name} missing runtime_customization_package.yaml"
        return result
    
    # Load and validate package
    package = load_package(app_dir)
    result["package_loaded"] = package is not None
    
    if package and "error" in package:
        result["status"] = "LOAD_ERROR"
        result["severity"] = "ERROR"
        result["message"] = package["error"]
        return result
    
    if package:
        result["package_version"] = package.get('package_version', 'unknown')
        result["package_digest"] = package.get('package_digest', 'missing')
        
        # Check refs
        refs_check = check_package_refs(package, app_name)
        result["refs_check"] = refs_check
        
        # Determine status
        if refs_check["required_present"] and refs_check["all_refs_exist"]:
            if refs_check["recommended_present"]:
                result["status"] = "COMPLIANT"
                result["severity"] = "OK"
            else:
                result["status"] = "PARTIAL"
                result["severity"] = "WARNING"
                result["message"] = f"Missing recommended refs: {refs_check['recommended_missing']}"
        else:
            result["status"] = "INCOMPLETE"
            result["severity"] = "ERROR"
            missing = refs_check["required_missing"] + [m["ref"] for m in refs_check["missing_files"]]
            result["message"] = f"Missing required refs or files: {missing}"
    
    return result


def scan_all_apps() -> Dict:
    """Scan all apps directories."""
    apps_dirs = find_apps_directories()
    
    results = []
    errors = 0
    warnings = 0
    
    for app_dir in apps_dirs:
        result = scan_app(app_dir)
        results.append(result)
        
        if result.get("severity") == "ERROR":
            errors += 1
        elif result.get("severity") == "WARNING":
            warnings += 1
    
    return {
        "apps_scanned": len(apps_dirs),
        "apps_compliant": len([r for r in results if r.get("status") == "COMPLIANT"]),
        "apps_partial": len([r for r in results if r.get("status") == "PARTIAL"]),
        "apps_missing": len([r for r in results if r.get("status") in ["MISSING_PACKAGE", "INCOMPLETE"]]),
        "apps_exempt": len([r for r in results if r.get("status") == "EXEMPT"]),
        "errors": errors,
        "warnings": warnings,
        "app_results": results,
    }


def save_scan_results(results: Dict):
    """Save scan results to file."""
    SCAN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = str(Path(__file__).stat().st_mtime).split('.')[0]
    output_file = SCAN_OUTPUT_DIR / f"app_runtime_package_scan_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    return output_file


def main():
    """Main entry point."""
    print("APP_RUNTIME_PACKAGE_SCAN: Scanning apps_* for runtime_customization_package...")
    
    # Run scan
    results = scan_all_apps()
    
    # Save results
    output_file = save_scan_results(results)
    results["scan_output_file"] = str(output_file)
    results["timestamp"] = str(Path(__file__).stat().st_mtime)
    
    # Print summary
    print(f"\nApps scanned: {results['apps_scanned']}")
    print(f"  Compliant: {results['apps_compliant']}")
    print(f"  Partial: {results['apps_partial']}")
    print(f"  Missing/Incomplete: {results['apps_missing']}")
    print(f"  Exempt: {results['apps_exempt']}")
    print(f"\nErrors: {results['errors']}")
    print(f"Warnings: {results['warnings']}")
    
    # Print details
    if results['errors'] > 0 or results['warnings'] > 0:
        print("\n" + "="*60)
        print("APP PACKAGE ISSUES")
        print("="*60)
        
        for app in results['app_results']:
            status = app.get('status', 'UNKNOWN')
            severity = app.get('severity', 'INFO')
            
            if severity in ['ERROR', 'WARNING']:
                print(f"\n[{severity}] {app['app_name']}: {status}")
                if 'message' in app:
                    print(f"  {app['message']}")
                
                if 'refs_check' in app:
                    refs = app['refs_check']
                    if refs.get('required_missing'):
                        print(f"  Required refs missing: {refs['required_missing']}")
                    if refs.get('missing_files'):
                        for mf in refs['missing_files']:
                            print(f"  Missing file: {mf['path']} ({mf['ref']})")
        
        print("\n" + "="*60)
        print("Each app should have runtime_customization_package.yaml with:")
        print("  - Required refs: ingress_contract, schema, field_map")
        print("  - Recommended refs: route_profile, exit_profile, etc.")
        print("="*60)
        print(f"\nFull report: {output_file}")
    
    # Determine exit code
    if results['errors'] > 0:
        print("\nAPP_RUNTIME_PACKAGE_SCAN: Errors detected.")
        sys.exit(2)
    elif results['warnings'] > 0:
        print("\nAPP_RUNTIME_PACKAGE_SCAN: Warnings detected.")
        sys.exit(1)
    else:
        print("\nAPP_RUNTIME_PACKAGE_SCAN: All apps compliant.")
        sys.exit(0)


if __name__ == "__main__":
    main()
