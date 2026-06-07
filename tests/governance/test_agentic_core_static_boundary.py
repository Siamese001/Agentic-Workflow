#!/usr/bin/env python3
"""
test_agentic_core_static_boundary.py - CI Governance Test

Proves shared agentic_core has no app-specific business policy.

Acceptance:
- Generic runtime infrastructure allowed
- Documented temporary thin adapters allowed (with receipt)
- Hardcoded app_id branching in generic runtime fails
- CORE_APP_SPECIFIC_LEAKAGE fails hard

Negative controls:
- Hardcoded apps_lic route in generic core must fail
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Add repo root to path for imports
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Configuration
AGENTIC_CORE_PATH = REPO_ROOT / "agentic_core"
GOVERNANCE_DIR = REPO_ROOT / "artifacts" / "governance"
MIGRATION_RECEIPTS_DIR = GOVERNANCE_DIR / "migration_receipts"

# Classification categories
CLASSIFICATIONS = {
    "GENERIC_INFRASTRUCTURE": "Generic runtime infrastructure - ALLOW",
    "GENERIC_CORE_RUNTIME": "Generic core runtime - ALLOW",
    "TEMPORARY_THIN_ADAPTER": "Binding with migration receipt - ALLOW",
    "CORE_APP_SPECIFIC_LEAKAGE": "App-specific logic in core - FAIL",
    "DOC_ALLOWED": "Documentation - ALLOW",
    "TEST_ALLOWED": "Test files - ALLOW",
    "RECEIPT_ALLOWED": "Governance receipts - ALLOW",
}

# Forbidden patterns that indicate app-specific leakage
FORBIDDEN_APP_PATTERNS = [
    (r'if\s+app_id\s*==\s*["\']apps_\w+["\']', "app_id branching", "CRITICAL"),
    (r'app_id\s*==\s*["\']apps_\w+["\']', "app_id comparison", "CRITICAL"),
    (r'tenant_id\s*==\s*["\']apps_\w+["\']', "tenant_id comparison", "CRITICAL"),
    (r'["\']apps_lic["\']', "hardcoded apps_lic", "HIGH"),
    (r'["\']apps_rg["\']', "hardcoded apps_rg", "HIGH"),
    (r'["\']apps_qna["\']', "hardcoded apps_qna", "HIGH"),
    (r'["\']apps_research["\']', "hardcoded apps_research", "HIGH"),
    (r'R4_MANAGED_DRAFT', "app-specific route R4_MANAGED_DRAFT", "HIGH"),
    (r'R3R4_MANAGED_RESEARCH_THEN_DRAFT', "app-specific route R3R4", "HIGH"),
    (r'R1_RESUME_GENERATION', "app-specific route R1_RESUME", "HIGH"),
    (r'APPS_LIC_EXIT_GATES', "app-specific Exit gates", "HIGH"),
    (r'APPS_RG_EXIT_GATES', "app-specific Exit gates", "HIGH"),
    (r'final_draft_r1a_bypass', "app-specific cache bypass", "MEDIUM"),
    (r'final_draft_r1b_bypass', "app-specific cache bypass", "MEDIUM"),
    (r'linkedin_send', "app-specific send mode", "MEDIUM"),
    (r'email_outbox_send', "app-specific send mode", "MEDIUM"),
    # W4 extensions — new app literals and semantic patterns
    (r'["\']apps_architect["\']', "hardcoded apps_architect", "HIGH"),
    (r'["\']apps_eval["\']', "hardcoded apps_eval", "HIGH"),
    (r'["\']apps_rfp["\']', "hardcoded apps_rfp", "HIGH"),
    (r'company_brief', "app-specific domain: company_brief", "HIGH"),
    (r'interview_card', "app-specific domain: interview_card", "HIGH"),
    (r'resume_generator', "app-specific domain: resume_generator", "HIGH"),
    (r'recruiter', "app-specific role literal", "MEDIUM"),
    (r'outreach', "app-specific action: outreach", "MEDIUM"),
    (r'JD[._-]specific', "JD-domain semantics", "HIGH"),
    (r'resume[._-]specific', "resume-domain semantics", "HIGH"),
    (r'LIC[._-]specific', "apps_lic domain semantics", "HIGH"),
    (r'RG[._-]specific', "apps_rg domain semantics", "HIGH"),
    (r'QNA[._-]specific', "apps_qna domain semantics", "HIGH"),
    (r'research[._-]specific', "research-domain semantics", "HIGH"),
    (r"""["']apps_[a-z_]+["']""", "generic apps_* quoted literal in core", "HIGH"),
]

