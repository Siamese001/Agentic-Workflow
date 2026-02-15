#!/usr/bin/env python3
"""
Cache & Temp Governance Guard

Deterministic read-only scanner for cache/temp directory governance.
Enforces location constraints and tracked file detection.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Any


def is_cache_directory(dir_path: Path) -> bool:
    """Check if directory is a cache directory."""
    cache_names = {
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".nox",
        ".venv",
    }
    return dir_path.name in cache_names


def is_excluded_directory(dir_path: Path) -> bool:
    """Check if directory should be excluded from scanning."""
    return dir_path.name == ".git"


def estimate_directory_size(dir_path: Path) -> int:
    """Estimate directory size, capped at 200MB scan."""
    total_size = 0
    max_scan_bytes = 200 * 1024 * 1024  # 200MB
    
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
        # Use git ls-files to check for tracked files under this directory
        result = subprocess.run(
            ["git", "ls-files", str(relative_path)],
            capture_output=True,
            text=True,
            cwd=str(root_path),
        )
        return bool(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        return False


def is_forbidden_location(dir_path: Path, root_path: Path) -> bool:
    """Check if cache directory is in forbidden location."""
    try:
        relative_path = dir_path.relative_to(root_path)
        path_parts = relative_path.parts
        
        # Forbidden if under agentic_core/ or apps_*/
        if path_parts and path_parts[0] in {"agentic_core"}:
            return True
        if path_parts and path_parts[0].startswith("apps_"):
            return True
            
    except ValueError:
        # Directory is not under root_path
        pass
    
    return False


def scan_cache_directories(root_path: Path) -> dict[str, Any]:
    """Scan repository for cache directories."""
    violations = []
    inventory = []
    dirs_scanned = 0

    # Use deterministic ordering
    all_dirs = sorted(root_path.rglob("*"))
    
    for item_path in all_dirs:
        # Skip if not a directory
        if not item_path.is_dir():
            continue
            
        # Skip excluded directories
        if is_excluded_directory(item_path):
            continue
            
        dirs_scanned += 1
        
        # Check if this is a cache directory
        if not is_cache_directory(item_path):
            continue
            
        # Get relative path from repo root
        relative_path = item_path.relative_to(root_path)
        
        # Estimate size
        size_bytes = estimate_directory_size(item_path)
        
        # Check 1: Tracked cache violation
        if has_tracked_files(item_path, root_path):
            violations.append({
                "path": str(relative_path),
                "type": "tracked_cache",
                "detail": f"Cache directory contains tracked files: {relative_path}",
            })
        
        # Check 2: Forbidden location violation
        if is_forbidden_location(item_path, root_path):
            violations.append({
                "path": str(relative_path),
                "type": "cache_in_core_or_apps",
                "detail": f"Cache directory in forbidden location: {relative_path}",
            })
        
        # Build inventory entry
        inventory_item = {
            "path": str(relative_path),
            "type": "cache_directory",
            "detail": f"Size: {size_bytes:,} bytes",
        }
        
        # Add oversize detail for directories > 10MB (informational only)
        if size_bytes > 10 * 1024 * 1024:
            inventory_item["detail"] += " (oversize)"
        
        inventory.append(inventory_item)

    return {
        "dirs_scanned": dirs_scanned,
        "violations": violations,
        "inventory": inventory,
    }


def main():
    """Main scanner execution."""
    # Get repository root
    root_path = Path(__file__).parent.parent.parent

    print(f"Scanning repository for cache directories: {root_path}")

    # Scan for violations
    result = scan_cache_directories(root_path)

    # Ensure output directory exists
    output_dir = root_path / "artifacts" / "governance"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write report
    report_path = output_dir / "cache_guard_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)

    print(f"Scan complete. Report written to: {report_path}")
    print(f"Directories scanned: {result['dirs_scanned']}")
    print(f"Cache directories found: {len(result['inventory'])}")
    print(f"Violations found: {len(result['violations'])}")

    # Print inventory summary
    total_size = 0
    oversize_count = 0
    
    for item in result["inventory"]:
        # Extract size from detail string
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
