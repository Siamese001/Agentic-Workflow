"""Test RuntimeMutationGuardrailAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRuntimeMutationGuardrailAdg:
    """Test RuntimeMutationGuardrailAdg functionality."""

    def test_runtime_mutation_guardrail_adg_imports(self):
        """Test runtime_mutation_guardrail_adg module imports."""
        from agentic_core import runtime_mutation_guardrail_adg

        assert runtime_mutation_guardrail_adg is not None

    def test_runtime_mutation_guardrail_adg_class(self):
        """Test RuntimeMutationGuardrailAdg class exists."""
        from agentic_core import RuntimeMutationGuardrailAdg

        assert RuntimeMutationGuardrailAdg is not None

    def test_runtime_mutation_guardrail_adg_callable(self):
        """Test runtime_mutation_guardrail_adg functions are callable."""
        from agentic_core import validate_runtime_mutation_guardrail_adg

        assert callable(validate_runtime_mutation_guardrail_adg)
