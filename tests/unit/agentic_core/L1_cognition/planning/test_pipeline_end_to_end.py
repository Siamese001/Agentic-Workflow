"""End-to-end pipeline tests for the L1 v6 planning module."""

from __future__ import annotations

from agentic_core.L1_cognition.planning import (
    L1PlanContract,
    L1PlanHandoffPacket,
    NonAuthorityAssertion,
    ProposedRouteHint,
    run_l1_planning,
)


def test_pipeline_produces_l1_plan_contract(basic_parsed_input, span_sink, static_reader):
    packet = run_l1_planning(basic_parsed_input, prior_reader=static_reader, span_sink=span_sink)
    assert isinstance(packet, L1PlanHandoffPacket)
    assert isinstance(packet.l1_plan_contract, L1PlanContract)
    assert packet.l1_plan_contract.layer == "L1_REASONING_PLAN_GENERATION"
    assert packet.l1_plan_contract.version == "v6"
    assert packet.l1_plan_contract.authority == "advisory_plan_only"
    # NonAuthorityAssertion: every flag must be True for handoff.
    naa: NonAuthorityAssertion = packet.l1_plan_contract.non_authority_assertion
    assert naa.no_evidence_retrieval is True
    assert naa.no_final_route_commitment is True
    assert naa.no_tool_execution is True
    assert naa.no_durable_state_mutation is True
    assert naa.no_hitl_approval is True
    assert naa.no_uwg_commit is True


def test_pipeline_emits_18_spans_across_six_stages(basic_parsed_input, span_sink, static_reader):
    run_l1_planning(basic_parsed_input, prior_reader=static_reader, span_sink=span_sink)
    assert len(span_sink.events) == 18  # 3 per stage * 6 stages
    by_stage = {s: len(span_sink.by_stage(s)) for s in ("02.1", "02.2", "02.3", "02.4", "02.5", "02.6")}
    assert by_stage == {"02.1": 3, "02.2": 3, "02.3": 3, "02.4": 3, "02.5": 3, "02.6": 3}
    expected_lifecycle = ("input.accepted", "core.completed", "output.emitted")
    for stage in ("02.1", "02.2", "02.3", "02.4", "02.5", "02.6"):
        names = [e.span_name for e in span_sink.by_stage(stage)]
        for suffix in expected_lifecycle:
            assert any(n.endswith(suffix) for n in names), (stage, suffix, names)


def test_every_span_carries_no_authority_assertions(basic_parsed_input, span_sink, static_reader):
    run_l1_planning(basic_parsed_input, prior_reader=static_reader, span_sink=span_sink)
    for ev in span_sink.events:
        assert ev.no_route_authority is True, ev.span_name
        assert ev.no_retrieval_performed is True, ev.span_name
        assert ev.no_execution_performed is True, ev.span_name
        assert ev.no_write_performed is True, ev.span_name
        assert ev.input_digest.startswith("sha256:")
        assert ev.output_digest.startswith("sha256:")


def test_pipeline_is_deterministic_under_replay(basic_parsed_input, static_reader):
    a = run_l1_planning(basic_parsed_input, prior_reader=static_reader)
    b = run_l1_planning(basic_parsed_input, prior_reader=static_reader)
    # The plan_digest is the canonical replay key.
    assert a.plan_digest.digest == b.plan_digest.digest
    assert a.l1_plan_contract.identity == b.l1_plan_contract.identity
    assert a.l1_plan_contract.task_spec == b.l1_plan_contract.task_spec


def test_high_risk_input_routes_to_workflow_or_action_with_hitl(high_risk_parsed_input, static_reader):
    packet = run_l1_planning(high_risk_parsed_input, prior_reader=static_reader)
    route = packet.l1_plan_contract.route_hint["proposed_route_hint"]
    assert route in (
        ProposedRouteHint.R4_SINGLE_ACTION.value,
        ProposedRouteHint.R3R4_MANAGED_WORKFLOW.value,
        ProposedRouteHint.R5_FALLBACK.value,
    )
    # HITL or UWG hint must fire because the request is high-impact.
    action = packet.l1_plan_contract.action_expectation
    assert (
        action["hitl_hint"] is True
        or action["uwg_hint"] is True
        or action["irreversible_action_marker"] is True
    )


def test_refusal_input_routes_to_fallback(refusal_parsed_input, static_reader):
    packet = run_l1_planning(refusal_parsed_input, prior_reader=static_reader)
    route = packet.l1_plan_contract.route_hint["proposed_route_hint"]
    assert route == ProposedRouteHint.R5_FALLBACK.value
    marker = packet.l1_plan_contract.assumptions_and_gaps["abstain_or_fallback_marker"]
    assert marker in ("abstain", "fallback", "policy_review", "clarify"), marker


def test_route_hint_block_does_not_carry_authoritative_fields(basic_parsed_input, static_reader):
    packet = run_l1_planning(basic_parsed_input, prior_reader=static_reader)
    rh = packet.l1_plan_contract.route_hint
    # Authoritative fields owned by L0 must not appear in the L1 route hint.
    for forbidden in ("route_digest", "hmac_sig", "selected_route", "execution_authorization"):
        assert forbidden not in rh, forbidden
    assert rh["route_authority_assertion"] == "advisory_only"


def test_validation_summary_asserts_l1_invariants(basic_parsed_input, static_reader):
    packet = run_l1_planning(basic_parsed_input, prior_reader=static_reader)
    vs = packet.l1_plan_contract.validation_summary
    assert vs["no_retrieval_performed"] is True
    assert vs["no_execution_performed"] is True
    assert vs["no_write_performed"] is True


def test_handoff_receipt_targets_l0(basic_parsed_input, static_reader):
    packet = run_l1_planning(basic_parsed_input, prior_reader=static_reader)
    receipt = packet.l1_handoff_receipt
    assert receipt.target_layer == "L0_ROUTE_DECISION"
    assert receipt.l1_plan_id.startswith("l1plan::")
    assert receipt.plan_digest == packet.plan_digest.digest
    assert "l1.02.6.output.emitted" in receipt.telemetry_keys


def test_replay_manifest_excludes_volatile_fields(basic_parsed_input, static_reader):
    packet = run_l1_planning(basic_parsed_input, prior_reader=static_reader)
    manifest = packet.l1_plan_contract.plan_replay_manifest
    excluded = manifest["excluded_volatile_fields"]
    for must_exclude in (
        "wall_clock_time",
        "transient_span_ids",
        "provider_latency",
        "local_filesystem_temp_names",
    ):
        assert must_exclude in excluded, must_exclude
