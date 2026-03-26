"""ADG-driven tests for agentic_core/L4_state/enforcement/neo4j_store.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L4_state.enforcement.neo4j_store  # noqa: F401


def test_module_importable():
    import agentic_core.L4_state.enforcement.neo4j_store  # noqa: F401
    """Module neo4j_store must be importable."""
    assert agentic_core.L4_state.enforcement.neo4j_store is not None
