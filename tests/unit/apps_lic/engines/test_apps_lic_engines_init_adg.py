"""Test AppsLicEnginesInitAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAppsLicEnginesInitAdg:
    """Test AppsLicEnginesInitAdg functionality."""

    def test_apps_lic_engines_init_adg_imports(self):
        """Test apps_lic_engines_init_adg module imports."""
        from apps_lic.engines import control_plane

        assert control_plane is not None

    def test_apps_lic_engines_init_adg_class(self):
        """Test ControlPlane class exists in engines."""
        from apps_lic.engines.control_plane import ControlPlane

        assert ControlPlane is not None

    def test_apps_lic_engines_init_adg_callable(self):
        """Test PolicyDecision is callable."""
        from apps_lic.engines.control_plane import PolicyDecision

        assert callable(PolicyDecision)
