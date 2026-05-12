#!/usr/bin/env python3
"""
test_no_app_specific_literals_in_core.py - CI Governance Test

Scans agentic_core for forbidden app-specific literals/patterns.
Classifies matches and fails CORE_APP_SPECIFIC_LEAKAGE.

Classification categories:
- TEST_ALLOWED
- DOC_ALLOWED  
- RECEIPT_ALLOWED
- TEMPORARY_THIN_ADAPTER
- GENERIC_READY
- CORE_APP_SPECIFIC_LEAKAGE (FAIL)

Negative controls:
- Hardcoded apps_lic in generic core must fail
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Configuration
AGENTIC_CORE_PATH = REPO_ROOT / "agentic_core"
GOVERNANCE_DIR = REPO_ROOT / "artifacts" / "governance"
MIGRATION_RECEIPTS_DIR = GOVERNANCE_DIR / "migration_receipts"

# Classification categories
CATEGORIES = {
    "TEST_ALLOWED": "Test files - exempt from literal restrictions",
    "DOC_ALLOWED": "Documentation - exempt from literal restrictions", 
    "RECEIPT_ALLOWED": "Governance receipts - exempt",
    "TEMPORARY_THIN_ADAPTER": "Binding files with migration receipt - exempt",
    "GENERIC_READY": "Generic engines using profiles - allowed",
    "CORE_APP_SPECIFIC_LEAKAGE": "App literals in generic code - FAIL",
}

# Forbidden literal patterns
# Order matters: CRITICAL patterns (branching) must come before HIGH patterns (simple literals)
# to ensure proper detection priority in the negative control tests
FORBIDDEN_LITERALS = {
    # CRITICAL: Branching patterns (must be first for priority matching)
    "app_id_branching": {
        "patterns": [r'if\s+app_id\s*==\s*["\']', r'app_id\s*==\s*["\']'],
        "description": "app_id equality check",
        "severity": "CRITICAL"
    },
    "tenant_id_branching": {
        "patterns": [r'if\s+tenant_id\s*==\s*["\']', r'tenant_id\s*==\s*["\']apps_'],
        "description": "tenant_id equality check with apps",
        "severity": "CRITICAL"
    },
    # HIGH: Simple app name literals (checked after branching patterns)
    "apps_lic": {
        "patterns": [r'["\']apps_lic["\']', r'apps_lic\b'],
        "description": "apps_lic hardcoded",
        "severity": "HIGH"
    },
    "apps_rg": {
        "patterns": [r'["\']apps_rg["\']', r'apps_rg\b'],
        "description": "apps_rg hardcoded",
        "severity": "HIGH"
    },
    "apps_qna": {
        "patterns": [r'["\']apps_qna["\']', r'apps_qna\b'],
        "description": "apps_qna hardcoded",
        "severity": "HIGH"
    },
    "apps_research": {
        "patterns": [r'["\']apps_research["\']', r'apps_research\b'],
        "description": "apps_research hardcoded",
        "severity": "HIGH"
    },
    "app_specific_routes": {
        "patterns": [
            r'["\']R4_MANAGED_DRAFT["\']',
            r'["\']R3R4_MANAGED_RESEARCH_THEN_DRAFT["\']',
            r'["\']R1_RESUME_GENERATION["\']',
            r'["\']R2_EXPEDITED["\']',
            r'["\']R3_RESEARCH_ONLY["\']',
            r'["\']R5_RESUME_FROM_PROFILE["\']',
        ],
        "description": "app-specific route name",
        "severity": "HIGH"
    },
    "app_specific_cache": {
        "patterns": [
            r'["\']final_draft_r1a_bypass["\']',
            r'["\']final_draft_r1b_bypass["\']',
            r'["\']linkedin_send["\']',
            r'["\']email_outbox_send["\']',
        ],
        "description": "app-specific cache/send mode",
        "severity": "MEDIUM"
    },
    "app_specific_constants": {
        "patterns": [
            r'APPS_LIC_\w+\s*=',
            r'APPS_RG_\w+\s*=',
            r'APPS_QNA_\w+\s*=',
        ],
        "description": "app-specific constant definition",
        "severity": "HIGH"
    }
}

# File classification patterns
CLASSIFICATION_PATTERNS = {
    "TEST_ALLOWED": [
        r'.*/tests/.*\.py$',
        r'.*/test_.*\.py$',
        r'.*/conftest\.py$',
        r'.*/_test_.*\.py$',
    ],
    "DOC_ALLOWED": [
        r'.*\.md$',
        r'.*\.txt$',
        r'.*\.rst$',
    ],
    "RECEIPT_ALLOWED": [
        r'.*/artifacts/governance/.*',
        r'.*/migration_receipts/.*',
        r'.*/boundary_receipts/.*',
        r'.*/customization_receipts/.*',
    ],
    "TEMPORARY_THIN_ADAPTER": [
        r'.*/apps_\w+_.*_binding\.py$',
        r'.*/u0_apps_\w+_binding\.py$',
    ],
    "GENERIC_READY": [
        r'.*/package_driven_.*\.py$',
        r'.*/generic_.*\.py$',
    ]
}


def classify_file(filepath: str) -> Optional[str]:
    """Classify file by path patterns."""
    for category, patterns in CLASSIFICATION_PATTERNS.items():
        for pattern in patterns:
            if re.match(pattern, filepath, re.IGNORECASE):
                return category
    return None


def has_migration_receipt(filepath: str) -> bool:
    """Check if binding file has migration receipt."""
    if not MIGRATION_RECEIPTS_DIR.exists():
        return False
    
    binding_name = Path(filepath).stem
    
    for receipt_file in MIGRATION_RECEIPTS_DIR.glob("*.json"):
        try:
            with open(receipt_file, 'r', encoding='utf-8') as f:
                receipt = json.load(f)
                # Check if this binding is documented
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


def scan_file(filepath: str) -> List[Dict]:
    """Scan a single file for forbidden literals."""
    matches = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except (IOError, OSError):
        return matches
    
    rel_path = str(filepath).replace(str(REPO_ROOT), "").lstrip("/\\")
    
    # Classify file
    classification = classify_file(rel_path)
    
    # Scan for literals
    for line_num, line in enumerate(lines, 1):
        for literal_name, literal_info in FORBIDDEN_LITERALS.items():
            for pattern in literal_info["patterns"]:
                if re.search(pattern, line, re.IGNORECASE):
                    # Determine effective classification
                    effective_classification = classification
                    
                    # If it's a binding file, check for receipt
                    if classification == "TEMPORARY_THIN_ADAPTER":
                        if not has_migration_receipt(rel_path):
                            effective_classification = "TEMPORARY_THIN_ADAPTER_NO_RECEIPT"
                    
                    # If no classification, it's generic code
                    if not effective_classification:
                        effective_classification = "CORE_APP_SPECIFIC_LEAKAGE"
                    
                    matches.append({
                        "file": rel_path,
                        "line": line_num,
                        "literal_type": literal_name,
                        "pattern": pattern,
                        "description": literal_info["description"],
                        "severity": literal_info["severity"],
                        "content": line.strip()[:100],
                        "path_classification": classification,
                        "effective_classification": effective_classification,
                    })
    
    return matches


def scan_all_files() -> Dict:
    """Scan all agentic_core files."""
    all_matches = []
    files_by_classification = {
        "TEST_ALLOWED": [],
        "DOC_ALLOWED": [],
        "RECEIPT_ALLOWED": [],
        "TEMPORARY_THIN_ADAPTER": [],
        "TEMPORARY_THIN_ADAPTER_NO_RECEIPT": [],
        "GENERIC_READY": [],
        "GENERIC_UNCLASSIFIED": [],
        "CORE_APP_SPECIFIC_LEAKAGE": [],
    }
    
    if not AGENTIC_CORE_PATH.exists():
        return {"error": "agentic_core not found", "matches": [], "passed": False}
    
    for root, dirs, files in os.walk(AGENTIC_CORE_PATH):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for filename in files:
            if not filename.endswith(('.py', '.yaml', '.yml', '.md')):
                continue
            
            filepath = Path(root) / filename
            rel_path = str(filepath).replace(str(REPO_ROOT), "").lstrip("/\\")
            
            # Classify file
            classification = classify_file(rel_path)
            
            if classification:
                files_by_classification[classification].append(rel_path)
            else:
                files_by_classification["GENERIC_UNCLASSIFIED"].append(rel_path)
            
            # Scan for matches
            matches = scan_file(str(filepath))
            all_matches.extend(matches)
    
    # Categorize matches by effective classification
    leakage_matches = [m for m in all_matches if m["effective_classification"] == "CORE_APP_SPECIFIC_LEAKAGE"]
    
    return {
        "total_files_scanned": sum(len(v) for v in files_by_classification.values()),
        "files_by_classification": files_by_classification,
        "total_matches": len(all_matches),
        "matches_by_classification": {
            "TEST_ALLOWED": len([m for m in all_matches if m["effective_classification"] == "TEST_ALLOWED"]),
            "DOC_ALLOWED": len([m for m in all_matches if m["effective_classification"] == "DOC_ALLOWED"]),
            "RECEIPT_ALLOWED": len([m for m in all_matches if m["effective_classification"] == "RECEIPT_ALLOWED"]),
            "TEMPORARY_THIN_ADAPTER": len([m for m in all_matches if m["effective_classification"] == "TEMPORARY_THIN_ADAPTER"]),
            "TEMPORARY_THIN_ADAPTER_NO_RECEIPT": len([m for m in all_matches if m["effective_classification"] == "TEMPORARY_THIN_ADAPTER_NO_RECEIPT"]),
            "GENERIC_READY": len([m for m in all_matches if m["effective_classification"] == "GENERIC_READY"]),
            "CORE_APP_SPECIFIC_LEAKAGE": len(leakage_matches),
        },
        "leakage_matches": leakage_matches,
        "all_matches": all_matches,
        "passed": len(leakage_matches) == 0,
    }


# Negative control tests
def test_literal_classification():
    """NEGATIVE CONTROL: Verify literal detection works."""
    test_cases = [
        ('route = "apps_lic"', "apps_lic", True),
        ('if app_id == "apps_rg":', "app_id_branching", True),
        ('path = "/tests/test_foo.py"', None, False),  # Test file, exempt
    ]
    
    for code, expected_literal, should_match in test_cases:
        found = False
        matched_literal = None
        for literal_name, literal_info in FORBIDDEN_LITERALS.items():
            for pattern in literal_info["patterns"]:
                if re.search(pattern, code, re.IGNORECASE):
                    found = True
                    matched_literal = literal_name
                    break  # Exit pattern loop
            if found:
                break  # Exit literal_name loop after first match
        
        if should_match:
            assert found, f"Should have matched: {code}"
            if expected_literal:
                assert matched_literal == expected_literal, f"Expected {expected_literal}, got {matched_literal}"
        else:
            assert not found, f"Should not have matched: {code}"
    
    print("NEGATIVE CONTROL CONFIRMED: Literal classification working correctly")


def test_file_classification():
    """NEGATIVE CONTROL: Verify file classification works."""
    test_cases = [
        ("agentic_core/tests/test_foo.py", "TEST_ALLOWED"),
        ("agentic_core/AGENTS.md", "DOC_ALLOWED"),
        ("agentic_core/L0_routing/apps_lic_l0_binding.py", "TEMPORARY_THIN_ADAPTER"),
        ("agentic_core/L0_routing/package_driven_selector.py", "GENERIC_READY"),  # Generic engine
        ("agentic_core/L0_routing/generic_route_resolver.py", "GENERIC_READY"),  # Generic engine
    ]
    
    for filepath, expected in test_cases:
        result = classify_file(filepath)
        if expected:
            assert result == expected, f"Expected {expected}, got {result} for {filepath}"
        else:
            assert result is None, f"Expected None, got {result} for {filepath}"
    
    print("NEGATIVE CONTROL CONFIRMED: File classification working correctly")


def main():
    """Run the test suite."""
    print("="*70)
    print("TEST: No App-Specific Literals in Core")
    print("="*70)
    
    # Run negative controls
    print("\nRunning negative controls...")
    test_literal_classification()
    test_file_classification()
    
    # Run main scan
    print("\nScanning for forbidden literals...")
    results = scan_all_files()
    
    if "error" in results:
        print(f"ERROR: {results['error']}")
        sys.exit(1)
    
    # Print summary
    print(f"\nFiles scanned: {results['total_files_scanned']}")
    print("\nFiles by classification:")
    for cat, files in results['files_by_classification'].items():
        if files:
            print(f"  {cat}: {len(files)}")
    
    print(f"\nTotal literal matches: {results['total_matches']}")
    print("Matches by classification:")
    for cat, count in results['matches_by_classification'].items():
        status = "✓" if cat != "CORE_APP_SPECIFIC_LEAKAGE" else "✗"
        print(f"  {status} {cat}: {count}")
    
    # Handle leakage
    leakage = results['leakage_matches']
    if leakage:
        print("\n" + "="*70)
        print("FAIL: CORE_APP_SPECIFIC_LEAKAGE detected")
        print("="*70)
        
        # Group by severity
        critical = [m for m in leakage if m['severity'] == 'CRITICAL']
        high = [m for m in leakage if m['severity'] == 'HIGH']
        medium = [m for m in leakage if m['severity'] == 'MEDIUM']
        
        print(f"\nCRITICAL ({len(critical)}): App branching logic - must fix immediately")
        for m in critical[:5]:
            print(f"  {m['file']}:{m['line']} - {m['description']}")
        
        print(f"\nHIGH ({len(high)}): App-specific constants - must fix")
        for m in high[:5]:
            print(f"  {m['file']}:{m['line']} - {m['description']}")
        
        print(f"\nMEDIUM ({len(medium)}): App-specific config - should fix")
        for m in medium[:3]:
            print(f"  {m['file']}:{m['line']} - {m['description']}")
        
        if len(leakage) > 13:
            print(f"\n... and {len(leakage) - 13} more")
        
        print("\n" + "="*70)
        print("These are app-specific literals in generic core code.")
        print("Options:")
        print("  1. Move to apps_*/config/domain_contract/ profiles")
        print("  2. Use generic engine with profile refs")
        print("  3. Mark file as TEMPORARY_THIN_ADAPTER with receipt")
        print("="*70)
        
        # Write results
        output_file = GOVERNANCE_DIR / "test_no_app_specific_literals_results.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults written to: {output_file}")
        sys.exit(1)
    
    # Check for bindings without receipts
    no_receipt_count = results['matches_by_classification'].get('TEMPORARY_THIN_ADAPTER_NO_RECEIPT', 0)
    if no_receipt_count > 0:
        print(f"\nWARNING: {no_receipt_count} TEMPORARY_THIN_ADAPTER files lack receipts")
        print("  (Allowed but should be documented for W5 migration)")
    
    print("\n" + "="*70)
    print("PASS: No CORE_APP_SPECIFIC_LEAKAGE detected")
    print("="*70)
    print(f"\n{results['total_matches']} literals found in allowlisted categories:")
    for cat, count in results['matches_by_classification'].items():
        if cat != 'CORE_APP_SPECIFIC_LEAKAGE' and count > 0:
            print(f"  - {cat}: {count}")
    
    # Write results
    output_file = GOVERNANCE_DIR / "test_no_app_specific_literals_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
