"""Test SsotAuditTrailMixin functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSsotAuditTrailMixin:
    """Test SsotAuditTrailMixin functionality."""

    def test_ssot_audit_trail_mixin_imports(self):
        """Test ssot_audit_trail_mixin module imports."""
        from agentic_core import ssot_audit_trail_mixin

        assert ssot_audit_trail_mixin is not None

    def test_ssot_audit_trail_mixin_class(self):
        """Test SsotAuditTrailMixin class exists."""
        from agentic_core import SsotAuditTrailMixin

        assert SsotAuditTrailMixin is not None

    def test_ssot_audit_trail_mixin_callable(self):
        """Test ssot_audit_trail_mixin functions are callable."""
        from agentic_core import validate_ssot_audit_trail_mixin

        assert callable(validate_ssot_audit_trail_mixin)
