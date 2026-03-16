from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "dependency_graph_enforcer")
emit_determinism_digest("p0", "dependency_graph_enforcer")

_emit_dispatches_healing_run("p1", "dependency_graph_enforcer", "L5")
_emit_routes_through("p1", "dependency_graph_enforcer", "L5")
_emit_escalates_to_human("p1", "dependency_graph_enforcer", "L5")
_emit_reads_policy_state("p1", "dependency_graph_enforcer", "L5")

_emit_applies_guardrail("p0", "dependency_graph_enforcer", "p0_governance")
_emit_snapshots_state("p0", "dependency_graph_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "dependency_graph_enforcer", "execution_auth")
_emit_validates_capability("p2", "dependency_graph_enforcer", "capability_check")
_emit_routes_to_capability("p2", "dependency_graph_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "dependency_graph_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "dependency_graph_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "dependency_graph_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "dependency_graph_enforcer", "exec_output")
_emit_dispatches_agent("p3", "dependency_graph_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "dependency_graph_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "dependency_graph_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "dependency_graph_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "dependency_graph_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "dependency_graph_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "dependency_graph_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "dependency_graph_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "dependency_graph_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "dependency_graph_enforcer", "eval_metric")
_emit_stores_embedding("p4", "dependency_graph_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "dependency_graph_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "dependency_graph_enforcer", "exec_snapshot_link")

"\nDependency Graph - Code structure analysis and impact tracking.\nExtracted from BudgetManagerAgent.py for single responsibility.\n"
import ast

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class DependencyGraph:
    """Builds a directed graph of imports and class hierarchies."""

    def __init__(self):
        """Initialize empty dependency graph."""
        self.graph: dict[str, dict[str, list[str]]] = {}
        self.reverse_graph: dict[str, list[str]] = {}

    def build(self, files: list[str]) -> None:
        """Build the dependency graph from a list of Python files.

        Args:
            files: List of Python file paths to analyze
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "DependencyGraph.build")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DependencyGraph.build".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        print("🕸️ Building Holistic Code Graph...")
        for file_path in files:
            self.graph[file_path] = {"imports": [], "classes": []}
            try:
                with open(file_path, encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            self.graph[file_path]["imports"].append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.graph[file_path]["imports"].append(node.module)
                    elif isinstance(node, ast.ClassDef):
                        self.graph[file_path]["classes"].append(node.name)
            except Exception:
                raise
                pass
        for file, data in self.graph.items():
            for imp in data["imports"]:
                if imp not in self.reverse_graph:
                    self.reverse_graph[imp] = []
                self.reverse_graph[imp].append(file)

    def get_impact_radius(self, file_path: str) -> list[str]:
        """Returns files that import modules defined in file_path.

        Args:
            file_path: Path to file to analyze

        Returns:
            List of file paths that would be impacted by changes
        """
        impacted = set()
        module_name = file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        if module_name in self.reverse_graph:
            impacted.update(self.reverse_graph[module_name])
        return list(impacted)

    def get_imports(self, file_path: str) -> list[str]:
        """Get all imports for a specific file.

        Args:
            file_path: Path to file

        Returns:
            List of imported module names
        """
        return self.graph.get(file_path, {}).get("imports", [])

    def get_classes(self, file_path: str) -> list[str]:
        """Get all class definitions in a specific file.

        Args:
            file_path: Path to file

        Returns:
            List of class names defined in the file
        """
        return self.graph.get(file_path, {}).get("classes", [])

    def get_all_files(self) -> list[str]:
        """Get all files in the dependency graph.

        Returns:
            List of all analyzed file paths
        """
        return list(self.graph.keys())

    def clear(self) -> None:
        """Clear all graph data."""
        self.graph.clear()
        self.reverse_graph.clear()
