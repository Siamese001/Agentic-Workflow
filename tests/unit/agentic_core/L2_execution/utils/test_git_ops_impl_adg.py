"""Test GitOpsImplAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGitOpsImplAdg:
    """Test GitOpsImplAdg functionality."""

    def test_git_ops_impl_adg_imports(self):
        """Test git_ops_impl_adg module imports."""
        from agentic_core import git_ops_impl_adg
        assert git_ops_impl_adg is not None

    def test_git_ops_impl_adg_class(self):
        """Test GitOpsImplAdg class exists."""
        from agentic_core import GitOpsImplAdg
        assert GitOpsImplAdg is not None

    def test_git_ops_impl_adg_callable(self):
        """Test git_ops_impl_adg functions are callable."""
        from agentic_core import validate_git_ops_impl_adg
        assert callable(validate_git_ops_impl_adg)
