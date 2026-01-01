"""Unit tests for core domain models: MissionPlan, MissionResult, Missing."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


@pytest.mark.unit
class test_mission_plan_model:
    """Test MissionPlan domain model."""

    def test_mission_plan_creation_with_builder(self) -> Any:
        """
        GIVEN: MissionPlan.Builder with required fields
        WHEN: build() is called
        THEN: Valid MissionPlan instance created
        """
        from agentic_core.L0_maintenance.P1_core.core import MissionPlan
        plan: Any = MissionPlan(mission_id='test-001', objective='Test sovereignty', phases=['phase1', 'phase2'], status='pending')
        assert plan.mission_id == 'test-001'
        assert plan.objective == 'Test sovereignty'
        assert len(plan.phases) == 2
        assert plan.status == 'pending'

    def test_mission_plan_async_execute(self) -> Any:
        """
        GIVEN: MissionPlan instance
        WHEN: execute() is called
        THEN: Returns MissionResult with success status
        """
        from agentic_core.L0_maintenance.P1_core.core import MissionPlan
        plan: Any = MissionPlan(mission_id='exec-001', objective='Execute test', phases=['init'], status='pending')
        import asyncio
        result: Any = asyncio.run(plan.execute())
        assert result is not None
        assert hasattr(result, 'mission_id')
        assert hasattr(result, 'success')

    def test_mission_plan_validation_requires_mission_id(self) -> Any:
        """
        GIVEN: MissionPlan without mission_id
        WHEN: Validation occurs
        THEN: Raises ValueError
        """
        from agentic_core.L0_maintenance.P1_core.core import MissionPlan
        with pytest.raises((ValueError, TypeError)):
            MissionPlan(mission_id=None, objective='Test', phases=[], status='pending')

    @pytest.mark.parametrize('status', ['pending', 'running', 'completed', 'failed'])
    def test_mission_plan_status_transitions(self, status: Any) -> Any:
        """
        GIVEN: MissionPlan with various statuses
        WHEN: Status is set
        THEN: Status persists correctly
        """
        from agentic_core.L0_maintenance.P1_core.core import MissionPlan
        plan: Any = MissionPlan(mission_id=f'status-{status}', objective='Test status', phases=['phase1'], status=status)
        assert plan.status == status

@pytest.mark.unit
class test_mission_result_model:
    """Test MissionResult domain model."""

    def test_mission_result_to_dict(self) -> Any:
        """
        GIVEN: MissionResult instance
        WHEN: to_dict() is called
        THEN: Returns dictionary representation
        """
        from agentic_core.L0_maintenance.P1_core.core import MissionResult
        result: Any = MissionResult(mission_id='result-001', success=True, output={'data': 'test'}, metadata={'timestamp': '2024-12-27'})
        result_dict: Any = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict['mission_id'] == 'result-001'
        assert result_dict['success'] is True
        assert 'output' in result_dict

    def test_mission_result_success_flag(self) -> Any:
        """
        GIVEN: MissionResult with success=True
        WHEN: Checked
        THEN: Success flag is True
        """
        from agentic_core.L0_maintenance.P1_core.core import MissionResult
        result: Any = MissionResult(mission_id='success-001', success=True, output={}, metadata={})
        assert result.success is True

    def test_mission_result_failure_with_error(self) -> Any:
        """
        GIVEN: MissionResult with success=False and error
        WHEN: Checked
        THEN: Error information preserved
        """
        from agentic_core.L0_maintenance.P1_core.core import MissionResult
        result: Any = MissionResult(mission_id='fail-001', success=False, output={}, metadata={'error': 'Test failure'})
        assert result.success is False
        assert 'error' in result.metadata

@pytest.mark.unit
class test_agentic_core_model:
    """Test AgenticCore domain model."""

    def test_agentic_core_initialization(self) -> Any:
        """
        GIVEN: AgenticCore instantiation
        WHEN: Created
        THEN: Default attributes set correctly
        """
        from agentic_core.L0_maintenance.P1_core.core import AgenticCore
        core: Any = AgenticCore()
        assert hasattr(core, 'history')
        assert hasattr(core, 'status')
        assert hasattr(core, 'version')
        assert hasattr(core, 'capabilities')
        assert core.status == 'active'

    def test_agentic_core_run_returns_dict(self) -> Any:
        """
        GIVEN: AgenticCore instance
        WHEN: run() is called
        THEN: Returns dict with status and metadata
        """
        from agentic_core.L0_maintenance.P1_core.core import AgenticCore
        core: Any = AgenticCore()
        result: Any = core.run(mission={'test': 'data'})
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'success' in result

    def test_agentic_core_reflect_logs_to_history(self) -> Any:
        """
        GIVEN: AgenticCore instance
        WHEN: reflect() is called
        THEN: Reflection logged to history
        """
        from agentic_core.L0_maintenance.P1_core.core import AgenticCore
        core: Any = AgenticCore()
        initial_history_len: Any = len(core.history)
        core.reflect(context='Test reflection')
        assert len(core.history) > initial_history_len
        assert any(('reflect' in str(entry).lower() for entry in core.history))

    def test_agentic_core_heal_returns_dict(self) -> Any:
        """
        GIVEN: AgenticCore instance
        WHEN: heal() is called
        THEN: Returns dict with healed, recovery, error fields
        """
        from agentic_core.L0_maintenance.P1_core.core import AgenticCore
        core: Any = AgenticCore()
        result: Any = core.heal()
        assert isinstance(result, dict)
        assert 'healed' in result
        assert 'recovery' in result
        assert 'error' in result

    def test_agentic_core_get_status(self) -> Any:
        """
        GIVEN: AgenticCore instance
        WHEN: get_status() is called
        THEN: Returns comprehensive status dict
        """
        from agentic_core.L0_maintenance.P1_core.core import AgenticCore
        core: Any = AgenticCore()
        status: Any = core.get_status()
        assert isinstance(status, dict)
        assert 'status' in status
        assert 'history_length' in status
        assert 'sovereign' in status

@pytest.mark.unit
class test_missing_class:
    """Test Missing sentinel class."""

    def test_missing_singleton_behavior(self) -> Any:
        """
        GIVEN: Multiple Missing instances
        WHEN: Created
        THEN: All reference same singleton
        """
        from agentic_core.L0_maintenance.P1_core.core import Missing
        missing1: Any = Missing()
        missing2: Any = Missing()
        assert missing1 is missing2

    def test_missing_repr(self) -> Any:
        """
        GIVEN: Missing instance
        WHEN: repr() called
        THEN: Returns descriptive string
        """
        from agentic_core.L0_maintenance.P1_core.core import Missing
from typing import Any
        missing: Any = Missing()
        representation: Any = repr(missing)
        assert 'Missing' in representation or 'MISSING' in representation
