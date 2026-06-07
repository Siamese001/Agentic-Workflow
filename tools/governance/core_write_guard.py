#!/usr/bin/env python3
"""
core_write_guard.py - Pre-write hook for agentic_core governance.

Blocks unsafe edits to agentic_core/ unless:
- Generic infrastructure
- Temporary thin adapter with 12-field migration receipt
- Documentation/tests/receipts

Exit codes:
  0 - Allow (advisory mode, or no violations)
  1 - Warn (advisory mode with warnings)
  2 - Block (strict mode, or unsafe edits detected)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Import shared receipt validation
try:
    from receipt_validator import find_and_validate_receipt, REQUIRED_FIELDS
except ImportError:
    # Handle running from different directories
    sys.path.insert(0, str(Path(__file__).parent))
    from receipt_validator import find_and_validate_receipt, REQUIRED_FIELDS

# Configuration
ADVISORY_SUNSET = "2026-06-15"

REPO_ROOT = Path("C:\\Git\\Agentic-Workflow-FRESH")
AGENTIC_CORE_PATH = REPO_ROOT / "agentic_core"
GOVERNANCE_DIR = REPO_ROOT / "artifacts" / "governance"
MIGRATION_RECEIPTS_DIR = GOVERNANCE_DIR / "migration_receipts"

# Classification categories
CLASSIFICATIONS = {
    "GENERIC_INFRASTRUCTURE": "Generic runtime infrastructure",
    "GENERIC_CORE_RUNTIME": "Generic core runtime code",
    "TEMPORARY_THIN_ADAPTER": "Binding with migration receipt",
    "CORE_APP_SPECIFIC_LEAKAGE": "App-specific logic in core - BLOCK",
    "DOC_ALLOWED": "Documentation files",
    "TEST_ALLOWED": "Test files",
    "RECEIPT_ALLOWED": "Governance receipts",
}

# Allowlisted paths that bypass core editing restrictions
ALLOWLISTED_PATHS = {
    # Documentation
    r".*\.md$",
    r".*AGENTS\.md$",
    r".*README.*",
    r".*RUNBOOK.*",
    r".*SLO.*",
    r".*TEST_STRATEGY.*",
    # Tests
    r".*/tests/.*",
    r".*/test_.*\.py$",
    r".*/conftest\.py$",
    # Receipts and governance
    r".*/artifacts/governance/.*",
    r".*/\docs/archive/windsurf/legacy-tree/.*",
    # Config (if generic)
    r".*/config/[^/]+\.json$",
    r".*/config/[^/]+\.yaml$",
}

# Temporary adapter pattern
BINDING_PATTERN = re.compile(r".*apps_\w+_.*_binding\.py$")

# Forbidden app-specific patterns in core
FORBIDDEN_PATTERNS = [
    (r'if\s+app_id\s*==\s*["\']apps_\w+["\']', "app_id branching"),
    (r'app_id\s*==\s*["\']apps_\w+["\']', "app_id comparison"),
    (r'["\']apps_lic["\']', "hardcoded apps_lic"),
    (r'["\']apps_rg["\']', "hardcoded apps_rg"),
    (r'["\']apps_qna["\']', "hardcoded apps_qna"),
    (r'["\']apps_research["\']', "hardcoded apps_research"),
    (r'APPS_\w+_\w+\s*=\s*\[', "app-specific constant list"),
]


def is_allowlisted(filepath: str) -> bool:
    """Check if path is allowlisted (docs, tests, receipts)."""
    for pattern in ALLOWLISTED_PATHS:
        if re.match(pattern, filepath, re.IGNORECASE):
            return True
    return False


def is_temporary_binding(filepath: str) -> bool:
    """Check if file is a temporary binding (apps_*_*_binding.py)."""
    return bool(BINDING_PATTERN.match(filepath))


def has_valid_receipt(binding_file: str) -> Tuple[bool, str]:
    """
    Check if binding file has valid 12-field migration receipt.
    
    Returns:
        (has_valid_receipt, reason_message)
    """
    is_valid, reason, receipt = find_and_validate_receipt(binding_file)
    return is_valid, reason


def scan_for_forbidden_patterns(filepath: str) -> List[Dict]:
    """Scan file for forbidden app-specific patterns."""
    violations = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except (IOError, UnicodeDecodeError) as e:
        return [{"error": f"Cannot read file: {e}"}]
    
    for line_num, line in enumerate(lines, 1):
        for pattern, description in FORBIDDEN_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                # Check if this is in a test file (allowed)
                if '/tests/' in filepath or 'test_' in filepath:
                    continue
                # Check if this is a binding file (receipt required)
                if is_temporary_binding(filepath):
                    continue
                violations.append({
                    "line": line_num,
                    "pattern": description,
                    "content": line.strip()[:80]
                })
    
    return violations


def classify_file(filepath: str, strict: bool = False) -> Tuple[str, List[Dict]]:
    """Classify a file according to governance model."""
    rel_path = str(filepath).replace(str(REPO_ROOT), "").lstrip("/\\")
    
    # Check if in agentic_core
    if "agentic_core" not in rel_path:
        return ("OUT_OF_SCOPE", [])
    
    # Check allowlist
    if is_allowlisted(rel_path):
        if ".md" in filepath:
            return ("DOC_ALLOWED", [])
        if "/tests/" in rel_path or "test_" in filepath:
            return ("TEST_ALLOWED", [])
        return ("RECEIPT_ALLOWED", [])
    
    # Check if it's a temporary binding
    if is_temporary_binding(rel_path):
        has_receipt, reason = has_valid_receipt(rel_path)
        if has_receipt:
            return ("TEMPORARY_THIN_ADAPTER", [])
        else:
            violation = {
                "severity": "HIGH" if strict else "MEDIUM",
                "message": f"TEMPORARY_THIN_ADAPTER without valid 12-field receipt: {reason}",
                "receipt_issue": reason
            }
            return ("TEMPORARY_THIN_ADAPTER_NO_RECEIPT", [violation])
    
    # Scan for forbidden patterns
    violations = scan_for_forbidden_patterns(filepath)
    
    if violations:
        return ("CORE_APP_SPECIFIC_LEAKAGE", violations)
    
    # Check file naming patterns for generic classification
    if "generic" in rel_path.lower() or "package_driven" in rel_path.lower():
        return ("GENERIC_CORE_RUNTIME", [])
    
    if "config" in rel_path or "utils" in rel_path or "contracts" in rel_path:
        return ("GENERIC_INFRASTRUCTURE", [])
    
    # Default to requiring classification
    return ("NEEDS_CLASSIFICATION", [])


def get_staged_files() -> List[str]:
    """Get list of files being modified (from environment or git)."""
    # Check for WINDSUFF_FILES environment variable (set by Windsurf)
    windsurf_files = os.environ.get('WINDSURF_FILES', '')
    if windsurf_files:
        return [f.strip() for f in windsurf_files.split(',') if f.strip()]
    
    # Fallback: check for files in command line args
    if len(sys.argv) > 1:
        return sys.argv[1:]
    
    # Last resort: try git
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=10
        )
        if result.returncode == 0:
            return [f.strip() for f in result.stdout.split('\n') if f.strip()]
    except Exception:
        pass
    
    return []


def get_enforcement_mode(cli_strict: bool) -> Tuple[bool, str]:
    """Returns (is_strict, reason_message)."""
    today = datetime.now().isoformat()[:10]
    
    if today > ADVISORY_SUNSET:
        if cli_strict:
            return True, f"STRICT MODE (sunset {ADVISORY_SUNSET} passed, --strict flag)"
        return True, f"STRICT MODE (sunset {ADVISORY_SUNSET} enforced)"
    
    if cli_strict:
        return True, "Strict mode (CLI flag)"
    
    return False, f"Advisory mode (sunset {ADVISORY_SUNSET})"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CORE_WRITE_GUARD: Pre-write hook for agentic_core governance"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail-closed mode (post-sunset, this is default)",
    )
    args = parser.parse_args()
    
    is_strict, mode_reason = get_enforcement_mode(args.strict)
    
    violations = []
    warnings = []
    blocked_files = []
    
    print(f"CORE_WRITE_GUARD: Pre-write hook ({mode_reason})")
    
    # Get files to check
    files_to_check = get_staged_files()
    
    if not files_to_check:
        # No files to check - allow
        print("CORE_WRITE_GUARD: No files to check, allowing.")
        sys.exit(0)
    
    # Check each file
    for filepath in files_to_check:
        full_path = REPO_ROOT / filepath
        
        # Skip if not in agentic_core
        if "agentic_core" not in filepath:
            continue
        
        # Skip if doesn't exist (may be deleted)
        if not full_path.exists():
            continue
        
        # Skip directories
        if full_path.is_dir():
            continue
        
        classification, issues = classify_file(str(full_path), strict=is_strict)
        
        if classification == "CORE_APP_SPECIFIC_LEAKAGE":
            blocked_files.append({
                "file": filepath,
                "classification": classification,
                "violations": issues
            })
        elif classification == "TEMPORARY_THIN_ADAPTER_NO_RECEIPT":
            if is_strict:
                blocked_files.append({
                    "file": filepath,
                    "classification": classification,
                    "violations": issues
                })
            else:
                warnings.append({
                    "file": filepath,
                    "warning": issues[0].get("message", "Unverified binding")
                })
        elif classification == "NEEDS_CLASSIFICATION":
            warnings.append({
                "file": filepath,
                "warning": "File needs explicit classification"
            })
    
    # Determine exit code
    exit_code = 0
    if blocked_files:
        exit_code = 2
    elif warnings and is_strict:
        # Strict mode: treat warnings as blocking
        exit_code = 2
    elif warnings and not is_strict:
        # Advisory mode: warnings non-blocking
        exit_code = 0
    
    # Generate output
    output = {
        "guard": "core_write_guard",
        "mode": mode_reason,
        "is_strict": is_strict,
        "timestamp": str(Path(__file__).stat().st_mtime),
        "files_checked": len(files_to_check),
        "agentic_core_files": len([f for f in files_to_check if "agentic_core" in f]),
        "blocked_files": len(blocked_files),
        "warnings": len(warnings),
        "violations": blocked_files,
        "warning_details": warnings,
        "exit_code": exit_code
    }
    
    # Print JSON output for parsing
    print(json.dumps(output, indent=2))
    
    # Print human-readable summary
    if blocked_files:
        print("\n" + "="*60)
        print("BLOCKING VIOLATIONS DETECTED")
        print("="*60)
        for item in blocked_files:
            print(f"\nFile: {item['file']}")
            print(f"Classification: {item['classification']}")
            for v in item['violations']:
                if 'line' in v:
                    print(f"  Line {v['line']}: {v['pattern']}")
                    print(f"    {v['content']}")
        print("\n" + "="*60)
        print("These files contain app-specific logic in agentic_core.")
        print("Move to apps_*/config/domain_contract/ or use TEMPORARY_THIN_ADAPTER")
        print("with 12-field migration receipt.")
        print("="*60)
        sys.exit(2)
    
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  {w['file']}: {w['warning']}")
        if not is_strict:
            print(f"\n[ADVISORY MODE] Warnings non-blocking. Set --strict for fail-closed.")
    
    print("\nCORE_WRITE_GUARD: All agentic_core files passed.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
