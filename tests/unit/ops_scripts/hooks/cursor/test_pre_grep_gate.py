"""Unit tests for pre_grep_gate.py — the ADG-first Grep PreToolUse chokepoint.

Plan: grep-pretooluse-adg-gate-a3f1c7. The decision function ``evaluate`` is exercised in
isolation with the ADG-health probe and the deps-intent breadcrumb monkeypatched, so the
tests are deterministic and need no live ADG snapshot.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[5]
_GATE_PATH = _REPO_ROOT / ".claude" / "governance" / "scripts" / "pre_grep_gate.py"


def _load_gate():
    spec = importlib.util.spec_from_file_location("pre_grep_gate", _GATE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = _load_gate()


def _grep(pattern: str) -> dict:
    return {"tool_name": "Grep", "tool_input": {"pattern": pattern}}


@pytest.fixture
def healthy(monkeypatch):
    monkeypatch.setattr(gate, "_adg_healthy", lambda: True)
    monkeypatch.delenv(gate._BYPASS_ENV, raising=False)
    return monkeypatch


# --------------------------------------------------------------------------------------
# allow paths
# --------------------------------------------------------------------------------------

def test_non_grep_tool_allowed(healthy):
    code, _ = gate.evaluate({"tool_name": "Read", "tool_input": {"file_path": "x"}})
    assert code == 0


def test_bypass_env_allows(monkeypatch):
    monkeypatch.setattr(gate, "_adg_healthy", lambda: True)
    monkeypatch.setattr(gate, "_breadcrumb_fresh", lambda: True)
    monkeypatch.setenv(gate._BYPASS_ENV, "1")
    code, reason = gate.evaluate(_grep("FooAgent"))
    assert code == 0
    assert gate._BYPASS_ENV in reason


def test_adg_unhealthy_fails_open_with_marker(monkeypatch):
    monkeypatch.setattr(gate, "_adg_healthy", lambda: False)
    monkeypatch.setattr(gate, "_breadcrumb_fresh", lambda: True)
    monkeypatch.delenv(gate._BYPASS_ENV, raising=False)
    code, reason = gate.evaluate(_grep("import agentic_core"))
    assert code == 0
    assert reason.startswith("DEGRADED_FALLBACK:")


def test_literal_todo_allowed_even_with_breadcrumb(healthy):
    healthy.setattr(gate, "_breadcrumb_fresh", lambda: True)
    code, reason = gate.evaluate(_grep("TODO: refactor this"))
    assert code == 0
    assert "literal" in reason


def test_empty_pattern_allowed(healthy):
    healthy.setattr(gate, "_breadcrumb_fresh", lambda: True)
    code, _ = gate.evaluate({"tool_name": "Grep", "tool_input": {}})
    assert code == 0


def test_structural_pattern_without_breadcrumb_warns_but_allows(healthy):
    healthy.setattr(gate, "_breadcrumb_fresh", lambda: False)
    code, reason = gate.evaluate(_grep("from agentic_core.x import y"))
    assert code == 0
    assert reason.startswith("WARN")


def test_ambiguous_pattern_without_breadcrumb_allowed(healthy):
    healthy.setattr(gate, "_breadcrumb_fresh", lambda: False)
    code, reason = gate.evaluate(_grep("some_value"))
    assert code == 0
    assert "no deps-intent" in reason


# --------------------------------------------------------------------------------------
# block path
# --------------------------------------------------------------------------------------

def test_breadcrumb_plus_nonliteral_blocks(healthy):
    healthy.setattr(gate, "_breadcrumb_fresh", lambda: True)
    code, reason = gate.evaluate(_grep("PaymentAgent"))
    assert code == 2
    assert "ADG-FIRST" in reason
    assert "adg_edge_fanin" in reason


def test_breadcrumb_plus_import_blocks(healthy):
    healthy.setattr(gate, "_breadcrumb_fresh", lambda: True)
    code, _ = gate.evaluate(_grep("import agentic_core.L2_execution"))
    assert code == 2


# --------------------------------------------------------------------------------------
# helper-level checks
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "pat",
    ["import x", "from a.b import c", "class FooAgent", "def handler", "agentic_core.x", "apps_rg.y"],
)
def test_structural_patterns_detected(pat):
    assert gate._is_structural_pattern(pat)


@pytest.mark.parametrize("pat", ["TODO: x", "FIXME later", "# guardian: allow", ""])
def test_clearly_nonstructural(pat):
    assert gate._is_clearly_nonstructural(pat)


def test_evaluate_never_raises_on_garbage(healthy):
    healthy.setattr(gate, "_breadcrumb_fresh", lambda: False)
    # Missing tool_input, weird types — must not raise.
    code, _ = gate.evaluate({"tool_name": "Grep", "tool_input": None})
    assert code == 0
