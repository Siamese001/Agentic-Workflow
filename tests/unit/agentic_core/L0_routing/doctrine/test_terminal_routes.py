"""Unit tests for agentic_core.L0_routing.doctrine.terminal_routes.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
``terminal_routes`` (03.3) realizes R1A/R1B/R5 terminal route decisions, HITL
posture, and the terminal [RET] packet. All are frozen dataclasses with strict
``__post_init__`` validation raising ``DoctrineContractError`` (a ValueError
subclass). Coverage hits enum value sets, every constructible defaults path,
the validators, and the hard-no invariants doctrine encodes.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.doctrine import DoctrineContractError
from agentic_core.L0_routing.doctrine.terminal_routes import (
    ExactCacheRouteDecision,
    FallbackRouteDecision,
    HITLPostureAnnotation,
    SafeResponseType,
    SemanticCacheRouteDecision,
    TerminalExecutionForm,
    TerminalRetPacket,
)


def _exact(**overrides: object) -> ExactCacheRouteDecision:
    base: dict[str, object] = {
        "cache_key": "ck",
        "normalized_request_hash": "nrh",
        "prior_answer_ref": "ans",
        "prior_policy_hash": "ph1",
        "current_policy_hash": "ph1",
        "freshness_status": "fresh",
        "tenant_scope_status": "ok",
        "schema_compatibility_status": "ok",
        "source_snapshot_status": "ok",
        "cache_hit_basis": "exact_match",
        "exact_cache_guard_receipt": "guard",
        "ret_packet_ref": "ret",
    }
    base.update(overrides)
    return ExactCacheRouteDecision(**base)  # type: ignore[arg-type]


def _semantic(**overrides: object) -> SemanticCacheRouteDecision:
    base: dict[str, object] = {
        "semantic_match_id": "sm",
        "query_vec_model_id": "bge",
        "cached_query_ref": "q",
        "cached_answer_ref": "a",
        "similarity_score": 0.92,
        "calibrated_threshold": 0.85,
        "task_class_compatibility": "ok",
        "output_contract_compatibility": "ok",
        "freshness_risk_status": "low",
        "source_specificity_risk_status": "low",
        "policy_compatibility_status": "ok",
        "tenant_scope_status": "ok",
        "semantic_cache_guard_receipt": "guard",
        "ret_packet_ref": "ret",
    }
    base.update(overrides)
    return SemanticCacheRouteDecision(**base)  # type: ignore[arg-type]


def _ret(**overrides: object) -> TerminalRetPacket:
    base: dict[str, object] = {
        "request_id": "rq",
        "run_id": "rn",
        "trace_root": "tr",
        "route_id": "R1A_EXACT_CACHE",
        "route_digest_ref": "rd",
        "policy_hash": "ph",
        "blueprint_hash": "bh",
        "replay_key": "rk",
        "reason_codes": ("ok",),
        "confidence": 0.9,
        "support_status": "supported",
        "freshness_status": "fresh",
        "tenant_scope_status": "ok",
    }
    base.update(overrides)
    return TerminalRetPacket(**base)  # type: ignore[arg-type]


class TestEnums:
    def test_terminal_execution_form_single_member(self) -> None:
        assert {f.value for f in TerminalExecutionForm} == {"TERMINAL_SHORTCIRCUIT"}

    def test_safe_response_type_members(self) -> None:
        assert {s.value for s in SafeResponseType} == {
            "CLARIFY",
            "ABSTAIN",
            "REFUSE",
            "SAFE_PARTIAL",
            "UNSUPPORTED_SOURCE",
            "POLICY_SAFE_EXPLANATION",
        }


class TestExactCacheRouteDecision:
    def test_construct_defaults(self) -> None:
        d = _exact()
        assert d.route_id == "R1A_EXACT_CACHE"
        assert d.execution_form is TerminalExecutionForm.TERMINAL_SHORTCIRCUIT
        assert d.prior_evidence_contract_ref == ""

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _exact().cache_key = "x"  # type: ignore[misc]

    def test_empty_required_field_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="must be non-empty"):
            _exact(cache_key="")

    def test_bad_route_id_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="must be R1A_EXACT_CACHE"):
            _exact(route_id="R5_FALLBACK")

    def test_policy_compatible_basis_across_mismatched_hashes_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="policy_compatible"):
            _exact(prior_policy_hash="ph1", current_policy_hash="ph2", cache_hit_basis="policy_compatible")

    def test_error_is_value_error_subclass(self) -> None:
        with pytest.raises(ValueError):
            _exact(cache_key="")


class TestSemanticCacheRouteDecision:
    def test_construct_defaults(self) -> None:
        d = _semantic()
        assert d.route_id == "R1B_SEMANTIC_CACHE"

    @pytest.mark.parametrize("bad", [-0.1, 1.1, float("nan")])
    def test_out_of_range_similarity_raises(self, bad: float) -> None:
        with pytest.raises(DoctrineContractError):
            _semantic(similarity_score=bad)

    def test_bool_similarity_rejected(self) -> None:
        with pytest.raises(DoctrineContractError, match="must be float"):
            _semantic(similarity_score=True)

    def test_similarity_below_threshold_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="below calibrated_threshold"):
            _semantic(similarity_score=0.5, calibrated_threshold=0.85)

    def test_similarity_equal_threshold_ok(self) -> None:
        assert _semantic(similarity_score=0.85, calibrated_threshold=0.85).similarity_score == 0.85


class TestFallbackRouteDecision:
    def test_construct_defaults(self) -> None:
        d = FallbackRouteDecision(
            safe_response_type=SafeResponseType.ABSTAIN,
            reason_codes=("insufficient_evidence",),
            fallback_guard_receipt="g",
            ret_packet_ref="r",
        )
        assert d.route_id == "R5_FALLBACK"
        assert d.fallback_chain_terminal_entry == "R5_FALLBACK"

    def test_non_enum_safe_response_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="must be SafeResponseType"):
            FallbackRouteDecision(
                safe_response_type="ABSTAIN",  # type: ignore[arg-type]
                reason_codes=("x",),
                fallback_guard_receipt="g",
                ret_packet_ref="r",
            )

    def test_empty_reason_codes_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="at least one reason_code"):
            FallbackRouteDecision(
                safe_response_type=SafeResponseType.REFUSE,
                reason_codes=(),
                fallback_guard_receipt="g",
                ret_packet_ref="r",
            )

    def test_bad_terminal_entry_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="fallback_chain_terminal_entry must be R5_FALLBACK"):
            FallbackRouteDecision(
                safe_response_type=SafeResponseType.REFUSE,
                reason_codes=("x",),
                fallback_guard_receipt="g",
                ret_packet_ref="r",
                fallback_chain_terminal_entry="WRONG",
            )


class TestHITLPostureAnnotation:
    def test_construct_defaults(self) -> None:
        a = HITLPostureAnnotation(hitl_required=True, hitl_reason_codes=("needs_human",))
        assert a.re_clearance_required is True
        assert a.hitl_not_sovereign_assertion is True
        assert a.human_input_origin_trust == "untrusted_human_data"

    def test_required_without_reason_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="at least one reason_code"):
            HITLPostureAnnotation(hitl_required=True, hitl_reason_codes=())

    def test_non_sovereign_assertion_false_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="must be True"):
            HITLPostureAnnotation(
                hitl_required=False,
                hitl_reason_codes=(),
                hitl_not_sovereign_assertion=False,
            )

    def test_bad_origin_trust_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="untrusted_human_data"):
            HITLPostureAnnotation(
                hitl_required=False,
                hitl_reason_codes=(),
                human_input_origin_trust="trusted",
            )

    def test_non_bool_field_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="must be bool"):
            HITLPostureAnnotation(
                hitl_required="yes",  # type: ignore[arg-type]
                hitl_reason_codes=("x",),
            )


class TestTerminalRetPacket:
    @pytest.mark.parametrize("route_id", ["R1A_EXACT_CACHE", "R1B_SEMANTIC_CACHE", "R5_FALLBACK"])
    def test_valid_route_ids(self, route_id: str) -> None:
        assert _ret(route_id=route_id).route_id == route_id

    def test_bad_route_id_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="must be R1A/R1B/R5"):
            _ret(route_id="R3_GENERATE")

    def test_optional_refs_allow_empty(self) -> None:
        assert _ret(safe_response_ref="", cached_answer_ref="").safe_response_ref == ""

    def test_assertion_false_raises(self) -> None:
        with pytest.raises(DoctrineContractError, match="assertions must all be True"):
            _ret(no_l2_execution_assertion=False)

    @pytest.mark.parametrize("bad", [-0.1, 1.5, float("nan")])
    def test_confidence_out_of_range_raises(self, bad: float) -> None:
        with pytest.raises(DoctrineContractError, match="confidence must be in"):
            _ret(confidence=bad)

    def test_confidence_bool_rejected(self) -> None:
        with pytest.raises(DoctrineContractError, match="confidence must be float"):
            _ret(confidence=True)

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _ret().run_id = "x"  # type: ignore[misc]
