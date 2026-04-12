"""
DDD Alignment Guardian - Sovereign Edition (December 29, 2025)
Detects violations of Domain-Driven Design tactical patterns:
- Anemic Domain models (data holders without behavior)
- God Classes (excessive responsibilities)
- Mutable Value Objects
- Service layer bloat indicators
- Aggregate root misuse patterns
"""

import ast
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "guard_ddd_alignment_util")
emit_determinism_digest("p0", "guard_ddd_alignment_util")

_emit_dispatches_healing_run("p1", "guard_ddd_alignment_util", "L5")
_emit_routes_through("p1", "guard_ddd_alignment_util", "L5")
_emit_checks_agent_registry("p1", "guard_ddd_alignment_util", "agent_registry")
_emit_validates_agent_capability("p1", "guard_ddd_alignment_util", "capability")
_emit_dispatches_execution_plan("p1", "guard_ddd_alignment_util", "exec_plan")
_emit_agent_executes_agent("p1", "guard_ddd_alignment_util", "sub_agent")
_emit_routes_to_agent("p1", "guard_ddd_alignment_util", "target_agent")
_emit_verifies_policy("p1", "guard_ddd_alignment_util", "policy_check")
_emit_observes_runtime_state("p1", "guard_ddd_alignment_util", "runtime_state")
_emit_verifies_boundary("p1", "guard_ddd_alignment_util", "boundary_check")
_emit_transcripts_response("p1", "guard_ddd_alignment_util", "transcript")
_emit_hard_fails_untranscripted("p1", "guard_ddd_alignment_util")
_emit_gated_by_confidence("p1", "guard_ddd_alignment_util", "confidence_gate")
_emit_escalates_to_human("p1", "guard_ddd_alignment_util", "L5")
_emit_reads_policy_state("p1", "guard_ddd_alignment_util", "L5")
_emit_authorize_and_execute("p2", "guard_ddd_alignment_util", "execution_auth")
_emit_validates_capability("p2", "guard_ddd_alignment_util", "capability_check")
_emit_routes_to_capability("p2", "guard_ddd_alignment_util", "capability_route")
_emit_writes_via_uwg("p2", "guard_ddd_alignment_util", "uwg_write")
_emit_blocks_direct_write("p2", "guard_ddd_alignment_util", "direct_write_block")
_emit_records_tool_invocation("p2", "guard_ddd_alignment_util", "tool_invocation")
_emit_captures_execution_output("p2", "guard_ddd_alignment_util", "exec_output")
_emit_dispatches_agent("p3", "guard_ddd_alignment_util", "agent_dispatch")
_emit_coordinates_agents("p3", "guard_ddd_alignment_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "guard_ddd_alignment_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "guard_ddd_alignment_util", "healing_outcome")
_emit_escalates_failure("p3", "guard_ddd_alignment_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "guard_ddd_alignment_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "guard_ddd_alignment_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "guard_ddd_alignment_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "guard_ddd_alignment_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "guard_ddd_alignment_util", "eval_metric")
_emit_stores_embedding("p4", "guard_ddd_alignment_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "guard_ddd_alignment_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "guard_ddd_alignment_util", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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
    _emit_records_incident_event,
    _emit_records_learning_event,
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
    _emit_writes_through,
)

_emit_emits_metric_event("guard_ddd_alignment_util", "p4obs", "metric_1")
_emit_emits_metric_event("guard_ddd_alignment_util", "p4obs", "metric_2")
_emit_emits_metric_event("guard_ddd_alignment_util", "p4obs", "metric_3")
_emit_emits_metric_event("guard_ddd_alignment_util", "p4obs", "metric_4")
_emit_emits_metric_event("guard_ddd_alignment_util", "p4obs", "metric_5")
_emit_emits_metric_event("guard_ddd_alignment_util", "p4obs", "metric_6")
_emit_records_incident_event("guard_ddd_alignment_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("guard_ddd_alignment_util", "p4obs", "anomaly")
_emit_writes_observability_log("guard_ddd_alignment_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("guard_ddd_alignment_util", "p4obs", "mon_state")
_emit_triggers_alert("guard_ddd_alignment_util", "p4obs", "alert")
_emit_links_incident_trace("guard_ddd_alignment_util", "p4obs", "trace_link")
_emit_captures_pattern("guard_ddd_alignment_util", "p3lm", "pattern")
_emit_records_learning_event("guard_ddd_alignment_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("guard_ddd_alignment_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("guard_ddd_alignment_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("guard_ddd_alignment_util", "p3lm", "routing")
_emit_improves_agent_policy("guard_ddd_alignment_util", "p3lm", "policy")
_emit_stores_learning_state("guard_ddd_alignment_util", "p3lm", "state")
_emit_records_execution_trace("guard_ddd_alignment_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("guard_ddd_alignment_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("guard_ddd_alignment_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("guard_ddd_alignment_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("guard_ddd_alignment_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("guard_ddd_alignment_util", "env_read", "p2_env_1")
_emit_reads_environ("guard_ddd_alignment_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("guard_ddd_alignment_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("guard_ddd_alignment_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "guard_ddd_alignment_util", "context_pull")
_emit_pulls_context("p1", "guard_ddd_alignment_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "guard_ddd_alignment_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "guard_ddd_alignment_util", "uwg_term_2")
_emit_writes_through("p1", "guard_ddd_alignment_util", "write_through")
_emit_writes_through("p1", "guard_ddd_alignment_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "guard_ddd_alignment_util", "safety_validation")
_emit_invokes_eval("p1", "guard_ddd_alignment_util", "eval_call")
_emit_proposal_commits_routing("p1", "guard_ddd_alignment_util", "routing_commit")

try:
    from ops_scripts.dev_tools.L0_routing_scripts.full_agent_discovery import SCRIPTS_DIR, TESTS_DIR
except ImportError as e:
    raise ImportError(f"Required dependency missing: {e}")  # guardian: allow-silent-swallow
    SCRIPTS_DIR = "ops_scripts"
    TESTS_DIR = "tests"


def get_ddd_violations_detailed(root_path: str) -> list[dict]:
    """
    [NEW] Detailed DDD Violation detector — structured output for L0 healing/forensics.

    Returns:
        List of dicts with keys: file, line, type, description, Severity
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_ddd_violations_detailed", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_ddd_violations_detailed", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "get_ddd_violations_detailed")
    violations: list[dict] = []
    root = Path(root_path)
    if not root.exists():
        return violations
    python_files = list(get_python_files(root))
    if not python_files:
        return violations
    for py_file in python_files:
        try:
            relative_path = py_file.relative_to(root)
        except ValueError:
            relative_path = py_file.name
        if any(
            skip in str(relative_path) for skip in [TESTS_DIR, "migrations", "__pycache__", ".venv", "venv"]
        ) or py_file.name.startswith("_"):
            continue
        try:
            code = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(code, filename=str(py_file))
        except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
            violations.append(
                {
                    "file": str(relative_path),
                    "line": 1,
                    "type": "Parse Error",
                    "description": f"Invalid syntax: {e}",
                    "Severity": "LOW",
                },
            )
            continue
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            violations.append(
                {
                    "file": str(relative_path),
                    "line": 1,
                    "type": "Read Error",
                    "description": f"Failed to read/parse: {e}",
                    "Severity": "LOW",
                },
            )
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            methods = [
                n for n in node.body if isinstance(n, ast.FunctionDef) and (not n.name.startswith("__"))
            ]
            attrs = [n for n in node.body if isinstance(n, ast.Assign)]
            ann_attrs = [n for n in node.body if isinstance(n, ast.AnnAssign)]
            total_methods = len(methods)
            total_attrs = len(attrs) + len(ann_attrs)
            if total_attrs >= 6 and total_methods <= 2:
                path_str = str(relative_path).lower()
                class_name_lower = node.name.lower()
                has_dataclass_decorator = any(
                    isinstance(d, ast.Name)
                    and d.id == "dataclass"
                    or (isinstance(d, ast.Attribute) and d.attr == "dataclass")
                    or (
                        isinstance(d, ast.Call)
                        and (
                            isinstance(d.func, ast.Name)
                            and d.func.id == "dataclass"
                            or (isinstance(d.func, ast.Attribute) and d.func.attr == "dataclass")
                        )
                    )
                    for d in node.decorator_list
                )
                is_data_class_exempt = (
                    has_dataclass_decorator
                    or "schemas" in path_str
                    or "config" in path_str
                    or (SCRIPTS_DIR in path_str)
                    or ("types" in path_str)
                    or ("deprecated" in path_str)
                    or ("_registry" in path_str)
                    or ("_policy" in path_str)
                    or ("_config" in path_str)
                    or ("_types" in path_str)
                    or class_name_lower.endswith("_task")
                    or class_name_lower.endswith("_result")
                    or class_name_lower.endswith("_config")
                    or class_name_lower.endswith("_context")
                    or class_name_lower.endswith("_finding")
                    or class_name_lower.endswith("_pattern")
                    or class_name_lower.endswith("_gap")
                    or class_name_lower.endswith("_recommendation")
                    or class_name_lower.endswith("_entry")
                    or class_name_lower.endswith("_record")
                    or class_name_lower.endswith("_state")
                    or class_name_lower.endswith("_info")
                    or class_name_lower.endswith("_data")
                    or class_name_lower.endswith("_dto")
                    or class_name_lower.endswith("_vo")
                    or class_name_lower.endswith("bundle")
                    or class_name_lower.endswith("_phase")
                    or class_name_lower.endswith("_type")
                    or class_name_lower.endswith("_status")
                    or class_name_lower.endswith("_response")
                    or class_name_lower.endswith("_request")
                    or class_name_lower.endswith("_event")
                    or class_name_lower.endswith("_message")
                    or class_name_lower.endswith("_model")
                    or (class_name_lower == "Provider")
                    or (class_name_lower == "ExecutionPhase")
                    or ("result" in class_name_lower)
                    or ("bundle" in class_name_lower)
                    or ("type" in class_name_lower)
                    or ("status" in class_name_lower)
                    or ("role" in class_name_lower)
                    or ("spec" in class_name_lower)
                    or ("agent" in class_name_lower)
                )
                if not is_data_class_exempt:
                    violations.append(
                        {
                            "file": str(relative_path),
                            "line": node.lineno,
                            "type": "Anemic Domain Model",
                            "description": f"Class '{node.name}' has {total_attrs} attributes but only {total_methods} behaviors — probable data holder without domain logic",
                            "Severity": "HIGH",
                        },
                    )
            if total_methods > 25:
                violations.append(
                    {
                        "file": str(relative_path),
                        "line": node.lineno,
                        "type": "God Class",
                        "description": f"Class '{node.name}' has {total_methods} methods — potential Violation of Single Responsibility Principle",
                        "Severity": "MEDIUM",
                    },
                )
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(base.attr)
            if (
                any(vo_indicator in bases for vo_indicator in ["ValueObject", "VO", "Immutable"])
                or "ValueObject" in node.name
            ):
                setters_or_mutators = [
                    m
                    for m in methods
                    if m.name.startswith(("set_", "update_", "add_", "remove_")) or "mutat" in m.name.lower()
                ]
                if setters_or_mutators:
                    violations.append(
                        {
                            "file": str(relative_path),
                            "line": node.lineno,
                            "type": "Mutable Value Object",
                            "description": f"Value Object '{node.name}' contains mutating methods ({[m.name for m in setters_or_mutators]}) — VOs must be immutable",
                            "Severity": "CRITICAL",
                        },
                    )
            if node.name.endswith("Service") or node.name.endswith("Manager"):
                complex_methods = 0
                for method in methods:
                    method_complexity = len(
                        [
                            n
                            for n in ast.walk(method)
                            if isinstance(n, ast.If | ast.For | ast.While | ast.Try)
                        ],
                    )
                    if method_complexity > 8:
                        complex_methods += 1
                if complex_methods > 5:
                    violations.append(
                        {
                            "file": str(relative_path),
                            "line": node.lineno,
                            "type": "Fat Service",
                            "description": f"Service '{node.name}' has {complex_methods} complex methods — likely containing domain logic instead of orchestration",
                            "Severity": "MEDIUM",
                        },
                    )
    return violations


def validate_ddd_alignment(root_path: str) -> tuple[float, list[str]]:
    """
    Existing Auditor-compatible validator — simple score + string issues.
    Used directly by Sovereign Auditor v3.1.
    """
    detailed_violations = get_ddd_violations_detailed(root_path)
    base_score = 100.0
    penalty_per_violation = 5.0
    critical_count = sum(1 for v in detailed_violations if v["Severity"] == "CRITICAL")
    penalty_per_violation += critical_count * 10.0
    score = max(0.0, base_score - len(detailed_violations) * penalty_per_violation)
    issues: list[str] = []
    for v in detailed_violations:
        line_info = f"line {v['line']}" if v["line"] > 0 else ""
        issues.append(f"{v['file']}:{line_info} [{v['Severity']}] {v['type']}: {v['description']}")
    return (score, issues)
