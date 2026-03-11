"""Wave 5.2: Replay artifact sealing tests.

Validates:
- replay_hash computed on create
- integrity_verified set True on create
- Tampered raw_response_bytes fails integrity check
- Tampered model_version fails integrity check
- Valid bundle passes integrity check
- verify_replay_integrity function
"""

import pytest

from agentic_core.L2_execution.types.llm_replay_types import (
    ReplayBundle,
    verify_replay_integrity,
)

pytestmark = pytest.mark.governance

PROMPT = b"test prompt"
RESPONSE = b"test response"


class TestReplayHashComputed:
    """replay_hash must be set on create."""

    def test_replay_hash_is_sha256(self):
        bundle = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        assert len(bundle.replay_hash) == 64
        assert all(c in "0123456789abcdef" for c in bundle.replay_hash)

    def test_integrity_verified_true_on_create(self):
        bundle = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        assert bundle.integrity_verified is True

    def test_replay_hash_deterministic(self):
        a = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        b = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        assert a.replay_hash == b.replay_hash


class TestTamperDetection:
    """Tampered bundles must fail integrity check."""

    def test_tampered_response_fails(self):
        good = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        tampered = ReplayBundle(
            model_version=good.model_version,
            tokenizer_version=good.tokenizer_version,
            raw_prompt_bytes=good.raw_prompt_bytes,
            raw_response_bytes=b"TAMPERED",
            provider_checksum=good.provider_checksum,
            replay_hash=good.replay_hash,
            integrity_verified=good.integrity_verified,
        )
        assert not verify_replay_integrity(tampered)

    def test_tampered_model_version_fails(self):
        good = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        tampered = ReplayBundle(
            model_version="TAMPERED",
            tokenizer_version=good.tokenizer_version,
            raw_prompt_bytes=good.raw_prompt_bytes,
            raw_response_bytes=good.raw_response_bytes,
            provider_checksum=good.provider_checksum,
            replay_hash=good.replay_hash,
            integrity_verified=good.integrity_verified,
        )
        assert not verify_replay_integrity(tampered)

    def test_valid_bundle_passes(self):
        bundle = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        assert verify_replay_integrity(bundle)
