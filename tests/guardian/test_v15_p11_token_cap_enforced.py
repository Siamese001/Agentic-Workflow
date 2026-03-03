"""V15 P11 Wave 1.8 — TokenCapArtifact Enforcement at LLM Gateway.

Proves:
- Missing TokenCapArtifact aborts when V15 enforced.
- Denied TokenCapArtifact aborts when V15 enforced.
- Allowed TokenCapArtifact lets the call path proceed.
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest

from agentic_core.L0_routing.types.guardian_contract_types import V15HardFailAbort
from agentic_core.L0_routing.types.routing_artifact_types import (
    TokenCapArtifact,
    TokenGateResult,
)
from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
    SovereignLLMGateway,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SENTINEL_RESULT = {"content": "sentinel", "tokens": 0, "provider": "openai", "model": "test"}


def _make_token_cap(
    gate_result: TokenGateResult = TokenGateResult.ALLOW,
    trace_id: str = "TC-TEST-001",
) -> TokenCapArtifact:
    return TokenCapArtifact(
        trace_id=trace_id,
        policy_hash="deadbeef",
        budget_limit=1000,
        tokens_requested=100,
        gate_result=gate_result,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_singleton():
    """Ensure each test gets a fresh gateway instance."""
    SovereignLLMGateway.reset_instance()
    yield
    SovereignLLMGateway.reset_instance()


class TestTokenCapEnforced:
    """Integration tests: TokenCapArtifact gate in SovereignLLMGateway."""

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    async def test_missing_token_cap_aborts_when_enforced(self):
        """generate() with no token_cap must raise V15HardFailAbort."""
        gw = SovereignLLMGateway()
        with pytest.raises(V15HardFailAbort, match="TokenCapArtifact missing"):
            await gw.generate(prompt="test", token_cap=None)

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    async def test_denied_token_cap_aborts_when_enforced(self):
        """generate() with gate_result=DENY must raise V15HardFailAbort."""
        gw = SovereignLLMGateway()
        cap = _make_token_cap(gate_result=TokenGateResult.DENY)
        with pytest.raises(V15HardFailAbort, match="TokenCapArtifact denied"):
            await gw.generate(prompt="test", token_cap=cap)

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"V15_ENFORCEMENT": "1"})
    async def test_allow_token_cap_allows_call_path(self):
        """generate() with gate_result=ALLOW must reach _call_provider."""
        gw = SovereignLLMGateway()
        cap = _make_token_cap(gate_result=TokenGateResult.ALLOW)

        with patch.object(
            gw,
            "_call_provider",
            new_callable=AsyncMock,
            return_value=SENTINEL_RESULT,
        ):
            result = await gw.generate(prompt="test", token_cap=cap)

        assert result == SENTINEL_RESULT

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"V15_ENFORCEMENT": "0"})
    async def test_no_enforcement_skips_gate(self):
        """When V15 not enforced, missing token_cap must not abort."""
        gw = SovereignLLMGateway()

        with patch.object(
            gw,
            "_call_provider",
            new_callable=AsyncMock,
            return_value=SENTINEL_RESULT,
        ):
            result = await gw.generate(prompt="test", token_cap=None)

        assert result == SENTINEL_RESULT
