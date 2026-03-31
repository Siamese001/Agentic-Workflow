"""Test RemediationDispatcherExceptionHandling functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRemediationDispatcherExceptionHandling:
    """Test RemediationDispatcherExceptionHandling functionality."""

    def test_remediation_dispatcher_exception_handling_imports(self):
        """Test remediation_dispatcher_exception_handling module imports."""
        from agentic_core import remediation_dispatcher_exception_handling
        assert remediation_dispatcher_exception_handling is not None

    def test_remediation_dispatcher_exception_handling_class(self):
        """Test RemediationDispatcherExceptionHandling class exists."""
        from agentic_core import RemediationDispatcherExceptionHandling
        assert RemediationDispatcherExceptionHandling is not None

    def test_remediation_dispatcher_exception_handling_callable(self):
        """Test remediation_dispatcher_exception_handling functions are callable."""
        from agentic_core import validate_remediation_dispatcher_exception_handling
        assert callable(validate_remediation_dispatcher_exception_handling)
