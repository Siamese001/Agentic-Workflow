"""Test ArtifactTypedCompatTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestArtifactTypedCompatTypesAdg:
    """Test ArtifactTypedCompatTypesAdg functionality."""

    def test_artifact_typed_compat_types_adg_imports(self):
        """Test artifact_typed_compat_types_adg module imports."""
        from agentic_core import artifact_typed_compat_types_adg

        assert artifact_typed_compat_types_adg is not None

    def test_artifact_typed_compat_types_adg_class(self):
        """Test ArtifactTypedCompatTypesAdg class exists."""
        from agentic_core import ArtifactTypedCompatTypesAdg

        assert ArtifactTypedCompatTypesAdg is not None

    def test_artifact_typed_compat_types_adg_callable(self):
        """Test artifact_typed_compat_types_adg functions are callable."""
        from agentic_core import validate_artifact_typed_compat_types_adg

        assert callable(validate_artifact_typed_compat_types_adg)
