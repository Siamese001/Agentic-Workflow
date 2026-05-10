"""
Tests for ops_scripts/ci/check_deferred_plan_guard_markers.py

Covers:
- Plan with prose guard + marker → compliant (exit 0)
- Plan with prose guard but no marker → violation (exit 1)
- Plan with no prose guard → compliant (exit 0)
- Bypass env var → exit 0 always
- Multiple plans: all compliant → exit 0
- Multiple plans: one violation → exit 1
- _count_prose_guards excludes quoted mentions
- _has_marker detects the marker line
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_deferred_plan_guard_markers.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_deferred_plan_guard_markers", GATE_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def mod():
    return _load_module()


# ---------------------------------------------------------------------------
# _count_prose_guards
# ---------------------------------------------------------------------------

class TestCountProseGuards:
    def test_nothing_here_should_be_implemented_without(self, mod):
        text = "Nothing here should be implemented without a separate Author-Gate decision."
        assert mod._count_prose_guards(text) == 1

    def test_do_not_implement_without(self, mod):
        text = "Do not implement without Author-Gate."
        assert mod._count_prose_guards(text) == 1

    def test_must_not_be_implemented_without(self, mod):
        text = "must not be implemented without explicit approval"
        assert mod._count_prose_guards(text) == 1

    def test_should_not_be_implemented_without(self, mod):
        text = "should not be implemented without gate"
        assert mod._count_prose_guards(text) == 1

    def test_case_insensitive(self, mod):
        text = "DO NOT IMPLEMENT WITHOUT author gate"
        assert mod._count_prose_guards(text) == 1

    def test_quoted_mention_excluded(self, mod):
        text = '"do not implement without" is an example phrase'
        assert mod._count_prose_guards(text) == 0

    def test_backtick_mention_excluded(self, mod):
        text = "`do not implement without` marker required"
        assert mod._count_prose_guards(text) == 0

    def test_no_guard_prose(self, mod):
        text = "This plan implements X and Y. Proceed normally."
        assert mod._count_prose_guards(text) == 0

    def test_multiple_occurrences(self, mod):
        text = (
            "Do not implement without Author-Gate.\n"
            "Also, nothing here should be implemented without a decision.\n"
        )
        assert mod._count_prose_guards(text) == 2


# ---------------------------------------------------------------------------
# _has_marker
# ---------------------------------------------------------------------------

class TestHasMarker:
    def test_marker_present(self, mod):
        text = "DO_NOT_IMPLEMENT_GUARD: plan=x reason=blocked"
        assert mod._has_marker(text) is True

    def test_marker_with_leading_whitespace(self, mod):
        text = "  DO_NOT_IMPLEMENT_GUARD: plan=x reason=blocked"
        assert mod._has_marker(text) is True

    def test_no_marker(self, mod):
        text = "Nothing here should be implemented without a gate."
        assert mod._has_marker(text) is False

    def test_partial_marker_not_matched(self, mod):
        text = "DO_NOT_IMPLEMENT some other text"
        assert mod._has_marker(text) is False


# ---------------------------------------------------------------------------
# _check_one
# ---------------------------------------------------------------------------

class TestCheckOne:
    def _write(self, tmp_path: Path, name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_prose_guard_with_marker_compliant(self, mod, tmp_path):
        p = self._write(
            tmp_path, "plan.md",
            "Do not implement without Author-Gate.\n"
            "DO_NOT_IMPLEMENT_GUARD: plan=x reason=blocked\n"
        )
        ok, prose, marker = mod._check_one(p)
        assert ok is True
        assert prose >= 1
        assert marker is True

    def test_prose_guard_without_marker_violation(self, mod, tmp_path):
        p = self._write(
            tmp_path, "plan.md",
            "Nothing here should be implemented without a separate Author-Gate.\n"
        )
        ok, prose, marker = mod._check_one(p)
        assert ok is False
        assert prose >= 1
        assert marker is False

    def test_no_prose_no_marker_compliant(self, mod, tmp_path):
        p = self._write(tmp_path, "plan.md", "# Normal Plan\nImplement X.\n")
        ok, prose, marker = mod._check_one(p)
        assert ok is True
        assert prose == 0

    def test_missing_file_treated_as_compliant(self, mod, tmp_path):
        ok, prose, marker = mod._check_one(tmp_path / "nonexistent.md")
        assert ok is True


# ---------------------------------------------------------------------------
# main() via subprocess (real exit codes)
# ---------------------------------------------------------------------------

class TestMainExitCodes:
    def _run(self, *args, env=None):
        cmd = [sys.executable, str(GATE_PATH)] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
            env=env,
        )
        return result

    def test_compliant_plan_exits_0(self, tmp_path):
        p = tmp_path / "ok-plan.md"
        p.write_text(
            "Do not implement without Author-Gate.\n"
            "DO_NOT_IMPLEMENT_GUARD: plan=ok-plan reason=blocked\n",
            encoding="utf-8",
        )
        result = self._run(str(p))
        assert result.returncode == 0

    def test_violating_plan_exits_1(self, tmp_path):
        p = tmp_path / "bad-plan.md"
        p.write_text(
            "Nothing here should be implemented without a separate Author-Gate.\n",
            encoding="utf-8",
        )
        result = self._run(str(p))
        assert result.returncode == 1
        assert "DO_NOT_IMPLEMENT_GUARD" in result.stderr

    def test_normal_plan_exits_0(self, tmp_path):
        p = tmp_path / "normal-plan.md"
        p.write_text("# Normal Plan\nImplement X.\n", encoding="utf-8")
        result = self._run(str(p))
        assert result.returncode == 0

    def test_bypass_exits_0_even_with_violation(self, tmp_path):
        p = tmp_path / "bad-bypass.md"
        p.write_text(
            "Nothing here should be implemented without Author-Gate.\n",
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["DEFERRED_PLAN_GUARD_BYPASS"] = "1"
        result = self._run(str(p), env=env)
        assert result.returncode == 0

    def test_multiple_paths_one_violation_exits_1(self, tmp_path):
        ok = tmp_path / "ok.md"
        ok.write_text(
            "Do not implement without gate.\n"
            "DO_NOT_IMPLEMENT_GUARD: plan=ok reason=blocked\n",
            encoding="utf-8",
        )
        bad = tmp_path / "bad.md"
        bad.write_text(
            "Nothing here should be implemented without a separate Author-Gate.\n",
            encoding="utf-8",
        )
        result = self._run(str(ok), str(bad))
        assert result.returncode == 1

    def test_multiple_paths_all_compliant_exits_0(self, tmp_path):
        for i in range(3):
            p = tmp_path / f"plan{i}.md"
            p.write_text("# Normal Plan\n", encoding="utf-8")
        paths = [str(tmp_path / f"plan{i}.md") for i in range(3)]
        result = self._run(*paths)
        assert result.returncode == 0

    def test_remediation_message_in_stderr(self, tmp_path):
        p = tmp_path / "needs-marker.md"
        p.write_text(
            "Do not implement without Author-Gate.\n",
            encoding="utf-8",
        )
        result = self._run(str(p))
        assert result.returncode == 1
        assert "Remediation" in result.stderr
        assert "DO_NOT_IMPLEMENT_GUARD" in result.stderr
