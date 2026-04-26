"""Per-stage contract validation tests for the L1 v6 planning module."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.planning import (
    ActionExpectation,
    DependencySketch,
    DraftPlan,
    DraftPlanInput,
    DraftPlanPacket,
    L1ContractViolation,
    L1PlanContractInput,
    L1PlanHandoffPacket,
    NonAuthorityAssertion,
    ParsedIntentPacket,
    ParsedRequestInput,
    PlanBundlePacket,
    PlanningPriorReadInput,
    PlanningReasoningInput,
    PlanningReasoningPacket,
    PlanValidationInput,
    ProposedRouteHint,
    QuerySpec,
    RouteHintSet,
    SupportExpectation,
    TaskSpec,
    ValidatedPlanPacket,
    WorkUnit,
    WorkUnitSet,
    WorkUnitType,
    build_plan_bundle,
    emit_l1_plan_contract,
    parse_intent_frame,
    run_l1_planning,
    run_l1_reasoning_loop,
    validate_and_repair_l1_plan,
    write_draft_plan,
)
from agentic_core.L1_cognition.planning.contracts import L1ContractViolation as _LV  # noqa: F401


# ---------------------------------------------------------------------------
# Stage 02.1
# ---------------------------------------------------------------------------


def test_parsed_request_input_requires_request_or_rejected():
    with pytest.raises(L1ContractViolation):
        ParsedRequestInput(
            request_id="r",
            session_id="s",
            trace_root="t",
            caller_scope_baseline="b",
            normalized_user_payload="x",
            validated_request=None,
            rejected_request_summary=None,
        )


def test_parse_intent_frame_returns_packet(basic_parsed_input):
    packet = parse_intent_frame(basic_parsed_input)
    assert isinstance(packet, ParsedIntentPacket)
    assert packet.intent_frame.request_id == basic_parsed_input.request_id
    assert packet.parsed_request_receipt.input_digest.startswith("sha256:")
    assert packet.parsed_request_receipt.output_digest.startswith("sha256:")
    sep = packet.user_intent_authority_separation_receipt
    assert sep["treats_user_text_as_intent_only"] is True
    assert sep["does_not_grant_authority"] is True


def test_request_detail_inventory_extracts_files_and_dates():
    pi = ParsedRequestInput(
        request_id="r",
        session_id="s",
        trace_root="t",
        caller_scope_baseline="b",
        normalized_user_payload="Read README.md and CHANGELOG.md from 2026-04-26",
        validated_request={"k": "v"},
    )
    packet = parse_intent_frame(pi)
    inv = packet.request_detail_inventory
    assert "README.md" in inv.files
    assert "CHANGELOG.md" in inv.files
    assert "2026-04-26" in inv.dates


# ---------------------------------------------------------------------------
# Stage 02.2
# ---------------------------------------------------------------------------


def test_build_plan_bundle_returns_packet(basic_parsed_input, static_reader):
    parsed_packet = parse_intent_frame(basic_parsed_input)
    prior_input = PlanningPriorReadInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        request_id=basic_parsed_input.request_id,
        trace_root=basic_parsed_input.trace_root,
        caller_scope_baseline=basic_parsed_input.caller_scope_baseline,
        policy_hash_observed=basic_parsed_input.policy_hash_observed,
        instruction_hash_observed=basic_parsed_input.instruction_hash_observed,
    )
    bundle_packet = build_plan_bundle(prior_input, static_reader)
    assert isinstance(bundle_packet, PlanBundlePacket)
    assert bundle_packet.bundle_digest.startswith("sha256:")
    assert bundle_packet.plan_bundle.bundle_hash
    # rule_aware_planning_frame must be a dict with 3 keys.
    raf = bundle_packet.rule_aware_planning_frame
    assert {"can_be_proposed", "must_be_grounded", "must_be_escalated"} <= set(raf)


def test_plan_bundle_marks_priors_not_evidence(basic_parsed_input, static_reader):
    parsed_packet = parse_intent_frame(basic_parsed_input)
    prior_input = PlanningPriorReadInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        request_id=basic_parsed_input.request_id,
        trace_root=basic_parsed_input.trace_root,
        caller_scope_baseline=basic_parsed_input.caller_scope_baseline,
        policy_hash_observed=basic_parsed_input.policy_hash_observed,
        instruction_hash_observed=basic_parsed_input.instruction_hash_observed,
    )
    bundle_packet = build_plan_bundle(prior_input, static_reader)
    assert bundle_packet.planning_reference_manifest.no_answer_evidence_assertion is True


# ---------------------------------------------------------------------------
# Stage 02.3
# ---------------------------------------------------------------------------


def test_reasoning_loop_respects_max_passes(basic_parsed_input, static_reader):
    parsed_packet = parse_intent_frame(basic_parsed_input)
    prior_input = PlanningPriorReadInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        request_id=basic_parsed_input.request_id,
        trace_root=basic_parsed_input.trace_root,
        caller_scope_baseline=basic_parsed_input.caller_scope_baseline,
        policy_hash_observed=basic_parsed_input.policy_hash_observed,
        instruction_hash_observed=basic_parsed_input.instruction_hash_observed,
    )
    bundle_packet = build_plan_bundle(prior_input, static_reader)
    rinput = PlanningReasoningInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        request_detail_inventory=parsed_packet.request_detail_inventory,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        plan_bundle=bundle_packet.plan_bundle,
        rule_aware_planning_frame=bundle_packet.rule_aware_planning_frame,
        request_id=basic_parsed_input.request_id,
        trace_root=basic_parsed_input.trace_root,
        policy_hash_observed=basic_parsed_input.policy_hash_observed,
        instruction_hash_observed=basic_parsed_input.instruction_hash_observed,
        max_refinement_passes=1,
    )
    packet = run_l1_reasoning_loop(rinput)
    assert isinstance(packet, PlanningReasoningPacket)
    assert packet.planning_loop_budget_receipt.passes_used <= 1
    assert packet.planning_loop_budget_receipt.loop_not_spinning_assertion is True
    # No chain-of-thought leakage — internal state is bounded summaries.
    state = packet.internal_plan_state
    assert isinstance(state.normalized_goal_summary, str)
    assert len(state.normalized_goal_summary) <= 240


# ---------------------------------------------------------------------------
# Stage 02.4
# ---------------------------------------------------------------------------


def test_route_hint_authority_assertion_locked():
    """RouteHintSet must reject any non-advisory authority assertion."""
    with pytest.raises(L1ContractViolation):
        RouteHintSet(
            route_hint_id="x",
            proposed_route_hint=ProposedRouteHint.R3_GROUNDED_READ,
            route_authority_assertion="committed",
        )


def test_route_hint_confidence_bounded():
    with pytest.raises(L1ContractViolation):
        RouteHintSet(
            route_hint_id="x",
            proposed_route_hint=ProposedRouteHint.R3_GROUNDED_READ,
            confidence=1.5,
        )


def test_work_unit_set_rejects_duplicates():
    a = WorkUnit(
        work_unit_id="u1",
        description="d",
        work_unit_type=WorkUnitType.INTERPRET,
    )
    b = WorkUnit(
        work_unit_id="u1",  # duplicate id
        description="e",
        work_unit_type=WorkUnitType.INTERPRET,
    )
    with pytest.raises(L1ContractViolation):
        WorkUnitSet(units=(a, b))


def test_work_unit_set_requires_at_least_one_unit():
    with pytest.raises(L1ContractViolation):
        WorkUnitSet(units=())


# ---------------------------------------------------------------------------
# Stage 02.5
# ---------------------------------------------------------------------------


def test_validation_passes_for_basic_input(basic_parsed_input, static_reader):
    # Run pipeline through stage 02.5.
    parsed_packet = parse_intent_frame(basic_parsed_input)
    prior_input = PlanningPriorReadInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        request_id=basic_parsed_input.request_id,
        trace_root=basic_parsed_input.trace_root,
        caller_scope_baseline=basic_parsed_input.caller_scope_baseline,
        policy_hash_observed=basic_parsed_input.policy_hash_observed,
        instruction_hash_observed=basic_parsed_input.instruction_hash_observed,
    )
    bundle_packet = build_plan_bundle(prior_input, static_reader)
    rinput = PlanningReasoningInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        request_detail_inventory=parsed_packet.request_detail_inventory,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        plan_bundle=bundle_packet.plan_bundle,
        rule_aware_planning_frame=bundle_packet.rule_aware_planning_frame,
        request_id=basic_parsed_input.request_id,
        trace_root=basic_parsed_input.trace_root,
        policy_hash_observed=basic_parsed_input.policy_hash_observed,
        instruction_hash_observed=basic_parsed_input.instruction_hash_observed,
    )
    rpacket = run_l1_reasoning_loop(rinput)
    dinput = DraftPlanInput(
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        request_detail_inventory=parsed_packet.request_detail_inventory,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        plan_bundle=bundle_packet.plan_bundle,
        rule_aware_planning_frame=bundle_packet.rule_aware_planning_frame,
        internal_plan_state=rpacket.internal_plan_state,
        reasoning_trace_summary=rpacket.planning_reasoning_trace_summary,
        request_id=basic_parsed_input.request_id,
        trace_root=basic_parsed_input.trace_root,
        policy_hash_observed=basic_parsed_input.policy_hash_observed,
        instruction_hash_observed=basic_parsed_input.instruction_hash_observed,
    )
    dpacket = write_draft_plan(dinput)
    vinput = PlanValidationInput(
        draft_plan=dpacket.draft_plan,
        intent_frame=parsed_packet.intent_frame,
        ambiguity_register=parsed_packet.ambiguity_register,
        first_safety_authority_reading=parsed_packet.first_safety_authority_reading,
        request_id=basic_parsed_input.request_id,
        trace_root=basic_parsed_input.trace_root,
        policy_hash_observed=basic_parsed_input.policy_hash_observed,
        instruction_hash_observed=basic_parsed_input.instruction_hash_observed,
    )
    vpacket = validate_and_repair_l1_plan(vinput)
    assert isinstance(vpacket, ValidatedPlanPacket)
    assert vpacket.self_repair_ledger.no_tool_rescue_assertion is True
    assert vpacket.self_repair_ledger.no_retrieval_rescue_assertion is True


# ---------------------------------------------------------------------------
# Stage 02.6
# ---------------------------------------------------------------------------


def test_non_authority_assertion_rejects_false_flags():
    with pytest.raises(L1ContractViolation):
        NonAuthorityAssertion(no_evidence_retrieval=False)


def test_handoff_receipt_target_layer_locked():
    from agentic_core.L1_cognition.planning import L1HandoffReceipt

    with pytest.raises(L1ContractViolation):
        L1HandoffReceipt(
            handoff_receipt_id="x",
            l1_plan_id="y",
            target_layer="L1_REASONING",  # wrong target
            handoff_time_policy="immediate",
            plan_digest="sha256:0",
            trace_root="t",
            request_id="r",
            readiness_status="ready",
            non_authority_assertion_ref="ref",
        )


def test_l1_plan_contract_blocks_authoritative_route_fields():
    from agentic_core.L1_cognition.planning import (
        L1PlanContract,
        PlanDigest,
    )

    bad_route = {
        "route_hint_id": "x",
        "proposed_route_hint": "R3_GROUNDED_READ",
        "route_authority_assertion": "advisory_only",
        "route_digest": "naughty",  # forbidden
    }
    with pytest.raises(L1ContractViolation):
        L1PlanContract(
            layer="L1_REASONING_PLAN_GENERATION",
            version="v6",
            authority="advisory_plan_only",
            identity={},
            intent_frame={},
            query_spec=None,
            task_spec={},
            route_hint=bad_route,
            support_expectation={},
            action_expectation={},
            assumptions_and_gaps={},
            validation_summary={
                "no_retrieval_performed": True,
                "no_execution_performed": True,
                "no_write_performed": True,
            },
            downstream_notes={},
            plan_replay_manifest={},
            plan_digest=PlanDigest(digest="sha256:0"),
            non_authority_assertion=NonAuthorityAssertion(),
        )
