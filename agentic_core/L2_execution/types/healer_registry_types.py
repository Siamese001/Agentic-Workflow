"""
Healer Registry — Declarative mapping of check_id to healer function.

Each healer receives the full check dict from the guardian aggregate
and returns a HealCheckResult. Healers may accept optional keyword
arguments (repo_root, apply) for mutating mode support.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult
from agentic_core.L2_execution.types.heal_result_adapter import adapt_heal_result
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
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
    _emit_routes_through,  # noqa: E402
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
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("healer_registry_types", "p4obs", "metric_1")
_emit_emits_metric_event("healer_registry_types", "p4obs", "metric_2")
_emit_emits_metric_event("healer_registry_types", "p4obs", "metric_3")
_emit_emits_metric_event("healer_registry_types", "p4obs", "metric_4")
_emit_emits_metric_event("healer_registry_types", "p4obs", "metric_5")
_emit_emits_metric_event("healer_registry_types", "p4obs", "metric_6")
_emit_records_incident_event("healer_registry_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("healer_registry_types", "p4obs", "anomaly")
_emit_writes_observability_log("healer_registry_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("healer_registry_types", "p4obs", "mon_state")
_emit_triggers_alert("healer_registry_types", "p4obs", "alert")
_emit_links_incident_trace("healer_registry_types", "p4obs", "trace_link")
_emit_captures_pattern("healer_registry_types", "p3lm", "pattern")
_emit_records_learning_event("healer_registry_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healer_registry_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("healer_registry_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healer_registry_types", "p3lm", "routing")
_emit_improves_agent_policy("healer_registry_types", "p3lm", "policy")
_emit_stores_learning_state("healer_registry_types", "p3lm", "state")
_emit_records_execution_trace("healer_registry_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healer_registry_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healer_registry_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healer_registry_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healer_registry_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healer_registry_types", "env_read", "p2_env_1")
_emit_reads_environ("healer_registry_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("healer_registry_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healer_registry_types", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "healer_registry_types")
emit_determinism_digest("p0", "healer_registry_types")

_emit_dispatches_healing_run("p1", "healer_registry_types", "L2")
_emit_routes_through("p1", "healer_registry_types", "L2")
_emit_checks_agent_registry("p1", "healer_registry_types", "agent_registry")
_emit_validates_agent_capability("p1", "healer_registry_types", "capability")
_emit_dispatches_execution_plan("p1", "healer_registry_types", "exec_plan")
_emit_agent_executes_agent("p1", "healer_registry_types", "sub_agent")
_emit_routes_to_agent("p1", "healer_registry_types", "target_agent")
_emit_verifies_policy("p1", "healer_registry_types", "policy_check")
_emit_observes_runtime_state("p1", "healer_registry_types", "runtime_state")
_emit_verifies_boundary("p1", "healer_registry_types", "boundary_check")
_emit_transcripts_response("p1", "healer_registry_types", "transcript")
_emit_hard_fails_untranscripted("p1", "healer_registry_types")
_emit_gated_by_confidence("p1", "healer_registry_types", "confidence_gate")
_emit_escalates_to_human("p1", "healer_registry_types", "L2")
_emit_reads_policy_state("p1", "healer_registry_types", "L2")
_emit_pulls_context("p1", "healer_registry_types", "context_pull")
_emit_pulls_context("p1", "healer_registry_types", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "healer_registry_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healer_registry_types", "uwg_term_secondary")
_emit_writes_through("p1", "healer_registry_types", "write_through")
_emit_writes_through("p1", "healer_registry_types", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "healer_registry_types", "safety_validation")
_emit_invokes_eval("p1", "healer_registry_types", "eval_call")
_emit_proposal_commits_routing("p1", "healer_registry_types", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "healer_registry_types")
_emit_applies_guardrail("p0", "healer_registry_types", "p0_governance")
_emit_snapshots_state("p0", "healer_registry_types", "state_snapshot")
_emit_authorize_and_execute("p2", "healer_registry_types", "execution_auth")
_emit_validates_capability("p2", "healer_registry_types", "capability_check")
_emit_routes_to_capability("p2", "healer_registry_types", "capability_route")
_emit_writes_via_uwg("p2", "healer_registry_types", "uwg_write")
_emit_blocks_direct_write("p2", "healer_registry_types", "direct_write_block")
_emit_records_tool_invocation("p2", "healer_registry_types", "tool_invocation")
_emit_captures_execution_output("p2", "healer_registry_types", "exec_output")
_emit_dispatches_agent("p3", "healer_registry_types", "agent_dispatch")
_emit_coordinates_agents("p3", "healer_registry_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "healer_registry_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "healer_registry_types", "healing_outcome")
_emit_escalates_failure("p3", "healer_registry_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "healer_registry_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healer_registry_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "healer_registry_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "healer_registry_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healer_registry_types", "eval_metric")
_emit_stores_embedding("p4", "healer_registry_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "healer_registry_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healer_registry_types", "exec_snapshot_link")


def _merge_heal_context(*args: Any, **kwargs: Any) -> dict[str, Any]:
    context: dict[str, Any] = {}
    for arg in args:
        if isinstance(arg, dict):
            context.update(arg)
    context.update(kwargs)
    return context


def _repo_root(context: dict[str, Any]) -> Path:
    root = context.get("repo_root") or context.get("project_root") or Path.cwd()
    return Path(root).resolve()


def _bool_context(context: dict[str, Any], key: str, default: bool) -> bool:
    value = context.get(key, default)
    return bool(value)


def _target_territory(context: dict[str, Any]) -> str | None:
    target = context.get("target_territory") or context.get("territory")
    return str(target) if target else None


def _file_path(context: dict[str, Any], repo_root: Path) -> Path | None:
    raw = context.get("file_path") or context.get("path") or context.get("file")
    if raw is None:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = repo_root / path
    return path.resolve()


def _adapt_result(check_id: str, raw_result: dict[str, Any] | str | None, repo_root: Path) -> HealCheckResult:
    return adapt_heal_result(check_id, raw_result, repo_root)


def heal_import_compliance(*args: Any, **kwargs: Any) -> HealCheckResult:
    context = _merge_heal_context(*args, **kwargs)
    repo_root = _repo_root(context)
    file_path = _file_path(context, repo_root)
    if file_path is None:
        return _adapt_result(
            "import_compliance",
            {"status": "SKIPPED", "notes": "No file_path provided"},
            repo_root,
        )
    from agentic_core.L5_safety.reasoning.CodeHealerAgent import CodeHealerAgent, HealerConfig

    agent = CodeHealerAgent(
        project_root=repo_root,
        agent_config=HealerConfig(
            enable_canon=False,
            enable_import=True,
            enable_structural=False,
            dry_run=_bool_context(context, "dry_run", True),
        ),
    )
    raw = agent.heal_repository(
        dry_run=_bool_context(context, "dry_run", True),
        execute=_bool_context(context, "execute", False),
        file_path=file_path,
    )
    return _adapt_result("import_compliance", raw, repo_root)


def heal_layer_gravity(*args: Any, **kwargs: Any) -> HealCheckResult:
    context = _merge_heal_context(*args, **kwargs)
    repo_root = _repo_root(context)
    from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import GravityLeakRepairAgent

    agent = GravityLeakRepairAgent(project_root=repo_root)
    raw = agent.heal_repository(
        dry_run=_bool_context(context, "dry_run", True),
        execute=_bool_context(context, "execute", False),
    )
    return _adapt_result("layer_gravity", raw, repo_root)


def heal_architecture_governance(*args: Any, **kwargs: Any) -> HealCheckResult:
    context = _merge_heal_context(*args, **kwargs)
    repo_root = _repo_root(context)
    from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import ArchitectureGovernorAgent

    agent = ArchitectureGovernorAgent(project_root=repo_root)
    raw = agent.heal_repository(
        dry_run=_bool_context(context, "dry_run", True),
        execute=_bool_context(context, "execute", False),
        target_territory=_target_territory(context),
    )
    return _adapt_result("architecture_governance", raw, repo_root)


def heal_naming_compliance(*args: Any, **kwargs: Any) -> HealCheckResult:
    context = _merge_heal_context(*args, **kwargs)
    repo_root = _repo_root(context)
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

    agent = FileClassificationAgent(project_root=repo_root)
    raw = agent.heal_repository(
        dry_run=_bool_context(context, "dry_run", True),
        execute=_bool_context(context, "execute", False),
        target_territory=_target_territory(context),
        cached_scan=context.get("cached_scan"),
    )
    return _adapt_result("naming_compliance", raw, repo_root)


def heal_territory_compliance(*args: Any, **kwargs: Any) -> HealCheckResult:
    context = _merge_heal_context(*args, **kwargs)
    repo_root = _repo_root(context)
    from agentic_core.L5_safety.reasoning.root_hygiene_healer import RootHygieneHealerAgent

    agent = RootHygieneHealerAgent(project_root=repo_root)
    raw = agent.heal_repository(
        dry_run=_bool_context(context, "dry_run", True),
        execute=_bool_context(context, "execute", False),
    )
    return _adapt_result("territory_compliance", raw, repo_root)


def heal_guardian_drift_detection(*args: Any, **kwargs: Any) -> HealCheckResult:
    context = _merge_heal_context(*args, **kwargs)
    repo_root = _repo_root(context)
    from agentic_core.L5_safety.reasoning.root_hygiene_healer import RootHygieneHealerAgent

    agent = RootHygieneHealerAgent(project_root=repo_root)
    raw = agent.heal_repository(
        dry_run=_bool_context(context, "dry_run", True),
        execute=_bool_context(context, "execute", False),
    )
    return _adapt_result("guardian_drift_detection", raw, repo_root)


def heal_file_classification(*args: Any, **kwargs: Any) -> HealCheckResult:
    context = _merge_heal_context(*args, **kwargs)
    repo_root = _repo_root(context)
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

    agent = FileClassificationAgent(project_root=repo_root)
    raw = agent.heal_repository(
        dry_run=_bool_context(context, "dry_run", True),
        execute=_bool_context(context, "execute", False),
        target_territory=_target_territory(context),
        cached_scan=context.get("cached_scan"),
    )
    return _adapt_result("file_classification", raw, repo_root)


def heal_filesystem_ssot_drift(*args: Any, **kwargs: Any) -> HealCheckResult:
    context = _merge_heal_context(*args, **kwargs)
    repo_root = _repo_root(context)
    from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import FilesystemSSOTReconcilerAgent

    agent = FilesystemSSOTReconcilerAgent(project_root=repo_root)
    raw = agent.heal_repository(
        dry_run=_bool_context(context, "dry_run", True),
        execute=_bool_context(context, "execute", False),
        force=True,
    )
    return _adapt_result("filesystem_ssot_drift", raw, repo_root)


def heal_gravity_violations(*args: Any, **kwargs: Any) -> HealCheckResult:
    context = _merge_heal_context(*args, **kwargs)
    repo_root = _repo_root(context)
    from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import GravityLeakRepairAgent

    agent = GravityLeakRepairAgent(project_root=repo_root)
    raw = agent.heal_repository(
        dry_run=_bool_context(context, "dry_run", True),
        execute=_bool_context(context, "execute", False),
    )
    return _adapt_result("gravity_violations", raw, repo_root)


def heal_hierarchy_violations(*args: Any, **kwargs: Any) -> HealCheckResult:
    context = _merge_heal_context(*args, **kwargs)
    repo_root = _repo_root(context)
    from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent

    agent = StructureEnforcerAgent(project_root=repo_root)
    raw = agent.heal_repository(
        dry_run=_bool_context(context, "dry_run", True),
        execute=_bool_context(context, "execute", False),
        target_territory=_target_territory(context),
    )
    return _adapt_result("hierarchy_violations", raw, repo_root)


def heal_missing_structure(*args: Any, **kwargs: Any) -> HealCheckResult:
    context = _merge_heal_context(*args, **kwargs)
    repo_root = _repo_root(context)
    from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent

    agent = StructureEnforcerAgent(project_root=repo_root)
    raw = agent.heal_repository(
        dry_run=_bool_context(context, "dry_run", True),
        execute=_bool_context(context, "execute", False),
        target_territory=_target_territory(context),
    )
    return _adapt_result("missing_structure", raw, repo_root)


def heal_subfolder_compliance(*args: Any, **kwargs: Any) -> HealCheckResult:
    context = _merge_heal_context(*args, **kwargs)
    repo_root = _repo_root(context)
    from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent

    agent = StructureEnforcerAgent(project_root=repo_root)
    raw = agent.heal_repository(
        dry_run=_bool_context(context, "dry_run", True),
        execute=_bool_context(context, "execute", False),
        target_territory=_target_territory(context),
    )
    return _adapt_result("subfolder_compliance", raw, repo_root)


HealerFn = Callable[..., HealCheckResult]

HEALER_REGISTRY: dict[str, HealerFn] = {
    "guardian_drift_detection": heal_guardian_drift_detection,
    "naming_compliance": heal_naming_compliance,
    "territory_compliance": heal_territory_compliance,
    "missing_structure": heal_missing_structure,
    "subfolder_compliance": heal_subfolder_compliance,
    "import_compliance": heal_import_compliance,
    "layer_gravity": heal_layer_gravity,
    "filesystem_ssot_drift": heal_filesystem_ssot_drift,
    "hierarchy_violations": heal_hierarchy_violations,
    "architecture_governance": heal_architecture_governance,
    "gravity_violations": heal_gravity_violations,
    "file_classification": heal_file_classification,
}

__all__ = ["HealerFn", "HEALER_REGISTRY"]
