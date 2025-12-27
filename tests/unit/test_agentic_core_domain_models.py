"""Unit tests for core domain models: MissionPlan, MissionResult, Missing."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime


@pytest.mark.unit
class TestMissionPlanModel:
    """Test MissionPlan domain model."""
    
    def test_mission_plan_creation_with_builder(self):
        """
        GIVEN: MissionPlan.Builder with required fields
        WHEN: build() is called
        THEN: Valid MissionPlan instance created
        """
        # Arrange & Act
        from agentic_core.core import MissionPlan
        
        plan = MissionPlan(
            mission_id="test-001",
            objective="Test sovereignty",
            phases=["phase1", "phase2"],
            status="pending"
        )
        
        # Assert
        assert plan.mission_id == "test-001"
        assert plan.objective == "Test sovereignty"
        assert len(plan.phases) == 2
        assert plan.status == "pending"
    
    def test_mission_plan_async_execute(self):
        """
        GIVEN: MissionPlan instance
        WHEN: execute() is called
        THEN: Returns MissionResult with success status
        """
        # Arrange
        from agentic_core.core import MissionPlan
        
        plan = MissionPlan(
            mission_id="exec-001",
            objective="Execute test",
            phases=["init"],
            status="pending"
        )
        
        # Act
        import asyncio
        result = asyncio.run(plan.execute())
        
        # Assert
        assert result is not None
        assert hasattr(result, 'mission_id')
        assert hasattr(result, 'success')
    
    def test_mission_plan_validation_requires_mission_id(self):
        """
        GIVEN: MissionPlan without mission_id
        WHEN: Validation occurs
        THEN: Raises ValueError
        """
        # Arrange & Act & Assert
        from agentic_core.core import MissionPlan
        
        with pytest.raises((ValueError, TypeError)):
            MissionPlan(
                mission_id=None,
                objective="Test",
                phases=[],
                status="pending"
            )
    
    @pytest.mark.parametrize("status", ["pending", "running", "completed", "failed"])
    def test_mission_plan_status_transitions(self, status):
        """
        GIVEN: MissionPlan with various statuses
        WHEN: Status is set
        THEN: Status persists correctly
        """
        # Arrange
        from agentic_core.core import MissionPlan
        
        plan = MissionPlan(
            mission_id=f"status-{status}",
            objective="Test status",
            phases=["phase1"],
            status=status
        )
        
        # Assert
        assert plan.status == status


@pytest.mark.unit
class TestMissionResultModel:
    """Test MissionResult domain model."""
    
    def test_mission_result_to_dict(self):
        """
        GIVEN: MissionResult instance
        WHEN: to_dict() is called
        THEN: Returns dictionary representation
        """
        # Arrange
        from agentic_core.core import MissionResult
        
        result = MissionResult(
            mission_id="result-001",
            success=True,
            output={"data": "test"},
            metadata={"timestamp": "2024-12-27"}
        )
        
        # Act
        result_dict = result.to_dict()
        
        # Assert
        assert isinstance(result_dict, dict)
        assert result_dict["mission_id"] == "result-001"
        assert result_dict["success"] is True
        assert "output" in result_dict
    
    def test_mission_result_success_flag(self):
        """
        GIVEN: MissionResult with success=True
        WHEN: Checked
        THEN: Success flag is True
        """
        # Arrange
        from agentic_core.core import MissionResult
        
        result = MissionResult(
            mission_id="success-001",
            success=True,
            output={},
            metadata={}
        )
        
        # Assert
        assert result.success is True
    
    def test_mission_result_failure_with_error(self):
        """
        GIVEN: MissionResult with success=False and error
        WHEN: Checked
        THEN: Error information preserved
        """
        # Arrange
        from agentic_core.core import MissionResult
        
        result = MissionResult(
            mission_id="fail-001",
            success=False,
            output={},
            metadata={"error": "Test failure"}
        )
        
        # Assert
        assert result.success is False
        assert "error" in result.metadata


@pytest.mark.unit
class TestAgenticCoreModel:
    """Test AgenticCore domain model."""
    
    def test_agentic_core_initialization(self):
        """
        GIVEN: AgenticCore instantiation
        WHEN: Created
        THEN: Default attributes set correctly
        """
        # Arrange & Act
        from agentic_core.core import AgenticCore
        
        core = AgenticCore()
        
        # Assert
        assert hasattr(core, 'history')
        assert hasattr(core, 'status')
        assert hasattr(core, 'version')
        assert hasattr(core, 'capabilities')
        assert core.status == "active"
    
    def test_agentic_core_run_returns_dict(self):
        """
        GIVEN: AgenticCore instance
        WHEN: run() is called
        THEN: Returns dict with status and metadata
        """
        # Arrange
        from agentic_core.core import AgenticCore
        
        core = AgenticCore()
        
        # Act
        result = core.run(mission={"test": "data"})
        
        # Assert
        assert isinstance(result, dict)
        assert "status" in result
        assert "success" in result
    
    def test_agentic_core_reflect_logs_to_history(self):
        """
        GIVEN: AgenticCore instance
        WHEN: reflect() is called
        THEN: Reflection logged to history
        """
        # Arrange
        from agentic_core.core import AgenticCore
        
        core = AgenticCore()
        initial_history_len = len(core.history)
        
        # Act
        core.reflect(context="Test reflection")
        
        # Assert
        assert len(core.history) > initial_history_len
        assert any("reflect" in str(entry).lower() for entry in core.history)
    
    def test_agentic_core_heal_returns_dict(self):
        """
        GIVEN: AgenticCore instance
        WHEN: heal() is called
        THEN: Returns dict with healed, recovery, error fields
        """
        # Arrange
        from agentic_core.core import AgenticCore
        
        core = AgenticCore()
        
        # Act
        result = core.heal()
        
        # Assert
        assert isinstance(result, dict)
        assert "healed" in result
        assert "recovery" in result
        assert "error" in result
    
    def test_agentic_core_get_status(self):
        """
        GIVEN: AgenticCore instance
        WHEN: get_status() is called
        THEN: Returns comprehensive status dict
        """
        # Arrange
        from agentic_core.core import AgenticCore
        
        core = AgenticCore()
        
        # Act
        status = core.get_status()
        
        # Assert
        assert isinstance(status, dict)
        assert "status" in status
        assert "history_length" in status
        assert "sovereign" in status


@pytest.mark.unit
class TestMissingClass:
    """Test Missing sentinel class."""
    
    def test_missing_singleton_behavior(self):
        """
        GIVEN: Multiple Missing instances
        WHEN: Created
        THEN: All reference same singleton
        """
        # Arrange & Act
        from agentic_core.core import Missing
        
        missing1 = Missing()
        missing2 = Missing()
        
        # Assert
        assert missing1 is missing2
    
    def test_missing_repr(self):
        """
        GIVEN: Missing instance
        WHEN: repr() called
        THEN: Returns descriptive string
        """
        # Arrange
        from agentic_core.core import Missing
        
        missing = Missing()
        
        # Act
        representation = repr(missing)
        
        # Assert
        assert "Missing" in representation or "MISSING" in representation
