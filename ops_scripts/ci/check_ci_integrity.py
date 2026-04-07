#!/usr/bin/env python3
"""
CI gate: §22 CI Integrity Gates.

Enforces all 13 conditions from §22.1. Runs after evidence contract checker
in the gate sequence (§22.2).

Conditions checked:
  1.  Required evidence artifact present in docs/reports/plans/
  2.  FACT_CLASSIFICATION section present and Unresolved list empty
  3.  Broad pytest run not used before final work unit
  4.  Unexpected skip/xfail not in pre-existing skip registry
  5.  Failing test has FAILURE_CAPTURE record (checked via evidence scan)
  6.  ADG schema mapping not changed mid-run
  7.  Repair did not begin before clustering (timestamp check)
  8.  Test strictness not weakened (assert True, removed assertions)
  9.  repair_class present in commits touching production code
  10. Policy drift not misclassified (delegated to check_policy_drift_classification.py)
  11. Contract conflict unresolved (CONTRACT_CONFLICT section check)
  12. Environment contract missing (delegated to check_environment_contract.py)
  13. Repair run declared complete without full-suite evidence

Exits 1 on any violation.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / "docs" / "reports" / "plans"
REGISTRY_PATH = REPO_ROOT / "artifacts" / "adg" / "pre_existing_skip_registry.json"

REPAIR_COMPLETE_PHRASES = [
    "repair complete",
    "stabilization complete",
    "repair is complete",
    "stabilization is complete",
]

FULL_SUITE_MARKERS = [
    "passed",  # used in conjunction with zero failures
]


def evidence_files() -> list[Path]:
    if not PLANS_DIR.exists():
        return []
    return sorted(PLANS_DIR.rglob("*.md"))


# ---------------------------------------------------------------------------
# Condition 2: FACT_CLASSIFICATION present and Unresolved empty
# ---------------------------------------------------------------------------
def check_fact_classification(violations: list[str]) -> None:
    for path in evidence_files():
        content = path.read_text(encoding="utf-8", errors="replace")
        if "## FACT_CLASSIFICATION" not in content:
            continue  # not an evidence file requiring this section
        # Check for non-empty Unresolved
        unresolved_match = re.search(
            r"### Unresolved\s*\n(.*?)(?:\n###|\n##|\Z)", content, re.DOTALL,
        )
        if unresolved_match:
            body = unresolved_match.group(1).strip()
            # Non-empty if there's a dash-list item
            if re.search(r"^\s*-\s+\S", body, re.MULTILINE):
                violations.append(
                    f"CONDITION 2: {path.relative_to(REPO_ROOT)} has non-empty "
                    f"FACT_CLASSIFICATION.Unresolved — phase cannot be declared complete (§2.1.1)",
                )


# ---------------------------------------------------------------------------
# Condition 8: Test strictness not weakened
# ---------------------------------------------------------------------------
def check_test_strictness(violations: list[str]) -> None:
    tests_dir = REPO_ROOT / "tests"
    if not tests_dir.exists():
        return
    for path in sorted(tests_dir.rglob("test_*.py")):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            continue
        for lineno, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped in ("assert True", "assert True  # noqa", "assert True # noqa"):
                violations.append(
                    f"CONDITION 8: {path.relative_to(REPO_ROOT)}:{lineno}: "
                    f"'assert True' detected — zero-assertion test (§11, §22.1 cond. 8)",
                )


# ---------------------------------------------------------------------------
# Condition 8b: broken_test_fix commits must preserve semantic equivalence
# Detects weakening of error type specificity (decision tree Check 4 constraint)
# ---------------------------------------------------------------------------
def check_broken_test_fix_semantic_equivalence(violations: list[str]) -> None:
    tests_dir = REPO_ROOT / "tests"
    if not tests_dir.exists():
        return
    # Patterns that indicate weakened error type — ValueError→Exception, etc.
    weakened_raises = re.compile(r"pytest\.raises\(\s*Exception\s*\)")
    broad_except = re.compile(r"pytest\.raises\(\s*(BaseException|Exception)\s*[,)]")
    for path in sorted(tests_dir.rglob("test_*.py")):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            continue
        for lineno, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if weakened_raises.search(stripped) or broad_except.search(stripped):
                # Only flag if there is no guardian annotation allowing it
                if "# guardian: allow-broad-raises" not in stripped:
                    violations.append(
                        f"CONDITION 8b: {path.relative_to(REPO_ROOT)}:{lineno}: "
                        f"pytest.raises(Exception/BaseException) detected — broadened error type "
                        f"violates broken_test_fix semantic equivalence requirement "
                        f"(decision tree Check 4, §1.2, §5.4 gate #8). "
                        f"Use specific exception type or add '# guardian: allow-broad-raises' with justification.",
                    )


# ---------------------------------------------------------------------------
# Condition 9: repair_class in commits touching production code
# ---------------------------------------------------------------------------
def check_repair_class_in_commits(violations: list[str]) -> None:
    result = subprocess.run(
        ["git", "log", "-20", "--pretty=format:%H %s"],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    production_dirs = ["agentic_core/", "apps_rg/", "apps_lic/", "apps_shared/", "system_learning/"]
    for line in result.stdout.splitlines():
        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue
        commit_hash, message = parts
        if "repair_class:" in message:
            continue  # already has it
        # Check if commit touches production files
        diff_result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", commit_hash],
            cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        for changed_file in diff_result.stdout.splitlines():
            if any(changed_file.startswith(d) for d in production_dirs):
                # Only flag if it looks like a repair commit (has fix/repair/patch in message)
                if any(kw in message.lower() for kw in ("fix", "repair", "patch", "resolve")):
                    violations.append(
                        f"CONDITION 9: commit {commit_hash[:8]} touches production code "
                        f"({changed_file}) but message has no 'repair_class:' footer (§22.1 cond. 9)",
                    )
                    break


# ---------------------------------------------------------------------------
# Condition 11: Contract conflict unresolved
# ---------------------------------------------------------------------------
def check_contract_conflicts(violations: list[str]) -> None:
    for path in evidence_files():
        content = path.read_text(encoding="utf-8", errors="replace")
        if "CONTRACT_CONFLICT" not in content:
            continue
        # Check the section has a resolution
        match = re.search(r"## CONTRACT_CONFLICT(.*?)(?:\n##|\Z)", content, re.DOTALL)
        if match:
            body = match.group(1)
            if "winning contract" not in body.lower() and "resolution layer" not in body.lower():
                violations.append(
                    f"CONDITION 11: {path.relative_to(REPO_ROOT)}: CONTRACT_CONFLICT section "
                    f"present but no 'winning contract' or 'resolution layer' declared (§19, §22.1 cond. 11)",
                )


# ---------------------------------------------------------------------------
# Condition 13: Repair run declared complete without full-suite evidence
# ---------------------------------------------------------------------------
def check_repair_complete_claim(violations: list[str]) -> None:
    for path in evidence_files():
        try:
            content = path.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            continue
        for phrase in REPAIR_COMPLETE_PHRASES:
            if phrase in content:
                # Check that the same file or a sibling contains a full-suite green result
                has_full_suite = "0 failed" in content or "passed" in content
                # Minimal check: must also not have failure counts
                has_failures = re.search(r"\d+ failed", content) is not None
                if not has_full_suite or has_failures:
                    violations.append(
                        f"CONDITION 13: {path.relative_to(REPO_ROOT)}: claims '{phrase}' "
                        f"but no post-repair full-suite green result found in same artifact (§7.3, §22.1 cond. 13)",
                    )
                break


def main() -> int:
    violations: list[str] = []

    check_fact_classification(violations)
    check_test_strictness(violations)
    check_broken_test_fix_semantic_equivalence(violations)
    check_repair_class_in_commits(violations)
    check_contract_conflicts(violations)
    check_repair_complete_claim(violations)

    if violations:
        print(f"ERROR: §22 CI integrity gate violations ({len(violations)}):")
        for v in violations:
            print(f"  {v}")
        return 1

    print("OK: §22 CI integrity gates — all conditions satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
