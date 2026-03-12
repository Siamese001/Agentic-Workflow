"""ADG-driven tests for L2_execution/determinism/determinism_guard.py — fan_in=0."""
from __future__ import annotations

import uuid

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.determinism.determinism_guard import assert_no_uuid4


class TestAssertNoUuid4:
    def test_callable(self):
        assert callable(assert_no_uuid4)

    def test_passes_when_no_uuid4_called(self):
        with assert_no_uuid4():
            x = 1 + 1
        assert x == 2

    def test_raises_when_uuid4_called(self):
        with pytest.raises(RuntimeError, match="uuid.uuid4"):
            with assert_no_uuid4():
                uuid.uuid4()
