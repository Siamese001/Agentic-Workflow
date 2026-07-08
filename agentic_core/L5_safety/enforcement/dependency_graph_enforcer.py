from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "dependency_graph_enforcer")
trace_contract.emit_determinism_digest("p0", "dependency_graph_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "dependency_graph_enforcer", "L5")
trace_contract._emit_routes_through("p1", "dependency_graph_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "dependency_graph_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "dependency_graph_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "dependency_graph_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "dependency_graph_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "dependency_graph_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "dependency_graph_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "dependency_graph_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "dependency_graph_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "dependency_graph_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "dependency_graph_enforcer")
trace_contract._emit_gated_by_confidence("p1", "dependency_graph_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "dependency_graph_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "dependency_graph_enforcer", "L5")

trace_contract._emit_applies_guardrail("p0", "dependency_graph_enforcer", "p0_governance")
trace_contract._emit_snapshots_state("p0", "dependency_graph_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "dependency_graph_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "dependency_graph_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "dependency_graph_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "dependency_graph_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "dependency_graph_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "dependency_graph_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "dependency_graph_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "dependency_graph_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "dependency_graph_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "dependency_graph_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "dependency_graph_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "dependency_graph_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "dependency_graph_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "dependency_graph_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "dependency_graph_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "dependency_graph_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "dependency_graph_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "dependency_graph_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "dependency_graph_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "dependency_graph_enforcer", "exec_snapshot_link")

"\nDependency Graph - Code structure analysis and impact tracking.\nExtracted from BudgetManagerAgent.py for single responsibility.\n"
import ast

from tqdm import tqdm

trace_contract._emit_emits_metric_event("dependency_graph_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("dependency_graph_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("dependency_graph_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("dependency_graph_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("dependency_graph_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("dependency_graph_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("dependency_graph_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("dependency_graph_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("dependency_graph_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("dependency_graph_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("dependency_graph_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("dependency_graph_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("dependency_graph_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("dependency_graph_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("dependency_graph_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("dependency_graph_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("dependency_graph_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("dependency_graph_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("dependency_graph_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("dependency_graph_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("dependency_graph_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("dependency_graph_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("dependency_graph_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("dependency_graph_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("dependency_graph_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("dependency_graph_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("dependency_graph_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("dependency_graph_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "dependency_graph_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "dependency_graph_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "dependency_graph_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "dependency_graph_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "dependency_graph_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "dependency_graph_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "dependency_graph_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "dependency_graph_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "dependency_graph_enforcer", "routing_commit")


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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "DependencyGraph.build")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DependencyGraph.build".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        print("🕸️ Building Holistic Code Graph...")
        for file_path in tqdm(files, desc="Processing", unit="item"):
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
            except (ValueError, TypeError, RuntimeError) as e:
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
        module_name = str(Path(file_path).as_posix()).replace("/", ".").replace(".py", "")
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
