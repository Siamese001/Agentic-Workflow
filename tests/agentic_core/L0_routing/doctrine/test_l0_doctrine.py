"""Unit tests for the 03.x L0 doctrine contracts and pipeline.

Constitutional compliance:

- No ``pytest.mark.skip`` (constitutional §1).
- No bare ``except Exception`` (constitutional §15).
- Asserts both happy-path and hard-fail behavior per doctrine spec.
"""

from __future__ import annotations

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
from agentic_core.L0_routing.doctrine.replay import RouteReplayManifest, verify_replay
from agentic_core.L0_routing.doctrine.selector import (
    compute_score_vector,
    select_route,
)
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
    TerminalExecutionForm,
    TerminalRetPacket,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _valid_decision_input(**overrides: object) -> RouteDecisionInput:
    base: dict[str, object] = dict(
        request_id="req-1",
        run_id="run-1",
        session_id="sess-1",
        trace_root="trace-1",
        tenant_id="tenant-a",
        policy_hash="poly-h",
        blueprint_hash="bp-h",
        replay_key="rk-1",
        l1_plan_id="lp-1",
        l1_plan_digest="ld-1",
        task_spec="What does the policy say about retention?",
        query_spec="policy retention rule",
        support_expectation="POLICY_CLAUSE",
        visible_source_handles=("policy_doc",),
        source_expectations=("policy_doc",),
    )
    base.update(overrides)
    return RouteDecisionInput(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 03.1 preflight
# ---------------------------------------------------------------------------


class TestL01Preflight:
    def test_happy_path_returns_route_ready(self) -> None:
        frame = run_l0_preflight(_valid_decision_input())
        assert isinstance(frame, RouteCandidateFrame)
        assert frame.preflight_status == PreflightStatus.ROUTE_READY
        assert len(frame.route_candidates) > 0
        # R5 is always in candidate set as safety net per 03.1 §_build_candidates.
        assert CandidateRouteId.R5_FALLBACK in frame.route_candidates
        # candidate_frame_hash is deterministic; same input -> same hash.
        frame2 = run_l0_preflight(_valid_decision_input())
        assert frame.candidate_frame_hash == frame2.candidate_frame_hash

    def test_missing_policy_hash_hard_fails(self) -> None:
        # Override after construction is impossible (frozen); use overrides API.
        with pytest.raises(DoctrineContractError):
            _valid_decision_input(policy_hash="")

    def test_missing_request_id_hard_fails_at_pipeline(self) -> None:
        # request_id is required at construction so it raises in dataclass __post_init__.
        with pytest.raises(DoctrineContractError):
            _valid_decision_input(request_id="")

    def test_l1_already_executed_blocks_route(self) -> None:
        decision_input = _valid_decision_input(
            validation_summary=L1ValidationSummary(no_execution_performed=False),
        )
        frame = run_l0_preflight(decision_input)
        assert frame.preflight_status == PreflightStatus.ROUTE_BLOCKED_AUTHORITY
        assert frame.route_candidates == (CandidateRouteId.R5_FALLBACK,)

    def test_missing_source_class_drops_r3(self) -> None:
        decision_input = _valid_decision_input(
            visible_source_handles=(),
            source_expectations=("policy_doc", "user_file"),
        )
        frame = run_l0_preflight(decision_input)
        assert frame.preflight_status == PreflightStatus.ROUTE_NEEDS_CLARIFY_FALLBACK
        assert CandidateRouteId.R3_SIMPLE_GROUNDED_READ not in frame.route_candidates

    def test_irreversible_ambiguous_action_blocks(self) -> None:
        decision_input = _valid_decision_input(
            task_spec="Delete forever someplace",
            action_expectation="purge",
        )
        frame = run_l0_preflight(decision_input)
        # SAFE_FALLBACK_ONLY because action target is ambiguous & irreversible.
        assert frame.preflight_status == PreflightStatus.ROUTE_SAFE_FALLBACK_ONLY


# ---------------------------------------------------------------------------
# 03.2 selector
# ---------------------------------------------------------------------------


class TestL02Selector:
    def test_select_route_returns_receipt_for_grounded_read(self) -> None:
        decision_input = _valid_decision_input()
        frame = run_l0_preflight(decision_input)
        receipt = select_route(
            frame,
            request_id="req-1",
            run_id="run-1",
            trace_root="trace-1",
            l1_plan_id="lp-1",
            preflight_id="pf-1",
        )
        assert isinstance(receipt, RouteSelectionReceipt)
        assert isinstance(receipt.fixed_order_receipt, FixedDecisionOrderReceipt)
        assert isinstance(receipt.route_score_vector, RouteScoreVector)
        # The route picked must match the FixedDecisionOrder receipt.
        assert receipt.fixed_order_receipt.selected_route_id == receipt.selected_route_id
        # Same inputs -> same selection hash (determinism §03.2).
        receipt2 = select_route(
            frame,
            request_id="req-1",
            run_id="run-1",
            trace_root="trace-1",
            l1_plan_id="lp-1",
            preflight_id="pf-1",
        )
        assert receipt.route_selection_hash == receipt2.route_selection_hash

    def test_unsafe_envelope_routes_to_r5(self) -> None:
        decision_input = _valid_decision_input(
            validation_summary=L1ValidationSummary(no_write_performed=False),
        )
        frame = run_l0_preflight(decision_input)
        receipt = select_route(
            frame,
            request_id="r",
            run_id="rn",
            trace_root="tr",
            l1_plan_id="lp",
            preflight_id="pf",
        )
        assert receipt.selected_route_id == CandidateRouteId.R5_FALLBACK
        assert receipt.selected_execution_form == ExecutionFormSelected.TERMINAL_SHORTCIRCUIT

    def test_compute_score_vector_clamps_to_unit(self) -> None:
        discriminators = RouteDiscriminatorFrame(
            asks_for_factual_claim=True,
            asks_for_source_grounding=True,
            can_be_cached_exactly=True,
        )
        sv = compute_score_vector(
            discriminators,
            (CandidateRouteId.R1A_EXACT_CACHE, CandidateRouteId.R5_FALLBACK),
        )
        assert 0.0 <= sv.exact_cache_score <= 1.0
        assert sv.confidence_class in {ConfidenceClass.EXACT, ConfidenceClass.HIGH}


# ---------------------------------------------------------------------------
# 03.3 terminal routes
# ---------------------------------------------------------------------------


class TestL03TerminalRoutes:
    def test_exact_cache_decision_validates(self) -> None:
        d = ExactCacheRouteDecision(
            cache_key="ck-1",
            normalized_request_hash="nrh-1",
            prior_answer_ref="ans-1",
            prior_policy_hash="ph-1",
            current_policy_hash="ph-1",
            freshness_status="ok",
            tenant_scope_status="ok",
            schema_compatibility_status="ok",
            source_snapshot_status="ok",
            cache_hit_basis="policy_compatible",
            exact_cache_guard_receipt="rcpt",
            ret_packet_ref="ret-1",
        )
        assert d.route_id == "R1A_EXACT_CACHE"
        assert d.execution_form == TerminalExecutionForm.TERMINAL_SHORTCIRCUIT

    def test_exact_cache_rejects_policy_drift_with_compatible_basis(self) -> None:
        with pytest.raises(DoctrineContractError):
            ExactCacheRouteDecision(
                cache_key="ck-1",
                normalized_request_hash="nrh-1",
                prior_answer_ref="ans-1",
                prior_policy_hash="ph-old",
                current_policy_hash="ph-new",
                freshness_status="ok",
                tenant_scope_status="ok",
                schema_compatibility_status="ok",
                source_snapshot_status="ok",
                cache_hit_basis="policy_compatible",
                exact_cache_guard_receipt="rcpt",
                ret_packet_ref="ret-1",
            )

    def test_semantic_cache_below_threshold_fails(self) -> None:
        with pytest.raises(DoctrineContractError):
            SemanticCacheRouteDecision(
                semantic_match_id="sm-1",
                query_vec_model_id="bge",
                cached_query_ref="q",
                cached_answer_ref="a",
                similarity_score=0.5,
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

    def test_fallback_requires_reason_codes(self) -> None:
        with pytest.raises(DoctrineContractError):
            FallbackRouteDecision(
                safe_response_type=SafeResponseType.ABSTAIN,
                reason_codes=(),
                fallback_guard_receipt="rcpt",
                ret_packet_ref="ret",
            )

    def test_fallback_with_reason_codes_validates(self) -> None:
        f = FallbackRouteDecision(
            safe_response_type=SafeResponseType.CLARIFY,
            reason_codes=("MISSING_SOURCE",),
            fallback_guard_receipt="rcpt",
            ret_packet_ref="ret",
        )
        assert f.route_id == "R5_FALLBACK"

    def test_hitl_posture_must_assert_non_sovereign(self) -> None:
        with pytest.raises(DoctrineContractError):
            HITLPostureAnnotation(
                hitl_required=True,
                hitl_reason_codes=("review",),
                hitl_not_sovereign_assertion=False,
            )

    def test_terminal_ret_packet_invariants(self) -> None:
        with pytest.raises(DoctrineContractError):
            TerminalRetPacket(
                request_id="r",
                run_id="rn",
                trace_root="tr",
                route_id="R3_SIMPLE_GROUNDED_READ",  # not allowed
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


# ---------------------------------------------------------------------------
# 03.4 handoffs
# ---------------------------------------------------------------------------


class TestL04Handoffs:
    def test_r3_handoff_requires_real_support_target(self) -> None:
        with pytest.raises(DoctrineContractError):
            R3GroundedReadHandoff(
                request_id="r",
                run_id="rn",
                trace_root="tr",
                l1_plan_ref="lp",
                query_spec_ref="qs",
                task_spec_ref="ts",
                support_target=SupportTarget.NONE,
                citation_mode=CitationMode.INLINE,
                freshness_class=FreshnessClass.STATIC,
                tenant_scope="t",
                acl_scope=("read",),
                region_scope="us",
                c0_budget=C0Budget(
                    max_k=10,
                    max_graph_hops=1,
                    max_refine_attempts=1,
                    max_latency_ms=5000,
                    max_token_context=4000,
                ),
                fallback_chain=("R5_FALLBACK",),
                route_digest_ref="rd",
            )

    def test_r4_irreversible_requires_hitl(self) -> None:
        with pytest.raises(DoctrineContractError):
            R4SingleActionHandoff(
                action_spec_ref="as",
                action_kind="delete",
                side_effect_class=SideEffectClass.IRREVERSIBLE,
                reversibility_class=ReversibilityClass.IRREVERSIBLE,
                capability_class=CapabilityClass.ACTION,
                sandbox_class=SandboxClass.PROCESS_SANDBOX,
                capability_token_required=True,
                sandbox_envelope_required=True,
                action_args_status="complete",
                hitl_required=False,  # invalid for irreversible
                uwg_required_if_write=True,
                fallback_chain=("R5_FALLBACK",),
            )

    def test_r4_validates_with_hitl(self) -> None:
        h = R4SingleActionHandoff(
            action_spec_ref="as",
            action_kind="delete",
            side_effect_class=SideEffectClass.IRREVERSIBLE,
            reversibility_class=ReversibilityClass.IRREVERSIBLE,
            capability_class=CapabilityClass.ACTION,
            sandbox_class=SandboxClass.PROCESS_SANDBOX,
            capability_token_required=True,
            sandbox_envelope_required=True,
            action_args_status="complete",
            hitl_required=True,
            uwg_required_if_write=True,
            fallback_chain=("R5_FALLBACK",),
        )
        assert h.l3_required is False

    def test_ptc_candidate_requires_sandbox_and_cert(self) -> None:
        with pytest.raises(DoctrineContractError):
            PTCPermissionMetadata(
                ptc_candidate=True,
                ptc_requires_l2_sandbox=False,
            )

    def test_argument_grounding_handoff_validates(self) -> None:
        h = R3R4ArgumentGroundingHandoff(
            action_spec_ref="as",
            c0_argument_targets=("subject",),
            required_argument_fields=("subject_ref",),
            citation_or_source_requirements=("doc_ref",),
            action_args_from_evidence_policy="cite_required",
        )
        assert h.l3_required is False
        assert h.support_target == SupportTarget.ACTION_ARGUMENT_GROUNDING

    def test_downstream_layer_map_requires_exit(self) -> None:
        with pytest.raises(DoctrineContractError):
            DownstreamLayerRequirementMap(requires_exit_review=False)


# ---------------------------------------------------------------------------
# 03.5 telemetry + replay
# ---------------------------------------------------------------------------


class TestL05TelemetryReplay:
    def test_route_telemetry_event_with_hash_is_deterministic(self) -> None:
        evt = RouteTelemetryEvent(
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
            reason_codes=("GROUNDING_REQUIRED",),
            rejected_routes=("R1A_EXACT_CACHE",),
            fallback_chain=("R3R4_MANAGED_WORKFLOW", "R5_FALLBACK"),
            policy_hash="p",
            blueprint_hash="b",
            replay_key="rk",
            downstream_requirements=("c0", "pa", "l2"),
            ptc_allowed_downstream=False,
            timestamp_or_run_clock_offset=120,
        )
        a = evt.with_hash()
        b = evt.with_hash()
        assert a.event_hash == b.event_hash
        assert a.event_hash != ""

    def test_telemetry_rejects_unknown_route_id(self) -> None:
        with pytest.raises(DoctrineContractError):
            RouteTelemetryEvent(
                event_id="evt-1",
                request_id="r",
                run_id="rn",
                trace_root="tr",
                route_span_id="rs",
                l1_plan_id="lp",
                route_contract_id="rc",
                selected_route_id="R99_INVALID",
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

    def test_route_span_attributes_validates(self) -> None:
        attrs = RouteSpanAttributes(
            route_id="R3_SIMPLE_GROUNDED_READ",
            execution_form="SINGLE_STEP",
            confidence=0.85,
            reason_codes=("ok",),
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
        assert attrs.requires_c0 is True

    def test_replay_manifest_certifiable_only_with_no_reasons(self) -> None:
        with pytest.raises(DoctrineContractError):
            RouteReplayManifest(
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
                non_replayable_reasons=("entropy_present",),  # contradiction
            )

    def test_verify_replay_detects_drift(self) -> None:
        m_a = RouteReplayManifest(
            replay_manifest_id="rm-a",
            route_contract_id="rc",
            normalized_request_hash="nrh",
            l1_plan_digest="lpd",
            route_candidate_frame_hash="rcf-1",
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
        m_b = RouteReplayManifest(
            replay_manifest_id="rm-b",
            route_contract_id="rc",
            normalized_request_hash="nrh",
            l1_plan_digest="lpd",
            route_candidate_frame_hash="rcf-2",  # drift
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
        ok, reasons = verify_replay(m_a, m_b)
        assert ok is False
        assert any("route_candidate_frame_hash" in r for r in reasons)


# ---------------------------------------------------------------------------
# Audit receipt smoke test
# ---------------------------------------------------------------------------


class TestRouteInputAuditReceipt:
    def test_audit_receipt_constructs(self) -> None:
        r = RouteInputAuditReceipt(
            receipt_id="rcpt-1",
            request_id="r",
            run_id="rn",
            trace_root="tr",
            l1_plan_id="lp",
            preflight_id="pf",
            candidate_count=3,
            blocked_count=0,
            fail_closed_reason="",
            receipt_hash="h",
        )
        assert r.candidate_count == 3
