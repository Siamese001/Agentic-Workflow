#!/usr/bin/env python3
"""Script Sprawl Guard — Prevent creation of new runner scripts and wrapper executables.

Constitutional Rule: NO new runner scripts or wrapper executables. Use canonical
invocation policy: `python -m module.path` for all Python modules.

This gate enforces that:
1. No new executable scripts in tools/ or ops_scripts/
2. No wrapper scripts that just invoke existing modules
3. All Python modules invoked via `python -m` canonical form
4. Entrypoints added to existing canonical locations only

BLOCKS commits that:
- Create new .py files in tools/ without justification
- Add wrapper scripts that duplicate module invocation
- Create runner scripts instead of using `python -m`

PASSES commits that:
- Modify existing scripts with justification
- Add modules (not runners) with proper invocation docs
- Include script-sprawl justification in commit message
"""

import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "check_script_sprawl", "uwg_governed_write")
_emit_writes_through("p1", "check_script_sprawl", "uwg_governed_write_2")
_emit_pulls_context("p1", "check_script_sprawl", "context_retrieval")
_emit_pulls_context("p1", "check_script_sprawl", "context_retrieval_2")
emit_determinism_digest("trace_check_script_sprawl", "check_script_sprawl_dispatch")
emit_determinism_digest("trace_check_script_sprawl", "check_script_sprawl_complete")
_emit_validated_by_safety_plane("p1", "check_script_sprawl", "safety_validation")

# Repo root
_REPO_ROOT = Path(__file__).resolve().parents[2]

# Directories where new scripts trigger scrutiny
_SCRIPT_DIRECTORIES = [
    "tools/",
    "ops_scripts/",
    "ops_scripts/ci/",
    "ops_scripts/hooks/",
    "ops_scripts/maintenance/",
]

# Patterns that indicate a runner/wrapper script
_RUNNER_PATTERNS = [
    r"if\s+__name__\s*==\s*['\"]__main__['\"]:",
    r"subprocess\.run\(",
    r"subprocess\.call\(",
    r"os\.system\(",
    r"exec\(",
]

# Required justification keywords in commit message
_JUSTIFICATION_KEYWORDS = [
    "script-sprawl",
    "canonical invocation",
    "no runner",
    "entrypoint justified",
    "CI gate",
    "pre-commit hook",
]

# Allowed script categories (must be documented in commit)
_ALLOWED_CATEGORIES = [
    "CI gate",
    "pre-commit hook",
    "maintenance utility",
    "deployment script",
]


def _get_staged_files() -> list[str]:
    """Get list of newly added Python files in script directories."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []

    staged = []
    for line in result.stdout.splitlines():
        file_path = line.strip()
        if not file_path.endswith(".py"):
            continue
        # Check if in script directories
        if any(file_path.startswith(script_dir) for script_dir in _SCRIPT_DIRECTORIES):
            staged.append(file_path)

    return staged


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


def _is_runner_script(content: str) -> bool:
    """Check if file content indicates a runner/wrapper script."""
    for pattern in _RUNNER_PATTERNS:
        if re.search(pattern, content):
            return True
    return False


def _has_justification(commit_msg: str) -> bool:
    """Check if commit message contains script-sprawl justification."""
    msg_lower = commit_msg.lower()
    return any(keyword in msg_lower for keyword in _JUSTIFICATION_KEYWORDS)


def _extract_category(commit_msg: str) -> str | None:
    """Extract script category from commit message."""
    msg_lower = commit_msg.lower()
    for category in _ALLOWED_CATEGORIES:
        if category.lower() in msg_lower:
            return category
    return None


def main() -> int:
    """Enforce script sprawl guard — prevent new runner scripts."""
    staged_files = _get_staged_files()
    if not staged_files:
        return 0

    commit_msg = _get_commit_message()
    has_justification = _has_justification(commit_msg)
    category = _extract_category(commit_msg)

    violations = []

    # Check each new script file
    for file_path in staged_files:
        content = _get_file_content(file_path)
        if not content:
            continue

        is_runner = _is_runner_script(content)
        if is_runner:
            violations.append(file_path)

    # If no violations, pass
    if not violations:
        return 0

    # If violations but has justification and category, pass with warning
    if has_justification and category:
        print("\n[WARN] Script Sprawl Guard — New scripts detected but justified")
        print(f"\nCategory: {category}")
        print("\nNew scripts:")
        for v in violations:
            print(f"  - {v}")
        print("\nCommit message contains justification. Allowing commit.")
        return 0

    # Violations without justification — FAIL
    print("\n[FAIL] Script Sprawl Guard — New runner scripts without justification")
    print("\nNew runner scripts detected:")
    for v in violations:
        print(f"  - {v}")

    print("\n§SCRIPT-SPRAWL-GUARD requires:")
    print("  1. NO new runner scripts or wrapper executables")
    print("  2. Use canonical invocation: `python -m module.path`")
    print("  3. Document category if script is truly necessary")
    print("\nAllowed categories (must be in commit message):")
    for cat in _ALLOWED_CATEGORIES:
        print(f"  - {cat}")

    print("\nRequired in commit message:")
    print("  - 'script-sprawl', 'canonical invocation', or")
    print("  - 'CI gate', 'pre-commit hook', etc.")

    print("\nCanonical invocation policy:")
    print("  [X] Create new runner script: tools/run_my_module.py")
    print("  [OK] Invoke module directly: python -m my_module")
    print("\n  [X] Wrapper script that calls subprocess.run()")
    print("  [OK] Add __main__.py to module for direct invocation")

    print("\nSee: .windsurf/skills/script-sprawl-guard/")

    return 1


if __name__ == "__main__":
    sys.exit(main())
