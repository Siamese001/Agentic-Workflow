"""Test SkillExtractorNodeTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSkillExtractorNodeTypesAdg:
    """Test SkillExtractorNodeTypesAdg functionality."""

    def test_skill_extractor_node_types_adg_imports(self):
        """Test skill_extractor_node_types_adg module imports."""
        from agentic_core import skill_extractor_node_types_adg
        assert skill_extractor_node_types_adg is not None

    def test_skill_extractor_node_types_adg_class(self):
        """Test SkillExtractorNodeTypesAdg class exists."""
        from agentic_core import SkillExtractorNodeTypesAdg
        assert SkillExtractorNodeTypesAdg is not None

    def test_skill_extractor_node_types_adg_callable(self):
        """Test skill_extractor_node_types_adg functions are callable."""
        from agentic_core import validate_skill_extractor_node_types_adg
        assert callable(validate_skill_extractor_node_types_adg)
