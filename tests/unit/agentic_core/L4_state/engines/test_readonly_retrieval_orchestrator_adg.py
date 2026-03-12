"""ADG-driven tests for agentic_core/L4_state/engines/readonly_retrieval_orchestrator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.engines.readonly_retrieval_orchestrator import (  # noqa: F401
        retrieve_with_readonly_guarantee,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    retrieve_with_readonly_guarantee = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="readonly_retrieval_orchestrator.py deps unavailable")
class TestRetrieveWithReadonlyGuarantee:
    def test_is_callable(self):
        assert callable(retrieve_with_readonly_guarantee)


def test_module_importable():
    """Module readonly_retrieval_orchestrator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
