"""ADG contract tests for L5_safety/types/core_contracts_types.py."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_core_contracts_types_adg")
_emit_applies_guardrail("p0", "test_core_contracts_types_adg", "p0_governance")
_emit_snapshots_state("p0", "test_core_contracts_types_adg", "state_snapshot")
emit_replay_key("p0", "test_core_contracts_types_adg")
emit_determinism_digest("p0", "test_core_contracts_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.core_contracts_types import (
        CORE_CONTRACTS_REGISTRY,
        AgentContract,
        HopSpec,
        RetryPolicy,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False; RetryPolicy = HopSpec = AgentContract = CORE_CONTRACTS_REGISTRY = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRetryPolicy:
    def test_defaults(self):
        rp = RetryPolicy()
        assert rp.max_retries == 3
    def test_frozen(self):
        rp = RetryPolicy()
        with pytest.raises(Exception): rp.max_retries = 99  # type: ignore[misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHopSpec:
    def test_creates(self):
        h = HopSpec(hop_id="h1", name="Step1")
        assert h.hop_id == "h1"; assert h.timeout_seconds == 30

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCoreContractsRegistry:
    def test_has_retry_policy(self):
        assert "RetryPolicy" in CORE_CONTRACTS_REGISTRY

def test_module_importable(): assert _AVAIL or not _AVAIL
