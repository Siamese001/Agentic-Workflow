# pylint: disable=protected-access
"""Tests for the prose_options_menu Signal 5 added to
post_agent_author_gate_miss_detector.py (plan author-gate-prose-options-detection-e7f2a3).

Coverage:
    TC-1  G1.P3 verbatim Option A/B/C block       → score ≥ 2, prose_options_menu in signals
    TC-2  DECISION_CAPTURED present + options      → score = 0 (anti-signal clears)
    TC-3  AUTHOR_GATE_PACKET present + options     → score = 0
    TC-4  AUTHOR_GATE_PACKET + ask_user_question   → score = 0
    TC-5  Single "Option A" reference only         → prose_options_menu NOT fired
    TC-6  Recommended Next Phase + Option A        → score ≥ 2
    TC-7  **A. Continue / **B. Expand / **C. Proceed → score ≥ 2
    TC-8  ask_user_question without packet + opts  → score ≥ 2 (double violation)
    TC-9  Documentation text with examples         → prose_options_menu NOT fired when
                                                     surrounded by DECISION_CAPTURED
    _has_prose_options_menu unit tests (positive + negative)
    _has_author_gate_completion_marker unit tests
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[4] / ".claude" / "governance/scripts" / "_legacy_windsurf"
sys.path.insert(0, str(_SCRIPTS_DIR))

from post_agent_author_gate_miss_detector import (  # noqa: E402
    MISS_SCORE_THRESHOLD,
    _compute_miss_score,
    _has_author_gate_completion_marker,
    _has_prose_options_menu,
)

# ---------------------------------------------------------------------------
# G1.P3 verbatim sample — the exact response that triggered the RCA
# ---------------------------------------------------------------------------

_G1P3_SAMPLE = """
Here are the next steps after completing G1.P3.

**Option A — Continue G2 (Session Metadata):**
  Proceed with G2 wave which adds session-level metadata to the baseline.
  This is the natural progression and keeps scope bounded.

**Option B — Expand G1 (Additional Paths):**
  Add the 12 remaining paths before moving to G2.
  Pros: more complete baseline. Cons: delays G2.

**Option C — Proceed to A1/A2 (apps_contract):**
  Skip G2 and go directly to the apps_contract tier.
  Fastest path to coverage.

