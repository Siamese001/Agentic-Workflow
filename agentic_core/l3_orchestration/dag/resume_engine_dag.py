"""
Resume Engine DAG Module
LEVEL 5 - Directed Acyclic Graph execution engine for resume processing operations
"""

from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

@dataclass
class DAGNode:
    """Represents a node in the execution DAG"""
    node_id: str
    node_type: str
    dependencies: List[str]
    function: Callable
    parameters: Dict[str, Any]
    status: str = "pending"

@dataclass
class DAGExecutionResult:
    """Represents the result of DAG execution"""
    execution_id: str
    nodes_executed: List[str]
    execution_time: float
    success: bool
    results: Dict[str, Any]

class ResumeEngineDAG:
    """Handles DAG execution for resume processing operations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nodes: Dict[str, DAGNode] = {}
        self.execution_history: List[DAGExecutionResult] = []

    def add_node(
        self,
        node_id: str,
        node_type: str,
        dependencies: List[str],
        function: Callable,
        parameters: Dict[str, Any] = None
    ) -> None:
        """Add a node to the DAG"""
        if parameters is None:
            parameters = {}

        node = DAGNode(
            node_id=node_id,
            node_type=node_type,
            dependencies=dependencies,
            function=function,
            parameters=parameters
        )

        self.nodes[node_id] = node
        self.logger.info(f"Added node {node_id} of type {node_type}")

    async def execute_dag(self, input_data: Dict[str, Any]) -> DAGExecutionResult:
        """Execute the complete DAG"""
        try:
            start_time = datetime.utcnow()
            execution_id = f"dag_exec_{int(start_time.timestamp())}"

            # Validate DAG structure
            self._validate_dag()

            # Execute nodes in dependency order
            executed_nodes = []
            results = {}

            # Get execution order
            execution_order = self._get_execution_order()

            # Execute each node
            for node_id in execution_order:
                node = self.nodes[node_id]

                # Prepare node input
                node_input = self._prepare_node_input(node, results, input_data)

                # Execute node
                node_result = await self._execute_node(node, node_input)
                results[node_id] = node_result
                executed_nodes.append(node_id)

                self.logger.info(f"Executed node {node_id}")

            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            result = DAGExecutionResult(
                execution_id=execution_id,
                nodes_executed=executed_nodes,
                execution_time=execution_time,
                success=True,
                results=results
            )

            self.execution_history.append(result)
            return result

        except Exception as e:
            self.logger.error(f"DAG execution failed: {str(e)}")
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            result = DAGExecutionResult(
                execution_id=execution_id,
                nodes_executed=executed_nodes if 'executed_nodes' in locals() else [],
                execution_time=execution_time,
                success=False,
                results={"error": str(e)}
            )

            self.execution_history.append(result)
            return result

    def _validate_dag(self) -> None:
        """Validate DAG structure for circular dependencies"""
        # Simple validation - check for circular dependencies
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            if node_id in self.nodes:
                for dep in self.nodes[node_id].dependencies:
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if has_cycle(node_id):
                raise ValueError(f"Circular dependency detected involving node {node_id}")

    def _get_execution_order(self) -> List[str]:
        """Get topological order for node execution"""
        in_degree = {node_id: 0 for node_id in self.nodes}

        # Calculate in-degrees
        for node_id, node in self.nodes.items():
            for dep in node.dependencies:
                if dep in in_degree:
                    in_degree[node_id] += 1

        # Topological sort
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        execution_order = []

        while queue:
            current = queue.pop(0)
            execution_order.append(current)

            # Update in-degrees of dependent nodes
            for node_id, node in self.nodes.items():
                if current in node.dependencies:
                    in_degree[node_id] -= 1
                    if in_degree[node_id] == 0:
                        queue.append(node_id)

        return execution_order

    def _prepare_node_input(
        self, node: DAGNode, results: Dict[str, Any], input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare input data for node execution"""
        node_input = {**input_data, **node.parameters}

        # Add results from dependency nodes
        for dep in node.dependencies:
            if dep in results:
                node_input[f"dep_{dep}"] = results[dep]

        return node_input

    async def _execute_node(self, node: DAGNode, node_input: Dict[str, Any]) -> Any:
        """Execute a single node"""
        try:
            node.status = "running"

            if asyncio.iscoroutinefunction(node.function):
                result = await node.function(**node_input)
            else:
                result = node.function(**node_input)

            node.status = "completed"
            return result

        except Exception as e:
            node.status = "failed"
            raise e

    def get_execution_history(self) -> List[DAGExecutionResult]:
        """Get history of DAG executions"""
        return self.execution_history.copy()

    def clear_dag(self) -> None:
        """Clear all nodes from the DAG"""
        self.nodes.clear()
        self.logger.info("Cleared all nodes from DAG")

# Mock resume processing functions for demonstration
async def extract_resume_data(resume_text: str) -> Dict[str, Any]:
    """Mock function to extract data from resume"""
    await asyncio.sleep(0.1)  # Simulate processing time
    return {
        "skills": ["Python", "JavaScript", "Machine Learning"],
        "experience": "5 years",
        "education": "BS Computer Science"
    }

async def analyze_resume_skills(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Mock function to analyze resume skills"""
    await asyncio.sleep(0.1)
    return {
        "skill_score": 0.85,
        "recommendations": ["Add cloud certifications", "Include project details"]
    }

async def generate_resume_summary(resume_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Mock function to generate resume summary"""
    await asyncio.sleep(0.1)
    return {
        "summary": "Experienced software engineer with strong technical skills",
        "score": 0.82
    }

__all__ = ["ResumeEngineDAG", "DAGNode", "DAGExecutionResult", "extract_resume_data", "analyze_resume_skills", "generate_resume_summary"]
