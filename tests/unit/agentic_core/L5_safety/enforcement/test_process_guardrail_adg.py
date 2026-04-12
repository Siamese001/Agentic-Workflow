"""Test ProcessGuardrailAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestProcessGuardrailAdg:
    """Test ProcessGuardrailAdg functionality."""

    def test_process_guardrail_adg_imports(self):
        """Test process_guardrail_adg module imports."""
        from agentic_core import process_guardrail_adg

        assert process_guardrail_adg is not None

    def test_process_guardrail_adg_class(self):
        """Test ProcessGuardrailAdg class exists."""
        from agentic_core import ProcessGuardrailAdg

        assert ProcessGuardrailAdg is not None

    def test_process_guardrail_adg_callable(self):
        """Test process_guardrail_adg functions are callable."""
        from agentic_core import validate_process_guardrail_adg

        assert callable(validate_process_guardrail_adg)
