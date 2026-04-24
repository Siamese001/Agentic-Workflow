"""Tests for tools.guardian.bulk_fix_bare_markers (W17.b-tail 2026-04-24).

Critical invariants:
- Long-form exemptions (`# guardian: allow-X -- justification`) are NEVER rewritten.
- Short-form exemptions (`# guardian: allow-X`) are NEVER rewritten.
- Bare review-notes (`# guardian: <prose>` where prose doesn't start with `allow-`)
  ARE rewritten to `# review: <prose>` with body preserved verbatim.
- Indentation and trailing content on the line are preserved.
- Non-.py files and excluded paths are skipped.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure tools/ is importable
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.guardian.bulk_fix_bare_markers import (
    _ANY_GUARDIAN_RE,
    _is_bare_marker,
    _is_prod_path,
    _rewrite_file,
)


class TestBareMarkerClassifier:
    @pytest.mark.parametrize(
        "body",
        [
            " allow-broad-exception -- hook fail-soft",  # long form
            " allow-silent-swallow",                     # short form
            " allow-magic-config",
            "allow-type-erasure",                        # no leading space
            " allow-global-mutation -- env init",
        ],
    )
    def test_allow_prefix_is_not_bare(self, body: str) -> None:
        assert _is_bare_marker(body) is False

    @pytest.mark.parametrize(
        "body",
        [
            " Parsing errors need separate handling",
            " RoutingCapacityError should be handled",
            " Add error context logging",
            " TODO: refactor this",
            "",  # empty
            "   ",  # whitespace only
        ],
    )
    def test_non_allow_is_bare(self, body: str) -> None:
        assert _is_bare_marker(body) is True


class TestRegexBacktrackSafety:
    """Regression: previous regex used a negative lookahead that backtracked.

    These tests ensure the NEW implementation does not rewrite exemption
    directives even when `\\s*` could have given back characters in the old
    regex.
    """

    @pytest.mark.parametrize(
        "line",
        [
            "# guardian: allow-broad-except -- hook fail-soft contract",
            "    # guardian: allow-silent-swallow",
            "foo  # guardian: allow-silent-swallow -- audit log write",
            "except X:  # guardian: allow-silent-swallow",
        ],
    )
    def test_exemption_lines_are_preserved(
        self, tmp_path: Path, line: str
    ) -> None:
        file = tmp_path / "sample.py"
        file.write_text(line + "\n", encoding="utf-8")
        edit = _rewrite_file(file, apply=True)
        assert edit.count == 0
        assert file.read_text(encoding="utf-8") == line + "\n"


class TestRewriteBehavior:
    def test_bare_is_rewritten(self, tmp_path: Path) -> None:
        file = tmp_path / "sample.py"
        original = "x = 1  # guardian: Parsing errors need handling\n"
        expected = "x = 1  # review: Parsing errors need handling\n"
        file.write_text(original, encoding="utf-8")
        edit = _rewrite_file(file, apply=True)
        assert edit.count == 1
        assert file.read_text(encoding="utf-8") == expected

    def test_indentation_preserved(self, tmp_path: Path) -> None:
        file = tmp_path / "sample.py"
        original = "    # guardian: TODO refactor\n"
        expected = "    # review: TODO refactor\n"
        file.write_text(original, encoding="utf-8")
        _rewrite_file(file, apply=True)
        assert file.read_text(encoding="utf-8") == expected

    def test_dry_run_does_not_write(self, tmp_path: Path) -> None:
        file = tmp_path / "sample.py"
        original = "# guardian: review note\n"
        file.write_text(original, encoding="utf-8")
        edit = _rewrite_file(file, apply=False)
        assert edit.count == 1
        assert file.read_text(encoding="utf-8") == original

    def test_mixed_file_only_rewrites_bare(self, tmp_path: Path) -> None:
        file = tmp_path / "mixed.py"
        original = (
            "a = 1  # guardian: allow-silent-swallow\n"          # keep
            "b = 2  # guardian: ReviewNote needed\n"             # rewrite
            "c = 3  # guardian: allow-broad -- with justification\n"  # keep
            "d = 4  # guardian: TODO\n"                          # rewrite
            "e = 5  # regular comment\n"                         # keep
        )
        file.write_text(original, encoding="utf-8")
        edit = _rewrite_file(file, apply=True)
        assert edit.count == 2
        result = file.read_text(encoding="utf-8")
        assert "# guardian: allow-silent-swallow" in result
        assert "# guardian: allow-broad -- with justification" in result
        assert "# review: ReviewNote needed" in result
        assert "# review: TODO" in result
        assert "# regular comment" in result

    def test_empty_body_rewritten(self, tmp_path: Path) -> None:
        file = tmp_path / "sample.py"
        file.write_text("# guardian:\n", encoding="utf-8")
        edit = _rewrite_file(file, apply=True)
        assert edit.count == 1
        assert file.read_text(encoding="utf-8") == "# review:\n"

    def test_preview_captured(self, tmp_path: Path) -> None:
        file = tmp_path / "sample.py"
        file.write_text(
            "# guardian: one\n# guardian: two\n# guardian: three\n# guardian: four\n",
            encoding="utf-8",
        )
        edit = _rewrite_file(file, apply=True)
        assert edit.count == 4
        assert len(edit.preview) == 3  # capped at 3

    def test_regex_does_not_match_prose_containing_guardian(
        self, tmp_path: Path
    ) -> None:
        file = tmp_path / "sample.py"
        # String literal mentioning "guardian:" should not be rewritten.
        original = 'msg = "The guardian: woke"\n'
        file.write_text(original, encoding="utf-8")
        edit = _rewrite_file(file, apply=True)
        # The regex DOES match (it's a substring match), but because "The " is
        # not a # prefix, the match group 'prefix' won't be a comment marker.
        # However _ANY_GUARDIAN_RE requires `#` before `guardian:`, so no match.
        match = _ANY_GUARDIAN_RE.search(original)
        assert match is None, "regex must require # prefix before guardian:"
        assert edit.count == 0
        assert file.read_text(encoding="utf-8") == original


class TestPathExclusion:
    @pytest.mark.parametrize(
        "path",
        [
            "agentic_core/L5_safety/foo.py",
            "tools/debug/_w17_guardian_triage.py",
            "apps_shared/utils/bar.py",
        ],
    )
    def test_prod_paths_included(self, path: str) -> None:
        assert _is_prod_path(path) is True

    @pytest.mark.parametrize(
        "path",
        [
            "archives/2026-04-23/foo.py",
            "docs/architecture/bar.py",
            "tools/archive/old.py",
            "tools/silent_swallower_report.json",
            ".backup/guardian_tests/baz.py",
            "some/_backup/file.py",
        ],
    )
    def test_excluded_paths(self, path: str) -> None:
        assert _is_prod_path(path) is False
