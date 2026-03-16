"""
Tests for FLAT_DIRECTORIES enforcement.

Validates that validate_flat_directory() correctly rejects files nested
inside directories that must be flat (no subfolders).

[CREATED 2026-02-08] RCA: mixins/contracts/ was not caught because no
validator enforced the "flat" flag in SOVEREIGN_TERRITORIES.
"""

from __future__ import annotations

from agentic_core.L5_safety.config.structure_blueprint import (
    AGENTIC_CORE_DIR,
    FLAT_DIRECTORIES,
    validate_flat_directory,
)
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

_emit_records_execution_trace("p0", "evidence", "test_flat_directory_enforcement")
_emit_applies_guardrail("p0", "test_flat_directory_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_flat_directory_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_flat_directory_enforcement", "state_snapshot")
emit_replay_key("p0", "test_flat_directory_enforcement")
emit_determinism_digest("p0", "test_flat_directory_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_flat_directory_enforcement", "execution_auth")
_emit_validates_capability("p2", "test_flat_directory_enforcement", "capability_check")
_emit_routes_to_capability("p2", "test_flat_directory_enforcement", "capability_route")
_emit_writes_via_uwg("p2", "test_flat_directory_enforcement", "uwg_write")
_emit_blocks_direct_write("p2", "test_flat_directory_enforcement", "direct_write_block")
_emit_records_tool_invocation("p2", "test_flat_directory_enforcement", "tool_invocation")
_emit_captures_execution_output("p2", "test_flat_directory_enforcement", "exec_output")
_emit_dispatches_agent("p3", "test_flat_directory_enforcement", "agent_dispatch")
_emit_coordinates_agents("p3", "test_flat_directory_enforcement", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_flat_directory_enforcement", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_flat_directory_enforcement", "healing_outcome")
_emit_escalates_failure("p3", "test_flat_directory_enforcement", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_flat_directory_enforcement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_flat_directory_enforcement", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_flat_directory_enforcement", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_flat_directory_enforcement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_flat_directory_enforcement", "eval_metric")
_emit_stores_embedding("p4", "test_flat_directory_enforcement", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_flat_directory_enforcement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_flat_directory_enforcement", "exec_snapshot_link")


class TestFlatDirectories:
    """FLAT_DIRECTORIES constant is correctly defined."""

    def test_mixins_is_flat(self):
        assert "mixins" in FLAT_DIRECTORIES

    def test_base_agents_is_flat(self):
        assert "base_agents" in FLAT_DIRECTORIES

    def test_interfaces_is_flat(self):
        assert "interfaces" in FLAT_DIRECTORIES


class TestValidateFlatDirectory:
    """validate_flat_directory() catches nested files in flat directories."""

    def test_file_directly_in_mixins_is_ok(self):
        parts = (AGENTIC_CORE_DIR, "mixins", "meta_learning_mixin.py")
        assert validate_flat_directory(parts) is None

    def test_file_in_mixins_subfolder_is_violation(self):
        parts = (AGENTIC_CORE_DIR, "mixins", "contracts", "meta_learning_contract.py")
        result = validate_flat_directory(parts)
        assert result is not None
        assert result["domain"] == "mixins"
        assert result["illegal_child"] == "contracts"
        assert "FLAT VIOLATION" in result["message"]

    def test_file_directly_in_base_agents_is_ok(self):
        parts = (AGENTIC_CORE_DIR, "base_agents", "SovereignBaseAgent.py")
        assert validate_flat_directory(parts) is None

    def test_file_in_base_agents_subfolder_is_violation(self):
        parts = (AGENTIC_CORE_DIR, "base_agents", "legacy", "OldBase.py")
        result = validate_flat_directory(parts)
        assert result is not None
        assert result["domain"] == "base_agents"
        assert result["illegal_child"] == "legacy"

    def test_file_directly_in_interfaces_is_ok(self):
        parts = (AGENTIC_CORE_DIR, "interfaces", "IOrchestratorProtocol.py")
        assert validate_flat_directory(parts) is None

    def test_file_in_interfaces_subfolder_is_violation(self):
        parts = (AGENTIC_CORE_DIR, "interfaces", "v2", "INewProtocol.py")
        result = validate_flat_directory(parts)
        assert result is not None
        assert result["domain"] == "interfaces"

    def test_pycache_in_flat_dir_is_allowed(self):
        parts = (AGENTIC_CORE_DIR, "mixins", "__pycache__", "foo.cpython-312.pyc")
        assert validate_flat_directory(parts) is None

    def test_non_flat_directory_is_not_checked(self):
        parts = (AGENTIC_CORE_DIR, "L5_safety", "reasoning", "sub", "file.py")
        assert validate_flat_directory(parts) is None

    def test_deeply_nested_flat_violation(self):
        parts = (AGENTIC_CORE_DIR, "mixins", "a", "b", "file.py")
        result = validate_flat_directory(parts)
        assert result is not None
        assert result["illegal_child"] == "a"
