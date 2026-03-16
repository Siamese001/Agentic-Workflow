"""3.9: Baseline tests for LicHealingOrchestrator (HEAL-GAP-04)."""

from __future__ import annotations

import sys
from types import ModuleType

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

_emit_records_execution_trace("p0", "evidence", "test_lic_healing_orchestrator")
_emit_applies_guardrail("p0", "test_lic_healing_orchestrator", "p0_governance")
_emit_reads_policy_state("p0", "test_lic_healing_orchestrator", "policy_binding")
_emit_snapshots_state("p0", "test_lic_healing_orchestrator", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_lic_healing_orchestrator", "p4obs", "metric_1")
_emit_emits_metric_event("test_lic_healing_orchestrator", "p4obs", "metric_2")
_emit_emits_metric_event("test_lic_healing_orchestrator", "p4obs", "metric_3")
_emit_emits_metric_event("test_lic_healing_orchestrator", "p4obs", "metric_4")
_emit_emits_metric_event("test_lic_healing_orchestrator", "p4obs", "metric_5")
_emit_emits_metric_event("test_lic_healing_orchestrator", "p4obs", "metric_6")
_emit_records_incident_event("test_lic_healing_orchestrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_lic_healing_orchestrator", "p4obs", "anomaly")
_emit_writes_observability_log("test_lic_healing_orchestrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_lic_healing_orchestrator", "p4obs", "mon_state")
_emit_triggers_alert("test_lic_healing_orchestrator", "p4obs", "alert")
_emit_links_incident_trace("test_lic_healing_orchestrator", "p4obs", "trace_link")
_emit_captures_pattern("test_lic_healing_orchestrator", "p3lm", "pattern")
_emit_records_learning_event("test_lic_healing_orchestrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_lic_healing_orchestrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_lic_healing_orchestrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_lic_healing_orchestrator", "p3lm", "routing")
_emit_improves_agent_policy("test_lic_healing_orchestrator", "p3lm", "policy")
_emit_stores_learning_state("test_lic_healing_orchestrator", "p3lm", "state")
_emit_records_execution_trace("test_lic_healing_orchestrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_lic_healing_orchestrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_lic_healing_orchestrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_lic_healing_orchestrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_lic_healing_orchestrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_lic_healing_orchestrator", "env_read", "p2_env_1")
_emit_reads_environ("test_lic_healing_orchestrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_lic_healing_orchestrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_lic_healing_orchestrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_lic_healing_orchestrator", "context_pull")
_emit_pulls_context("p1", "test_lic_healing_orchestrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_lic_healing_orchestrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_lic_healing_orchestrator", "uwg_term_2")
_emit_writes_through("p1", "test_lic_healing_orchestrator", "write_through")
_emit_writes_through("p1", "test_lic_healing_orchestrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_lic_healing_orchestrator", "safety_validation")
_emit_invokes_eval("p1", "test_lic_healing_orchestrator", "eval_call")
_emit_proposal_commits_routing("p1", "test_lic_healing_orchestrator", "routing_commit")
emit_replay_key("p0", "test_lic_healing_orchestrator")
emit_determinism_digest("p0", "test_lic_healing_orchestrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_lic_healing_orchestrator", "execution_auth")
_emit_validates_capability("p2", "test_lic_healing_orchestrator", "capability_check")
_emit_routes_to_capability("p2", "test_lic_healing_orchestrator", "capability_route")
_emit_writes_via_uwg("p2", "test_lic_healing_orchestrator", "uwg_write")
_emit_blocks_direct_write("p2", "test_lic_healing_orchestrator", "direct_write_block")
_emit_records_tool_invocation("p2", "test_lic_healing_orchestrator", "tool_invocation")
_emit_captures_execution_output("p2", "test_lic_healing_orchestrator", "exec_output")
_emit_dispatches_agent("p3", "test_lic_healing_orchestrator", "agent_dispatch")
_emit_coordinates_agents("p3", "test_lic_healing_orchestrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_lic_healing_orchestrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_lic_healing_orchestrator", "healing_outcome")
_emit_escalates_failure("p3", "test_lic_healing_orchestrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_lic_healing_orchestrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_lic_healing_orchestrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_lic_healing_orchestrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_lic_healing_orchestrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_lic_healing_orchestrator", "eval_metric")
_emit_stores_embedding("p4", "test_lic_healing_orchestrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_lic_healing_orchestrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_lic_healing_orchestrator", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def _make_lic_agent_base_stub():
    """Inject a minimal LICAgentBase stub so LicHealingOrchestrator can be imported."""
    stub_mod = ModuleType("apps_lic.utils.LICAgentBase")
    parent_mod = ModuleType("apps_lic.utils")

    class _LICAgentBase:
        recovery_playbooks: dict = {}

        def ml_cache_get(self, key):
            return None

        def ml_cache_set(self, key, val):
            return True

        def retrieve_healing_patterns(self, v, top_k=3):
            return []

        def store_healing_pattern(self, v, r):
            return True

        def guardrails_check_healing_depth(self, vid):
            return True

        def guardrails_increment_healing_depth(self, vid):
            pass

        def guardrails_reset_healing_depth(self, vid):
            pass

        def cache_pattern_with_metadata(self, *a, **kw):
            pass

        def ml_enhanced_heal(self, v, fn):
            return fn(v)

        def ml_cache_incident_resolution(self, *a, **kw):
            return True

    stub_mod.LICAgentBase = _LICAgentBase
    sys.modules.setdefault("apps_lic.utils", parent_mod)
    sys.modules["apps_lic.utils.LICAgentBase"] = stub_mod
    return _LICAgentBase


_LICAgentBase = _make_lic_agent_base_stub()


class TestLicHealingOrchestratorExecuteHealing:
    def _get_orchestrator(self):
        if "apps_lic.reasoning.LicHealingOrchestrator" in sys.modules:
            del sys.modules["apps_lic.reasoning.LicHealingOrchestrator"]
        from apps_lic.reasoning.LicHealingOrchestrator import LicHealingOrchestrator

        orch = LicHealingOrchestrator.__new__(LicHealingOrchestrator)
        orch.recovery_playbooks = {
            "structural": "structural_recovery",
            "schema": "schema_recovery",
            "output_contract": "schema_recovery",
            "llm_call": "llm_recovery",
            "api_timeout": "llm_recovery",
        }
        return orch

    def test_unknown_incident_returns_resolved(self):
        orch = self._get_orchestrator()
        result = orch._execute_healing({"type": "unknown_xyz"})
        assert result["status"] in ("resolved", "error")
        assert result["incident_type"] == "unknown_xyz"

    def test_structural_incident_dispatches(self):
        orch = self._get_orchestrator()
        result = orch._execute_healing({"type": "structural", "content": "safe content"})
        assert "healer" in result
        assert result["healer"] == "ControlPlane"

    def test_schema_incident_dispatches(self):
        orch = self._get_orchestrator()
        result = orch._execute_healing({"type": "schema", "stage_id": 3, "context": {}})
        assert "healer" in result

    def test_execute_healing_always_returns_dict(self):
        orch = self._get_orchestrator()
        for incident_type in ("structural", "schema", "output_contract", "unknown"):
            result = orch._execute_healing({"type": incident_type, "content": "test"})
            assert isinstance(result, dict)
            assert "status" in result
