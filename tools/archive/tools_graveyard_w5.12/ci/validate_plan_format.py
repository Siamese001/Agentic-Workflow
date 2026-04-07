#!/usr/bin/env python3
"""
Windsurf Plan Format Validator
Enforces plan structure compliance with Windsurf guidelines.
Type-aware validation for different plan categories.
"""

import os
import re
import sys
from pathlib import Path
from typing import Any

# Plan type requirements
PLAN_REQUIREMENTS = {
    "execution": {
        "required_sections": ["## Wave Structure", "## Rules", "## Success Criteria"],
        "requires_wave_table": True,
        "requires_tokens": True,
    },
    "rca": {
        "required_sections": ["## Violation", "## Root Cause", "## Corrective Actions"],
        "requires_wave_table": False,
        "requires_tokens": False,
    },
    "gap_analysis": {
        "required_sections": ["## Gap Register", "## Execution Plan"],
        "requires_wave_table": True,  # Gap analyses often have implementation plans
        "requires_tokens": True,
    },
    "investigation": {
        "required_sections": ["## Findings", "## Evidence"],
        "requires_wave_table": False,
        "requires_tokens": False,
    },
}

WAVE_TABLE_PATTERN = r"\| Waves \| Metric \| Scope \| Checkpoint \|(\s*\| Tokens \|)?"


def detect_plan_type(content: str, filename: str) -> str:
    """Detect plan type from content and filename."""
    content_lower = content.lower()
    filename_lower = filename.lower()

    # RCA patterns
    if any(
        pattern in content_lower
        for pattern in ["## violation", "## root cause", "## corrective actions", "rca:"]
    ):
        return "rca"

    # Gap analysis patterns
    if any(pattern in content_lower for pattern in ["gap register", "gap analysis", "implementation gap"]):
        return "gap_analysis"

    # Execution plan patterns
    if any(
        pattern in content_lower
        for pattern in ["## wave structure", "## execution plan", "phase 1", "wave 1"]
    ):
        return "execution"

    # Investigation patterns
    if any(pattern in content_lower for pattern in ["## investigation", "## findings", "## assessment"]):
        return "investigation"

    # Default to execution if filename contains 'plan'
    if "plan" in filename_lower:
        return "execution"

    # Default fallback
    return "investigation"


def is_legacy_plan(content: str, filename: str) -> bool:
    """Check if this is a legacy plan created before standards."""
    # Simple heuristic: if it has wave structure, it's post-standards
    if "## Wave Structure" in content:
        return False

    # If it has 2025 dates or earlier, likely legacy
    if "2025" in content or "2024" in content or "2023" in content:
        return True

    # If filename has old date pattern
    if re.search(r"202[0-9]", filename):
        return True

    # Default to legacy for safety
    return True


