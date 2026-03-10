"""REQ-087: MODIFY_DIFF must invalidate all prior signatures on the plan artifact."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.enforcement.crypto_trust_contracts import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    VerificationError,
    sign_artifact,
    verify_signature,
)
from agentic_core.L0_routing.types.crypto_trust_types import (
    DeterministicTestEnclave,
    KeyRecord,
    KeyStatus,
    TrustRoot,
)

_KEY_ID = "req087-test-key"
_KEY_SECRET = b"req087-fixed-secret-32b-padding!!"


def _make_trust_root() -> TrustRoot:
    return TrustRoot(
        keys=(
            KeyRecord(
                key_id=_KEY_ID,
                public_key=_KEY_SECRET,
                created_tick=0,
                status=KeyStatus.ACTIVE,
            ),
        )
    )


@pytest.mark.governance
def test_modify_diff_invalidates_old_signature() -> None:
    """Old envelope on original bytes MUST raise VerificationError on modified bytes."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)

    original_bytes = b'{"action":"plan","payload":"initial_plan","trace_id":"REQ087-T1"}'
    envelope = sign_artifact(original_bytes, _KEY_ID, enclave, "REQ087-T1", 1)

    modified_bytes = b'{"action":"plan","payload":"modified_plan","trace_id":"REQ087-T1"}'

    with pytest.raises(VerificationError):
        verify_signature(modified_bytes, envelope, trust_root, enclave)


@pytest.mark.governance
def test_modify_diff_new_signature_verifies() -> None:
    """After MODIFY_DIFF a freshly computed signature MUST verify against modified bytes."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)

    original_bytes = b'{"action":"plan","payload":"initial_plan","trace_id":"REQ087-T2"}'
    sign_artifact(original_bytes, _KEY_ID, enclave, "REQ087-T2", 1)

    modified_bytes = b'{"action":"plan","payload":"modified_plan","trace_id":"REQ087-T2"}'
    new_envelope = sign_artifact(modified_bytes, _KEY_ID, enclave, "REQ087-T2", 2)

    assert verify_signature(modified_bytes, new_envelope, trust_root, enclave)


@pytest.mark.governance
def test_single_byte_diff_invalidates_signature() -> None:
    """Even a single-byte change MUST invalidate the prior signature (hash avalanche)."""
    trust_root = _make_trust_root()
    enclave = DeterministicTestEnclave(trust_root)

    base = b"plan:version1"
    envelope = sign_artifact(base, _KEY_ID, enclave, "REQ087-T3", 1)

    mutated = b"plan:version2"
    with pytest.raises(VerificationError):
        verify_signature(mutated, envelope, trust_root, enclave)
