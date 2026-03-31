"""Test ADG G7 G16 creative extensions functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgG7G16CreativeExtensions:
    """Test ADG G7 G16 creative extensions functionality."""

    def test_g7_g16_creative_imports(self):
        """Test G7 G16 creative module imports."""
        from tools.adg import identify_guardrail_gaps
        assert identify_guardrail_gaps is not None

    def test_g7_g16_creative_extensions(self):
        """Test G7 G16 creative extensions function."""
        from tools.adg.identify_guardrail_gaps import apply_creative_extensions
        assert callable(apply_creative_extensions)

    def test_g7_g16_extension_handler(self):
        """Test G7 G16 extension handler."""
        from tools.adg.identify_guardrail_gaps import G7G16ExtensionHandler
        assert G7G16ExtensionHandler is not None
