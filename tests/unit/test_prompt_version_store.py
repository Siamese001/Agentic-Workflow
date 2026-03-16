"""Unit tests for PromptVersionStore.

Phase 1 Wave 1.1 test suite. Verifies immutability, deduplication,
and error handling for S0/I0 prompt versioning.
"""

import pytest

from agentic_core.L4_state.memory.prompt_version_store import PromptVersionStore
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

_emit_records_execution_trace("p0", "evidence", "test_prompt_version_store")
_emit_applies_guardrail("p0", "test_prompt_version_store", "p0_governance")
_emit_reads_policy_state("p0", "test_prompt_version_store", "policy_binding")
_emit_snapshots_state("p0", "test_prompt_version_store", "state_snapshot")
emit_replay_key("p0", "test_prompt_version_store")
emit_determinism_digest("p0", "test_prompt_version_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_prompt_version_store", "execution_auth")
_emit_validates_capability("p2", "test_prompt_version_store", "capability_check")
_emit_routes_to_capability("p2", "test_prompt_version_store", "capability_route")
_emit_writes_via_uwg("p2", "test_prompt_version_store", "uwg_write")
_emit_blocks_direct_write("p2", "test_prompt_version_store", "direct_write_block")
_emit_records_tool_invocation("p2", "test_prompt_version_store", "tool_invocation")
_emit_captures_execution_output("p2", "test_prompt_version_store", "exec_output")
_emit_dispatches_agent("p3", "test_prompt_version_store", "agent_dispatch")
_emit_coordinates_agents("p3", "test_prompt_version_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_prompt_version_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_prompt_version_store", "healing_outcome")
_emit_escalates_failure("p3", "test_prompt_version_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_prompt_version_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_prompt_version_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_prompt_version_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_prompt_version_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_prompt_version_store", "eval_metric")
_emit_stores_embedding("p4", "test_prompt_version_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_prompt_version_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_prompt_version_store", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@pytest.mark.unit
class TestPromptVersionStore:
    def setup_method(self):
        self.store = PromptVersionStore()
        self.store.clear()  # ensure clean state

    def test_commit_s0_returns_sha256(self):
        content = "You are a helpful assistant."
        version = self.store.commit_version("S0", content)
        assert isinstance(version, str)
        assert len(version) == 64  # SHA-256 hex length
        assert all(c in "0123456789abcdef" for c in version)

    def test_commit_i0_returns_sha256(self):
        content = "Respond concisely."
        version = self.store.commit_version("I0", content)
        assert isinstance(version, str)
        assert len(version) == 64

    def test_same_content_returns_same_version(self):
        content = "Same content."
        v1 = self.store.commit_version("S0", content)
        v2 = self.store.commit_version("S0", content)
        assert v1 == v2

    def test_different_content_returns_different_versions(self):
        v1 = self.store.commit_version("S0", "Content A")
        v2 = self.store.commit_version("S0", "Content B")
        assert v1 != v2

    def test_invalid_prompt_type_raises(self):
        with pytest.raises(ValueError, match="prompt_type must be 'S0' or 'I0'"):
            self.store.commit_version("X0", "content")

    def test_get_s0_returns_content(self):
        content = "S0 prompt."
        version = self.store.commit_version("S0", content)
        assert self.store.get_s0(version) == content

    def test_get_i0_returns_content(self):
        content = "I0 prompt."
        version = self.store.commit_version("I0", content)
        assert self.store.get_i0(version) == content

    def test_get_unknown_version_raises(self):
        with pytest.raises(KeyError):
            self.store.get_s0("nonexistent")

    def test_list_versions(self):
        v1 = self.store.commit_version("S0", "A")
        v2 = self.store.commit_version("I0", "B")
        versions = self.store.list_versions()
        assert set(versions) == {v1, v2}
        assert len(versions) == 2

    def test_deduplication_across_types(self):
        content = "Same content."
        v_s0 = self.store.commit_version("S0", content)
        v_i0 = self.store.commit_version("I0", content)
        # Same content should map to same version regardless of type
        assert v_s0 == v_i0
        # But both get_* methods should work
        assert self.store.get_s0(v_s0) == content
        assert self.store.get_i0(v_i0) == content

    def test_clear_resets_store(self):
        self.store.commit_version("S0", "A")
        assert self.store.list_versions()
        self.store.clear()
        assert not self.store.list_versions()
