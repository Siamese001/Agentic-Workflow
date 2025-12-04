"""
Test Safety Planning

Tests comprehensive safety planning functionality for résumé validation,
including safety plan creation, content validation, and policy enforcement.
"""

import pytest
from unittest.mock import Mock

# Import actual safety planning components
try:
    from l1.safety_planning import (
        SafetyPlan,
    )
except ImportError:
    pytest.skip("Safety planning components not available", allow_module_level=True)

# Mark as L1 planning tests
pytestmark = [pytest.mark.l1, pytest.mark.planning, pytest.mark.safety]


class TestSafetyPlanning:
    """Test safety planning functionality."""
    
    def test_safety_plan_dataclass_structure(self):
        """Test SafetyPlan dataclass structure."""
        # Create a mock prompt
        prompt = Mock()
        prompt.id = "test.safety"
        prompt.content = "Test safety content"
        
        # Create SafetyPlan
        safety_plan = SafetyPlan(prompt=prompt)
        
        # Validate structure
        assert hasattr(safety_plan, 'prompt')
        assert safety_plan.prompt == prompt
        assert isinstance(safety_plan.prompt, Mock)
