#!/usr/bin/env python3
"""
core_write_guard.py - Pre-write hook for agentic_core governance.

Blocks unsafe edits to agentic_core/ unless:
- Generic infrastructure
- Temporary thin adapter with migration receipt
- Documentation/tests/receipts

Exit codes:
  0 - Allow (no blocking violations)
  2 - Block (unsafe edits detected)
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Configuration
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
    r".*/\.windsurf/.*",
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


def has_migration_receipt(binding_file: str) -> bool:
    """Check if migration receipt exists for binding file."""
    if not MIGRATION_RECEIPTS_DIR.exists():
        return False
    
    binding_name = Path(binding_file).stem
    # Look for receipts matching binding name
    for receipt_file in MIGRATION_RECEIPTS_DIR.glob("*.json"):
        try:
            with open(receipt_file, 'r', encoding='utf-8') as f:
                receipt = json.load(f)
                if receipt.get('binding_file', '').endswith(binding_file):
                    return True
                if receipt.get('original_binding', {}).get('file', '').endswith(binding_file):
                    return True
        except (json.JSONDecodeError, IOError):
            continue
    return False


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


def classify_file(filepath: str) -> Tuple[str, List[Dict]]:
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
        if has_migration_receipt(rel_path):
            return ("TEMPORARY_THIN_ADAPTER", [])
        else:
            return ("TEMPORARY_THIN_ADAPTER", [{
                "warning": "Binding without verified migration receipt"
            }])
    
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


def main():
    """Main entry point."""
    violations = []
    warnings = []
    blocked_files = []
    
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
        
        classification, issues = classify_file(str(full_path))
        
        if classification == "CORE_APP_SPECIFIC_LEAKAGE":
            blocked_files.append({
                "file": filepath,
                "classification": classification,
                "violations": issues
            })
        elif classification == "TEMPORARY_THIN_ADAPTER" and issues:
            warnings.append({
                "file": filepath,
                "warning": issues[0].get("warning", "Unverified binding")
            })
        elif classification == "NEEDS_CLASSIFICATION":
            warnings.append({
                "file": filepath,
                "warning": "File needs explicit classification"
            })
    
    # Generate output
    output = {
        "guard": "core_write_guard",
        "timestamp": str(Path(__file__).stat().st_mtime),
        "files_checked": len(files_to_check),
        "agentic_core_files": len([f for f in files_to_check if "agentic_core" in f]),
        "blocked_files": len(blocked_files),
        "warnings": len(warnings),
        "violations": blocked_files,
        "warning_details": warnings,
        "exit_code": 2 if blocked_files else 0
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
        print("with migration receipt.")
        print("="*60)
        sys.exit(2)
    
    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  {w['file']}: {w['warning']}")
    
    print("\nCORE_WRITE_GUARD: All agentic_core files passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
