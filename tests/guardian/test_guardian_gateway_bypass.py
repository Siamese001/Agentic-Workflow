"""Test GuardianGatewayBypass functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianGatewayBypass:
    """Test GuardianGatewayBypass functionality."""

    def test_guardian_gateway_bypass_imports(self):
        """Test guardian_gateway_bypass module imports."""
        from agentic_core import guardian_gateway_bypass
        assert guardian_gateway_bypass is not None

    def test_guardian_gateway_bypass_class(self):
        """Test GuardianGatewayBypass class exists."""
        from agentic_core import GuardianGatewayBypass
        assert GuardianGatewayBypass is not None

    def test_guardian_gateway_bypass_callable(self):
        """Test guardian_gateway_bypass functions are callable."""
        from agentic_core import validate_guardian_gateway_bypass
        assert callable(validate_guardian_gateway_bypass)
