"""Enforces plans only exist in SSOT-approved location.

Per Constitutional Rule #9, this gate blocks commits when NEW plans are found
in prohibited locations (docs/reports/plans/). Existing plans are grandfathered.
"""

import subprocess
import sys
from pathlib import Path


def get_staged_files(project_root: Path) -> list[Path]:
    """Get list of staged files for the current commit."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    if result.returncode != 0:
        print(f"Warning: Could not get staged files: {result.stderr}")
        return []

    files = [project_root / f for f in result.stdout.strip().split("\n") if f]
    return files


def validate_plan_locations(project_root: Path | None = None) -> bool:
    """Check new/staged plans are in SSOT-approved .windsurf/plans/ location.

    Returns:
        True if all staged plans are in SSOT-approved locations, False otherwise.
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    staged_files = get_staged_files(project_root)
    if not staged_files:
        print("No staged files to check")
        return True

    # Check only staged .md files in docs/reports/plans/ (prohibited)
    violations = []
    for file_path in staged_files:
        str_path = str(file_path).replace("\\", "/")
        if "/docs/reports/plans/" in str_path and file_path.suffix == ".md":
            violations.append(file_path)

    if violations:
        print("PLAN LOCATION VIOLATIONS (new/modified plans):")
        for v in violations:
            print(f"   {v} -> should be in .windsurf/plans/")
        print("\nMove these files to .windsurf/plans/ and re-commit.")
        return False

    print("All staged plans in SSOT-approved location (.windsurf/plans/)")
    return True


if __name__ == "__main__":
    sys.exit(0 if validate_plan_locations() else 1)
