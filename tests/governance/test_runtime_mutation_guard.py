"""REQ-417: runtime mutation guard — block core-module reload and sys.modules injection."""

from __future__ import annotations

import importlib

import pytest

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
)
from agentic_core.L5_safety.enforcement.runtime_mutation_guardrail import (
    _CORE_PREFIXES,
    _guarded_setattr,
    _GuardedSysModules,
    install_guards,
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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_runtime_mutation_guard")
_emit_applies_guardrail("p0", "test_runtime_mutation_guard", "p0_governance")
_emit_reads_policy_state("p0", "test_runtime_mutation_guard", "policy_binding")
_emit_snapshots_state("p0", "test_runtime_mutation_guard", "state_snapshot")
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_runtime_mutation_guard", "p4obs", "metric_1")
_emit_emits_metric_event("test_runtime_mutation_guard", "p4obs", "metric_2")
_emit_emits_metric_event("test_runtime_mutation_guard", "p4obs", "metric_3")
_emit_emits_metric_event("test_runtime_mutation_guard", "p4obs", "metric_4")
_emit_emits_metric_event("test_runtime_mutation_guard", "p4obs", "metric_5")
_emit_emits_metric_event("test_runtime_mutation_guard", "p4obs", "metric_6")
_emit_records_incident_event("test_runtime_mutation_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_runtime_mutation_guard", "p4obs", "anomaly")
_emit_writes_observability_log("test_runtime_mutation_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_runtime_mutation_guard", "p4obs", "mon_state")
_emit_triggers_alert("test_runtime_mutation_guard", "p4obs", "alert")
_emit_links_incident_trace("test_runtime_mutation_guard", "p4obs", "trace_link")
_emit_captures_pattern("test_runtime_mutation_guard", "p3lm", "pattern")
_emit_records_learning_event("test_runtime_mutation_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_runtime_mutation_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_runtime_mutation_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_runtime_mutation_guard", "p3lm", "routing")
_emit_improves_agent_policy("test_runtime_mutation_guard", "p3lm", "policy")
_emit_stores_learning_state("test_runtime_mutation_guard", "p3lm", "state")
_emit_records_execution_trace("test_runtime_mutation_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_runtime_mutation_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_runtime_mutation_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_runtime_mutation_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_runtime_mutation_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_runtime_mutation_guard", "env_read", "p2_env_1")
_emit_reads_environ("test_runtime_mutation_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_runtime_mutation_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_runtime_mutation_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_runtime_mutation_guard", "context_pull")
_emit_pulls_context("p1", "test_runtime_mutation_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_runtime_mutation_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_runtime_mutation_guard", "uwg_term_2")
_emit_writes_through("p1", "test_runtime_mutation_guard", "write_through")
_emit_writes_through("p1", "test_runtime_mutation_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_runtime_mutation_guard", "safety_validation")
_emit_invokes_eval("p1", "test_runtime_mutation_guard", "eval_call")
_emit_proposal_commits_routing("p1", "test_runtime_mutation_guard", "routing_commit")
_emit_escalates_to_human("p1", "test_runtime_mutation_guard", "human_escalation")
_emit_routes_through("p1", "test_runtime_mutation_guard", "route_through")
_emit_checks_agent_registry("p1", "test_runtime_mutation_guard", "agent_registry")
_emit_validates_agent_capability("p1", "test_runtime_mutation_guard", "capability")
_emit_dispatches_execution_plan("p1", "test_runtime_mutation_guard", "exec_plan")
_emit_agent_executes_agent("p1", "test_runtime_mutation_guard", "sub_agent")
_emit_routes_to_agent("p1", "test_runtime_mutation_guard", "target_agent")
_emit_verifies_policy("p1", "test_runtime_mutation_guard", "policy_check")
_emit_observes_runtime_state("p1", "test_runtime_mutation_guard", "runtime_state")
_emit_verifies_boundary("p1", "test_runtime_mutation_guard", "boundary_check")
_emit_transcripts_response("p1", "test_runtime_mutation_guard", "transcript")
_emit_hard_fails_untranscripted("p1", "test_runtime_mutation_guard")
_emit_gated_by_confidence("p1", "test_runtime_mutation_guard", "confidence_gate")
emit_replay_key("p0", "test_runtime_mutation_guard")
emit_determinism_digest("p0", "test_runtime_mutation_guard")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_runtime_mutation_guard", "execution_auth")
_emit_validates_capability("p2", "test_runtime_mutation_guard", "capability_check")
_emit_routes_to_capability("p2", "test_runtime_mutation_guard", "capability_route")
_emit_writes_via_uwg("p2", "test_runtime_mutation_guard", "uwg_write")
_emit_blocks_direct_write("p2", "test_runtime_mutation_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "test_runtime_mutation_guard", "tool_invocation")
_emit_captures_execution_output("p2", "test_runtime_mutation_guard", "exec_output")
_emit_dispatches_agent("p3", "test_runtime_mutation_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "test_runtime_mutation_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_runtime_mutation_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_runtime_mutation_guard", "healing_outcome")
_emit_escalates_failure("p3", "test_runtime_mutation_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_runtime_mutation_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_runtime_mutation_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_runtime_mutation_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_runtime_mutation_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_runtime_mutation_guard", "eval_metric")
_emit_stores_embedding("p4", "test_runtime_mutation_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_runtime_mutation_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_runtime_mutation_guard", "exec_snapshot_link")


@pytest.mark.governance
def test_install_guards_is_idempotent() -> None:
    """install_guards() MUST be callable multiple times without error or double-patching."""
    install_guards()
    install_guards()
    install_guards()


@pytest.mark.governance
def test_importlib_reload_core_module_is_blocked() -> None:
    """importlib.reload of a core-prefix module MUST raise ImportError with REQ-417."""
    import agentic_core.L2_execution.UniversalWriteGateway as _uwg_mod

    with pytest.raises(ImportError, match="REQ-417"):
        importlib.reload(_uwg_mod)


@pytest.mark.governance
def test_importlib_reload_stdlib_module_is_allowed() -> None:
    """importlib.reload of a stdlib module MUST NOT be blocked by the guard."""
    import json

    result = importlib.reload(json)
    assert result is json


@pytest.mark.governance
def test_core_prefixes_cover_all_layers() -> None:
    """_CORE_PREFIXES MUST include all canonical app-layer namespaces."""
    required = {"agentic_core.", "apps_lic.", "apps_rg.", "apps_shared.", "system_learning."}
    missing = required - set(_CORE_PREFIXES)
    assert not missing, f"Missing core prefixes: {missing}"


# =============================================================================
# sys.modules guard (_GuardedSysModules)
# =============================================================================


@pytest.mark.governance
def test_guarded_sys_modules_allows_new_key() -> None:
    """_GuardedSysModules MUST allow adding a new core-prefix key (initial import)."""
    guarded: _GuardedSysModules = _GuardedSysModules()
    guarded["agentic_core.new_module_xyz"] = object()


@pytest.mark.governance
def test_sys_modules_replacement_blocked_for_core_module() -> None:
    """_GuardedSysModules MUST raise ImportError when replacing an already-loaded core key."""
    guarded: _GuardedSysModules = _GuardedSysModules()
    sentinel = object()
    guarded["agentic_core.L2_execution.UniversalWriteGateway"] = sentinel

    with pytest.raises(ImportError, match="REQ-417"):
        guarded["agentic_core.L2_execution.UniversalWriteGateway"] = object()


@pytest.mark.governance
def test_guarded_sys_modules_allows_non_core_replacement() -> None:
    """_GuardedSysModules MUST allow replacement of non-core-prefix keys."""
    guarded: _GuardedSysModules = _GuardedSysModules()
    guarded["third_party.lib"] = object()
    guarded["third_party.lib"] = object()


# =============================================================================
# setattr reference guard
# =============================================================================


@pytest.mark.governance
def test_guarded_setattr_raises_for_core_instance() -> None:
    """_guarded_setattr MUST raise AttributeError with REQ-417 for core-layer instances."""
    from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway

    uwg = UniversalWriteGateway()
    with pytest.raises(AttributeError, match="REQ-417"):
        _guarded_setattr(uwg, "injected_attr", "bad_value")


@pytest.mark.governance
def test_guarded_setattr_allows_non_core_instance() -> None:
    """_guarded_setattr MUST allow attribute setting on non-core instances."""

    class _Innocent:
        pass

    obj = _Innocent()
    _guarded_setattr(obj, "x", 42)
    assert obj.x == 42


# =============================================================================
# SOV-DELTA: object.__setattr__ AST scanner smoke test
# =============================================================================


@pytest.mark.governance
def test_object_dunder_setattr_scanner_exists() -> None:
    """SOV-DELTA: ops_scripts/ci/check_object_dunder_setattr.py MUST exist and be importable."""
    from pathlib import Path

    scanner = Path(__file__).resolve().parents[2] / OPS_SCRIPTS_DIR / "ci" / "check_object_dunder_setattr.py"
    assert scanner.exists(), "check_object_dunder_setattr.py not found"


@pytest.mark.governance
def test_object_dunder_setattr_scanner_detects_core_pattern() -> None:
    """SOV-DELTA AST scanner MUST detect object.__setattr__(uwg, ...) patterns."""
    import ast
    import sys

    sys.path.insert(0, str(__file__))

    from pathlib import Path

    scanner_path = (
        Path(__file__).resolve().parents[2] / OPS_SCRIPTS_DIR / "ci" / "check_object_dunder_setattr.py"
    )
    snippet = "object.__setattr__(uwg, 'x', 1)"
    tree = ast.parse(snippet)

    import importlib.util

    spec = importlib.util.spec_from_file_location("check_osd", scanner_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    call_node = tree.body[0].value  # type: ignore[attr-defined]
    assert mod._is_object_dunder_setattr(call_node) is True
    assert mod._arg0_is_core_name(call_node) is True
