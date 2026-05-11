#!/usr/bin/env python3
"""
core_leakage_scan.py - Post-write hook to scan agentic_core for app-specific leakage.

Scans for forbidden literals and patterns:
- apps_lic, apps_rg, apps_qna, apps_research
- if app_id, app_id ==
- App-specific route names
- App-specific cache policy names
- App-specific send modes

Exit codes:
  0 - Clean (no unapproved leakage)
  2 - Leakage detected
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional

# Configuration
REPO_ROOT = Path("C:\\Git\\Agentic-Workflow-FRESH")
AGENTIC_CORE_PATH = REPO_ROOT / "agentic_core"
GOVERNANCE_DIR = REPO_ROOT / "artifacts" / "governance"
SCAN_OUTPUT_DIR = GOVERNANCE_DIR / "scans"

# Forbidden patterns in agentic_core
FORBIDDEN_PATTERNS = {
    "hardcoded_app_names": {
        "patterns": [
            r'["\']apps_lic["\']',
            r'["\']apps_rg["\']', 
            r'["\']apps_qna["\']',
            r'["\']apps_research["\']',
            r'["\']apps_exec["\']',
            r'["\']apps_rfp["\']',
            r'["\']apps_underwriting_ai["\']',
            r'["\']apps_architect["\']',
            r'["\']apps_eval["\']',
            r'["\']apps_repo_brief["\']',
        ],
        "severity": "HIGH",
        "description": "Hardcoded app name in core"
    },
    "app_id_branching": {
        "patterns": [
            r'if\s+app_id\s*==\s*["\']',
            r'app_id\s*==\s*["\']',
            r'if\s+tenant_id\s*==\s*["\']apps_',
            r'tenant_id\s*==\s*["\']apps_',
        ],
        "severity": "CRITICAL",
        "description": "App-specific branching in core"
    },
    "app_specific_routes": {
        "patterns": [
            r'["\']R4_MANAGED_DRAFT["\']',
            r'["\']R3R4_MANAGED_RESEARCH_THEN_DRAFT["\']',
            r'["\']R1_RESUME_GENERATION["\']',
            r'["\']R2_EXPEDITED["\']',
            r'["\']R3_RESEARCH_ONLY["\']',
        ],
        "severity": "HIGH",
        "description": "App-specific route name in core"
    },
    "app_specific_cache_policies": {
        "patterns": [
            r'["\']final_draft_r1a_bypass["\']',
            r'["\']final_draft_r1b_bypass["\']',
            r'["\']linkedin_send["\']',
            r'["\']email_outbox_send["\']',
            r'APPS_\w+_CACHE_BYPASS',
            r'APPS_\w+_CACHE_PROFILES',
        ],
        "severity": "MEDIUM",
        "description": "App-specific cache policy in core"
    },
    "app_specific_exit_gates": {
        "patterns": [
            r'APPS_LIC_EXIT_GATES',
            r'APPS_RG_EXIT_GATES',
            r'APPS_\w+_FORBIDDEN_ACTIONS',
            r'G21_APPS_\w+_SPECIFIC',
            r'G22_APPS_\w+_SPECIFIC',
        ],
        "severity": "HIGH",
        "description": "App-specific Exit gate configuration in core"
    },
    "app_specific_thresholds": {
        "patterns": [
            r'APPS_\w+_MIN_JUDGE_SCORE',
            r'APPS_\w+_MIN_CONFIDENCE',
            r'APPS_\w+_THRESHOLDS',
        ],
        "severity": "MEDIUM",
        "description": "App-specific threshold in core"
    }
}

# Allowlist categories
ALLOWLIST_CATEGORIES = {
    "TEST_ALLOWED": [
        r".*/tests/.*",
        r".*/test_.*\.py$",
        r".*/conftest\.py$",
        r".*/_test_.*\.py$",
    ],
    "DOC_ALLOWED": [
        r".*\.md$",
        r".*AGENTS\.md$",
        r".*README.*",
        r".*\.txt$",
        r".*\.rst$",
    ],
    "RECEIPT_ALLOWED": [
        r".*/artifacts/governance/.*",
        r".*/migration_receipts/.*",
        r".*/boundary_receipts/.*",
    ],
    "TEMPORARY_THIN_ADAPTER": [
        r".*/apps_\w+_.*_binding\.py$",
        r".*/u0_apps_\w+_binding\.py$",
    ],
    "GENERIC_READY": [
        r".*/package_driven_.*\.py$",
        r".*/generic_.*\.py$",
    ]
}


def matches_allowlist(filepath: str, category: str) -> bool:
    """Check if file matches allowlist category."""
    patterns = ALLOWLIST_CATEGORIES.get(category, [])
    for pattern in patterns:
        if re.search(pattern, filepath, re.IGNORECASE):
            return True
    return False


def get_allowlist_category(filepath: str) -> Optional[str]:
    """Determine the allowlist category for a file."""
    for category in ALLOWLIST_CATEGORIES:
        if matches_allowlist(filepath, category):
            return category
    return None


def scan_file(filepath: str) -> List[Dict]:
    """Scan a single file for forbidden patterns."""
    violations = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
    except (IOError, OSError) as e:
        return [{"error": f"Cannot read file: {e}"}]
    
    rel_path = str(filepath).replace(str(REPO_ROOT), "").lstrip("/\\")
    
    # Check allowlist
    allowlist_cat = get_allowlist_category(rel_path)
    
    for pattern_name, pattern_info in FORBIDDEN_PATTERNS.items():
        for pattern in pattern_info["patterns"]:
            for line_num, line in enumerate(lines, 1):
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    violation = {
                        "file": rel_path,
                        "line": line_num,
                        "pattern_name": pattern_name,
                        "pattern": pattern,
                        "severity": pattern_info["severity"],
                        "description": pattern_info["description"],
                        "content": line.strip()[:100],
                        "allowlist_category": allowlist_cat,
                        "match_text": match.group(0)
                    }
                    violations.append(violation)
    
    return violations


def scan_agentic_core() -> Dict:
    """Scan entire agentic_core directory."""
    all_violations = []
    files_scanned = 0
    files_with_violations = 0
    
    if not AGENTIC_CORE_PATH.exists():
        return {
            "error": f"agentic_core path not found: {AGENTIC_CORE_PATH}"
        }
    
    for root, dirs, files in os.walk(AGENTIC_CORE_PATH):
        # Skip __pycache__
        dirs[:] = [d for d in dirs if d != '__pycache__' and not d.startswith('.')]
        
        for filename in files:
            # Only scan Python and YAML files
            if not filename.endswith(('.py', '.yaml', '.yml', '.json')):
                continue
            
            filepath = Path(root) / filename
            files_scanned += 1
            
            violations = scan_file(str(filepath))
            
            # Filter out allowlisted violations
            non_allowlisted = [
                v for v in violations 
                if not v.get("allowlist_category") and "error" not in v
            ]
            
            if non_allowlisted:
                files_with_violations += 1
                all_violations.extend(non_allowlisted)
    
    return {
        "files_scanned": files_scanned,
        "files_with_violations": files_with_violations,
        "total_violations": len(all_violations),
        "violations": all_violations,
        "critical_count": len([v for v in all_violations if v.get("severity") == "CRITICAL"]),
        "high_count": len([v for v in all_violations if v.get("severity") == "HIGH"]),
        "medium_count": len([v for v in all_violations if v.get("severity") == "MEDIUM"]),
    }


def save_scan_results(results: Dict):
    """Save scan results to file."""
    SCAN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = str(Path(__file__).stat().st_mtime).split('.')[0]
    output_file = SCAN_OUTPUT_DIR / f"core_leakage_scan_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    return output_file


def main():
    """Main entry point."""
    print("CORE_LEAKAGE_SCAN: Scanning agentic_core for app-specific leakage...")
    
    # Run scan
    results = scan_agentic_core()
    
    # Save results
    output_file = save_scan_results(results)
    
    # Add metadata
    results["scan_output_file"] = str(output_file)
    results["timestamp"] = str(Path(__file__).stat().st_mtime)
    
    # Print summary
    print(f"\nFiles scanned: {results['files_scanned']}")
    print(f"Files with violations: {results['files_with_violations']}")
    print(f"Total violations: {results['total_violations']}")
    print(f"  Critical: {results['critical_count']}")
    print(f"  High: {results['high_count']}")
    print(f"  Medium: {results['medium_count']}")
    
    # Print violations
    if results['violations']:
        print("\n" + "="*70)
        print("VIOLATIONS DETECTED")
        print("="*70)
        
        for v in results['violations'][:20]:  # Limit output
            print(f"\n[{v['severity']}] {v['pattern_name']}")
            print(f"  File: {v['file']}:{v['line']}")
            print(f"  {v['description']}")
            print(f"  Content: {v['content']}")
        
        if len(results['violations']) > 20:
            print(f"\n... and {len(results['violations']) - 20} more violations")
        
        print("\n" + "="*70)
        print("These violations indicate app-specific logic in agentic_core.")
        print("Classification:")
        print("  CRITICAL: App branching logic - must migrate immediately")
        print("  HIGH: App-specific constants - move to apps_*/config/")
        print("  MEDIUM: App-specific config - use profile refs")
        print("="*70)
        print(f"\nFull report: {output_file}")
        
        # Exit with error if critical or high violations exist
        if results['critical_count'] > 0 or results['high_count'] > 0:
            sys.exit(2)
    else:
        print("\nCORE_LEAKAGE_SCAN: No app-specific leakage detected.")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
