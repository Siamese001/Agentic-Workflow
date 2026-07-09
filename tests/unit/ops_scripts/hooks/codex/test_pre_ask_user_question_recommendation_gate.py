"""Unit tests for the Codex request_user_input recommendation gate."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[5]
_GATE_PATH = (
    _REPO_ROOT
    / ".codex"
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


def _question(*options: dict, header: str = "Approach", **overrides: object) -> dict:
    data = {
        "id": "approach",
        "question": "Which approach?",
        "header": header,
        "options": list(options),
    }
    data.update(overrides)
    return data


def _payload(*options: dict, question_overrides: dict | None = None, tool_name: str = "functions.request_user_input") -> dict:
    return {
        "tool_name": tool_name,
        "tool_input": {
            "questions": [
                _question(*options, **(question_overrides or {})),
            ]
        },
    }


def _opt(label: str, description: str = "a trade-off") -> dict:
    return {"label": label, "description": description}


def _recommended(label: str = "Do it inline (Recommended)", confidence: str = "0.82") -> dict:
    return _opt(
        label,
        f"[RECOMMENDED ⭐ confidence={confidence}] Pros: fastest fix. Cons: more local coupling. "
        "Flips if blast radius grows.",
    )


def _alternative(label: str = "Refactor first", confidence: str = "0.61") -> dict:
    return _opt(label, f"[confidence={confidence}] Pros: cleaner shape. Cons: slower delivery.")


def test_non_request_user_input_allowed():
    code, reason = gate.evaluate({"tool_name": "Grep", "tool_input": {}})
    assert code == 0
    assert "not a native question tool" in reason


def test_compliant_codex_request_user_input_passes():
    code, reason = gate.evaluate(_payload(_recommended(), _alternative()))
    assert code == 0
    assert reason.startswith("ok:")


def test_unqualified_codex_request_user_input_passes():
    payload = _payload(_recommended(), _alternative(), tool_name="request_user_input")
    code, reason = gate.evaluate(payload)
    assert code == 0
    assert reason.startswith("ok:")


def test_missing_question_id_blocks():
    payload = _payload(_recommended(), _alternative(), question_overrides={"id": ""})
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "must include non-empty 'id'" in reason


def test_missing_header_blocks():
    payload = _payload(_recommended(), _alternative(), question_overrides={"header": ""})
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "must include non-empty 'header'" in reason


def test_legacy_multiselect_field_blocks():
    payload = _payload(_recommended(), _alternative(), question_overrides={"multiSelect": False})
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "must not include legacy-only 'multiSelect'" in reason


def test_one_option_blocks_codex_schema():
    payload = _payload(_recommended())
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "must include 2-3 options" in reason


def test_four_options_blocks_codex_schema():
    payload = _payload(
        _recommended(),
        _alternative("B"),
        _alternative("C"),
        _alternative("D"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "must include 2-3 options" in reason


def test_option_description_required():
    payload = _payload(_recommended(), {"label": "Other", "description": ""})
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "must include non-empty 'description'" in reason


def test_bypass_allows(_clean_env):
    _clean_env.setenv(gate._BYPASS_ENV, "1")
    payload = _payload(_opt("Option A"), _opt("Option B"))
    code, reason = gate.evaluate(payload)
    assert code == 0
    assert "bypass" in reason.lower()


def test_recommended_without_ui_contract_blocks():
    payload = _payload(
        _opt("Patch gate (Recommended)", "Confidence high. Pros: closes gap. Cons: churn. Flips if unavailable."),
        _alternative("Document only", "0.24"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "Codex request_user_input recommendation/confidence contract" in reason
    assert "[RECOMMENDED ⭐ confidence=0.NN]" in reason


def test_confidence_keyword_without_numeric_prefix_blocks():
    payload = _payload(
        _opt("Merge as-is (Recommended)", "Confidence: medium. Pros: quick. Cons: risky. Flips if tests fail."),
        _alternative("Hold", "0.40"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "must begin" in reason


def test_out_of_range_confidence_value_blocks_visible_ui_contract():
    payload = _payload(
        _recommended("Patch gate (Recommended)", "1.20"),
        _alternative("Document only", "0.24"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "recommended description must begin '[RECOMMENDED ⭐ confidence=0.NN]'" in reason


def test_non_recommended_out_of_range_confidence_value_blocks_visible_ui_contract():
    payload = _payload(
        _recommended("Patch gate (Recommended)", "1.00"),
        _alternative("Document only", "1.20"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "Document only description must begin with numeric 0.00-1.00 confidence prefix" in reason


def test_missing_recommended_marker_is_advisory():
    payload = _payload(
        _opt("Option A", "[confidence=0.51] Pros: quick. Cons: less proof."),
        _opt("Option B", "[confidence=0.49] Pros: safer. Cons: slower."),
    )
    code, reason = gate.evaluate(payload)
    assert code == 0
    assert reason.startswith("ADVISORY")
    assert "no option marked" in reason


def test_recommended_without_confidence_blocks_by_default():
    payload = _payload(
        _opt("Pick this one (Recommended)", "just a plain trade-off, no band"),
        _alternative("Other", "0.35"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "contract" in reason
    assert "confidence" in reason


def test_symmetric_question_not_blocked_by_default():
    payload = _payload(
        _opt("Red", "[confidence=0.50] Pros: warm. Cons: less contrast."),
        _opt("Blue", "[confidence=0.50] Pros: cool. Cons: less warmth."),
    )
    code, reason = gate.evaluate(payload)
    assert code == 0
    assert reason.startswith("ADVISORY")


def test_recommended_not_first_is_flagged():
    payload = _payload(
        _alternative("Other", "0.40"),
        _recommended("Pick this (Recommended)", "0.80"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "not placed first" in reason


def test_violation_is_logged(_clean_env):
    payload = _payload(
        _opt("A", "[confidence=0.50] Pros: a. Cons: b."),
        _opt("B", "[confidence=0.50] Pros: c. Cons: d."),
    )
    gate.evaluate(payload)
    assert gate._VIOLATIONS_LOG.exists()
    assert "no option marked" in gate._VIOLATIONS_LOG.read_text(encoding="utf-8")


def test_strict_blocks_missing_recommended(_clean_env):
    _clean_env.setenv(gate._STRICT_ENV, "1")
    payload = _payload(
        _opt("A", "[confidence=0.50] Pros: a. Cons: b."),
        _opt("B", "[confidence=0.50] Pros: c. Cons: d."),
    )
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "contract" in reason


def test_strict_allows_compliant(_clean_env):
    _clean_env.setenv(gate._STRICT_ENV, "1")
    code, _ = gate.evaluate(_payload(_recommended("Go (Recommended)", "0.80"), _alternative("Stop", "0.35")))
    assert code == 0


def test_all_options_require_pros_and_cons():
    payload = _payload(
        _opt("Go (Recommended)", "[RECOMMENDED ⭐ confidence=0.80] Pros: completes the work. Flips if tests fail."),
        _alternative("Stop", "0.35"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "Pros: and Cons:" in reason


def test_recommended_requires_flip_condition():
    payload = _payload(
        _opt("Go (Recommended)", "[RECOMMENDED ⭐ confidence=0.80] Pros: completes the work. Cons: touches more code."),
        _alternative("Stop", "0.35"),
    )
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "Flips if" in reason


def test_no_questions_allowed_fail_open():
    code, _ = gate.evaluate({"tool_name": "functions.request_user_input", "tool_input": {"questions": []}})
    assert code == 0


def test_free_text_shape_blocks_for_codex():
    payload = {
        "tool_name": "functions.request_user_input",
        "tool_input": {"questions": [{"id": "name", "question": "name?", "header": "Name"}]},
    }
    code, reason = gate.evaluate(payload)
    assert code == 2
    assert "must include an options list" in reason


def test_non_dict_payload_allowed():
    code, _ = gate.evaluate(None)  # type: ignore[arg-type]
    assert code == 0
