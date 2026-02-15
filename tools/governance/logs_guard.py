#!/usr/bin/env python3
"""
Logs & Outputs Governance Guard

Deterministic read-only scanner for log/output file governance.
Enforces location constraints, sensitive content detection, and inventory tracking.
"""

import json
import re
from pathlib import Path
from typing import Any


def is_log_or_output_file(file_path: Path) -> bool:
    """Check if file is a log or output file based on extension."""
    log_extensions = {".log", ".out", ".err", ".txt", ".jsonl"}
    return file_path.suffix.lower() in log_extensions


def is_log_or_output_directory(dir_path: Path) -> bool:
    """Check if directory is a log or output directory."""
    log_dir_names = {"logs", "output", "outputs", "run_logs", "debug_logs"}
    return dir_path.name in log_dir_names


def is_excluded_directory(dir_path: Path) -> bool:
    """Check if directory should be excluded from scanning."""
    excluded_dirs = {
        ".git",
        ".nox",
        ".venv",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        ".mypy_cache",
    }
    return dir_path.name in excluded_dirs


def is_in_excluded_directory(file_path: Path) -> bool:
    """Check if file is in any excluded directory."""
    for parent in file_path.parents:
        if is_excluded_directory(parent):
            return True
    return False


def is_allowed_location(file_path: Path, root_path: Path) -> bool:
    """Check if file is in an allowed location."""
    relative_path = file_path.relative_to(root_path)

    # Check if file is under any allowed root directory
    allowed_roots = {"artifacts/logs", "artifacts/outputs", "logs", "output", "outputs"}

    # Build path string for each possible prefix using pathlib
    for i in range(len(relative_path.parts)):
        prefix_path = Path(*relative_path.parts[: i + 1])
        prefix_str = str(prefix_path).replace("\\", "/").casefold()
        if prefix_str in allowed_roots:
            return True

    return False


def scan_sensitive_content(file_path: Path) -> list[str]:
    """Scan file for sensitive content patterns."""
    sensitive_patterns = [
        r"(?i)api[_-]?key\s*[:=]",
        r"(?i)secret\s*[:=]",
        r"sk-[A-Za-z0-9]{20,}",
        r"xox[baprs]-[A-Za-z0-9-]{10,}",
    ]

    violations = []

    try:
        # Skip files > 2MB for content scanning
        if file_path.stat().st_size > 2 * 1024 * 1024:
            return violations

        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        for pattern in sensitive_patterns:
            if re.search(pattern, content):
                violations.append(f"Sensitive pattern detected: {pattern}")

    except (UnicodeDecodeError, PermissionError, OSError):
        # Skip files that can't be read as text
        pass

    return violations


def scan_logs_and_outputs(root_path: Path) -> dict[str, Any]:
    """Scan repository for log and output files."""
    violations = []
    inventory = []
    files_scanned = 0

    # Use deterministic ordering
    all_files = sorted(root_path.rglob("*"))

    for item_path in all_files:
        # Skip excluded directories
        if item_path.is_dir() and is_excluded_directory(item_path):
            continue

        # Skip files in excluded directories
        if item_path.is_file() and is_in_excluded_directory(item_path):
            continue

        # Check if this is a log/output file or in a log/output directory
        is_log_file = False
        is_in_log_dir = False

        if item_path.is_file():
            if is_log_or_output_file(item_path):
                is_log_file = True
            # Check if file is in a log/output directory
            for parent in item_path.parents:
                if is_log_or_output_directory(parent):
                    is_in_log_dir = True
                    break

        # Skip if not a log/output file and not in log/output directory
        if not is_log_file and not is_in_log_dir:
            continue

        # Skip directories
        if item_path.is_dir():
            continue

        files_scanned += 1

        # Get relative path from repo root
        relative_path = item_path.relative_to(root_path)
        file_size = item_path.stat().st_size
        file_ext = item_path.suffix.lower()

        # Determine file kind
        if is_log_file:
            kind = "log_file"
        elif is_in_log_dir:
            kind = "in_log_dir"
        else:
            kind = "unknown"

        # Check 1: Location constraint
        if not is_allowed_location(item_path, root_path):
            violations.append(
                {
                    "file": str(relative_path),
                    "type": "disallowed_log_location",
                    "detail": f"Log/output file not in allowed location: {relative_path}",
                }
            )

        # Check 2: Sensitive content
        sensitive_violations = scan_sensitive_content(item_path)
        for violation in sensitive_violations:
            violations.append({"file": str(relative_path), "type": "sensitive_content", "detail": violation})

        # Build inventory entry
        inventory_item = {"file": str(relative_path), "bytes": file_size, "ext": file_ext, "kind": kind}

        # Add oversize detail for files > 5MB (informational only)
        if file_size > 5 * 1024 * 1024:
            inventory_item["detail"] = "oversize"

        inventory.append(inventory_item)

    return {"files_scanned": files_scanned, "violations": violations, "inventory": inventory}


def main():
    """Main scanner execution."""
    # Get repository root
    root_path = Path(__file__).parent.parent.parent

    print(f"Scanning repository for logs and outputs: {root_path}")

    # Scan for violations
    result = scan_logs_and_outputs(root_path)

    # Ensure output directory exists
    output_dir = root_path / "artifacts" / "governance"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write report
    report_path = output_dir / "logs_guard_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)

    print(f"Scan complete. Report written to: {report_path}")
    print(f"Files scanned: {result['files_scanned']}")
    print(f"Violations found: {len(result['violations'])}")

    # Print inventory summary
    oversize_count = sum(1 for item in result["inventory"] if item.get("detail") == "oversize")
    if oversize_count > 0:
        print(f"Oversize files (>5MB): {oversize_count}")

    # Print breakdown by kind
    kind_counts = {}
    for item in result["inventory"]:
        kind = item.get("kind", "unknown")
        kind_counts[kind] = kind_counts.get(kind, 0) + 1

    if kind_counts:
        print("File kinds found:")
        for kind, count in sorted(kind_counts.items()):
            print(f"  {kind}: {count}")

    if result["violations"]:
        print("LOGS/OUTPUTS GOVERNANCE VIOLATIONS DETECTED:")
        for violation in result["violations"]:
            print(f"  {violation['file']}: {violation['type']} - {violation['detail']}")
        return 1
    else:
        print("No logs/outputs governance violations found.")
        return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
