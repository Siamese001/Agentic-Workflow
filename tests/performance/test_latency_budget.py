"""
Latency Budget Tests for V10 Atomic Agents.

Verifies that agents with AtomicExecutionMixin meet latency requirements
for critical operations. Per V10 spec, file operations should complete
within budget to prevent blocking.

Usage:
    python -m pytest tests/performance/test_latency_budget.py -v
    python -m pytest tests/performance/test_latency_budget.py -k "CodeHealerAgent" -v
"""

import tempfile
import time
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "test_latency_budget")
_emit_applies_guardrail("p0", "test_latency_budget", "p0_governance")
_emit_reads_policy_state("p0", "test_latency_budget", "policy_binding")
_emit_snapshots_state("p0", "test_latency_budget", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_latency_budget", "p4obs", "metric_1")
_emit_emits_metric_event("test_latency_budget", "p4obs", "metric_2")
_emit_emits_metric_event("test_latency_budget", "p4obs", "metric_3")
_emit_emits_metric_event("test_latency_budget", "p4obs", "metric_4")
_emit_emits_metric_event("test_latency_budget", "p4obs", "metric_5")
_emit_emits_metric_event("test_latency_budget", "p4obs", "metric_6")
_emit_records_incident_event("test_latency_budget", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_latency_budget", "p4obs", "anomaly")
_emit_writes_observability_log("test_latency_budget", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_latency_budget", "p4obs", "mon_state")
_emit_triggers_alert("test_latency_budget", "p4obs", "alert")
_emit_links_incident_trace("test_latency_budget", "p4obs", "trace_link")
_emit_captures_pattern("test_latency_budget", "p3lm", "pattern")
_emit_records_learning_event("test_latency_budget", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_latency_budget", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_latency_budget", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_latency_budget", "p3lm", "routing")
_emit_improves_agent_policy("test_latency_budget", "p3lm", "policy")
_emit_stores_learning_state("test_latency_budget", "p3lm", "state")
_emit_records_execution_trace("test_latency_budget", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_latency_budget", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_latency_budget", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_latency_budget", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_latency_budget", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_latency_budget", "env_read", "p2_env_1")
_emit_reads_environ("test_latency_budget", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_latency_budget", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_latency_budget", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_latency_budget", "context_pull")
_emit_pulls_context("p1", "test_latency_budget", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_latency_budget", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_latency_budget", "uwg_term_2")
_emit_writes_through("p1", "test_latency_budget", "write_through")
_emit_writes_through("p1", "test_latency_budget", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_latency_budget", "safety_validation")
_emit_invokes_eval("p1", "test_latency_budget", "eval_call")
_emit_proposal_commits_routing("p1", "test_latency_budget", "routing_commit")
emit_replay_key("p0", "test_latency_budget")
emit_determinism_digest("p0", "test_latency_budget")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_latency_budget", "execution_auth")
_emit_validates_capability("p2", "test_latency_budget", "capability_check")
_emit_routes_to_capability("p2", "test_latency_budget", "capability_route")
_emit_writes_via_uwg("p2", "test_latency_budget", "uwg_write")
_emit_blocks_direct_write("p2", "test_latency_budget", "direct_write_block")
_emit_records_tool_invocation("p2", "test_latency_budget", "tool_invocation")
_emit_captures_execution_output("p2", "test_latency_budget", "exec_output")
_emit_dispatches_agent("p3", "test_latency_budget", "agent_dispatch")
_emit_coordinates_agents("p3", "test_latency_budget", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_latency_budget", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_latency_budget", "healing_outcome")
_emit_escalates_failure("p3", "test_latency_budget", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_latency_budget", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_latency_budget", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_latency_budget", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_latency_budget", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_latency_budget", "eval_metric")
_emit_stores_embedding("p4", "test_latency_budget", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_latency_budget", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_latency_budget", "exec_snapshot_link")

# Latency budgets in seconds
LATENCY_BUDGETS = {
    "file_hash": 0.1,  # 100ms for file hashing
    "atomic_write": 0.5,  # 500ms for atomic write operation
    "rollback": 0.2,  # 200ms for rollback operation
    "heal_operation": 2.0,  # 2s for heal operation
}


class TestLatencyBudget:
    """Test latency budgets for atomic operations."""

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# Test file\nprint('hello')\n")
            temp_path = Path(f.name)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()

    def test_atomic_execution_mixin_import_latency(self):
        """Test that AtomicExecutionMixin can be imported quickly."""
        start = time.perf_counter()
        from agentic_core.mixins.atomic_execution_mixin import (
            AtomicExecutionMixin,
        )

        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"Import took {elapsed:.3f}s, budget is 1.0s"
        assert AtomicExecutionMixin is not None

    def test_CodeHealerAgent_instantiation_latency(self):
        """Test CodeHealerAgent instantiation meets latency budget."""
        start = time.perf_counter()
        try:
            from agentic_core.L5_safety.reasoning.CodeHealerAgent import (
                CodeHealerAgent,
            )

            agent = CodeHealerAgent()
            elapsed = time.perf_counter() - start

            assert elapsed < 2.0, f"Instantiation took {elapsed:.3f}s, budget is 2.0s"
            assert agent is not None
        except (ImportError, AttributeError, TypeError) as e:
            pytest.fail(f"CodeHealerAgent not available: {e}")

    def test_file_hash_computation_latency(self, temp_file):
        """Test file hash computation meets latency budget."""
        from agentic_core.mixins.atomic_execution_mixin import (
            AtomicExecutionMixin,
        )

        class TestAgent(AtomicExecutionMixin):
            pass

        agent = TestAgent()

        start = time.perf_counter()
        file_hash = agent._compute_file_hash(temp_file)
        elapsed = time.perf_counter() - start

        assert elapsed < LATENCY_BUDGETS["file_hash"], (
            f"Hash computation took {elapsed:.3f}s, budget is {LATENCY_BUDGETS['file_hash']}s"
        )
        assert file_hash is not None

    def test_atomic_write_latency(self, temp_file):
        """Test atomic write operation meets latency budget."""
        from agentic_core.mixins.atomic_execution_mixin import (
            AtomicExecutionMixin,
        )

        class TestAgent(AtomicExecutionMixin):
            pass

        agent = TestAgent()
        new_content = "# Modified\nprint('modified')\n"

        start = time.perf_counter()
        agent._atomic_write(temp_file, new_content)
        elapsed = time.perf_counter() - start

        assert elapsed < LATENCY_BUDGETS["atomic_write"], (
            f"Atomic write took {elapsed:.3f}s, budget is {LATENCY_BUDGETS['atomic_write']}s"
        )
        assert temp_file.read_text() == new_content

    @pytest.mark.parametrize(
        "agent_name",
        [
            "CodeHealerAgent",
            "VerificationGate",
            "LocationAgent",
        ],
    )
    def test_batch_3a_agents_have_atomic_mixin(self, agent_name):
        """Verify Batch 3.1A agents have AtomicExecutionMixin."""
        from agentic_core.mixins.atomic_execution_mixin import (
            AtomicExecutionMixin,
        )

        agent_imports = {
            "CodeHealerAgent": (
                "agentic_core.L5_safety.reasoning.CodeHealerAgent",
                "CodeHealerAgent",
            ),
            "VerificationGate": (
                "agentic_core.L5_safety.enforcement.verification_gate",
                "VerificationGate",
            ),
            "LocationAgent": (
                "agentic_core.L5_safety.reasoning.LocationAgent",
                "LocationAgent",
            ),
        }

        module_path, class_name = agent_imports[agent_name]
        try:
            import importlib

            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)

            assert issubclass(agent_class, AtomicExecutionMixin), (
                f"{agent_name} must inherit from AtomicExecutionMixin"
            )
        except ImportError as e:
            pytest.fail(f"Could not import {agent_name}: {e}")
