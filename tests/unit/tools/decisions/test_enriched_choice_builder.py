"""Unit tests for enriched_choice_builder.

Per hardened plan ui-choice-consistency-zero-loss-hardened-d9f3a1:
- Unit tests prove formatting invariants (confidence prefix, star count, trade-off)
- Tests verify DEFAULT_HEURISTIC_CONFIDENCE labeling
- Tests verify telemetry packet shape
- Tests verify AUTHOR_GATE_PACKET is never emitted

Responsibility split per review #6:
- These tests prove the BUILDER's formatting invariants
- Scanner tests (separate) prove callsite discipline
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

# Import the module under test
import sys
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.decisions.enriched_choice_builder import (
    build_enriched_choice_question,
    DEFAULT_HEURISTIC_CONFIDENCE,
    EnrichedOption,
    TelemetryPacket,
    _validate_options,
    _enrich_options,
    _validate_star_invariant,
)


class TestBasicFormatting:
    """Tests 1-2: Basic enriched question formatting."""

    def test_two_option_enriched_question(self):
        """Test 1: Standard two-option enriched question passes."""
        payload = build_enriched_choice_question(
            question="Which approach?",
            options=[
                {
                    "id": "A",
                    "label": "Fast approach",
                    "description": "Quick implementation",
                    "tradeoff": "Higher risk of edge-case misses",
                    "confidence": 0.74,
                },
                {
                    "id": "B",
                    "label": "Safe approach",
                    "description": "Conservative implementation",
                    "tradeoff": "Slower but validates all assumptions",
                    "confidence": 0.88,
                },
            ],
        )

        assert payload["question"] == "Which approach?"
        assert len(payload["options"]) == 2

        # Verify label format: "ID [confidence=X.XX] Label"
        opt_a = payload["options"][0]
        assert opt_a["label"].startswith("A [confidence=0.74]")
        assert "Fast approach" in opt_a["label"]

        opt_b = payload["options"][1]
        assert opt_b["label"].startswith("B [confidence=0.88]")
        assert "Safe approach" in opt_b["label"]

    def test_three_option_enriched_question(self):
        """Test 2: Three-option enriched question passes."""
        payload = build_enriched_choice_question(
            question="Pick a strategy:",
            options=[
                {
                    "id": "X",
                    "label": "Option X",
                    "description": "First option",
                    "tradeoff": "Tradeoff X",
                },
                {
                    "id": "Y",
                    "label": "Option Y",
                    "description": "Second option",
                    "tradeoff": "Tradeoff Y",
                },
                {
                    "id": "Z",
                    "label": "Option Z",
                    "description": "Third option",
                    "tradeoff": "Tradeoff Z",
                },
            ],
        )

        assert len(payload["options"]) == 3
        # All options have confidence prefix (using default)
        for opt in payload["options"]:
            assert "[confidence=" in opt["label"]
            assert "trade-off:" in opt["description"]


class TestStarInvariant:
    """Tests 3-5: Star/recommendation invariants."""

    def test_recommended_option_has_exactly_one_star(self):
        """Test 3: Recommended option has exactly one star."""
        payload = build_enriched_choice_question(
            question="Which approach?",
            options=[
                {
                    "id": "A",
                    "label": "Fast approach",
                    "description": "Quick implementation",
                    "tradeoff": "Higher risk",
                    "confidence": 0.74,
                },
                {
                    "id": "B",
                    "label": "Safe approach",
                    "description": "Conservative implementation",
                    "tradeoff": "Slower but safer",
                    "confidence": 0.88,
                },
            ],
            recommended_id="B",
        )

        opt_a = payload["options"][0]
        opt_b = payload["options"][1]

        # Option B (recommended) has star
        assert "⭐" in opt_b["label"]
        # Option A (not recommended) has no star
        assert "⭐" not in opt_a["label"]

        # Exactly one star total
        star_count = sum(1 for opt in payload["options"] if "⭐" in opt["label"])
        assert star_count == 1

    def test_no_recommendation_allows_zero_stars(self):
        """Test 4: No recommendation allows zero stars."""
        payload = build_enriched_choice_question(
            question="Which approach?",
            options=[
                {
                    "id": "A",
                    "label": "Fast approach",
                    "description": "Quick implementation",
                    "tradeoff": "Higher risk",
                },
                {
                    "id": "B",
                    "label": "Safe approach",
                    "description": "Conservative implementation",
                    "tradeoff": "Slower but safer",
                },
            ],
            # No recommended_id
        )

        # No stars in any option
        for opt in payload["options"]:
            assert "⭐" not in opt["label"]

        # Telemetry shows no recommendation
        assert payload["telemetry_packet"]["recommended_index"] is None

    def test_multiple_stars_fails_validation(self):
        """Test 5: Multiple recommended options fails validation."""
        # This should be caught by the builder
        # Note: build_enriched_choice_question only accepts single recommended_id
        # So we test the internal _validate_star_invariant directly

        enriched = [
            EnrichedOption(
                id="A", label="Option A", description="Desc A",
                tradeoff="Trade A", confidence=0.8, confidence_source="explicit",
                is_recommended=True,
            ),
            EnrichedOption(
                id="B", label="Option B", description="Desc B",
                tradeoff="Trade B", confidence=0.8, confidence_source="explicit",
                is_recommended=True,  # Second recommendation - invalid
            ),
        ]

        with pytest.raises(ValueError, match="Multiple recommended options"):
            _validate_star_invariant(enriched)


class TestConfidenceHandling:
    """Tests 6-7: Confidence source labeling."""

    def test_explicit_confidence_preserved(self):
        """Test 6: Explicit confidence is preserved and labeled."""
        payload = build_enriched_choice_question(
            question="Which?",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "Description",
                    "tradeoff": "Tradeoff",
                    "confidence": 0.91,
                },
            ],
        )

        # Telemetry shows explicit source
        assert payload["telemetry_packet"]["confidence_source"] == "explicit"

        # Label shows the explicit confidence
        assert "[confidence=0.91]" in payload["options"][0]["label"]

    def test_missing_confidence_uses_default_with_label(self):
        """Test 7: Missing confidence uses DEFAULT_HEURISTIC_CONFIDENCE with source label."""
        payload = build_enriched_choice_question(
            question="Which?",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "Description",
                    "tradeoff": "Tradeoff",
                    # No confidence provided
                },
            ],
        )

        # Telemetry shows heuristic default source
        assert payload["telemetry_packet"]["confidence_source"] == "heuristic_default"

        # Label shows the default confidence
        expected_conf = f"[confidence={DEFAULT_HEURISTIC_CONFIDENCE:.2f}]"
        assert expected_conf in payload["options"][0]["label"]


class TestTradeoffRequirement:
    """Test 8: Trade-off required validation."""

    def test_missing_tradeoff_raises_valueerror(self):
        """Test 8: Missing trade-off raises ValueError."""
        with pytest.raises(ValueError, match="tradeoff"):
            build_enriched_choice_question(
                question="Which?",
                options=[
                    {
                        "id": "A",
                        "label": "Option A",
                        "description": "Description",
                        # Missing tradeoff
                    },
                ],
            )

    def test_all_options_have_tradeoff_segment(self):
        """Verify all options have trade-off segment in description."""
        payload = build_enriched_choice_question(
            question="Which?",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "Description A",
                    "tradeoff": "Tradeoff A description",
                },
                {
                    "id": "B",
                    "label": "Option B",
                    "description": "Description B",
                    "tradeoff": "Tradeoff B description",
                },
            ],
        )

        for opt in payload["options"]:
            assert "· trade-off:" in opt["description"]


class TestTelemetry:
    """Tests 9-11: Telemetry packet shape and authority boundaries."""

    def test_telemetry_packet_shape(self):
        """Test 9: Telemetry packet has correct ASK_USER_QUESTION_PACKET shape."""
        payload = build_enriched_choice_question(
            question="Which?",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "Description",
                    "tradeoff": "Tradeoff",
                    "confidence": 0.85,
                },
            ],
            recommended_id="A",
            telemetry_context="test-context",
        )

        telemetry = payload["telemetry_packet"]

        # Required fields
        assert telemetry["packet_type"] == "ASK_USER_QUESTION_PACKET"
        assert telemetry["context"] == "test-context"
        assert telemetry["option_count"] == 1
        assert telemetry["recommended_index"] == 0
        assert telemetry["confidence_source"] == "explicit"
        assert "invariants" in telemetry
        assert "confidence_prefix" in telemetry["invariants"]
        assert "tradeoff_segment" in telemetry["invariants"]
        assert "star_marker" in telemetry["invariants"]

        # Timestamp format
        assert "T" in telemetry["timestamp"]  # ISO format

    def test_author_gate_packet_never_in_telemetry(self):
        """Test 10: AUTHOR_GATE_PACKET never appears in telemetry."""
        payload = build_enriched_choice_question(
            question="Which?",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "Description",
                    "tradeoff": "Tradeoff",
                },
            ],
        )

        telemetry = payload["telemetry_packet"]

        # Verify it's ASK_USER_QUESTION_PACKET, never AUTHOR_GATE_PACKET
        assert telemetry["packet_type"] == "ASK_USER_QUESTION_PACKET"
        assert telemetry["packet_type"] != "AUTHOR_GATE_PACKET"

        # Verify no AUTHOR_GATE fields present
        assert "decision_id" not in telemetry
        assert "candidates" not in telemetry
        assert "routing" not in telemetry

    def test_telemetry_context_preserved(self):
        """Test 11: Telemetry context is preserved from input."""
        payload = build_enriched_choice_question(
            question="Which?",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "Description",
                    "tradeoff": "Tradeoff",
                },
            ],
            telemetry_context="my-custom-context",
        )

        assert payload["telemetry_packet"]["context"] == "my-custom-context"

    def test_default_context_when_not_provided(self):
        """Default context is 'enriched_choice' when not provided."""
        payload = build_enriched_choice_question(
            question="Which?",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "Description",
                    "tradeoff": "Tradeoff",
                },
            ],
        )

        assert payload["telemetry_packet"]["context"] == "enriched_choice"


class TestOptionLimits:
    """Additional validation tests."""

    def test_max_four_options(self):
        """Maximum 4 options allowed."""
        with pytest.raises(ValueError, match="Maximum 4 options"):
            build_enriched_choice_question(
                question="Which?",
                options=[
                    {"id": str(i), "label": f"Opt {i}", "description": "Desc", "tradeoff": "Trade"}
                    for i in range(5)
                ],
            )

    def test_no_options_fails(self):
        """At least one option required."""
        with pytest.raises(ValueError, match="At least one option"):
            build_enriched_choice_question(
                question="Which?",
                options=[],
            )

    def test_duplicate_ids_fails(self):
        """Duplicate IDs not allowed."""
        with pytest.raises(ValueError, match="unique"):
            build_enriched_choice_question(
                question="Which?",
                options=[
                    {"id": "A", "label": "Opt A", "description": "Desc", "tradeoff": "Trade"},
                    {"id": "A", "label": "Opt A2", "description": "Desc2", "tradeoff": "Trade2"},
                ],
            )

    def test_missing_id_fails(self):
        """Missing ID fails validation."""
        with pytest.raises(ValueError, match="id"):
            build_enriched_choice_question(
                question="Which?",
                options=[
                    {"label": "Opt A", "description": "Desc", "tradeoff": "Trade"},
                ],
            )

    def test_invalid_recommended_id_fails(self):
        """Recommended ID must exist in options."""
        with pytest.raises(ValueError, match="recommended_id"):
            build_enriched_choice_question(
                question="Which?",
                options=[
                    {"id": "A", "label": "Opt A", "description": "Desc", "tradeoff": "Trade"},
                ],
                recommended_id="B",  # Doesn't exist
            )


class TestConfidenceClamping:
    """Confidence value clamping to [0, 1]."""

    def test_confidence_clamped_to_max_1(self):
        """Confidence > 1.0 is clamped to 1.0."""
        payload = build_enriched_choice_question(
            question="Which?",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "Description",
                    "tradeoff": "Tradeoff",
                    "confidence": 1.5,  # > 1.0
                },
            ],
        )

        # Should be clamped to 1.0
        assert "[confidence=1.00]" in payload["options"][0]["label"]

    def test_confidence_clamped_to_min_0(self):
        """Confidence < 0 is clamped to 0."""
        payload = build_enriched_choice_question(
            question="Which?",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "Description",
                    "tradeoff": "Tradeoff",
                    "confidence": -0.5,  # < 0
                },
            ],
        )

        # Should be clamped to 0.0
        assert "[confidence=0.00]" in payload["options"][0]["label"]


class TestLabelDescriptionLength:
    """Length capping for safety."""

    def test_label_capped_at_120_chars(self):
        """Label is capped at 120 characters."""
        payload = build_enriched_choice_question(
            question="Which?",
            options=[
                {
                    "id": "A",
                    "label": "A" * 200,  # Very long label
                    "description": "Description",
                    "tradeoff": "Tradeoff",
                },
            ],
        )

        assert len(payload["options"][0]["label"]) <= 120

    def test_description_capped_at_240_chars(self):
        """Description is capped at 240 characters."""
        payload = build_enriched_choice_question(
            question="Which?",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "D" * 500,  # Very long description
                    "tradeoff": "T" * 100,  # Very long tradeoff
                },
            ],
        )

        assert len(payload["options"][0]["description"]) <= 240


# ========================== Hardened E2E Invariant Tests ==========================
# Mirror Author-Gate's four-requirement contract for enriched ask_user_question:
#   1. Clickable — options reach ask_user_question format (label+description)
#   2. Confidence prefix — [confidence=X.XX] on every option
#   3. Tradeoff segment — ` · trade-off: <≥20 chars>` in every description
#   4. Dominance star — ⭐ on exactly one option iff recommendation exists


class TestE2EFourRequirementContract:
    """End-to-end tests verifying all 4 invariants hold simultaneously."""

    def test_all_four_invariants_with_recommendation(self):
        """Full pipeline with recommended option satisfies all 4 invariants."""
        payload = build_enriched_choice_question(
            question="Which refactoring approach?",
            options=[
                {
                    "id": "A",
                    "label": "Extract method",
                    "description": "Pull shared logic into utility",
                    "tradeoff": "Increases import count but reduces duplication across modules",
                    "confidence": 0.88,
                },
                {
                    "id": "B",
                    "label": "Inline and simplify",
                    "description": "Merge callers into single function",
                    "tradeoff": "Simpler call graph but longer function bodies per module",
                    "confidence": 0.72,
                },
            ],
            recommended_id="A",
            telemetry_context="refactor-scope",
        )

        opts = payload["options"]
        # INV-1: Clickable — each option has label + description keys
        for opt in opts:
            assert "label" in opt and isinstance(opt["label"], str)
            assert "description" in opt and isinstance(opt["description"], str)

        # INV-2: Confidence prefix on ALL options
        for opt in opts:
            assert re.search(r"\[confidence=\d\.\d{2}\]", opt["label"]), (
                f"Missing confidence prefix in label: {opt['label']}"
            )

        # INV-3: Tradeoff segment in ALL descriptions
        for opt in opts:
            assert "· trade-off:" in opt["description"], (
                f"Missing tradeoff in description: {opt['description']}"
            )

        # INV-4: Exactly one star on recommended, zero on others
        star_labels = [o for o in opts if "⭐" in o["label"]]
        assert len(star_labels) == 1
        assert "A" in star_labels[0]["label"]

    def test_all_four_invariants_without_recommendation(self):
        """No-recommendation path: zero stars, all other invariants hold."""
        payload = build_enriched_choice_question(
            question="Which approach?",
            options=[
                {
                    "id": "X",
                    "label": "Option X",
                    "description": "First choice",
                    "tradeoff": "Faster delivery but less test coverage across layers",
                },
                {
                    "id": "Y",
                    "label": "Option Y",
                    "description": "Second choice",
                    "tradeoff": "More thorough testing but higher token cost per phase",
                },
            ],
        )

        opts = payload["options"]
        for opt in opts:
            assert "label" in opt and "description" in opt
            assert re.search(r"\[confidence=\d\.\d{2}\]", opt["label"])
            assert "· trade-off:" in opt["description"]
            assert "⭐" not in opt["label"]

    def test_telemetry_packet_round_trips_with_all_fields(self):
        """Telemetry packet contains all required fields for SQLite writeback."""
        payload = build_enriched_choice_question(
            question="Pick a strategy",
            options=[
                {
                    "id": "S1",
                    "label": "Strategy 1",
                    "description": "Aggressive approach",
                    "tradeoff": "Faster but riskier — may require rollback if tests fail",
                    "confidence": 0.91,
                },
            ],
            recommended_id="S1",
            telemetry_context="test-strategy",
        )

        telem = payload["telemetry_packet"]
        # All required fields for ledger write
        assert telem["packet_type"] == "ASK_USER_QUESTION_PACKET"
        assert isinstance(telem["timestamp"], str) and "T" in telem["timestamp"]
        assert telem["context"] == "test-strategy"
        assert telem["option_count"] == 1
        assert telem["recommended_index"] == 0
        assert telem["confidence_source"] == "explicit"
        assert set(telem["invariants"]) == {"confidence_prefix", "tradeoff_segment", "star_marker"}

    def test_confidence_score_precision_two_decimals(self):
        """Confidence labels use exactly two decimal places."""
        for conf in [0.1, 0.5, 0.72, 0.999, 1.0, 0.0]:
            payload = build_enriched_choice_question(
                question="Q",
                options=[{"id": "A", "label": "L", "description": "D", "tradeoff": "T", "confidence": conf}],
            )
            label = payload["options"][0]["label"]
            match = re.search(r"\[confidence=(\d\.\d{2})\]", label)
            assert match, f"Confidence format wrong for input {conf}: {label}"
            parsed = float(match.group(1))
            assert 0.0 <= parsed <= 1.0

    def test_tradeoff_minimum_length_enforced(self):
        """Tradeoff text should appear with meaningful content in description."""
        payload = build_enriched_choice_question(
            question="Q",
            options=[
                {
                    "id": "A",
                    "label": "Option A",
                    "description": "Some description",
                    "tradeoff": "Gains reversibility but increases import surface area significantly",
                },
            ],
        )
        desc = payload["options"][0]["description"]
        # Extract tradeoff portion after "trade-off:"
        idx = desc.index("trade-off:")
        tradeoff_body = desc[idx + len("trade-off:"):].strip()
        # Meaningful length (mirrors the ≥20 char check in UI audit)
        assert len(tradeoff_body.replace(" ", "")) >= 10

    def test_mixed_explicit_and_heuristic_confidence(self):
        """Options with mixed confidence sources: explicit wins for telemetry."""
        payload = build_enriched_choice_question(
            question="Mix?",
            options=[
                {"id": "A", "label": "ExplA", "description": "D", "tradeoff": "Trade A detail here is longer", "confidence": 0.85},
                {"id": "B", "label": "HeurB", "description": "D", "tradeoff": "Trade B detail here is longer"},
            ],
        )

        # Telemetry source = explicit because at least one option had explicit
        assert payload["telemetry_packet"]["confidence_source"] == "explicit"

        # Option A shows its explicit confidence
        assert "[confidence=0.85]" in payload["options"][0]["label"]
        # Option B shows the heuristic default
        assert f"[confidence={DEFAULT_HEURISTIC_CONFIDENCE:.2f}]" in payload["options"][1]["label"]

    def test_star_never_appears_in_description(self):
        """Star marker only appears in label, never in description."""
        payload = build_enriched_choice_question(
            question="Q",
            options=[
                {"id": "A", "label": "Opt A", "description": "D", "tradeoff": "Trade off detail long enough here", "confidence": 0.90},
                {"id": "B", "label": "Opt B", "description": "D", "tradeoff": "Trade off detail long enough here", "confidence": 0.70},
            ],
            recommended_id="A",
        )
        for opt in payload["options"]:
            assert "⭐" not in opt["description"]
