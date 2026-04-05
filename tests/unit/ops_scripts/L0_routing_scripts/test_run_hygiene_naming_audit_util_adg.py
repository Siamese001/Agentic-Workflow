"""Test RunHygieneNamingAuditUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRunHygieneNamingAuditUtilAdg:
    """Test RunHygieneNamingAuditUtilAdg functionality."""

    def test_run_hygiene_naming_audit_util_adg_imports(self):
        """Test run_hygiene_naming_audit_util_adg module imports."""
        from agentic_core import run_hygiene_naming_audit_util_adg
        assert run_hygiene_naming_audit_util_adg is not None

    def test_run_hygiene_naming_audit_util_adg_class(self):
        """Test RunHygieneNamingAuditUtilAdg class exists."""
        from agentic_core import RunHygieneNamingAuditUtilAdg
        assert RunHygieneNamingAuditUtilAdg is not None

    def test_run_hygiene_naming_audit_util_adg_callable(self):
        """Test run_hygiene_naming_audit_util_adg functions are callable."""
        from agentic_core import validate_run_hygiene_naming_audit_util_adg
        assert callable(validate_run_hygiene_naming_audit_util_adg)
