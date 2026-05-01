"""
Graph-coordinated orchestration for L3 orchestration layer.

Uses ADG graph analysis to coordinate multi-agent workflows, optimize
execution paths, and manage dependencies across the system.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import sys
from dataclasses import dataclass
from enum import Enum

# Add tools to path for graph utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "tools"))

from tools.adg.analysis.sqlite_direct import GraphQueryHelper
from tools.adg.analysis.networkx_analysis import NetworkXAnalyzer

logger = logging.getLogger(__name__)


class ExecutionStrategy(Enum):
    """Execution strategy for orchestrated workflows."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINED = "pipelined"
    ADAPTIVE = "adaptive"


@dataclass
class WorkflowStep:
    """Single step in an orchestrated workflow."""

    step_id: str
    agent_id: str
    action: str
    dependencies: Set[str]
    estimated_duration: float
    critical_path_score: float
    layer: str


class GraphCoordinatedOrchestrator:
    """L3 orchestrator with graph-based coordination."""

    def __init__(self, adg_snapshot_path: str):
        """
        Initialize graph-coordinated orchestrator.

        Args:
            adg_snapshot_path: Path to ADG SQLite snapshot
        """
        self.graph_helper = GraphQueryHelper(adg_snapshot_path)
        self.networkx_analyzer = NetworkXAnalyzer(adg_snapshot_path)
        self._active_workflows = {}
        self._execution_cache = {}

    def plan_workflow(self, workflow_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan workflow using graph-based dependency analysis.

        Args:
            workflow_spec: Workflow specification with agents and actions

        Returns:
            Execution plan with optimized ordering and coordination
        """
        workflow_id = workflow_spec.get("workflow_id", "unknown")

        try:
            # Analyze workflow components in graph context
            step_analysis = self._analyze_workflow_steps(workflow_spec)

            # Build dependency graph
            dependency_graph = self._build_dependency_graph(step_analysis)

            # Optimize execution order
            optimized_plan = self._optimize_execution_order(dependency_graph, step_analysis)

            # Identify coordination points
            coordination_points = self._identify_coordination_points(optimized_plan)

            # Calculate execution metrics
            execution_metrics = self._calculate_execution_metrics(optimized_plan)

            plan = {
                "workflow_id": workflow_id,
                "execution_plan": optimized_plan,
                "coordination_points": coordination_points,
                "metrics": execution_metrics,
                "strategy": self._determine_execution_strategy(optimized_plan),
            }

            self._active_workflows[workflow_id] = plan
            return plan

        except Exception as e:  # guardian: allow-broad-exception -- workflow planning failure: non-fatal; error dict returned so caller can handle gracefully
            logger.error(f"Failed to plan workflow {workflow_id}: {e}")
            return {"error": str(e), "workflow_id": workflow_id}

    def _analyze_workflow_steps(self, workflow_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze individual workflow steps in graph context."""
        steps = workflow_spec.get("steps", [])
        analyzed_steps = []

        for step in steps:
            agent_id = step.get("agent_id")
            action = step.get("action")

            try:
                # Find agent in graph
                agent_nodes = self.graph_helper.find_nodes_by_name(agent_id)

                if not agent_nodes:
                    logger.warning(f"Agent {agent_id} not found in ADG")
                    analyzed_step = {**step, "graph_analysis": {"found": False, "risk_level": "unknown"}}
                else:
                    agent_node = agent_nodes[0]
                    node_id = agent_node["id"]

                    # Analyze agent's graph position
                    fan_in = self.graph_helper.get_fan_in(node_id)
                    fan_out = self.graph_helper.get_fan_out(node_id)

                    # Check for critical path involvement
                    critical_paths = self._check_critical_path_involvement(node_id)

                    analyzed_step = {
                        **step,
                        "graph_analysis": {
                            "found": True,
                            "node_id": node_id,
                            "layer": agent_node.get("layer", "unknown"),
                            "fan_in_count": len(fan_in),
                            "fan_out_count": len(fan_out),
                            "critical_path_score": self._calculate_critical_path_score(critical_paths),
                            "risk_level": self._assess_agent_risk(fan_in, fan_out, agent_node.get("layer")),
                        },
                    }

                analyzed_steps.append(analyzed_step)

            except Exception as e:  # guardian: allow-broad-exception -- step analysis failure: non-fatal; degraded step included in results
                logger.error(f"Failed to analyze step {step}: {e}")
                analyzed_steps.append({**step, "graph_analysis": {"found": False, "error": str(e)}})

        return analyzed_steps

    def _build_dependency_graph(self, step_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build dependency graph for workflow steps."""
        dependency_graph = {}

        for step in step_analysis:
            step_id = step.get("step_id")
            dependencies = set(step.get("dependencies", []))

            # Add graph-based dependencies
            graph_analysis = step.get("graph_analysis", {})
            if graph_analysis.get("found"):
                # Check for implicit dependencies based on graph structure
                implicit_deps = self._find_implicit_dependencies(step, step_analysis)
                dependencies.update(implicit_deps)

            dependency_graph[step_id] = {"dependencies": dependencies, "step": step, "dependents": set()}

        # Build reverse dependencies
        for step_id, deps in dependency_graph.items():
            for dep in deps["dependencies"]:
                if dep in dependency_graph:
                    dependency_graph[dep]["dependents"].add(step_id)

        return dependency_graph

    def _optimize_execution_order(
        self, dependency_graph: Dict[str, Any], step_analysis: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Optimize execution order using graph analysis."""
        # Use topological sort with priority scoring
        ordered_steps = []
        remaining_steps = set(dependency_graph.keys())

        # Priority queue based on critical path score and dependencies
        def get_priority(step_id: str) -> float:
            step = dependency_graph[step_id]["step"]
            graph_analysis = step.get("graph_analysis", {})
            critical_score = graph_analysis.get("critical_path_score", 0)

            # Higher priority for critical path steps
            # Lower priority for steps with many dependents (they block others)
            dependent_count = len(dependency_graph[step_id]["dependents"])

            return critical_score - (dependent_count * 0.1)

        while remaining_steps:
            # Find steps with no unmet dependencies
            ready_steps = [
                step_id
                for step_id in remaining_steps
                if not dependency_graph[step_id]["dependencies"].intersection(remaining_steps)
            ]

            if not ready_steps:
                raise ValueError("Circular dependency detected in workflow")

            # Sort by priority
            ready_steps.sort(key=get_priority, reverse=True)

            # Add highest priority step to execution order
            next_step = ready_steps[0]
            ordered_steps.append(dependency_graph[next_step]["step"])
            remaining_steps.remove(next_step)

        return ordered_steps

    def _identify_coordination_points(self, optimized_plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify points requiring coordination across agents."""
        coordination_points = []

        for i, step in enumerate(optimized_plan):
            step_id = step.get("step_id")
            graph_analysis = step.get("graph_analysis", {})

            # Identify coordination needs
            coordination_needs = []

            # Cross-layer coordination
            if i > 0:
                prev_step = optimized_plan[i - 1]
                prev_layer = prev_step.get("graph_analysis", {}).get("layer")
                curr_layer = graph_analysis.get("layer")

                if prev_layer and curr_layer and prev_layer != curr_layer:
                    coordination_needs.append(
                        {
                            "type": "cross_layer_transition",
                            "from_layer": prev_layer,
                            "to_layer": curr_layer,
                            "reason": "Layer boundary crossing",
                        }
                    )

            # High-risk agent coordination
            risk_level = graph_analysis.get("risk_level", "low")
            if risk_level == "high":
                coordination_needs.append(
                    {
                        "type": "high_risk_coordination",
                        "risk_level": risk_level,
                        "reason": "High-risk agent requires coordination",
                    }
                )

            # Critical path coordination
            critical_score = graph_analysis.get("critical_path_score", 0)
            if critical_score > 0.7:
                coordination_needs.append(
                    {
                        "type": "critical_path_coordination",
                        "critical_score": critical_score,
                        "reason": "Critical path step requires careful coordination",
                    }
                )

            if coordination_needs:
                coordination_points.append(
                    {"step_id": step_id, "step_index": i, "coordination_needs": coordination_needs}
                )

        return coordination_points

    def _calculate_execution_metrics(self, optimized_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate execution metrics for the workflow."""
        total_duration = 0
        critical_path_duration = 0
        parallelizable_steps = 0

        for step in optimized_plan:
            duration = step.get("estimated_duration", 1.0)
            total_duration += duration

            graph_analysis = step.get("graph_analysis", {})
            critical_score = graph_analysis.get("critical_path_score", 0)

            if critical_score > 0.5:
                critical_path_duration += duration

            # Check if step can be parallelized
            dependencies = step.get("dependencies", [])
            if not dependencies:
                parallelizable_steps += 1

        parallelism_ratio = parallelizable_steps / len(optimized_plan) if optimized_plan else 0

        return {
            "total_estimated_duration": total_duration,
            "critical_path_duration": critical_path_duration,
            "parallelism_ratio": parallelism_ratio,
            "step_count": len(optimized_plan),
            "coordination_complexity": len(self._identify_coordination_points(optimized_plan)),
        }

    def _determine_execution_strategy(self, optimized_plan: List[Dict[str, Any]]) -> str:
        """Determine optimal execution strategy."""
        metrics = self._calculate_execution_metrics(optimized_plan)

        parallelism_ratio = metrics["parallelism_ratio"]
        coordination_complexity = metrics["coordination_complexity"]

        if parallelism_ratio > 0.7 and coordination_complexity < 3:
            return ExecutionStrategy.PARALLEL.value
        elif parallelism_ratio > 0.4 and coordination_complexity < 5:
            return ExecutionStrategy.PIPELINED.value
        elif coordination_complexity > 5:
            return ExecutionStrategy.ADAPTIVE.value
        else:
            return ExecutionStrategy.SEQUENTIAL.value

    def _find_implicit_dependencies(self, step: Dict[str, Any], all_steps: List[Dict[str, Any]]) -> Set[str]:
        """Find implicit dependencies based on graph structure."""
        implicit_deps = set()

        graph_analysis = step.get("graph_analysis", {})
        if not graph_analysis.get("found"):
            return implicit_deps

        node_id = graph_analysis["node_id"]

        # Check for data flow dependencies
        try:
            data_flow = self.graph_helper.get_fan_in(node_id, relation_types=["reads_from", "writes_to"])

            for dep in data_flow:
                dep_name = dep.get("target_adg_name", "")

                # Find if any other step produces this data
                for other_step in all_steps:
                    if other_step.get("step_id") == step.get("step_id"):
                        continue

                    other_agent = other_step.get("agent_id", "")
                    if dep_name in other_agent or other_agent in dep_name:
                        implicit_deps.add(other_step.get("step_id"))

        except Exception as e:  # guardian: allow-broad-exception -- implicit dependency resolution optional: non-fatal; empty set returned to caller
            logger.warning(f"Could not find implicit dependencies: {e}")

        return implicit_deps

    def _check_critical_path_involvement(self, node_id: int) -> List[Dict[str, Any]]:
        """Check if node is involved in critical paths."""
        try:
            critical_paths = self.graph_helper.execute_query(
                """
                SELECT path_id, path_criticality_score
                FROM mv_critical_path_blast_radius
                WHERE src_id = ? OR tgt_id = ?
                ORDER BY path_criticality_score DESC
                LIMIT 5
            """,
                [node_id, node_id],
            )

            return critical_paths

        except Exception as e:  # guardian: allow-broad-exception -- critical path check failure: non-fatal; empty list returned
            logger.warning(f"Could not check critical path involvement: {e}")
            return []

    def _calculate_critical_path_score(self, critical_paths: List[Dict[str, Any]]) -> float:
        """Calculate critical path score for a node."""
        if not critical_paths:
            return 0.0

        # Use the highest criticality score
        max_score = max(path.get("path_criticality_score", 0) for path in critical_paths)
        return min(max_score, 1.0)  # Normalize to [0,1]

    def _assess_agent_risk(self, fan_in: List[Dict], fan_out: List[Dict], layer: Optional[str]) -> str:
        """Assess risk level of an agent."""
        fan_in_count = len(fan_in)
        fan_out_count = len(fan_out)

        # Risk factors
        if layer in ["L0_routing", "L5_safety"]:
            return "high"
        elif fan_in_count > 15 or fan_out_count > 10:
            return "medium"
        else:
            return "low"

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of an active workflow."""
        if workflow_id not in self._active_workflows:
            return {"error": f"Workflow {workflow_id} not found"}

        return self._active_workflows[workflow_id]

    def close(self):
        """Clean up resources."""
        self.graph_helper.close()
        self.networkx_analyzer.close()


# Singleton instance for L3 orchestration
_orchestrator = None


def get_graph_orchestrator(adg_snapshot_path: Optional[str] = None) -> GraphCoordinatedOrchestrator:
    """Get or create graph orchestrator singleton."""
    global _orchestrator

    if _orchestrator is None:
        if adg_snapshot_path is None:
            raise ValueError("ADG snapshot path required for first initialization")
        _orchestrator = GraphCoordinatedOrchestrator(adg_snapshot_path)

    return _orchestrator
