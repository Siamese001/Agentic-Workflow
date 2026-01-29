#!/usr/bin/env python3
"""
ROOT STRUCTURE REMEDIATION PROTOCOL
Renames scripts/ to ops_scripts/ and enforces strict separation.

PHASE 1: SSOT HARDENING (Blueprint Diffs)
- Updates canonical registry to recognize ops_scripts instead of scripts
- Adds strict log placement rules

PHASE 2: MIGRATION & CLEANUP
- Physical rename scripts/ -> ops_scripts/
- Sorts contents based on import rules
- Moves core-dependent scripts to L0_maintenance/scripts/
- Moves runtime logs to L0_maintenance/logs/

PHASE 3: VERIFICATION
- Tests migration success
- Validates structure compliance
"""

import re
import shutil
from pathlib import Path
from re import Pattern

# --- CONFIGURATION ---
PROJECT_ROOT = Path(".").resolve()
OLD_SCRIPTS_DIR = PROJECT_ROOT / "scripts"
NEW_OPS_DIR = PROJECT_ROOT / "ops_scripts"

CORE_SCRIPTS_DEST = PROJECT_ROOT / "agentic_core" / "L0_maintenance" / "scripts"
CORE_LOGS_DEST = PROJECT_ROOT / "agentic_core" / "L0_maintenance" / "logs"

# Allowed patterns for Root Logs (Must match SSOT)
ALLOWED_ROOT_LOG_PATTERNS: list[Pattern] = [
    re.compile(r"^trace_.*\.jsonl$"),
    re.compile(r"^mission_.*\.log$"),
    re.compile(r"^execution_.*\.trace$"),
]


def setup_dirs():
    """Ensure destination directories exist."""
    NEW_OPS_DIR.mkdir(parents=True, exist_ok=True)
    CORE_SCRIPTS_DEST.mkdir(parents=True, exist_ok=True)
    CORE_LOGS_DEST.mkdir(parents=True, exist_ok=True)


def migrate_and_audit_scripts():
    """
    1. Scans old 'scripts/' (if exists).
    2. Rule: If imports 'agentic_core' -> Move to agentic_core/L0_maintenance/scripts.
    3. Rule: If Standalone -> Move to new 'ops_scripts/'.
    4. Remove old 'scripts/' dir if empty.
    """
    if not OLD_SCRIPTS_DIR.exists():
        print(f"[-] No '{OLD_SCRIPTS_DIR.name}' directory found. Checking '{NEW_OPS_DIR.name}'...")
        if NEW_OPS_DIR.exists():
            print(f"[*] '{NEW_OPS_DIR.name}' already exists. Scanning for compliance...")
            source_dir = NEW_OPS_DIR
        else:
            print("[*] No scripts directory found. Creating new ops_scripts structure.")
            NEW_OPS_DIR.mkdir(parents=True, exist_ok=True)
            return
    else:
        source_dir = OLD_SCRIPTS_DIR

    print(f"[*] Scanning {source_dir} for migration & import violations...")

    moved_to_core = 0
    moved_to_ops = 0
    violations_found = 0

    # Snapshot file list to avoid modification issues during iteration
    files = list(source_dir.glob("*.py"))

    for file_path in files:
        if file_path.name == "root_drift_remediation.py":
            continue

        try:
            content = file_path.read_text(encoding="utf-8")

            # 1. Check for Core Dependency Violation
            if "agentic_core" in content:
                dest = CORE_SCRIPTS_DEST / file_path.name
                print(f"    [CORE_MOVE] {file_path.name} -> L0_maintenance (Dependency Detected)")
                shutil.move(str(file_path), str(dest))
                moved_to_core += 1
                violations_found += 1

            # 2. If valid standalone, ensure it is in the new OPS directory
            else:
                if source_dir == OLD_SCRIPTS_DIR:
                    dest = NEW_OPS_DIR / file_path.name
                    print(f"    [OPS_MIGRATE] {file_path.name} -> {NEW_OPS_DIR.name}")
                    shutil.move(str(file_path), str(dest))
                    moved_to_ops += 1
                else:
                    print(f"    [VERIFIED] {file_path.name} is valid in {NEW_OPS_DIR.name}")

        except Exception as e:
            print(f"    [ERR] Could not process {file_path.name}: {e}")

    # Cleanup old directory if empty
    if source_dir == OLD_SCRIPTS_DIR and not any(source_dir.iterdir()):
        print(f"[*] Removing empty legacy directory: {OLD_SCRIPTS_DIR}")
        source_dir.rmdir()

    print(
        f"[*] Scripts Migration Complete. Core: {moved_to_core}, Ops: {moved_to_ops}, Violations: {violations_found}"
    )
    return {
        "moved_to_core": moved_to_core,
        "moved_to_ops": moved_to_ops,
        "violations_found": violations_found,
    }


