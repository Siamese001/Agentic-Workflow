"""
Test REQ-413: Provider Binding Determinism

Tests that determinism digest includes provider_id, model_id, gateway_version,
and semantic_clock_vector for reproducible LLM interactions.
"""

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

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L2_execution.enforcement.provider_binding_determinism import (
    ProviderBindingContext,
    compute_provider_binding_digest,
    extract_provider_context_from_request,
    verify_provider_binding_determinism,
)


class TestREQ413ProviderBindingDeterminism:
    """Test suite for REQ-413 Provider Binding Determinism."""

    def test_compute_provider_binding_digest_deterministic(self):
        """Test that provider binding digest is deterministic."""
        # Given
        provider_id = "openai"
        model_id = "gpt-4"
        gateway_version = "1.0.0"
        semantic_clock = SemanticClockSnapshot(tick=42, vector_clock=(("L0", 1), ("L2", 3), ("L5", 2)))

        # When
        digest1 = compute_provider_binding_digest(
            provider_id=provider_id,
            model_id=model_id,
            gateway_version=gateway_version,
            semantic_clock=semantic_clock,
        )

        digest2 = compute_provider_binding_digest(
            provider_id=provider_id,
            model_id=model_id,
            gateway_version=gateway_version,
            semantic_clock=semantic_clock,
        )

        # Then
        assert digest1 == digest2
        assert len(digest1) == 64  # SHA-256 hex length
        assert all(c in "0123456789abcdef" for c in digest1)

    def test_compute_provider_binding_digest_different_inputs(self):
        """Test that different inputs produce different digests."""
        # Given
        semantic_clock = SemanticClockSnapshot(tick=42, vector_clock=(("L0", 1), ("L2", 3), ("L5", 2)))

        # When
        digest_openai = compute_provider_binding_digest(
            provider_id="openai", model_id="gpt-4", gateway_version="1.0.0", semantic_clock=semantic_clock
        )

        digest_anthropic = compute_provider_binding_digest(
            provider_id="anthropic", model_id="gpt-4", gateway_version="1.0.0", semantic_clock=semantic_clock
        )

        # Then
        assert digest_openai != digest_anthropic

    def test_compute_provider_binding_digest_with_additional_context(self):
        """Test that additional context is included in digest."""
        # Given
        semantic_clock = SemanticClockSnapshot(tick=42, vector_clock=(("L0", 1), ("L2", 3)))
        additional_context = {"temperature": "0.7", "max_tokens": "1000"}

        # When
        digest_without_context = compute_provider_binding_digest(
            provider_id="openai", model_id="gpt-4", gateway_version="1.0.0", semantic_clock=semantic_clock
        )

        digest_with_context = compute_provider_binding_digest(
            provider_id="openai",
            model_id="gpt-4",
            gateway_version="1.0.0",
            semantic_clock=semantic_clock,
            additional_context=additional_context,
        )

        # Then
        assert digest_without_context != digest_with_context

    def test_verify_provider_binding_determinism_success(self):
        """Test successful verification of provider binding determinism."""
        # Given
        provider_id = "google"
        model_id = "gemini-pro"
        gateway_version = "1.0.0"
        semantic_clock = SemanticClockSnapshot(tick=100, vector_clock=(("L1", 5), ("L3", 2)))

        expected_digest = compute_provider_binding_digest(
            provider_id=provider_id,
            model_id=model_id,
            gateway_version=gateway_version,
            semantic_clock=semantic_clock,
        )

        # When
        result = verify_provider_binding_determinism(
            expected_digest=expected_digest,
            provider_id=provider_id,
            model_id=model_id,
            gateway_version=gateway_version,
            semantic_clock=semantic_clock,
        )

        # Then
        assert result is True

    def test_verify_provider_binding_determinism_failure(self):
        """Test failed verification of provider binding determinism."""
        # Given
        semantic_clock = SemanticClockSnapshot(tick=100, vector_clock=(("L1", 5), ("L3", 2)))

        expected_digest = compute_provider_binding_digest(
            provider_id="openai", model_id="gpt-4", gateway_version="1.0.0", semantic_clock=semantic_clock
        )

        # When - using different provider
        result = verify_provider_binding_determinism(
            expected_digest=expected_digest,
            provider_id="anthropic",  # Different!
            model_id="gpt-4",
            gateway_version="1.0.0",
            semantic_clock=semantic_clock,
        )

        # Then
        assert result is False

    def test_extract_provider_context_from_request(self):
        """Test extraction of provider context from LLM request."""
        # Given
        request = {
            "provider": "openai",
            "model": "gpt-4-turbo",
            "semantic_clock": {"tick": 50, "vector_clock": {"L0": 1, "L2": 2, "L5": 1}},
            "other_field": "should_be_ignored",
        }

        # When
        context = extract_provider_context_from_request(request)

        # Then
        assert isinstance(context, ProviderBindingContext)
        assert context.provider_id == "openai"
        assert context.model_id == "gpt-4-turbo"
        assert context.gateway_version == "1.0.0"  # Default from env
        assert context.semantic_clock_vector == {"L0": 1, "L2": 2, "L5": 1}

    def test_extract_provider_context_missing_fields(self):
        """Test extraction with missing fields uses defaults."""
        # Given
        request = {}

        # When
        context = extract_provider_context_from_request(request)

        # Then
        assert context.provider_id == "unknown"
        assert context.model_id == "unknown"
        assert context.gateway_version == "1.0.0"
        assert context.semantic_clock_vector == {}

    def test_semantic_clock_vector_serialization(self):
        """Test that semantic clock vector is properly serialized."""
        # Given
        semantic_clock = SemanticClockSnapshot(
            tick=123, vector_clock=(("L0", 10), ("L1", 5), ("L2", 15), ("L5", 8), ("L6", 3))
        )

        # When
        digest = compute_provider_binding_digest(
            provider_id="test", model_id="test-model", gateway_version="1.0.0", semantic_clock=semantic_clock
        )

        # Then - should not raise and should be deterministic
        assert digest is not None
        assert len(digest) == 64

    def test_provider_binding_determinism_replay_scenario(self):
        """Test provider binding determinism in a replay scenario."""
        # Given - Original request
        original_clock = SemanticClockSnapshot(tick=42, vector_clock=(("L0", 1), ("L2", 3), ("L5", 2)))

        original_digest = compute_provider_binding_digest(
            provider_id="anthropic",
            model_id="claude-3-5-sonnet-20241022",
            gateway_version="1.0.0",
            semantic_clock=original_clock,
        )

        # When - Replay with same parameters
        replay_clock = SemanticClockSnapshot(tick=42, vector_clock=(("L0", 1), ("L2", 3), ("L5", 2)))

        replay_digest = compute_provider_binding_digest(
            provider_id="anthropic",
            model_id="claude-3-5-sonnet-20241022",
            gateway_version="1.0.0",
            semantic_clock=replay_clock,
        )

        # Then - Should match exactly for replay determinism
        assert original_digest == replay_digest

    def test_different_gateway_versions_produce_different_digests(self):
        """Test that different gateway versions produce different digests."""
        # Given
        semantic_clock = SemanticClockSnapshot(tick=1, vector_clock=())

        # When
        digest_v1 = compute_provider_binding_digest(
            provider_id="openai", model_id="gpt-4", gateway_version="1.0.0", semantic_clock=semantic_clock
        )

        digest_v2 = compute_provider_binding_digest(
            provider_id="openai", model_id="gpt-4", gateway_version="2.0.0", semantic_clock=semantic_clock
        )

        # Then
        assert digest_v1 != digest_v2
