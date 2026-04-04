"""Enforces plans only exist in SSOT-approved location.

Per constitutional plan-location rules, this gate blocks commits when NEW plans
are found in prohibited locations (for example `.windsurf/plans/`).
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
        check=False,
        cwd=project_root,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Git command failed: {result.stderr}")

    files = [project_root / f for f in result.stdout.strip().split("\n") if f]
    return files


def validate_plan_locations(project_root: Path | None = None) -> bool:
    """Check new/staged plans are in SSOT-approved docs/reports/plans/ location.

    Returns:
        True if all staged plans are in SSOT-approved locations, False otherwise.
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    staged_files = get_staged_files(project_root)
    if not staged_files:
        print("No staged files to check")
        return True

    # Check staged .md files in prohibited plan locations.
    violations = []
    for file_path in staged_files:
        str_path = str(file_path).replace("\\", "/")
        is_markdown = file_path.suffix == ".md"
        in_windsurf_plans = "/.windsurf/plans/" in str_path
        if is_markdown and in_windsurf_plans:
            violations.append(file_path)

    if violations:
        print("PLAN LOCATION VIOLATIONS (new/modified plans):")
        for v in violations:
            print(f"   {v} -> should be in docs/reports/plans/")
        print("\nMove these files to docs/reports/plans/ and re-commit.")
        return False

    print("All staged plans in SSOT-approved location (docs/reports/plans/)")
    return True


if __name__ == "__main__":
    sys.exit(0 if validate_plan_locations() else 1)
