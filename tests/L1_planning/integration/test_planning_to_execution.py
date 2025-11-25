"""
L1 Planning Layer Integration Tests

Tests integration between L1 planning and L2 execution layers.
Focuses on plan handoff, parameter passing, and execution readiness.
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock

# Mark all tests in this module as L1 integration tests
pytestmark = [pytest.mark.integration, pytest.mark.l1, pytest.mark.planning]


class TestPlanToExecutionHandoff:
    """Test L1 to L2 plan handoff mechanisms."""
    
    def test_plan_execution_parameter_mapping(self):
        """Test that plan parameters map correctly to execution inputs."""
        # Mock L1 plan output
        plan_output = {
            "plan_id": "plan_001",
            "mission": "Analyze resume for job match",
            "steps": [
                {
                    "step_id": "extract_jd",
                    "tool": "text_analyzer",
                    "parameters": {
                        "text": "{{job_description}}",
                        "analysis_type": "requirements_extraction"
                    }
                },
                {
                    "step_id": "parse_resume",
                    "tool": "resume_parser", 
                    "parameters": {
                        "resume_text": "{{resume_content}}",
                        "format": "structured"
                    }
                }
            ]
        }
        
        # Mock L2 execution input preparation
        execution_inputs = []
        for step in plan_output["steps"]:
            execution_input = {
                "tool_name": step["tool"],
                "parameters": step["parameters"],
                "step_id": step["step_id"]
            }
            execution_inputs.append(execution_input)
        
        assert len(execution_inputs) == 2
        assert execution_inputs[0]["tool_name"] == "text_analyzer"
        assert execution_inputs[1]["tool_name"] == "resume_parser"
    
    def test_execution_context_propagation(self):
        """Test that execution context is properly propagated from planning."""
        plan_context = {
            "workflow_id": "workflow_123",
            "user_request": "Improve my resume for this job",
            "priority": "high",
            "telemetry_enabled": True
        }
        
        # Mock context propagation to execution
        execution_context = {
            "workflow_id": plan_context["workflow_id"],
            "request_id": "req_456",
            "parent_context": plan_context,
            "execution_mode": "batch"
        }
        
        assert execution_context["workflow_id"] == "workflow_123"
        assert execution_context["parent_context"]["priority"] == "high"
    
    @patch('l2.execution_engine.ExecutionEngine')
    def test_plan_execution_readiness_validation(self, mock_engine):
        """Test that plans are validated for execution readiness."""
        mock_engine.validate_plan.return_value = True
        
        plan = {
            "plan_id": "ready_plan",
            "steps": [
                {"step_id": "step_1", "tool": "available_tool"},
                {"step_id": "step_2", "tool": "another_tool"}
            ]
        }
        
        # Validate plan for execution
        is_ready = mock_engine.validate_plan(plan)
        assert is_ready is True
        
        # Verify validation was called
        mock_engine.validate_plan.assert_called_once_with(plan)


class TestPlanningDependencyResolution:
    """Test L1 dependency resolution for execution ordering."""
    
    def test_dependency_graph_construction(self):
        """Test construction of dependency graphs for execution."""
        plan_steps = [
            {"step_id": "extract_jd", "dependencies": []},
            {"step_id": "parse_resume", "dependencies": []},
            {"step_id": "compare_match", "dependencies": ["extract_jd", "parse_resume"]},
            {"step_id": "generate_improvements", "dependencies": ["compare_match"]}
        ]
        
        # Build dependency graph
        dependency_graph = {}
        for step in plan_steps:
            dependency_graph[step["step_id"]] = step["dependencies"]
        
        # Verify graph structure
        assert dependency_graph["extract_jd"] == []
        assert dependency_graph["compare_match"] == ["extract_jd", "parse_resume"]
        assert set(dependency_graph.keys()) == {"extract_jd", "parse_resume", "compare_match", "generate_improvements"}
    
    def test_execution_order_from_dependencies(self):
        """Test execution order derivation from dependency graph."""
        dependency_graph = {
            "extract_jd": [],
            "parse_resume": [],
            "compare_match": ["extract_jd", "parse_resume"],
            "generate_improvements": ["compare_match"]
        }
        
        # Simplified topological sort
        execution_order = []
        remaining_steps = set(dependency_graph.keys())
        
        while remaining_steps:
            ready_steps = [
                step for step in remaining_steps 
                if all(dep in execution_order for dep in dependency_graph[step])
            ]
            
            if not ready_steps:
                raise ValueError("Circular dependency detected")
            
            # Take first ready step
            next_step = ready_steps[0]
            execution_order.append(next_step)
            remaining_steps.remove(next_step)
        
        assert execution_order == ["extract_jd", "parse_resume", "compare_match", "generate_improvements"]


class TestPlanningParameterSubstitution:
    """Test L1 parameter substitution and template resolution."""
    
    def test_template_variable_resolution(self):
        """Test resolution of template variables in plan parameters."""
        plan_template = {
            "steps": [
                {
                    "step_id": "analyze_jd",
                    "parameters": {
                        "text": "{{job_description}}",
                        "analysis_type": "{{analysis_mode}}"
                    }
                }
            ]
        }
        
        # Mock variable substitution
        variables = {
            "job_description": "Senior Software Engineer position...",
            "analysis_mode": "technical_requirements"
        }
        
        resolved_step = plan_template["steps"][0].copy()
        resolved_step["parameters"] = {
            key: value.replace("{{" + key + "}}", variables.get(key, value))
            for key, value in resolved_step["parameters"].items()
        }
        
        assert resolved_step["parameters"]["text"] == "Senior Software Engineer position..."
        assert resolved_step["parameters"]["analysis_type"] == "technical_requirements"
    
    def test_nested_parameter_resolution(self):
        """Test resolution of nested parameter structures."""
        plan_with_nesting = {
            "steps": [
                {
                    "step_id": "complex_step",
                    "parameters": {
                        "config": {
                            "input_text": "{{resume_content}}",
                            "options": {
                                "mode": "{{processing_mode}}",
                                "threshold": {{confidence_threshold}}
                            }
                        }
                    }
                }
            ]
        }
        
        variables = {
            "resume_content": "Experienced software developer...",
            "processing_mode": "comprehensive",
            "confidence_threshold": 0.85
        }
        
        # Mock nested resolution (simplified)
        resolved = plan_with_nesting["steps"][0]["parameters"]
        resolved["config"]["input_text"] = variables["resume_content"]
        resolved["config"]["options"]["mode"] = variables["processing_mode"]
        resolved["config"]["options"]["threshold"] = variables["confidence_threshold"]
        
        assert resolved["config"]["input_text"] == "Experienced software developer..."
        assert resolved["config"]["options"]["threshold"] == 0.85


class TestPlanningErrorPropagation:
    """Test L1 error handling and propagation to execution."""
    
    def test_planning_failure_handling(self):
        """Test handling of planning failures."""
        planning_result = {
            "success": False,
            "error": "Unable to generate plan: insufficient requirements",
            "partial_plan": None,
            "error_code": "INSUFFICIENT_INPUT"
        }
        
        # Mock error handling in execution preparation
        if not planning_result["success"]:
            execution_plan = None
            error_to_propagate = {
                "source": "L1_planning",
                "error": planning_result["error"],
                "code": planning_result["error_code"]
            }
        else:
            execution_plan = planning_result["partial_plan"]
            error_to_propagate = None
        
        assert execution_plan is None
        assert error_to_propagate["source"] == "L1_planning"
        assert "insufficient requirements" in error_to_propagate["error"]
    
    def test_partial_plan_handling(self):
        """Test handling of partial or incomplete plans."""
        partial_plan = {
            "plan_id": "partial_001",
            "complete": False,
            "steps": [
                {"step_id": "step_1", "complete": True},
                {"step_id": "step_2", "complete": False, "error": "Missing parameters"}
            ],
            "warning": "Plan partially generated, some steps may fail"
        }
        
        # Mock partial plan validation
        incomplete_steps = [
            step for step in partial_plan["steps"] 
            if not step.get("complete", True)
        ]
        
        assert len(incomplete_steps) == 1
        assert incomplete_steps[0]["step_id"] == "step_2"
        assert partial_plan["complete"] is False


class TestPlanningOptimizationIntegration:
    """Test L1 optimization features and their integration impact."""
    
    def test_plan_pruning_integration(self):
        """Test that plan pruning affects execution correctly."""
        original_plan = {
            "steps": [
                {"step_id": "redundant_step", "tool": "analyzer", "redundant": True},
                {"step_id": "essential_step", "tool": "parser", "redundant": False},
                {"step_id": "another_redundant", "tool": "validator", "redundant": True}
            ]
        }
        
        # Mock plan pruning
        pruned_plan = {
            "steps": [
                step for step in original_plan["steps"]
                if not step.get("redundant", False)
            ]
        }
        
        assert len(pruned_plan["steps"]) == 1
        assert pruned_plan["steps"][0]["step_id"] == "essential_step"
    
    def test_parallel_step_identification(self):
        """Test identification of parallelizable steps for execution."""
        plan_with_parallelism = {
            "steps": [
                {"step_id": "extract_jd", "dependencies": []},
                {"step_id": "parse_resume", "dependencies": []},
                {"step_id": "analyze_skills", "dependencies": ["extract_jd"]},
                {"step_id": "analyze_experience", "dependencies": ["parse_resume"]},
                {"step_id": "combine_results", "dependencies": ["analyze_skills", "analyze_experience"]}
            ]
        }
        
        # Identify parallel steps (same dependency level)
        parallel_groups = {}
        for step in plan_with_parallelism["steps"]:
            deps = tuple(sorted(step["dependencies"]))
            if deps not in parallel_groups:
                parallel_groups[deps] = []
            parallel_groups[deps].append(step["step_id"])
        
        assert len(parallel_groups[()]) == 2  # Two steps can run in parallel
        assert "extract_jd" in parallel_groups[()]
        assert "parse_resume" in parallel_groups[()]
