"""Exhaustive edge-case coverage for L0 doctrine contracts.

For every public contract type this file verifies:

- type guards (wrong type → DoctrineContractError)
- empty-required-string rejection
- oversize-string rejection (>512)
- oversize-tuple rejection (>64)
- bool-as-int rejection on int fields
- NaN / out-of-range rejection on float fields
- wrong-enum-type substitution rejection
- every "must be True" assertion flipped to False raises
- every entry-law / coherence rule

The goal is "no requirement passes by ⚠ PARTIAL" — every doctrine post_init
invariant has at least one direct edge-case test.

Constitutional compliance: no ``except Exception``, no I/O, no subprocess.
"""

from __future__ import annotations

import math

import pytest

from agentic_core.L0_routing.doctrine import DoctrineContractError
from agentic_core.L0_routing.doctrine.contracts_l0_1 import (
    CandidateRouteId,
    L1ValidationSummary,
    PreflightStatus,
    RouteCandidateFrame,
    RouteDecisionInput,
    RouteDiscriminatorFrame,
    RouteInputAuditReceipt,
    RoutePreflightStatusReport,
    SourceAvailabilitySnapshot,
)
from agentic_core.L0_routing.doctrine.contracts_l0_2 import (
    ConfidenceClass,
    ExecutionFormSelected,
    FixedDecisionOrderReceipt,
    RouteScoreVector,
    RouteSelectionReceipt,
)
from agentic_core.L0_routing.doctrine.handoffs import (
    C0Budget,
    CapabilityClass,
    CitationMode,
    DownstreamLayerRequirementMap,
    FreshnessClass,
    PTCPermissionMetadata,
    R3GroundedReadHandoff,
    R3R4ArgumentGroundingHandoff,
    R4SingleActionHandoff,
    ReversibilityClass,
    SandboxClass,
    SideEffectClass,
    SupportTarget,
)
from agentic_core.L0_routing.doctrine.preflight import run_l0_preflight
from agentic_core.L0_routing.doctrine.replay import (
    RouteReplayManifest,
    verify_replay,
)
from agentic_core.L0_routing.doctrine.selector import select_route
from agentic_core.L0_routing.doctrine.telemetry import (
    RouteSpanAttributes,
    RouteTelemetryEvent,
)
from agentic_core.L0_routing.doctrine.terminal_routes import (
    ExactCacheRouteDecision,
    FallbackRouteDecision,
    HITLPostureAnnotation,
    SafeResponseType,
    SemanticCacheRouteDecision,
    TerminalRetPacket,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


_OVERSIZE_STR = "x" * 513
_LARGE_TUPLE = tuple(f"item-{i}" for i in range(70))


def _valid_l1_validation() -> L1ValidationSummary:
    return L1ValidationSummary()


def _valid_decision_input(**overrides: object) -> RouteDecisionInput:
    base: dict[str, object] = dict(
        request_id="rq",
        run_id="rn",
        session_id="ss",
        trace_root="tr",
        tenant_id="t",
        policy_hash="p",
        blueprint_hash="b",
        replay_key="rk",
        l1_plan_id="lp",
        l1_plan_digest="ld",
        task_spec="What does the policy say about retention?",
        query_spec="policy retention",
        validation_summary=_valid_l1_validation(),
    )
    base.update(overrides)
    return RouteDecisionInput(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 03.1 RouteDecisionInput edge cases
# ---------------------------------------------------------------------------


class TestRouteDecisionInputEdges:

    @pytest.mark.parametrize(
        "field",
        [
            "request_id",
            "run_id",
            "trace_root",
            "tenant_id",
            "policy_hash",
            "blueprint_hash",
            "replay_key",
            "l1_plan_id",
            "l1_plan_digest",
            "task_spec",
            "query_spec",
        ],
    )
    def test_empty_required_field_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_decision_input(**{field: ""})

    @pytest.mark.parametrize(
        "field",
        [
            "request_id",
            "tenant_id",
            "policy_hash",
            "blueprint_hash",
            "task_spec",
            "query_spec",
        ],
    )
    def test_oversize_required_field_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_decision_input(**{field: _OVERSIZE_STR})

    @pytest.mark.parametrize(
        "field",
        ["request_id", "tenant_id", "policy_hash", "task_spec"],
    )
    def test_wrong_type_required_field_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_decision_input(**{field: 123})

    def test_validation_summary_wrong_type_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_decision_input(validation_summary="not-a-summary")

    @pytest.mark.parametrize(
        "field",
        [
            "assumptions_and_gaps",
            "caller_scope_baseline",
            "visible_source_handles",
            "source_expectations",
            "risk_hints",
            "freshness_hints",
            "artifact_requirements",
        ],
    )
    def test_oversize_tuple_field_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_decision_input(**{field: _LARGE_TUPLE})

    @pytest.mark.parametrize(
        "field",
        ["assumptions_and_gaps", "visible_source_handles", "source_expectations"],
    )
    def test_non_tuple_field_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_decision_input(**{field: ["not", "a", "tuple"]})

    def test_tuple_with_int_element_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_decision_input(visible_source_handles=("ok", 42, "ok2"))

    def test_tuple_with_empty_element_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_decision_input(visible_source_handles=("ok", "", "ok2"))


class TestL1ValidationSummaryEdges:

    @pytest.mark.parametrize(
        "field",
        [
            "no_retrieval_performed",
            "no_execution_performed",
            "no_write_performed",
            "no_final_route_authority_claimed",
        ],
    )
    def test_non_bool_raises(self, field: str) -> None:
        kwargs: dict[str, object] = {
            "no_retrieval_performed": True,
            "no_execution_performed": True,
            "no_write_performed": True,
            "no_final_route_authority_claimed": True,
        }
        kwargs[field] = "yes"
        with pytest.raises(DoctrineContractError):
            L1ValidationSummary(**kwargs)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 03.1 RouteDiscriminatorFrame edge cases (all 25 fields are bool)
# ---------------------------------------------------------------------------


class TestRouteDiscriminatorFrameEdges:

    @pytest.mark.parametrize(
        "field",
        [
            "asks_for_factual_claim",
            "asks_for_source_grounding",
            "asks_for_external_action",
            "asks_for_durable_mutation",
            "likely_requires_l3",
            "likely_requires_hitl",
            "likely_ptc_capable_downstream",
        ],
    )
    def test_non_bool_field_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            RouteDiscriminatorFrame(**{field: "true"})  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 03.1 RoutePreflightStatusReport edge cases
# ---------------------------------------------------------------------------


def _valid_preflight_status(**overrides: object) -> RoutePreflightStatusReport:
    base: dict[str, object] = dict(
        preflight_id="pf-1",
        status=PreflightStatus.ROUTE_READY,
        eligible_for_route_selection=True,
        blocked_reason="",
        policy_status="ok",
        tenant_scope_status="ok",
        acl_scope_status="ok",
        route_input_completeness="complete",
        missing_critical_fields=(),
        invalid_authority_claims=(),
        stale_policy_or_blueprint_flags=(),
        source_handle_status=(),
        action_scope_status="ok",
        egress_scope_status="ok",
        preflight_hash="h",
    )
    base.update(overrides)
    return RoutePreflightStatusReport(**base)  # type: ignore[arg-type]


class TestRoutePreflightStatusReportEdges:

    def test_status_ready_with_eligible_false_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_preflight_status(eligible_for_route_selection=False)

    def test_status_blocked_with_eligible_true_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_preflight_status(
                status=PreflightStatus.ROUTE_BLOCKED_POLICY,
                eligible_for_route_selection=True,
            )

    def test_status_wrong_enum_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_preflight_status(status="ROUTE_READY")  # raw string, not enum


# ---------------------------------------------------------------------------
# 03.1 RouteCandidateFrame edge cases
# ---------------------------------------------------------------------------


class TestRouteCandidateFrameEdges:

    def test_empty_candidates_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            RouteCandidateFrame(route_candidates=())

    def test_oversize_candidates_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            RouteCandidateFrame(
                route_candidates=tuple([CandidateRouteId.R5_FALLBACK] * 70),
            )

    def test_non_enum_in_candidates_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            RouteCandidateFrame(
                route_candidates=("R5_FALLBACK",),  # raw string, not enum
            )

    def test_non_tuple_candidates_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            RouteCandidateFrame(route_candidates=[CandidateRouteId.R5_FALLBACK])  # type: ignore[arg-type]

    def test_wrong_discriminator_type_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            RouteCandidateFrame(
                route_candidates=(CandidateRouteId.R5_FALLBACK,),
                discriminators="not-a-frame",  # type: ignore[arg-type]
            )

    def test_wrong_source_availability_type_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            RouteCandidateFrame(
                route_candidates=(CandidateRouteId.R5_FALLBACK,),
                source_availability="not-a-snapshot",  # type: ignore[arg-type]
            )

    def test_wrong_preflight_status_type_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            RouteCandidateFrame(
                route_candidates=(CandidateRouteId.R5_FALLBACK,),
                preflight_status="ROUTE_READY",  # type: ignore[arg-type]
            )


# ---------------------------------------------------------------------------
# 03.1 RouteInputAuditReceipt edge cases
# ---------------------------------------------------------------------------


def _valid_receipt(**overrides: object) -> RouteInputAuditReceipt:
    base: dict[str, object] = dict(
        receipt_id="r",
        request_id="rq",
        run_id="rn",
        trace_root="tr",
        l1_plan_id="lp",
        preflight_id="pf",
        candidate_count=2,
        blocked_count=0,
        fail_closed_reason="",
        receipt_hash="h",
    )
    base.update(overrides)
    return RouteInputAuditReceipt(**base)  # type: ignore[arg-type]


class TestRouteInputAuditReceiptEdges:

    def test_negative_candidate_count_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_receipt(candidate_count=-1)

    def test_negative_blocked_count_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_receipt(blocked_count=-1)

    def test_bool_as_count_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_receipt(candidate_count=True)


# ---------------------------------------------------------------------------
# 03.1 SourceAvailabilitySnapshot edge cases
# ---------------------------------------------------------------------------


class TestSourceAvailabilitySnapshotEdges:

    def test_with_hash_is_deterministic(self) -> None:
        a = SourceAvailabilitySnapshot(
            source_classes_expected=("policy", "doc"),
            source_classes_available=("policy",),
        ).with_hash()
        b = SourceAvailabilitySnapshot(
            source_classes_expected=("policy", "doc"),
            source_classes_available=("policy",),
        ).with_hash()
        assert a.availability_hash == b.availability_hash

    def test_oversize_tuple_field_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            SourceAvailabilitySnapshot(source_classes_expected=_LARGE_TUPLE)


# ---------------------------------------------------------------------------
# 03.2 RouteScoreVector edge cases
# ---------------------------------------------------------------------------


class TestRouteScoreVectorEdges:

    @pytest.mark.parametrize(
        "field",
        [
            "exact_cache_score",
            "semantic_cache_score",
            "grounding_need_score",
            "single_action_score",
            "managed_workflow_score",
            "fallback_need_score",
            "hitl_need_score",
            "freshness_risk",
            "support_risk",
            "action_risk",
            "mutation_risk",
            "egress_risk",
            "ambiguity_risk",
            "tenant_acl_risk",
            "cost_risk",
            "slo_risk",
        ],
    )
    def test_score_above_one_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            RouteScoreVector(**{field: 1.5})

    @pytest.mark.parametrize("field", ["exact_cache_score", "freshness_risk"])
    def test_score_negative_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            RouteScoreVector(**{field: -0.1})

    @pytest.mark.parametrize("field", ["exact_cache_score", "support_risk"])
    def test_score_nan_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            RouteScoreVector(**{field: math.nan})

    def test_confidence_class_wrong_type_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            RouteScoreVector(confidence_class="HIGH")  # type: ignore[arg-type]

    def test_score_bool_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            RouteScoreVector(exact_cache_score=True)  # bool blocked


# ---------------------------------------------------------------------------
# 03.2 FixedDecisionOrderReceipt + RouteSelectionReceipt edges
# ---------------------------------------------------------------------------


def _valid_fixed_order(**overrides: object) -> FixedDecisionOrderReceipt:
    base: dict[str, object] = dict(
        decision_order_version="03.2-v1",
        evaluated_steps=("0_invalid_or_unsafe", "7_fallback"),
        first_passing_step="7_fallback",
        skipped_steps_with_reasons=(),
        blocked_routes=(),
        selected_route_id=CandidateRouteId.R5_FALLBACK,
        selected_execution_form=ExecutionFormSelected.TERMINAL_SHORTCIRCUIT,
        deterministic_order_hash="h",
    )
    base.update(overrides)
    return FixedDecisionOrderReceipt(**base)  # type: ignore[arg-type]


class TestFixedDecisionOrderReceiptEdges:

    def test_route_id_wrong_enum_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_fixed_order(selected_route_id="R5_FALLBACK")

    def test_execution_form_wrong_enum_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_fixed_order(selected_execution_form="TERMINAL_SHORTCIRCUIT")


def _valid_selection_receipt(**overrides: object) -> RouteSelectionReceipt:
    base: dict[str, object] = dict(
        route_selection_id="rs-1",
        request_id="rq",
        run_id="rn",
        trace_root="tr",
        l1_plan_id="lp",
        preflight_id="pf",
        selected_route_id=CandidateRouteId.R5_FALLBACK,
        selected_execution_form=ExecutionFormSelected.TERMINAL_SHORTCIRCUIT,
        confidence=0.5,
        confidence_class=ConfidenceClass.LOW,
        reason_codes=(),
        route_score_vector=RouteScoreVector(),
        cheapest_safe_route_rationale="r",
        rejected_route_reasons=(),
        fallback_chain_hint=(),
        downstream_required_layers=(),
        fixed_order_receipt=_valid_fixed_order(),
        route_selection_hash="h",
    )
    base.update(overrides)
    return RouteSelectionReceipt(**base)  # type: ignore[arg-type]


class TestRouteSelectionReceiptEdges:

    def test_confidence_above_one_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_selection_receipt(confidence=1.5)

    def test_confidence_negative_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_selection_receipt(confidence=-0.1)

    def test_confidence_nan_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_selection_receipt(confidence=math.nan)

    def test_route_id_disagrees_with_fixed_order_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_selection_receipt(
                selected_route_id=CandidateRouteId.R3_SIMPLE_GROUNDED_READ,
            )  # fixed_order says R5

    def test_score_vector_wrong_type_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_selection_receipt(route_score_vector="not-a-vector")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 03.2 select_route public-API edges
# ---------------------------------------------------------------------------


class TestSelectRouteAPIEdges:

    def test_non_frame_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            select_route(
                "not-a-frame",  # type: ignore[arg-type]
                request_id="r",
                run_id="rn",
                trace_root="tr",
                l1_plan_id="lp",
                preflight_id="pf",
            )

    def test_empty_request_id_raises(self) -> None:
        frame = RouteCandidateFrame(route_candidates=(CandidateRouteId.R5_FALLBACK,))
        with pytest.raises(DoctrineContractError):
            select_route(
                frame,
                request_id="",
                run_id="rn",
                trace_root="tr",
                l1_plan_id="lp",
                preflight_id="pf",
            )

    def test_run_l0_preflight_non_input_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            run_l0_preflight("not-an-input")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 03.3 Terminal route edges
# ---------------------------------------------------------------------------


def _valid_exact_cache(**overrides: object) -> ExactCacheRouteDecision:
    base: dict[str, object] = dict(
        cache_key="ck",
        normalized_request_hash="nrh",
        prior_answer_ref="ans",
        prior_policy_hash="ph",
        current_policy_hash="ph",
        freshness_status="ok",
        tenant_scope_status="ok",
        schema_compatibility_status="ok",
        source_snapshot_status="ok",
        cache_hit_basis="strict",
        exact_cache_guard_receipt="rcpt",
        ret_packet_ref="ret",
    )
    base.update(overrides)
    return ExactCacheRouteDecision(**base)  # type: ignore[arg-type]


class TestExactCacheRouteDecisionEdges:

    @pytest.mark.parametrize(
        "field",
        [
            "cache_key",
            "normalized_request_hash",
            "prior_answer_ref",
            "freshness_status",
        ],
    )
    def test_empty_required_field_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_exact_cache(**{field: ""})

    def test_non_default_route_id_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_exact_cache(route_id="R3_SIMPLE_GROUNDED_READ")


def _valid_semantic_cache(**overrides: object) -> SemanticCacheRouteDecision:
    base: dict[str, object] = dict(
        semantic_match_id="sm",
        query_vec_model_id="m",
        cached_query_ref="q",
        cached_answer_ref="a",
        similarity_score=0.95,
        calibrated_threshold=0.85,
        task_class_compatibility="ok",
        output_contract_compatibility="ok",
        freshness_risk_status="ok",
        source_specificity_risk_status="ok",
        policy_compatibility_status="ok",
        tenant_scope_status="ok",
        semantic_cache_guard_receipt="rcpt",
        ret_packet_ref="ret",
    )
    base.update(overrides)
    return SemanticCacheRouteDecision(**base)  # type: ignore[arg-type]


class TestSemanticCacheRouteDecisionEdges:

    @pytest.mark.parametrize(
        "field,value",
        [
            ("similarity_score", 1.5),
            ("similarity_score", -0.1),
            ("similarity_score", math.nan),
            ("calibrated_threshold", 1.5),
            ("calibrated_threshold", math.nan),
        ],
    )
    def test_score_or_threshold_out_of_unit_raises(
        self, field: str, value: float
    ) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_semantic_cache(**{field: value})

    def test_similarity_below_threshold_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_semantic_cache(similarity_score=0.5, calibrated_threshold=0.9)

    def test_score_bool_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_semantic_cache(similarity_score=True)


class TestFallbackRouteDecisionEdges:

    def test_wrong_safe_response_type_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            FallbackRouteDecision(
                safe_response_type="ABSTAIN",  # type: ignore[arg-type]
                reason_codes=("R",),
                fallback_guard_receipt="rcpt",
                ret_packet_ref="ret",
            )

    def test_oversize_reason_codes_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            FallbackRouteDecision(
                safe_response_type=SafeResponseType.ABSTAIN,
                reason_codes=tuple(f"r-{i}" for i in range(40)),
                fallback_guard_receipt="rcpt",
                ret_packet_ref="ret",
            )

    def test_non_default_route_id_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            FallbackRouteDecision(
                safe_response_type=SafeResponseType.ABSTAIN,
                reason_codes=("R",),
                fallback_guard_receipt="rcpt",
                ret_packet_ref="ret",
                route_id="R5_OTHER",
            )

    def test_wrong_fallback_chain_terminal_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            FallbackRouteDecision(
                safe_response_type=SafeResponseType.ABSTAIN,
                reason_codes=("R",),
                fallback_guard_receipt="rcpt",
                ret_packet_ref="ret",
                fallback_chain_terminal_entry="R3_SIMPLE_GROUNDED_READ",
            )


class TestHITLPostureAnnotationEdges:

    def test_required_with_no_reasons_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            HITLPostureAnnotation(hitl_required=True, hitl_reason_codes=())

    def test_origin_trust_must_be_untrusted(self) -> None:
        with pytest.raises(DoctrineContractError):
            HITLPostureAnnotation(
                hitl_required=False,
                hitl_reason_codes=(),
                human_input_origin_trust="trusted",
            )


class TestTerminalRetPacketEdges:

    def _valid(self, **overrides: object) -> TerminalRetPacket:
        base: dict[str, object] = dict(
            request_id="rq",
            run_id="rn",
            trace_root="tr",
            route_id="R1A_EXACT_CACHE",
            route_digest_ref="rd",
            policy_hash="p",
            blueprint_hash="b",
            replay_key="rk",
            reason_codes=("ok",),
            confidence=1.0,
            support_status="ok",
            freshness_status="ok",
            tenant_scope_status="ok",
        )
        base.update(overrides)
        return TerminalRetPacket(**base)  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "field",
        ["exit_review_required", "no_l2_execution_assertion", "no_l4_write_assertion"],
    )
    def test_must_be_true_assertions(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            self._valid(**{field: False})

    @pytest.mark.parametrize(
        "value", [1.5, -0.1, math.nan]
    )
    def test_confidence_out_of_unit_raises(self, value: float) -> None:
        with pytest.raises(DoctrineContractError):
            self._valid(confidence=value)


# ---------------------------------------------------------------------------
# 03.4 Handoff edges
# ---------------------------------------------------------------------------


def _valid_c0_budget(**overrides: object) -> C0Budget:
    base: dict[str, object] = dict(
        max_k=10,
        max_graph_hops=1,
        max_refine_attempts=1,
        max_latency_ms=5000,
        max_token_context=4000,
    )
    base.update(overrides)
    return C0Budget(**base)  # type: ignore[arg-type]


class TestC0BudgetEdges:

    def test_max_k_zero_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_c0_budget(max_k=0)

    def test_max_token_context_zero_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_c0_budget(max_token_context=0)

    def test_negative_max_latency_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_c0_budget(max_latency_ms=-1)

    def test_bool_as_int_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_c0_budget(max_k=True)


def _valid_r3(**overrides: object) -> R3GroundedReadHandoff:
    base: dict[str, object] = dict(
        request_id="r",
        run_id="rn",
        trace_root="tr",
        l1_plan_ref="lp",
        query_spec_ref="qs",
        task_spec_ref="ts",
        support_target=SupportTarget.POLICY_CLAUSE,
        citation_mode=CitationMode.INLINE,
        freshness_class=FreshnessClass.STATIC,
        tenant_scope="t",
        acl_scope=("read",),
        region_scope="us",
        c0_budget=_valid_c0_budget(),
        fallback_chain=("R5_FALLBACK",),
        route_digest_ref="rd",
    )
    base.update(overrides)
    return R3GroundedReadHandoff(**base)  # type: ignore[arg-type]


class TestR3GroundedReadHandoffEdges:

    def test_l3_required_true_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_r3(l3_required=True)

    def test_l2_required_false_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_r3(l2_required=False)

    def test_wrong_support_target_type_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_r3(support_target="POLICY_CLAUSE")

    def test_wrong_citation_mode_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_r3(citation_mode="INLINE")

    def test_wrong_route_id_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_r3(route_id="R4_SINGLE_ACTION")

    def test_oversize_fallback_chain_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_r3(fallback_chain=tuple(f"f-{i}" for i in range(40)))


def _valid_r4(**overrides: object) -> R4SingleActionHandoff:
    base: dict[str, object] = dict(
        action_spec_ref="as",
        action_kind="create",
        side_effect_class=SideEffectClass.LOCAL_REVERSIBLE,
        reversibility_class=ReversibilityClass.REVERSIBLE_LOCAL,
        capability_class=CapabilityClass.ACTION,
        sandbox_class=SandboxClass.PROCESS_SANDBOX,
        capability_token_required=True,
        sandbox_envelope_required=True,
        action_args_status="complete",
        hitl_required=False,
        uwg_required_if_write=False,
        fallback_chain=("R5_FALLBACK",),
    )
    base.update(overrides)
    return R4SingleActionHandoff(**base)  # type: ignore[arg-type]


class TestR4SingleActionHandoffEdges:

    def test_no_capability_token_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_r4(capability_token_required=False)

    def test_no_sandbox_envelope_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_r4(sandbox_envelope_required=False)

    def test_l3_required_true_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_r4(l3_required=True)

    def test_l2_required_false_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_r4(l2_required=False)

    def test_wrong_route_id_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_r4(route_id="R3_SIMPLE_GROUNDED_READ")

    @pytest.mark.parametrize(
        "field,enum_value",
        [
            ("side_effect_class", "PURE"),
            ("reversibility_class", "LOW_RISK"),
            ("capability_class", "ACTION"),
            ("sandbox_class", "FULL_SANDBOX"),
        ],
    )
    def test_raw_string_for_enum_raises(self, field: str, enum_value: str) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_r4(**{field: enum_value})


class TestR3R4ArgumentGroundingHandoffEdges:

    def test_wrong_support_target_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            R3R4ArgumentGroundingHandoff(
                action_spec_ref="as",
                c0_argument_targets=("subject",),
                required_argument_fields=("subject_ref",),
                citation_or_source_requirements=("doc",),
                action_args_from_evidence_policy="cite_required",
                support_target=SupportTarget.POLICY_CLAUSE,  # wrong
            )

    def test_l3_required_true_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            R3R4ArgumentGroundingHandoff(
                action_spec_ref="as",
                c0_argument_targets=("subject",),
                required_argument_fields=("subject_ref",),
                citation_or_source_requirements=("doc",),
                action_args_from_evidence_policy="cite_required",
                l3_required=True,
            )

    def test_argument_grounding_required_false_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            R3R4ArgumentGroundingHandoff(
                action_spec_ref="as",
                c0_argument_targets=("subject",),
                required_argument_fields=("subject_ref",),
                citation_or_source_requirements=("doc",),
                action_args_from_evidence_policy="cite_required",
                argument_grounding_required=False,
            )

    def test_wrong_route_id_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            R3R4ArgumentGroundingHandoff(
                action_spec_ref="as",
                c0_argument_targets=("subject",),
                required_argument_fields=("subject_ref",),
                citation_or_source_requirements=("doc",),
                action_args_from_evidence_policy="cite_required",
                route_id="R3R4_MANAGED_WORKFLOW",
            )


class TestPTCPermissionMetadataEdges:

    @pytest.mark.parametrize(
        "field",
        ["ptc_requires_l2_sandbox", "ptc_requires_l5_egress_certification"],
    )
    def test_ptc_candidate_without_safety_flag_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            PTCPermissionMetadata(ptc_candidate=True, **{field: False})

    def test_non_bool_field_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            PTCPermissionMetadata(ptc_candidate="true")  # type: ignore[arg-type]


class TestDownstreamLayerRequirementMapEdges:

    @pytest.mark.parametrize(
        "field",
        [
            "requires_c0",
            "requires_prompt_assembly",
            "requires_l2",
            "requires_l3",
            "requires_l5_certification",
            "requires_uwg_if_commit",
            "requires_hitl_reclearance_if_human_modified",
            "requires_ptc_sandbox_if_ptc_candidate",
        ],
    )
    def test_non_bool_field_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            DownstreamLayerRequirementMap(**{field: "true"})  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 03.5 Telemetry + Replay edges
# ---------------------------------------------------------------------------


def _valid_telemetry(**overrides: object) -> RouteTelemetryEvent:
    base: dict[str, object] = dict(
        event_id="evt-1",
        request_id="r",
        run_id="rn",
        trace_root="tr",
        route_span_id="rs",
        l1_plan_id="lp",
        route_contract_id="rc",
        selected_route_id="R3_SIMPLE_GROUNDED_READ",
        execution_form="SINGLE_STEP",
        confidence=0.9,
        reason_codes=(),
        rejected_routes=(),
        fallback_chain=(),
        policy_hash="p",
        blueprint_hash="b",
        replay_key="rk",
        downstream_requirements=(),
        ptc_allowed_downstream=False,
        timestamp_or_run_clock_offset=0,
    )
    base.update(overrides)
    return RouteTelemetryEvent(**base)  # type: ignore[arg-type]


class TestRouteTelemetryEventEdges:

    def test_negative_timestamp_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_telemetry(timestamp_or_run_clock_offset=-1)

    def test_bool_as_timestamp_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_telemetry(timestamp_or_run_clock_offset=True)

    def test_unknown_execution_form_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_telemetry(execution_form="QUANTUM_LEAP")

    def test_confidence_above_one_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_telemetry(confidence=1.2)

    def test_oversize_reason_codes_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_telemetry(reason_codes=tuple(f"r{i}" for i in range(40)))

    def test_non_bool_ptc_allowed_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_telemetry(ptc_allowed_downstream="yes")

    def test_with_hash_excludes_event_hash_from_payload(self) -> None:
        evt = _valid_telemetry()
        payload = evt.canonical_payload()
        assert "event_hash" not in payload

    def test_with_hash_idempotent(self) -> None:
        a = _valid_telemetry().with_hash()
        b = a.with_hash()  # rehash an already-hashed event
        # The second hash of an already-hashed event is identical because
        # canonical_payload() drops event_hash before computing.
        assert a.event_hash == b.event_hash


class TestRouteSpanAttributesEdges:

    def _valid(self, **overrides: object) -> RouteSpanAttributes:
        base: dict[str, object] = dict(
            route_id="R3_SIMPLE_GROUNDED_READ",
            execution_form="SINGLE_STEP",
            confidence=0.85,
            reason_codes=(),
            freshness_class="STATIC",
            cache_policy="READ_THROUGH",
            support_target="POLICY_CLAUSE",
            cost_tier="TIER_M",
            requires_c0=True,
            requires_l3=False,
            requires_l2=True,
            ptc_allowed_downstream=False,
            route_digest="rd",
        )
        base.update(overrides)
        return RouteSpanAttributes(**base)  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "field",
        ["requires_c0", "requires_l3", "requires_l2", "ptc_allowed_downstream"],
    )
    def test_non_bool_raises(self, field: str) -> None:
        with pytest.raises(DoctrineContractError):
            self._valid(**{field: "true"})

    def test_confidence_above_one_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            self._valid(confidence=2.0)


def _valid_manifest(**overrides: object) -> RouteReplayManifest:
    base: dict[str, object] = dict(
        replay_manifest_id="rm",
        route_contract_id="rc",
        normalized_request_hash="nrh",
        l1_plan_digest="lpd",
        route_candidate_frame_hash="rcf",
        route_score_vector_hash="rsv",
        fixed_decision_order_hash="fdoh",
        policy_hash="p",
        blueprint_hash="b",
        snapshot_id="snap",
        source_availability_snapshot_hash="sas",
        registry_snapshot_hash="rs",
        deterministic_route_digest="drd",
        hmac_sig="",
        replay_certifiable=True,
    )
    base.update(overrides)
    return RouteReplayManifest(**base)  # type: ignore[arg-type]


class TestRouteReplayManifestEdges:

    def test_certifiable_false_without_reasons_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_manifest(replay_certifiable=False, non_replayable_reasons=())

    def test_non_bool_certifiable_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            _valid_manifest(replay_certifiable="yes")

    def test_expected_digest_changes_with_snapshot_id(self) -> None:
        a = _valid_manifest(snapshot_id="snap-A")
        b = _valid_manifest(snapshot_id="snap-B")
        assert a.expected_digest() != b.expected_digest()

    def test_canonical_payload_excludes_hmac_sig(self) -> None:
        m = _valid_manifest(hmac_sig="abc")
        payload = m.canonical_payload()
        assert "hmac_sig" not in payload


class TestVerifyReplayEdges:

    def test_non_manifest_raises(self) -> None:
        with pytest.raises(DoctrineContractError):
            verify_replay("not", _valid_manifest())  # type: ignore[arg-type]

    def test_identical_manifests_certifiable(self) -> None:
        a = _valid_manifest()
        b = _valid_manifest()
        ok, reasons = verify_replay(a, b)
        assert ok is True
        assert reasons == ()

    def test_drift_in_each_field_individually(self) -> None:
        base = _valid_manifest()
        for field, new_value in [
            ("policy_hash", "different"),
            ("blueprint_hash", "different"),
            ("snapshot_id", "different"),
            ("route_candidate_frame_hash", "different"),
            ("fixed_decision_order_hash", "different"),
            ("route_score_vector_hash", "different"),
            ("source_availability_snapshot_hash", "different"),
            ("deterministic_route_digest", "different"),
        ]:
            other = _valid_manifest(**{field: new_value})
            ok, reasons = verify_replay(base, other)
            assert ok is False, f"drift in {field} should fail replay"
            assert any(field in r for r in reasons), f"reason missing for {field}: {reasons}"
