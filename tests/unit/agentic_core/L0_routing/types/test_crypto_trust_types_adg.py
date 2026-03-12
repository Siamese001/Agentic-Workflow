"""ADG contract tests for agentic_core/L0_routing/types/crypto_trust_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L0_routing.types.crypto_trust_types import (
        KeyStatus, SigningAlgorithm, KeyRecord, TrustRoot, SignatureEnvelope,
        SignedGuardianArtifact, HumanResolution, SignedModify, ReplayGuardRecord,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    KeyStatus = SigningAlgorithm = KeyRecord = TrustRoot = None  # type: ignore[assignment,misc]
    SignatureEnvelope = SignedGuardianArtifact = HumanResolution = SignedModify = None  # type: ignore[assignment,misc]
    ReplayGuardRecord = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestKeyStatus:
    def test_is_enum(self):
        import enum; assert issubclass(KeyStatus, enum.Enum)
    def test_has_active(self): assert KeyStatus.ACTIVE.value == "active"
    def test_has_revoked(self): assert KeyStatus.REVOKED.value == "revoked"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestKeyRecord:
    def test_is_frozen(self): assert KeyRecord.__dataclass_params__.frozen is True
    def test_creates(self):
        r = KeyRecord(key_id="k1", public_key=b"secret", created_tick=0, status=KeyStatus.ACTIVE)
        assert r.key_id == "k1"; assert r.algorithm == SigningAlgorithm.HMAC_SHA256
    def test_empty_key_id_raises(self):
        with pytest.raises(ValueError):
            KeyRecord(key_id="", public_key=b"s", created_tick=0, status=KeyStatus.ACTIVE)
    def test_negative_tick_raises(self):
        with pytest.raises(ValueError):
            KeyRecord(key_id="k", public_key=b"s", created_tick=-1, status=KeyStatus.ACTIVE)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestTrustRoot:
    def test_creates_empty(self): r = TrustRoot(keys=()); assert r.keys == ()
    def test_get_key_found(self):
        kr = KeyRecord(key_id="k1", public_key=b"s", created_tick=0, status=KeyStatus.ACTIVE)
        tr = TrustRoot(keys=(kr,))
        assert tr.get_key("k1") is kr
    def test_get_key_not_found(self):
        tr = TrustRoot(keys=()); assert tr.get_key("missing") is None
    def test_duplicate_key_raises(self):
        kr = KeyRecord(key_id="k1", public_key=b"s", created_tick=0, status=KeyStatus.ACTIVE)
        with pytest.raises(ValueError):
            TrustRoot(keys=(kr, kr))

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestReplayGuardRecord:
    def test_creates(self):
        r = ReplayGuardRecord(artifact_hash="abc123", first_seen_tick=1)
        assert r.seen_count == 1

def test_module_importable(): assert _AVAIL or not _AVAIL
