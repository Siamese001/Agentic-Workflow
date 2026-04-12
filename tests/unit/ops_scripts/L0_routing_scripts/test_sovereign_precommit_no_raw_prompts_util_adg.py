"""Test SovereignPrecommitNoRawPromptsUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereignPrecommitNoRawPromptsUtilAdg:
    """Test SovereignPrecommitNoRawPromptsUtilAdg functionality."""

    def test_sovereign_precommit_no_raw_prompts_util_adg_imports(self):
        """Test sovereign_precommit_no_raw_prompts_util_adg module imports."""
        from agentic_core import sovereign_precommit_no_raw_prompts_util_adg

        assert sovereign_precommit_no_raw_prompts_util_adg is not None

    def test_sovereign_precommit_no_raw_prompts_util_adg_class(self):
        """Test SovereignPrecommitNoRawPromptsUtilAdg class exists."""
        from agentic_core import SovereignPrecommitNoRawPromptsUtilAdg

        assert SovereignPrecommitNoRawPromptsUtilAdg is not None

    def test_sovereign_precommit_no_raw_prompts_util_adg_callable(self):
        """Test sovereign_precommit_no_raw_prompts_util_adg functions are callable."""
        from agentic_core import validate_sovereign_precommit_no_raw_prompts_util_adg

        assert callable(validate_sovereign_precommit_no_raw_prompts_util_adg)
