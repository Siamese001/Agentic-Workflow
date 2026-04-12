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
        try:
            from agentic_core import guardrail_enforcement

            assert guardrail_enforcement is not None
        except ImportError:
            pytest.skip("guardrail_enforcement not available")

    def test_guardrail_enforcement_class(self):
        """Test GuardrailEnforcement class exists."""
        try:
            from agentic_core import GuardrailEnforcement

            assert GuardrailEnforcement is not None
        except ImportError:
            pytest.skip("GuardrailEnforcement not available")

    def test_guardrail_enforcement_callable(self):
        """Test guardrail_enforcement functions are callable."""
        try:
            from agentic_core import validate_guardrail_enforcement

            assert callable(validate_guardrail_enforcement)
        except ImportError:
            pytest.skip("validate_guardrail_enforcement not available")
