#!/usr/bin/env python3
"""
Governance Policy Validation Hook

Enforces that governance policy changes are properly documented and authorized.
Validates that changes to critical configurations have corresponding policy updates.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Governance policies that require documentation.
# IMPORTANT: Requirements are enforced ONLY when the governed file is changed (staged or unstaged).
GOVERNANCE_REQUIREMENTS: dict[str, dict[str, dict[str, str]]] = {
    ".pre-commit-config.yaml": {
        "excluded_patterns": {
            "description": "Exclude patterns must have architectural rationale",
            "pattern": r"^\s*exclude:\s*\(",
            "policy_file": "docs/rules/governance.md",
            "required_section": "Third-Party Code Exclusions",
        },
    },
    "pytest.ini": {
        "authoritative_suite_policy": {
            "description": "pytest.ini scope changes must have documented policy (authoritative suite + reversibility)",
            "pattern": r"^\s*(testpaths|addopts)\s*=",
            "policy_file": "docs/rules/governance.md",
            "required_section": "Pytest Authoritative Suite",
        }
    },
    "ops_scripts/ci/check_anti_patterns.py": {
        "baseline_protection": {
            "description": "Baseline write protection must be implemented",
            "pattern": r"ALLOW_LANDMINE_BASELINE_WRITE",
            "policy_file": "docs/rules/governance.md",
            "required_section": "Baseline Write Protection",
        }
    },
}

# Any hook moved to manual stage must be documented with metadata under a section that names the hook id.
# Required section header format (example): "## Folder Purity Validation (T3d)"
# i.e., the hook id must appear in parentheses to allow stable matching.
MANUAL_HOOK_REQUIRED_FIELDS = [
    "### Rationale",
    "### Scope",
    "### Reversibility",
    "### Owner",
    "### Sunset Criteria",
]


def load_policy_sections(policy_file: Path) -> dict[str, bool]:
    """Load which sections exist in the governance policy file."""
    if not policy_file.exists():
        return {}

    content = policy_file.read_text(encoding="utf-8")
    sections = {}

    # Extract section headers (## Section Name and ### Subsection Name)
    for match in re.finditer(r"^#{2,3}\s+(.+)$", content, re.MULTILINE):
        section_name = match.group(1).strip()
        sections[section_name] = True

    return sections


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, check=False, capture_output=True, text=True)
    return (p.stdout or "") + (p.stderr or "")


def _git_diff(path: Path) -> str:
    # Include both staged and unstaged diffs so the hook behaves predictably during local iteration.
    return _run(["git", "diff", "--cached", "--", str(path)]) + _run(["git", "diff", "--", str(path)])


def _file_changed(path: Path) -> bool:
    return bool(_git_diff(path).strip())


def _require_fields_under_section(
    doc_text: str, section_header: str, required_fields: list[str]
) -> list[str]:
    """
    Require specific field headings (e.g., '### Rationale') under a given '## ...' section.
    Best-effort parsing: scans from section header until next '## ' header.
    """
    if section_header not in doc_text:
        return required_fields[:]

    start = doc_text.find(section_header)
    next_idx = doc_text.find("\n## ", start + 1)
    block = doc_text[start:] if next_idx == -1 else doc_text[start:next_idx]

    missing: list[str] = []
    for f in required_fields:
        if f not in block:
            missing.append(f)
    return missing


def _parse_manual_stage_hook_ids(precommit_text: str) -> list[str]:
    """
    Extract hook ids that are moved to manual stage.
    Supports both:
      - stages: [manual]
      - stages:
          - manual
    """
    hook_blocks = re.split(r"(?m)^\s*-\s+id:\s+", precommit_text)
    if len(hook_blocks) <= 1:
        return []

    ids: list[str] = []
    # First split chunk is preamble; subsequent chunks start with "<id>\n..."
    for chunk in hook_blocks[1:]:
        hook_id = chunk.splitlines()[0].strip()
        body = chunk
        if re.search(r"(?m)^\s*stages:\s*\[\s*manual\s*\]\s*$", body):
            ids.append(hook_id)
            continue
        if re.search(r"(?ms)^\s*stages:\s*\n(?:\s*-\s*.+\n)*\s*-\s*manual\s*$", body):
            ids.append(hook_id)
            continue
    return sorted(set(ids))


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

    # Only enforce governance requirements if the file actually changed.
    # This prevents false positives where a pattern exists but no governance-relevant edit occurred.
    if not _file_changed(file_path):
        return violations

    # Check file content against each requirement
    content = _read_text(file_path)

    for req_name, req_config in requirements.items():
        pattern = req_config["pattern"]
        policy_file = req_config["policy_file"]
        required_section = req_config["required_section"]

        # Check if the pattern exists in the file
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
    policy_text = _read_text(policy_file)

    # Check each governed file
    for file_pattern in GOVERNANCE_REQUIREMENTS:
        file_path = Path(file_pattern)
        if file_path.exists():
            file_violations = validate_file_governance(file_path, policy_sections)
            violations.extend([f"{file_path}: {v}" for v in file_violations])

    # Manual-stage hook governance: require metadata fields under a section that includes the hook id.
    precommit = Path(".pre-commit-config.yaml")
    if precommit.exists() and _file_changed(precommit):
        precommit_text = _read_text(precommit)
        manual_ids = _parse_manual_stage_hook_ids(precommit_text)
        for hook_id in manual_ids:
            # Require a stable section header containing the hook id in parentheses.
            matching_headers = [
                h for h in policy_sections.keys() if re.search(rf"\({re.escape(hook_id)}\)", h)
            ]
            if not matching_headers:
                violations.append(
                    f".pre-commit-config.yaml: hook '{hook_id}' moved to manual stage but governance.md "
                    f"lacks a section header containing '({hook_id})'"
                )
                continue
            # Enforce metadata under the first matching header.
            header = matching_headers[0]
            missing_fields = _require_fields_under_section(
                policy_text, f"## {header}", MANUAL_HOOK_REQUIRED_FIELDS
            )
            if missing_fields:
                violations.append(
                    f"docs/rules/governance.md: section '{header}' missing required subsections: "
                    + ", ".join(missing_fields)
                )

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
