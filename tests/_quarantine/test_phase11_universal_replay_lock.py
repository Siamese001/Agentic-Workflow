# QUARANTINE: migration/provider-specific test
# DELETE AFTER: BGE is canonical generator and replay invariants fully covered by test_replay_determinism_invariants.py
# Superseded by: tests/governance/test_replay_determinism_invariants.py (INV-RPL-1, INV-RPL-2)
"""
W11 Universal Replay Lock Test

Proves deterministic replay envelope behavior across runs and validates
that parameter changes produce digest changes as expected.
"""

import os
from unittest.mock import patch

import pytest

from agentic_core.replay.replay_envelope import ReplayEnvelope, create_deterministic_cache_key

# from agentic_core.L2_execution.types.gateway_types import GenerationRequest
# from agentic_core.L2_execution.enforcement.SovereignLLMGateway import SovereignLLMGateway
from system_learning.engines.deterministic_replay_engine import DeterministicReplayEngine
from system_learning.engines.retrieval_profile import RetrievalProfile

# Provider-agnostic test constants — the envelope tests hash opaque strings;
# the specific provider values do not affect what the tests prove.
_TEST_EMBEDDER_PROVIDER = "bge-m3"
_TEST_EMBEDDER_MODEL = "BAAI/bge-m3"
_TEST_EMBEDDER_DIM = 1024
_TEST_EMBEDDER_DIM_ALT = 768  # distinct dim for digest-sensitivity assertions


# Mock types for testing without full dependency chain
class GenerationRequest:
    def __init__(self, agent_id, provider, model, prompt, temperature=0.7, max_tokens=1000):
        self.agent_id = agent_id
        self.provider = provider
        self.model = model
        self.prompt = prompt
        self.temperature = temperature
        self.max_tokens = max_tokens


