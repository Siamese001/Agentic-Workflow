"""Test ControlPlane functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestControlPlane:
    """Test ControlPlane functionality."""

    def test_control_plane_imports(self):
        """Test control_plane module imports."""
        from apps_lic.engines import control_plane

        assert control_plane is not None

    def test_control_plane_class(self):
        """Test ControlPlane class exists."""
        from apps_lic.engines.control_plane import ControlPlane

        assert ControlPlane is not None

    def test_control_plane_callable(self):
        """Test control_plane functions are callable."""
        from apps_lic.engines.control_plane import PolicyAction, PolicyDecision

        assert callable(PolicyDecision)
        assert callable(PolicyAction)
