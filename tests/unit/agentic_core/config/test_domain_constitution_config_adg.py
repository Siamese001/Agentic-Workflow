"""Test DomainConstitutionConfigAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDomainConstitutionConfigAdg:
    """Test DomainConstitutionConfigAdg functionality."""

    def test_domain_constitution_config_adg_imports(self):
        """Test domain_constitution_config_adg module imports."""
        from agentic_core import domain_constitution_config_adg
        assert domain_constitution_config_adg is not None

    def test_domain_constitution_config_adg_class(self):
        """Test DomainConstitutionConfigAdg class exists."""
        from agentic_core import DomainConstitutionConfigAdg
        assert DomainConstitutionConfigAdg is not None

    def test_domain_constitution_config_adg_callable(self):
        """Test domain_constitution_config_adg functions are callable."""
        from agentic_core import validate_domain_constitution_config_adg
        assert callable(validate_domain_constitution_config_adg)
