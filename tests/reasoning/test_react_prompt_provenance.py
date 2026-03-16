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
