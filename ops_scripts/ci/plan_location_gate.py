"""Enforces plans only exist in SSOT-approved location.

Per Constitutional Rule #9, this gate blocks commits when plans are found
in prohibited locations (docs/reports/plans/).
"""
import sys
from pathlib import Path


def validate_plan_locations(project_root: Path | None = None) -> bool:
    """Check all plans are in SSOT-approved .windsurf/plans/ location.

    Returns:
        True if all plans are in SSOT-approved locations, False otherwise.
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    # Plans must be in .windsurf/plans/, NOT in docs/reports/plans/
    prohibited_checks = [
        ("docs/reports/plans/*.md", ".windsurf/plans/"),
    ]

    violations = []
    for pattern, correct_location in prohibited_checks:
        matches = list(project_root.glob(pattern))
        for match in matches:
            violations.append((match, correct_location))

    if violations:
        print("PLAN LOCATION VIOLATIONS:")
        for v, correct in violations:
            print(f"   {v} -> should be in {correct}")
        print("\nMove these files to their correct locations and re-commit.")
        return False

    print("All plans in SSOT-approved location (.windsurf/plans/)")
    return True


if __name__ == "__main__":
    sys.exit(0 if validate_plan_locations() else 1)
