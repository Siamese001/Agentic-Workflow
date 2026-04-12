"""Test ThreeTierComplianceEnforcerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestThreeTierComplianceEnforcerAdg:
    """Test ThreeTierComplianceEnforcerAdg functionality."""

    def test_three_tier_compliance_enforcer_adg_imports(self):
        """Test three_tier_compliance_enforcer_adg module imports."""
        from agentic_core import three_tier_compliance_enforcer_adg

        assert three_tier_compliance_enforcer_adg is not None

    def test_three_tier_compliance_enforcer_adg_class(self):
        """Test ThreeTierComplianceEnforcerAdg class exists."""
        from agentic_core import ThreeTierComplianceEnforcerAdg

        assert ThreeTierComplianceEnforcerAdg is not None

    def test_three_tier_compliance_enforcer_adg_callable(self):
        """Test three_tier_compliance_enforcer_adg functions are callable."""
        from agentic_core import validate_three_tier_compliance_enforcer_adg

        assert callable(validate_three_tier_compliance_enforcer_adg)
