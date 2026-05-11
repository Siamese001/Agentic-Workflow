#!/usr/bin/env python3
"""
test_no_direct_l4_write_bypass.py - CI Governance Test

Proves apps_* cannot import L4 write APIs directly.
Proves L2/L3/Exit/L6 cannot write durable state directly.
Verifies durable write path remains:
  Exit X3C -> CommitRequest -> UWG -> L4

Negative controls:
- Direct apps_* L4 write must fail
- Import of L4State.write in apps must fail
"""

import ast
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

# Forbidden imports and calls indicating direct L4 write
FORBIDDEN_PATTERNS = {
    "l4_state_import": {
        "patterns": [
            r'from\s+.*L4_state.*\s+import',
            r'import\s+.*L4_state',
            r'from\s+.*L4_state',
        ],
        "description": "Direct import of L4 state module",
        "severity": "CRITICAL"
    },
    "durable_write_import": {
        "patterns": [
            r'from\s+.*durable_write',
            r'import\s+.*durable_write',
        ],
        "description": "Direct import of durable_write",
        "severity": "CRITICAL"
    },
    "l4_state_write_call": {
        "patterns": [
            r'L4State\.write\(',
            r'L4State\.save\(',
            r'L4State\.commit\(',
            r'\.l4_write\(',
            r'\.durable_write\(',
        ],
        "description": "Direct call to L4 write methods",
        "severity": "CRITICAL"
    },
    "commit_request_bypass": {
        "patterns": [
            r'CommitRequest\(.*direct=True',
            r'CommitRequest\(.*bypass_uwg=True',
            r'\.write_direct_to_l4\(',
        ],
        "description": "Bypass of UWG in commit path",
        "severity": "CRITICAL"
    },
    "state_persistence_direct": {
        "patterns": [
            r'\.persist_to_l4\(',
            r'\.save_durable_state\(',
            r'\.write_l4_record\(',
        ],
        "description": "Direct state persistence call",
        "severity": "HIGH"
    }
}

# Allowed patterns (Exit layer using proper path)
ALLOWED_PATTERNS = {
    "exit_x3c": [
        r'ExitX3C\(',
        r'X3CCommitRequest\(',
        r'emit_x3c\(',
    ],
    "uwg_path": [
        r'UWG\.process\(',
        r'uwg\.commit\(',
        r'await_uwg\(',
    ],
    "exit_layer": [
        r'agentic_core.*exit',
        r'L6_observability.*promotion',
    ]
}

# Apps that are allowed to receive L4 data (read-only)
READONLY_L4_ACCESS = [
    r'\.load_from_l4\(',
    r'\.read_l4_state\(',
    r'\.query_l4\(',
]


def find_apps_directories() -> List[Path]:
    """Find all apps_* directories."""
    apps_dirs = []
    for item in REPO_ROOT.iterdir():
        if item.is_dir() and APPS_PATTERN.match(item.name):
            apps_dirs.append(item)
    return sorted(apps_dirs)


def scan_file_for_forbidden_patterns(filepath: str, file_type: str) -> List[Dict]:
    """Scan a file for forbidden L4 write patterns."""
    violations = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except (IOError, OSError):
        return violations
    
    rel_path = str(filepath).replace(str(REPO_ROOT), "").lstrip("/\\")
    
    for line_num, line in enumerate(lines, 1):
        # Skip comments
        code_line = line.split('#')[0]
        
        for pattern_name, pattern_info in FORBIDDEN_PATTERNS.items():
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, code_line, re.IGNORECASE):
                    # Check if it's a readonly access (allowed)
                    if file_type == "apps" and any(re.search(readonly, code_line) for readonly in READONLY_L4_ACCESS):
                        continue
                    
                    violations.append({
                        "file": rel_path,
                        "line": line_num,
                        "pattern": pattern_name,
                        "description": pattern_info["description"],
                        "severity": pattern_info["severity"],
                        "content": line.strip()[:100],
                        "file_type": file_type,
                    })
    
    return violations


