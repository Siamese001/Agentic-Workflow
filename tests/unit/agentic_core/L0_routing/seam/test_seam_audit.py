"""Test SeamAudit functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSeamAudit:
    """Test SeamAudit functionality."""

    def test_seam_audit_imports(self):
        """Test seam_audit module imports."""
        from agentic_core import seam_audit

        assert seam_audit is not None

    def test_seam_audit_class(self):
        """Test SeamAudit class exists."""
        from agentic_core import SeamAudit

        assert SeamAudit is not None

    def test_seam_audit_callable(self):
        """Test seam_audit functions are callable."""
        from agentic_core import validate_seam_audit

        assert callable(validate_seam_audit)
