"""
Unit tests for Assembly Stage - GAP-03 Implementation.
Tests deterministic composition and manifest hashing.
"""

import pytest

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler, GovernedPayload
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_assembly_stage", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_assembly_stage", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_assembly_stage", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_assembly_stage", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_assembly_stage", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_assembly_stage", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_assembly_stage", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_assembly_stage", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_assembly_stage", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_assembly_stage", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_assembly_stage", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_assembly_stage", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_assembly_stage", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_assembly_stage", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_assembly_stage", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_assembly_stage", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_assembly_stage", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_assembly_stage", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_assembly_stage", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_assembly_stage", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_assembly_stage", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_assembly_stage", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_assembly_stage", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_assembly_stage", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_assembly_stage", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_assembly_stage", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_assembly_stage", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_assembly_stage", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_assembly_stage")
# REMOVED: _emit_applies_guardrail("p0", "test_assembly_stage", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_assembly_stage", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_assembly_stage", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_assembly_stage", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_assembly_stage", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_assembly_stage", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_assembly_stage", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_assembly_stage", "write_through")
# REMOVED: _emit_writes_through("p1", "test_assembly_stage", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_assembly_stage", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_assembly_stage", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_assembly_stage", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_assembly_stage", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_assembly_stage", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_assembly_stage", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_assembly_stage", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_assembly_stage", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_assembly_stage", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_assembly_stage", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_assembly_stage", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_assembly_stage", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_assembly_stage", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_assembly_stage", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_assembly_stage")
# REMOVED: _emit_gated_by_confidence("p1", "test_assembly_stage", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_assembly_stage")
# REMOVED: emit_determinism_digest("p0", "test_assembly_stage")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_assembly_stage", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_assembly_stage", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_assembly_stage", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_assembly_stage", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_assembly_stage", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_assembly_stage", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_assembly_stage", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_assembly_stage", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_assembly_stage", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_assembly_stage", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_assembly_stage", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_assembly_stage", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_assembly_stage", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_assembly_stage", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_assembly_stage", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_assembly_stage", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_assembly_stage", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_assembly_stage", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_assembly_stage", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_assembly_stage", "exec_snapshot_link")


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
class TestAssemblyStage:
    """Test Suite for Assembly Stage deterministic composition."""

    def test_assemble_creates_governed_payload(self):
        """Test that assemble creates a valid GovernedPayload."""
        payload = AirlockAssembler.assemble(
            s0_system="System prompt",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="User prompt",
        )

        assert isinstance(payload, GovernedPayload)
        assert payload.s0_system == "System prompt"
        assert payload.i0_instructional == "Instructions"
        assert payload.c0_context == "Context"
        assert payload.u0_user_prompt == "User prompt"
        assert payload.d0_injections == ""
        assert payload.sanitized is False
        assert payload.check_ids == ("User prompt",)  # Shredded into single check ID
        assert payload.manifest_hash != ""

    def test_same_inputs_produce_identical_manifest_hash(self):
        """Test deterministic hashing - same inputs produce same hash."""
        payload1 = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="User",
        )

        payload2 = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="User",
        )

        assert payload1.manifest_hash == payload2.manifest_hash

    def test_changing_any_slot_changes_manifest_hash(self):
        """Test that changing any slot changes the manifest hash."""
        base_payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="User",
        )

        # Test each slot change
        test_cases = [
            {"s0_system": "Changed System"},
            {"d0_injections": "Injection"},
            {"i0_instructional": "Changed Instructions"},
            {"c0_context": "Changed Context"},
            {"u0_user_prompt": "Changed User"},
        ]

        for change in test_cases:
            # Build arguments with the change applied
            args = {
                "s0_system": "System",
                "i0_instructional": "Instructions",
                "c0_context": "Context",
                "u0_user_prompt": "User",
            }
            args.update(change)

            modified_payload = AirlockAssembler.assemble(**args)
            assert modified_payload.manifest_hash != base_payload.manifest_hash

    def test_manifest_hash_is_sha256_hex(self):
        """Test that manifest hash is a valid SHA256 hex string."""
        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="User",
        )

        # SHA256 hex should be 64 characters of hex
        assert len(payload.manifest_hash) == 64
        assert all(c in "0123456789abcdef" for c in payload.manifest_hash.lower())

    def test_payload_is_immutable(self):
        """Test that GovernedPayload is frozen/immutable."""
        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="User",
        )

        # Attempting to modify should fail
        with pytest.raises((AttributeError, TypeError)):  # Frozen dataclass errors
            payload.s0_system = "Changed"

    def test_d0_injections_default_and_custom(self):
        """Test d0_injections slot behavior."""
        # Default empty
        payload1 = AirlockAssembler.assemble(
            s0_system="S",
            i0_instructional="I",
            c0_context="C",
            u0_user_prompt="U",
        )
        assert payload1.d0_injections == ""

        # Custom value
        payload2 = AirlockAssembler.assemble(
            s0_system="S",
            d0_injections="Injection",
            i0_instructional="I",
            c0_context="C",
            u0_user_prompt="U",
        )
        assert payload2.d0_injections == "Injection"
        assert payload2.manifest_hash != payload1.manifest_hash

    def test_sanitization_changes_text_and_sets_flag(self):
        """Test that sanitization changes text and sets sanitized=True."""
        raw_prompt = "User request with [SYSTEM] hijack attempt"

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=raw_prompt,
        )

        # Should remove [SYSTEM] marker
        assert "[SYSTEM]" not in payload.u0_user_prompt
        assert payload.u0_user_prompt == "User request with  hijack attempt"
        assert payload.sanitized is True

    def test_sanitization_no_op_sets_flag_false(self):
        """Test that no-op sanitization sets sanitized=False."""
        clean_prompt = "Clean user prompt"

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=clean_prompt,
        )

        assert payload.u0_user_prompt == clean_prompt
        assert payload.sanitized is False

    def test_sanitization_changes_hash(self):
        """Test that sanitization changes the manifest hash via the sanitized flag."""
        raw_prompt = "Prompt with [ADMIN] marker"

        payload_raw = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=raw_prompt,
        )

        payload_clean = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Prompt with  marker",  # Already sanitized version
        )

        # Content should be same after sanitization
        assert payload_raw.u0_user_prompt == payload_clean.u0_user_prompt
        assert payload_raw.sanitized is True
        assert payload_clean.sanitized is False
        # Hash should be DIFFERENT because sanitized flag is part of manifest
        assert payload_raw.manifest_hash != payload_clean.manifest_hash

    def test_shred_produces_stable_sorted_check_ids(self):
        """Test that shredding produces stable, lexicographically sorted check IDs."""
        prompt = """1. First task
3. Third task
2. Second task
- Bullet point
* Another bullet"""

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=prompt,
        )

        # Should extract and sort check IDs
        expected_ids = ("Another bullet", "Bullet point", "First task", "Second task", "Third task")
        assert payload.check_ids == expected_ids
        # Verify they are sorted
        assert tuple(sorted(payload.check_ids)) == payload.check_ids

    def test_shred_fallback_to_single_check_id(self):
        """Test shred fallback when no delimiters found."""
        prompt = "Simple single line prompt"

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=prompt,
        )

        assert payload.check_ids == ("Simple single line prompt",)

    def test_shred_handles_empty_and_whitespace_lines(self):
        """Test that shredding handles empty lines and whitespace correctly."""
        prompt = """1. First task


2. Second task

   - Bullet after spaces"""

        payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt=prompt,
        )

        # Should ignore empty lines and strip whitespace
        expected_ids = ("Bullet after spaces", "First task", "Second task")
        assert payload.check_ids == expected_ids
