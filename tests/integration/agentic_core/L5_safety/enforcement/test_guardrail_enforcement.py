"""Test GuardrailEnforcement functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardrailEnforcement:
    """Test GuardrailEnforcement functionality."""

    def test_guardrail_enforcement_imports(self):
        """Test guardrail_enforcement module imports."""
        from agentic_core import guardrail_enforcement
        assert guardrail_enforcement is not None

    def test_guardrail_enforcement_class(self):
        """Test GuardrailEnforcement class exists."""
        from agentic_core import GuardrailEnforcement
        assert GuardrailEnforcement is not None

    def test_guardrail_enforcement_callable(self):
        """Test guardrail_enforcement functions are callable."""
        from agentic_core import validate_guardrail_enforcement
        assert callable(validate_guardrail_enforcement)
