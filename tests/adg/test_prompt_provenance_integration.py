"""Integration tests for the full prompt provenance lifecycle.

Covers:
  - TestFullPromptLifecycleIntegration: build → validate → execute → drift → adapt → bus
"""

from __future__ import annotations

import hashlib

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_prompt_provenance_integration")
_emit_applies_guardrail("p0", "test_prompt_provenance_integration", "p0_governance")
_emit_reads_policy_state("p0", "test_prompt_provenance_integration", "policy_binding")
_emit_snapshots_state("p0", "test_prompt_provenance_integration", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_prompt_provenance_integration", "p4obs", "metric_1")
_emit_emits_metric_event("test_prompt_provenance_integration", "p4obs", "metric_2")
_emit_emits_metric_event("test_prompt_provenance_integration", "p4obs", "metric_3")
_emit_emits_metric_event("test_prompt_provenance_integration", "p4obs", "metric_4")
_emit_emits_metric_event("test_prompt_provenance_integration", "p4obs", "metric_5")
_emit_emits_metric_event("test_prompt_provenance_integration", "p4obs", "metric_6")
_emit_records_incident_event("test_prompt_provenance_integration", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_prompt_provenance_integration", "p4obs", "anomaly")
_emit_writes_observability_log("test_prompt_provenance_integration", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_prompt_provenance_integration", "p4obs", "mon_state")
_emit_triggers_alert("test_prompt_provenance_integration", "p4obs", "alert")
_emit_links_incident_trace("test_prompt_provenance_integration", "p4obs", "trace_link")
_emit_captures_pattern("test_prompt_provenance_integration", "p3lm", "pattern")
_emit_records_learning_event("test_prompt_provenance_integration", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_prompt_provenance_integration", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_prompt_provenance_integration", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_prompt_provenance_integration", "p3lm", "routing")
_emit_improves_agent_policy("test_prompt_provenance_integration", "p3lm", "policy")
_emit_stores_learning_state("test_prompt_provenance_integration", "p3lm", "state")
_emit_records_execution_trace("test_prompt_provenance_integration", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_prompt_provenance_integration", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_prompt_provenance_integration", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_prompt_provenance_integration", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_prompt_provenance_integration", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_prompt_provenance_integration", "env_read", "p2_env_1")
_emit_reads_environ("test_prompt_provenance_integration", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_prompt_provenance_integration", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_prompt_provenance_integration", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_prompt_provenance_integration", "context_pull")
_emit_pulls_context("p1", "test_prompt_provenance_integration", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_prompt_provenance_integration", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_prompt_provenance_integration", "uwg_term_2")
_emit_writes_through("p1", "test_prompt_provenance_integration", "write_through")
_emit_writes_through("p1", "test_prompt_provenance_integration", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_prompt_provenance_integration", "safety_validation")
_emit_invokes_eval("p1", "test_prompt_provenance_integration", "eval_call")
_emit_proposal_commits_routing("p1", "test_prompt_provenance_integration", "routing_commit")
_emit_escalates_to_human("p1", "test_prompt_provenance_integration", "human_escalation")
_emit_routes_through("p1", "test_prompt_provenance_integration", "route_through")
_emit_checks_agent_registry("p1", "test_prompt_provenance_integration", "agent_registry")
_emit_validates_agent_capability("p1", "test_prompt_provenance_integration", "capability")
_emit_dispatches_execution_plan("p1", "test_prompt_provenance_integration", "exec_plan")
_emit_agent_executes_agent("p1", "test_prompt_provenance_integration", "sub_agent")
_emit_routes_to_agent("p1", "test_prompt_provenance_integration", "target_agent")
_emit_verifies_policy("p1", "test_prompt_provenance_integration", "policy_check")
_emit_observes_runtime_state("p1", "test_prompt_provenance_integration", "runtime_state")
_emit_verifies_boundary("p1", "test_prompt_provenance_integration", "boundary_check")
_emit_transcripts_response("p1", "test_prompt_provenance_integration", "transcript")
_emit_hard_fails_untranscripted("p1", "test_prompt_provenance_integration")
_emit_gated_by_confidence("p1", "test_prompt_provenance_integration", "confidence_gate")
emit_replay_key("p0", "test_prompt_provenance_integration")
emit_determinism_digest("p0", "test_prompt_provenance_integration")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_prompt_provenance_integration", "execution_auth")
_emit_validates_capability("p2", "test_prompt_provenance_integration", "capability_check")
_emit_routes_to_capability("p2", "test_prompt_provenance_integration", "capability_route")
_emit_writes_via_uwg("p2", "test_prompt_provenance_integration", "uwg_write")
_emit_blocks_direct_write("p2", "test_prompt_provenance_integration", "direct_write_block")
_emit_records_tool_invocation("p2", "test_prompt_provenance_integration", "tool_invocation")
_emit_captures_execution_output("p2", "test_prompt_provenance_integration", "exec_output")
_emit_dispatches_agent("p3", "test_prompt_provenance_integration", "agent_dispatch")
_emit_coordinates_agents("p3", "test_prompt_provenance_integration", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_prompt_provenance_integration", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_prompt_provenance_integration", "healing_outcome")
_emit_escalates_failure("p3", "test_prompt_provenance_integration", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_prompt_provenance_integration", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_prompt_provenance_integration", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_prompt_provenance_integration", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_prompt_provenance_integration", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_prompt_provenance_integration", "eval_metric")
_emit_stores_embedding("p4", "test_prompt_provenance_integration", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_prompt_provenance_integration", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_prompt_provenance_integration", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_TS = 1_700_200_000
_H64 = "a" * 64
_H64b = "b" * 64


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _make_outcome_record(
    trace_id="tr-001",
    final_outcome="SUCCESS",
    groundedness=0.85,
    hitl=False,
    healer=False,
    healer_id=None,
    guardrail_hits=(),
    replay_status="NOT_TESTED",
    failure_slot="NONE",
    prompt_hash=None,
):
    from system_learning.types.prompt_artifact_types import PromptOutcomeRecord

    ph = prompt_hash or _sha256("prompt")
    oid = _sha256(trace_id + final_outcome + str(groundedness))
    return PromptOutcomeRecord(
        outcome_id=oid,
        prompt_hash=ph,
        trace_id=trace_id,
        route="PATH_A",
        model="gpt-4o",
        groundedness_score=groundedness,
        guardrail_hits=guardrail_hits,
        healer_invoked=healer,
        healer_id=healer_id,
        hitl_escalation=hitl,
        replay_status=replay_status,
        final_outcome=final_outcome,
        failure_slot=failure_slot,
        support_score=0.9,
        completeness_score=0.95,
        citation_count=3,
        adg_entity_name=f"ADG::PromptOutcome::{oid[:16]}",
        timestamp_utc=_TS,
    )


def _make_build_request(
    s0="System role content",
    d0="Defensive fence content",
    i0="Instruction content",
    c0="Context / RAG content",
    u0="User input here",
    template_ids=("tmpl-001",),
    fewshot_ids=("fs-001",),
    injection_ids=("inj-001",),
    model_target="gpt-4o",
    policy_hash=None,
):
    from system_learning.engines.prompt_provenance_builder import (
        PromptBuildRequest,
        SlotPayload,
    )

    return PromptBuildRequest(
        s0=SlotPayload(content=s0),
        d0=SlotPayload(content=d0),
        i0=SlotPayload(content=i0),
        c0=SlotPayload(content=c0, source_ids=(_sha256("chunk-1"),)),
        u0=SlotPayload(content=u0),
        template_ids=template_ids,
        fewshot_ids=fewshot_ids,
        injection_ids=injection_ids,
        model_target=model_target,
        policy_hash=policy_hash,
        adg_entity_prefix="ADG::CompiledPrompt",
        timestamp_utc=_TS,
    )


# ===========================================================================
# 8. Integration — full prompt lifecycle
# ===========================================================================


class TestFullPromptLifecycleIntegration:
    """End-to-end: build → validate → execute → drift → adapt → bus."""

    def _build_artifact(self):
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt

        req = _make_build_request(policy_hash=_sha256("policy_v1"))
        result = build_compiled_prompt(req)
        return result.artifact, result.adg_relations

    def test_build_to_validate_pipeline(self):
        from system_learning.engines.prompt_safety_validator import (
            PromptSafetyValidator,
            SafetyValidatorConfig,
        )

        artifact, prov_rels = self._build_artifact()
        ph = _sha256("policy_v1")
        cfg = SafetyValidatorConfig(active_policy_hash=ph)
        decision, safety_rels = PromptSafetyValidator(cfg).validate(artifact, _TS)
        assert decision.allowed is True
        total_rels = prov_rels + safety_rels
        rel_types = {r for (_, r, _) in total_rels}
        from system_learning.types.prompt_adg_relations import (
            PROVENANCE_USES_S0_RULE,
            SAFETY_ALLOWED,
        )

        assert PROVENANCE_USES_S0_RULE in rel_types
        assert SAFETY_ALLOWED in rel_types

    def test_execute_produces_outcome_record(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution

        artifact, _ = self._build_artifact()
        result = trace_execution(
            artifact.prompt_hash,
            "tr-integration-001",
            {
                "route_selected": "PATH_A",
                "model_id": "gpt-4o",
                "latency_ms": 400,
                "retrieval_groundedness_score": 0.88,
                "success": True,
                "chunk_ids": ["c1", "c2"],
                "citation_set_hash": _sha256("cset"),
            },
            _TS + 10,
        )
        assert result.outcome_record.final_outcome == "SUCCESS"
        assert result.outcome_record.groundedness_score == pytest.approx(0.88, abs=1e-5)

    def test_adapt_outcome_to_bus_record(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcome_to_record

        artifact, _ = self._build_artifact()
        exec_result = trace_execution(
            artifact.prompt_hash,
            "tr-adapt-001",
            {"success": True, "retrieval_groundedness_score": 0.9},
            _TS + 20,
        )
        bus_record = convert_outcome_to_record(exec_result.outcome_record)
        assert bus_record.outcome_class == "SUCCESS"
        assert bus_record.retrieval_groundedness == pytest.approx(0.9, abs=1e-5)

    def test_drift_detected_after_groundedness_drop(self):
        from system_learning.engines.prompt_drift_detector import detect_prompt_drift

        baseline = [_make_outcome_record(trace_id=f"b{i}", groundedness=0.9) for i in range(20)]
        current = [_make_outcome_record(trace_id=f"c{i}", groundedness=0.7) for i in range(20)]
        signals = detect_prompt_drift(baseline, current, _H64, _H64b, _TS)
        assert any(s.drift_type == "GROUNDEDNESS_DROP" for s in signals)

    def test_bus_adapter_feeds_meta_learning_cluster(self):
        from system_learning.engines.prompt_outcome_bus_adapter import convert_outcomes_to_records
        from system_learning.engines.rca_cluster_engine import cluster_records

        outcomes = [
            _make_outcome_record(trace_id=f"tr-{i}", groundedness=0.2, final_outcome="SAFE_FAILURE")
            for i in range(6)
        ]
        records = convert_outcomes_to_records(outcomes)
        clusters = cluster_records(records, _TS)
        assert len(clusters) >= 1
        # Should produce a LOW_GROUNDEDNESS cluster
        patterns = {c.failure_pattern for c in clusters}
        assert "LOW_GROUNDEDNESS" in patterns

    def test_all_adg_relations_use_known_relation_types(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.engines.prompt_safety_validator import validate_prompt
        from system_learning.types.prompt_adg_relations import ALL_PROMPT_RELATIONS

        artifact, prov_rels = self._build_artifact()
        _, safety_rels = validate_prompt(artifact, _TS)
        exec_result = trace_execution(artifact.prompt_hash, "tr-all-rels", {"success": True}, _TS + 5)
        all_rels = prov_rels + safety_rels + exec_result.adg_relations
        for _, rel, _ in all_rels:
            assert rel in ALL_PROMPT_RELATIONS, f"Unknown relation type emitted: {rel!r}"

    def test_provenance_chain_prompt_hash_consistent(self):
        from system_learning.engines.prompt_execution_tracer import trace_execution
        from system_learning.engines.prompt_provenance_builder import build_compiled_prompt

        req = _make_build_request()
        build_result = build_compiled_prompt(req)
        artifact = build_result.artifact

        exec_result = trace_execution(
            artifact.prompt_hash,
            "tr-chain-001",
            {"success": True, "retrieval_groundedness_score": 0.85},
            _TS + 100,
        )
        # The outcome record should reference the same prompt hash
        assert exec_result.outcome_record.prompt_hash == artifact.prompt_hash
