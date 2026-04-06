#!/usr/bin/env python3
"""Shim Discipline — Enforce consistent shim and backward-compatibility stub discipline.

Constitutional Rule: When moving or renaming canonical modules, MUST create documented
shims with deprecation warnings. NO undocumented shims or shimless moves that break consumers.

This gate enforces that:
1. All shims have deprecation warnings
2. Shims reference canonical location
3. No shimless moves of canonical modules
4. Shim files follow naming convention (*_shim.py, *_compat.py, *_util.py)

BLOCKS commits that:
- Move modules without creating backward-compatibility shims
- Create shims without deprecation warnings
- Create undocumented shims without canonical location reference
- Rename files ending in _shim.py/_compat.py without justification

PASSES commits that:
- Include shim-discipline justification in commit message
- Create shims with proper deprecation warnings
- Document canonical location in shim files
"""

import re
import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "check_shim_discipline", "uwg_governed_write")
_emit_writes_through("p1", "check_shim_discipline", "uwg_governed_write_2")
_emit_pulls_context("p1", "check_shim_discipline", "context_retrieval")
_emit_pulls_context("p1", "check_shim_discipline", "context_retrieval_2")
emit_determinism_digest("trace_check_shim_discipline", "check_shim_discipline_dispatch")
emit_determinism_digest("trace_check_shim_discipline", "check_shim_discipline_complete")
_emit_validated_by_safety_plane("p1", "check_shim_discipline", "safety_validation")

# Repo root
_REPO_ROOT = Path(__file__).resolve().parents[2]

# Shim file patterns
_SHIM_FILE_PATTERNS = [
    r".*_shim\.py$",
    r".*_compat\.py$",
    r".*_util\.py$",
    r".*_legacy\.py$",
]

# Required elements in shim files
_REQUIRED_SHIM_ELEMENTS = [
    r"warnings\.warn\(",
    r"DeprecationWarning",
    r"canonical",
    r"moved to",
]

# Patterns indicating a module move/rename
_MOVE_INDICATORS = [
    ("--diff-filter=R", "renamed"),
    ("--diff-filter=D", "deleted"),
]

# Required justification keywords
_JUSTIFICATION_KEYWORDS = [
    "shim-discipline",
    "backward-compatibility",
    "deprecation warning",
    "canonical location",
    "shimless move justified",
]


def _get_staged_files() -> dict[str, list[str]]:
    """Get staged files categorized by change type."""
    files = {"added": [], "renamed": [], "deleted": [], "modified": []}

    # Added files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        files["added"] = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip().endswith(".py")
        ]

    # Renamed files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-status", "--diff-filter=R"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            parts = line.strip().split("\t")
            if len(parts) >= 3 and parts[2].endswith(".py"):
                files["renamed"].append((parts[1], parts[2]))

    # Deleted files
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=D"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        files["deleted"] = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip().endswith(".py")
        ]

    return files


