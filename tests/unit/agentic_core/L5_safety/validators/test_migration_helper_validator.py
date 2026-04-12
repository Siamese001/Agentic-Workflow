"""Test MigrationHelperValidator functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMigrationHelperValidator:
    """Test MigrationHelperValidator functionality."""

    def test_migration_helper_validator_imports(self):
        """Test migration_helper_validator module imports."""
        from agentic_core import migration_helper_validator

        assert migration_helper_validator is not None

    def test_migration_helper_validator_class(self):
        """Test MigrationHelperValidator class exists."""
        from agentic_core import MigrationHelperValidator

        assert MigrationHelperValidator is not None

    def test_migration_helper_validator_callable(self):
        """Test migration_helper_validator functions are callable."""
        from agentic_core import validate_migration_helper_validator

        assert callable(validate_migration_helper_validator)
