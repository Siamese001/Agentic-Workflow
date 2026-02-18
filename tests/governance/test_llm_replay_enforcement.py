"""H3 governance tests: Provider-pinned LLM replay enforcement.

Validates:
- ReplayBundle immutability and checksum verification
- ReplayMode policy (production vs dev/test)
- DETERMINISTIC_INFERENCE labeled NON_AUTHORITATIVE
- RECORDED_OUTPUT replay returns stored bytes
- Production mode validation rejects DETERMINISTIC_INFERENCE
"""

import pytest

from agentic_core.L2_execution.types.llm_replay_types import (
    DEV_TEST_ALLOWED_MODES,
    PRODUCTION_ALLOWED_MODES,
    LLMReplayStrategy,
    ReplayBundle,
    ReplayMode,
    is_authoritative,
    mode_label,
    validate_production_mode,
)

pytestmark = pytest.mark.governance

SAMPLE_PROMPT = b"What is the capital of France?"
SAMPLE_RESPONSE = b"The capital of France is Paris."


class TestReplayBundle:
    """ReplayBundle must be frozen with valid checksum."""

    def test_bundle_is_frozen(self):
        bundle = ReplayBundle.create(
            model_version="gpt-4-0613",
            tokenizer_version="cl100k_base_v1",
            raw_prompt_bytes=SAMPLE_PROMPT,
            raw_response_bytes=SAMPLE_RESPONSE,
        )
        with pytest.raises(AttributeError):
            bundle.model_version = "tampered"  # type: ignore[misc]

    def test_checksum_is_sha256(self):
        bundle = ReplayBundle.create(
            model_version="gpt-4-0613",
            tokenizer_version="cl100k_base_v1",
            raw_prompt_bytes=SAMPLE_PROMPT,
            raw_response_bytes=SAMPLE_RESPONSE,
        )
        assert len(bundle.provider_checksum) == 64
        assert all(c in "0123456789abcdef" for c in bundle.provider_checksum)

    def test_checksum_deterministic(self):
        a = ReplayBundle.create(
            model_version="gpt-4-0613",
            tokenizer_version="cl100k_base_v1",
            raw_prompt_bytes=SAMPLE_PROMPT,
            raw_response_bytes=SAMPLE_RESPONSE,
        )
        b = ReplayBundle.create(
            model_version="gpt-4-0613",
            tokenizer_version="cl100k_base_v1",
            raw_prompt_bytes=SAMPLE_PROMPT,
            raw_response_bytes=SAMPLE_RESPONSE,
        )
        assert a.provider_checksum == b.provider_checksum

    def test_checksum_differs_with_different_versions(self):
        a = ReplayBundle.create(
            model_version="gpt-4-0613",
            tokenizer_version="cl100k_base_v1",
            raw_prompt_bytes=SAMPLE_PROMPT,
            raw_response_bytes=SAMPLE_RESPONSE,
        )
        b = ReplayBundle.create(
            model_version="gpt-4-0314",
            tokenizer_version="cl100k_base_v1",
            raw_prompt_bytes=SAMPLE_PROMPT,
            raw_response_bytes=SAMPLE_RESPONSE,
        )
        assert a.provider_checksum != b.provider_checksum

    def test_verify_checksum_passes(self):
        bundle = ReplayBundle.create(
            model_version="gpt-4-0613",
            tokenizer_version="cl100k_base_v1",
            raw_prompt_bytes=SAMPLE_PROMPT,
            raw_response_bytes=SAMPLE_RESPONSE,
        )
        assert bundle.verify_checksum() is True

    def test_verify_checksum_fails_on_tampered(self):
        bundle = ReplayBundle(
            model_version="gpt-4-0613",
            tokenizer_version="cl100k_base_v1",
            raw_prompt_bytes=SAMPLE_PROMPT,
            raw_response_bytes=SAMPLE_RESPONSE,
            provider_checksum="0" * 64,
        )
        assert bundle.verify_checksum() is False


class TestReplayModePolicy:
    """Mode policy must enforce production restrictions."""

    def test_production_only_allows_recorded_output(self):
        assert PRODUCTION_ALLOWED_MODES == frozenset({ReplayMode.RECORDED_OUTPUT})

    def test_dev_test_allows_both_modes(self):
        assert ReplayMode.RECORDED_OUTPUT in DEV_TEST_ALLOWED_MODES
        assert ReplayMode.DETERMINISTIC_INFERENCE in DEV_TEST_ALLOWED_MODES

    def test_validate_production_passes_recorded_output(self):
        validate_production_mode(ReplayMode.RECORDED_OUTPUT)

    def test_validate_production_rejects_deterministic(self):
        with pytest.raises(ValueError, match="not allowed in production"):
            validate_production_mode(ReplayMode.DETERMINISTIC_INFERENCE)


class TestGovernanceLabels:
    """DETERMINISTIC_INFERENCE must be NON_AUTHORITATIVE."""

    def test_recorded_output_is_authoritative(self):
        assert is_authoritative(ReplayMode.RECORDED_OUTPUT) is True

    def test_deterministic_is_not_authoritative(self):
        assert is_authoritative(ReplayMode.DETERMINISTIC_INFERENCE) is False

    def test_deterministic_label_non_authoritative(self):
        label = mode_label(ReplayMode.DETERMINISTIC_INFERENCE)
        assert label == "NON_AUTHORITATIVE"

    def test_recorded_output_label_authoritative(self):
        assert mode_label(ReplayMode.RECORDED_OUTPUT) == "AUTHORITATIVE"


class TestLLMReplayStrategy:
    """Strategy must replay correctly per mode."""

    def test_recorded_output_returns_stored_bytes(self):
        bundle = ReplayBundle.create(
            model_version="gpt-4-0613",
            tokenizer_version="cl100k_base_v1",
            raw_prompt_bytes=SAMPLE_PROMPT,
            raw_response_bytes=SAMPLE_RESPONSE,
        )
        strategy = LLMReplayStrategy(bundle=bundle, mode=ReplayMode.RECORDED_OUTPUT)
        assert strategy.replay() == SAMPLE_RESPONSE

    def test_deterministic_inference_raises(self):
        bundle = ReplayBundle.create(
            model_version="gpt-4-0613",
            tokenizer_version="cl100k_base_v1",
            raw_prompt_bytes=SAMPLE_PROMPT,
            raw_response_bytes=SAMPLE_RESPONSE,
        )
        strategy = LLMReplayStrategy(bundle=bundle, mode=ReplayMode.DETERMINISTIC_INFERENCE)
        with pytest.raises(NotImplementedError, match="NON_AUTHORITATIVE"):
            strategy.replay()

    def test_strategy_governance_label(self):
        bundle = ReplayBundle.create(
            model_version="gpt-4-0613",
            tokenizer_version="cl100k_base_v1",
            raw_prompt_bytes=SAMPLE_PROMPT,
            raw_response_bytes=SAMPLE_RESPONSE,
        )
        auth = LLMReplayStrategy(bundle=bundle, mode=ReplayMode.RECORDED_OUTPUT)
        non_auth = LLMReplayStrategy(bundle=bundle, mode=ReplayMode.DETERMINISTIC_INFERENCE)
        assert auth.is_authoritative is True
        assert non_auth.is_authoritative is False
        assert auth.governance_label == "AUTHORITATIVE"
        assert non_auth.governance_label == "NON_AUTHORITATIVE"
