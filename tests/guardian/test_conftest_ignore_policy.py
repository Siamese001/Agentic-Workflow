"""
Ignore List Governance Ratchet.

Prevents silent expansion of collect_ignore_glob in tests/guardian/conftest.py.
Every exclusion must be in the locked allowlist and must have:
- a TODO(#<id>) ticket ref
- an owner=@<handle> tag
- a review_by=YYYY-MM-DD expiration date (fails once expired)

If the ignore list changes, this test FAILS until the locked snapshot is updated
with a justification and code review.
"""

from __future__ import annotations

import ast
import datetime
import re
import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

pytestmark = pytest.mark.guardian

# ---------------------------------------------------------------------------
# Locked snapshot — update ONLY with code review justification
# ---------------------------------------------------------------------------

LOCKED_IGNORE_ALLOWLIST: frozenset[str] = frozenset(
    {
        "test_comprehensive_structure.py",
        "test_mro_integrity.py",
    },
)

MAX_IGNORES: int = 4  # Hard ceiling — requires code review to raise

# Every ignore entry MUST have a TODO comment with a ticket/issue reference
# Pattern: TODO(#<digits>) or TODO(<identifier>):
_TICKET_REF_PATTERN = re.compile(r"TODO\([#\w-]+")
_OWNER_PATTERN = re.compile(r"owner=@[\w-]+")
_REVIEW_BY_PATTERN = re.compile(r"review_by=(\d{4}-\d{2}-\d{2})")

CONFTEST_PATH = PROJECT_ROOT / TESTS_DIR / "guardian" / "conftest.py"

# Inject "today" for deterministic test execution; override in fixtures if needed
_TODAY: datetime.date = datetime.date.today()


# ---------------------------------------------------------------------------
# AST extraction of collect_ignore_glob from conftest.py
# ---------------------------------------------------------------------------


def _extract_ignore_glob_from_conftest() -> list[str]:
    """AST-extract the collect_ignore_glob list from conftest.py."""
    source = CONFTEST_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(CONFTEST_PATH))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "collect_ignore_glob":
                    if isinstance(node.value, ast.List):
                        return [
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                        ]
    return []


def _extract_ignore_section_comments() -> str:
    """Extract the comment block around collect_ignore_glob for ticket ref validation."""
    source = CONFTEST_PATH.read_text(encoding="utf-8")
    lines = source.splitlines()
    in_section = False
    section_lines: list[str] = []
    for line in lines:
        if "collect_ignore_glob" in line:
            in_section = True
        if in_section:
            section_lines.append(line)
            if line.strip() == "]":
                break
        # Also capture comments immediately before the assignment
        if not in_section and line.strip().startswith("#"):
            section_lines.append(line)
        elif not in_section and not line.strip().startswith("#"):
            section_lines = []  # reset if non-comment line before assignment
    return "\n".join(section_lines)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestIgnoreListGovernance:
    """collect_ignore_glob must match the locked allowlist exactly."""

    def test_conftest_exists(self):
        assert CONFTEST_PATH.exists(), f"conftest.py not found at {CONFTEST_PATH}"

    def test_ignore_list_matches_locked_allowlist(self):
        """Ignore list must match the frozen allowlist — no silent additions."""
        actual = set(_extract_ignore_glob_from_conftest())
        assert actual == LOCKED_IGNORE_ALLOWLIST, (
            f"collect_ignore_glob changed without updating locked allowlist.\n"
            f"  Expected: {sorted(LOCKED_IGNORE_ALLOWLIST)}\n"
            f"  Actual:   {sorted(actual)}\n"
            f"Update LOCKED_IGNORE_ALLOWLIST in test_conftest_ignore_policy.py "
            f"with code review justification."
        )

    def test_ignore_list_does_not_exceed_max(self):
        """Ignore list must not exceed MAX_IGNORES ceiling."""
        actual = _extract_ignore_glob_from_conftest()
        assert len(actual) <= MAX_IGNORES, (
            f"collect_ignore_glob has {len(actual)} entries, exceeds MAX_IGNORES ({MAX_IGNORES}). "
            f"Fix the underlying issues instead of adding more ignores."
        )

    def test_each_ignore_has_ticket_reference(self):
        """Every ignore entry must have a TODO(#<id>) in the surrounding comments."""
        section = _extract_ignore_section_comments()
        actual = _extract_ignore_glob_from_conftest()
        for entry in actual:
            # Strip extension for flexible matching
            stem = entry.replace(".py", "")
            # Check that a TODO ticket ref mentions this file
            has_ref = any(_TICKET_REF_PATTERN.search(line) and stem in line for line in section.splitlines())
            assert has_ref, (
                f"Ignore entry '{entry}' has no TODO(#<id>) ticket reference. "
# TODO: Address this issue - f"Add a comment like: # TODO(#123): fix {entry} (<reason>)"
            )


def _get_comment_line_for_entry(section: str, stem: str) -> str | None:
    """Find the TODO comment line that references a given file stem."""
    for line in section.splitlines():
        if stem in line and _TICKET_REF_PATTERN.search(line):
            return line
    return None


class TestIgnoreListExpiration:
    """Each ignore entry must have an owner and a non-expired review_by date."""

    def test_each_ignore_has_owner(self):
        """Every ignore entry must have owner=@<handle> in its TODO comment."""
        section = _extract_ignore_section_comments()
        actual = _extract_ignore_glob_from_conftest()
        for entry in actual:
            stem = entry.replace(".py", "")
            line = _get_comment_line_for_entry(section, stem)
            assert line is not None, f"No TODO comment found for '{entry}'"
            assert _OWNER_PATTERN.search(line), (
                f"Ignore entry '{entry}' missing owner tag. Add owner=@<handle> to the TODO comment."
            )

    def test_each_ignore_has_review_by_date(self):
        """Every ignore entry must have review_by=YYYY-MM-DD in its TODO comment."""
        section = _extract_ignore_section_comments()
        actual = _extract_ignore_glob_from_conftest()
        for entry in actual:
            stem = entry.replace(".py", "")
            line = _get_comment_line_for_entry(section, stem)
            assert line is not None, f"No TODO comment found for '{entry}'"
            assert _REVIEW_BY_PATTERN.search(line), (
                f"Ignore entry '{entry}' missing review_by date. "
                f"Add review_by=YYYY-MM-DD to the TODO comment."
            )

    def test_no_expired_ignores(self):
        """Ignore entries with review_by date in the past must fail."""
        section = _extract_ignore_section_comments()
        actual = _extract_ignore_glob_from_conftest()
        for entry in actual:
            stem = entry.replace(".py", "")
            line = _get_comment_line_for_entry(section, stem)
            if line is None:
                continue
            match = _REVIEW_BY_PATTERN.search(line)
            if match:
                review_date = datetime.date.fromisoformat(match.group(1))
                assert review_date >= _TODAY, (
                    f"Ignore entry '{entry}' expired on {review_date}. "
                    f"Either fix the underlying issue or extend the review_by date "
                    f"with justification."
                )
