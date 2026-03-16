"""ADG-driven tests for L5_safety/validators/context_validator.py — fan_in=1."""
from __future__ import annotations

import time

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_context_validator_adg")
_emit_applies_guardrail("p0", "test_context_validator_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_context_validator_adg", "policy_binding")
_emit_snapshots_state("p0", "test_context_validator_adg", "state_snapshot")
emit_replay_key("p0", "test_context_validator_adg")
emit_determinism_digest("p0", "test_context_validator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_FIXED_TS = 9999999999.0  # far-future: ensures is_expired() returns False

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.validators.context_validator import CacheEntry


class TestCacheEntry:
    def test_creates(self):
        entry = CacheEntry(
            key="test:key",
            value={"result": True},
            timestamp=_FIXED_TS,
            ttl=60,
            agent="TestAgent",
        )
        assert entry.key == "test:key"

    def test_not_expired_fresh(self):
        entry = CacheEntry(
            key="k",
            value="v",
            timestamp=_FIXED_TS,
            ttl=60,
            agent="A",
        )
        assert entry.is_expired() is False

    def test_expired_old_timestamp(self):
        entry = CacheEntry(
            key="k",
            value="v",
            timestamp=time.time() - 200,
            ttl=60,
            agent="A",
        )
        assert entry.is_expired() is True

    def test_value_preserved(self):
        entry = CacheEntry(
            key="k",
            value={"data": [1, 2, 3]},
            timestamp=_FIXED_TS,
            ttl=30,
            agent="B",
        )
        assert entry.value == {"data": [1, 2, 3]}
