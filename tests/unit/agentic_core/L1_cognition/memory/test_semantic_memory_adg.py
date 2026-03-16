"""ADG-driven tests for L1_cognition/memory/SemanticMemory.py — fan_in=1."""
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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "test_semantic_memory_adg")
_emit_applies_guardrail("p0", "test_semantic_memory_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_semantic_memory_adg", "policy_binding")
_emit_snapshots_state("p0", "test_semantic_memory_adg", "state_snapshot")
emit_replay_key("p0", "test_semantic_memory_adg")
emit_determinism_digest("p0", "test_semantic_memory_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_semantic_memory_adg", "execution_auth")
_emit_validates_capability("p2", "test_semantic_memory_adg", "capability_check")
_emit_routes_to_capability("p2", "test_semantic_memory_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_semantic_memory_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_semantic_memory_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_semantic_memory_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_semantic_memory_adg", "exec_output")
_emit_dispatches_agent("p3", "test_semantic_memory_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_semantic_memory_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_semantic_memory_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_semantic_memory_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_semantic_memory_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_semantic_memory_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_semantic_memory_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_semantic_memory_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_semantic_memory_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_semantic_memory_adg", "eval_metric")
_emit_stores_embedding("p4", "test_semantic_memory_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_semantic_memory_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_semantic_memory_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.memory.SemanticMemory import (
    EmbeddingProvider,
    SemanticMemory,
    VectorIndex,
)


class TestEmbeddingProvider:
    def test_creates_with_default(self):
        ep = EmbeddingProvider()
        assert ep.model == "default"

    def test_embed_returns_list(self):
        ep = EmbeddingProvider()
        result = ep.embed("hello world")
        assert isinstance(result, list)
        assert len(result) == 384


class TestVectorIndex:
    def test_creates(self):
        idx = VectorIndex()
        assert idx.dimension == 384

    def test_add_and_search(self):
        idx = VectorIndex()
        idx.add("key1", [0.1] * 384)
        results = idx.search([0.0] * 384, top_k=5)
        assert "key1" in results

    def test_search_respects_top_k(self):
        idx = VectorIndex()
        for i in range(10):
            idx.add(f"k{i}", [float(i)] * 384)
        results = idx.search([0.0] * 384, top_k=3)
        assert len(results) <= 3


class TestSemanticMemory:
    def test_creates(self):
        mem = SemanticMemory()
        assert mem is not None

    def test_store_and_retrieve(self):
        mem = SemanticMemory()
        mem.store("concept", "AI is cool")
        val = mem.retrieve("concept")
        assert val == "AI is cool"

    def test_retrieve_missing_returns_none(self):
        mem = SemanticMemory()
        assert mem.retrieve("nonexistent") is None