Recommended Next Phase: Option A — Continue G2 is the most incremental choice.
"""


# ---------------------------------------------------------------------------
# _has_prose_options_menu — unit tests
# ---------------------------------------------------------------------------


class TestHasProseOptionsMenu:
    def test_g1p3_sample_fires(self):
        assert _has_prose_options_menu(_G1P3_SAMPLE) is True

    def test_bold_option_a_b_fires(self):
        text = "**Option A — Do this**\n\n**Option B — Do that**"
        assert _has_prose_options_menu(text) is True

    def test_single_option_a_does_not_fire(self):
        text = "You could think of **Option A** as the simpler approach here."
        assert _has_prose_options_menu(text) is False

    def test_recommended_next_phase_plus_option_fires(self):
        text = (
            "Recommended Next Phase: Option A — Continue with G2.\n"
            "Option B — Alternative approach for extended coverage."
        )
        assert _has_prose_options_menu(text) is True

    def test_bold_letter_prefix_fires(self):
        text = "**A. Continue G2**\n**B. Expand G1**\n**C. Proceed to A1**"
        assert _has_prose_options_menu(text) is True

    def test_option_with_paren_fires(self):
        text = "Option A (fastest path)\nOption B (safest path)"
        assert _has_prose_options_menu(text) is True

    def test_recommended_next_action_fires(self):
        text = (
            "Recommended Next Action: proceed with wave 3.\n"
            "**Option A — Wave 3 immediately.**"
        )
        assert _has_prose_options_menu(text) is True

    def test_unrelated_prose_does_not_fire(self):
        text = "The system processes requests via a queue and returns results."
        assert _has_prose_options_menu(text) is False

    def test_two_different_patterns_required(self):
        """Same pattern matched twice counts as only 1 pattern hit."""
        text = "**Option A — first**\n**Option A — duplicate**"
        # Both hits are from the same pattern (index 0). Requires ≥2 *distinct* patterns.
        # The function iterates patterns (not matches), so two hits of the same
        # pattern only increment matched_patterns once.
        # This text should still fire because **Option A** matches pattern[0] once,
        # and pattern[2] (\bOption A — \w) also matches — that's 2 distinct patterns.
        assert _has_prose_options_menu(text) is True

    def test_empty_string_does_not_fire(self):
        assert _has_prose_options_menu("") is False


# ---------------------------------------------------------------------------
# _has_author_gate_completion_marker — unit tests
# ---------------------------------------------------------------------------


class TestHasAuthorGateCompletionMarker:
    def test_decision_captured_detected(self):
        text = "DECISION_CAPTURED: type=refactor_scope, repo_area=x, selected=y, outcome=executed"
        assert _has_author_gate_completion_marker(text) is True

    def test_author_gate_packet_detected(self):
        text = 'AUTHOR_GATE_PACKET: {"version": 1}'
        assert _has_author_gate_completion_marker(text) is True

    def test_hitl_packet_detected(self):
        text = 'HITL_PACKET: {"version": 1}'
        assert _has_author_gate_completion_marker(text) is True

    def test_ask_with_ag10_shape_detected(self):
        text = (
            '<invoke name="ask_user_question">\n'
            "AUTHOR-GATE DECISION — refactor_scope\n"
            "⭐ Recommended: Archive\n"
        )
        assert _has_author_gate_completion_marker(text) is True

    def test_ask_without_ag10_shape_not_detected(self):
        text = (
            '<invoke name="ask_user_question">\n'
            "<parameter>pick one</parameter>\n"
        )
        assert _has_author_gate_completion_marker(text) is False

    def test_plain_response_not_detected(self):
        assert _has_author_gate_completion_marker("Here is a plain response.") is False


# ---------------------------------------------------------------------------
# _compute_miss_score — TC-1 through TC-9
# ---------------------------------------------------------------------------


class TestComputeMissScoreProseOptions:
    def test_tc1_g1p3_sample_fires(self):
        """TC-1: G1.P3 verbatim Option A/B/C triggers miss_score >= 2."""
        score, report = _compute_miss_score(_G1P3_SAMPLE)
        assert score >= MISS_SCORE_THRESHOLD
        assert "prose_options_menu" in report["positive_signals"]

    def test_tc2_decision_captured_suppresses(self):
        """TC-2: DECISION_CAPTURED present + prose options → score = 0."""
        text = (
            "DECISION_CAPTURED: type=architecture_choice, repo_area=gov, "
            "selected=option_a, outcome=executed\n"
            + _G1P3_SAMPLE
        )
        score, report = _compute_miss_score(text)
        assert score == 0
        assert report.get("anti_signal") == "capture_marker_present"

    def test_tc3_author_gate_packet_suppresses(self):
        """TC-3: AUTHOR_GATE_PACKET present + prose options → score = 0."""
        text = 'AUTHOR_GATE_PACKET: {"version": 1}\n' + _G1P3_SAMPLE
        score, report = _compute_miss_score(text)
        assert score == 0
        assert report.get("anti_signal") == "capture_marker_present"

    def test_tc4_ag10_compliant_ask_suppresses(self):
        """TC-4: AUTHOR_GATE_PACKET + ask_user_question with AG-10 shape → score = 0."""
        text = (
            'AUTHOR_GATE_PACKET: {"version": 1}\n'
            '<invoke name="ask_user_question">\n'
            "AUTHOR-GATE DECISION — architecture_choice\n"
            "⭐ Recommended: Option A\n"
            + _G1P3_SAMPLE
        )
        score, report = _compute_miss_score(text)
        assert score == 0
        assert report.get("anti_signal") == "capture_marker_present"

    def test_tc5_single_option_a_does_not_trigger(self):
        """TC-5: Single 'Option A' reference without a sibling does not trigger."""
        text = "You could consider **Option A** as the simpler path for this change."
        score, report = _compute_miss_score(text)
        assert "prose_options_menu" not in report.get("positive_signals", [])
        assert score < MISS_SCORE_THRESHOLD

    def test_tc6_recommended_next_phase_plus_option_triggers(self):
        """TC-6: 'Recommended Next Phase' phrase + Option A sibling → score ≥ 2."""
        text = (
            "Recommended Next Phase: Option A — Continue with session metadata.\n"
            "Option B — Expand baseline before moving on."
        )
        score, report = _compute_miss_score(text)
        assert score >= MISS_SCORE_THRESHOLD
        assert "prose_options_menu" in report["positive_signals"]

    def test_tc7_bold_letter_prefix_triggers(self):
        """TC-7: **A. Continue / **B. Expand / **C. Proceed → score ≥ 2."""
        text = (
            "**A. Continue G2** — natural progression.\n"
            "**B. Expand G1** — more complete but slower.\n"
            "**C. Proceed to A1/A2** — fastest path."
        )
        score, report = _compute_miss_score(text)
        assert score >= MISS_SCORE_THRESHOLD
        assert "prose_options_menu" in report["positive_signals"]

    def test_tc8_ask_without_packet_plus_options_double_violation(self):
        """TC-8: ask_user_question without packet + prose options → score ≥ 2."""
        text = (
            '<invoke name="ask_user_question">\n'
            "<parameter>pick an option</parameter>\n"
            "**Option A — First path**\n"
            "**Option B — Second path**\n"
        )
        score, report = _compute_miss_score(text)
        assert score >= MISS_SCORE_THRESHOLD
        # Both signals should fire
        signals = report["positive_signals"]
        assert any("ask_user_question_without_ag10_shape" in s for s in signals)
        assert "prose_options_menu" in signals

    def test_tc9_doc_example_with_decision_captured_does_not_trigger(self):
        """TC-9: Documentation text with option menu examples + DECISION_CAPTURED → 0."""
        text = (
            "DECISION_CAPTURED: type=architecture_choice, repo_area=docs, "
            "selected=option_a, outcome=executed\n\n"
            "## Example of FORBIDDEN pattern (do not copy)\n\n"
            "**Option A — Continue G2**\n"
            "**Option B — Expand G1**\n"
            "**Option C — Proceed to A1**\n"
        )
        score, report = _compute_miss_score(text)
        assert score == 0
        assert report.get("anti_signal") == "capture_marker_present"

    def test_prose_options_signal_weight_is_three(self):
        """Signal 5 alone (weight +3) must exceed MISS_SCORE_THRESHOLD (2)."""
        text = (
            "**Option A — Do the first thing.**\n"
            "**Option B — Do the second thing.**\n"
        )
        score, report = _compute_miss_score(text)
        assert score >= 3
        assert "prose_options_menu" in report["positive_signals"]

    def test_existing_signals_not_weakened(self):
        """Verify Signal 1 (multi_file_edit) is unchanged and still scores +2."""
        text = (
            'edit(file_path="agentic_core/L0_routing/run.py") '
            'edit(file_path="apps_lic/engines/control.py") '
            "bare except subprocess"
        )
        score, report = _compute_miss_score(text)
        assert score >= MISS_SCORE_THRESHOLD
        assert any(s.startswith("multi_file_edit") for s in report["positive_signals"])
        assert any(s.startswith("keyword") for s in report["positive_signals"])
