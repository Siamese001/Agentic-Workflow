"""Test memory MCP adapter functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMemoryMcpAdapter:
    """Test memory MCP adapter functionality."""
