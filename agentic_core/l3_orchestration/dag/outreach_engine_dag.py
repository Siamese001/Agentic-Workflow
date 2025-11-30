"""
Outreach Engine DAG Module
LEVEL 5 - Directed Acyclic Graph execution engine for outreach operations
"""

from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging

@dataclass
class OutreachDAGNode:
    """Represents a node in the outreach execution DAG"""
    node_id: str
    node_type: str
    dependencies: List[str]
    function: Callable
    parameters: Dict[str, Any]
    status: str = "pending"

@dataclass
class OutreachDAGExecutionResult:
    """Represents the result of outreach DAG execution"""
    execution_id: str
    nodes_executed: List[str]
    execution_time: float
    success: bool
    results: Dict[str, Any]

class OutreachEngineDAG:
    """Handles DAG execution for outreach operations"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nodes: Dict[str, OutreachDAGNode] = {}
        self.execution_history: List[OutreachDAGExecutionResult] = []

    def add_node(
        self,
        node_id: str,
        node_type: str,
        dependencies: List[str],
        function: Callable,
        parameters: Dict[str, Any] = None
    ) -> None:
        """Add a node to the outreach DAG"""
        if parameters is None:
            parameters = {}

        node = OutreachDAGNode(
            node_id=node_id,
            node_type=node_type,
            dependencies=dependencies,
            function=function,
            parameters=parameters
        )

        self.nodes[node_id] = node
        self.logger.info(f"Added outreach node {node_id} of type {node_type}")

    async def execute_dag(self, input_data: Dict[str, Any]) -> OutreachDAGExecutionResult:
        """Execute the complete outreach DAG"""
        try:
            start_time = datetime.utcnow()
            execution_id = f"outreach_dag_exec_{int(start_time.timestamp())}"

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

                self.logger.info(f"Executed outreach node {node_id}")

            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            result = OutreachDAGExecutionResult(
                execution_id=execution_id,
                nodes_executed=executed_nodes,
                execution_time=execution_time,
                success=True,
                results=results
            )

            self.execution_history.append(result)
            return result

        except Exception as e:
            self.logger.error(f"Outreach DAG execution failed: {str(e)}")
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            result = OutreachDAGExecutionResult(
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
        self, node: OutreachDAGNode, results: Dict[str, Any], input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare input data for node execution"""
        node_input = {**input_data, **node.parameters}

        # Add results from dependency nodes
        for dep in node.dependencies:
            if dep in results:
                node_input[f"dep_{dep}"] = results[dep]

        return node_input

    async def _execute_node(self, node: OutreachDAGNode, node_input: Dict[str, Any]) -> Any:
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

    def get_execution_history(self) -> List[OutreachDAGExecutionResult]:
        """Get history of DAG executions"""
        return self.execution_history.copy()

    def clear_dag(self) -> None:
        """Clear all nodes from the DAG"""
        self.nodes.clear()
        self.logger.info("Cleared all nodes from outreach DAG")

# Mock outreach processing functions for demonstration
async def research_contact(contact_info: Dict[str, Any]) -> Dict[str, Any]:
    """Mock function to research contact"""
    await asyncio.sleep(0.1)
    return {
        "contact_id": contact_info.get("email"),
        "company": contact_info.get("company"),
        "title": contact_info.get("title"),
        "research_confidence": 0.85
    }

async def personalize_message(contact_data: Dict[str, Any], message_template: str) -> Dict[str, Any]:
    """Mock function to personalize message"""
    await asyncio.sleep(0.1)
    return {
        "personalized_message": message_template.replace("{{name}}", contact_data.get("name", "there")),
        "personalization_score": 0.9
    }

async def send_outreach(message_data: Dict[str, Any], contact_data: Dict[str, Any]) -> Dict[str, Any]:
    """Mock function to send outreach"""
    await asyncio.sleep(0.1)
    return {
        "message_id": f"msg_{int(datetime.utcnow().timestamp())}",
        "status": "sent",
        "delivery_confidence": 0.95
    }

__all__ = ["OutreachEngineDAG", "OutreachDAGNode", "OutreachDAGExecutionResult", "research_contact", "personalize_message", "send_outreach"]
