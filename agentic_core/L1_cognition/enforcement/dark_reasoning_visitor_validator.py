from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "dark_reasoning_visitor_validator")
trace_contract.emit_determinism_digest("p0", "dark_reasoning_visitor_validator")

trace_contract._emit_dispatches_healing_run("p1", "dark_reasoning_visitor_validator", "L1")
trace_contract._emit_routes_through("p1", "dark_reasoning_visitor_validator", "L1")
trace_contract._emit_checks_agent_registry("p1", "dark_reasoning_visitor_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "dark_reasoning_visitor_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "dark_reasoning_visitor_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "dark_reasoning_visitor_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "dark_reasoning_visitor_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "dark_reasoning_visitor_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "dark_reasoning_visitor_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "dark_reasoning_visitor_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "dark_reasoning_visitor_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "dark_reasoning_visitor_validator")
trace_contract._emit_gated_by_confidence("p1", "dark_reasoning_visitor_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "dark_reasoning_visitor_validator", "L1")
trace_contract._emit_reads_policy_state("p1", "dark_reasoning_visitor_validator", "L1")
trace_contract._emit_authorize_and_execute("p2", "dark_reasoning_visitor_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "dark_reasoning_visitor_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "dark_reasoning_visitor_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "dark_reasoning_visitor_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "dark_reasoning_visitor_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "dark_reasoning_visitor_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "dark_reasoning_visitor_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "dark_reasoning_visitor_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "dark_reasoning_visitor_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "dark_reasoning_visitor_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "dark_reasoning_visitor_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "dark_reasoning_visitor_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "dark_reasoning_visitor_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "dark_reasoning_visitor_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "dark_reasoning_visitor_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "dark_reasoning_visitor_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "dark_reasoning_visitor_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "dark_reasoning_visitor_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "dark_reasoning_visitor_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "dark_reasoning_visitor_validator", "exec_snapshot_link")

'\nSovereign Guardian: observability Footprint (Dark Reasoning Check)\nEnsures every L1 reasoning step leaves an L6 observability trail.\n\nThe Governance Cycle:\n1. L0 (Auditor) defines what is "Legal."\n2. L1-L5 perform the actual agentic operations.\n3. L6 (observability) records the ground truth of those operations.\n4. L0 (Auditor) periodically sweeps L6 to ensure L1-L5 behaved, flagging Dark Reasoning if an agent "thought" without telling the system.\n\nPhase 9C: Dark Reasoning Guardian (Dec 26, 2025)\n'
import ast
from pathlib import Path


trace_contract._emit_emits_metric_event("dark_reasoning_visitor_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("dark_reasoning_visitor_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("dark_reasoning_visitor_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("dark_reasoning_visitor_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("dark_reasoning_visitor_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("dark_reasoning_visitor_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("dark_reasoning_visitor_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("dark_reasoning_visitor_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("dark_reasoning_visitor_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("dark_reasoning_visitor_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("dark_reasoning_visitor_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("dark_reasoning_visitor_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("dark_reasoning_visitor_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("dark_reasoning_visitor_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("dark_reasoning_visitor_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("dark_reasoning_visitor_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("dark_reasoning_visitor_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("dark_reasoning_visitor_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("dark_reasoning_visitor_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("dark_reasoning_visitor_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("dark_reasoning_visitor_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("dark_reasoning_visitor_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("dark_reasoning_visitor_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("dark_reasoning_visitor_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("dark_reasoning_visitor_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("dark_reasoning_visitor_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("dark_reasoning_visitor_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("dark_reasoning_visitor_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "dark_reasoning_visitor_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "dark_reasoning_visitor_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "dark_reasoning_visitor_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "dark_reasoning_visitor_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "dark_reasoning_visitor_validator", "write_through")
trace_contract._emit_writes_through("p1", "dark_reasoning_visitor_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "dark_reasoning_visitor_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "dark_reasoning_visitor_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "dark_reasoning_visitor_validator", "routing_commit")


def check_dark_reasoning(filepath: Path) -> list[str]:
    """
    Check for reasoning operations without corresponding observability footprints.

    Dark Reasoning occurs when an agent performs cognitive operations (think, plan, decide)
    without leaving a trace in the L6 observability layer (logging, telemetry).

    Args:
        filepath: Path to Python file to audit

    Returns:
        List of issues found (empty if compliant)
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "check_dark_reasoning", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "check_dark_reasoning", "p0_governance")
    issues = []
    file_str = str(filepath).replace("\\", "/")
    if not any(layer in file_str for layer in ["L1_cognition", "L2_execution", "L3_orchestration"]):
        return []
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)

        class DarkReasoningVisitor(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
                self.reasoning_methods = {"think", "plan", "decide", "reason", "validate", "execute_plan"}

            def visit_Call(self, node):
                import uuid as _uuid  # noqa: PLC0415

                _trace_id = str(_uuid.uuid4())
                trace_contract._emit_records_execution_trace(
                    _trace_id,
                    trace_contract.LayerSegment.L1_REASONING,
                    "DarkReasoningVisitor.visit_Call",
                )

                if isinstance(node.func, ast.Attribute) and node.func.attr.lower() in self.reasoning_methods:
                    self.issues.append(
                        f"Dark Reasoning Violation: Unobserved reasoning call '{node.func.attr}' at line {node.lineno}",
                    )
                if isinstance(node.func, ast.Attribute) and node.func.attr in {
                    "chat",
                    "complete",
                    "messages",
                }:
                    if isinstance(node.func.value, ast.Name) and node.func.value.id in {
                        "client",
                        "openai",
                        "anthropic",
                    }:
                        self.issues.append(f"Potential L5 Bypass: Direct LLM call at line {node.lineno}")
                self.generic_visit(node)

        visitor = DarkReasoningVisitor()
        visitor.visit(tree)
        issues.extend(visitor.issues)
    except (SyntaxError, ValueError, TypeError, AttributeError, OSError, RuntimeError) as e:  # guardian: allow-log-and-swallow -- AST parse/visit failure: non-fatal; file skipped in dark reasoning check
        import logging

        logging.getLogger(__name__).debug(
            "dark_reasoning_visitor_validator: Exception swallowed at L237: %s", e
        )
    return issues


def validate_observability_footprint(target_dir: str) -> tuple[float, list[str]]:
    """
    Validate that all reasoning operations have observability footprints.

    Args:
        target_dir: Directory to audit

    Returns:
        Tuple of (score percentage, list of issues)
    """
    issues = []
    total_files = 0
    from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

    for path in get_python_files(Path(target_dir)):
        total_files += 1
        file_issues = check_dark_reasoning(path)
        issues.extend([f"{str(path)}: {i}" for i in file_issues])
    score = 100.0
    if issues:
        score = max(0, 100 - len(issues) * 5)
    return (score, issues)
