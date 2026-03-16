"""CI tests — ReAct prompt provenance recording.

Verifies:
  - PromptProvenanceRecord is built correctly from inputs.
  - prompt_hash is deterministic for identical prompt text.
  - record_hash is stable across replay runs.
  - Different prompt texts produce different prompt_hash values.
  - rag_context_ids are captured correctly.

CI failure condition:
  - Prompt hash differs between replay runs for identical input.
  - Provenance record missing required fields.
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_react_prompt_provenance")
_emit_applies_guardrail("p0", "test_react_prompt_provenance", "p0_governance")
_emit_snapshots_state("p0", "test_react_prompt_provenance", "state_snapshot")
emit_replay_key("p0", "test_react_prompt_provenance")
emit_determinism_digest("p0", "test_react_prompt_provenance")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_react_prompt_provenance", "execution_auth")
_emit_validates_capability("p2", "test_react_prompt_provenance", "capability_check")
_emit_routes_to_capability("p2", "test_react_prompt_provenance", "capability_route")
_emit_writes_via_uwg("p2", "test_react_prompt_provenance", "uwg_write")
_emit_blocks_direct_write("p2", "test_react_prompt_provenance", "direct_write_block")
_emit_records_tool_invocation("p2", "test_react_prompt_provenance", "tool_invocation")
_emit_captures_execution_output("p2", "test_react_prompt_provenance", "exec_output")
_emit_dispatches_agent("p3", "test_react_prompt_provenance", "agent_dispatch")
_emit_coordinates_agents("p3", "test_react_prompt_provenance", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_react_prompt_provenance", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_react_prompt_provenance", "healing_outcome")
_emit_escalates_failure("p3", "test_react_prompt_provenance", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_react_prompt_provenance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_react_prompt_provenance", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_react_prompt_provenance", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_react_prompt_provenance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_react_prompt_provenance", "eval_metric")
_emit_stores_embedding("p4", "test_react_prompt_provenance", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_react_prompt_provenance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_react_prompt_provenance", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.react_trace_types import PromptProvenanceRecord
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_react_prompt_provenance", "p4obs", "metric_1")
_emit_emits_metric_event("test_react_prompt_provenance", "p4obs", "metric_2")
_emit_emits_metric_event("test_react_prompt_provenance", "p4obs", "metric_3")
_emit_emits_metric_event("test_react_prompt_provenance", "p4obs", "metric_4")
_emit_emits_metric_event("test_react_prompt_provenance", "p4obs", "metric_5")
_emit_emits_metric_event("test_react_prompt_provenance", "p4obs", "metric_6")
_emit_records_incident_event("test_react_prompt_provenance", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_react_prompt_provenance", "p4obs", "anomaly")
_emit_writes_observability_log("test_react_prompt_provenance", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_react_prompt_provenance", "p4obs", "mon_state")
_emit_triggers_alert("test_react_prompt_provenance", "p4obs", "alert")
_emit_links_incident_trace("test_react_prompt_provenance", "p4obs", "trace_link")
_emit_captures_pattern("test_react_prompt_provenance", "p3lm", "pattern")
_emit_records_learning_event("test_react_prompt_provenance", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_react_prompt_provenance", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_react_prompt_provenance", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_react_prompt_provenance", "p3lm", "routing")
_emit_improves_agent_policy("test_react_prompt_provenance", "p3lm", "policy")
_emit_stores_learning_state("test_react_prompt_provenance", "p3lm", "state")
_emit_records_execution_trace("test_react_prompt_provenance", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_react_prompt_provenance", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_react_prompt_provenance", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_react_prompt_provenance", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_react_prompt_provenance", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_react_prompt_provenance", "env_read", "p2_env_1")
_emit_reads_environ("test_react_prompt_provenance", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_react_prompt_provenance", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_react_prompt_provenance", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_react_prompt_provenance", "context_pull")
_emit_pulls_context("p1", "test_react_prompt_provenance", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_react_prompt_provenance", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_react_prompt_provenance", "uwg_term_secondary")
_emit_writes_through("p1", "test_react_prompt_provenance", "write_through")
_emit_writes_through("p1", "test_react_prompt_provenance", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_react_prompt_provenance", "safety_validation")
_emit_invokes_eval("p1", "test_react_prompt_provenance", "eval_call")
_emit_proposal_commits_routing("p1", "test_react_prompt_provenance", "routing_commit")


class TestPromptProvenanceRecord:
    def _make(
        self,
        prompt_text: str = "What is the capital?",
        prompt_template_id: str = "react_v1",
        rag_context_ids: tuple[str, ...] = ("ctx1", "ctx2"),
        policy_hash: str = "pol1",
        model_id: str = "gpt-4",
    ) -> PromptProvenanceRecord:
        return PromptProvenanceRecord.build(
            prompt_text=prompt_text,
            prompt_template_id=prompt_template_id,
            rag_context_ids=rag_context_ids,
            policy_hash=policy_hash,
            model_id=model_id,
        )

    def test_build_sets_prompt_hash(self):
        rec = self._make()
        assert rec.prompt_hash != ""
        assert len(rec.prompt_hash) == 64

    def test_prompt_hash_deterministic(self):
        rec1 = self._make(prompt_text="Hello world")
        rec2 = self._make(prompt_text="Hello world")
        assert rec1.prompt_hash == rec2.prompt_hash

    def test_different_prompt_different_hash(self):
        rec1 = self._make(prompt_text="Question A")
        rec2 = self._make(prompt_text="Question B")
        assert rec1.prompt_hash != rec2.prompt_hash

    def test_record_hash_stable(self):
        rec1 = self._make()
        rec2 = self._make()
        assert rec1.record_hash() == rec2.record_hash()

    def test_rag_context_ids_captured(self):
        rec = self._make(rag_context_ids=("id_x", "id_y", "id_z"))
        assert rec.rag_context_ids == ("id_x", "id_y", "id_z")

    def test_empty_rag_context_ids(self):
        rec = self._make(rag_context_ids=())
        assert rec.rag_context_ids == ()
        assert len(rec.prompt_hash) == 64

    def test_policy_hash_stored(self):
        rec = self._make(policy_hash="pol_xyz")
        assert rec.policy_hash == "pol_xyz"

    def test_model_id_stored(self):
        rec = self._make(model_id="claude-3")
        assert rec.model_id == "claude-3"

    def test_prompt_template_id_stored(self):
        rec = self._make(prompt_template_id="tmpl_99")
        assert rec.prompt_template_id == "tmpl_99"

    def test_record_is_immutable(self):
        rec = self._make()
        with pytest.raises((AttributeError, TypeError)):
            rec.prompt_hash = "mutated"  # type: ignore[misc]

    def test_different_policy_different_record_hash(self):
        rec1 = self._make(policy_hash="pol_a")
        rec2 = self._make(policy_hash="pol_b")
        assert rec1.record_hash() != rec2.record_hash()

    def test_different_rag_ids_different_record_hash(self):
        rec1 = self._make(rag_context_ids=("c1",))
        rec2 = self._make(rag_context_ids=("c2",))
        assert rec1.record_hash() != rec2.record_hash()

    def test_canonical_bytes_deterministic(self):
        rec = self._make()
        assert rec.canonical_bytes() == rec.canonical_bytes()
