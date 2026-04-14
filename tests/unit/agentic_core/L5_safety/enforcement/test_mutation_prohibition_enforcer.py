"""Test MutationProhibitionEnforcer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMutationProhibitionEnforcer:
    """Test MutationProhibitionEnforcer functionality."""

    def test_mutation_prohibition_enforcer_imports(self):
        """Test mutation_prohibition_enforcer module imports."""
        from agentic_core import mutation_prohibition_enforcer

        assert mutation_prohibition_enforcer is not None

    def test_mutation_prohibition_enforcer_class(self):
        """Test MutationProhibitionEnforcer class exists."""
        from agentic_core import MutationProhibitionEnforcer

        assert MutationProhibitionEnforcer is not None

    def test_mutation_prohibition_enforcer_callable(self):
        """Test mutation_prohibition_enforcer functions are callable."""
        from agentic_core import validate_mutation_prohibition_enforcer

        assert callable(validate_mutation_prohibition_enforcer)

    def test_validate_mutating_mode_read_only_raises(self):
        """Read-only mode must be rejected by _validate_mutating_mode."""
        from agentic_core.L5_safety.enforcement.mutation_prohibition_enforcer import _validate_mutating_mode

        with pytest.raises(ValueError, match="safe_open_write requires a mutating mode"):
            _validate_mutating_mode("r")

    def test_validate_mutating_mode_write_passes(self):
        """Write mode must not raise."""
        from agentic_core.L5_safety.enforcement.mutation_prohibition_enforcer import _validate_mutating_mode

        _validate_mutating_mode("w")  # must not raise

    def test_validate_mutating_mode_read_binary_raises(self):
        """Binary read mode must also be rejected."""
        from agentic_core.L5_safety.enforcement.mutation_prohibition_enforcer import _validate_mutating_mode

        with pytest.raises(ValueError):
            _validate_mutating_mode("rb")
