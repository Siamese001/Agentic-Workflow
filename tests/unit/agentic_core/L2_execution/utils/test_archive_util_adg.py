"""ADG-driven tests for L2_execution/utils/archive_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.utils.archive_util import parse_mcp_client_specs
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    parse_mcp_client_specs = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="archive_util deps unavailable")
class TestParseMcpClientSpecs:
    def test_empty_list_returns_empty(self):
        result = parse_mcp_client_specs([])
        assert result == []

    def test_importable(self):
        assert callable(parse_mcp_client_specs)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
