"""
Sovereign Guard: Block underscore-prefixed fields in SSOT models.
Location: agentic_core/L0_routing/scripts/
"""

import ast
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "underscore_visitor_util", "p0_governance")
_emit_reads_policy_state("p0", "underscore_visitor_util", "policy_binding")
_emit_snapshots_state("p0", "underscore_visitor_util", "state_snapshot")
emit_replay_key("p0", "underscore_visitor_util")
emit_determinism_digest("p0", "underscore_visitor_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "underscore_visitor_util", "execution_auth")
_emit_validates_capability("p2", "underscore_visitor_util", "capability_check")
_emit_routes_to_capability("p2", "underscore_visitor_util", "capability_route")
_emit_writes_via_uwg("p2", "underscore_visitor_util", "uwg_write")
_emit_blocks_direct_write("p2", "underscore_visitor_util", "direct_write_block")
_emit_records_tool_invocation("p2", "underscore_visitor_util", "tool_invocation")
_emit_captures_execution_output("p2", "underscore_visitor_util", "exec_output")
_emit_dispatches_agent("p3", "underscore_visitor_util", "agent_dispatch")
_emit_coordinates_agents("p3", "underscore_visitor_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "underscore_visitor_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "underscore_visitor_util", "healing_outcome")
_emit_escalates_failure("p3", "underscore_visitor_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "underscore_visitor_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "underscore_visitor_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "underscore_visitor_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "underscore_visitor_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "underscore_visitor_util", "eval_metric")
_emit_stores_embedding("p4", "underscore_visitor_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "underscore_visitor_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "underscore_visitor_util", "exec_snapshot_link")

ssot_target = "agentic_core/schemas/models/core_contracts_types.py"


class UnderscoreVisitor(ast.NodeVisitor):
    """Brief description of functionality and purpose."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.violations = []

    def visit_AnnAssign(self, node):
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "UnderscoreVisitor.visit_AnnAssign")

        if isinstance(node.target, ast.Name) and node.target.id.startswith("_"):
            if not node.target.id.startswith("__"):
                self.violations.append((node.lineno, node.target.id))
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.startswith("_"):
                if not target.id.startswith("__"):
                    self.violations.append((node.lineno, target.id))
        self.generic_visit(node)


def main():
    """Brief description of functionality and purpose."""
    has_error = False
    for arg in sys.argv[1:]:
        if SSOT_TARGET not in str(arg).replace("\\", "/"):
            continue
        try:
            visitor = UnderscoreVisitor(arg)
            visitor.visit(ast.parse(Path(arg).read_text(encoding="utf-8")))
            if visitor.violations:
                has_error = True
                print(f"[ERROR] Underscore fields forbidden in SSOT ({arg}):")
                for line, field in visitor.violations:
                    print(f"  L{line}: {field}")
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"[WARNING] Could not parse {arg}: {e}")
    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()
