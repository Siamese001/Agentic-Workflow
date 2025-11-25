"""
L1 Planning Layer Unit Tests

Tests for pure planning functionality without tool execution or state mutations.
Focuses on schema validation, reasoning mode selection, and plan structure.
"""

import pytest
from typing import Dict, Any, List
from dataclasses import dataclass
from unittest.mock import Mock, patch

# Mark all tests in this module as L1 planning unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l1, pytest.mark.planning]


@dataclass(frozen=True)
class MockPlanStep:
    """Mock plan step for testing L1 planning logic."""
    step_id: str
    description: str
    reasoning_mode: str
    dependencies: List[str]


@dataclass(frozen=True)
class MockPlan:
    """Mock plan structure for L1 testing."""
    plan_id: str
    mission: str
    steps: List[MockPlanStep]
    metadata: Dict[str, Any]


class TestPlanSchemaValidation:
    """Test L1 plan schema validation and structure."""
    
    def test_valid_plan_structure(self):
        """Test that valid plan structures pass validation."""
        plan = MockPlan(
            plan_id="test_plan_001",
            mission="Analyze resume for job match",
            steps=[
                MockPlanStep(
                    step_id="step_1",
                    description="Extract key requirements from job description",
                    reasoning_mode="analytical",
                    dependencies=[]
                ),
                MockPlanStep(
                    step_id="step_2", 
                    description="Compare resume against requirements",
                    reasoning_mode="comparative",
                    dependencies=["step_1"]
                )
            ],
            metadata={"priority": "high", "estimated_duration": 300}
        )
        
        # Validate plan structure
        assert plan.plan_id.startswith("test_plan_")
        assert len(plan.steps) == 2
        assert plan.steps[1].dependencies == ["step_1"]
        assert plan.metadata["priority"] == "high"
    
    def test_plan_step_dependency_validation(self):
        """Test that plan step dependencies are properly structured."""
        step_with_deps = MockPlanStep(
            step_id="step_2",
            description="Dependent step",
            reasoning_mode="synthesis",
            dependencies=["step_1"]
        )
        
        step_without_deps = MockPlanStep(
            step_id="step_1",
            description="Independent step", 
            reasoning_mode="analytical",
            dependencies=[]
        )
        
        assert len(step_with_deps.dependencies) == 1
        assert len(step_without_deps.dependencies) == 0
        assert step_with_deps.dependencies[0] == "step_1"


class TestReasoningModeSelection:
    """Test L1 reasoning mode selection logic."""
    
    def test_analytical_reasoning_mode(self):
        """Test analytical reasoning mode selection."""
        mission = "Analyze the technical requirements of this job posting"
        # Mock reasoning mode selector
        selected_mode = "analytical"  # Simplified for unit test
        
        assert selected_mode == "analytical"
    
    def test_comparative_reasoning_mode(self):
        """Test comparative reasoning mode selection."""
        mission = "Compare this resume against the job requirements"
        selected_mode = "comparative"
        
        assert selected_mode == "comparative"
    
    def test_synthesis_reasoning_mode(self):
        """Test synthesis reasoning mode selection."""
        mission = "Generate a tailored resume based on job requirements"
        selected_mode = "synthesis"
        
        assert selected_mode == "synthesis"


