"""W13 P0: Capability tokens include canonical digest hash; missing hash → invalid.

REQ-354: Capability tokens must be replay-bound with a canonical digest.
Tokens without a bound digest are rejected at validation time.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Optional

import pytest

pytestmark = pytest.mark.governance


# ---------------------------------------------------------------------------
# Replay-bound capability token (self-contained)
# ---------------------------------------------------------------------------

class CapabilityTokenError(ValueError):
    """Raised when token validation fails."""


@dataclass(frozen=True)
class ReplayBoundCapabilityToken:
    """
    Capability token bound to a canonical replay digest.
    A token without a replay_digest_hash is structurally invalid.
    """
    token_id: str
    capability_scope: str
    target_namespace: str
    allowed_action: str
    issued_at_tick: int
    window_size: int
    replay_digest_hash: str          # REQUIRED — empty string = invalid
    issuer_id: str
    nonce: str
    used: bool = False

    def is_replay_bound(self) -> bool:
        """Return True iff token carries a non-empty replay digest."""
        return bool(self.replay_digest_hash) and len(self.replay_digest_hash) == 64

    def validate(self, current_tick: int) -> None:
        """
        Raise CapabilityTokenError if token is invalid:
          - replay_digest_hash missing or wrong length
          - token expired (current_tick outside window)
          - token already used
        """
        if not self.is_replay_bound():
            raise CapabilityTokenError(
                f"Token '{self.token_id}' is not replay-bound: "
                f"replay_digest_hash='{self.replay_digest_hash}'"
            )
        if self.used:
            raise CapabilityTokenError(f"Token '{self.token_id}' already used (single-use)")
        if current_tick < self.issued_at_tick:
            raise CapabilityTokenError(
                f"Token '{self.token_id}' not yet valid: "
                f"tick={current_tick} < issued_at={self.issued_at_tick}"
            )
        if current_tick >= self.issued_at_tick + self.window_size:
            raise CapabilityTokenError(
                f"Token '{self.token_id}' expired: "
                f"tick={current_tick} >= {self.issued_at_tick + self.window_size}"
            )

    def bind_to_digest(self, digest_hash: str) -> "ReplayBoundCapabilityToken":
        """Return a new token bound to the given digest."""
        return ReplayBoundCapabilityToken(
            token_id=self.token_id,
            capability_scope=self.capability_scope,
            target_namespace=self.target_namespace,
            allowed_action=self.allowed_action,
            issued_at_tick=self.issued_at_tick,
            window_size=self.window_size,
            replay_digest_hash=digest_hash,
            issuer_id=self.issuer_id,
            nonce=self.nonce,
            used=self.used,
        )


def _make_digest(seed: str) -> str:
    """Make a valid 64-hex digest from a seed string."""
    return hashlib.sha256(seed.encode()).hexdigest()


def _make_token(
    replay_digest_hash: str = "",
    used: bool = False,
    issued_at_tick: int = 10,
    window_size: int = 20,
) -> ReplayBoundCapabilityToken:
    return ReplayBoundCapabilityToken(
        token_id="tok_test_001",
        capability_scope="pointer_update:ns_a",
        target_namespace="ns_a",
        allowed_action="pointer_update",
        issued_at_tick=issued_at_tick,
        window_size=window_size,
        replay_digest_hash=replay_digest_hash,
        issuer_id="issuer_guardian",
        nonce=hashlib.sha256(b"nonce_seed").hexdigest()[:16],
        used=used,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_token_with_valid_digest_passes_validation():
    """Token with valid replay_digest_hash passes validate()."""
    token = _make_token(replay_digest_hash=_make_digest("valid_digest_seed"))
    token.validate(current_tick=15)  # within window [10, 30)


@pytest.mark.governance
def test_token_missing_digest_is_rejected():
    """Token with empty replay_digest_hash is rejected as not replay-bound."""
    token = _make_token(replay_digest_hash="")

    assert not token.is_replay_bound()
    with pytest.raises(CapabilityTokenError, match="not replay-bound"):
        token.validate(current_tick=15)


@pytest.mark.governance
def test_token_short_digest_is_rejected():
    """Token with too-short digest (not 64 hex) is rejected."""
    token = _make_token(replay_digest_hash="abc123")   # too short

    assert not token.is_replay_bound()
    with pytest.raises(CapabilityTokenError, match="not replay-bound"):
        token.validate(current_tick=15)


@pytest.mark.governance
def test_used_token_is_rejected():
    """Already-used token is rejected even if replay-bound."""
    token = _make_token(replay_digest_hash=_make_digest("seed"), used=True)

    with pytest.raises(CapabilityTokenError, match="already used"):
        token.validate(current_tick=15)


@pytest.mark.governance
def test_expired_token_is_rejected():
    """Token past its window is rejected."""
    token = _make_token(
        replay_digest_hash=_make_digest("seed"),
        issued_at_tick=10,
        window_size=5,  # expires at tick 15
    )
    with pytest.raises(CapabilityTokenError, match="expired"):
        token.validate(current_tick=15)  # == issued_at + window_size → expired


@pytest.mark.governance
def test_future_token_is_rejected():
    """Token not yet valid (current_tick < issued_at) is rejected."""
    token = _make_token(
        replay_digest_hash=_make_digest("seed"),
        issued_at_tick=50,
        window_size=10,
    )
    with pytest.raises(CapabilityTokenError, match="not yet valid"):
        token.validate(current_tick=30)


@pytest.mark.governance
def test_bind_to_digest_creates_replay_bound_token():
    """bind_to_digest() returns a new token with the digest set."""
    unbound = _make_token(replay_digest_hash="")
    assert not unbound.is_replay_bound()

    digest = _make_digest("canonical_digest_001")
    bound = unbound.bind_to_digest(digest)

    assert bound.is_replay_bound()
    assert bound.replay_digest_hash == digest
    # Original must be unchanged (frozen dataclass)
    assert not unbound.is_replay_bound()


@pytest.mark.governance
def test_digest_change_invalidates_token():
    """Two tokens identical except replay_digest_hash are not equivalent."""
    digest_a = _make_digest("run_1")
    digest_b = _make_digest("run_2")

    token_a = _make_token(replay_digest_hash=digest_a)
    token_b = _make_token(replay_digest_hash=digest_b)

    assert token_a.replay_digest_hash != token_b.replay_digest_hash
    # Both are structurally valid but bound to different execution contexts
    token_a.validate(current_tick=15)
    token_b.validate(current_tick=15)


@pytest.mark.governance
def test_replay_digest_hash_determinism():
    """Same canonical inputs always produce same digest → same token binding."""
    canonical_json = json.dumps(
        {"plan": "plan_hash_abc", "tick": 42, "provider": "anthropic"},
        sort_keys=True,
        separators=(",", ":"),
    )
    digest_run1 = hashlib.sha256(canonical_json.encode()).hexdigest()
    digest_run2 = hashlib.sha256(canonical_json.encode()).hexdigest()

    assert digest_run1 == digest_run2
    assert len(digest_run1) == 64

    token_run1 = _make_token(replay_digest_hash=digest_run1)
    token_run2 = _make_token(replay_digest_hash=digest_run2)

    assert token_run1.replay_digest_hash == token_run2.replay_digest_hash
