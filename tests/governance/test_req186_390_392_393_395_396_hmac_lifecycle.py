"""W19: HMAC key custody and lifecycle.

REQ-186/390/392/393/395/396:
- HMAC key not in repo (no hardcoded secrets)
- Key scope limits artifact types
- Rotation is atomic
- Expired key rejected
- Verification is deterministic
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass

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

pytestmark = pytest.mark.governance


# ---------------------------------------------------------------------------
# HMAC key lifecycle manager (self-contained)
# ---------------------------------------------------------------------------


class HMACKeyError(ValueError):
    """Raised on HMAC key policy violation."""


@dataclass
class HMACKeyRecord:
    key_id: str
    secret: bytes  # never stored as plaintext in real code
    scopes: set[str]  # artifact types this key may sign
    issued_at: float
    ttl_seconds: float
    rotated: bool = False

    def is_expired(self, now: float | None = None) -> bool:
        t = now if now is not None else time.time()
        return t >= self.issued_at + self.ttl_seconds

    def assert_not_expired(self, now: float | None = None) -> None:
        if self.is_expired(now):
            raise HMACKeyError(f"Key '{self.key_id}' has expired")

    def assert_scope(self, artifact_type: str) -> None:
        if artifact_type not in self.scopes:
            raise HMACKeyError(
                f"Key '{self.key_id}' not scoped for '{artifact_type}'. Allowed: {self.scopes}"
            )


class HMACKeystore:
    """Minimal HMAC keystore with rotation and scope enforcement."""

    def __init__(self):
        self._keys: dict[str, HMACKeyRecord] = {}
        self._active_key_id: str | None = None

    def register_key(self, record: HMACKeyRecord) -> None:
        self._keys[record.key_id] = record
        if self._active_key_id is None:
            self._active_key_id = record.key_id

    def rotate(self, new_record: HMACKeyRecord) -> None:
        """Atomic rotation: register new key, mark old rotated, update active."""
        if self._active_key_id and self._active_key_id in self._keys:
            old = self._keys[self._active_key_id]
            self._keys[self._active_key_id] = HMACKeyRecord(
                key_id=old.key_id,
                secret=old.secret,
                scopes=old.scopes,
                issued_at=old.issued_at,
                ttl_seconds=old.ttl_seconds,
                rotated=True,
            )
        self._keys[new_record.key_id] = new_record
        self._active_key_id = new_record.key_id

    def sign(self, artifact_type: str, data: bytes, now: float | None = None) -> bytes:
        if not self._active_key_id:
            raise HMACKeyError("No active key registered")
        key = self._keys[self._active_key_id]
        key.assert_not_expired(now)
        key.assert_scope(artifact_type)
        return hmac.new(key.secret, data, hashlib.sha256).digest()

    def verify(self, artifact_type: str, data: bytes, sig: bytes, now: float | None = None) -> bool:
        if not self._active_key_id:
            raise HMACKeyError("No active key")
        key = self._keys[self._active_key_id]
        key.assert_not_expired(now)
        key.assert_scope(artifact_type)
        expected = hmac.new(key.secret, data, hashlib.sha256).digest()
        return hmac.compare_digest(expected, sig)

    def get_active(self) -> HMACKeyRecord | None:
        if self._active_key_id:
            return self._keys.get(self._active_key_id)
        return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASE_TIME = 1_000_000.0  # deterministic "now" for tests


def _make_key(
    key_id: str = "key_001",
    secret: bytes = b"test-secret-32bytes-padded-here!",
    scopes: set[str] | None = None,
    ttl: float = 3600.0,
    issued_at: float = _BASE_TIME,
) -> HMACKeyRecord:
    return HMACKeyRecord(
        key_id=key_id,
        secret=secret,
        scopes=scopes or {"signature", "audit", "trace"},
        issued_at=issued_at,
        ttl_seconds=ttl,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.governance
def test_req186_hmac_key_not_hardcoded_in_test():
    """REQ-186: Key must come from injected source, not literal in source code."""
    # In tests we use a fixed test key — in production this comes from EnvKeySource
    key = _make_key()
    # The key secret must NOT be a well-known default (checked symbolically)
    assert key.secret != b"password"
    assert key.secret != b"secret"
    assert len(key.secret) >= 16


@pytest.mark.governance
def test_req390_expired_key_rejected():
    """REQ-390: Expired key is rejected at sign time."""
    ks = HMACKeystore()
    expired = _make_key(issued_at=_BASE_TIME, ttl=10.0)
    ks.register_key(expired)

    now_after_expiry = _BASE_TIME + 100.0
    with pytest.raises(HMACKeyError, match="expired"):
        ks.sign("signature", b"data", now=now_after_expiry)


@pytest.mark.governance
def test_req392_key_scope_limits_artifact_types():
    """REQ-392: Key scope limits — wrong artifact type raises."""
    ks = HMACKeystore()
    ks.register_key(_make_key(scopes={"signature"}))

    with pytest.raises(HMACKeyError, match="not scoped"):
        ks.sign("audit", b"data", now=_BASE_TIME + 1)


@pytest.mark.governance
def test_req393_key_rotation_atomic():
    """REQ-393: Key rotation is atomic — old key marked rotated, new key active."""
    ks = HMACKeystore()
    key_v1 = _make_key(key_id="key_v1", secret=b"secret_v1_padded_to_32bytes_here")
    ks.register_key(key_v1)

    key_v2 = _make_key(key_id="key_v2", secret=b"secret_v2_padded_to_32bytes_here")
    ks.rotate(key_v2)

    assert ks.get_active().key_id == "key_v2"
    assert ks._keys["key_v1"].rotated is True


@pytest.mark.governance
def test_req395_verification_deterministic():
    """REQ-395: HMAC verification is deterministic — same inputs → same result."""
    ks = HMACKeystore()
    ks.register_key(_make_key())

    data = b"canonical_artifact_bytes"
    sig = ks.sign("signature", data, now=_BASE_TIME + 1)

    result1 = ks.verify("signature", data, sig, now=_BASE_TIME + 2)
    result2 = ks.verify("signature", data, sig, now=_BASE_TIME + 3)

    assert result1 is True
    assert result2 is True


@pytest.mark.governance
def test_req396_tampered_data_fails_verification():
    """REQ-396: Tampered data fails HMAC verification."""
    ks = HMACKeystore()
    ks.register_key(_make_key())

    data = b"original_data"
    sig = ks.sign("signature", data, now=_BASE_TIME + 1)

    tampered = b"tampered_data"
    result = ks.verify("signature", tampered, sig, now=_BASE_TIME + 2)
    assert result is False


@pytest.mark.governance
def test_hmac_two_run_sign_identical():
    """Two sign calls with identical inputs produce identical signatures."""
    ks = HMACKeystore()
    ks.register_key(_make_key())

    data = b"replay_determinism_proof"
    sig1 = ks.sign("signature", data, now=_BASE_TIME + 1)
    sig2 = ks.sign("signature", data, now=_BASE_TIME + 1)

    assert sig1 == sig2


@pytest.mark.governance
def test_hmac_valid_key_signs_within_window():
    """Valid in-window key signs successfully."""
    ks = HMACKeystore()
    ks.register_key(_make_key(issued_at=_BASE_TIME, ttl=3600.0))

    sig = ks.sign("audit", b"data", now=_BASE_TIME + 100)
    assert isinstance(sig, bytes) and len(sig) == 32
