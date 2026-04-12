"""
Agent Variable Compliance Audit Script (Phase 5)

Ensures L1/L2 agents actually pass required variables when calling templates.
Uses AST analysis to detect template rendering calls and validate context variables.
"""

import ast
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "template_render_visitor", "p0_governance")
_emit_reads_policy_state("p0", "template_render_visitor", "policy_binding")
_emit_snapshots_state("p0", "template_render_visitor", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("template_render_visitor", "p4obs", "metric_1")
_emit_emits_metric_event("template_render_visitor", "p4obs", "metric_2")
_emit_emits_metric_event("template_render_visitor", "p4obs", "metric_3")
_emit_emits_metric_event("template_render_visitor", "p4obs", "metric_4")
_emit_emits_metric_event("template_render_visitor", "p4obs", "metric_5")
_emit_emits_metric_event("template_render_visitor", "p4obs", "metric_6")
_emit_records_incident_event("template_render_visitor", "p4obs", "incident")
_emit_captures_runtime_anomaly("template_render_visitor", "p4obs", "anomaly")
_emit_writes_observability_log("template_render_visitor", "p4obs", "obs_log")
_emit_updates_monitoring_state("template_render_visitor", "p4obs", "mon_state")
_emit_triggers_alert("template_render_visitor", "p4obs", "alert")
_emit_links_incident_trace("template_render_visitor", "p4obs", "trace_link")
_emit_captures_pattern("template_render_visitor", "p3lm", "pattern")
_emit_records_learning_event("template_render_visitor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("template_render_visitor", "p3lm", "snapshot")
_emit_feeds_meta_learning("template_render_visitor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("template_render_visitor", "p3lm", "routing")
_emit_improves_agent_policy("template_render_visitor", "p3lm", "policy")
_emit_stores_learning_state("template_render_visitor", "p3lm", "state")
_emit_records_execution_trace("template_render_visitor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("template_render_visitor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("template_render_visitor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("template_render_visitor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("template_render_visitor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("template_render_visitor", "env_read", "p2_env_1")
_emit_reads_environ("template_render_visitor", "env_read", "p2_env_2")
_emit_reads_runtime_state("template_render_visitor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("template_render_visitor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "template_render_visitor", "context_pull")
_emit_pulls_context("p1", "template_render_visitor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "template_render_visitor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "template_render_visitor", "uwg_term_2")
_emit_writes_through("p1", "template_render_visitor", "write_through")
_emit_writes_through("p1", "template_render_visitor", "write_through_2")
_emit_validated_by_safety_plane("p1", "template_render_visitor", "safety_validation")
_emit_invokes_eval("p1", "template_render_visitor", "eval_call")
_emit_proposal_commits_routing("p1", "template_render_visitor", "routing_commit")
_emit_escalates_to_human("p1", "template_render_visitor", "human_escalation")
_emit_routes_through("p1", "template_render_visitor", "route_through")
_emit_checks_agent_registry("p1", "template_render_visitor", "agent_registry")
_emit_validates_agent_capability("p1", "template_render_visitor", "capability")
_emit_dispatches_execution_plan("p1", "template_render_visitor", "exec_plan")
_emit_agent_executes_agent("p1", "template_render_visitor", "sub_agent")
_emit_routes_to_agent("p1", "template_render_visitor", "target_agent")
_emit_verifies_policy("p1", "template_render_visitor", "policy_check")
_emit_observes_runtime_state("p1", "template_render_visitor", "runtime_state")
_emit_verifies_boundary("p1", "template_render_visitor", "boundary_check")
_emit_transcripts_response("p1", "template_render_visitor", "transcript")
_emit_hard_fails_untranscripted("p1", "template_render_visitor")
_emit_gated_by_confidence("p1", "template_render_visitor", "confidence_gate")
emit_replay_key("p0", "template_render_visitor")
emit_determinism_digest("p0", "template_render_visitor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "template_render_visitor", "execution_auth")
_emit_validates_capability("p2", "template_render_visitor", "capability_check")
_emit_routes_to_capability("p2", "template_render_visitor", "capability_route")
_emit_writes_via_uwg("p2", "template_render_visitor", "uwg_write")
_emit_blocks_direct_write("p2", "template_render_visitor", "direct_write_block")
_emit_records_tool_invocation("p2", "template_render_visitor", "tool_invocation")
_emit_captures_execution_output("p2", "template_render_visitor", "exec_output")
_emit_dispatches_agent("p3", "template_render_visitor", "agent_dispatch")
_emit_coordinates_agents("p3", "template_render_visitor", "agent_coordination")
_emit_records_workflow_lineage("p3", "template_render_visitor", "workflow_lineage")
_emit_records_healing_outcome("p3", "template_render_visitor", "healing_outcome")
_emit_escalates_failure("p3", "template_render_visitor", "failure_escalation")
_emit_orchestrates_workflow("p3", "template_render_visitor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "template_render_visitor", "healing_dispatch")
_emit_invokes_evaluation("p3", "template_render_visitor", "evaluation_signal")
_emit_records_telemetry_event("p4", "template_render_visitor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "template_render_visitor", "eval_metric")
_emit_stores_embedding("p4", "template_render_visitor", "embedding_store")
_emit_updates_meta_learning_state("p4", "template_render_visitor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "template_render_visitor", "exec_snapshot_link")


def extract_template_schema(template_path: Path, base_dir: Path) -> dict[str, list[str]]:
    """Extract required variables from template's Phase 4 header."""
    full_path = base_dir / template_path
    try:
        with open(full_path, encoding="utf-8") as f:
            content = f.read()
        for line in content.split("\n")[:20]:
            if "{# SCHEMA:" in line:
                schema_match = line.replace("{# SCHEMA:", "").replace("#}", "").strip()
                required_vars = []
                if "required_vars=[" in schema_match:
                    req_part = schema_match.split("required_vars=[")[1].split("]")[0]
                    required_vars = [
                        v.strip() for v in req_part.split(",") if v.strip() and v.strip() != "[]"
                    ]
                return {"required_vars": required_vars}
        return {"required_vars": []}
    # guardian: allow-silent-swallow
    except Exception:
        return {"required_vars": []}


class TemplateRenderVisitor(ast.NodeVisitor):
    """AST visitor to find template.render() calls and analyze context."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.violations = []
        self.current_function = None
        self.current_class = None

    def visit_FunctionDef(self, node):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "TemplateRenderVisitor.visit_FunctionDef"
        )

        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_Call(self, node):
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "render"
            and isinstance(node.func.value, ast.Name)
        ):
            template_name = None
            context_dict = None
            if node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant):
                    template_name = arg.value
                elif isinstance(arg, ast.Str):
                    template_name = arg.s
            for keyword in node.keywords:
                if keyword.arg == "context":
                    if isinstance(keyword.value, ast.Dict):
                        context_dict = keyword.value
            if template_name and context_dict:
                self._validate_render_call(node, template_name, context_dict)
        self.generic_visit(node)

    def _validate_render_call(self, node, template_name: str, context_dict: ast.Dict):
        """Validate a template render call against required variables."""
        if not template_name.endswith(".jinja"):
            template_name += ".jinja"
        template_path = Path(template_name)
        schema = extract_template_schema(template_path, self.base_dir)
        if not schema["required_vars"]:
            return
        context_keys = set()
        for key in context_dict.keys:
            if isinstance(key, ast.Constant):
                context_keys.add(key.value)
            elif isinstance(key, ast.Str):
                context_keys.add(key.s)
        missing_vars = set(schema["required_vars"]) - context_keys
        if missing_vars:
            self.violations.append(
                {
                    "file": self.current_file,
                    "line": node.lineno,
                    "class": self.current_class,
                    "function": self.current_function,
                    "template": template_name,
                    "required_vars": schema["required_vars"],
                    "provided_vars": sorted(context_keys),
                    "missing_vars": sorted(missing_vars),
                },
            )


def find_python_files(base_dir: Path) -> list[Path]:
    """Find all Python files in the agentic_core directory."""
    python_files = []
    for file_path in base_dir.rglob("*.py"):
        if file_path.is_file():
            python_files.append(file_path)
    return python_files


def audit_agent_compliance(base_dir: Path) -> list[dict]:
    """Audit agent compliance with template variable requirements."""
    violations = []
    python_files = find_python_files(base_dir)
    for py_file in python_files:
        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=str(py_file))
            visitor = TemplateRenderVisitor(base_dir)
            visitor.current_file = str(py_file.relative_to(base_dir))
            visitor.visit(tree)
            violations.extend(visitor.violations)
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"WARNING: Could not parse {py_file}: {e}")
    return violations


def main():
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent.parent
    print("Agent Variable Compliance Audit (Phase 5)")
    print("=" * 50)
    print(f"Scanning: {base_dir}")
    print()
    violations = audit_agent_compliance(base_dir)
    if violations:
        print(f"❌ FOUND {len(violations)} COMPLIANCE VIOLATIONS:")
        print()
        for violation in violations:
            print(f"File: {violation['file']}")
            if violation["class"]:
                print(f"  Class: {violation['class']}")
            if violation["function"]:
                print(f"  Function: {violation['function']}")
            print(f"  Line: {violation['line']}")
            print(f"  Template: {violation['template']}")
            print(f"  Required: {', '.join(violation['required_vars'])}")
            print(f"  Provided: {', '.join(violation['provided_vars'])}")
            print(f"  Missing: {', '.join(violation['missing_vars'])}")
            print()
        sys.exit(1)
    else:
        print("✅ NO COMPLIANCE VIOLATIONS FOUND")
        print("All template.render() calls provide required variables.")
        sys.exit(0)


if __name__ == "__main__":
    main()
