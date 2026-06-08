"""
Tests for pre_user_prompt_deferred_plan_gate.py

Covers:
- Plan with DO_NOT_IMPLEMENT_GUARD: marker → DEFERRED_PLAN_BLOCKED: emitted
- Plan with only prose guard (no marker) → DEFERRED_PLAN_PROSE_GUARD: emitted
- Plan with no guard at all → no output
- reason= field extraction from marker
- bypass env var silences all output
- _scan_plans skips archive-prefix (_) files
- multiple guarded plans → multiple lines
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_PATH = REPO_ROOT / ".claude" / "governance/scripts" / "pre_user_prompt_deferred_plan_gate.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("deferred_plan_gate", HOOK_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def mod():
    return _load_module()


# ---------------------------------------------------------------------------
# _extract_guard_reason
# ---------------------------------------------------------------------------

class TestExtractGuardReason:
    def test_reason_field_extracted(self, mod):
        text = "DO_NOT_IMPLEMENT_GUARD: plan=my-plan-abc123 reason=needs Author-Gate"
        assert mod._extract_guard_reason(text) == "needs Author-Gate"

    def test_body_returned_when_no_reason_field(self, mod):
        text = "DO_NOT_IMPLEMENT_GUARD: plan=my-plan-abc123 requires gate"
        result = mod._extract_guard_reason(text)
        assert result is not None
        assert len(result) > 0

    def test_none_when_no_marker(self, mod):
        text = "This plan should not be implemented without Author-Gate decision."
        assert mod._extract_guard_reason(text) is None

    def test_leading_whitespace_ok(self, mod):
        text = "  DO_NOT_IMPLEMENT_GUARD: plan=x-abc123 reason=blocked"
        assert mod._extract_guard_reason(text) == "blocked"

    def test_reason_capped_at_120_chars(self, mod):
        long_reason = "x" * 200
        text = f"DO_NOT_IMPLEMENT_GUARD: plan=p reason={long_reason}"
        result = mod._extract_guard_reason(text)
        assert result is not None
        assert len(result) <= 120


# ---------------------------------------------------------------------------
# _has_prose_guard
# ---------------------------------------------------------------------------

class TestHasProseGuard:
    def test_nothing_here_should_be_implemented_without(self, mod):
        text = "Nothing here should be implemented without a separate Author-Gate."
        assert mod._has_prose_guard(text) is True

    def test_do_not_implement_without(self, mod):
        text = "Do not implement without Author-Gate decision."
        assert mod._has_prose_guard(text) is True

    def test_case_insensitive(self, mod):
        text = "DO NOT IMPLEMENT WITHOUT a gate"
        assert mod._has_prose_guard(text) is True

    def test_no_prose_guard(self, mod):
        text = "This is a normal plan with no restrictions."
        assert mod._has_prose_guard(text) is False

    def test_should_not_be_implemented_without(self, mod):
        text = "This should not be implemented without explicit approval."
        assert mod._has_prose_guard(text) is True

    def test_must_not_be_implemented_without(self, mod):
        text = "must not be implemented without Author-Gate"
        assert mod._has_prose_guard(text) is True


# ---------------------------------------------------------------------------
# _scan_plans (using tmp_path for isolation)
# ---------------------------------------------------------------------------

class TestScanPlans:
    def _write_plan(self, plans_dir: Path, name: str, content: str) -> Path:
        p = plans_dir / name
        p.write_text(content, encoding="utf-8")
        return p

    def test_marker_plan_returned_as_blocked(self, mod, tmp_path, monkeypatch):
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        self._write_plan(
            plans_dir, "my-deferred-abc123.md",
            "DO_NOT_IMPLEMENT_GUARD: plan=my-deferred-abc123 reason=gate required\n"
        )
        monkeypatch.setattr(mod, "PLANS_DIR", plans_dir)
        results = mod._scan_plans()
        assert len(results) == 1
        slug, reason, has_marker = results[0]
        assert slug == "my-deferred-abc123"
        assert "gate required" in reason
        assert has_marker is True

    def test_prose_only_plan_returned_without_marker(self, mod, tmp_path, monkeypatch):
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        self._write_plan(
            plans_dir, "prose-plan-def456.md",
            "Nothing here should be implemented without a separate Author-Gate.\n"
        )
        monkeypatch.setattr(mod, "PLANS_DIR", plans_dir)
        results = mod._scan_plans()
        assert len(results) == 1
        slug, reason, has_marker = results[0]
        assert slug == "prose-plan-def456"
        assert has_marker is False

    def test_normal_plan_not_returned(self, mod, tmp_path, monkeypatch):
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        self._write_plan(
            plans_dir, "normal-plan-aaa111.md",
            "# Normal Plan\nThis plan implements feature X.\n"
        )
        monkeypatch.setattr(mod, "PLANS_DIR", plans_dir)
        results = mod._scan_plans()
        assert results == []

    def test_archive_prefix_files_skipped(self, mod, tmp_path, monkeypatch):
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        self._write_plan(
            plans_dir, "_archive-plan-bbb222.md",
            "DO_NOT_IMPLEMENT_GUARD: plan=_archive-plan-bbb222 reason=archived\n"
        )
        monkeypatch.setattr(mod, "PLANS_DIR", plans_dir)
        results = mod._scan_plans()
        assert results == []

    def test_multiple_guarded_plans(self, mod, tmp_path, monkeypatch):
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        self._write_plan(
            plans_dir, "plan-a-aaa111.md",
            "DO_NOT_IMPLEMENT_GUARD: plan=plan-a-aaa111 reason=gate A\n"
        )
        self._write_plan(
            plans_dir, "plan-b-bbb222.md",
            "Nothing here should be implemented without Author-Gate.\n"
        )
        monkeypatch.setattr(mod, "PLANS_DIR", plans_dir)
        results = mod._scan_plans()
        assert len(results) == 2

    def test_missing_plans_dir_returns_empty(self, mod, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "PLANS_DIR", tmp_path / "nonexistent")
        assert mod._scan_plans() == []


# ---------------------------------------------------------------------------
# main() output
# ---------------------------------------------------------------------------

class TestMain:
    def test_blocked_plan_emits_deferred_plan_blocked(self, mod, tmp_path, monkeypatch, capsys):
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        (plans_dir / "guarded-ccc333.md").write_text(
            "DO_NOT_IMPLEMENT_GUARD: plan=guarded-ccc333 reason=gate required\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(mod, "PLANS_DIR", plans_dir)
        monkeypatch.delenv("DEFERRED_PLAN_GATE_BYPASS", raising=False)
        rc = mod.main()
        assert rc == 0
        out = capsys.readouterr().out
        assert "DEFERRED_PLAN_BLOCKED:" in out
        assert "guarded-ccc333" in out

    def test_prose_only_plan_emits_prose_guard(self, mod, tmp_path, monkeypatch, capsys):
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        (plans_dir / "prose-ddd444.md").write_text(
            "Nothing here should be implemented without Author-Gate.\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(mod, "PLANS_DIR", plans_dir)
        monkeypatch.delenv("DEFERRED_PLAN_GATE_BYPASS", raising=False)
        rc = mod.main()
        assert rc == 0
        out = capsys.readouterr().out
        assert "DEFERRED_PLAN_PROSE_GUARD:" in out
        assert "prose-ddd444" in out

    def test_no_guarded_plans_no_output(self, mod, tmp_path, monkeypatch, capsys):
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        (plans_dir / "clean-eee555.md").write_text("# Normal Plan\n", encoding="utf-8")
        monkeypatch.setattr(mod, "PLANS_DIR", plans_dir)
        monkeypatch.delenv("DEFERRED_PLAN_GATE_BYPASS", raising=False)
        rc = mod.main()
        assert rc == 0
        out = capsys.readouterr().out
        assert out.strip() == ""

    def test_bypass_env_suppresses_output(self, mod, tmp_path, monkeypatch, capsys):
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        (plans_dir / "guarded-fff666.md").write_text(
            "DO_NOT_IMPLEMENT_GUARD: plan=guarded-fff666 reason=blocked\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(mod, "PLANS_DIR", plans_dir)
        monkeypatch.setenv("DEFERRED_PLAN_GATE_BYPASS", "1")
        rc = mod.main()
        assert rc == 0
        out = capsys.readouterr().out
        assert out.strip() == ""

    def test_empty_plans_dir_no_output(self, mod, tmp_path, monkeypatch, capsys):
        plans_dir = tmp_path / "plans"
        plans_dir.mkdir()
        monkeypatch.setattr(mod, "PLANS_DIR", plans_dir)
        monkeypatch.delenv("DEFERRED_PLAN_GATE_BYPASS", raising=False)
        rc = mod.main()
        assert rc == 0
        assert capsys.readouterr().out.strip() == ""
