from agentic_core.L2_execution.tools import write_gateway as _wg
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "cache_guard")
emit_determinism_digest("p0", "cache_guard")

_emit_dispatches_healing_run("p1", "cache_guard", "L5")
_emit_routes_through("p1", "cache_guard", "L5")
_emit_escalates_to_human("p1", "cache_guard", "L5")
_emit_reads_policy_state("p1", "cache_guard", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "cache_guard")
_emit_applies_guardrail("p0", "cache_guard", "p0_governance")
_emit_snapshots_state("p0", "cache_guard", "state_snapshot")

"\nCache & Temp Governance Guard\n\nDeterministic read-only scanner for cache/temp directory governance.\nEnforces location constraints and tracked file detection.\n"
import os
import subprocess
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)


def is_cache_directory(dir_path: Path) -> bool:
    """Check if directory is a cache directory."""
    cache_names = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
    return dir_path.name in cache_names


def is_excluded_directory(dir_path: Path) -> bool:
    """Check if directory should be excluded from scanning."""
    return dir_path.name == ".git"


def estimate_directory_size(dir_path: Path) -> int:
    """Estimate directory size, capped at 200MB scan."""
    total_size = 0
    max_scan_bytes = 200 * 1024 * 1024
    try:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = Path(root) / file
                try:
                    total_size += file_path.stat().st_size
                    if total_size > max_scan_bytes:
                        return total_size
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass
    return total_size


def has_tracked_files(dir_path: Path, root_path: Path) -> bool:
    """Check if cache directory has any tracked files under it."""
    try:
        relative_path = dir_path.relative_to(root_path)
        result = subprocess.run(
            ["git", "ls-files", str(relative_path)], capture_output=True, text=True, cwd=str(root_path)
        )
        return bool(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        return False


def is_forbidden_location(dir_path: Path, root_path: Path) -> bool:
    """Check if cache directory is in forbidden location."""
    try:
        relative_path = dir_path.relative_to(root_path)
        path_parts = relative_path.parts
        if path_parts and path_parts[0] in {AGENTIC_CORE_DIR}:
            return True
        if path_parts and path_parts[0].startswith("apps_"):
            return True
    except ValueError:
        pass
    return False


def scan_cache_directories(root_path: Path) -> dict[str, Any]:
    """Scan repository for cache directories."""
    violations = []
    inventory = []
    dirs_scanned = 0
    all_dirs = sorted(root_path.rglob("*"))
    for item_path in all_dirs:
        if not item_path.is_dir():
            continue
        if is_excluded_directory(item_path):
            continue
        dirs_scanned += 1
        if not is_cache_directory(item_path):
            continue
        relative_path = item_path.relative_to(root_path)
        size_bytes = estimate_directory_size(item_path)
        if has_tracked_files(item_path, root_path):
            violations.append(
                {
                    "path": str(relative_path),
                    "type": "tracked_cache",
                    "detail": f"Cache directory contains tracked files: {relative_path}",
                }
            )
        if is_forbidden_location(item_path, root_path):
            violations.append(
                {
                    "path": str(relative_path),
                    "type": "cache_in_core_or_apps",
                    "detail": f"Cache directory in forbidden location: {relative_path}",
                }
            )
        inventory_item = {
            "path": str(relative_path),
            "type": "cache_directory",
            "detail": f"Size: {size_bytes:,} bytes",
        }
        if size_bytes > 10 * 1024 * 1024:
            inventory_item["detail"] += " (oversize)"
        inventory.append(inventory_item)
    return {"dirs_scanned": dirs_scanned, "violations": violations, "inventory": inventory}


def main():
    """Main scanner execution."""
    root_path = Path(__file__).parent.parent.parent
    print(f"Scanning repository for cache directories: {root_path}")
    result = scan_cache_directories(root_path)
    output_dir = root_path / "artifacts" / "governance"
    _wg.ensure_dir(output_dir)
    report_path = output_dir / "cache_guard_report.json"
    _wg.write_json(report_path, result, indent=2)
    print(f"Scan complete. Report written to: {report_path}")
    print(f"Directories scanned: {result['dirs_scanned']}")
    print(f"Cache directories found: {len(result['inventory'])}")
    print(f"Violations found: {len(result['violations'])}")
    total_size = 0
    oversize_count = 0
    for item in result["inventory"]:
        detail = item.get("detail", "")
        if "Size:" in detail:
            try:
                size_str = detail.split("Size:")[1].split(" bytes")[0].replace(",", "").strip()
                size_bytes = int(size_str)
                total_size += size_bytes
                if size_bytes > 10 * 1024 * 1024:
                    oversize_count += 1
            except (ValueError, IndexError):
                pass
    if total_size > 0:
        print(f"Total cache size: {total_size:,} bytes")
    if oversize_count > 0:
        print(f"Oversize directories (>10MB): {oversize_count}")
    if result["violations"]:
        print("CACHE/TEMP GOVERNANCE VIOLATIONS DETECTED:")
        for violation in result["violations"]:
            print(f"  {violation['path']}: {violation['type']} - {violation['detail']}")
        return 1
    else:
        print("No cache/temp governance violations found.")
        return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
