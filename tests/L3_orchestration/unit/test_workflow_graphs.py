"""
L3 Orchestration Layer Unit Tests

Tests for workflow graphs, DAG execution, and agent coordination without planning or execution logic.
Focuses on graph structure, node ordering, and orchestration control flow.
"""

import pytest
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock, patch

# Mark all tests in this module as L3 orchestration unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l3, pytest.mark.orchestration]


class NodeStatus(Enum):
    """Node execution status for workflow graphs."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class MockWorkflowNode:
    """Mock workflow node for testing L3 orchestration."""
    node_id: str
    node_type: str  # "agent", "tool", "condition", "merge"
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: NodeStatus = NodeStatus.PENDING


@dataclass(frozen=True)
class MockWorkflowGraph:
    """Mock workflow graph for L3 testing."""
    graph_id: str
    nodes: List[MockWorkflowNode]
    metadata: Dict[str, Any] = field(default_factory=dict)


class TestWorkflowGraphStructure:
    """Test L3 workflow graph structure and validation."""
    
    def test_valid_graph_construction(self):
        """Test construction of valid workflow graphs."""
        nodes = [
            MockWorkflowNode("start", "agent", []),
            MockWorkflowNode("analyze", "agent", ["start"]),
            MockWorkflowNode("decision", "condition", ["analyze"]),
            MockWorkflowNode("process_a", "agent", ["decision"]),
            MockWorkflowNode("process_b", "agent", ["decision"]),
            MockWorkflowNode("merge", "merge", ["process_a", "process_b"]),
            MockWorkflowNode("end", "agent", ["merge"])
        ]
        
        graph = MockWorkflowGraph("test_graph", nodes)
        
        assert len(graph.nodes) == 7
        assert graph.nodes[0].node_id == "start"
        assert len(graph.nodes[0].dependencies) == 0
        assert len(graph.nodes[-1].dependencies) == 1
    
    def test_dependency_validation(self):
        """Test validation of node dependencies in workflow graphs."""
        nodes = [
            MockWorkflowNode("node_1", "agent", []),
            MockWorkflowNode("node_2", "agent", ["node_1"]),
            MockWorkflowNode("node_3", "agent", ["node_1", "node_2"])
        ]
        
        # Build dependency map
        dependency_map = {node.node_id: node.dependencies for node in nodes}
        
        # Validate all dependencies exist
        all_node_ids = set(node.node_id for node in nodes)
        invalid_deps = []
        
        for node_id, deps in dependency_map.items():
            for dep in deps:
                if dep not in all_node_ids:
                    invalid_deps.append((node_id, dep))
        
        assert len(invalid_deps) == 0
        assert dependency_map["node_3"] == ["node_1", "node_2"]
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies in workflow graphs."""
        nodes_with_circular = [
            MockWorkflowNode("a", "agent", ["c"]),
            MockWorkflowNode("b", "agent", ["a"]),
            MockWorkflowNode("c", "agent", ["b"])  # Creates circular dependency
        ]
        
        # Detect circular dependencies using DFS
        def has_cycle(node_id: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            node = next((n for n in nodes_with_circular if n.node_id == node_id), None)
            if node:
                for dep in node.dependencies:
                    if dep not in visited:
                        if has_cycle(dep, visited, rec_stack):
                            return True
                    elif dep in rec_stack:
                        return True
            
            rec_stack.remove(node_id)
            return False
        
        visited = set()
        rec_stack = set()
        has_circular = any(has_cycle(node.node_id, visited, rec_stack) for node in nodes_with_circular)
        
        assert has_circular is True


class TestNodeExecutionOrdering:
    """Test L3 node execution ordering and topological sorting."""
    
    def test_topological_sort(self):
        """Test topological sorting of workflow nodes."""
        nodes = [
            MockWorkflowNode("extract_jd", "agent", []),
            MockWorkflowNode("parse_resume", "agent", []),
            MockWorkflowNode("analyze_requirements", "agent", ["extract_jd"]),
            MockWorkflowNode("analyze_skills", "agent", ["parse_resume"]),
            MockWorkflowNode("compare_match", "agent", ["analyze_requirements", "analyze_skills"]),
            MockWorkflowNode("generate_report", "agent", ["compare_match"])
        ]
        
        # Perform topological sort
        in_degree = {node.node_id: 0 for node in nodes}
        dependency_map = {node.node_id: node.dependencies for node in nodes}
        
        # Calculate in-degrees
        for node_id, deps in dependency_map.items():
            for dep in deps:
                in_degree[node_id] += 1
        
        # Kahn's algorithm for topological sort
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Find nodes that depend on current
            for node_id, deps in dependency_map.items():
                if current in deps:
                    in_degree[node_id] -= 1
                    if in_degree[node_id] == 0:
                        queue.append(node_id)
        
        expected_order = ["extract_jd", "parse_resume", "analyze_requirements", "analyze_skills", "compare_match", "generate_report"]
        assert result == expected_order
    
    def test_parallel_execution_identification(self):
        """Test identification of nodes that can execute in parallel."""
        nodes = [
            MockWorkflowNode("task_a", "agent", []),
            MockWorkflowNode("task_b", "agent", []),
            MockWorkflowNode("task_c", "agent", ["task_a"]),
            MockWorkflowNode("task_d", "agent", ["task_b"]),
            MockWorkflowNode("task_e", "agent", ["task_c", "task_d"])
        ]
        
        # Group nodes by dependency level
        dependency_levels = {}
        for node in nodes:
            level = len(node.dependencies)
            if level not in dependency_levels:
                dependency_levels[level] = []
            dependency_levels[level].append(node.node_id)
        
        assert len(dependency_levels[0]) == 2  # Two tasks can run in parallel
        assert "task_a" in dependency_levels[0]
        assert "task_b" in dependency_levels[0]
        assert len(dependency_levels[1]) == 2  # Next level also has parallel tasks
    
    def test_critical_path_identification(self):
        """Test identification of critical path in workflow graphs."""
        nodes = [
            MockWorkflowNode("start", "agent", [], duration=1),
            MockWorkflowNode("branch_a", "agent", ["start"], duration=3),
            MockWorkflowNode("branch_b", "agent", ["start"], duration=2),
            MockWorkflowNode("merge", "agent", ["branch_a", "branch_b"], duration=1),
            MockWorkflowNode("end", "agent", ["merge"], duration=1)
        ]
        
        # Add duration attribute for critical path calculation
        nodes_with_duration = []
        for node in nodes:
            duration = getattr(node, 'duration', 1)
            nodes_with_duration.append({**node.__dict__, 'duration': duration})
        
        # Calculate critical path (simplified)
        path_times = {
            "path_a": 1 + 3 + 1 + 1,  # start -> branch_a -> merge -> end
            "path_b": 1 + 2 + 1 + 1   # start -> branch_b -> merge -> end
        }
        
        critical_path = max(path_times, key=path_times.get)
        assert critical_path == "path_a"
        assert path_times["path_a"] == 6


class TestConditionalBranching:
    """Test L3 conditional branching and decision nodes."""
    
    def test_condition_node_evaluation(self):
        """Test evaluation of condition nodes in workflows."""
        condition_node = MockWorkflowNode(
            "check_experience",
            "condition",
            ["analyze_resume"],
            {"condition": "experience_years >= 5", "true_branch": "senior_path", "false_branch": "junior_path"}
        )
        
        # Mock condition evaluation
        context = {"experience_years": 7}
        condition_result = eval(condition_node.parameters["condition"], {}, context)
        
        if condition_result:
            next_node = condition_node.parameters["true_branch"]
        else:
            next_node = condition_node.parameters["false_branch"]
        
        assert condition_result is True
        assert next_node == "senior_path"
    
    def test_multi_branch_condition(self):
        """Test multi-way conditional branching."""
        multi_condition_node = MockWorkflowNode(
            "skill_level_check",
            "condition",
            ["assess_skills"],
            {
                "conditions": [
                    {"condition": "skill_score >= 90", "branch": "expert_path"},
                    {"condition": "skill_score >= 70", "branch": "advanced_path"},
                    {"condition": "skill_score >= 50", "branch": "intermediate_path"}
                ],
                "default_branch": "beginner_path"
            }
        )
        
        # Test different skill scores
        test_cases = [
            (95, "expert_path"),
            (75, "advanced_path"),
            (60, "intermediate_path"),
            (30, "beginner_path")
        ]
        
        for score, expected_branch in test_cases:
            context = {"skill_score": score}
            
            # Find matching condition
            selected_branch = multi_condition_node.parameters["default_branch"]
            for condition_spec in multi_condition_node.parameters["conditions"]:
                if eval(condition_spec["condition"], {}, context):
                    selected_branch = condition_spec["branch"]
                    break
            
            assert selected_branch == expected_branch
    
    def test_branch_pruning(self):
        """Test pruning of unreachable branches in workflows."""
        workflow_nodes = [
            MockWorkflowNode("start", "agent", []),
            MockWorkflowNode("decision", "condition", ["start"]),
            MockWorkflowNode("branch_a", "agent", ["decision"]),
            MockWorkflowNode("branch_b", "agent", ["decision"]),
            MockWorkflowNode("merge", "agent", ["branch_a", "branch_b"])
        ]
        
        # Mock branch selection based on condition
        condition_result = True  # Simulate condition evaluating to True
        selected_branch = "branch_a" if condition_result else "branch_b"
        
        # Prune unused branches
        pruned_nodes = []
        for node in workflow_nodes:
            if node.node_type == "condition":
                pruned_nodes.append(node)
            elif node.node_id == selected_branch or node.node_id in ["start", "merge"]:
                pruned_nodes.append(node)
        
        assert len(pruned_nodes) == 4  # start, decision, selected branch, merge
        assert any(node.node_id == "branch_a" for node in pruned_nodes)
        assert not any(node.node_id == "branch_b" for node in pruned_nodes)


class TestAgentCoordination:
    """Test L3 multi-agent coordination and communication."""
    
    def test_agent_handoff_mechanisms(self):
        """Test handoff mechanisms between agents."""
        agent_workflow = [
            MockWorkflowNode("extractor_agent", "agent", [], {"output_context": "extracted_data"}),
            MockWorkflowNode("analyzer_agent", "agent", ["extractor_agent"], {"input_context": "extracted_data"}),
            MockWorkflowNode("generator_agent", "agent", ["analyzer_agent"], {"input_context": "analysis_results"})
        ]
        
        # Mock context passing between agents
        context_flow = {}
        for i, node in enumerate(agent_workflow):
            if i > 0:
                prev_node = agent_workflow[i-1]
                input_context = node.parameters.get("input_context")
                output_context = prev_node.parameters.get("output_context")
                
                context_flow[node.node_id] = {
                    "receives_from": prev_node.node_id,
                    "input_type": input_context,
                    "output_type": output_context
                }
        
        assert context_flow["analyzer_agent"]["receives_from"] == "extractor_agent"
        assert context_flow["generator_agent"]["input_type"] == "analysis_results"
    
    def test_parallel_agent_execution(self):
        """Test coordination of parallel agent execution."""
        parallel_agents = [
            MockWorkflowNode("skill_analyzer", "agent", []),
            MockWorkflowNode("experience_analyzer", "agent", []),
            MockWorkflowNode("education_analyzer", "agent", []),
            MockWorkflowNode("result_synthesizer", "agent", ["skill_analyzer", "experience_analyzer", "education_analyzer"])
        ]
        
        # Identify parallel agents (no dependencies)
        parallel_agents = [node for node in parallel_agents if len(node.dependencies) == 0 and node.node_type == "agent"]
        
        assert len(parallel_agents) == 3
        parallel_agent_ids = [agent.node_id for agent in parallel_agents]
        assert "skill_analyzer" in parallel_agent_ids
        assert "experience_analyzer" in parallel_agent_ids
        assert "education_analyzer" in parallel_agent_ids
    
    def test_agent_resource_sharing(self):
        """Test resource sharing between coordinated agents."""
        shared_resources = {
            "knowledge_base": {"access_type": "read_write", "agents": ["analyzer", "validator"]},
            "temp_storage": {"access_type": "read_write", "agents": ["processor", "formatter"]},
            "config_store": {"access_type": "read_only", "agents": ["analyzer", "processor", "validator"]}
        }
        
        # Check for resource conflicts
        resource_conflicts = []
        for resource_name, resource_info in shared_resources.items():
            if len(resource_info["agents"]) > 1 and resource_info["access_type"] == "read_write":
                resource_conflicts.append(resource_name)
        
        assert len(resource_conflicts) == 2  # knowledge_base and temp_storage have potential conflicts
        assert "config_store" not in resource_conflicts  # read_only resources don't conflict


class TestWorkflowStateManagement:
    """Test L3 workflow state management and tracking."""
    
    def test_node_status_tracking(self):
        """Test tracking of node execution status."""
        nodes = [
            MockWorkflowNode("node_1", "agent", [], status=NodeStatus.COMPLETED),
            MockWorkflowNode("node_2", "agent", ["node_1"], status=NodeStatus.RUNNING),
            MockWorkflowNode("node_3", "agent", ["node_1"], status=NodeStatus.READY),
            MockWorkflowNode("node_4", "agent", ["node_2", "node_3"], status=NodeStatus.PENDING)
        ]
        
        # Count nodes by status
        status_counts = {}
        for status in NodeStatus:
            status_counts[status.value] = sum(1 for node in nodes if node.status == status)
        
        assert status_counts["completed"] == 1
        assert status_counts["running"] == 1
        assert status_counts["ready"] == 1
        assert status_counts["pending"] == 1
    
    def test_workflow_progress_calculation(self):
        """Test calculation of workflow execution progress."""
        nodes = [
            MockWorkflowNode("n1", "agent", [], status=NodeStatus.COMPLETED),
            MockWorkflowNode("n2", "agent", [], status=NodeStatus.COMPLETED),
            MockWorkflowNode("n3", "agent", [], status=NodeStatus.RUNNING),
            MockWorkflowNode("n4", "agent", [], status=NodeStatus.PENDING),
            MockWorkflowNode("n5", "agent", [], status=NodeStatus.PENDING)
        ]
        
        total_nodes = len(nodes)
        completed_nodes = sum(1 for node in nodes if node.status == NodeStatus.COMPLETED)
        running_nodes = sum(1 for node in nodes if node.status == NodeStatus.RUNNING)
        
        # Calculate progress (completed + 0.5 * running) / total
        progress = (completed_nodes + 0.5 * running_nodes) / total_nodes
        
        assert progress == 0.5  # 2 completed + 0.5 running / 5 total = 2.5/5 = 0.5
    
    def test_checkpoint_creation_and_recovery(self):
        """Test creation of workflow checkpoints and recovery."""
        workflow_state = {
            "workflow_id": "workflow_123",
            "completed_nodes": ["node_1", "node_2"],
            "running_nodes": ["node_3"],
            "node_outputs": {
                "node_1": {"result": "success", "data": "processed_data_1"},
                "node_2": {"result": "success", "data": "processed_data_2"}
            },
            "metadata": {"checkpoint_time": "2025-01-25T12:00:00Z"}
        }
        
        # Mock checkpoint creation
        checkpoint = {
            "state": workflow_state,
            "recovery_instructions": {
                "resume_from": "node_3",
                "restore_context": workflow_state["node_outputs"],
                "skip_completed": workflow_state["completed_nodes"]
            }
        }
        
        assert checkpoint["recovery_instructions"]["resume_from"] == "node_3"
        assert len(checkpoint["recovery_instructions"]["skip_completed"]) == 2
        assert checkpoint["state"]["metadata"]["checkpoint_time"] is not None
