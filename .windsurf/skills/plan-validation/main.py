#!/usr/bin/env python3
"""
Windsurf Skill: Plan Validation
Validates plan documents against §10 standards before writing.
"""

import re
import sys
from pathlib import Path


def validate_wave_table(content: str) -> tuple[bool, list[str]]:
    """Validate wave summary table exists and has required columns."""
    issues = []

    # Look for wave table
    wave_table_pattern = (
        r"\| Wave \| Phase IDs \| Focus \| Est\. Tokens \| Assumptions \| Status \| Success Criteria \|"
    )
    if not re.search(wave_table_pattern, content):
        issues.append("Missing wave summary table with required columns")
        return False, issues

    # Check for at least one wave row
    lines = content.split("\n")
    table_start = -1
    for i, line in enumerate(lines):
        if re.search(wave_table_pattern, line):
            table_start = i
            break

    if table_start == -1:
        issues.append("Wave table found but couldn't locate start")
        return False, issues

    # Look for data rows (skip header and separator)
    data_rows = 0
    for i in range(table_start + 2, min(table_start + 10, len(lines))):
        if "|" in lines[i] and "---" not in lines[i]:
            if any(cell.strip() for cell in lines[i].split("|")[1:-1]):
                data_rows += 1

    if data_rows == 0:
        issues.append("Wave table has no data rows")
        return False, issues

    return True, []


def validate_token_estimates(content: str) -> tuple[bool, list[str]]:
    """Validate token estimates are present and reasonable."""
    issues = []

    # Check for token estimates in wave table
    token_pattern = r"\|\s*\*\*Wave\s+\d+\*\*\s*\|[^|]*\|[^|]*\|\s*(\d+,?\d*)\s*\|"
    matches = re.findall(token_pattern, content)

    if not matches:
        issues.append("No token estimates found in wave table")
        return False, issues

    # Check if any estimate exceeds 200K (RED status)
    for match in matches:
        tokens = int(match.replace(",", ""))
        if tokens > 200000:
            issues.append(f"Token estimate {tokens:,} exceeds RED threshold (200K)")

    return len(issues) == 0, issues


def validate_success_criteria(content: str) -> tuple[bool, list[str]]:
    """Validate success criteria are measurable."""
    issues = []

    # Look for success criteria column
    lines = content.split("\n")
    for line in lines:
        if "|" in line and "Success Criteria" in line:
            # Check next few lines for criteria
            idx = lines.index(line)
            for i in range(idx + 2, min(idx + 8, len(lines))):
                if "|" in lines[i] and "---" not in lines[i]:
                    criteria = lines[i].split("|")[-2].strip()
                    if not criteria or criteria.lower() in ["tbd", "todo", ""]:
                        issues.append(f"Empty or placeholder success criteria: {criteria}")

    return len(issues) == 0, issues


def validate_plan_location(file_path: str) -> tuple[bool, list[str]]:
    """Validate plan is being saved to SSOT-approved location."""
    issues = []

    path = Path(file_path)

    # Must be in .windsurf/plans/
    if ".windsurf/plans/" not in str(path).replace("\\", "/"):
        issues.append(f"Plan path {file_path} not in SSOT location .windsurf/plans/")
        return False, issues

    # Check for user home directory violation
    if str(path).startswith("C:\\Users\\") or str(path).startswith("/Users/"):
        issues.append(f"Plan path {file_path} violates SSOT (in user home directory)")
        return False, issues

    return True, []


def validate_plan_format(content: str, file_path: str) -> dict[str, any]:
    """Main validation entry point."""
    result = {"valid": True, "issues": [], "warnings": []}

    # Required validations
    validators = [
        validate_wave_table,
        validate_token_estimates,
        validate_success_criteria,
        lambda c: validate_plan_location(file_path),
    ]

    for validator in validators:
        is_valid, issues = validator(content)
        if not is_valid:
            result["valid"] = False
            result["issues"].extend(issues)

    return result


def main(content: str, file_path: str) -> dict[str, any]:
    """Windsurf skill entry point."""
    return validate_plan_format(content, file_path)


if __name__ == "__main__":
    # Health check
    if len(sys.argv) == 2 and sys.argv[1] == "--health-check":
        print("[PASS] Plan validation health check")
        sys.exit(0)

    # Test mode
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        with open(test_file) as f:
            content = f.read()

        result = validate_plan_format(content, test_file)
        print(f"Valid: {result['valid']}")
        if result["issues"]:
            print("Issues:")
            for issue in result["issues"]:
                print(f"  - {issue}")
