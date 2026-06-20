"""Tests for post_ask_user_question_capture — the PostToolUse WRITE+SELECTION seam.

Plan: askq-confidence-meta-learning-loop-c4e7a1 (W1.2).

Covers: confidence parsing, recommended-index detection, defensive selection extraction across
multiple plausible tool_response shapes, per-question row building, and an end-to-end capture that
writes through the real ledger (redirected to a temp DB) and is read back — proving the
recommended-vs-selected learning signal is persisted.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_CAPTURE_PATH = REPO_ROOT / ".codex" / "governance" / "scripts" / "post_ask_user_question_capture.py"
_spec = importlib.util.spec_from_file_location("post_ask_user_question_capture", _CAPTURE_PATH)
assert _spec and _spec.loader
cap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cap)


# ----------------------------- pure helpers ----------------------------- #


class TestParseConfidence:
    def test_explicit_numeric(self):
        assert cap.parse_confidence("[confidence=0.85] safer path") == (0.85, "explicit")

    def test_recommended_star_form(self):
        score, source = cap.parse_confidence("[RECOMMENDED ⭐ confidence=0.92] best option")
        assert score == 0.92
        assert source == "explicit"

    def test_word_band_fallback(self):
        assert cap.parse_confidence("high confidence here") == (0.9, "band")

    def test_none_when_absent(self):
        assert cap.parse_confidence("no signal at all") == (None, "heuristic_default")


class TestRecommendedIndex:
    def test_finds_recommended_suffix(self):
        opts = [{"label": "A"}, {"label": "B (Recommended)"}, {"label": "C"}]
        assert cap.recommended_index(opts) == 1

    def test_none_when_no_recommendation(self):
        assert cap.recommended_index([{"label": "A"}, {"label": "B"}]) is None


class TestSelectionExtraction:
    def test_label_match_answers_shape(self):
        opts = [{"label": "Lazy import"}, {"label": "Extract interface (Recommended)"}]
        sel = ["Extract interface (Recommended)"]
        assert cap.selected_index_for_question(0, opts, sel, {}) == 1

    def test_label_match_ignores_recommended_suffix_mismatch(self):
        # User payload may echo the label without the suffix — still matches.
        opts = [{"label": "Lazy import"}, {"label": "Extract interface (Recommended)"}]
        assert cap.selected_index_for_question(0, opts, ["Extract interface"], {}) == 1

    def test_numeric_index_fallback(self):
        opts = [{"label": "A"}, {"label": "B"}]
        assert cap.selected_index_for_question(0, opts, [], {0: 1}) == 1

    def test_none_when_unresolved(self):
        opts = [{"label": "A"}, {"label": "B"}]
        assert cap.selected_index_for_question(0, opts, ["something else"], {}) is None

    def test_collect_strings_from_header_label_map(self):
        out: list[str] = []
        cap._collect_selected_strings({"Approach": "Extract interface"}, out)
        assert "Extract interface" in out

    def test_collect_strings_from_list(self):
        out: list[str] = []
        cap._collect_selected_strings(["Option A", "Option B"], out)
        assert out == ["Option A", "Option B"]


class TestBuildDecisionRows:
    def _tool_input(self):
        return {
            "questions": [
                {
                    "header": "Approach",
                    "question": "Which approach for the split?",
                    "options": [
                        {"label": "Extract file (Recommended)", "description": "[RECOMMENDED ⭐ confidence=0.85] clearer"},
                        {"label": "Keep inline", "description": "[confidence=0.70] less churn"},
                    ],
                }
            ]
        }

    def test_row_captures_recommended_and_confidence(self):
        rows = cap.build_decision_rows(self._tool_input(), {"answers": [{"selected_label": "Extract file (Recommended)"}]})
        assert len(rows) == 1
        packet = rows[0]["packet"]
        assert packet["recommended_index"] == 0
        assert packet["confidence_score"] == 0.85
        assert packet["confidence_source"] == "explicit"
        assert packet["option_count"] == 2
        assert packet["context"] == "approach"
        assert rows[0]["selected_index"] == 0  # user took the recommendation

    def test_override_signal_recorded(self):
        # User picked the NON-recommended option — the key learning signal.
        rows = cap.build_decision_rows(self._tool_input(), {"answers": [{"selected_label": "Keep inline"}]})
        assert rows[0]["packet"]["recommended_index"] == 0
        assert rows[0]["selected_index"] == 1

    def test_multi_question(self):
        ti = {
            "questions": [
                {"header": "Store", "options": [{"label": "Reuse (Recommended)", "description": "[confidence=0.8] x"}, {"label": "Migrate", "description": "[confidence=0.6] y"}]},
                {"header": "Mode", "options": [{"label": "Advisory (Recommended)", "description": "[confidence=0.75] z"}, {"label": "Blocking", "description": "[confidence=0.5] w"}]},
            ]
        }
        rows = cap.build_decision_rows(ti, {"Store": "Reuse (Recommended)", "Mode": "Blocking"})
        assert len(rows) == 2
        assert rows[0]["selected_index"] == 0
        assert rows[1]["selected_index"] == 1

    def test_empty_when_no_questions(self):
        assert cap.build_decision_rows({}, {}) == []

    def test_reused_labels_scoped_per_question_answers_list(self):
        # Two questions reuse labels A/B. q0 -> B (idx 1), q1 -> A (idx 0).
        # A global pool would mis-assign q0 to the first 'A' match — this asserts per-question scope.
        ti = {
            "questions": [
                {"header": "Q0", "options": [{"label": "A", "description": "[confidence=0.6] a"}, {"label": "B (Recommended)", "description": "[confidence=0.8] b"}]},
                {"header": "Q1", "options": [{"label": "A (Recommended)", "description": "[confidence=0.8] a"}, {"label": "B", "description": "[confidence=0.6] b"}]},
            ]
        }
        rows = cap.build_decision_rows(ti, {"answers": [{"selected_label": "B"}, {"selected_label": "A"}]})
        assert rows[0]["selected_index"] == 1  # q0 chose B
        assert rows[1]["selected_index"] == 0  # q1 chose A

    def test_reused_labels_scoped_per_question_header_map(self):
        ti = {
            "questions": [
                {"header": "Q0", "options": [{"label": "A"}, {"label": "B"}]},
                {"header": "Q1", "options": [{"label": "A"}, {"label": "B"}]},
            ]
        }
        rows = cap.build_decision_rows(ti, {"Q0": "B", "Q1": "A"})
        assert rows[0]["selected_index"] == 1
        assert rows[1]["selected_index"] == 0


class TestSelectedStringsScoping:
    def test_positional_answers_isolates_question(self):
        q = {"header": "Q1"}
        out = cap.selected_strings_for_question({"answers": [{"selected_label": "X"}, {"selected_label": "Y"}]}, 1, q, 2)
        assert out == ["Y"]

    def test_header_keyed_isolates_question(self):
        q = {"header": "Mode"}
        out = cap.selected_strings_for_question({"Store": "Reuse", "Mode": "Advisory"}, 1, q, 2)
        assert out == ["Advisory"]

    def test_single_question_whole_response_fallback(self):
        q = {"header": "unmatched-header"}
        out = cap.selected_strings_for_question({"chosen": "OnlyAnswer"}, 0, q, 1)
        assert "OnlyAnswer" in out

    def test_multi_question_no_unscoped_fallback(self):
        # With 2 questions and an unkeyed dict, do NOT leak the whole response into one question.
        q = {"header": "unmatched-header"}
        out = cap.selected_strings_for_question({"chosen": "Leak"}, 0, q, 2)
        assert out == []


# ----------------------------- end-to-end ----------------------------- #


@pytest.fixture
def temp_ledger(tmp_path):
    """Redirect the real ledger writer to a temp DB (mirrors the shadow-loop fixture)."""
    import tools.ledgers.ask_user_question_ledger as ledger_mod

    original = ledger_mod.LEDGER_PATH
    ledger_mod.LEDGER_PATH = tmp_path / "test_capture_ledger.sqlite"
    ledger_mod.ensure_schema()
    yield ledger_mod
    ledger_mod.LEDGER_PATH = original


class TestCaptureEndToEnd:
    def test_capture_writes_row_with_selection(self, temp_ledger):
        payload = {
            "tool_name": "AskUserQuestion",
            "tool_input": {
                "questions": [
                    {
                        "header": "Capture mech",
                        "question": "Which capture mechanism?",
                        "options": [
                            {"label": "PostToolUse hook (Recommended)", "description": "[RECOMMENDED ⭐ confidence=0.88] atomic"},
                            {"label": "Self-report marker", "description": "[confidence=0.40] brittle"},
                        ],
                    }
                ]
            },
            "tool_response": {"answers": [{"selected_label": "PostToolUse hook (Recommended)"}]},
        }
        ids = cap.capture(payload)
        assert len(ids) == 1

        rows = temp_ledger.list_recent_decisions(context="capture-mech")
        assert len(rows) == 1
        assert rows[0]["recommended_index"] == 0
        assert rows[0]["selected_index"] == 0
        assert rows[0]["confidence_score"] == 0.88
        assert rows[0]["confidence_source"] == "explicit"

    def test_capture_ignores_non_ask_user_question(self, temp_ledger):
        assert cap.capture({"tool_name": "Write", "tool_input": {}}) == []

    def test_capture_override_persisted(self, temp_ledger):
        payload = {
            "tool_name": "AskUserQuestion",
            "tool_input": {
                "questions": [
                    {
                        "header": "X",
                        "options": [
                            {"label": "A (Recommended)", "description": "[confidence=0.9] a"},
                            {"label": "B", "description": "[confidence=0.6] b"},
                        ],
                    }
                ]
            },
            "tool_response": {"answers": [{"selected_label": "B"}]},
        }
        ids = cap.capture(payload)
        assert len(ids) == 1
        row = temp_ledger.list_recent_decisions(context="x")[0]
        assert row["recommended_index"] == 0
        assert row["selected_index"] == 1  # override captured


class TestMainEntryPointClosure:
    """Drive the real stdin -> main() -> write_decision path (loop closure proof)."""

    def test_main_stdin_writes_row(self, temp_ledger, monkeypatch):
        import io
        import json as _json

        payload = {
            "tool_name": "AskUserQuestion",
            "tool_input": {
                "questions": [
                    {
                        "header": "Next step",
                        "options": [
                            {"label": "Ship it (Recommended)", "description": "[RECOMMENDED ⭐ confidence=0.80] go"},
                            {"label": "Wait", "description": "[confidence=0.50] hold"},
                        ],
                    }
                ]
            },
            "tool_response": {"answers": [{"selected_label": "Wait"}]},
        }
        monkeypatch.setattr("sys.stdin", io.StringIO(_json.dumps(payload)))
        rc = cap.main()
        assert rc == 0
        rows = temp_ledger.list_recent_decisions(context="next-step")
        assert len(rows) == 1
        assert rows[0]["recommended_index"] == 0
        assert rows[0]["selected_index"] == 1  # override captured through the real entry path

    def test_main_empty_stdin_is_noop(self, temp_ledger, monkeypatch):
        import io

        monkeypatch.setattr("sys.stdin", io.StringIO(""))
        assert cap.main() == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