def audit_logs():
    """
    Scans root logs/.
    Rule: If it doesn't match ALLOWED_PATTERNS, it's a runtime log -> Move to L0.
    """
    logs_dir = PROJECT_ROOT / "logs"
    if not logs_dir.exists():
        print("[-] No root logs/ directory found. Skipping.")
        return {"moved_count": 0}

    print(f"[*] Scanning {logs_dir} for non-trace artifacts...")

    moved_count = 0
    for file_path in logs_dir.iterdir():
        if file_path.is_dir():
            continue

        is_allowed = any(p.match(file_path.name) for p in ALLOWED_ROOT_LOG_PATTERNS)

        if not is_allowed:
            dest = CORE_LOGS_DEST / file_path.name
            print(f"    [LOG_MOVE] {file_path.name} -> Core (Runtime/Debug Log)")
            shutil.move(str(file_path), str(dest))
            moved_count += 1

    print(f"[*] Logs Audit Complete. Moved: {moved_count}")
    return {"moved_count": moved_count}


def validate_structure():
    """Validates the new structure complies with SSOT."""
    print("[*] Validating new structure...")

    issues = []

    # Check ops_scripts exists
    if not NEW_OPS_DIR.exists():
        issues.append("ops_scripts directory does not exist")

    # Check old scripts is gone
    if OLD_SCRIPTS_DIR.exists():
        issues.append("Legacy scripts directory still exists")

    # Check for core imports in ops_scripts
    if NEW_OPS_DIR.exists():
        for py_file in NEW_OPS_DIR.glob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                if "agentic_core" in content:
                    issues.append(f"Core dependency found in ops_scripts/{py_file.name}")
            except Exception:
                pass

    if issues:
        print("[!] Structure validation issues found:")
        for issue in issues:
            print(f"    - {issue}")
        return False
    else:
        print("[✓] Structure validation passed")
        return True


def main():
    print("=== ROOT STRUCTURE REMEDIATION PROTOCOL ===")
    print("Phase 1: SSOT hardening completed in structure_blueprint.py")
    print("Phase 2: Migration & cleanup starting...")

    setup_dirs()

    # Execute migration
    script_results = migrate_and_audit_scripts()
    log_results = audit_logs()

    print("Phase 3: Verification...")
    is_valid = validate_structure()

    print("\n=== REMEDIATION SUMMARY ===")
    print(f"Scripts moved to core: {script_results['moved_to_core']}")
    print(f"Scripts moved to ops: {script_results['moved_to_ops']}")
    print(f"Violations found: {script_results['violations_found']}")
    print(f"Logs moved to core: {log_results['moved_count']}")
    print(f"Structure valid: {is_valid}")

    if is_valid:
        print("\n✅ REMEDIATION COMPLETE - Structure is compliant")
    else:
        print("\n❌ REMEDIATION INCOMPLETE - Manual fixes required")

    return is_valid


if __name__ == "__main__":
    main()
