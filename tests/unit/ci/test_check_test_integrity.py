"""Tests for Gate B: check_test_integrity.py AST scanner."""

from __future__ import annotations

import textwrap
from pathlib import Path


def _write_temp_test(tmp_path: Path, content: str) -> Path:
    f = tmp_path / "test_sample.py"
    f.write_text(textwrap.dedent(content), encoding="utf-8")
    return f


class TestCheckTestIntegritySilentSwallower:
    def test_no_violations_on_clean_test(self, tmp_path):
        from ops_scripts.ci.check_test_integrity import scan_file

        f = _write_temp_test(
            tmp_path,
            """
            def test_something():
                assert 1 + 1 == 2
        """,
        )
        assert scan_file(f) == []

    def test_flags_assertion_less_test(self, tmp_path):
        from ops_scripts.ci.check_test_integrity import scan_file

        f = _write_temp_test(
            tmp_path,
            """
            def test_no_asserts():
                x = 1 + 1
        """,
        )
        violations = scan_file(f)
        assert any("zero assert" in v[1] for v in violations)

    def test_flags_xfail_without_strict(self, tmp_path):
        from ops_scripts.ci.check_test_integrity import scan_file

        f = _write_temp_test(
            tmp_path,
            """
            import pytest

            @pytest.mark.xfail
            def test_xfail_no_strict():
                assert False
        """,
        )
        violations = scan_file(f)
        assert any("strict=True" in v[1] for v in violations)

    def test_xfail_with_strict_passes(self, tmp_path):
        from ops_scripts.ci.check_test_integrity import scan_file

        f = _write_temp_test(
            tmp_path,
            """
            import pytest

            @pytest.mark.xfail(strict=True, reason="linked_issue: #42")
            def test_xfail_strict():
                assert False
        """,
        )
        violations = scan_file(f)
        xfail_violations = [v for v in violations if "strict" in v[1]]
        assert xfail_violations == []


class TestCheckTestIntegrityMain:
    def test_main_returns_0_on_clean_dir(self, tmp_path):
        from ops_scripts.ci.check_test_integrity import main

        clean_test = tmp_path / "test_clean.py"
        clean_test.write_text("def test_ok():\n    assert True\n", encoding="utf-8")
        result = main([str(tmp_path)])
        assert result == 0

    def test_main_returns_1_on_violations(self, tmp_path):
        from ops_scripts.ci.check_test_integrity import main

        bad_test = tmp_path / "test_bad.py"
        bad_test.write_text("def test_noop():\n    pass\n", encoding="utf-8")
        result = main([str(tmp_path)])
        assert result == 1
