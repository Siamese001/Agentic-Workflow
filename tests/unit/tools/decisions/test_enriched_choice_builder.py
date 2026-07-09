"""Tests for the canonical Codex request_user_input enriched choice builder."""

from __future__ import annotations

import re
from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from tools.decisions.enriched_choice_builder import (  # noqa: E402
    DEFAULT_HEURISTIC_CONFIDENCE,
    EnrichedOption,
    _validate_options,
    _validate_star_invariant,
    build_enriched_choice_question,
)


def _options() -> list[dict]:
    return [
        {
            "id": "A",
            "label": "Fast approach",
            "description": "Quick implementation",
            "pros": "Fastest path to a working fix",
            "cons": "Higher risk of edge-case misses",
            "tradeoff": "Fastest path but higher risk of edge-case misses",
            "confidence": 0.74,
        },
        {
            "id": "B",
            "label": "Safe approach",
            "description": "Conservative implementation",
            "pros": "Validates assumptions before editing",
            "cons": "Slower than the direct patch",
            "tradeoff": "Slower but validates all assumptions",
            "flip_condition": "the bug is isolated to one obvious line",
            "confidence": 0.88,
        },
    ]


class TestCanonicalOutput:
    def test_recommended_option_is_first_and_canonical(self):
        payload = build_enriched_choice_question(
            question="Which approach?",
            options=_options(),
            recommended_id="B",
            telemetry_context="branch-resolution",
        )

        opts = payload["options"]
        assert opts[0]["label"] == "B. Safe approach (Recommended)"
        assert opts[1]["label"] == "A. Fast approach"
        assert "⭐" not in opts[0]["label"]

        assert opts[0]["description"].startswith("[RECOMMENDED ⭐ confidence=0.88]")
        assert opts[1]["description"].startswith("[confidence=0.74]")
        for opt in opts:
            assert "Pros:" in opt["description"]
            assert "Cons:" in opt["description"]
            assert re.match(r"^\[(?:RECOMMENDED ⭐ )?confidence=\d\.\d{2}\]", opt["description"])
        assert "Flips if the bug is isolated to one obvious line." in opts[0]["description"]
        assert payload["tool_name"] == "functions.request_user_input"
        assert payload["tool_input"]["questions"] == payload["questions"]
        assert payload["questions"][0]["id"] == "branch_resolution"
        assert payload["questions"][0]["header"] == "branch"
        assert payload["questions"][0]["options"] == opts

    def test_no_recommendation_keeps_order_and_has_no_star(self):
        payload = build_enriched_choice_question(
            question="Pick one",
            options=_options(),
            recommended_id=None,
        )

        labels = [o["label"] for o in payload["options"]]
        assert labels == ["A. Fast approach", "B. Safe approach"]
        assert all("Recommended" not in label for label in labels)
        assert all("⭐" not in o["description"] for o in payload["options"])
        assert payload["telemetry_packet"]["recommended_index"] is None

    def test_legacy_tradeoff_derives_visible_pros_and_cons(self):
        payload = build_enriched_choice_question(
            question="Which target?",
            options=[
                {
                    "id": "A",
                    "label": "High impact",
                    "description": "Touch the shared module",
                    "tradeoff": "Higher impact but more complex blast radius",
                    "confidence": 0.81,
                },
                {
                    "id": "B",
                    "label": "Low risk",
                    "description": "Touch a leaf module",
                    "tradeoff": "Lower risk but less structural impact",
                    "confidence": 0.68,
                },
            ],
            recommended_id="A",
        )

        desc = payload["options"][0]["description"]
        assert "Pros: Higher impact." in desc
        assert "Cons: more complex blast radius." in desc


class TestConfidenceHandling:
    def test_explicit_confidence_preserved_in_description_and_telemetry(self):
        payload = build_enriched_choice_question(
            question="Q?",
            options=[_options()[0]],
            recommended_id="A",
        )

        assert "[RECOMMENDED ⭐ confidence=0.74]" in payload["options"][0]["description"]
        assert payload["telemetry_packet"]["confidence_source"] == "explicit"
        assert payload["telemetry_packet"]["confidence_score"] == 0.74

    def test_missing_confidence_uses_default_with_source_label(self):
        opt = {
            "id": "A",
            "label": "Option A",
            "description": "Description",
            "tradeoff": "Useful result but slower review",
        }
        payload = build_enriched_choice_question("Q?", [opt], recommended_id="A")

        expected = f"[RECOMMENDED ⭐ confidence={DEFAULT_HEURISTIC_CONFIDENCE:.2f}]"
        assert payload["options"][0]["description"].startswith(expected)
        assert payload["telemetry_packet"]["confidence_source"] == "heuristic_default"

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [(1.5, "1.00"), (-0.5, "0.00"), (0.834, "0.83")],
    )
    def test_confidence_is_clamped_and_rounded(self, raw, expected):
        opt = {
            "id": "A",
            "label": "Option A",
            "description": "Description",
            "tradeoff": "Useful result but slower review",
            "confidence": raw,
        }
        payload = build_enriched_choice_question("Q?", [opt], recommended_id="A")
        assert f"confidence={expected}" in payload["options"][0]["description"]


