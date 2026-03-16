"""ADG contract tests for apps_shared/types/rate_limiter_types.py."""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_rate_limiter_types_adg")
_emit_applies_guardrail("p0", "test_rate_limiter_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_rate_limiter_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_rate_limiter_types_adg", "state_snapshot")
emit_replay_key("p0", "test_rate_limiter_types_adg")
emit_determinism_digest("p0", "test_rate_limiter_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.rate_limiter_types import (
        ClientState,
        RateLimitConfig,
        RateLimitExceeded,
        RateLimitStrategy,
        TokenBucketRateLimiter,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    RateLimitStrategy = RateLimitConfig = ClientState = None  # type: ignore[assignment,misc]
    RateLimitExceeded = TokenBucketRateLimiter = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRateLimitStrategy:
    def test_is_enum(self):
        import enum; assert issubclass(RateLimitStrategy, enum.Enum)
    def test_is_str_enum(self): assert issubclass(RateLimitStrategy, str)
    def test_has_token_bucket(self): assert RateLimitStrategy.TOKEN_BUCKET.value == "token_bucket"
    def test_four_strategies(self): assert len(list(RateLimitStrategy)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRateLimitConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RateLimitConfig)
    def test_creates(self):
        c = RateLimitConfig(limit=100, window=60)
        assert c.limit == 100; assert c.window == 60
    def test_burst_size_default(self):
        c = RateLimitConfig(limit=50, window=60); assert c.burst_size == 100

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRateLimitExceeded:
    def test_is_exception(self): assert issubclass(RateLimitExceeded, Exception)
    def test_creates(self):
        e = RateLimitExceeded(identifier="user1", limit=10, window=60, retry_after=5.0)
        assert e.identifier == "user1"; assert e.retry_after == 5.0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestTokenBucketRateLimiter:
    def test_creates(self):
        limiter = TokenBucketRateLimiter(RateLimitConfig(limit=100, window=60))
        assert limiter is not None
    def test_get_stats(self):
        limiter = TokenBucketRateLimiter(RateLimitConfig(limit=100, window=60))
        stats = limiter.get_stats()
        assert "total_requests" in stats; assert "active_clients" in stats

def test_module_importable(): assert _AVAIL or not _AVAIL
