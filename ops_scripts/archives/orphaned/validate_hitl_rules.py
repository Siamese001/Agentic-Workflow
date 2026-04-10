"""
HITL Rules Validation Script
Verifies structural integrity of hitl-enforcement.md configuration sections.
"""

import re
import sys
from pathlib import Path


def validate_yaml_config_section(filepath: Path) -> list[str]:
    """Extract and validate YAML config from §HITL-9."""
    errors = []
    content = filepath.read_text(encoding="utf-8")

    # Find §HITL-9 section
    hitl9_match = re.search(r"## §HITL-9:.*?(?=## \§|$)", content, re.DOTALL)
    if not hitl9_match:
        errors.append("FAIL: §HITL-9 section not found")
        return errors

    section = hitl9_match.group(0)

    # Check required threshold keys
    required_keys = [
        "surface_threshold: 0.72",
        "dominance_score_threshold: 0.85",
        "dominance_delta: 0.12",
        "allow_single_option_hitl: true",
    ]

    for key in required_keys:
        if key not in section:
            errors.append(f"FAIL: Missing required config: {key}")

    # Validate YAML block structure
    yaml_block_match = re.search(r"```yaml\n(.*?)\n```", section, re.DOTALL)
    if not yaml_block_match:
        errors.append("FAIL: YAML config block not found in §HITL-9")

    return errors


def validate_option_shape_section(filepath: Path) -> list[str]:
    """Verify §HITL-10 option shape contract exists with required fields."""
    errors = []
    content = filepath.read_text(encoding="utf-8")

    hitl10_match = re.search(r"## §HITL-10:.*?(?=## \§|$)", content, re.DOTALL)
    if not hitl10_match:
        errors.append("FAIL: §HITL-10 section not found")
        return errors

    section = hitl10_match.group(0)

    required_fields = [
        "decision_thesis",
        "value_to_goal",
        "key_tradeoffs",
        "execution_impact",
        "risk_profile",
        "time_to_value",
    ]

    for field in required_fields:
        if field not in section:
            errors.append(f"FAIL: Missing required option field: {field}")

    return errors


def validate_no_hardcoded_2to4(filepath: Path) -> list[str]:
    """Verify old '2-4' minimum count language is removed."""
    errors = []
    content = filepath.read_text(encoding="utf-8")

    # Check for forbidden patterns
    forbidden_patterns = [r"Present 2-4 concrete options", r"Options \(2-4\)", r"2-4 concrete alternatives"]

    for pattern in forbidden_patterns:
        if re.search(pattern, content):
            errors.append(f"FAIL: Found forbidden pattern: {pattern}")

    # Check that new patterns exist
    required_patterns = [
        "surface_threshold = 0.72",
        "dominance rule",
        "Surface 1\u2013N options",
        "LOW_CONFIDENCE_AMBIGUITY",
    ]

    for pattern in required_patterns:
        if pattern not in content:
            errors.append(f"FAIL: Missing required pattern: {pattern}")

    return errors


def main() -> int:
    """Run all validations."""
    hitl_file = Path(".windsurf/rules/hitl-enforcement.md")

    if not hitl_file.exists():
        print("ERROR: hitl-enforcement.md not found")
        return 1

    all_errors = []

    print("Validating HITL Rules...")
    print("=" * 50)

    # Validate config section
    print("\n[1] Checking §HITL-9 configuration...")
    errors = validate_yaml_config_section(hitl_file)
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  {e}")
    else:
        print("  ✓ §HITL-9 config valid")

    # Validate option shape
    print("\n[2] Checking §HITL-10 option shape...")
    errors = validate_option_shape_section(hitl_file)
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  {e}")
    else:
        print("  ✓ §HITL-10 option shape valid")

    # Validate no old patterns
    print("\n[3] Checking for deprecated patterns...")
    errors = validate_no_hardcoded_2to4(hitl_file)
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  {e}")
    else:
        print("  ✓ No deprecated patterns found")

    print("\n" + "=" * 50)
    if all_errors:
        print(f"FAILED: {len(all_errors)} validation errors")
        return 1
    else:
        print("PASSED: All validations successful")
        return 0


if __name__ == "__main__":
    sys.exit(main())
