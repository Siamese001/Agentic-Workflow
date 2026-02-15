#!/usr/bin/env python3
"""
Governance Policy Validation Hook

Enforces that governance policy changes are properly documented and authorized.
Validates that changes to critical configurations have corresponding policy updates.
"""

import argparse
import sys
from pathlib import Path

# Governance policies that require documentation
GOVERNANCE_REQUIREMENTS = {
    ".pre-commit-config.yaml": {
        "manual_stage_hooks": {
            "description": "Hooks moved to manual stage must have policy documentation",
            "pattern": r"stages:\s*\[manual\]",
            "policy_file": "docs/rules/governance.md",
            "required_section": "Folder Purity Validation (T3d)",
        },
        "excluded_patterns": {
            "description": "Exclude patterns must have architectural rationale",
            "pattern": r"exclude:\s*\(",
            "policy_file": "docs/rules/governance.md",
            "required_section": "Third-Party Code Exclusions",
        },
    },
    "pytest.ini": {
        "testpaths_changes": {
            "description": "Testpaths changes must have documented rationale",
            "pattern": r"testpaths\s*=",
            "policy_file": "docs/rules/governance.md",
            "required_section": "pytest.ini testpaths Adjustment (Phase 2.8.3)",
        }
    },
    "ops_scripts/ci/check_anti_patterns.py": {
        "baseline_protection": {
            "description": "Baseline write protection must be implemented",
            "pattern": r"ALLOW_LANDMINE_BASELINE_WRITE",
            "policy_file": "docs/rules/governance.md",
            "required_section": "Baseline Write Protection (Phase 2.7)",
        }
    },
}


def load_policy_sections(policy_file: Path) -> dict[str, bool]:
    """Load which sections exist in the governance policy file."""
    if not policy_file.exists():
        return {}

    content = policy_file.read_text(encoding="utf-8")
    sections = {}

    # Extract section headers (## Section Name and ### Subsection Name)
    import re

    for match in re.finditer(r"^#{2,3}\s+(.+)$", content, re.MULTILINE):
        section_name = match.group(1).strip()
        sections[section_name] = True

    return sections


def validate_file_governance(file_path: Path, policy_sections: dict[str, bool]) -> list[str]:
    """Validate that a file's changes have proper governance documentation."""
    violations = []

    # Get governance requirements for this file
    try:
        rel_path = str(file_path.relative_to(Path.cwd()))
    except ValueError:
        # File is not under current directory, use absolute path as key
        rel_path = str(file_path)
    requirements = GOVERNANCE_REQUIREMENTS.get(rel_path, {})

    if not requirements:
        return violations

    # Check file content against each requirement
    content = file_path.read_text(encoding="utf-8")

    for req_name, req_config in requirements.items():
        pattern = req_config["pattern"]
        policy_file = req_config["policy_file"]
        required_section = req_config["required_section"]

        # Check if the pattern exists in the file
        import re

        if re.search(pattern, content):
            # Pattern found - check if policy documentation exists
            if not policy_sections.get(required_section):
                violations.append(
                    f"{req_name}: {req_config['description']}. "
                    f"Missing section '{required_section}' in {policy_file}"
                )

    return violations


def validate_governance_consistency() -> list[str]:
    """Validate that governance policies are internally consistent."""
    violations = []
    policy_file = Path("docs/rules/governance.md")

    if not policy_file.exists():
        violations.append("Governance policy file does not exist: docs/rules/governance.md")
        return violations

    # Load policy sections
    policy_sections = load_policy_sections(policy_file)

    # Check each governed file
    for file_pattern in GOVERNANCE_REQUIREMENTS:
        file_path = Path(file_pattern)
        if file_path.exists():
            file_violations = validate_file_governance(file_path, policy_sections)
            violations.extend([f"{file_path}: {v}" for v in file_violations])

    # Validate that .windsurfrules references governance policies
    windsurf_rules = Path(".windsurfrules")
    if windsurf_rules.exists():
        content = windsurf_rules.read_text(encoding="utf-8")
        if "docs/rules/governance.md" not in content:
            violations.append(".windsurfrules: Should reference docs/rules/governance.md for policy details")

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate governance policy compliance")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    violations = validate_governance_consistency()

    if violations:
        print("[GOVERNANCE] Policy validation failed:")
        for violation in violations:
            print(f"  - {violation}")

        if args.verbose:
            print("\n[GOVERNANCE] Required policy sections:")
            policy_file = Path("docs/rules/governance.md")
            if policy_file.exists():
                sections = load_policy_sections(policy_file)
                for section in sorted(sections.keys()):
                    print(f"  ✓ {section}")

        print("\n[GOVERNANCE] Fix required:")
        print("  1. Update docs/rules/governance.md with missing sections")
        print("  2. Ensure all configuration changes have policy documentation")
        print("  3. Reference governance policies in relevant files")

        return 1
    else:
        if args.verbose:
            print("[GOVERNANCE] All policies properly documented and enforced")
        return 0


if __name__ == "__main__":
    sys.exit(main())
