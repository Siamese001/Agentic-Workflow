"""Test ForensicAuditUnified functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestForensicAuditUnified:
    """Test ForensicAuditUnified functionality."""

    def test_forensic_audit_unified_imports(self):
        """Test forensic_audit_unified module imports."""
        from agentic_core import forensic_audit_unified
        assert forensic_audit_unified is not None

    def test_forensic_audit_unified_class(self):
        """Test ForensicAuditUnified class exists."""
        from agentic_core import ForensicAuditUnified
        assert ForensicAuditUnified is not None

    def test_forensic_audit_unified_callable(self):
        """Test forensic_audit_unified functions are callable."""
        from agentic_core import validate_forensic_audit_unified
        assert callable(validate_forensic_audit_unified)
