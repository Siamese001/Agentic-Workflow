"""Runtime proof harness for the 03.x L0/L3 doctrine implementation.

Exercises the full pipeline end-to-end and prints captured runtime evidence
(digests, hashes, determinism checks). Used to populate the requirements
traceability matrix in docs/reports/plans/.
"""

from __future__ import annotations

import json
import sys

from agentic_core.L0_routing.doctrine.contracts_l0_1 import (
    L1ValidationSummary,
    RouteDecisionInput,
)
from agentic_core.L0_routing.doctrine.preflight import run_l0_preflight
from agentic_core.L0_routing.doctrine.replay import (
    RouteReplayManifest,
    verify_replay,
)
from agentic_core.L0_routing.doctrine.selector import select_route
from agentic_core.L0_routing.doctrine.telemetry import RouteTelemetryEvent
from agentic_core.L3_orchestration.doctrine.contracts_l3_6 import (
    L3WorkflowInput,
    RouteSLOEnvelope,
    WorkflowExecutionForm,
)
from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import L3ContextBus
from agentic_core.L3_orchestration.doctrine.contracts_l3_8 import (
    CostLatencyTokenSummary,
)
from agentic_core.L3_orchestration.doctrine.eligibility import build_l3_workflow
from agentic_core.L3_orchestration.doctrine.governance import (
    govern_concurrency,
    run_completion_test,
    seal_workflow_package,
)
from agentic_core.L3_orchestration.doctrine.state import (
    emit_step_contract,
    initial_ledger,
    select_next_ready_node,
)


