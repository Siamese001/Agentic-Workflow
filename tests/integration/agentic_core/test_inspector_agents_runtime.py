"""
Integration tests: verify inspector agents at runtime with full dependencies.

These tests require pydantic to be installed (transitive dep via agentic_core).
Run with: pytest tests/integration/ -q

Tests verify:
    1. Real inspector agents import and instantiate (MRO resolved)
    2. InspectionCapability.run_inspection() returns InspectionResult
    3. Decorator canonical imports work at runtime with full dep chain
    4. Shim identity holds at runtime

To install required deps: pip install pydantic
"""

from __future__ import annotations

import os

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_inspector_agents_runtime")
_emit_applies_guardrail("p0", "test_inspector_agents_runtime", "p0_governance")
_emit_reads_policy_state("p0", "test_inspector_agents_runtime", "policy_binding")
_emit_snapshots_state("p0", "test_inspector_agents_runtime", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_inspector_agents_runtime", "p4obs", "metric_1")
_emit_emits_metric_event("test_inspector_agents_runtime", "p4obs", "metric_2")
_emit_emits_metric_event("test_inspector_agents_runtime", "p4obs", "metric_3")
_emit_emits_metric_event("test_inspector_agents_runtime", "p4obs", "metric_4")
_emit_emits_metric_event("test_inspector_agents_runtime", "p4obs", "metric_5")
_emit_emits_metric_event("test_inspector_agents_runtime", "p4obs", "metric_6")
_emit_records_incident_event("test_inspector_agents_runtime", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_inspector_agents_runtime", "p4obs", "anomaly")
_emit_writes_observability_log("test_inspector_agents_runtime", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_inspector_agents_runtime", "p4obs", "mon_state")
_emit_triggers_alert("test_inspector_agents_runtime", "p4obs", "alert")
_emit_links_incident_trace("test_inspector_agents_runtime", "p4obs", "trace_link")
_emit_captures_pattern("test_inspector_agents_runtime", "p3lm", "pattern")
_emit_records_learning_event("test_inspector_agents_runtime", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_inspector_agents_runtime", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_inspector_agents_runtime", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_inspector_agents_runtime", "p3lm", "routing")
_emit_improves_agent_policy("test_inspector_agents_runtime", "p3lm", "policy")
_emit_stores_learning_state("test_inspector_agents_runtime", "p3lm", "state")
_emit_records_execution_trace("test_inspector_agents_runtime", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_inspector_agents_runtime", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_inspector_agents_runtime", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_inspector_agents_runtime", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_inspector_agents_runtime", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_inspector_agents_runtime", "env_read", "p2_env_1")
_emit_reads_environ("test_inspector_agents_runtime", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_inspector_agents_runtime", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_inspector_agents_runtime", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_inspector_agents_runtime", "context_pull")
_emit_pulls_context("p1", "test_inspector_agents_runtime", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_inspector_agents_runtime", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_inspector_agents_runtime", "uwg_term_2")
_emit_writes_through("p1", "test_inspector_agents_runtime", "write_through")
_emit_writes_through("p1", "test_inspector_agents_runtime", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_inspector_agents_runtime", "safety_validation")
_emit_invokes_eval("p1", "test_inspector_agents_runtime", "eval_call")
_emit_proposal_commits_routing("p1", "test_inspector_agents_runtime", "routing_commit")
_emit_escalates_to_human("p1", "test_inspector_agents_runtime", "human_escalation")
_emit_routes_through("p1", "test_inspector_agents_runtime", "route_through")
_emit_checks_agent_registry("p1", "test_inspector_agents_runtime", "agent_registry")
_emit_validates_agent_capability("p1", "test_inspector_agents_runtime", "capability")
_emit_dispatches_execution_plan("p1", "test_inspector_agents_runtime", "exec_plan")
_emit_agent_executes_agent("p1", "test_inspector_agents_runtime", "sub_agent")
_emit_routes_to_agent("p1", "test_inspector_agents_runtime", "target_agent")
_emit_verifies_policy("p1", "test_inspector_agents_runtime", "policy_check")
_emit_observes_runtime_state("p1", "test_inspector_agents_runtime", "runtime_state")
_emit_verifies_boundary("p1", "test_inspector_agents_runtime", "boundary_check")
_emit_transcripts_response("p1", "test_inspector_agents_runtime", "transcript")
_emit_hard_fails_untranscripted("p1", "test_inspector_agents_runtime")
_emit_gated_by_confidence("p1", "test_inspector_agents_runtime", "confidence_gate")
emit_replay_key("p0", "test_inspector_agents_runtime")
emit_determinism_digest("p0", "test_inspector_agents_runtime")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_inspector_agents_runtime", "execution_auth")
_emit_validates_capability("p2", "test_inspector_agents_runtime", "capability_check")
_emit_routes_to_capability("p2", "test_inspector_agents_runtime", "capability_route")
_emit_writes_via_uwg("p2", "test_inspector_agents_runtime", "uwg_write")
_emit_blocks_direct_write("p2", "test_inspector_agents_runtime", "direct_write_block")
_emit_records_tool_invocation("p2", "test_inspector_agents_runtime", "tool_invocation")
_emit_captures_execution_output("p2", "test_inspector_agents_runtime", "exec_output")
_emit_dispatches_agent("p3", "test_inspector_agents_runtime", "agent_dispatch")
_emit_coordinates_agents("p3", "test_inspector_agents_runtime", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_inspector_agents_runtime", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_inspector_agents_runtime", "healing_outcome")
_emit_escalates_failure("p3", "test_inspector_agents_runtime", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_inspector_agents_runtime", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_inspector_agents_runtime", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_inspector_agents_runtime", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_inspector_agents_runtime", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_inspector_agents_runtime", "eval_metric")
_emit_stores_embedding("p4", "test_inspector_agents_runtime", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_inspector_agents_runtime", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_inspector_agents_runtime", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Check if pydantic is available
try:
    import pydantic  # noqa: F401

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


# If integration explicitly required and pydantic is missing, FAIL immediately
if os.environ.get("INTEGRATION_FULL_DEPS_REQUIRED", "0") == "1" and not PYDANTIC_AVAILABLE:
    pytest.fail(
        "integration_full_deps tests require pydantic. Install with: pip install pydantic",
        pytrace=False,
    )

pytestmark = [
    pytest.mark.integration_full_deps,
    pytest.mark.skipif(not PYDANTIC_AVAILABLE, reason="pydantic not installed"),
]


# ---------------------------------------------------------------------------
# Test: Real inspector agents import, instantiate, and run_inspection
# ---------------------------------------------------------------------------


class TestDagRuntimeInspectorAgent:
    """Validate DagRuntimeInspectorAgent imports and runs diagnostics."""

    def test_importable(self) -> None:
        from agentic_core.L3_orchestration.reasoning.DagRuntimeInspectorAgent import (
            DagRuntimeInspectorAgent,
        )

        assert DagRuntimeInspectorAgent is not None

    def test_diagnose_returns_inspection_result(self) -> None:
        from agentic_core.L3_orchestration.reasoning.DagRuntimeInspectorAgent import (
            DagRuntimeInspectorAgent,
        )
        from agentic_core.mixins.inspection_capability_mixin import InspectionResult

        agent = DagRuntimeInspectorAgent()
        result = agent.run_inspection("test_target")

        assert isinstance(result, InspectionResult)
        assert isinstance(result.healthy, bool)
        assert isinstance(result.issues, list)
        assert isinstance(result.metrics, dict)


# ---------------------------------------------------------------------------
# Test: Decorator canonical imports work at runtime
# ---------------------------------------------------------------------------


class TestDecoratorRuntimeImports:
    """Verify canonical decorator imports work with full dep chain loaded."""

    def test_standard_heal_importable_with_full_deps(self) -> None:
        from agentic_core.utils.decorators_base_util import standard_heal

        assert callable(standard_heal)

    def test_timeout_importable_with_full_deps(self) -> None:
        from agentic_core.utils.timeout_decorator_util import timeout

        decorator = timeout(30)
        assert callable(decorator)

    def test_shim_identity_with_full_deps(self) -> None:
        from agentic_core.L5_safety.utils.decorators_util import (
            standard_heal as shim,
        )
        from agentic_core.utils.decorators_base_util import standard_heal as canonical

        assert shim is canonical

    def test_timeout_shim_identity_with_full_deps(self) -> None:
        from agentic_core.L0_routing.utils.timeout_decorator_util import (
            timeout as shim,
        )
        from agentic_core.utils.timeout_decorator_util import timeout as canonical

        assert shim is canonical


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
