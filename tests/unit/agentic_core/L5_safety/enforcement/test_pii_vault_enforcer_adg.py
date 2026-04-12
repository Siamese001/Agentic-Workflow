"""Test PiiVaultEnforcerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPiiVaultEnforcerAdg:
    """Test PiiVaultEnforcerAdg functionality."""

    def test_pii_vault_enforcer_adg_imports(self):
        """Test pii_vault_enforcer_adg module imports."""
        from agentic_core import pii_vault_enforcer_adg

        assert pii_vault_enforcer_adg is not None

    def test_pii_vault_enforcer_adg_class(self):
        """Test PiiVaultEnforcerAdg class exists."""
        from agentic_core import PiiVaultEnforcerAdg

        assert PiiVaultEnforcerAdg is not None

    def test_pii_vault_enforcer_adg_callable(self):
        """Test pii_vault_enforcer_adg functions are callable."""
        from agentic_core import validate_pii_vault_enforcer_adg

        assert callable(validate_pii_vault_enforcer_adg)
