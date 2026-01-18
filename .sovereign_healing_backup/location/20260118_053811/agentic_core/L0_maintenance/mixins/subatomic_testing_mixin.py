"""
SubatomicTestingMixin - Provides testing utilities for agents.

This mixin provides common testing functionality that can be mixed into agent classes.
"""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SubatomicTestingMixin:
    """
    Mixin providing subatomic testing capabilities for agents.
    
    This mixin adds testing utilities that allow agents to perform
    fine-grained testing operations.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the testing mixin."""
        super().__init__(*args, **kwargs)
        self._test_results: List[Dict[str, Any]] = []
        self._test_mode: bool = False
    
    def enable_test_mode(self) -> None:
        """Enable test mode for the agent."""
        self._test_mode = True
        logger.debug("Test mode enabled")
    
    def disable_test_mode(self) -> None:
        """Disable test mode for the agent."""
        self._test_mode = False
        logger.debug("Test mode disabled")
    
    def is_test_mode(self) -> bool:
        """Check if test mode is enabled."""
        return getattr(self, '_test_mode', False)
    
    def record_test_result(self, test_name: str, passed: bool, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a test result.
        
        Args:
            test_name: Name of the test
            passed: Whether the test passed
            details: Optional additional details
        """
        result = {
            "test_name": test_name,
            "passed": passed,
            "details": details or {}
        }
        self._test_results.append(result)
        logger.debug(f"Test result recorded: {test_name} - {'PASSED' if passed else 'FAILED'}")
    
    def get_test_results(self) -> List[Dict[str, Any]]:
        """Get all recorded test results."""
        return self._test_results.copy()
    
    def clear_test_results(self) -> None:
        """Clear all recorded test results."""
        self._test_results = []
        logger.debug("Test results cleared")
    
    def run_subatomic_test(self, test_func: callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Run a subatomic test function and record the result.
        
        Args:
            test_func: The test function to run
            *args: Positional arguments for the test function
            **kwargs: Keyword arguments for the test function
            
        Returns:
            Dict containing test result
        """
        test_name = getattr(test_func, '__name__', 'unknown_test')
        try:
            result = test_func(*args, **kwargs)
            self.record_test_result(test_name, True, {"result": result})
            return {"passed": True, "result": result}
        except Exception as e:
            self.record_test_result(test_name, False, {"error": str(e)})
            return {"passed": False, "error": str(e)}
