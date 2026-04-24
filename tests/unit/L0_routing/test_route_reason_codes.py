"""W1b.P1 tests — RouteReasonCode enum + back-compat normalization."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.types.routing_artifact_types import (
    L0Route,
    RouteReasonCode,
    validate_reason_codes,
)


class TestEnumVocabulary:
    def test_enum_is_closed_and_stable(self) -> None:
        # W1b.P1 canonical set — 16 codes (14 initial + 2 R3 codes added to
        # align with check_r3_grounding_gate return values from W3.P1).
        # Additions require an ADR.
        expected = {
            "d1_exact_hit",
            "d2_semantic_hit",
            "d3_grounding_required",
            "d3_coverage_below_floor",
            "below_grounding_threshold",
            "no_grounding_signal",
            "d4_action_required",
            "d4_write_scope",
            "r5_low_confidence",
            "r5_ood_detected",
            "r5_budget_exceeded",
            "r5_circuit_breaker_open",
            "r5_clarification_needed",
            "r5_toxicity_flagged",
            "gate_hit",
            "pass_through",
        }
        actual = {code.value for code in RouteReasonCode}
        assert actual == expected

    def test_enum_is_str_subclass(self) -> None:
        # This is the keystone back-compat property — str-enum members
        # compare equal to their .value string.
        assert RouteReasonCode.D1_EXACT_HIT == "d1_exact_hit"
        assert ("d1_exact_hit",) == (RouteReasonCode.D1_EXACT_HIT.value,)

    def test_json_serializable(self) -> None:
        import json

        serialized = json.dumps([RouteReasonCode.R5_LOW_CONFIDENCE.value])
        assert serialized == '["r5_low_confidence"]'


class TestValidateReasonCodes:
    def test_plain_string_passes_through_by_default(self) -> None:
        result = validate_reason_codes(("d1_exact_hit",))
        assert result == ("d1_exact_hit",)

    def test_enum_member_normalized_to_string(self) -> None:
        result = validate_reason_codes((RouteReasonCode.D2_SEMANTIC_HIT,))
        assert result == ("d2_semantic_hit",)
        assert all(isinstance(x, str) for x in result)

    def test_mixed_tuple_accepted(self) -> None:
        result = validate_reason_codes(
            (RouteReasonCode.D1_EXACT_HIT, "gate_hit"),
        )
        assert result == ("d1_exact_hit", "gate_hit")

    def test_unknown_string_accepted_when_strict_false(self) -> None:
        # Default non-strict — preserves back-compat for any legacy
        # free-form reason codes still in flight.
        result = validate_reason_codes(("legacy_untyped_code",))
        assert result == ("legacy_untyped_code",)

    def test_unknown_string_rejected_when_strict_true(self) -> None:
        with pytest.raises(ValueError, match="not in the closed RouteReasonCode"):
            validate_reason_codes(("nonsense",), strict=True)

    def test_non_string_non_enum_always_rejected(self) -> None:
        with pytest.raises(ValueError, match="must be str or RouteReasonCode"):
            validate_reason_codes((42,))  # type: ignore[arg-type]

    def test_empty_tuple_is_valid(self) -> None:
        assert validate_reason_codes(()) == ()


class TestRouteGatesBackCompat:
    """The existing invariant test expects raw-string reason_codes. Verify
    our change preserves that equality contract."""

    def test_d1_reason_code_still_equals_literal_tuple(self) -> None:
        # This is exactly what the existing test_route_gates_v9_invariants
        # asserts: ``contract["reason_codes"] == ("d1_exact_hit",)``.
        emitted = (RouteReasonCode.D1_EXACT_HIT.value,)
        assert emitted == ("d1_exact_hit",)

    def test_d2_reason_code_still_equals_literal_tuple(self) -> None:
        emitted = (RouteReasonCode.D2_SEMANTIC_HIT.value,)
        assert emitted == ("d2_semantic_hit",)

    def test_l0_route_enum_still_intact(self) -> None:
        # Tangential sanity — W1b should not have perturbed L0Route.
        assert L0Route.R1A.value == "R1A"
        assert L0Route.R1B.value == "R1B"
