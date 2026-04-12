"""Test RuleTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRuleTypesAdg:
    """Test RuleTypesAdg functionality."""

    def test_rule_types_adg_imports(self):
        """Test rule_types_adg module imports."""
        from agentic_core import rule_types_adg

        assert rule_types_adg is not None

    def test_rule_types_adg_class(self):
        """Test RuleTypesAdg class exists."""
        from agentic_core import RuleTypesAdg

        assert RuleTypesAdg is not None

    def test_rule_types_adg_callable(self):
        """Test rule_types_adg functions are callable."""
        from agentic_core import validate_rule_types_adg

        assert callable(validate_rule_types_adg)
