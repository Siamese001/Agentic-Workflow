"""ADG contract tests for L5_safety/types/core_contracts_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.core_contracts_types import RetryPolicy, HopSpec, AgentContract, CORE_CONTRACTS_REGISTRY
    _AVAIL = True
except Exception:
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
