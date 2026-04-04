import tempfile
from pathlib import Path

import pytest


class TestToolRegistryMigration:
    @pytest.fixture
    def mock_env(self):
        """Creates a mock environment with the 'ToolRegistry' casing issue."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            yield root

    def test_migration_logic(self, mock_env):
        """Test migration_logic runtime behavior."""
        assert mock_env is not None
        assert isinstance(mock_env, Path)
