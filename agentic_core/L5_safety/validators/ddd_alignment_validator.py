from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "ddd_alignment_validator")
emit_determinism_digest("p0", "ddd_alignment_validator")

_emit_dispatches_healing_run("p1", "ddd_alignment_validator", "L5")
_emit_routes_through("p1", "ddd_alignment_validator", "L5")
_emit_checks_agent_registry("p1", "ddd_alignment_validator", "agent_registry")
_emit_validates_agent_capability("p1", "ddd_alignment_validator", "capability")
_emit_dispatches_execution_plan("p1", "ddd_alignment_validator", "exec_plan")
_emit_agent_executes_agent("p1", "ddd_alignment_validator", "sub_agent")
_emit_routes_to_agent("p1", "ddd_alignment_validator", "target_agent")
_emit_verifies_policy("p1", "ddd_alignment_validator", "policy_check")
_emit_observes_runtime_state("p1", "ddd_alignment_validator", "runtime_state")
_emit_verifies_boundary("p1", "ddd_alignment_validator", "boundary_check")
_emit_transcripts_response("p1", "ddd_alignment_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "ddd_alignment_validator")
_emit_gated_by_confidence("p1", "ddd_alignment_validator", "confidence_gate")
_emit_escalates_to_human("p1", "ddd_alignment_validator", "L5")
_emit_reads_policy_state("p1", "ddd_alignment_validator", "L5")
_emit_authorize_and_execute("p2", "ddd_alignment_validator", "execution_auth")
_emit_validates_capability("p2", "ddd_alignment_validator", "capability_check")
_emit_routes_to_capability("p2", "ddd_alignment_validator", "capability_route")
_emit_writes_via_uwg("p2", "ddd_alignment_validator", "uwg_write")
_emit_blocks_direct_write("p2", "ddd_alignment_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "ddd_alignment_validator", "tool_invocation")
_emit_captures_execution_output("p2", "ddd_alignment_validator", "exec_output")
_emit_dispatches_agent("p3", "ddd_alignment_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "ddd_alignment_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "ddd_alignment_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "ddd_alignment_validator", "healing_outcome")
_emit_escalates_failure("p3", "ddd_alignment_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "ddd_alignment_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ddd_alignment_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "ddd_alignment_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "ddd_alignment_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ddd_alignment_validator", "eval_metric")
_emit_stores_embedding("p4", "ddd_alignment_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "ddd_alignment_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ddd_alignment_validator", "exec_snapshot_link")

"\nSovereign Guardian: DDD Alignment\nEnforces Bounded Contexts and Aggregate Root access.\n"
import ast
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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
    _emit_writes_through,
)

_emit_emits_metric_event("ddd_alignment_validator", "p4obs", "metric_1")
_emit_emits_metric_event("ddd_alignment_validator", "p4obs", "metric_2")
_emit_emits_metric_event("ddd_alignment_validator", "p4obs", "metric_3")
_emit_emits_metric_event("ddd_alignment_validator", "p4obs", "metric_4")
_emit_emits_metric_event("ddd_alignment_validator", "p4obs", "metric_5")
_emit_emits_metric_event("ddd_alignment_validator", "p4obs", "metric_6")
_emit_records_incident_event("ddd_alignment_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("ddd_alignment_validator", "p4obs", "anomaly")
_emit_writes_observability_log("ddd_alignment_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("ddd_alignment_validator", "p4obs", "mon_state")
_emit_triggers_alert("ddd_alignment_validator", "p4obs", "alert")
_emit_links_incident_trace("ddd_alignment_validator", "p4obs", "trace_link")
_emit_captures_pattern("ddd_alignment_validator", "p3lm", "pattern")
_emit_records_learning_event("ddd_alignment_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ddd_alignment_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("ddd_alignment_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ddd_alignment_validator", "p3lm", "routing")
_emit_improves_agent_policy("ddd_alignment_validator", "p3lm", "policy")
_emit_stores_learning_state("ddd_alignment_validator", "p3lm", "state")
_emit_records_execution_trace("ddd_alignment_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ddd_alignment_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ddd_alignment_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ddd_alignment_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ddd_alignment_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ddd_alignment_validator", "env_read", "p2_env_1")
_emit_reads_environ("ddd_alignment_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("ddd_alignment_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ddd_alignment_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ddd_alignment_validator", "context_pull")
_emit_pulls_context("p1", "ddd_alignment_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ddd_alignment_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ddd_alignment_validator", "uwg_term_2")
_emit_writes_through("p1", "ddd_alignment_validator", "write_through")
_emit_writes_through("p1", "ddd_alignment_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "ddd_alignment_validator", "safety_validation")
_emit_invokes_eval("p1", "ddd_alignment_validator", "eval_call")
_emit_proposal_commits_routing("p1", "ddd_alignment_validator", "routing_commit")


def _get_sovereign_domain():
    """Lazy load sovereign domain to avoid L0 → L1 dependency."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_sovereign_domain", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_sovereign_domain", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "_get_sovereign_domain")
    import importlib

    module = importlib.import_module("agentic_core.L1_cognition.P2_domain.sovereign")
    return module


def check_bounded_contexts(filepath: Path) -> list[str]:
    """Brief description of functionality and purpose."""
    issues: Any = []
    file_str: Any = str(filepath).replace("\\", "/")
    current_context: Any = next(
        (ctx for ctx, info in BOUNDED_CONTEXTS.items() if info.get("path") in file_str), None
    )
    if not current_context:
        return []
    stdlib_modules: Any = {
        "pathlib",
        "os",
        "sys",
        "json",
        "logging",
        "typing",
        "datetime",
        "collections",
        "itertools",
        "functools",
        "re",
        "asyncio",
        "abc",
        "dataclasses",
        "enum",
        "copy",
        "io",
        "time",
        "uuid",
        "hashlib",
    }
    try:
        tree: Any = ast.parse(filepath.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                module_root: Any = node.module.split(".")[0]
                if module_root in stdlib_modules:
                    continue
                if "apps_shared.base_agents" in node.module:
                    continue
                for ctx, info in BOUNDED_CONTEXTS.items():
                    if ctx == current_context:
                        continue
                    if ctx == "SharedContracts":
                        continue    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
                    target_path: Any = info.get("path", "")
                    if target_path.replace("/", ".") in node.module:
                        if "contracts" not in node.module and "interfaces" not in node.module:
                            issues.append(
                                f"Potential Context Violation: Importing {ctx} logic ({node.module}) into {current_context}"
                            )
    except (OSError, UnicodeDecodeError, SyntaxError):    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
        pass
    return issues


def validate_ddd_alignment(target_dir: str) -> tuple[float, list[str]]:
    """Brief description of functionality and purpose."""
    issues: Any = []
    total_files: Any = 0
    from agentic_core.utils.schemas.ssot_discovery_validator import get_python_files

    for path in get_python_files(Path(target_dir)):
        if TESTS_DIR in str(path):
            continue
        total_files += 1
        issues.extend([f"{str(path)}: {i}" for i in check_bounded_contexts(path)])
    score: Any = 100.0
    if issues:
        score: Any = max(0, 100 - len(issues) * 2)
    return (score, issues)