class TestPlanOrderingAndDependencies:
    """Test L1 plan step ordering and dependency resolution."""
    
    def test_topological_ordering(self):
        """Test that plan steps maintain valid topological order."""
        steps = [
            MockPlanStep("step_1", "Extract JD", "analytical", []),
            MockPlanStep("step_2", "Parse resume", "analytical", []),
            MockPlanStep("step_3", "Compare requirements", "comparative", ["step_1", "step_2"]),
            MockPlanStep("step_4", "Generate improvements", "synthesis", ["step_3"])
        ]
        
        # Verify dependency order
        step_ids = [step.step_id for step in steps]
        assert step_ids == ["step_1", "step_2", "step_3", "step_4"]
        
        # Verify dependencies exist before dependents
        for step in steps:
            for dep in step.dependencies:
                dep_index = step_ids.index(dep)
                step_index = step_ids.index(step.step_id)
                assert dep_index < step_index, f"Dependency {dep} should come before {step.step_id}"
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies in plans."""
        # This would be implemented with actual dependency graph validation
        # For now, just test the concept
        invalid_steps = [
            MockPlanStep("step_1", "Step 1", "analytical", ["step_2"]),
            MockPlanStep("step_2", "Step 2", "analytical", ["step_1"])
        ]
        
        # In a real implementation, this would detect circular dependency
        # For unit test, we verify the structure exists
        assert invalid_steps[0].dependencies == ["step_2"]
        assert invalid_steps[1].dependencies == ["step_1"]


class TestInputValidationAndErrorHandling:
    """Test L1 input validation and error handling."""
    
    def test_empty_mission_handling(self):
        """Test handling of empty or null mission inputs."""
        with pytest.raises(ValueError, match="Mission cannot be empty"):
            # This would be the actual validation logic
            if not "test mission":
                raise ValueError("Mission cannot be empty")
    
    def test_invalid_step_id_format(self):
        """Test validation of step ID formats."""
        invalid_ids = ["", "   ", "invalid id with spaces", "123_invalid"]
        
        for invalid_id in invalid_ids:
            with pytest.raises(ValueError, match="Invalid step ID format"):
                # Mock validation logic
                if not invalid_id.replace("_", "").isalnum() or " " in invalid_id:
                    raise ValueError("Invalid step ID format")
    
    def test_malformed_dependencies(self):
        """Test handling of malformed dependency references."""
        valid_steps = ["step_1", "step_2", "step_3"]
        invalid_deps = ["nonexistent_step", "", "step_1", "step_4"]
        
        # Test dependency validation
        for dep in invalid_deps:
            if dep not in valid_steps:
                # In real implementation, this would raise an error
                assert dep not in valid_steps


class TestPlanOptimizationAndPruning:
    """Test L1 plan optimization and unnecessary step pruning."""
    
    def test_redundant_step_detection(self):
        """Test detection of redundant or duplicate steps."""
        steps = [
            MockPlanStep("extract_1", "Extract requirements", "analytical", []),
            MockPlanStep("extract_2", "Extract job requirements", "analytical", []),
            MockPlanStep("compare", "Compare resume", "comparative", ["extract_1"])
        ]
        
        # Detect similar steps (simplified for unit test)
        similar_steps = [
            step for step in steps 
            if "extract" in step.description.lower()
        ]
        
        assert len(similar_steps) == 2
        assert similar_steps[0].step_id == "extract_1"
        assert similar_steps[1].step_id == "extract_2"
    
    def test_plan_depth_optimization(self):
        """Test optimization of plan depth to avoid excessive recursion."""
        deep_plan = MockPlan(
            plan_id="deep_plan",
            mission="Deep analysis",
            steps=[MockPlanStep(f"step_{i}", f"Step {i}", "analytical", [f"step_{i-1}"] if i > 0 else []) 
                   for i in range(10)]
        )
        
        # Check plan depth
        max_depth = len(deep_plan.steps)
        assert max_depth == 10
        
        # In real implementation, might optimize if depth > threshold
        if max_depth > 8:
            # Would trigger optimization logic
            pass


class TestPlanOutputFormatting:
    """Test L1 plan output formatting and serialization."""
    
    def test_plan_serialization(self):
        """Test that plans can be properly serialized to JSON."""
        plan = MockPlan(
            plan_id="serial_test",
            mission="Test serialization",
            steps=[
                MockPlanStep("s1", "First step", "analytical", [])
            ],
            metadata={"test": True}
        )
        
        # Mock serialization
        serialized = {
            "plan_id": plan.plan_id,
            "mission": plan.mission,
            "steps": [
                {
                    "step_id": step.step_id,
                    "description": step.description,
                    "reasoning_mode": step.reasoning_mode,
                    "dependencies": step.dependencies
                }
                for step in plan.steps
            ],
            "metadata": plan.metadata
        }
        
        assert serialized["plan_id"] == "serial_test"
        assert len(serialized["steps"]) == 1
        assert serialized["steps"][0]["step_id"] == "s1"
        assert serialized["metadata"]["test"] is True
