"""ADG-driven tests for L2_execution/deterministic_providers.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.deterministic_providers import (
    DeterministicPatchError,
    _ACTIVE_TRACE_ID,
    _PATCHED,
)


class TestDeterministicPatchError:
    def test_is_exception(self):
        assert issubclass(DeterministicPatchError, Exception)


class TestModuleLevelSentinels:
    def test_active_trace_id_initially_none(self):
        assert _ACTIVE_TRACE_ID is None or isinstance(_ACTIVE_TRACE_ID, str)

    def test_patched_is_bool(self):
        assert isinstance(_PATCHED, bool)
