"""
Unit tests for SubatomicTestingMixin - L0 Maintenance zombie healing.
Phase 7: Zombie Healing - 100% coverage test suite
"""
import pytest
from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin


class TestAgent(SubatomicTestingMixin):
    """Test agent class that uses SubatomicTestingMixin."""
    
    def __init__(self):
        super().__init__()


class TestSubatomicTestingMixin:
    """Comprehensive test suite for SubatomicTestingMixin."""
    
    def test_initialization(self):
        """Test mixin initializes with default values."""
        agent = TestAgent()
        
        assert hasattr(agent, '_test_results')
        assert hasattr(agent, '_test_mode')
        assert agent._test_results == []
        assert agent._test_mode is False
    
    def test_enable_test_mode(self):
        """Test enabling test mode."""
        agent = TestAgent()
        
        agent.enable_test_mode()
        
        assert agent._test_mode is True
        assert agent.is_test_mode() is True
    
    def test_disable_test_mode(self):
        """Test disabling test mode."""
        agent = TestAgent()
        agent.enable_test_mode()
        
        agent.disable_test_mode()
        
        assert agent._test_mode is False
        assert agent.is_test_mode() is False
    
    def test_is_test_mode_default(self):
        """Test is_test_mode returns False by default."""
        agent = TestAgent()
        
        assert agent.is_test_mode() is False
    
    def test_is_test_mode_after_enable(self):
        """Test is_test_mode returns True after enabling."""
        agent = TestAgent()
        agent.enable_test_mode()
        
        assert agent.is_test_mode() is True
    
    def test_record_test_result_passed(self):
        """Test recording a passed test result."""
        agent = TestAgent()
        
        agent.record_test_result("test_example", True, {"info": "success"})
        
        results = agent.get_test_results()
        assert len(results) == 1
        assert results[0]["test_name"] == "test_example"
        assert results[0]["passed"] is True
        assert results[0]["details"]["info"] == "success"
    
    def test_record_test_result_failed(self):
        """Test recording a failed test result."""
        agent = TestAgent()
        
        agent.record_test_result("test_failure", False, {"error": "assertion failed"})
        
        results = agent.get_test_results()
        assert len(results) == 1
        assert results[0]["test_name"] == "test_failure"
        assert results[0]["passed"] is False
        assert results[0]["details"]["error"] == "assertion failed"
    
    def test_record_test_result_without_details(self):
        """Test recording test result without details."""
        agent = TestAgent()
        
        agent.record_test_result("test_simple", True)
        
        results = agent.get_test_results()
        assert len(results) == 1
        assert results[0]["details"] == {}
    
    def test_record_multiple_test_results(self):
        """Test recording multiple test results."""
        agent = TestAgent()
        
        agent.record_test_result("test1", True)
        agent.record_test_result("test2", False)
        agent.record_test_result("test3", True)
        
        results = agent.get_test_results()
        assert len(results) == 3
        assert results[0]["test_name"] == "test1"
        assert results[1]["test_name"] == "test2"
        assert results[2]["test_name"] == "test3"
    
    def test_get_test_results_returns_copy(self):
        """Test get_test_results returns a copy, not reference."""
        agent = TestAgent()
        agent.record_test_result("test1", True)
        
        results1 = agent.get_test_results()
        results2 = agent.get_test_results()
        
        # Modify first copy
        results1.append({"test_name": "fake", "passed": False, "details": {}})
        
        # Second copy should be unaffected
        assert len(results2) == 1
        assert len(agent.get_test_results()) == 1
    
    def test_clear_test_results(self):
        """Test clearing test results."""
        agent = TestAgent()
        agent.record_test_result("test1", True)
        agent.record_test_result("test2", False)
        
        assert len(agent.get_test_results()) == 2
        
        agent.clear_test_results()
        
        assert len(agent.get_test_results()) == 0
        assert agent._test_results == []
    
    def test_run_subatomic_test_success(self):
        """Test running a successful subatomic test."""
        agent = TestAgent()
        
        def passing_test():
            return "success"
        
        result = agent.run_subatomic_test(passing_test)
        
        assert result["passed"] is True
        assert result["result"] == "success"
        
        # Verify result was recorded
        results = agent.get_test_results()
        assert len(results) == 1
        assert results[0]["test_name"] == "passing_test"
        assert results[0]["passed"] is True
    
    def test_run_subatomic_test_failure(self):
        """Test running a failing subatomic test."""
        agent = TestAgent()
        
        def failing_test():
            raise ValueError("Test error")
        
        result = agent.run_subatomic_test(failing_test)
        
        assert result["passed"] is False
        assert "error" in result
        assert "Test error" in result["error"]
        
        # Verify failure was recorded
        results = agent.get_test_results()
        assert len(results) == 1
        assert results[0]["passed"] is False
    
    def test_run_subatomic_test_with_args(self):
        """Test running subatomic test with arguments."""
        agent = TestAgent()
        
        def test_with_args(a, b):
            return a + b
        
        result = agent.run_subatomic_test(test_with_args, 5, 3)
        
        assert result["passed"] is True
        assert result["result"] == 8
    
    def test_run_subatomic_test_with_kwargs(self):
        """Test running subatomic test with keyword arguments."""
        agent = TestAgent()
        
        def test_with_kwargs(x=0, y=0):
            return x * y
        
        result = agent.run_subatomic_test(test_with_kwargs, x=4, y=7)
        
        assert result["passed"] is True
        assert result["result"] == 28
    
    def test_run_subatomic_test_lambda(self):
        """Test running subatomic test with lambda function."""
        agent = TestAgent()
        
        result = agent.run_subatomic_test(lambda: 42)
        
        assert result["passed"] is True
        assert result["result"] == 42
    
    def test_multiple_agents_independent(self):
        """Test multiple agent instances maintain independent state."""
        agent1 = TestAgent()
        agent2 = TestAgent()
        
        agent1.enable_test_mode()
        agent1.record_test_result("test1", True)
        
        agent2.record_test_result("test2", False)
        
        # Verify independence
        assert agent1.is_test_mode() is True
        assert agent2.is_test_mode() is False
        assert len(agent1.get_test_results()) == 1
        assert len(agent2.get_test_results()) == 1
        assert agent1.get_test_results()[0]["test_name"] == "test1"
        assert agent2.get_test_results()[0]["test_name"] == "test2"
    
    def test_test_mode_toggle_multiple_times(self):
        """Test toggling test mode multiple times."""
        agent = TestAgent()
        
        agent.enable_test_mode()
        assert agent.is_test_mode() is True
        
        agent.disable_test_mode()
        assert agent.is_test_mode() is False
        
        agent.enable_test_mode()
        assert agent.is_test_mode() is True
        
        agent.enable_test_mode()  # Enable when already enabled
        assert agent.is_test_mode() is True
    
    def test_record_test_result_with_complex_details(self):
        """Test recording test result with complex nested details."""
        agent = TestAgent()
        
        complex_details = {
            "metrics": {"accuracy": 0.95, "precision": 0.92},
            "errors": ["error1", "error2"],
            "nested": {"deep": {"value": 123}}
        }
        
        agent.record_test_result("complex_test", True, complex_details)
        
        results = agent.get_test_results()
        assert results[0]["details"]["metrics"]["accuracy"] == 0.95
        assert results[0]["details"]["errors"] == ["error1", "error2"]
        assert results[0]["details"]["nested"]["deep"]["value"] == 123
