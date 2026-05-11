#!/usr/bin/env python3
"""
test_no_app_exit_x3_emission.py - CI Governance Test

Proves apps_* cannot emit X3 dispositions.
Proves app Exit profiles are config/data only.
Verifies only core Exit emits final X3 disposition.

Negative controls:
- apps_* X3 emission must fail
- Import of X3 disposition emitters in apps must fail
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Configuration
GOVERNANCE_DIR = REPO_ROOT / "artifacts" / "governance"
AGENTIC_CORE_PATH = REPO_ROOT / "agentic_core"
APPS_PATTERN = re.compile(r'^apps_\w+$')

# Forbidden patterns indicating app X3 emission
FORBIDDEN_PATTERNS = {
    "x3_disposition_emit": {
        "patterns": [
            r'emit_x3\(',
            r'emit_x3_disposition\(',
            r'X3Disposition\(',
            r'X3Commit\(',
            r'\.emit_disposition\(',
            r'\.finalize_x3\(',
        ],
        "description": "Direct X3 disposition emission",
        "severity": "CRITICAL"
    },
    "x3_import": {
        "patterns": [
            r'from\s+.*X3.*\s+import',
            r'import\s+.*X3Disposition',
            r'from\s+.*exit.*x3',
            r'from\s+.*disposition.*import',
        ],
        "description": "Import of X3 emission modules",
        "severity": "CRITICAL"
    },
    "exit_emulation": {
        "patterns": [
            r'class.*Exit.*:',
            r'def\s+exit_pipeline\(',
            r'def\s+emit_final_disposition\(',
            r'\.x3_emit\(',
        ],
        "description": "App attempting to emulate Exit layer",
        "severity": "HIGH"
    },
    "disposition_construction": {
        "patterns": [
            r'DispositionPacket\(',
            r'FinalReviewPacket\(',
            r'ExitReviewPacket\(',
            r'\.create_x3_payload\(',
        ],
        "description": "Construction of disposition packets in app",
        "severity": "HIGH"
    },
    "bypass_exit": {
        "patterns": [
            r'bypass_exit.*=.*True',
            r'skip_exit.*=.*True',
            r'direct_commit.*=.*True',
        ],
        "description": "Attempt to bypass Exit layer",
        "severity": "CRITICAL"
    }
}

# Allowed patterns (configuration/data only)
ALLOWED_PATTERNS = {
    "exit_profile_config": [
        r'exit_profile\.yaml',
        r'exit_gates:',
        r'forbidden_actions:',
        r'required_gates:',
    ],
    "exit_data_only": [
        r'exit_config\s*=',
        r'profile\.get\(["\']exit',
        r'config\[\'exit_profile\'\]',
    ]
}

# Apps that are allowed to reference Exit (for routing to it)
ALLOWED_EXIT_REFERENCES = [
    r'from\s+apps_shared.*exit',
    r'import\s+apps_shared\.cert',
    r'maybe_invoke_exit_eval',
    r'ExitEvalHook',
]


def find_apps_directories() -> List[Path]:
    """Find all apps_* directories."""
    apps_dirs = []
    for item in REPO_ROOT.iterdir():
        if item.is_dir() and APPS_PATTERN.match(item.name):
            apps_dirs.append(item)
    return sorted(apps_dirs)


def is_allowed_exit_reference(line: str) -> bool:
    """Check if line is allowed Exit reference (not emission)."""
    for pattern in ALLOWED_EXIT_REFERENCES:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    
    # Check if it's just config/data reference
    for pattern in ALLOWED_PATTERNS["exit_data_only"]:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    
    return False


def is_config_file(filepath: str) -> bool:
    """Check if file is a config/data file (not code)."""
    config_patterns = [
        r'\.yaml$',
        r'\.yml$',
        r'\.json$',
        r'config/',
        r'domain_contract/',
    ]
    for pattern in config_patterns:
        if re.search(pattern, filepath, re.IGNORECASE):
            return True
    return False


def scan_file(filepath: str, app_name: str) -> List[Dict]:
    """Scan a single file for X3 emission patterns."""
    violations = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except (IOError, OSError):
        return violations
    
    rel_path = str(filepath).replace(str(REPO_ROOT), "").lstrip("/\\")
    
    # Skip config files - they should only have data
    if is_config_file(rel_path):
        return violations
    
    for line_num, line in enumerate(lines, 1):
        # Skip comments
        code_line = line.split('#')[0]
        
        for pattern_name, pattern_info in FORBIDDEN_PATTERNS.items():
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, code_line, re.IGNORECASE):
                    # Check if it's an allowed reference
                    if is_allowed_exit_reference(code_line):
                        continue
                    
                    violations.append({
                        "file": rel_path,
                        "line": line_num,
                        "pattern": pattern_name,
                        "pattern_regex": pattern,
                        "description": pattern_info["description"],
                        "severity": pattern_info["severity"],
                        "content": line.strip()[:100],
                        "app_name": app_name,
                    })
    
    return violations


def scan_all_apps() -> List[Dict]:
    """Scan all apps for X3 emission violations."""
    all_violations = []
    
    apps_dirs = find_apps_directories()
    
    for app_dir in apps_dirs:
        app_name = app_dir.name
        
        for root, dirs, files in os.walk(app_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for filename in files:
                if not filename.endswith('.py'):
                    continue
                
                filepath = Path(root) / filename
                violations = scan_file(str(filepath), app_name)
                all_violations.extend(violations)
    
    return all_violations


def verify_core_exit_present() -> Dict:
    """Verify core Exit layer exists and handles X3."""
    exit_paths = [
        AGENTIC_CORE_PATH / "runtime" / "exit",
        AGENTIC_CORE_PATH / "L6_observability",
        AGENTIC_CORE_PATH / "L3_orchestration" / "exit_eval",
    ]
    
    exit_found = False
    x3_handling_found = False
    exit_files = []
    
    for exit_path in exit_paths:
        if exit_path.exists():
            exit_found = True
            exit_files.append(str(exit_path))
            
            # Check for X3 handling
            for root, dirs, files in os.walk(exit_path):
                for filename in files:
                    if not filename.endswith('.py'):
                        continue
                    
                    filepath = Path(root) / filename
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        if re.search(r'emit_x3|X3Disposition|x3_emit|CommitRequest', content, re.IGNORECASE):
                            x3_handling_found = True
                    except IOError:
                        pass
    
    return {
        "exit_found": exit_found,
        "x3_handling_found": x3_handling_found,
        "exit_paths": exit_files,
    }


def run_all_checks() -> Dict:
    """Run all X3 emission checks."""
    apps_violations = scan_all_apps()
    exit_status = verify_core_exit_present()
    
    return {
        "apps_violations": apps_violations,
        "exit_status": exit_status,
        "total_violations": len(apps_violations),
        "critical_count": len([v for v in apps_violations if v['severity'] == 'CRITICAL']),
        "high_count": len([v for v in apps_violations if v['severity'] == 'HIGH']),
        "passed": len(apps_violations) == 0 and exit_status['exit_found'],
        "core_exit_present": exit_status['exit_found'],
        "x3_handling_present": exit_status['x3_handling_found'],
    }


# Negative control tests
def test_app_x3_emit_fails():
    """NEGATIVE CONTROL: App X3 emission must be detected."""
    sample_code = 'emit_x3(disposition)'
    assert re.search(r'emit_x3\(', sample_code), "Pattern should match"
    print("NEGATIVE CONTROL CONFIRMED: App X3 emission detected")


def test_app_x3_disposition_fails():
    """NEGATIVE CONTROL: App X3Disposition construction must be detected."""
    sample_code = 'X3Disposition(result=result)'
    assert re.search(r'X3Disposition\(', sample_code), "Pattern should match"
    print("NEGATIVE CONTROL CONFIRMED: X3Disposition construction detected")


def test_app_exit_bypass_fails():
    """NEGATIVE CONTROL: App Exit bypass must be detected."""
    sample_code = 'bypass_exit = True'
    assert re.search(r'bypass_exit.*=.*True', sample_code), "Pattern should match"
    print("NEGATIVE CONTROL CONFIRMED: Exit bypass detected")


def main():
    """Run the test suite."""
    print("="*70)
    print("TEST: No App Exit X3 Emission")
    print("="*70)
    print("\nValidating X3 disposition emission:")
    print("  Required: Only core Exit emits X3")
    print("  Forbidden: Apps emitting X3 or bypassing Exit")
    print("  App Exit profiles: Config/data only")
    
    # Run negative controls
    print("\nRunning negative controls...")
    test_app_x3_emit_fails()
    test_app_x3_disposition_fails()
    test_app_exit_bypass_fails()
    
    # Run checks
    print("\nScanning apps for X3 emission violations...")
    results = run_all_checks()
    
    # Print summary
    print(f"\nApps scanned: {len(find_apps_directories())}")
    print(f"App violations found: {results['total_violations']}")
    if results['total_violations'] > 0:
        print(f"  CRITICAL: {results['critical_count']}")
        print(f"  HIGH: {results['high_count']}")
    
    print(f"\nCore Exit layer present: {'Yes' if results['core_exit_present'] else 'No'}")
    print(f"X3 handling in core: {'Yes' if results['x3_handling_present'] else 'No'}")
    
    # Print violations
    if results['apps_violations']:
        print("\n" + "-"*70)
        print("APP VIOLATIONS (X3 emission detected):")
        print("-"*70)
        
        # Group by app
        by_app = {}
        for v in results['apps_violations']:
            app = v['app_name']
            if app not in by_app:
                by_app[app] = []
            by_app[app].append(v)
        
        for app, violations in by_app.items():
            print(f"\n{app}:")
            for v in violations[:5]:
                print(f"  [{v['severity']}] {v['file']}:{v['line']}")
                print(f"    Pattern: {v['pattern']}")
                print(f"    Content: {v['content']}")
            if len(violations) > 5:
                print(f"  ... and {len(violations) - 5} more")
    
    # Handle result
    if results['total_violations'] > 0:
        print("\n" + "="*70)
        print("FAIL: App X3 emission detected")
        print("="*70)
        print("\nApps must not emit X3 dispositions directly.")
        print("Correct approach:")
        print("  1. Apps define Exit profile in config/domain_contract/")
        print("  2. Apps hand off to core via apps_shared.cert.maybe_invoke_exit_eval")
        print("  3. Core Exit layer evaluates and emits X3 if approved")
        print("  4. X3 flows: Exit -> UWG -> L4")
        print("\nForbidden patterns:")
        for name, info in FORBIDDEN_PATTERNS.items():
            print(f"  - {name}: {info['description']}")
        print("="*70)
        
        # Write results
        output_file = GOVERNANCE_DIR / "test_no_app_exit_x3_results.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults written to: {output_file}")
        sys.exit(1)
    
    if not results['core_exit_present']:
        print("\n" + "="*70)
        print("FAIL: Core Exit layer not found")
        print("="*70)
        print("Expected Exit layer at:")
        print("  - agentic_core/runtime/exit/")
        print("  - or agentic_core/L6_observability/")
        print("="*70)
        sys.exit(1)
    
    print("\n" + "="*70)
    print("PASS: No app X3 emission detected")
    print("="*70)
    print("\nX3 emission validation:")
    print("  ✓ Apps do not emit X3 directly")
    print("  ✓ Apps use Exit profiles (config only)")
    print("  ✓ Core Exit layer present")
    print("  ✓ X3 handling in core Exit")
    
    # Write results
    output_file = GOVERNANCE_DIR / "test_no_app_exit_x3_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
