"""Test ADG node types functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.adg.schema import NodeType
from agentic_core.adg.schema import NODE_TYPES


@pytest.mark.unit
class TestAdgNodeTypes:
    """Test ADG node types functionality."""



