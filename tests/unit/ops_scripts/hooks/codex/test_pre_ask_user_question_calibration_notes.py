"""Tests for the advisory precedent-calibration notes in the AskUserQuestion PreToolUse gate.

Plan: askq-confidence-meta-learning-loop-c4e7a1 (W2.2). The note is ADVISORY only — these tests
assert it surfaces a divergence when precedent exists and stays silent otherwise (and never via
the allow/block path, which is covered by the gate's own test suite).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_GATE_PATH = REPO_ROOT / ".codex" / "governance" / "scripts" / "pre_ask_user_question_recommendation_gate.py"
_spec = importlib.util.spec_from_file_location("pre_ask_user_question_recommendation_gate", _GATE_PATH)
assert _spec and _spec.loader
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


@pytest.fixture
def temp_ledger(tmp_path, monkeypatch):
    import tools.ledgers.ask_user_question_ledger as ledger_mod

    monkeypatch.setattr(ledger_mod, "LEDGER_PATH", tmp_path / "calib_notes_ledger.sqlite")
    ledger_mod.ensure_schema()
    monkeypatch.delenv("ASK_REC_CALIBRATION_ADVISORY", raising=False)
    return ledger_mod


def _payload(header: str, conf: float):
    return {
        "tool_name": "AskUserQuestion",
        "tool_input": {
            "questions": [
                {
                    "header": header,
                    "options": [
                        {"label": "Do it (Recommended)", "description": f"[confidence={conf:.2f}] go"},
                        {"label": "Don't", "description": "[confidence=0.40] no"},
                    ],
                }
            ]
        },
    }


def test_note_emitted_on_divergence(temp_ledger):
    # 12 prior overrides for context "approach" -> 0% acceptance; stating 0.90 is divergent.
    for _ in range(12):
        temp_ledger.write_decision({"context": "approach", "recommended_index": 0, "option_count": 2}, selected_index=1)
    notes = gate.calibration_notes(_payload("Approach", 0.90))
    assert len(notes) == 1
    assert "approach" in notes[0]
    assert "stated 0.90" in notes[0]


def test_no_note_without_precedent(temp_ledger):
    assert gate.calibration_notes(_payload("Approach", 0.90)) == []


def test_no_note_when_aligned(temp_ledger):
    # High acceptance + a confidence near it -> not divergent -> no note.
    for _ in range(12):
        temp_ledger.write_decision({"context": "approach", "recommended_index": 0, "option_count": 2}, selected_index=0)
    assert gate.calibration_notes(_payload("Approach", 0.95)) == []


def test_env_off_silences(temp_ledger, monkeypatch):
    for _ in range(12):
        temp_ledger.write_decision({"context": "approach", "recommended_index": 0, "option_count": 2}, selected_index=1)
    monkeypatch.setenv("ASK_REC_CALIBRATION_ADVISORY", "0")
    assert gate.calibration_notes(_payload("Approach", 0.90)) == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