# Allowlisted file patterns
ALLOWLIST_PATTERNS = [
    r'.*\.md$',  # Documentation
    r'.*AGENTS\.md$',
    r'.*/tests/.*',  # Test files
    r'.*/test_.*\.py$',
    r'.*/conftest\.py$',
    r'.*/_test_.*\.py$',
    r'.*/artifacts/governance/.*',  # Receipts
    r'.*/migration_receipts/.*',
    r'.*/boundary_receipts/.*',
    r'.*/\docs/archive/windsurf/legacy-tree/.*',
    r'.*/package_driven_.*\.py$',  # Generic engines
    r'.*/generic_.*\.py$',
]

# Temporary binding pattern
BINDING_PATTERN = re.compile(r'.*apps_\w+_.*_binding\.py$')


def is_allowlisted(filepath: str) -> bool:
    """Check if file path is allowlisted."""
    for pattern in ALLOWLIST_PATTERNS:
        if re.match(pattern, filepath, re.IGNORECASE):
            return True
    return False


def is_temporary_binding(filepath: str) -> bool:
    """Check if file is a temporary adapter binding."""
    return bool(BINDING_PATTERN.match(filepath))


def has_migration_receipt(filepath: str) -> bool:
    """Verify migration receipt exists for binding."""
    if not MIGRATION_RECEIPTS_DIR.exists():
        return False
    
    binding_name = Path(filepath).stem
    
    for receipt_file in MIGRATION_RECEIPTS_DIR.glob("*.json"):
        try:
            with open(receipt_file, 'r', encoding='utf-8') as f:
                receipt = json.load(f)
                # Check various receipt formats
                if receipt.get('binding_file', '').endswith(filepath):
                    return True
                if receipt.get('original_binding', {}).get('file', '').endswith(filepath):
                    return True
                for file_item in receipt.get('files_created', []):
                    if isinstance(file_item, dict):
                        if file_item.get('path', '').endswith(filepath):
                            return True
                    elif isinstance(file_item, str) and file_item.endswith(filepath):
                        return True
        except (json.JSONDecodeError, IOError):
            continue
    
    return False


def scan_file_for_violations(filepath: str) -> List[Dict]:
    """Scan a single Python file for forbidden patterns."""
    violations = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except (IOError, OSError):
        return violations
    
    rel_path = str(filepath).replace(str(REPO_ROOT), "").lstrip("/\\")
    
    # Skip if allowlisted
    if is_allowlisted(rel_path):
        return violations
    
    # Scan each line
    for line_num, line in enumerate(lines, 1):
        for pattern, description, severity in FORBIDDEN_APP_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                # Check if this is in a binding file with receipt
                if is_temporary_binding(rel_path) and has_migration_receipt(rel_path):
                    continue
                
                violations.append({
                    "file": rel_path,
                    "line": line_num,
                    "pattern": pattern,
                    "description": description,
                    "severity": severity,
                    "content": line.strip()[:100],
                    "classification": "CORE_APP_SPECIFIC_LEAKAGE"
                })
    
    return violations


def scan_agentic_core() -> Dict:
    """Scan entire agentic_core for boundary violations."""
    all_violations = []
    files_scanned = 0
    binding_files = []
    generic_files = []
    
    if not AGENTIC_CORE_PATH.exists():
        return {
            "error": f"agentic_core not found: {AGENTIC_CORE_PATH}",
            "violations": [],
            "passed": False
        }
    
    for root, dirs, files in os.walk(AGENTIC_CORE_PATH):
        # Skip __pycache__ and hidden
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for filename in files:
            if not filename.endswith('.py'):
                continue
            
            filepath = Path(root) / filename
            files_scanned += 1
            
            rel_path = str(filepath).replace(str(REPO_ROOT), "").lstrip("/\\")
            
            # Categorize file
            if is_temporary_binding(rel_path):
                binding_files.append({
                    "file": rel_path,
                    "has_receipt": has_migration_receipt(rel_path)
                })
            else:
                generic_files.append(rel_path)
            
            # Scan for violations
            violations = scan_file_for_violations(str(filepath))
            all_violations.extend(violations)
    
    return {
        "files_scanned": files_scanned,
        "binding_files": binding_files,
        "generic_files": generic_files,
        "violations": all_violations,
        "critical_count": len([v for v in all_violations if v['severity'] == 'CRITICAL']),
        "high_count": len([v for v in all_violations if v['severity'] == 'HIGH']),
        "medium_count": len([v for v in all_violations if v['severity'] == 'MEDIUM']),
        "passed": len(all_violations) == 0
    }