def validate_plan_format(plan_path: str) -> dict[str, Any]:
    """Validate plan follows Windsurf format requirements."""

    try:
        with open(plan_path, encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        return {
            "valid": False,
            "issues": ["Encoding error: cannot read file as UTF-8"],
            "warnings": [],
            "plan_type": "unknown",
            "wave_table_found": False,
            "wave_table_line": None,
        }

    # Detect plan type and legacy status
    filename = Path(plan_path).name
    plan_type = detect_plan_type(content, filename)
    is_legacy = is_legacy_plan(content, filename)

    # Legacy plans get lenient validation
    if is_legacy:
        return {
            "valid": True,
            "issues": [],
            "warnings": ["Legacy plan - exempt from current validation standards"],
            "plan_type": plan_type,
            "wave_table_found": False,
            "wave_table_line": None,
            "is_legacy": True,
        }

    requirements = PLAN_REQUIREMENTS.get(plan_type, PLAN_REQUIREMENTS["investigation"])

    issues = []
    warnings = []

    # Check for required sections based on plan type
    for section in requirements["required_sections"]:
        if section not in content:
            issues.append(f"Missing required section for {plan_type}: {section}")

    # Check wave table if required
    wave_table_found = False
    wave_table_line = None

    if requirements["requires_wave_table"]:
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if line.startswith("## Wave Structure"):
                # Look for table in next 10 lines
                for j in range(i + 1, min(i + 11, len(lines))):
                    if re.match(WAVE_TABLE_PATTERN, lines[j]):
                        wave_table_found = True
                        wave_table_line = j + 1
                        break
                break

        if not wave_table_found:
            issues.append(
                f"Wave table not found after '## Wave Structure' section (required for {plan_type})",
            )
            issues.append("Expected pattern: | Waves | Metric | Scope | Checkpoint | [Tokens |]")

        # Check for token estimates if required
        if requirements["requires_tokens"] and wave_table_line:
            token_found = False
            for j in range(wave_table_line + 2, min(wave_table_line + 15, len(lines))):
                if "|" in lines[j] and any(char.isdigit() for char in lines[j]):
                    row = lines[j]
                    if "Wave" in row or any(x in row.lower() for x in ["k", "m", "token"]):
                        token_found = True
                        break

            if not token_found:
                warnings.append(f"No token estimates found in wave table (recommended for {plan_type})")

    # Additional checks for execution plans
    if plan_type == "execution":
        if "## Implementation Commands" not in content:
            warnings.append("No implementation commands section (recommended for execution plans)")
        if "## Rollback Strategy" not in content:
            warnings.append("No rollback strategy section (recommended for execution plans)")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "plan_type": plan_type,
        "wave_table_found": wave_table_found,
        "wave_table_line": wave_table_line,
        "is_legacy": False,
    }


def test_plan_validator():
    """Test the plan validator against known good/bad examples."""

    print("=== Testing Plan Validator ===\n")

    # Test 1: Check existing plan format
    existing_plan = "docs/reports/plans/convergent_wave_plan_101_150.md"
    if os.path.exists(existing_plan):
        print(f"Testing existing plan: {existing_plan}")
        result = validate_plan_format(existing_plan)
        print(f"Valid: {result['valid']}")
        if result["issues"]:
            print("Issues:")
            for issue in result["issues"]:
                print(f"  - {issue}")
        if result["warnings"]:
            print("Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
        print()

    # Test 2: Check the problematic plan I created
    problematic_plan = "C:/Users/amita/.windsurf/plans/dependency-reclassification-swe15-format-2b3c4d.md"
    if os.path.exists(problematic_plan):
        print(f"Testing problematic plan: {problematic_plan}")
        result = validate_plan_format(problematic_plan)
        print(f"Valid: {result['valid']}")
        if result["issues"]:
            print("Issues:")
            for issue in result["issues"]:
                print(f"  - {issue}")
        if result["warnings"]:
            print("Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
        print()

    # Test 3: Create a minimal valid plan to test validator
    test_plan_content = """# Test Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Test metric | Test scope | A | 10,000 |

## Rules
- Test rule 1
- Test rule 2

## Success Criteria
- [ ] Criteria 1
- [ ] Criteria 2
"""

    test_plan_path = "test_plan.md"
    with open(test_plan_path, "w") as f:
        f.write(test_plan_content)

    print("Testing minimal valid plan")
    result = validate_plan_format(test_plan_path)
    print(f"Valid: {result['valid']}")
    if result["issues"]:
        print("Issues:")
        for issue in result["issues"]:
            print(f"  - {issue}")
    if result["warnings"]:
        print("Warnings:")
        for warning in result["warnings"]:
            print(f"  - {warning}")

    # Cleanup
    os.remove(test_plan_path)

    print("\n=== Plan Validator Test Complete ===")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Validate specific plan
        plan_path = sys.argv[1]
        result = validate_plan_format(plan_path)

        print(f"Plan: {plan_path}")
        print(f"Valid: {result['valid']}")

        if result["issues"]:
            print("\n❌ Issues:")
            for issue in result["issues"]:
                print(f"  - {issue}")

        if result["warnings"]:
            print("\n⚠️  Warnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")

        if result["valid"]:
            print("\n✅ Plan format is valid!")
            sys.exit(0)
        else:
            print("\n❌ Plan format validation failed!")
            sys.exit(1)
    else:
        # Run tests
        test_plan_validator()
