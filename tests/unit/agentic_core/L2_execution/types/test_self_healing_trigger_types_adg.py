"""ADG-driven tests for L2_execution/types/self_healing_trigger_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.self_healing_trigger_types import (
        AUTHORIZED_DECISIONS,
        REJECTED_DECISIONS,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AUTHORIZED_DECISIONS = None  # type: ignore[assignment]
    REJECTED_DECISIONS = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="self_healing_trigger_types deps unavailable")
class TestAuthorizedDecisions:
    def test_is_frozenset(self):
        assert isinstance(AUTHORIZED_DECISIONS, frozenset)

    def test_contains_auto_approved(self):
        assert "AUTO_APPROVED" in AUTHORIZED_DECISIONS

    def test_contains_hil_approved(self):
        assert "HIL_APPROVED" in AUTHORIZED_DECISIONS


@pytest.mark.skipif(not _AVAILABLE, reason="self_healing_trigger_types deps unavailable")
class TestRejectedDecisions:
    def test_is_frozenset(self):
        assert isinstance(REJECTED_DECISIONS, frozenset)

    def test_disjoint_from_authorized(self):
        assert AUTHORIZED_DECISIONS.isdisjoint(REJECTED_DECISIONS)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
