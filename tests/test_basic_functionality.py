#!/usr/bin/env python3
"""
Basic functionality tests for Windsurf validation
"""

def test_basic_imports():
    """Test that critical modules can be imported"""
    try:
        from agentic_core.l2_execution.tools.drafting.draft_executor import DraftExecutor
        from agentic_core.l3_orchestration.framework import create_dag, validate_dag, execute_dag
        from runtime.runtime_utils import invoke_model
        from runtime.core.models import ComplexityLevel
        from runtime.core.routing import RoutingPolicy
        from runtime.observability import record_event
        from config.meta_profile import create_user_profile
        assert True  # All imports successful
    except Exception as e:
        assert False, f"Import failed: {e}"

def test_dag_functionality():
    """Test basic DAG functionality"""
    try:
        from agentic_core.l3_orchestration.framework import create_dag, validate_dag, execute_dag
        
        # Create and validate a test DAG
        dag = create_dag('test-dag')
        is_valid = validate_dag(dag)
        result = execute_dag(dag)
        
        assert is_valid == True
        assert result.status.value == 'COMPLETED'
    except Exception as e:
        assert False, f"DAG test failed: {e}"

def test_core_models():
    """Test core models functionality"""
    try:
        from runtime.core.models import ComplexityLevel, TaskType, ExecutionStatus
        
        # Test complexity levels
        low = ComplexityLevel.LOW
        medium = ComplexityLevel.MEDIUM
        high = ComplexityLevel.HIGH
        
        assert low < medium < high
        assert low.numeric_value() < medium.numeric_value() < high.numeric_value()
    except Exception as e:
        assert False, f"Core models test failed: {e}"

def test_observability():
    """Test observability functionality"""
    try:
        from runtime.observability import record_event, EventType, SeverityLevel
        
        # Test event recording
        record_event(
            event_type=EventType.SYSTEM,
            severity=SeverityLevel.INFO,
            message="Test event",
            source="test"
        )
        assert True  # Event recorded successfully
    except Exception as e:
        assert False, f"Observability test failed: {e}"

def test_config():
    """Test configuration functionality"""
    try:
        from config.meta_profile import create_user_profile, create_configuration_snapshot
        
        # Test user profile creation
        profile = create_user_profile(user_id="test-user")
        snapshot = create_configuration_snapshot(profile)
        
        assert profile.user_id == "test-user"
        assert snapshot is not None
    except Exception as e:
        assert False, f"Config test failed: {e}"