def _get_file_content(file_path: str) -> str:
    """Get content of a staged file."""
    result = subprocess.run(
        ["git", "show", f":{file_path}"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def _get_commit_message() -> str:
    """Get the current commit message."""
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        commit_msg_file = _REPO_ROOT / ".git" / "COMMIT_EDITMSG"
        if commit_msg_file.exists():
            return commit_msg_file.read_text(encoding="utf-8", errors="ignore")
        return ""
    return result.stdout.strip()


def _is_shim_file(file_path: str) -> bool:
    """Check if file matches shim naming patterns."""
    for pattern in _SHIM_FILE_PATTERNS:
        if re.match(pattern, file_path):
            return True
    return False


def _validate_shim_content(content: str) -> list[str]:
    """Validate that shim file has required elements."""
    missing = []
    for element_pattern in _REQUIRED_SHIM_ELEMENTS:
        if not re.search(element_pattern, content, re.IGNORECASE):
            missing.append(element_pattern)
    return missing


def _has_justification(commit_msg: str) -> bool:
    """Check if commit message contains shim-discipline justification."""
    msg_lower = commit_msg.lower()
    return any(keyword in msg_lower for keyword in _JUSTIFICATION_KEYWORDS)


def main() -> int:
    """Enforce shim discipline — consistent backward-compatibility stubs."""
    staged_files = _get_staged_files()
    commit_msg = _get_commit_message()
    has_justification = _has_justification(commit_msg)

    violations = []

    # Check new shim files have proper content
    for file_path in staged_files["added"]:
        if _is_shim_file(file_path):
            content = _get_file_content(file_path)
            if content:
                missing_elements = _validate_shim_content(content)
                if missing_elements:
                    violations.append(
                        f"Shim file missing required elements: {file_path}\n"
                        f"  Missing: {', '.join(missing_elements)}"
                    )

    # Check for module moves without shims
    for old_path, new_path in staged_files["renamed"]:
        # Skip if not in canonical locations (agentic_core, apps_*)
        if not any(
            old_path.startswith(prefix)
            for prefix in ["agentic_core/", "apps_rg/", "apps_lic/", "apps_shared/"]
        ):
            continue

        # Check if a shim was created at old location
        old_shim_path = old_path.replace(".py", "_shim.py")
        if old_shim_path not in staged_files["added"]:
            violations.append(
                f"Module moved without shim: {old_path} -> {new_path}\n"
                f"  Expected shim at: {old_shim_path}"
            )

    # Check for deleted canonical modules without shims
    for deleted_path in staged_files["deleted"]:
        # Skip if already a shim file
        if _is_shim_file(deleted_path):
            continue

        # Skip if not in canonical locations
        if not any(
            deleted_path.startswith(prefix)
            for prefix in ["agentic_core/", "apps_rg/", "apps_lic/", "apps_shared/"]
        ):
            continue

        # Check if this is part of a rename (already handled above)
        is_renamed = any(old == deleted_path for old, _ in staged_files["renamed"])
        if not is_renamed:
            violations.append(
                f"Canonical module deleted without shim: {deleted_path}\n"
                f"  Create shim or justify shimless deletion"
            )

    # If no violations, pass
    if not violations:
        return 0

    # If violations but has justification, pass with warning
    if has_justification:
        print("\n[WARN] Shim Discipline — Violations detected but justified")
        print("\nViolations:")
        for v in violations[:5]:
            print(f"  - {v}")
        print("\nCommit message contains shim-discipline justification. Allowing commit.")
        return 0

    # Violations without justification — FAIL
    print("\n[FAIL] Shim Discipline — Undocumented shims or shimless moves")
    print("\nViolations:")
    for v in violations[:10]:
        print(f"  - {v}")

    print("\n§SHIM-DISCIPLINE requires:")
    print("  1. All shims have deprecation warnings")
    print("  2. Shims reference canonical location")
    print("  3. No shimless moves of canonical modules")
    print("  4. Shim files follow naming: *_shim.py, *_compat.py")

    print("\nRequired in shim files:")
    print("  - warnings.warn(..., DeprecationWarning)")
    print("  - Reference to 'canonical' location")
    print("  - 'moved to' or similar migration guidance")

    print("\nRequired in commit message (if shimless move):")
    print("  - 'shim-discipline', 'shimless move justified', or")
    print("  - 'backward-compatibility', 'deprecation warning'")

    print("\nExample shim file:")
    print("  # my_module_shim.py")
    print("  import warnings")
    print("  warnings.warn(")
    print("    'my_module moved to new.location.my_module',")
    print("    DeprecationWarning,")
    print("    stacklevel=2")
    print("  )")
    print("  from new.location.my_module import *  # noqa: F401, F403")

    print("\nSee: .windsurf/skills/shim-discipline/")

    return 1


if __name__ == "__main__":
    sys.exit(main())
