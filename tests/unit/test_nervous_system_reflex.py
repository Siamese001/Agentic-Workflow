"""Unit tests for NervousSystem reflex layer."""
import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
class TestNervousSystemReflex:
    """Test NervousSystem reflex triggering and mission registration."""
    
    def test_nervous_system_initialization(self):
        """
        GIVEN: NervousSystem instantiation
        WHEN: Created
        THEN: Reflex layer ready
        """
        # Arrange & Act
        from agentic_core.L3_orchestration.nervous_system import NervousSystem
        
        ns = NervousSystem()
        
        # Assert
        assert hasattr(ns, 'reflexes')
        assert hasattr(ns, 'missions')
    
    def test_trigger_reflex_returns_handled_flag(self):
        """
        GIVEN: NervousSystem instance
        WHEN: trigger_reflex() called
        THEN: Returns dict with handled flag
        """
        # Arrange
        from agentic_core.L3_orchestration.nervous_system import NervousSystem
        
        ns = NervousSystem()
        
        # Act
        result = ns.trigger_reflex("test_stimulus")
        
        # Assert
        assert isinstance(result, dict)
        assert "handled" in result
    
    def test_get_status_returns_health_info(self):
        """
        GIVEN: NervousSystem instance
        WHEN: get_status() called
        THEN: Returns health check dict
        """
        # Arrange
        from agentic_core.L3_orchestration.nervous_system import NervousSystem
        
        ns = NervousSystem()
        
        # Act
        status = ns.get_status()
        
        # Assert
        assert isinstance(status, dict)
        assert "status" in status or "healthy" in status