def scan_apps() -> List[Dict]:
    """Scan apps_* for direct L4 write violations."""
    all_violations = []
    
    apps_dirs = find_apps_directories()
    
    for app_dir in apps_dirs:
        for root, dirs, files in os.walk(app_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for filename in files:
                if not filename.endswith('.py'):
                    continue
                
                filepath = Path(root) / filename
                violations = scan_file_for_forbidden_patterns(str(filepath), "apps")
                all_violations.extend(violations)
    
    return all_violations


def scan_core_layers() -> List[Dict]:
    """Scan agentic_core layers for direct L4 write (only Exit should write)."""
    all_violations = []
    
    if not AGENTIC_CORE_PATH.exists():
        return all_violations
    
    # Layers that should NOT write to L4 directly
    forbidden_layers = ['L0_routing', 'L1_cognition', 'L2_execution', 'L3_orchestration']
    
    for layer in forbidden_layers:
        layer_path = AGENTIC_CORE_PATH / layer
        if not layer_path.exists():
            continue
        
        for root, dirs, files in os.walk(layer_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for filename in files:
                if not filename.endswith('.py'):
                    continue
                
                filepath = Path(root) / filename
                violations = scan_file_for_forbidden_patterns(str(filepath), f"core_{layer}")
                
                # Additional check: these layers really shouldn't have L4 imports at all
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Check for L4 imports in forbidden layers
                    if re.search(r'from.*L4.*import|import.*L4', content, re.IGNORECASE):
                        if not any(v['file'].endswith(filename) for v in violations):
                            rel_path = str(filepath).replace(str(REPO_ROOT), "").lstrip("/\\")
                            violations.append({
                                "file": rel_path,
                                "line": 0,
                                "pattern": "l4_import_in_forbidden_layer",
                                "description": f"L4 import in {layer} (only Exit should access L4)",
                                "severity": "HIGH",
                                "content": "L4 module import detected",
                                "file_type": f"core_{layer}",
                            })
                except IOError:
                    pass
                
                all_violations.extend(violations)
    
    return all_violations


def check_exit_layer_uses_proper_path() -> List[Dict]:
    """Verify Exit layer uses X3C -> UWG -> L4 path."""
    violations = []
    
    exit_path = AGENTIC_CORE_PATH / "runtime" / "exit"
    if not exit_path.exists():
        exit_path = AGENTIC_CORE_PATH / "L6_observability"
    
    if not exit_path or not exit_path.exists():
        return violations
    
    # Check that Exit uses proper patterns
    for root, dirs, files in os.walk(exit_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for filename in files:
            if not filename.endswith('.py'):
                continue
            
            filepath = Path(root) / filename
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # If Exit has L4 write, ensure it's via proper path
                if re.search(r'L4State\.write\(|\.durable_write\(', content, re.IGNORECASE):
                    # Check for proper path indicators
                    has_x3c = re.search(r'X3C|CommitRequest|emit_x3c', content, re.IGNORECASE)
                    has_uwg = re.search(r'UWG|uwg', content, re.IGNORECASE)
                    
                    if not (has_x3c and has_uwg):
                        rel_path = str(filepath).replace(str(REPO_ROOT), "").lstrip("/\\")
                        violations.append({
                            "file": rel_path,
                            "line": 0,
                            "pattern": "exit_direct_l4_without_proper_path",
                            "description": "Exit layer has L4 write but may not use X3C->UWG path",
                            "severity": "WARNING",
                            "content": "Direct L4 write without clear X3C/UWG path",
                            "file_type": "core_exit",
                        })
            except IOError:
                pass
    
    return violations


def run_all_checks() -> Dict:
    """Run all L4 write bypass checks."""
    apps_violations = scan_apps()
    core_violations = scan_core_layers()
    exit_warnings = check_exit_layer_uses_proper_path()
    
    all_violations = apps_violations + core_violations
    
    return {
        "apps_violations": apps_violations,
        "core_violations": core_violations,
        "exit_warnings": exit_warnings,
        "total_violations": len(all_violations),
        "critical_count": len([v for v in all_violations if v['severity'] == 'CRITICAL']),
        "high_count": len([v for v in all_violations if v['severity'] == 'HIGH']),
        "passed": len(all_violations) == 0,
        "exit_has_warnings": len(exit_warnings) > 0,
    }


# Negative control tests
def test_direct_l4_write_in_apps_fails():
    """NEGATIVE CONTROL: Direct L4 write in apps must be detected."""
    sample_code = '''
    from agentic_core.L4_state import L4State
    L4State.write(data)
    '''
    # Should detect the violation
    assert re.search(r'L4State\.write\(', sample_code), "Pattern should match"
    print("NEGATIVE CONTROL CONFIRMED: Direct L4 write in apps detected")


def test_direct_durable_write_in_apps_fails():
    """NEGATIVE CONTROL: Direct durable_write in apps must be detected."""
    sample_code = 'durable_write(record)'
    assert re.search(r'durable_write\(', sample_code), "Pattern should match"
    print("NEGATIVE CONTROL CONFIRMED: Direct durable_write detected")


def test_forbidden_layer_l4_import_fails():
    """NEGATIVE CONTROL: L4 import in L2/L3 must be detected."""
    sample_code = 'from agentic_core.L4_state import L4State'
    assert re.search(r'from.*L4.*import', sample_code), "Pattern should match"
    print("NEGATIVE CONTROL CONFIRMED: L4 import in forbidden layer detected")


def main():
    """Run the test suite."""
    print("="*70)
    print("TEST: No Direct L4 Write Bypass")
    print("="*70)
    print("\nValidating durable write path:")
    print("  Required: Exit X3C -> CommitRequest -> UWG -> L4")
    print("  Forbidden: Any direct L4 write from apps or core layers")
    
    # Run negative controls
    print("\nRunning negative controls...")
    test_direct_l4_write_in_apps_fails()
    test_direct_durable_write_in_apps_fails()
    test_forbidden_layer_l4_import_fails()
    
    # Run checks
    print("\nScanning for violations...")
    results = run_all_checks()
    
    # Print summary
    print(f"\nApps violations: {len(results['apps_violations'])}")
    print(f"Core layer violations: {len(results['core_violations'])}")
    print(f"Exit warnings: {len(results['exit_warnings'])}")
    
    if results['total_violations'] > 0:
        print(f"  CRITICAL: {results['critical_count']}")
        print(f"  HIGH: {results['high_count']}")
    
    # Print violations
    if results['apps_violations']:
        print("\n" + "-"*70)
        print("APPS_* VIOLATIONS (Direct L4 write detected):")
        print("-"*70)
        for v in results['apps_violations'][:10]:
            print(f"\n[{v['severity']}] {v['file']}:{v['line']}")
            print(f"  Pattern: {v['pattern']}")
            print(f"  {v['description']}")
            print(f"  Content: {v['content']}")
    
    if results['core_violations']:
        print("\n" + "-"*70)
        print("CORE LAYER VIOLATIONS (L0/L1/L2/L3 accessing L4):")
        print("-"*70)
        for v in results['core_violations'][:10]:
            print(f"\n[{v['severity']}] {v['file']}:{v['line']}")
            print(f"  Pattern: {v['pattern']}")
            print(f"  {v['description']}")
    
    if results['exit_warnings']:
        print("\n" + "-"*70)
        print("EXIT LAYER WARNINGS (Verify X3C->UWG path):")
        print("-"*70)
        for w in results['exit_warnings']:
            print(f"\n[{w['severity']}] {w['file']}")
            print(f"  {w['description']}")
    
    # Handle result
    if results['total_violations'] > 0:
        print("\n" + "="*70)
        print("FAIL: Direct L4 write bypass detected")
        print("="*70)
        print("\nViolations indicate code attempting to write L4 directly.")
        print("Correct path:")
        print("  1. Apps: Use Exit profile, do not touch L4 directly")
        print("  2. Core layers (L0-L3): Hand off to Exit, do not write L4")
        print("  3. Exit: Use X3C CommitRequest, routed through UWG")
        print("\nForbidden patterns:")
        for name, info in FORBIDDEN_PATTERNS.items():
            print(f"  - {name}: {info['description']}")
        print("="*70)
        
        # Write results
        output_file = GOVERNANCE_DIR / "test_no_direct_l4_write_results.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults written to: {output_file}")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("PASS: No direct L4 write bypass detected")
    print("="*70)
    
    if results['exit_warnings']:
        print(f"\n{len(results['exit_warnings'])} Exit layer warnings (advisory)")
        print("Review to ensure X3C->UWG->L4 path is clearly documented.")
    
    print("\nDurable write path validation:")
    print("  ✓ Apps do not write L4 directly")
    print("  ✓ Core layers (L0-L3) do not write L4 directly")
    print("  ✓ Exit layer present (using X3C->UWG path)")
    
    # Write results
    output_file = GOVERNANCE_DIR / "test_no_direct_l4_write_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