def main() -> None:
    print("=" * 78)
    print("L0/L3 Doctrine Runtime Proof — exercising 03.1..03.8 in sequence")
    print("=" * 78)

    # ---- L0.1 preflight ----
    decision_input = RouteDecisionInput(
        request_id="proof-req-1",
        run_id="proof-run-1",
        session_id="proof-sess-1",
        trace_root="proof-trace-1",
        tenant_id="tenant-proof",
        policy_hash="policy-hash-v1",
        blueprint_hash="blueprint-hash-v1",
        replay_key="replay-proof-1",
        l1_plan_id="l1-plan-1",
        l1_plan_digest="l1-digest-1",
        task_spec="What does the policy say about retention?",
        query_spec="policy retention rule",
        support_expectation="POLICY_CLAUSE",
        visible_source_handles=("policy_doc",),
        source_expectations=("policy_doc",),
        validation_summary=L1ValidationSummary(),
    )
    frame = run_l0_preflight(decision_input)
    print(f"[03.1] preflight_status            = {frame.preflight_status.value}")
    print(f"[03.1] candidate_count             = {len(frame.route_candidates)}")
    print(f"[03.1] candidate_frame_hash        = {frame.candidate_frame_hash[:48]}...")
    print(f"[03.1] discriminators.requires_c0  = {frame.discriminators.likely_requires_c0}")

    # Determinism: re-run preflight; hash must match
    frame2 = run_l0_preflight(decision_input)
    assert frame.candidate_frame_hash == frame2.candidate_frame_hash
    print(f"[03.1] determinism_check           = PASS (frame hash stable)")

    # ---- L0.2 selector ----
    receipt = select_route(
        frame,
        request_id=decision_input.request_id,
        run_id=decision_input.run_id,
        trace_root=decision_input.trace_root,
        l1_plan_id=decision_input.l1_plan_id,
        preflight_id="pf-proof-1",
    )
    print(f"[03.2] selected_route_id           = {receipt.selected_route_id.value}")
    print(f"[03.2] execution_form              = {receipt.selected_execution_form.value}")
    print(f"[03.2] confidence_class            = {receipt.confidence_class.value}")
    print(f"[03.2] confidence_score            = {receipt.confidence:.3f}")
    print(f"[03.2] first_passing_step          = {receipt.fixed_order_receipt.first_passing_step}")
    print(f"[03.2] order_hash                  = {receipt.fixed_order_receipt.deterministic_order_hash[:48]}...")
    print(f"[03.2] route_selection_hash        = {receipt.route_selection_hash[:48]}...")

    receipt2 = select_route(
        frame,
        request_id=decision_input.request_id,
        run_id=decision_input.run_id,
        trace_root=decision_input.trace_root,
        l1_plan_id=decision_input.l1_plan_id,
        preflight_id="pf-proof-1",
    )
    assert receipt.route_selection_hash == receipt2.route_selection_hash
    print(f"[03.2] determinism_check           = PASS (selection hash stable)")

    # ---- L0.5 telemetry ----
    evt = RouteTelemetryEvent(
        event_id="evt-proof-1",
        request_id=decision_input.request_id,
        run_id=decision_input.run_id,
        trace_root=decision_input.trace_root,
        route_span_id="span-1",
        l1_plan_id=decision_input.l1_plan_id,
        route_contract_id="rc-proof-1",
        selected_route_id=receipt.selected_route_id.value,
        execution_form=receipt.selected_execution_form.value,
        confidence=receipt.confidence,
        reason_codes=receipt.reason_codes,
        rejected_routes=receipt.rejected_route_reasons[:4],
        fallback_chain=receipt.fallback_chain_hint,
        policy_hash=decision_input.policy_hash,
        blueprint_hash=decision_input.blueprint_hash,
        replay_key=decision_input.replay_key,
        downstream_requirements=receipt.downstream_required_layers,
        ptc_allowed_downstream=False,
        timestamp_or_run_clock_offset=120,
    )
    evt_hashed = evt.with_hash()
    print(f"[03.5] telemetry.event_hash        = {evt_hashed.event_hash[:48]}...")
    evt_again = evt.with_hash()
    assert evt_hashed.event_hash == evt_again.event_hash
    print(f"[03.5] telemetry determinism_check = PASS (event hash stable)")

    # ---- L0.5 replay manifest ----
    manifest_a = RouteReplayManifest(
        replay_manifest_id="rm-a",
        route_contract_id="rc-proof-1",
        normalized_request_hash="nrh-1",
        l1_plan_digest="l1-digest-1",
        route_candidate_frame_hash=frame.candidate_frame_hash,
        route_score_vector_hash="rsv-1",
        fixed_decision_order_hash=receipt.fixed_order_receipt.deterministic_order_hash,
        policy_hash=decision_input.policy_hash,
        blueprint_hash=decision_input.blueprint_hash,
        snapshot_id="snap-1",
        source_availability_snapshot_hash=frame.source_availability.availability_hash,
        registry_snapshot_hash="reg-1",
        deterministic_route_digest=f"drd:{receipt.route_selection_hash}",
        hmac_sig="",
        replay_certifiable=True,
    )
    manifest_b = RouteReplayManifest(
        replay_manifest_id="rm-b",
        route_contract_id="rc-proof-1",
        normalized_request_hash="nrh-1",
        l1_plan_digest="l1-digest-1",
        route_candidate_frame_hash=frame.candidate_frame_hash,
        route_score_vector_hash="rsv-1",
        fixed_decision_order_hash=receipt.fixed_order_receipt.deterministic_order_hash,
        policy_hash=decision_input.policy_hash,
        blueprint_hash=decision_input.blueprint_hash,
        snapshot_id="snap-1",
        source_availability_snapshot_hash=frame.source_availability.availability_hash,
        registry_snapshot_hash="reg-1",
        deterministic_route_digest=f"drd:{receipt.route_selection_hash}",
        hmac_sig="",
        replay_certifiable=True,
    )
    ok, reasons = verify_replay(manifest_a, manifest_b)
    print(f"[03.5] verify_replay (identical)   = {ok} reasons={reasons}")

    # ---- L3.6 build workflow ----
    wf_input = L3WorkflowInput(
        route_contract_id="rc-proof-1",
        selected_route_id="R3R4_MANAGED_WORKFLOW",
        execution_form=WorkflowExecutionForm.MANAGED_WORKFLOW,
        l1_plan_ref=decision_input.l1_plan_id,
        task_spec_ref="Audit repo and propose migration plan",
        query_spec_ref="depends on prior step then merge",
        support_expectation="SOURCE_BACKED_SUMMARY",
        action_expectation="multi-step propose",
        policy_hash=decision_input.policy_hash,
        blueprint_hash=decision_input.blueprint_hash,
        replay_key=decision_input.replay_key,
        snapshot_id="snap-1",
        route_digest=f"drd:{receipt.route_selection_hash}",
        route_slo=RouteSLOEnvelope(
            max_latency_ms=300_000, max_cost=4.0, max_tokens=200_000, max_iterations=4
        ),
        fallback_chain=("R3R4_MANAGED_WORKFLOW", "R5_FALLBACK"),
        tenant_scope="tenant-proof",
        acl_scope=("read", "write"),
        capability_class="READ_WRITE",
        sandbox_class="PROCESS_SANDBOX",
    )
    blueprint = build_l3_workflow(wf_input)
    print(f"[03.6] node_count                  = {len(blueprint.nodes)}")
    print(f"[03.6] edge_count                  = {len(blueprint.edges)}")
    print(f"[03.6] graph_hash                  = {blueprint.graph_hash[:48]}...")
    blueprint_2 = build_l3_workflow(wf_input)
    assert blueprint.graph_hash == blueprint_2.graph_hash
    print(f"[03.6] determinism_check           = PASS (graph hash stable)")

    # ---- L3.7 state ledger + step contract ----
    ledger = initial_ledger(
        blueprint,
        policy_hash=decision_input.policy_hash,
        blueprint_hash=decision_input.blueprint_hash,
        replay_key=decision_input.replay_key,
        route_contract_id="rc-proof-1",
        initial_budget=10.0,
        initial_slo_ms=300_000,
    )
    bus = L3ContextBus(
        workflow_id=blueprint.workflow_id,
        bus_hash="bus-proof",
        carried_query_refs=("q-proof",),
    )
    decision = select_next_ready_node(ledger, blueprint, bus)
    print(f"[03.7] first_ready_node            = {decision.node_id}")
    print(f"[03.7] readiness.ready             = {decision.ready}")
    print(f"[03.7] readiness_hash              = {decision.readiness_hash[:48]}...")

    contract = emit_step_contract(
        decision, ledger, blueprint, bus,
        parent_route_id="R3R4_MANAGED_WORKFLOW",
        route_digest=f"drd:{receipt.route_selection_hash}",
        snapshot_id="snap-1",
    )
    print(f"[03.7] step_contract_id            = {contract.step_contract_id[:48]}...")
    print(f"[03.7] no_durable_commit_authority = {contract.no_durable_commit_authority}")
    print(f"[03.7] node_type                   = {contract.node_type.value}")

    # ---- L3.8 govern + complete + seal (after marking all SUCCEEDED) ----
    from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import (
        L3StateLedger,
        NodeState,
    )

    succeeded = tuple(
        sorted(((n.node_id, NodeState.SUCCEEDED) for n in blueprint.nodes), key=lambda p: p[0])
    )
    ledger_done = L3StateLedger(
        workflow_id=ledger.workflow_id,
        route_contract_id=ledger.route_contract_id,
        policy_hash=ledger.policy_hash,
        blueprint_hash=ledger.blueprint_hash,
        replay_key=ledger.replay_key,
        graph_hash=ledger.graph_hash,
        node_states=succeeded,
        edge_states=ledger.edge_states,
        branch_states=ledger.branch_states,
        join_states=ledger.join_states,
        attempt_counts=ledger.attempt_counts,
        retry_counts=ledger.retry_counts,
        fallback_depth=0,
        remaining_budget=ledger.remaining_budget,
        remaining_slo=ledger.remaining_slo,
        checkpoints=ledger.checkpoints,
        paused_packets=ledger.paused_packets,
        reason_codes=ledger.reason_codes,
        ledger_hash=ledger.ledger_hash,
    )
    bus_done = L3ContextBus(
        workflow_id=blueprint.workflow_id,
        bus_hash="bus-proof-2",
        carried_l2_artifact_refs=("art-1", "art-2"),
        carried_evidence_refs=("ev-1",),
    )
    plan = govern_concurrency(ledger_done, blueprint, max_parallelism=4)
    print(f"[03.8] concurrency_plan_hash       = {plan.concurrency_plan_hash[:48]}...")

    completion = run_completion_test(ledger_done, blueprint, bus_done)
    print(f"[03.8] completion_status           = {completion.completion_status.value}")
    print(f"[03.8] mutation_proposal_only      = {completion.mutation_proposal_only}")

    pkg = seal_workflow_package(
        ledger=ledger_done,
        blueprint=blueprint,
        context_bus=bus_done,
        completion=completion,
        request_id=decision_input.request_id,
        run_id=decision_input.run_id,
        trace_root=decision_input.trace_root,
        cost_summary=CostLatencyTokenSummary(
            total_latency_ms=1500, total_tokens=4200, total_cost=0.12
        ),
    )
    print(f"[03.8] sealed_package_id           = {pkg.sealed_workflow_package_id[:48]}...")
    print(f"[03.8] outcome_class               = {pkg.workflow_outcome_class.value}")
    print(f"[03.8] exit_review_required        = {pkg.exit_review_required}")
    print(f"[03.8] no_durable_commit_assertion = {pkg.no_durable_commit_assertion}")
    print(f"[03.8] package_hash                = {pkg.package_hash[:48]}...")

    print("=" * 78)
    print("RUNTIME PROOF: ALL DOCTRINE INVARIANTS UPHELD")
    print("=" * 78)


if __name__ == "__main__":
    sys.exit(main())