class TestW11UniversalReplayLock:
    """W11: Universal Replay Key + End-to-End Determinism Lock."""

    def test_replay_envelope_determinism_across_runs(self):
        """Same input → identical ReplayEnvelope JSON across 2 runs."""
        # Create identical replay envelopes twice
        envelope1 = ReplayEnvelope.from_generation_context(
            routing_hash="abc123",
            manifest_hash="def456",
            model_id="gpt-4",
            model_version="1.0",
            temperature=0.7,
            policy_version="1.0",
            gateway_version="1.0",
            embedder_provider=_TEST_EMBEDDER_PROVIDER,
            embedder_model=_TEST_EMBEDDER_MODEL,
            embedder_dim=_TEST_EMBEDDER_DIM,
            agent_registry_hash="registry_hash_123",
            deterministic_engine_version="1.0.0",
        )

        envelope2 = ReplayEnvelope.from_generation_context(
            routing_hash="abc123",
            manifest_hash="def456",
            model_id="gpt-4",
            model_version="1.0",
            temperature=0.7,
            policy_version="1.0",
            gateway_version="1.0",
            embedder_provider=_TEST_EMBEDDER_PROVIDER,
            embedder_model=_TEST_EMBEDDER_MODEL,
            embedder_dim=_TEST_EMBEDDER_DIM,
            agent_registry_hash="registry_hash_123",
            deterministic_engine_version="1.0.0",
        )

        # Assert canonical JSON is identical
        json1 = envelope1.to_canonical_json()
        json2 = envelope2.to_canonical_json()
        assert json1 == json2

        # Assert digests are identical
        digest1 = envelope1.get_digest()
        digest2 = envelope2.get_digest()
        assert digest1 == digest2

    def test_replay_envelope_parameter_changes_affect_digest(self):
        """Changing model, embedder dim, policy version, retrieval threshold changes digest."""
        base_envelope = ReplayEnvelope.from_generation_context(
            routing_hash="abc123",
            manifest_hash="def456",
            model_id="gpt-4",
            model_version="1.0",
            temperature=0.7,
            policy_version="1.0",
            gateway_version="1.0",
            embedder_provider=_TEST_EMBEDDER_PROVIDER,
            embedder_model=_TEST_EMBEDDER_MODEL,
            embedder_dim=_TEST_EMBEDDER_DIM,
            agent_registry_hash="registry_hash_123",
            deterministic_engine_version="1.0.0",
        )

        base_digest = base_envelope.get_digest()

        # Test model change
        model_changed = ReplayEnvelope.from_generation_context(
            routing_hash="abc123",
            manifest_hash="def456",
            model_id="gpt-3.5-turbo",  # Changed
            model_version="1.0",
            temperature=0.7,
            policy_version="1.0",
            gateway_version="1.0",
            embedder_provider=_TEST_EMBEDDER_PROVIDER,
            embedder_model=_TEST_EMBEDDER_MODEL,
            embedder_dim=_TEST_EMBEDDER_DIM,
            agent_registry_hash="registry_hash_123",
            deterministic_engine_version="1.0.0",
        )
        assert model_changed.get_digest() != base_digest

        # Test embedder dim change
        dim_changed = ReplayEnvelope.from_generation_context(
            routing_hash="abc123",
            manifest_hash="def456",
            model_id="gpt-4",
            model_version="1.0",
            temperature=0.7,
            policy_version="1.0",
            gateway_version="1.0",
            embedder_provider=_TEST_EMBEDDER_PROVIDER,
            embedder_model=_TEST_EMBEDDER_MODEL,
            embedder_dim=_TEST_EMBEDDER_DIM_ALT,  # Changed from canonical dim
            agent_registry_hash="registry_hash_123",
            deterministic_engine_version="1.0.0",
        )
        assert dim_changed.get_digest() != base_digest

        # Test policy version change
        policy_changed = ReplayEnvelope.from_generation_context(
            routing_hash="abc123",
            manifest_hash="def456",
            model_id="gpt-4",
            model_version="1.0",
            temperature=0.7,
            policy_version="2.0",  # Changed
            gateway_version="1.0",
            embedder_provider=_TEST_EMBEDDER_PROVIDER,
            embedder_model=_TEST_EMBEDDER_MODEL,
            embedder_dim=_TEST_EMBEDDER_DIM,
            agent_registry_hash="registry_hash_123",
            deterministic_engine_version="1.0.0",
        )
        assert policy_changed.get_digest() != base_digest

    def test_deterministic_cache_key_stability(self):
        """Deterministic cache keys are stable across runs."""
        text = "test input text"
        embedder_identity = {
            "provider": _TEST_EMBEDDER_PROVIDER,
            "model": _TEST_EMBEDDER_MODEL,
            "dimensions": _TEST_EMBEDDER_DIM,
            "normalization_policy": "l2",
            "chunking_policy": "none",
        }

        key1 = create_deterministic_cache_key(text, embedder_identity)
        key2 = create_deterministic_cache_key(text, embedder_identity)

        assert key1 == key2
        assert len(key1) == 64  # SHA256 hex length

        # Different text should produce different key
        key3 = create_deterministic_cache_key("different text", embedder_identity)
        assert key3 != key1

        # Different embedder identity should produce different key
        different_identity = embedder_identity.copy()
        different_identity["model"] = "nomic-embed-text-v1"
        key4 = create_deterministic_cache_key(text, different_identity)
        assert key4 != key1

    @pytest.mark.skip(reason="Gateway test skipped due to dependency chain")
    def test_gateway_replay_envelope_binding(self):
        """Gateway binds ReplayEnvelope to response metadata."""
        # Skip this test to avoid dependency issues
        pass

    def test_deterministic_replay_engine_with_proper_dimensions(self):
        """DeterministicReplayEngine uses RetrievalProfile.embedding_dim."""
        engine = DeterministicReplayEngine()

        # Create test profiles with different dimensions
        base_profile = RetrievalProfile(embedding_dim=1536, top_k=5, similarity_cutoff=0.5, influence_cap=1.0)

        candidate_profile = RetrievalProfile(
            embedding_dim=3072,  # Different dimension
            top_k=5,
            similarity_cutoff=0.5,
            influence_cap=1.0,
        )

        # Run replay - should not crash with different dimensions
        result = engine.replay(base_profile=base_profile, candidate_profile=candidate_profile)

        # Assert result is valid
        assert result.case_count == 5  # Engine has 5 synthetic cases
        assert result.replay_digest is not None
        assert len(result.replay_digest) == 64  # SHA256 hex length

    def test_no_cross_phase_digest_leakage(self):
        """Ensure no W10/W9 digest leakage in W11 components."""
        # Test that ReplayEnvelope doesn't reference old digest patterns
        envelope = ReplayEnvelope.from_generation_context(
            routing_hash="abc123",
            manifest_hash="def456",
            model_id="gpt-4",
            model_version="1.0",
            temperature=0.7,
            policy_version="1.0",
            gateway_version="1.0",
            embedder_provider=_TEST_EMBEDDER_PROVIDER,
            embedder_model=_TEST_EMBEDDER_MODEL,
            embedder_dim=_TEST_EMBEDDER_DIM,
            agent_registry_hash="registry_hash_123",
            deterministic_engine_version="1.0.0",
        )

        json_str = envelope.to_canonical_json()

        # Should not contain old phase digest patterns
        assert "W10-" not in json_str
        assert "W9-" not in json_str
        assert "EMBEDDING-HIGH-SIGNAL" not in json_str
        assert "SIGNATURE-INTEGRITY" not in json_str

    original_digest = envelope.get_digest()

    # Tamper with policy_version in-memory (simulate corruption)
    with patch.object(envelope, "policy_version", "999.0"):
        tampered_digest = envelope.get_digest()

        # Should detect the tampering
        assert tampered_digest != original_digest

    print(f"W11_NEGCTRL_TAMPER: Original digest: {original_digest}")
    print(f"W11_NEGCTRL_TAMPER: Tampered digest: {tampered_digest}")


