"""Tests for tools/guardian/idempotency_check.py — W3.6 residual gap coverage."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.guardian.idempotency_check import (
    _check_justification_quality,
    _count_guardians_on_line,
    scan_file,
    scan_new_string,
    scan_paths,
)

# ---------------------------------------------------------------------------
# _count_guardians_on_line
# ---------------------------------------------------------------------------


class TestCountGuardiansOnLine:
    def test_zero_on_plain_line(self):
        assert _count_guardians_on_line("x = 1") == 0

    def test_one_guardian(self):
        assert _count_guardians_on_line("x = 1  # guardian: allow-broad-exception -- reason") == 1

    def test_two_guardians_on_same_line(self):
        line = "x  # guardian: allow-broad-exception -- r1  # guardian: allow-bare-except -- r2"
        assert _count_guardians_on_line(line) == 2

    def test_partial_word_no_match(self):
        assert _count_guardians_on_line("# guardian-check: something") == 0


# ---------------------------------------------------------------------------
# _check_justification_quality
# ---------------------------------------------------------------------------


class TestCheckJustificationQuality:
    def test_good_justification_double_dash(self):
        line = "x  # guardian: allow-broad-exception -- catches only ValueError from parser"
        assert _check_justification_quality(line) is None

    def test_good_justification_single_dash(self):
        line = "x  # guardian: allow-broad-exception - catches only ValueError from parser"
        assert _check_justification_quality(line) is None

    def test_missing_justification(self):
        line = "x  # guardian: allow-broad-exception"
        result = _check_justification_quality(line)
        assert result is not None
        assert "Missing justification" in result

    def test_generic_justification_needed(self):
        line = "x  # guardian: allow-broad-exception -- needed"
        result = _check_justification_quality(line)
        assert result is not None
        assert "needed" in result

    def test_generic_justification_legacy(self):
        line = "x  # guardian: allow-broad-exception -- legacy"
        result = _check_justification_quality(line)
        assert result is not None
        assert "legacy" in result

    def test_generic_justification_temporary(self):
        line = "x  # guardian: allow-broad-exception -- temporary"
        result = _check_justification_quality(line)
        assert result is not None
        assert "temporary" in result

    def test_hyphenated_word_in_justification_not_separator(self):
        """A hyphen within a word in justification must not be treated as separator."""
        line = "x  # guardian: allow-broad-exception -- catches non-fatal errors only"
        assert _check_justification_quality(line) is None

    def test_no_guardian_on_line(self):
        assert _check_justification_quality("x = 1") is None

    def test_justification_too_short(self):
        line = "x  # guardian: allow-broad-exception -- ok"
        result = _check_justification_quality(line)
        assert result is not None
        assert "Missing justification" in result


# ---------------------------------------------------------------------------
# scan_file
# ---------------------------------------------------------------------------


class TestScanFile:
    def test_clean_file_returns_empty(self, tmp_path):
        f = tmp_path / "clean.py"
        f.write_text("x = 1\ny = 2\n", encoding="utf-8")
        logging.info("C3 write receipt: tests/unit/tools/guardian/test_idempotency_check.py write side effect recorded")
        issues = scan_file(f)
        assert issues == []

    def test_duplicate_guardian_detected(self, tmp_path):
        f = tmp_path / "dup.py"
        f.write_text(
            "x  # guardian: allow-broad-exception -- r1  # guardian: allow-bare-except -- r2\n",
            encoding="utf-8",
        )
        issues = scan_file(f)
        assert len(issues) == 1
        assert "DUPLICATE" in issues[0]["issue"]
        assert issues[0]["line_no"] == 1

    def test_weak_justification_detected(self, tmp_path):
        f = tmp_path / "weak.py"
        f.write_text("x  # guardian: allow-broad-exception -- needed\n", encoding="utf-8")
        issues = scan_file(f)
        assert len(issues) == 1
        assert "WEAK_JUSTIFICATION" in issues[0]["issue"]

    def test_missing_file_returns_empty(self, tmp_path):
        missing = tmp_path / "nonexistent.py"
        issues = scan_file(missing)
        assert issues == []

    def test_good_guardian_returns_empty(self, tmp_path):
        f = tmp_path / "good.py"
        f.write_text(
            "x  # guardian: allow-broad-exception -- only catches OSError from disk flush\n",
            encoding="utf-8",
        )
        issues = scan_file(f)
        assert issues == []


# ---------------------------------------------------------------------------
# scan_new_string
# ---------------------------------------------------------------------------


class TestScanNewString:
    def test_clean_string_returns_empty(self):
        assert scan_new_string("x = 1\ny = 2\n") == []

    def test_duplicate_on_same_line_detected(self):
        s = "x  # guardian: allow-broad-exception -- r1  # guardian: allow-bare-except -- r2\n"
        violations = scan_new_string(s)
        assert len(violations) >= 1

    def test_missing_justification_detected(self):
        s = "x  # guardian: allow-broad-exception\n"
        violations = scan_new_string(s)
        assert len(violations) == 1
        assert "Missing justification" in violations[0]

    def test_existing_content_duplicate_tag_flagged(self):
        """G1 fix: re-adding an existing guardian tag must be flagged."""
        existing = "y  # guardian: allow-broad-exception -- reason already in file\n"
        new = "z  # guardian: allow-broad-exception -- another reason\n"
        violations = scan_new_string(new, existing_content=existing)
        assert len(violations) >= 1
        assert "already exists in file" in violations[0]

    def test_different_tag_in_existing_not_flagged(self):
        """Different guardian type in existing content must not block new distinct type."""
        existing = "y  # guardian: allow-broad-exception -- reason\n"
        new = "z  # guardian: allow-bare-except -- different reason here\n"
        violations = scan_new_string(new, existing_content=existing)
        assert violations == []

    def test_no_existing_content_skips_duplicate_check(self):
        new = "z  # guardian: allow-broad-exception -- some reason here\n"
        violations = scan_new_string(new, existing_content=None)
        assert violations == []


# ---------------------------------------------------------------------------
# scan_paths
# ---------------------------------------------------------------------------


class TestScanPaths:
    def test_directory_scan_finds_issues(self, tmp_path):
        f = tmp_path / "sub" / "bad.py"
        f.parent.mkdir()
        f.write_text("x  # guardian: allow-broad-exception -- needed\n", encoding="utf-8")
        issues = scan_paths([tmp_path])
        assert len(issues) == 1

    def test_excludes_pycache(self, tmp_path):
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        f = pycache / "cached.py"
        f.write_text("x  # guardian: allow-broad-exception\n", encoding="utf-8")
        issues = scan_paths([tmp_path])
        assert issues == []

    def test_non_python_files_ignored(self, tmp_path):
        f = tmp_path / "config.yaml"
        f.write_text("# guardian: allow-broad-exception\n", encoding="utf-8")
        issues = scan_paths([tmp_path])
        assert issues == []

    def test_empty_dir_returns_empty(self, tmp_path):
        assert scan_paths([tmp_path]) == []

    def test_nonexistent_path_returns_empty(self, tmp_path):
        missing = tmp_path / "nosuchdir"
        issues = scan_paths([missing])
        assert issues == []