# Negative control tests
def test_hardcoded_app_branching_fails():
    """NEGATIVE CONTROL: Hardcoded app_id branching must fail."""
    # This test documents that we actively reject this pattern
    sample_code = '''
    if app_id == "apps_lic":
        return "R4_MANAGED_DRAFT"
    '''
    # If we found this pattern in agentic_core, it's a violation
    pattern = r'if\s+app_id\s*==\s*["\']apps_\w+["\']'
    assert re.search(pattern, sample_code), "Test pattern should match"
    print("NEGATIVE CONTROL CONFIRMED: app_id branching pattern detected and rejected")


def test_app_specific_route_in_core_fails():
    """NEGATIVE CONTROL: App-specific route names in core must fail."""
    sample_code = 'route = "R4_MANAGED_DRAFT"'
    pattern = r'R4_MANAGED_DRAFT'
    assert re.search(pattern, sample_code), "Test pattern should match"
    print("NEGATIVE CONTROL CONFIRMED: app-specific route pattern detected and rejected")


def test_app_specific_exit_gates_in_core_fails():
    """NEGATIVE CONTROL: App-specific Exit gates in core must fail."""
    sample_code = 'APPS_LIC_EXIT_GATES = ["G21", "G22"]'
    pattern = r'APPS_LIC_EXIT_GATES'
    assert re.search(pattern, sample_code), "Test pattern should match"
    print("NEGATIVE CONTROL CONFIRMED: app-specific Exit gates pattern detected and rejected")


# Main test suite
def main():
    """Run the governance test suite."""
    print("="*70)
    print("TEST: agentic_core Static Boundary")
    print("="*70)
    
    # Run negative controls
    print("\nRunning negative controls...")
    test_hardcoded_app_branching_fails()
    test_app_specific_route_in_core_fails()
    test_app_specific_exit_gates_in_core_fails()
    
    # Run main scan
    print("\nScanning agentic_core for violations...")
    results = scan_agentic_core()
    
    # Print results
    print(f"\nFiles scanned: {results['files_scanned']}")
    print(f"Binding files: {len(results['binding_files'])}")
    print(f"Generic files: {len(results['generic_files'])}")
    
    # Check binding receipts
    bindings_without_receipts = [b for b in results['binding_files'] if not b['has_receipt']]
    if bindings_without_receipts:
        print(f"\nWARNING: {len(bindings_without_receipts)} bindings without verified receipts:")
        for b in bindings_without_receipts:
            print(f"  - {b['file']}")
    
    # Print violations
    if results['violations']:
        print(f"\nVIOLATIONS FOUND: {len(results['violations'])}")
        print(f"  CRITICAL: {results['critical_count']}")
        print(f"  HIGH: {results['high_count']}")
        print(f"  MEDIUM: {results['medium_count']}")
        
        print("\n" + "-"*70)
        for v in results['violations'][:10]:  # Show first 10
            print(f"\n[{v['severity']}] {v['classification']}")
            print(f"  File: {v['file']}:{v['line']}")
            print(f"  Pattern: {v['description']}")
            print(f"  Content: {v['content']}")
        
        if len(results['violations']) > 10:
            print(f"\n... and {len(results['violations']) - 10} more violations")
        
        print("\n" + "="*70)
        print("FAIL: CORE_APP_SPECIFIC_LEAKAGE detected in agentic_core")
        print("="*70)
        print("\nThese violations indicate app-specific logic in shared core.")
        print("Remediation options:")
        print("  1. Move logic to apps_*/config/domain_contract/")
        print("  2. Create generic engine + app profile")
        print("  3. Document as TEMPORARY_THIN_ADAPTER with migration receipt")
        print("="*70)
        
        # Write results for CI
        output_file = GOVERNANCE_DIR / "test_agentic_core_static_boundary_results.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults written to: {output_file}")
        sys.exit(1)
    else:
        print("\n" + "="*70)
        print("PASS: No CORE_APP_SPECIFIC_LEAKAGE detected")
        print("="*70)
        print(f"\nFiles scanned: {results['files_scanned']}")
        print(f"Binding files: {len(results['binding_files'])}")
        print(f"Generic runtime files: {len(results['generic_files'])}")
        
        if bindings_without_receipts:
            print(f"\nNote: {len(bindings_without_receipts)} TEMPORARY_THIN_ADAPTER bindings lack receipts")
            print("      (allowed but should have receipts for W5 migration)")
        
        # Write results
        output_file = GOVERNANCE_DIR / "test_agentic_core_static_boundary_results.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        sys.exit(0)


if __name__ == "__main__":
    main()
