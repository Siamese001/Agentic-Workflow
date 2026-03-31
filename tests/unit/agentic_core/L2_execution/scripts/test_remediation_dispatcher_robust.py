"""Test RemediationDispatcherRobust functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRemediationDispatcherRobust:
    """Test RemediationDispatcherRobust functionality."""

    def test_remediation_dispatcher_robust_imports(self):
        """Test remediation_dispatcher_robust module imports."""
        from agentic_core import remediation_dispatcher_robust
        assert remediation_dispatcher_robust is not None

    def test_remediation_dispatcher_robust_class(self):
        """Test RemediationDispatcherRobust class exists."""
        from agentic_core import RemediationDispatcherRobust
        assert RemediationDispatcherRobust is not None

    def test_remediation_dispatcher_robust_callable(self):
        """Test remediation_dispatcher_robust functions are callable."""
        from agentic_core import validate_remediation_dispatcher_robust
        assert callable(validate_remediation_dispatcher_robust)
