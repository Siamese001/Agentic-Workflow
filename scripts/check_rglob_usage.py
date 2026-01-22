"""
CI Guard: rglob/glob Usage Checker

Phase 4.1 CI Enforcement: This script counts un-guarded rglob/glob calls
to prevent performance regression. It should be run in CI/CD pipelines.

Usage:
    python scripts/check_rglob_usage.py

Exit Codes:
    0: Pass - rglob count is within limits
    1: Fail - rglob count exceeds maximum allowed

Author: Cascade
Date: January 19, 2026
Phase: 4.1 - Scaled Refactoring & CI Enforcement
"""

import re
import sys

# Configuration
MAX_ALLOWED_RGLOB = 260  # Phase 6: Temporary ceiling, target is 50

# Files to exclude from the count (these are the utilities that wrap rglob)
EXCLUDED_FILES = {
    "ssot_discovery.py",
    "scan_guard.py",
    "check_rglob_usage.py",  # This script
}

# Directories to exclude
EXCLUDED_DIRS = {
    "archives",
    ".sovereign_healing_backup",
    "__pycache__",
    ".git",
    ".pytest_cache",
}


def count_rglob_in_file(file_path: Path) -> int:
    """
    Count rglob/glob calls in a single file.

    Args:
        file_path: Path to the Python file

    Returns:
        Number of rglob/glob calls found
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return 0

    # Pattern to match .rglob( and .glob( calls
    rglob_pattern = r"\.rglob\s*\("
    glob_pattern = r"\.glob\s*\("

    rglob_count = len(re.findall(rglob_pattern, content))
    glob_count = len(re.findall(glob_pattern, content))

    return rglob_count + glob_count


def should_exclude_path(file_path: Path) -> bool:
    """Check if a file path should be excluded from counting."""
    # Check if file is in excluded list
    if file_path.name in EXCLUDED_FILES:
        return True

    # Check if any parent directory is excluded
    for part in file_path.parts:
        if part in EXCLUDED_DIRS:
            return True

    return False


def scan_for_rglob_usage(root_dir: Path) -> tuple[int, list[dict]]:
    """
    Scan directory for rglob/glob usage.

    Args:
        root_dir: Root directory to scan

    Returns:
        Tuple of (total_count, list of offender details)
    """
    total_count = 0
    offenders = []

    for py_file in root_dir.rglob("*.py"):
        # Skip excluded paths
        if should_exclude_path(py_file):
            continue

        count = count_rglob_in_file(py_file)
        if count > 0:
            offenders.append({"file": str(py_file.relative_to(root_dir)), "count": count})
            total_count += count

    # Sort by count descending
    offenders.sort(key=lambda x: x["count"], reverse=True)

    return total_count, offenders


def main():
    """Main entry point for CI check."""
    print("=" * 60)
    print("CI GUARD: rglob/glob Usage Check")
    print("=" * 60)

    # Find project root (parent of scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    agentic_core = project_root / "agentic_core"

    if not agentic_core.exists():
        print(f"ERROR: agentic_core directory not found at {agentic_core}")
        sys.exit(1)

    print(f"Scanning: {agentic_core}")
    print(f"Maximum allowed: {MAX_ALLOWED_RGLOB}")
    print()

    # Scan for rglob usage
    total_count, offenders = scan_for_rglob_usage(agentic_core)

    # Report results
    print(f"Total rglob/glob calls: {total_count}")
    print(f"Files with rglob/glob: {len(offenders)}")
    print()

    # Show top offenders
    if offenders:
        print("Top 10 Offenders:")
        for i, offender in enumerate(offenders[:10], 1):
            print(f"  {i:2}. {offender['file']}: {offender['count']} calls")
        print()

    # Check against threshold
    if total_count > MAX_ALLOWED_RGLOB:
        print("=" * 60)
        print(f"❌ FAIL: Count ({total_count}) exceeds maximum ({MAX_ALLOWED_RGLOB})")
        print("=" * 60)
        print()
        print("Action Required:")
        print("  1. Refactor files to use ssot_discovery.get_python_files()")
        print("  2. Or use scan_guard.guarded_rglob() for tracking")
        print()
        sys.exit(1)
    else:
        print("=" * 60)
        print(f"✅ PASS: Count ({total_count}) is within limit ({MAX_ALLOWED_RGLOB})")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
