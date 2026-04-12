"""Test AdgCliCommands functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAdgCliCommands:
    """Test AdgCliCommands functionality."""

    def test_adg_cli_imports(self):
        """Test ADG CLI module imports."""
        from tools.adg import cli

        assert cli is not None

    def test_cli_command_class(self):
        """Test CLI command class exists."""
        from tools.adg.cli import CLICommand

        assert CLICommand is not None

    def test_execute_cli_command(self):
        """Test execute CLI command function."""
        from tools.adg.cli import execute_command

        assert callable(execute_command)
