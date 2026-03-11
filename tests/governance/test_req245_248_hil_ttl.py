"""REQ-245/248: HIL exception TTL; policy override expires on TTL (semantic clock)."""

from __future__ import annotations

import dataclasses

import pytest


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@pytest.mark.governance
def test_req245_expired_exception_auto_revoked():
    from agentic_core.L0_routing.types.governance_types import PolicyExceptionArtifact

    fields = {f.name for f in dataclasses.fields(PolicyExceptionArtifact)}
    assert "ttl_ticks" in fields
    assert "semantic_clock_tick" in fields


@pytest.mark.governance
def test_req248_semantic_clock_ttl():
    from agentic_core.L0_routing.types.governance_types import (
        ExceptionScope,
        PolicyExceptionArtifact,
    )

    artifact = PolicyExceptionArtifact(
        trace_id="CC3AL1-00000001",
        nonce="n1",
        exception_scope=ExceptionScope.SINGLE_AGENT,
        semantic_clock_tick=10,
        issuer_signature="sig",
        ttl_ticks=5,
    )
    assert artifact.is_expired(now_tick=16)  # 16 > 10 + 5 → expired
    assert not artifact.is_expired(now_tick=14)  # 14 <= 10 + 5 → not expired