def test_negative_control_tamper_policy_version():
    """Negative control: Inject altered policy_version in-memory."""
    # Create legitimate envelope
    envelope = ReplayEnvelope.from_generation_context(
        routing_hash="abc123",
        manifest_hash="def456",
        model_id="gpt-4",
        model_version="1.0",
        temperature=0.7,
        policy_version="1.0",
        gateway_version="1.0",
        embedder_provider=_TEST_EMBEDDER_PROVIDER,
        embedder_model=_TEST_EMBEDDER_MODEL,
        embedder_dim=_TEST_EMBEDDER_DIM,
        agent_registry_hash="registry_hash_123",
        deterministic_engine_version="1.0.0",
    )

    original_digest = envelope.get_digest()

    # Tamper with policy_version in-memory (simulate corruption)
    with patch.object(envelope, "policy_version", "999.0"):
        tampered_digest = envelope.get_digest()

        # Should detect the tampering
        assert tampered_digest != original_digest

    print(f"W11_NEGCTRL_TAMPER: Original digest: {original_digest}")
    print(f"W11_NEGCTRL_TAMPER: Tampered digest: {tampered_digest}")

    print(f"W11-REPLAY-UNIVERSAL-DIGEST: {original_digest}")


def test_w11_acceptance_ssot():
    """Acceptance SSOT: Print W11-REPLAY-UNIVERSAL-DIGEST exactly once."""
    # Create deterministic test scenario
    envelope = ReplayEnvelope.from_generation_context(
        routing_hash="test_routing_hash",
        manifest_hash="test_manifest_hash",
        model_id="gpt-4",
        model_version="1.0",
        temperature=0.7,
        policy_version="1.0",
        gateway_version="1.0",
        embedder_provider=_TEST_EMBEDDER_PROVIDER,
        embedder_model=_TEST_EMBEDDER_MODEL,
        embedder_dim=_TEST_EMBEDDER_DIM,
        agent_registry_hash="test_registry_hash",
        deterministic_engine_version="1.0.0",
    )

    digest = envelope.get_digest()
    print(f"W11-REPLAY-UNIVERSAL-DIGEST: {digest}")

    # Verify digest stability
    digest2 = envelope.get_digest()
    assert digest == digest2

    return digest


if __name__ == "__main__":
    if "W11_NEGCTRL_TAMPER" in os.environ and os.environ["W11_NEGCTRL_TAMPER"] == "1":
        test_negative_control_tamper_policy_version()
    else:
        test_w11_acceptance_ssot()
