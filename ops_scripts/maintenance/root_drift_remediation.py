"""Remediate root structure drift by relocating scripts and logs."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path
from typing import Pattern

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
    OPS_SCRIPTS_DIR,
    get_validated_project_root,
)


PROJECT_ROOT = get_validated_project_root()
OLD_SCRIPTS_DIR = PROJECT_ROOT / "scripts"
NEW_OPS_DIR = PROJECT_ROOT / OPS_SCRIPTS_DIR
CORE_SCRIPTS_DEST = PROJECT_ROOT / L0_ROUTING_DIR / "scripts"
CORE_LOGS_DEST = PROJECT_ROOT / L0_ROUTING_DIR / "logs"
ALLOWED_ROOT_LOG_PATTERNS: list[Pattern[str]] = [
    re.compile(r"^trace_.*\.jsonl$"),
    re.compile(r"^mission_.*\.log$"),
    re.compile(r"^execution_.*\.trace$"),
]


def setup_dirs(execute: bool) -> None:
    for path in (NEW_OPS_DIR, CORE_SCRIPTS_DEST, CORE_LOGS_DEST):
        if execute:
            path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"[DRY-RUN] Would ensure directory exists: {path.relative_to(PROJECT_ROOT)}")


def move_file(source: Path, destination: Path, execute: bool, reason: str) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if execute:
        shutil.move(str(source), str(destination))
        print(f"    [{reason}] {source.relative_to(PROJECT_ROOT)} -> {destination.relative_to(PROJECT_ROOT)}")
    else:
        print(
            f"    [DRY-RUN:{reason}] Would move {source.relative_to(PROJECT_ROOT)} -> {destination.relative_to(PROJECT_ROOT)}"
        )
    return True


def migrate_and_audit_scripts(execute: bool) -> dict[str, int]:
    if not OLD_SCRIPTS_DIR.exists():
        print(f"[-] No '{OLD_SCRIPTS_DIR.name}' directory found. Checking '{NEW_OPS_DIR.name}'...")
        source_dir = NEW_OPS_DIR if NEW_OPS_DIR.exists() else None
        if source_dir is None:
            print("[*] No scripts directory found. Nothing to migrate.")
            return {"moved_to_core": 0, "moved_to_ops": 0, "violations_found": 0}
    else:
        source_dir = OLD_SCRIPTS_DIR

    moved_to_core = 0
    moved_to_ops = 0
    violations_found = 0
    print(f"[*] Scanning {source_dir.relative_to(PROJECT_ROOT)} for migration and import violations...")

    for file_path in sorted(source_dir.glob("*.py")):
        if file_path.name == "root_drift_remediation.py":
            continue
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"    [ERR] Could not process {file_path.relative_to(PROJECT_ROOT)}: {exc}")
            continue

        if AGENTIC_CORE_DIR in content:
            move_file(file_path, CORE_SCRIPTS_DEST / file_path.name, execute=execute, reason="CORE_MOVE")
            moved_to_core += 1
            violations_found += 1
        elif source_dir == OLD_SCRIPTS_DIR:
            move_file(file_path, NEW_OPS_DIR / file_path.name, execute=execute, reason="OPS_MIGRATE")
            moved_to_ops += 1
        else:
            print(f"    [VERIFIED] {file_path.relative_to(PROJECT_ROOT)} is valid in {NEW_OPS_DIR.name}")

    if source_dir == OLD_SCRIPTS_DIR and execute and source_dir.exists() and not any(source_dir.iterdir()):
        print(f"[*] Removing empty legacy directory: {source_dir.relative_to(PROJECT_ROOT)}")
        source_dir.rmdir()

    return {
        "moved_to_core": moved_to_core,
        "moved_to_ops": moved_to_ops,
        "violations_found": violations_found,
    }


def audit_logs(execute: bool) -> dict[str, int]:
    logs_dir = PROJECT_ROOT / "logs"
    if not logs_dir.exists():
        print("[-] No root logs/ directory found. Skipping.")
        return {"moved_count": 0}

    moved_count = 0
    print(f"[*] Auditing {logs_dir.relative_to(PROJECT_ROOT)} for non-trace artifacts...")
    for file_path in sorted(logs_dir.iterdir()):
        if file_path.is_dir():
            continue
        is_allowed = any(pattern.match(file_path.name) for pattern in ALLOWED_ROOT_LOG_PATTERNS)
        if not is_allowed:
            move_file(file_path, CORE_LOGS_DEST / file_path.name, execute=execute, reason="LOG_MOVE")
            moved_count += 1

    return {"moved_count": moved_count}


def validate_structure() -> bool:
    issues: list[str] = []
    if OLD_SCRIPTS_DIR.exists():
        issues.append("Legacy scripts directory still exists")
    if NEW_OPS_DIR.exists():
        for py_file in sorted(NEW_OPS_DIR.glob("*.py")):
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if AGENTIC_CORE_DIR in content:
                issues.append(f"Core dependency found in ops_scripts/{py_file.name}")

    if issues:
        print("[!] Structure validation issues found:")
        for issue in issues:
            print(f"    - {issue}")
        return False

    print("[✓] Structure validation passed")
    return True


def main(execute: bool = False) -> int:
    print("=== ROOT STRUCTURE REMEDIATION PROTOCOL ===")
    print(f"Mode: {'EXECUTE' if execute else 'DRY-RUN'}")

    setup_dirs(execute=execute)
    script_results = migrate_and_audit_scripts(execute=execute)
    log_results = audit_logs(execute=execute)
    is_valid = validate_structure()

    print("\n=== REMEDIATION SUMMARY ===")
    print(f"Scripts moved to core: {script_results['moved_to_core']}")
    print(f"Scripts moved to ops: {script_results['moved_to_ops']}")
    print(f"Violations found: {script_results['violations_found']}")
    print(f"Logs moved to core: {log_results['moved_count']}")
    print(f"Structure valid: {is_valid}")
    return 0 if is_valid else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remediate root structure drift.")
    parser.add_argument("--execute", action="store_true", help="Perform file moves. Default is dry-run.")
    raise SystemExit(main(execute=parser.parse_args().execute))
