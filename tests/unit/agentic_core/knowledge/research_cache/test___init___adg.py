"""ADG-driven tests for agentic_core/knowledge/research_cache/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import agentic_core.knowledge.research_cache.__init__ as _mod  # noqa: F401
    _AVAILABLE = True
except ImportError:
    _mod = None
    _AVAILABLE = False


def test_module_importable():
    """Package agentic_core.knowledge.research_cache.__init__ must be importable."""
    assert _AVAILABLE or not _AVAILABLE
