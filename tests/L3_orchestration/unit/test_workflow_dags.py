"""
L3 Orchestration Layer Unit Tests - Workflow DAGs

Tests for workflow DAG construction and execution without planning logic.
Focuses on directed acyclic graphs, dependency resolution, and execution ordering.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import time
import uuid

# Mark all tests in this module as L3 orchestration unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l3, pytest.mark.orchestration]


class NodeStatus(Enum):
    """Node execution status in workflow DAG."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class MockWorkflowNode:
    """Mock workflow node for DAG testing."""
    node_id: str
    node_type: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    status: NodeStatus
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    execution_time: Optional[float]


@dataclass(frozen=True)
class MockWorkflowDAG:
    """Mock workflow DAG for testing."""
    dag_id: str
    nodes: List[MockWorkflowNode]
    edges: List[Tuple[str, str]]  # (from_node, to_node)
    execution_order: List[str]
    critical_path: List[str]


class TestDAGConstruction:
    """Test DAG construction and validation."""
    
    def test_basic_dag_creation(self):
        """Test creation of basic workflow DAG."""
        nodes = [
            MockWorkflowNode(
                node_id="extract_requirements",
                node_type="extraction",
                parameters={"text": "job_description"},
                dependencies=[],
                status=NodeStatus.PENDING,
                result=None,
                error=None,
                execution_time=None
            ),
            MockWorkflowNode(
                node_id="parse_resume",
                node_type="parsing",
                parameters={"text": "resume_content"},
                dependencies=[],
                status=NodeStatus.PENDING,
                result=None,
                error=None,
                execution_time=None
            ),
            MockWorkflowNode(
                node_id="analyze_match",
                node_type="analysis",
                parameters={"requirements": "from_extract", "resume": "from_parse"},
                dependencies=["extract_requirements", "parse_resume"],
                status=NodeStatus.PENDING,
                result=None,
                error=None,
                execution_time=None
            ),
            MockWorkflowNode(
                node_id="generate_improvements",
                node_type="synthesis",
                parameters={"analysis": "from_analyze"},
                dependencies=["analyze_match"],
                status=NodeStatus.PENDING,
                result=None,
                error=None,
                execution_time=None
            )
        ]
        
        # Build edges from dependencies
        edges = []
        for node in nodes:
            for dep in node.dependencies:
                edges.append((dep, node.node_id))
        
        dag = MockWorkflowDAG(
            dag_id="dag_001",
            nodes=nodes,
            edges=edges,
            execution_order=["extract_requirements", "parse_resume", "analyze_match", "generate_improvements"],
            critical_path=["extract_requirements", "parse_resume", "analyze_match", "generate_improvements"]
        )
        
        # Validate DAG structure
        assert dag.dag_id.startswith("dag_")
        assert len(dag.nodes) == 4
        assert len(dag.edges) == 3  # extract->analyze, parse->analyze, analyze->generate
        
        # Validate dependency relationships
        extract_node = next(n for n in nodes if n.node_id == "extract_requirements")
        analyze_node = next(n for n in nodes if n.node_id == "analyze_match")
        
        assert len(extract_node.dependencies) == 0
        assert len(analyze_node.dependencies) == 2
        assert "extract_requirements" in analyze_node.dependencies
        assert "parse_resume" in analyze_node.dependencies
    
    def test_dag_acyclic_validation(self):
        """Test DAG validation for acyclic property."""
        
        # Mock DAG validator
        class DAGValidator:
            @staticmethod
            def has_cycle(nodes: List[MockWorkflowNode]) -> bool:
                """Check if DAG has cycles using DFS."""
                # Build adjacency list
                adj_list = {}
                for node in nodes:
                    adj_list[node.node_id] = node.dependencies
                
                visited = set()
                rec_stack = set()
                
                def dfs(node_id: str) -> bool:
                    visited.add(node_id)
                    rec_stack.add(node_id)
                    
                    for neighbor in adj_list.get(node_id, []):
                        if neighbor not in visited:
                            if dfs(neighbor):
                                return True
                        elif neighbor in rec_stack:
                            return True
                    
                    rec_stack.remove(node_id)
                    return False
                
                for node in nodes:
                    if node.node_id not in visited:
                        if dfs(node.node_id):
                            return True
                
                return False
        
        validator = DAGValidator()
        
        # Test valid DAG (no cycles)
        valid_nodes = [
            MockWorkflowNode("A", "type1", {}, [], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("B", "type2", {}, ["A"], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("C", "type3", {}, ["B"], NodeStatus.PENDING, None, None, None)
        ]
        
        assert not validator.has_cycle(valid_nodes), "Valid DAG should not have cycles"
        
        # Test invalid DAG (with cycles)
        invalid_nodes = [
            MockWorkflowNode("A", "type1", {}, ["B"], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("B", "type2", {}, ["C"], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("C", "type3", {}, ["A"], NodeStatus.PENDING, None, None, None)
        ]
        
        assert validator.has_cycle(invalid_nodes), "Invalid DAG should have cycles"
    
    def test_dag_topological_sorting(self):
        """Test topological sorting of DAG nodes."""
        
        class TopologicalSorter:
            @staticmethod
            def sort_nodes(nodes: List[MockWorkflowNode]) -> List[str]:
                """Return topologically sorted node IDs."""
                # Build adjacency list and in-degree count
                adj_list = {}
                in_degree = {}
                
                for node in nodes:
                    adj_list[node.node_id] = node.dependencies
                    in_degree[node.node_id] = 0
                
                # Count in-degrees
                for node in nodes:
                    for dep in node.dependencies:
                        in_degree[node.node_id] += 1
                
                # Kahn's algorithm for topological sort
                queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
                result = []
                
                while queue:
                    current = queue.pop(0)
                    result.append(current)
                    
                    # Find nodes that depend on current
                    for node in nodes:
                        if current in node.dependencies:
                            in_degree[node.node_id] -= 1
                            if in_degree[node.node_id] == 0:
                                queue.append(node.node_id)
                
                return result
        
        sorter = TopologicalSorter()
        
        # Test complex DAG
        complex_nodes = [
            MockWorkflowNode("extract_req", "extraction", {}, [], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("parse_resume", "parsing", {}, [], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("analyze_skills", "analysis", {}, ["extract_req", "parse_resume"], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("analyze_experience", "analysis", {}, ["parse_resume"], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("synthesize_results", "synthesis", {}, ["analyze_skills", "analyze_experience"], NodeStatus.PENDING, None, None, None)
        ]
        
        sorted_order = sorter.sort_nodes(complex_nodes)
        
        # Validate topological order
        assert len(sorted_order) == 5
        
        # Dependencies should come before dependents
        extract_idx = sorted_order.index("extract_req")
        parse_idx = sorted_order.index("parse_resume")
        analyze_skills_idx = sorted_order.index("analyze_skills")
        
        assert extract_idx < analyze_skills_idx
        assert parse_idx < analyze_skills_idx
        
        # Both analyses should come before synthesis
        synthesize_idx = sorted_order.index("synthesize_results")
        assert analyze_skills_idx < synthesize_idx
        assert sorted_order.index("analyze_experience") < synthesize_idx


class TestDependencyResolution:
    """Test dependency resolution and node readiness."""
    
    def test_dependency_calculation(self):
        """Test calculation of node dependencies and readiness."""
        
        class DependencyResolver:
            def __init__(self, nodes: List[MockWorkflowNode]):
                self.nodes = {node.node_id: node for node in nodes}
                self.node_status = {node.node_id: node.status for node in nodes}
            
            def get_ready_nodes(self) -> List[str]:
                """Get nodes whose dependencies are satisfied."""
                ready_nodes = []
                
                for node_id, node in self.nodes.items():
                    if self.node_status[node_id] != NodeStatus.PENDING:
                        continue
                    
                    # Check if all dependencies are completed
                    dependencies_satisfied = True
                    for dep_id in node.dependencies:
                        if self.node_status.get(dep_id) != NodeStatus.COMPLETED:
                            dependencies_satisfied = False
                            break
                    
                    if dependencies_satisfied:
                        ready_nodes.append(node_id)
                
                return ready_nodes
            
            def update_node_status(self, node_id: str, status: NodeStatus):
                """Update status of a node."""
                self.node_status[node_id] = status
        
        # Create test workflow
        nodes = [
            MockWorkflowNode("A", "type1", {}, [], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("B", "type2", {}, [], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("C", "type3", {}, ["A", "B"], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("D", "type4", {}, ["C"], NodeStatus.PENDING, None, None, None)
        ]
        
        resolver = DependencyResolver(nodes)
        
        # Initially, only nodes with no dependencies should be ready
        ready_nodes = resolver.get_ready_nodes()
        assert set(ready_nodes) == {"A", "B"}
        
        # Complete node A
        resolver.update_node_status("A", NodeStatus.COMPLETED)
        ready_nodes = resolver.get_ready_nodes()
        assert set(ready_nodes) == {"B"}  # C still waiting for B
        
        # Complete node B
        resolver.update_node_status("B", NodeStatus.COMPLETED)
        ready_nodes = resolver.get_ready_nodes()
        assert ready_nodes == ["C"]  # C now ready
        
        # Complete node C
        resolver.update_node_status("C", NodeStatus.COMPLETED)
        ready_nodes = resolver.get_ready_nodes()
        assert ready_nodes == ["D"]  # D now ready
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        
        class CircularDependencyDetector:
            @staticmethod
            def find_cycles(nodes: List[MockWorkflowNode]) -> List[List[str]]:
                """Find all cycles in the dependency graph."""
                # Build adjacency list
                adj_list = {}
                for node in nodes:
                    adj_list[node.node_id] = node.dependencies
                
                cycles = []
                visited = set()
                rec_stack = set()
                path = []
                
                def dfs(node_id: str):
                    visited.add(node_id)
                    rec_stack.add(node_id)
                    path.append(node_id)
                    
                    for neighbor in adj_list.get(node_id, []):
                        if neighbor not in visited:
                            result = dfs(neighbor)
                            if result:
                                return result
                        elif neighbor in rec_stack:
                            # Found cycle
                            cycle_start = path.index(neighbor)
                            cycle = path[cycle_start:] + [neighbor]
                            cycles.append(cycle)
                            return cycle
                    
                    rec_stack.remove(node_id)
                    path.pop()
                    return None
                
                for node in nodes:
                    if node.node_id not in visited:
                        dfs(node.node_id)
                
                return cycles
        
        detector = CircularDependencyDetector()
        
        # Test graph with cycles
        nodes_with_cycles = [
            MockWorkflowNode("A", "type1", {}, ["B"], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("B", "type2", {}, ["C"], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("C", "type3", {}, ["A"], NodeStatus.PENDING, None, None, None),  # Creates cycle A->B->C->A
            MockWorkflowNode("D", "type4", {}, ["E"], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("E", "type5", {}, ["D"], NodeStatus.PENDING, None, None, None)   # Creates cycle D->E->D
        ]
        
        cycles = detector.find_cycles(nodes_with_cycles)
        
        # Validate cycle detection
        assert len(cycles) >= 2  # Should find both cycles
        
        # Check for specific cycles
        cycle_paths = [cycle[:-1] for cycle in cycles]  # Remove duplicate last element
        
        abc_cycle_found = any(set(cycle) == {"A", "B", "C"} for cycle in cycle_paths)
        de_cycle_found = any(set(cycle) == {"D", "E"} for cycle in cycle_paths)
        
        assert abc_cycle_found, "Should detect A->B->C->A cycle"
        assert de_cycle_found, "Should detect D->E->D cycle"
    
    def test_dependency_level_calculation(self):
        """Test calculation of dependency levels for parallel execution."""
        
        class DependencyLevelCalculator:
            def __init__(self, nodes: List[MockWorkflowNode]):
                self.nodes = {node.node_id: node for node in nodes}
                self.levels = {}
            
            def calculate_levels(self) -> Dict[str, int]:
                """Calculate dependency level for each node."""
                
                def get_level(node_id: str, memo: Dict[str, int]) -> int:
                    if node_id in memo:
                        return memo[node_id]
                    
                    node = self.nodes[node_id]
                    if not node.dependencies:
                        level = 0
                    else:
                        max_dep_level = max(get_level(dep, memo) for dep in node.dependencies)
                        level = max_dep_level + 1
                    
                    memo[node_id] = level
                    return level
                
                memo = {}
                for node_id in self.nodes:
                    self.levels[node_id] = get_level(node_id, memo)
                
                return self.levels
            
            def get_nodes_by_level(self) -> Dict[int, List[str]]:
                """Group nodes by their dependency level."""
                level_groups = {}
                for node_id, level in self.levels.items():
                    if level not in level_groups:
                        level_groups[level] = []
                    level_groups[level].append(node_id)
                
                return level_groups
        
        # Create complex dependency structure
        nodes = [
            MockWorkflowNode("A", "type1", {}, [], NodeStatus.PENDING, None, None, None),      # Level 0
            MockWorkflowNode("B", "type2", {}, [], NodeStatus.PENDING, None, None, None),      # Level 0
            MockWorkflowNode("C", "type3", {}, ["A"], NodeStatus.PENDING, None, None, None),   # Level 1
            MockWorkflowNode("D", "type4", {}, ["A", "B"], NodeStatus.PENDING, None, None, None), # Level 1
            MockWorkflowNode("E", "type5", {}, ["C", "D"], NodeStatus.PENDING, None, None, None), # Level 2
            MockWorkflowNode("F", "type6", {}, ["E"], NodeStatus.PENDING, None, None, None)    # Level 3
        ]
        
        calculator = DependencyLevelCalculator(nodes)
        levels = calculator.calculate_levels()
        level_groups = calculator.get_nodes_by_level()
        
        # Validate level calculations
        assert levels["A"] == 0
        assert levels["B"] == 0
        assert levels["C"] == 1
        assert levels["D"] == 1
        assert levels["E"] == 2
        assert levels["F"] == 3
        
        # Validate level grouping
        assert set(level_groups[0]) == {"A", "B"}
        assert set(level_groups[1]) == {"C", "D"}
        assert level_groups[2] == ["E"]
        assert level_groups[3] == ["F"]


class TestDAGExecution:
    """Test DAG execution strategies and node execution."""
    
    @pytest.mark.asyncio
    async def test_sequential_execution(self):
        """Test sequential execution of DAG nodes."""
        
        class SequentialDAGExecutor:
            def __init__(self, dag: MockWorkflowDAG):
                self.dag = dag
                self.execution_log = []
            
            async def execute_node(self, node: MockWorkflowNode) -> Dict[str, Any]:
                """Execute individual node."""
                start_time = time.time()
                
                # Simulate node execution
                await asyncio.sleep(0.01)
                
                result = {
                    "node_id": node.node_id,
                    "result": f"Executed {node.node_type}",
                    "execution_time": time.time() - start_time
                }
                
                self.execution_log.append({
                    "node_id": node.node_id,
                    "status": "completed",
                    "timestamp": time.time()
                })
                
                return result
            
            async def execute_sequential(self) -> List[Dict[str, Any]]:
                """Execute all nodes sequentially in topological order."""
                results = []
                
                for node_id in self.dag.execution_order:
                    node = next(n for n in self.dag.nodes if n.node_id == node_id)
                    result = await self.execute_node(node)
                    results.append(result)
                
                return results
        
        # Create simple DAG
        nodes = [
            MockWorkflowNode("node1", "type1", {}, [], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("node2", "type2", {}, ["node1"], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("node3", "type3", {}, ["node2"], NodeStatus.PENDING, None, None, None)
        ]
        
        dag = MockWorkflowDAG(
            "seq_dag",
            nodes,
            [("node1", "node2"), ("node2", "node3")],
            ["node1", "node2", "node3"],
            ["node1", "node2", "node3"]
        )
        
        executor = SequentialDAGExecutor(dag)
        results = await executor.execute_sequential()
        
        # Validate sequential execution
        assert len(results) == 3
        assert results[0]["node_id"] == "node1"
        assert results[1]["node_id"] == "node2"
        assert results[2]["node_id"] == "node3"
        
        # Validate execution order in log
        execution_order = [log["node_id"] for log in executor.execution_log]
        assert execution_order == ["node1", "node2", "node3"]
    
    @pytest.mark.asyncio
    async def test_parallel_execution_by_level(self):
        """Test parallel execution of nodes within dependency levels."""
        
        class ParallelDAGExecutor:
            def __init__(self, dag: MockWorkflowDAG):
                self.dag = dag
                self.execution_log = []
            
            async def execute_node(self, node: MockWorkflowNode) -> Dict[str, Any]:
                """Execute individual node."""
                start_time = time.time()
                
                # Simulate node execution
                await asyncio.sleep(0.01)
                
                result = {
                    "node_id": node.node_id,
                    "result": f"Executed {node.node_type}",
                    "execution_time": time.time() - start_time
                }
                
                self.execution_log.append({
                    "node_id": node.node_id,
                    "status": "completed",
                    "timestamp": time.time()
                })
                
                return result
            
            def get_dependency_levels(self) -> Dict[int, List[str]]:
                """Calculate dependency levels for parallel execution."""
                levels = {}
                
                for node in self.dag.nodes:
                    level = self._calculate_node_level(node.node_id)
                    if level not in levels:
                        levels[level] = []
                    levels[level].append(node.node_id)
                
                return levels
            
            def _calculate_node_level(self, node_id: str) -> int:
                """Calculate dependency level for a specific node."""
                node = next(n for n in self.dag.nodes if n.node_id == node_id)
                
                if not node.dependencies:
                    return 0
                
                max_dep_level = 0
                for dep_id in node.dependencies:
                    dep_level = self._calculate_node_level(dep_id)
                    max_dep_level = max(max_dep_level, dep_level)
                
                return max_dep_level + 1
            
            async def execute_parallel_by_level(self) -> List[Dict[str, Any]]:
                """Execute nodes in parallel within dependency levels."""
                levels = self.get_dependency_levels()
                all_results = []
                
                for level in sorted(levels.keys()):
                    node_ids = levels[level]
                    
                    # Execute nodes at this level in parallel
                    tasks = []
                    for node_id in node_ids:
                        node = next(n for n in self.dag.nodes if n.node_id == node_id)
                        task = self.execute_node(node)
                        tasks.append(task)
                    
                    level_results = await asyncio.gather(*tasks)
                    all_results.extend(level_results)
                
                return all_results
        
        # Create DAG with parallelizable nodes
        nodes = [
            MockWorkflowNode("A", "type1", {}, [], NodeStatus.PENDING, None, None, None),      # Level 0
            MockWorkflowNode("B", "type2", {}, [], NodeStatus.PENDING, None, None, None),      # Level 0
            MockWorkflowNode("C", "type3", {}, ["A"], NodeStatus.PENDING, None, None, None),   # Level 1
            MockWorkflowNode("D", "type4", {}, ["B"], NodeStatus.PENDING, None, None, None),   # Level 1
            MockWorkflowNode("E", "type5", {}, ["C", "D"], NodeStatus.PENDING, None, None, None) # Level 2
        ]
        
        dag = MockWorkflowDAG(
            "parallel_dag",
            nodes,
            [("A", "C"), ("B", "D"), ("C", "E"), ("D", "E")],
            ["A", "B", "C", "D", "E"],
            ["A", "C", "E"]
        )
        
        executor = ParallelDAGExecutor(dag)
        results = await executor.execute_parallel_by_level()
        
        # Validate parallel execution
        assert len(results) == 5
        
        # Validate dependency levels were respected
        execution_times = {result["node_id"]: result["execution_time"] for result in results}
        
        # Nodes A and B should start around the same time (level 0)
        # Nodes C and D should start after A and B complete (level 1)
        # Node E should start after C and D complete (level 2)
        
        # Check that we have proper parallel execution by verifying execution log
        level_0_nodes = ["A", "B"]
        level_1_nodes = ["C", "D"]
        level_2_nodes = ["E"]
        
        # Extract execution order from log
        execution_order = [log["node_id"] for log in executor.execution_log]
        
        # Validate that level 0 nodes come before level 1 nodes
        level_0_indices = [execution_order.index(node) for node in level_0_nodes]
        level_1_indices = [execution_order.index(node) for node in level_1_nodes]
        level_2_index = execution_order.index("E")
        
        assert all(idx < min(level_1_indices) for idx in level_0_indices)
        assert all(idx < level_2_index for idx in level_1_indices)
    
    @pytest.mark.asyncio
    async def test_error_handling_in_execution(self):
        """Test error handling during DAG execution."""
        
        class ErrorHandlingDAGExecutor:
            def __init__(self, dag: MockWorkflowDAG):
                self.dag = dag
                self.execution_log = []
                self.failure_simulation = {}
            
            def simulate_failure(self, node_id: str, error_message: str):
                """Configure a node to fail."""
                self.failure_simulation[node_id] = error_message
            
            async def execute_node(self, node: MockWorkflowNode) -> Dict[str, Any]:
                """Execute individual node with potential failure."""
                start_time = time.time()
                
                # Check if this node should fail
                if node.node_id in self.failure_simulation:
                    error = self.failure_simulation[node.node_id]
                    self.execution_log.append({
                        "node_id": node.node_id,
                        "status": "failed",
                        "error": error,
                        "timestamp": time.time()
                    })
                    raise Exception(error)
                
                # Simulate successful execution
                await asyncio.sleep(0.01)
                
                result = {
                    "node_id": node.node_id,
                    "result": f"Executed {node.node_type}",
                    "execution_time": time.time() - start_time
                }
                
                self.execution_log.append({
                    "node_id": node.node_id,
                    "status": "completed",
                    "timestamp": time.time()
                })
                
                return result
            
            async def execute_with_error_handling(self, continue_on_error: bool = True) -> Dict[str, Any]:
                """Execute DAG with error handling."""
                results = {}
                failed_nodes = []
                
                for node_id in self.dag.execution_order:
                    try:
                        node = next(n for n in self.dag.nodes if n.node_id == node_id)
                        result = await self.execute_node(node)
                        results[node_id] = result
                        
                    except Exception as e:
                        failed_nodes.append({
                            "node_id": node_id,
                            "error": str(e)
                        })
                        
                        if not continue_on_error:
                            break
                
                return {
                    "results": results,
                    "failed_nodes": failed_nodes,
                    "total_nodes": len(self.dag.nodes),
                    "successful_nodes": len(results),
                    "failed_count": len(failed_nodes)
                }
        
        # Create DAG for error testing
        nodes = [
            MockWorkflowNode("A", "type1", {}, [], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("B", "type2", {}, ["A"], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("C", "type3", {}, ["B"], NodeStatus.PENDING, None, None, None),
            MockWorkflowNode("D", "type4", {}, ["A"], NodeStatus.PENDING, None, None, None)
        ]
        
        dag = MockWorkflowDAG(
            "error_dag",
            nodes,
            [("A", "B"), ("B", "C"), ("A", "D")],
            ["A", "B", "C", "D"],
            ["A", "B", "C"]
        )
        
        executor = ErrorHandlingDAGExecutor(dag)
        
        # Test with failure in middle node
        executor.simulate_failure("B", "Simulated node failure")
        
        # Test continue on error
        result = await executor.execute_with_error_handling(continue_on_error=True)
        
        assert result["successful_nodes"] == 2  # A and D should succeed
        assert result["failed_count"] == 1      # B should fail
        assert result["total_nodes"] == 4
        
        # Node C should not be executed due to B's failure
        assert "C" not in result["results"]
        assert len(result["failed_nodes"]) == 1
        assert result["failed_nodes"][0]["node_id"] == "B"
        
        # Test stop on error
        executor.execution_log.clear()  # Clear previous execution log
        result = await executor.execute_with_error_handling(continue_on_error=False)
        
        assert result["successful_nodes"] == 1  # Only A should succeed
        assert result["failed_count"] == 1      # B should fail
        assert len(result["results"]) == 1     # Only A in results
