"""
Tests for ops_scripts/ci/check_ag_hook_wiring.py

Verifies all four invariants:
  AG-WIRE-1: pre_user_prompt reminder hook present + visible
  AG-WIRE-2: miss_detector present + visible
  AG-WIRE-3: ui_audit present + visible
  AG-WIRE-4: ask_packet_audit present + visible

Also covers: no AG hooks present (skip), bypass env, fail-closed mode,
main() exit codes, report writing.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
GATE_PATH = REPO_ROOT / "ops_scripts" / "ci" / "check_ag_hook_wiring.py"


def _load_module() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("check_ag_hook_wiring", GATE_PATH)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


@pytest.fixture()
def mod():
    return _load_module()


# ---------------------------------------------------------------------------
# Helpers to build minimal hooks.json data structures
# ---------------------------------------------------------------------------

def _make_hooks(
    post_cascade: list[dict] | None = None,
    pre_prompt: list[dict] | None = None,
) -> dict:
    return {
        "hooks": {
            "post_cursor_agent_response": post_cascade or [],
            "pre_user_prompt": pre_prompt or [],
        }
    }


def _hook(script: str, show_output: bool = True) -> dict:
    return {
        "command": f"python .windsurf/scripts/{script}",
        "working_directory": "C:\\Git\\Agentic-Workflow-FRESH",
        "show_output": show_output,
    }


def _full_valid_hooks() -> dict:
    """A fully compliant hooks structure — all 4 invariants satisfied."""
    return _make_hooks(
        post_cascade=[
            _hook("post_cursor_agent_heartbeat.py"),
            _hook("post_cursor_agent_author_gate_miss_detector.py", show_output=True),
            _hook("post_cursor_agent_author_gate_ui_audit.py", show_output=True),
            _hook("post_cursor_agent_ask_user_question_packet_audit.py", show_output=True),
        ],
        pre_prompt=[
            _hook("pre_prompt_classifier.py"),
            _hook("pre_user_prompt_author_gate_reminder.py", show_output=True),
        ],
    )


# ---------------------------------------------------------------------------
# AG-WIRE-1: pre_user_prompt reminder hook
# ---------------------------------------------------------------------------

class TestWire1ReminderHook:
    def test_pass_when_reminder_present_and_visible(self, mod):
        hooks = _full_valid_hooks()
        violations = mod.evaluate(hooks)
        wire1 = [v for v in violations if v["invariant"] == "AG-WIRE-1"]
        assert wire1 == []

    def test_fail_when_reminder_absent(self, mod):
        hooks = _make_hooks(
            post_cascade=[_hook("post_cursor_agent_author_gate_miss_detector.py")],
            pre_prompt=[_hook("pre_prompt_classifier.py")],
        )
        violations = mod.evaluate(hooks)
        wire1 = [v for v in violations if v["invariant"] == "AG-WIRE-1"]
        assert len(wire1) == 1
        assert "missing" in wire1[0]["message"].lower() or "does not contain" in wire1[0]["message"].lower()

    def test_fail_when_reminder_show_output_false(self, mod):
        hooks = _make_hooks(
            post_cascade=[_hook("post_cursor_agent_author_gate_miss_detector.py")],
            pre_prompt=[
                _hook("pre_user_prompt_author_gate_reminder.py", show_output=False),
            ],
        )
        violations = mod.evaluate(hooks)
        wire1 = [v for v in violations if v["invariant"] == "AG-WIRE-1"]
        assert len(wire1) == 1
        assert "show_output" in wire1[0]["message"]


# ---------------------------------------------------------------------------
# AG-WIRE-2: miss detector
# ---------------------------------------------------------------------------

class TestWire2MissDetector:
    def test_pass_when_present_and_visible(self, mod):
        hooks = _full_valid_hooks()
        violations = mod.evaluate(hooks)
        assert not any(v["invariant"] == "AG-WIRE-2" for v in violations)

    def test_fail_when_absent(self, mod):
        hooks = _make_hooks(
            post_cascade=[
                _hook("post_cursor_agent_author_gate_ui_audit.py"),
                _hook("post_cursor_agent_ask_user_question_packet_audit.py"),
            ],
            pre_prompt=[_hook("pre_user_prompt_author_gate_reminder.py")],
        )
        violations = mod.evaluate(hooks)
        assert any(v["invariant"] == "AG-WIRE-2" for v in violations)

    def test_fail_when_show_output_false(self, mod):
        hooks = _make_hooks(
            post_cascade=[
                _hook("post_cursor_agent_author_gate_miss_detector.py", show_output=False),
                _hook("post_cursor_agent_author_gate_ui_audit.py"),
                _hook("post_cursor_agent_ask_user_question_packet_audit.py"),
            ],
            pre_prompt=[_hook("pre_user_prompt_author_gate_reminder.py")],
        )
        violations = mod.evaluate(hooks)
        wire2 = [v for v in violations if v["invariant"] == "AG-WIRE-2"]
        assert len(wire2) == 1
        assert "show_output" in wire2[0]["message"]


# ---------------------------------------------------------------------------
# AG-WIRE-3: UI audit hook
# ---------------------------------------------------------------------------

class TestWire3UiAudit:
    def test_pass_when_present_and_visible(self, mod):
        hooks = _full_valid_hooks()
        assert not any(v["invariant"] == "AG-WIRE-3" for v in mod.evaluate(hooks))

    def test_fail_when_absent(self, mod):
        hooks = _make_hooks(
            post_cascade=[
                _hook("post_cursor_agent_author_gate_miss_detector.py"),
                _hook("post_cursor_agent_ask_user_question_packet_audit.py"),
            ],
            pre_prompt=[_hook("pre_user_prompt_author_gate_reminder.py")],
        )
        assert any(v["invariant"] == "AG-WIRE-3" for v in mod.evaluate(hooks))

    def test_fail_when_show_output_false(self, mod):
        hooks = _make_hooks(
            post_cascade=[
                _hook("post_cursor_agent_author_gate_miss_detector.py"),
                _hook("post_cursor_agent_author_gate_ui_audit.py", show_output=False),
                _hook("post_cursor_agent_ask_user_question_packet_audit.py"),
            ],
            pre_prompt=[_hook("pre_user_prompt_author_gate_reminder.py")],
        )
        violations = mod.evaluate(hooks)
        wire3 = [v for v in violations if v["invariant"] == "AG-WIRE-3"]
        assert len(wire3) == 1


# ---------------------------------------------------------------------------
# AG-WIRE-4: ask-packet audit hook
# ---------------------------------------------------------------------------

class TestWire4AskPacketAudit:
    def test_pass_when_present_and_visible(self, mod):
        hooks = _full_valid_hooks()
        assert not any(v["invariant"] == "AG-WIRE-4" for v in mod.evaluate(hooks))

    def test_fail_when_absent(self, mod):
        hooks = _make_hooks(
            post_cascade=[
                _hook("post_cursor_agent_author_gate_miss_detector.py"),
                _hook("post_cursor_agent_author_gate_ui_audit.py"),
            ],
            pre_prompt=[_hook("pre_user_prompt_author_gate_reminder.py")],
        )
        assert any(v["invariant"] == "AG-WIRE-4" for v in mod.evaluate(hooks))

    def test_fail_when_show_output_false(self, mod):
        hooks = _make_hooks(
            post_cascade=[
                _hook("post_cursor_agent_author_gate_miss_detector.py"),
                _hook("post_cursor_agent_author_gate_ui_audit.py"),
                _hook("post_cursor_agent_ask_user_question_packet_audit.py", show_output=False),
            ],
            pre_prompt=[_hook("pre_user_prompt_author_gate_reminder.py")],
        )
        violations = mod.evaluate(hooks)
        wire4 = [v for v in violations if v["invariant"] == "AG-WIRE-4"]
        assert len(wire4) == 1


# ---------------------------------------------------------------------------
# No-AG-hooks: skip all checks
# ---------------------------------------------------------------------------

class TestNoAgHooks:
    def test_no_violations_when_no_ag_hooks_present(self, mod):
        hooks = _make_hooks(
            post_cascade=[_hook("post_cursor_agent_heartbeat.py")],
            pre_prompt=[_hook("pre_prompt_classifier.py")],
        )
        assert mod.evaluate(hooks) == []

    def test_no_violations_when_post_cursor_agent_empty(self, mod):
        hooks = _make_hooks(post_cascade=[], pre_prompt=[])
        assert mod.evaluate(hooks) == []

    def test_no_violations_when_hooks_section_missing(self, mod):
        assert mod.evaluate({}) == []


# ---------------------------------------------------------------------------
# All-pass: real hooks.json structure
# ---------------------------------------------------------------------------

class TestRealHooksJson:
    def test_current_hooks_json_passes_all_invariants(self, mod):
        """The actual repo hooks.json should satisfy all invariants after the hardening commit."""
        hooks_path = REPO_ROOT / ".windsurf" / "hooks.json"
        if not hooks_path.exists():
            pytest.skip("hooks.json not found")
        hooks_data = json.loads(hooks_path.read_text(encoding="utf-8"))
        violations = mod.evaluate(hooks_data)
        assert violations == [], f"Real hooks.json has wiring violations: {violations}"


# ---------------------------------------------------------------------------
# Main integration: exit codes + bypass + fail-closed
# ---------------------------------------------------------------------------

class TestMainExitCodes:
    def test_exits_0_on_valid_hooks(self, mod, tmp_path):
        hooks_path = tmp_path / "hooks.json"
        hooks_path.write_text(json.dumps(_full_valid_hooks()), encoding="utf-8")
        with (
            patch.object(mod, "HOOKS_PATH", hooks_path),
            patch.object(mod, "VIOLATIONS_OUT", tmp_path / "out.json"),
        ):
            rc = mod.main()
        assert rc == 0

    def test_exits_0_advisory_on_violation(self, mod, tmp_path):
        bad_hooks = _make_hooks(
            post_cascade=[_hook("post_cursor_agent_author_gate_ui_audit.py")],
            pre_prompt=[],
        )
        hooks_path = tmp_path / "hooks.json"
        hooks_path.write_text(json.dumps(bad_hooks), encoding="utf-8")
        with (
            patch.object(mod, "HOOKS_PATH", hooks_path),
            patch.object(mod, "VIOLATIONS_OUT", tmp_path / "out.json"),
            patch.dict(os.environ, {}, clear=False),
        ):
            os.environ.pop(mod.FAIL_CLOSED_ENV, None)
            rc = mod.main()
        assert rc == 0

    def test_exits_1_fail_closed_on_violation(self, mod, tmp_path):
        bad_hooks = _make_hooks(
            post_cascade=[_hook("post_cursor_agent_author_gate_ui_audit.py")],
            pre_prompt=[],
        )
        hooks_path = tmp_path / "hooks.json"
        hooks_path.write_text(json.dumps(bad_hooks), encoding="utf-8")
        with (
            patch.object(mod, "HOOKS_PATH", hooks_path),
            patch.object(mod, "VIOLATIONS_OUT", tmp_path / "out.json"),
            patch.dict(os.environ, {mod.FAIL_CLOSED_ENV: "1"}),
        ):
            rc = mod.main()
        assert rc == 1

    def test_bypass_exits_0_and_skips_checks(self, mod, tmp_path):
        bad_hooks = _make_hooks(
            post_cascade=[_hook("post_cursor_agent_author_gate_ui_audit.py")],
            pre_prompt=[],
        )
        hooks_path = tmp_path / "hooks.json"
        hooks_path.write_text(json.dumps(bad_hooks), encoding="utf-8")
        with (
            patch.object(mod, "HOOKS_PATH", hooks_path),
            patch.object(mod, "VIOLATIONS_OUT", tmp_path / "out.json"),
            patch.dict(os.environ, {mod.BYPASS_ENV: "1"}),
        ):
            rc = mod.main()
        assert rc == 0

    def test_exits_2_when_hooks_json_missing(self, mod, tmp_path):
        missing = tmp_path / "no_such.json"
        with (
            patch.object(mod, "HOOKS_PATH", missing),
            patch.object(mod, "VIOLATIONS_OUT", tmp_path / "out.json"),
        ):
            rc = mod.main()
        assert rc == 2

    def test_report_written_on_pass(self, mod, tmp_path):
        hooks_path = tmp_path / "hooks.json"
        hooks_path.write_text(json.dumps(_full_valid_hooks()), encoding="utf-8")
        out = tmp_path / "out.json"
        with (
            patch.object(mod, "HOOKS_PATH", hooks_path),
            patch.object(mod, "VIOLATIONS_OUT", out),
        ):
            mod.main()
        assert out.exists()
        report = json.loads(out.read_text())
        assert report["total_violations"] == 0

    def test_report_written_on_violation(self, mod, tmp_path):
        bad_hooks = _make_hooks(
            post_cascade=[_hook("post_cursor_agent_author_gate_ui_audit.py", show_output=False)],
            pre_prompt=[],
        )
        hooks_path = tmp_path / "hooks.json"
        hooks_path.write_text(json.dumps(bad_hooks), encoding="utf-8")
        out = tmp_path / "out.json"
        with (
            patch.object(mod, "HOOKS_PATH", hooks_path),
            patch.object(mod, "VIOLATIONS_OUT", out),
        ):
            mod.main()
        report = json.loads(out.read_text())
        assert report["total_violations"] > 0
