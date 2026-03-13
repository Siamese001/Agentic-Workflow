from agentic_core.L2_execution.tools import write_gateway as _wg

"\nLogs & Outputs Governance Guard\n\nDeterministic read-only scanner for log/output file governance.\nEnforces location constraints, sensitive content detection, and inventory tracking.\n"
import re
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)


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
    excluded_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
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
    allowed_roots = {"artifacts/logs", "artifacts/outputs", "logs", "output", "outputs"}
    for i in range(len(relative_path.parts)):
        prefix_path = Path(*relative_path.parts[: i + 1])
        prefix_str = str(prefix_path).replace("\\", "/").casefold()
        if prefix_str in allowed_roots:
            return True
    return False


def scan_sensitive_content(file_path: Path) -> list[str]:
    """Scan file for sensitive content patterns."""
    sensitive_patterns = [
        "(?i)api[_-]?key\\s*[:=]",
        "(?i)secret\\s*[:=]",
        "sk-[A-Za-z0-9]{20,}",
        "xox[baprs]-[A-Za-z0-9-]{10,}",
    ]
    violations = []
    try:
        if file_path.stat().st_size > 2 * 1024 * 1024:
            return violations
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for pattern in sensitive_patterns:
            if re.search(pattern, content):
                violations.append(f"Sensitive pattern detected: {pattern}")
    except (UnicodeDecodeError, PermissionError, OSError):
        pass
    return violations


def scan_logs_and_outputs(root_path: Path) -> dict[str, Any]:
    """Scan repository for log and output files."""
    violations = []
    inventory = []
    files_scanned = 0
    all_files = sorted(root_path.rglob("*"))
    for item_path in all_files:
        if item_path.is_dir() and is_excluded_directory(item_path):
            continue
        if item_path.is_file() and is_in_excluded_directory(item_path):
            continue
        is_log_file = False
        is_in_log_dir = False
        if item_path.is_file():
            if is_log_or_output_file(item_path):
                is_log_file = True
            for parent in item_path.parents:
                if is_log_or_output_directory(parent):
                    is_in_log_dir = True
                    break
        if not is_log_file and (not is_in_log_dir):
            continue
        if item_path.is_dir():
            continue
        files_scanned += 1
        relative_path = item_path.relative_to(root_path)
        file_size = item_path.stat().st_size
        file_ext = item_path.suffix.lower()
        if is_log_file:
            kind = "log_file"
        elif is_in_log_dir:
            kind = "in_log_dir"
        else:
            kind = "unknown"
        if not is_allowed_location(item_path, root_path):
            violations.append(
                {
                    "file": str(relative_path),
                    "type": "disallowed_log_location",
                    "detail": f"Log/output file not in allowed location: {relative_path}",
                }
            )
        sensitive_violations = scan_sensitive_content(item_path)
        for violation in sensitive_violations:
            violations.append({"file": str(relative_path), "type": "sensitive_content", "detail": violation})
        inventory_item = {"file": str(relative_path), "bytes": file_size, "ext": file_ext, "kind": kind}
        if file_size > 5 * 1024 * 1024:
            inventory_item["detail"] = "oversize"
        inventory.append(inventory_item)
    return {"files_scanned": files_scanned, "violations": violations, "inventory": inventory}


def main():
    """Main scanner execution."""
    root_path = Path(__file__).parent.parent.parent
    print(f"Scanning repository for logs and outputs: {root_path}")
    result = scan_logs_and_outputs(root_path)
    output_dir = root_path / "artifacts" / "governance"
    _wg.ensure_dir(output_dir)
    report_path = output_dir / "logs_guard_report.json"
    _wg.write_json(report_path, result, indent=2)
    print(f"Scan complete. Report written to: {report_path}")
    print(f"Files scanned: {result['files_scanned']}")
    print(f"Violations found: {len(result['violations'])}")
    oversize_count = sum(1 for item in result["inventory"] if item.get("detail") == "oversize")
    if oversize_count > 0:
        print(f"Oversize files (>5MB): {oversize_count}")
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
