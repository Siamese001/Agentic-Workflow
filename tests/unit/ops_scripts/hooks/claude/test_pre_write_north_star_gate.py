"""Unit tests for pre_write_north_star_gate.py — the north-star relevance PreToolUse gate.

The pure ``evaluate(data, state, env)`` decision function is exercised in isolation with an
explicit state dict and env, so the tests are deterministic and need no live state file.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[5]
_GATE_PATH = _REPO_ROOT / ".claude" / "hooks" / "pre_write_north_star_gate.py"


def _load_gate():
    spec = importlib.util.spec_from_file_location("pre_write_north_star_gate", _GATE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = _load_gate()

_STATE = {"lanes_passing": 1, "lanes_total": 11, "recent_north_star_pct": 18, "enabled": True}
_NO_BYPASS = {"NORTH_STAR_GATE_ENFORCE": "ask"}


def _edit(path: str) -> dict:
    return {"tool_name": "Write", "tool_input": {"file_path": path}}


# ---- allow paths -------------------------------------------------------------------

def test_non_edit_tool_allowed():
    code, _ = gate.evaluate({"tool_name": "Read", "tool_input": {"file_path": ".claude/rules/x.md"}},
                            state=_STATE, env=_NO_BYPASS)
    assert code == 0


def test_north_star_path_allowed():
    code, _ = gate.evaluate(_edit("apps_rg/engines/ibm_bullets.py"), state=_STATE, env=_NO_BYPASS)
    assert code == 0


def test_north_star_test_path_allowed():
    code, _ = gate.evaluate(_edit("tests/unit/apps_rg/test_lane.py"), state=_STATE, env=_NO_BYPASS)
    assert code == 0


def test_neutral_core_path_allowed():
    # agentic_core spine work is NOT intercepted (conservative — avoid over-blocking)
    code, _ = gate.evaluate(_edit("agentic_core/L2_execution/foo.py"), state=_STATE, env=_NO_BYPASS)
    assert code == 0


def test_parking_lot_always_allowed():
    # capture must never be blocked
    code, _ = gate.evaluate(_edit("PARKING_LOT.md"), state=_STATE, env=_NO_BYPASS)
    assert code == 0


def test_gate_own_state_allowed():
    code, _ = gate.evaluate(_edit("config/north_star_state.json"), state=_STATE, env=_NO_BYPASS)
    assert code == 0


# ---- block paths -------------------------------------------------------------------

def test_off_star_rules_blocked():
    code, reason = gate.evaluate(_edit(".claude/rules/new_rule.md"), state=_STATE, env=_NO_BYPASS)
    assert code == 2
    assert "AskUserQuestion" in reason
    assert "RECOMMENDED" in reason


def test_off_star_ci_gate_blocked():
    code, reason = gate.evaluate(_edit("ops_scripts/ci/check_new_thing.py"), state=_STATE, env=_NO_BYPASS)
    assert code == 2
    assert "Park it" in reason


def test_off_star_plans_blocked():
    code, reason = gate.evaluate(_edit("plans/some-new-plan-a1b2c3.md"), state=_STATE, env=_NO_BYPASS)
    assert code == 2


# ---- earned confidence -------------------------------------------------------------

def test_confidence_earned_from_base_rate():
    park, dop = gate._confidence({"recent_north_star_pct": 18})
    assert dop == 0.18
    assert park == 0.82


def test_confidence_floor_keeps_recommendation_confident():
    # even a 'good' 40% base-rate keeps park >= 0.70 floor so it always reads as the default
    park, _ = gate._confidence({"recent_north_star_pct": 40})
    assert park >= 0.70


def test_block_message_shows_earned_confidence():
    code, reason = gate.evaluate(_edit(".claude/hooks/new_hook.py"), state=_STATE, env=_NO_BYPASS)
    assert code == 2
    assert "confidence=0.82" in reason
    assert "confidence=0.18" in reason


# ---- auto-disable + toggles --------------------------------------------------------

def test_auto_disabled_when_shipped():
    shipped = {"lanes_passing": 11, "lanes_total": 11, "recent_north_star_pct": 18, "enabled": True}
    code, _ = gate.evaluate(_edit(".claude/rules/x.md"), state=shipped, env=_NO_BYPASS)
    assert code == 0


def test_disabled_state_allows():
    off = {"lanes_passing": 1, "lanes_total": 11, "enabled": False}
    code, _ = gate.evaluate(_edit(".claude/rules/x.md"), state=off, env=_NO_BYPASS)
    assert code == 0


def test_empty_state_failsoft_allows():
    code, _ = gate.evaluate(_edit(".claude/rules/x.md"), state={}, env=_NO_BYPASS)
    assert code == 0


def test_bypass_env_allows():
    code, _ = gate.evaluate(_edit(".claude/rules/x.md"), state=_STATE, env={"NORTH_STAR_GATE_BYPASS": "1"})
    assert code == 0


def test_mode_off_allows():
    code, _ = gate.evaluate(_edit(".claude/rules/x.md"), state=_STATE, env={"NORTH_STAR_GATE_ENFORCE": "off"})
    assert code == 0


def test_mode_warn_does_not_block_but_warns():
    code, reason = gate.evaluate(_edit(".claude/rules/x.md"), state=_STATE, env={"NORTH_STAR_GATE_ENFORCE": "warn"})
    assert code == 0
    assert reason.startswith("WARN:")
