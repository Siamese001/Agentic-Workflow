"""Unit tests for pre_ask_user_question_recommendation_gate.py.

The decision function ``evaluate`` is exercised in isolation — no live tool, no hook
plumbing. Covers the §6 recommended-marker check (Finding 1), the confidence-band check
(Finding 2), the recommended-first convention, advisory-vs-strict behavior, bypass, and
fail-open paths.

Plan precedent: RCA 2026-06-08 (AskUserQuestion shipped with no (Recommended)/confidence).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[5]
_GATE_PATH = (
    _REPO_ROOT
    / ".claude"
    / "governance"
    / "scripts"
    / "pre_ask_user_question_recommendation_gate.py"
)


def _load_gate():
    spec = importlib.util.spec_from_file_location("pre_auq_rec_gate", _GATE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = _load_gate()


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch, tmp_path):
    """Neutralize bypass/strict env and redirect the violations log to a temp file."""
    monkeypatch.delenv(gate._BYPASS_ENV, raising=False)
    monkeypatch.delenv(gate._STRICT_ENV, raising=False)
    monkeypatch.setattr(gate, "_VIOLATIONS_LOG", tmp_path / "viol.jsonl")
    return monkeypatch


def _auq(*options: dict, header: str = "Approach") -> dict:
    return {
        "tool_name": "AskUserQuestion",
        "tool_input": {
            "questions": [
                {"question": "Which approach?", "header": header, "options": list(options)}
            ]
        },
    }


def _opt(label: str, description: str = "a trade-off") -> dict:
    return {"label": label, "description": description}


# --------------------------------------------------------------------------------------
# allow paths
# --------------------------------------------------------------------------------------

def test_non_ask_user_question_allowed():
    code, reason = gate.evaluate({"tool_name": "Grep", "tool_input": {}})
    assert code == 0
    assert "not AskUserQuestion" in reason


def test_bypass_allows(_clean_env):
    _clean_env.setenv(gate._BYPASS_ENV, "1")
    payload = _auq(_opt("Option A"), _opt("Option B"))  # no recommended at all
    code, reason = gate.evaluate(payload)
    assert code == 0
    assert "bypass" in reason.lower()


def test_compliant_recommended_first_with_confidence():
    payload = _auq(
        _opt("Do it inline (Recommended)", "high confidence; flips if blast radius grows"),
        _opt("Refactor first", "lower-risk but slower"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 0
    assert reason.startswith("ok:")


def test_confidence_keyword_satisfies():
    payload = _auq(
        _opt("Merge as-is (Recommended)", "Confidence: medium — flips on new failures"),
        _opt("Hold", "wait for review"),
    )
    code, _ = gate.evaluate(payload)
    assert code == 0


# --------------------------------------------------------------------------------------
# advisory (non-strict) findings — exit 0 but flagged
# --------------------------------------------------------------------------------------

def test_missing_recommended_marker_is_advisory():
    payload = _auq(_opt("Option A"), _opt("Option B"))
    code, reason = gate.evaluate(payload)
    assert code == 0
    assert reason.startswith("ADVISORY")
    assert "no option marked" in reason


def test_recommended_without_confidence_blocks_by_default():
    # Default-to-enforcement (user directive 2026-06-13): a marked recommendation with no
    # confidence signal is the core violation → BLOCK (exit 2) without needing strict mode.
    payload = _auq(
        _opt("Pick this one (Recommended)", "just a plain trade-off, no band"),
        _opt("Other", "x"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "contract" in reason
    assert "confidence signal" in reason


def test_recommended_without_confidence_bypass_allows(_clean_env):
    # The bypass escape hatch still overrides the default block.
    _clean_env.setenv(gate._BYPASS_ENV, "1")
    payload = _auq(
        _opt("Pick this one (Recommended)", "no band"),
        _opt("Other", "x"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 0
    assert "bypass" in reason.lower()


def test_symmetric_question_not_blocked_by_default():
    # No option marked (Recommended) — a legitimate symmetric question — stays advisory,
    # NOT blocked, so the enforcement default does not false-block preference questions.
    payload = _auq(_opt("Red", "warm"), _opt("Blue", "cool"))
    code, reason = gate.evaluate(payload)
    assert code == 0
    assert reason.startswith("ADVISORY")


def test_recommended_not_first_is_flagged():
    payload = _auq(
        _opt("Other", "x"),
        _opt("Pick this (Recommended)", "high confidence"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 0
    assert "not placed first" in reason


def test_violation_is_logged(_clean_env):
    payload = _auq(_opt("A"), _opt("B"))
    gate.evaluate(payload)
    assert gate._VIOLATIONS_LOG.exists()
    assert "no option marked" in gate._VIOLATIONS_LOG.read_text(encoding="utf-8")


# --------------------------------------------------------------------------------------
# strict mode — exit 2 (block)
# --------------------------------------------------------------------------------------

def test_strict_blocks_missing_recommended(_clean_env):
    _clean_env.setenv(gate._STRICT_ENV, "1")
    payload = _auq(_opt("A"), _opt("B"))
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "contract" in reason


def test_strict_allows_compliant(_clean_env):
    _clean_env.setenv(gate._STRICT_ENV, "1")
    payload = _auq(
        _opt("Go (Recommended)", "high confidence"),
        _opt("Stop", "x"),
    )
    code, _ = gate.evaluate(payload)
    assert code == 0


# --------------------------------------------------------------------------------------
# fail-open / shape robustness
# --------------------------------------------------------------------------------------

def test_no_questions_allowed():
    code, _ = gate.evaluate({"tool_name": "AskUserQuestion", "tool_input": {"questions": []}})
    assert code == 0


def test_freetext_only_question_allowed():
    # A question with no options (free-text) has nothing to enforce.
    payload = {
        "tool_name": "AskUserQuestion",
        "tool_input": {"questions": [{"question": "name?", "header": "Name"}]},
    }
    code, _ = gate.evaluate(payload)
    assert code == 0


def test_non_dict_payload_allowed():
    code, _ = gate.evaluate(None)  # type: ignore[arg-type]
    assert code == 0
