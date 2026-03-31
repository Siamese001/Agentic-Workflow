"""Test GuardianPromptAssemblyExclusivity functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianPromptAssemblyExclusivity:
    """Test GuardianPromptAssemblyExclusivity functionality."""

    def test_guardian_prompt_assembly_exclusivity_imports(self):
        """Test guardian_prompt_assembly_exclusivity module imports."""
        from agentic_core import guardian_prompt_assembly_exclusivity
        assert guardian_prompt_assembly_exclusivity is not None

    def test_guardian_prompt_assembly_exclusivity_class(self):
        """Test GuardianPromptAssemblyExclusivity class exists."""
        from agentic_core import GuardianPromptAssemblyExclusivity
        assert GuardianPromptAssemblyExclusivity is not None

    def test_guardian_prompt_assembly_exclusivity_callable(self):
        """Test guardian_prompt_assembly_exclusivity functions are callable."""
        from agentic_core import validate_guardian_prompt_assembly_exclusivity
        assert callable(validate_guardian_prompt_assembly_exclusivity)
