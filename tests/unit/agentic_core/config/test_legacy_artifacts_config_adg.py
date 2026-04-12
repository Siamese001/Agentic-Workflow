"""Test LegacyArtifactsConfigAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLegacyArtifactsConfigAdg:
    """Test LegacyArtifactsConfigAdg functionality."""

    def test_legacy_artifacts_config_adg_imports(self):
        """Test legacy_artifacts_config_adg module imports."""
        from agentic_core import legacy_artifacts_config_adg

        assert legacy_artifacts_config_adg is not None

    def test_legacy_artifacts_config_adg_class(self):
        """Test LegacyArtifactsConfigAdg class exists."""
        from agentic_core import LegacyArtifactsConfigAdg

        assert LegacyArtifactsConfigAdg is not None

    def test_legacy_artifacts_config_adg_callable(self):
        """Test legacy_artifacts_config_adg functions are callable."""
        from agentic_core import validate_legacy_artifacts_config_adg

        assert callable(validate_legacy_artifacts_config_adg)