class TestTelemetryPacket:
    def test_packet_contains_learning_fields_and_options(self):
        payload = build_enriched_choice_question(
            question="Which approach?",
            options=_options(),
            recommended_id="B",
            telemetry_context="approach",
        )
        telemetry = payload["telemetry_packet"]

        assert telemetry["packet_type"] == "REQUEST_USER_INPUT_PACKET"
        assert telemetry["context"] == "approach"
        assert telemetry["question"] == "Which approach?"
        assert telemetry["option_count"] == 2
        assert telemetry["recommended_index"] == 0
        assert telemetry["confidence_score"] == 0.88
        assert telemetry["options"] == payload["options"]
        assert set(telemetry["invariants"]) == {
            "confidence_prefix",
            "pros_cons_segment",
            "star_marker",
            "recommended_label",
        }


class TestValidation:
    def test_missing_tradeoff_raises_valueerror(self):
        with pytest.raises(ValueError, match="tradeoff"):
            build_enriched_choice_question(
                question="Q?",
                options=[{"id": "A", "label": "Option A", "description": "Description"}],
            )

    def test_max_four_options(self):
        with pytest.raises(ValueError, match="Maximum 4 options"):
            build_enriched_choice_question(
                question="Q?",
                options=[
                    {"id": str(i), "label": f"Opt {i}", "description": "Desc", "tradeoff": "Trade"}
                    for i in range(5)
                ],
            )

    def test_no_options_fails(self):
        with pytest.raises(ValueError, match="At least one option"):
            build_enriched_choice_question("Q?", [])

    def test_duplicate_ids_fail(self):
        with pytest.raises(ValueError, match="unique"):
            _validate_options(
                [
                    {"id": "A", "label": "Opt A", "description": "Desc", "tradeoff": "Trade"},
                    {"id": "A", "label": "Opt A2", "description": "Desc2", "tradeoff": "Trade2"},
                ],
                recommended_id=None,
            )

    def test_invalid_recommended_id_fails(self):
        with pytest.raises(ValueError, match="recommended_id"):
            build_enriched_choice_question(
                question="Q?",
                options=[{"id": "A", "label": "Opt A", "description": "Desc", "tradeoff": "Trade"}],
                recommended_id="B",
            )

    def test_multiple_recommended_options_fails_star_invariant(self):
        enriched = [
            EnrichedOption(
                id="A",
                label="Option A",
                description="Desc A",
                tradeoff="Trade A",
                pros="Pro A",
                cons="Con A",
                confidence=0.8,
                confidence_source="explicit",
                is_recommended=True,
            ),
            EnrichedOption(
                id="B",
                label="Option B",
                description="Desc B",
                tradeoff="Trade B",
                pros="Pro B",
                cons="Con B",
                confidence=0.8,
                confidence_source="explicit",
                is_recommended=True,
            ),
        ]
        with pytest.raises(ValueError, match="Multiple recommended options"):
            _validate_star_invariant(enriched)


class TestLengthCaps:
    def test_label_capped_at_120_chars(self):
        opt = {
            "id": "A",
            "label": "A" * 200,
            "description": "Description",
            "tradeoff": "Useful result but slower review",
        }
        payload = build_enriched_choice_question("Q?", [opt], recommended_id="A")
        assert len(payload["options"][0]["label"]) <= 120

    def test_description_capped_at_240_chars(self):
        opt = {
            "id": "A",
            "label": "Option A",
            "description": "D" * 500,
            "tradeoff": "T" * 100,
        }
        payload = build_enriched_choice_question("Q?", [opt], recommended_id="A")
        assert len(payload["options"][0]["description"]) <= 240

    def test_required_recommended_fields_survive_description_cap(self):
        opt = {
            "id": "A",
            "label": "Store It",
            "description": "Verify the SQLite learning loop " * 20,
            "pros": "verifies confidence storage and future calibration " * 4,
            "cons": "uses a temporary ledger instead of production state " * 4,
            "tradeoff": "Stronger proof but more moving parts than a UI-only demo " * 4,
            "flip_condition": "you only want to inspect the visual prompt surface " * 4,
            "confidence": 0.84,
        }
        payload = build_enriched_choice_question("Q?", [opt], recommended_id="A")
        desc = payload["options"][0]["description"]

        assert len(desc) <= 240
        assert desc.startswith("[RECOMMENDED ⭐ confidence=0.84]")
        assert "Pros:" in desc
        assert "Cons:" in desc
        assert "Flips if" in desc
