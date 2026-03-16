"""
W5 Execution Trace and Plan Hash Tests

Tests for ExecutionTrace structure and plan_hash binding.
Validates canonical JSON formatting and deterministic hashing.
"""

import hashlib
import json

import pytest

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler
from agentic_core.L3_orchestration.types.execution_trace_types import (
    ExecutionTrace,
    canonical_json,
    compute_plan_hash,
    create_execution_trace_skeleton,
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

_emit_applies_guardrail("p0", "test_executiontrace_plan_hash", "p0_governance")
_emit_reads_policy_state("p0", "test_executiontrace_plan_hash", "policy_binding")
_emit_snapshots_state("p0", "test_executiontrace_plan_hash", "state_snapshot")
emit_replay_key("p0", "test_executiontrace_plan_hash")
emit_determinism_digest("p0", "test_executiontrace_plan_hash")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_executiontrace_plan_hash", "execution_auth")
_emit_validates_capability("p2", "test_executiontrace_plan_hash", "capability_check")
_emit_routes_to_capability("p2", "test_executiontrace_plan_hash", "capability_route")
_emit_writes_via_uwg("p2", "test_executiontrace_plan_hash", "uwg_write")
_emit_blocks_direct_write("p2", "test_executiontrace_plan_hash", "direct_write_block")
_emit_records_tool_invocation("p2", "test_executiontrace_plan_hash", "tool_invocation")
_emit_captures_execution_output("p2", "test_executiontrace_plan_hash", "exec_output")
_emit_dispatches_agent("p3", "test_executiontrace_plan_hash", "agent_dispatch")
_emit_coordinates_agents("p3", "test_executiontrace_plan_hash", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_executiontrace_plan_hash", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_executiontrace_plan_hash", "healing_outcome")
_emit_escalates_failure("p3", "test_executiontrace_plan_hash", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_executiontrace_plan_hash", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_executiontrace_plan_hash", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_executiontrace_plan_hash", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_executiontrace_plan_hash", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_executiontrace_plan_hash", "eval_metric")
_emit_stores_embedding("p4", "test_executiontrace_plan_hash", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_executiontrace_plan_hash", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_executiontrace_plan_hash", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


class TestW5ExecutionTracePlanHash:
    """Test suite for W5 execution trace and plan hash functionality."""

    @pytest.fixture
    def sample_payload(self):
        """Create sample governed payload."""
        return AirlockAssembler.assemble(
            s0_system="Test System",
            i0_instructional="Test Instructions",
            c0_context="Test Context",
            u0_user_prompt="Test prompt",
        )

    @pytest.fixture
    def sample_plan(self):
        """Create sample plan for testing."""
        return {
            "trace_id": "test_trace_001",
            "policy_hash": "policy_hash_001",
            "route_mode": "B",
            "governed_payload": {
                "s0_system": "Test System",
                "i0_instructional": "Test Instructions",
                "c0_context": "Test Context",
                "u0_user_prompt": "Test prompt",
            },
            "allowed_tools": ["tool1", "tool2"],
            "orchestration_steps": [
                {
                    "step_id": 1,
                    "action": "process_payload",
                    "deterministic": True,
                }
            ],
        }

    def test_canonical_json_format(self):
        """Test canonical JSON formatting requirements."""
        data = {
            "z_key": "last",
            "a_key": "first",
            "m_key": "middle",
            "nested": {
                "z_nested": "nested_last",
                "a_nested": "nested_first",
            },
            "list_items": ["item2", "item1"],
        }

        canonical = canonical_json(data)

        # Verify alphabetical key sorting
        assert canonical.startswith('{"a_key":"first","list_items":["item2","item1"],"m_key":"middle"')

        # Verify nested key sorting
        assert '"a_nested":"nested_first"' in canonical
        assert '"z_nested":"nested_last"' in canonical

        # Verify no whitespace variance
        assert "  " not in canonical
        assert "\n" not in canonical
        assert "\t" not in canonical

        # Verify UTF-8 handling
        data_unicode = {"unicode_key": "测试"}
        canonical_unicode = canonical_json(data_unicode)
        assert "测试" in canonical_unicode

    def test_canonical_json_deterministic(self):
        """Test canonical JSON produces identical output for identical input."""
        data = {
            "b": "value_b",
            "a": "value_a",
            "c": "value_c",
        }

        canonical1 = canonical_json(data)
        canonical2 = canonical_json(data)

        assert canonical1 == canonical2

    def test_plan_hash_computation(self, sample_plan):
        """Test plan hash computation from canonical plan."""
        plan_hash = compute_plan_hash(sample_plan)

        # Verify hash format
        assert len(plan_hash) == 64
        assert all(c in "0123456789abcdef" for c in plan_hash)

        # Verify deterministic
        hash2 = compute_plan_hash(sample_plan)
        assert plan_hash == hash2

        # Verify hash is SHA256 of canonical JSON
        canonical = canonical_json(sample_plan)
        expected_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        assert plan_hash == expected_hash

    def test_plan_hash_changes_with_plan_modification(self, sample_plan):
        """Test that plan hash changes when plan is modified."""
        original_hash = compute_plan_hash(sample_plan)

        # Modify plan
        modified_plan = sample_plan.copy()
        modified_plan["route_mode"] = "C"

        new_hash = compute_plan_hash(modified_plan)

        assert original_hash != new_hash

    def test_execution_trace_creation(self, sample_payload):
        """Test execution trace skeleton creation."""
        trace_id = "test_trace_001"
        plan_hash = "plan_hash_001"

        trace = create_execution_trace_skeleton(
            trace_id=trace_id,
            plan_hash=plan_hash,
            governed_payload=sample_payload,
            actor="Test_Actor",
            target="test_target",
        )

        # Verify required fields
        assert trace.trace_id == trace_id
        assert trace.plan_hash == plan_hash
        assert trace.actor == "Test_Actor"
        assert trace.target == "test_target"
        assert trace.timestamp is not None
        assert trace.governed_payload_hash is not None

        # Verify governed payload hash computation
        payload_dict = {
            "s0_system": sample_payload.s0_system,
            "i0_instructional": sample_payload.i0_instructional,
            "c0_context": sample_payload.c0_context,
            "u0_user_prompt": sample_payload.u0_user_prompt,
            "manifest_hash": sample_payload.manifest_hash,
            "routing_hash": sample_payload.routing_hash,
        }
        expected_payload_hash = hashlib.sha256(canonical_json(payload_dict).encode("utf-8")).hexdigest()
        assert trace.governed_payload_hash == expected_payload_hash

    def test_execution_trace_to_dict(self):
        """Test execution trace serialization."""
        trace = ExecutionTrace(
            trace_id="test_trace",
            plan_hash="plan_hash",
            actor="Test_Actor",
            target="test_target",
            diff={"field": "value"},
            policy_hash="policy_hash",
            timestamp="2023-01-01T00:00:00Z",
            prev_hash="prev_hash",
            replay_key="replay_key",
            governed_payload_hash="payload_hash",
        )

        trace_dict = trace.to_dict()

        # Verify all fields are present
        expected_keys = {
            "trace_id",
            "plan_hash",
            "actor",
            "target",
            "diff",
            "policy_hash",
            "timestamp",
            "prev_hash",
            "replay_key",
            "governed_payload_hash",
        }
        assert set(trace_dict.keys()) == expected_keys

        # Verify values
        assert trace_dict["trace_id"] == "test_trace"
        assert trace_dict["plan_hash"] == "plan_hash"
        assert trace_dict["actor"] == "Test_Actor"
        assert trace_dict["target"] == "test_target"

    def test_replay_key_computation(self):
        """Test replay key computation."""
        trace = ExecutionTrace(
            trace_id="test_trace",
            plan_hash="plan_hash",
            actor="Test_Actor",
        )

        transcript_hash = "transcript_hash_001"
        replay_key = trace.compute_replay_key(transcript_hash)

        # Verify replay key format
        assert len(replay_key) == 64
        assert all(c in "0123456789abcdef" for c in replay_key)

        # Verify replay key computation
        expected = hashlib.sha256(f"test_traceplan_hash{transcript_hash}".encode()).hexdigest()
        assert replay_key == expected

    def test_replay_key_deterministic(self):
        """Test replay key is deterministic."""
        trace = ExecutionTrace(
            trace_id="test_trace",
            plan_hash="plan_hash",
            actor="Test_Actor",
        )

        transcript_hash = "transcript_hash_001"

        key1 = trace.compute_replay_key(transcript_hash)
        key2 = trace.compute_replay_key(transcript_hash)

        assert key1 == key2

    def test_replay_key_changes_with_inputs(self):
        """Test replay key changes with different inputs."""
        trace = ExecutionTrace(
            trace_id="test_trace",
            plan_hash="plan_hash",
            actor="Test_Actor",
        )

        # Different transcript hash
        key1 = trace.compute_replay_key("transcript_1")
        key2 = trace.compute_replay_key("transcript_2")
        assert key1 != key2

        # Different trace_id
        trace2 = ExecutionTrace(
            trace_id="different_trace",
            plan_hash="plan_hash",
            actor="Test_Actor",
        )
        key3 = trace2.compute_replay_key("transcript_1")
        assert key1 != key3

        # Different plan_hash
        trace3 = ExecutionTrace(
            trace_id="test_trace",
            plan_hash="different_plan",
            actor="Test_Actor",
        )
        key4 = trace3.compute_replay_key("transcript_1")
        assert key1 != key4

    def test_governed_payload_hash_includes_all_fields(self, sample_payload):
        """Test governed payload hash includes all required fields."""
        trace = create_execution_trace_skeleton(
            trace_id="test_trace",
            plan_hash="plan_hash",
            governed_payload=sample_payload,
        )

        # Verify hash includes manifest and routing hashes
        payload_dict = {
            "s0_system": sample_payload.s0_system,
            "i0_instructional": sample_payload.i0_instructional,
            "c0_context": sample_payload.c0_context,
            "u0_user_prompt": sample_payload.u0_user_prompt,
            "manifest_hash": sample_payload.manifest_hash,
            "routing_hash": sample_payload.routing_hash,
        }

        expected_hash = hashlib.sha256(canonical_json(payload_dict).encode("utf-8")).hexdigest()

        assert trace.governed_payload_hash == expected_hash

    def test_execution_trace_with_different_payloads(self):
        """Test execution trace with different payload types."""
        # Simple payload
        simple_payload = AirlockAssembler.assemble(
            s0_system="System",
            i0_instructional="Instructions",
            c0_context="Context",
            u0_user_prompt="Simple",
        )

        # Complex payload
        complex_payload = AirlockAssembler.assemble(
            s0_system="Complex System",
            i0_instructional="Complex Instructions",
            c0_context="Complex Context",
            u0_user_prompt="1. Task 1\n2. Task 2\n3. Task 3",
        )

        trace1 = create_execution_trace_skeleton(
            trace_id="trace_1",
            plan_hash="plan_hash",
            governed_payload=simple_payload,
        )

        trace2 = create_execution_trace_skeleton(
            trace_id="trace_2",
            plan_hash="plan_hash",
            governed_payload=complex_payload,
        )

        # Hashes should be different
        assert trace1.governed_payload_hash != trace2.governed_payload_hash

    def test_canonical_json_handles_complex_structures(self):
        """Test canonical JSON handles complex nested structures."""
        complex_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "array": [3, 1, 2],
                        "string": "value",
                        "number": 42,
                        "boolean": True,
                        "null": None,
                    },
                    "z_key": "should be last",
                    "a_key": "should be first",
                },
            },
            "root_array": ["item3", "item1", "item2"],
            "root_z": "last",
            "root_a": "first",
        }

        canonical = canonical_json(complex_data)

        # Should not raise any exceptions
        assert isinstance(canonical, str)
        assert len(canonical) > 0

        # Should be parseable back to equivalent structure
        parsed = json.loads(canonical)
        assert parsed == complex_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
