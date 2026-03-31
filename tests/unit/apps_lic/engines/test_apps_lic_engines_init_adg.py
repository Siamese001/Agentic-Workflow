"""Test AppsLicEnginesInitAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAppsLicEnginesInitAdg:
    """Test AppsLicEnginesInitAdg functionality."""

    def test_apps_lic_engines_init_adg_imports(self):
        """Test apps_lic_engines_init_adg module imports."""
        from apps_apps import apps_lic_engines_init_adg
        assert apps_lic_engines_init_adg is not None

    def test_apps_lic_engines_init_adg_class(self):
        """Test AppsLicEnginesInitAdg class exists."""
        from apps_apps import AppsLicEnginesInitAdg
        assert AppsLicEnginesInitAdg is not None

    def test_apps_lic_engines_init_adg_callable(self):
        """Test apps_lic_engines_init_adg functions are callable."""
        from apps_apps import validate_apps_lic_engines_init_adg
        assert callable(validate_apps_lic_engines_init_adg)
