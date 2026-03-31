"""Test RemediationDispatcherAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRemediationDispatcherAdg:
    """Test RemediationDispatcherAdg functionality."""

    def test_remediation_dispatcher_adg_imports(self):
        """Test remediation_dispatcher_adg module imports."""
        from agentic_core import remediation_dispatcher_adg
        assert remediation_dispatcher_adg is not None

    def test_remediation_dispatcher_adg_class(self):
        """Test RemediationDispatcherAdg class exists."""
        from agentic_core import RemediationDispatcherAdg
        assert RemediationDispatcherAdg is not None

    def test_remediation_dispatcher_adg_callable(self):
        """Test remediation_dispatcher_adg functions are callable."""
        from agentic_core import validate_remediation_dispatcher_adg
        assert callable(validate_remediation_dispatcher_adg)
