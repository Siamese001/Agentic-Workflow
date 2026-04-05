"""Test ImmutableStagingBufferAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestImmutableStagingBufferAdg:
    """Test ImmutableStagingBufferAdg functionality."""

    def test_immutable_staging_buffer_adg_imports(self):
        """Test immutable_staging_buffer_adg module imports."""
        from agentic_core import immutable_staging_buffer_adg
        assert immutable_staging_buffer_adg is not None

    def test_immutable_staging_buffer_adg_class(self):
        """Test ImmutableStagingBufferAdg class exists."""
        from agentic_core import ImmutableStagingBufferAdg
        assert ImmutableStagingBufferAdg is not None

    def test_immutable_staging_buffer_adg_callable(self):
        """Test immutable_staging_buffer_adg functions are callable."""
        from agentic_core import validate_immutable_staging_buffer_adg
        assert callable(validate_immutable_staging_buffer_adg)
