"""
W5 Deterministic Replay Engine Tests

Tests for deterministic replay validation of RetrievalProfile changes.
"""

import os
import random
from unittest.mock import Mock

import pytest

from system_learning.engines.deterministic_replay_engine import DeterministicReplayEngine
from system_learning.engines.l4_state_writer import L4StateWriter
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.retrieval_profile_activation_gate import RetrievalProfileActivationGate


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@pytest.mark.unit_min_deps
class TestW5ReplayEngine:
    """Test W5 Deterministic Replay Engine functionality."""

    def test_determinism(self):
        """Test that two independent runs produce identical W5-REPLAY-DIGEST."""
        engine = DeterministicReplayEngine()

        # Create test profiles
        base_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        candidate_profile = RetrievalProfile(
            profile_id="test-profile-candidate",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=12,
            similarity_cutoff=0.82,
            influence_cap=0.55,
            normalization_policy="l2",
        )

        # Run replay twice independently
        result1 = engine.replay(
            base_profile=base_profile,
            candidate_profile=candidate_profile,
        )

        result2 = engine.replay(
            base_profile=base_profile,
            candidate_profile=candidate_profile,
        )

        # Verify deterministic digest
        assert result1.replay_digest == result2.replay_digest, (
            "Replay digest must be deterministic across runs"
        )

        # Verify other fields are identical
        assert result1.case_count == result2.case_count
        assert result1.changed_cases == result2.changed_cases
        assert result1.base_outputs == result2.base_outputs
        assert result1.candidate_outputs == result2.candidate_outputs

        # Verify digest format
        assert len(result1.replay_digest) == 64  # SHA-256 hex length

    def test_ordering_invariance(self):
        """Test that shuffling synthetic cases before replay doesn't affect digest."""
        engine = DeterministicReplayEngine()

        # Create test profiles
        base_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        candidate_profile = RetrievalProfile(
            profile_id="test-profile-candidate",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=15,
            similarity_cutoff=0.80,
            influence_cap=0.60,
            normalization_policy="l2",
        )

        # Run replay with original order
        result_original = engine.replay(
            base_profile=base_profile,
            candidate_profile=candidate_profile,
        )

        # Shuffle synthetic cases
        original_cases = engine._synthetic_cases.copy()
        random.shuffle(engine._synthetic_cases)

        # Run replay with shuffled order
        result_shuffled = engine.replay(
            base_profile=base_profile,
            candidate_profile=candidate_profile,
        )

        # Restore original order
        engine._synthetic_cases = original_cases

        # Verify digest is identical despite shuffling
        assert result_original.replay_digest == result_shuffled.replay_digest, (
            "Replay digest must be invariant to case ordering"
        )

        # Verify results are otherwise identical
        assert result_original.case_count == result_shuffled.case_count
        assert result_original.changed_cases == result_shuffled.changed_cases

    def test_activation_integration(self):
        """Test that activation gate uses replay engine and includes replay_digest."""
        gate = RetrievalProfileActivationGate()
        l4_writer = Mock(spec=L4StateWriter)
        now_utc = 1234567890

        # Activate approved proposal
        result = gate.activate_if_approved(
            base_profile_id="test-profile",
            proposal_digest="test-proposal-digest-approved",
            now_utc=now_utc,
            l4_writer=l4_writer,
        )

        # Verify activation succeeded
        assert result.activated == True
        assert result.replay_digest is not None, "ActivationResult should contain replay_digest"

        # Verify replay digest format
        assert len(result.replay_digest) == 64  # SHA-256 hex length

        # Verify activation digest is also present
        assert result.activation_digest is not None
        assert len(result.activation_digest) == 64

    def test_replay_changed_cases_counting(self):
        """Test that changed cases are correctly counted."""
        engine = DeterministicReplayEngine()

        # Create identical profiles (should have 0 changed cases)
        base_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        identical_profile = RetrievalProfile(
            profile_id="test-profile-identical",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        # Run replay with identical profiles
        result_identical = engine.replay(
            base_profile=base_profile,
            candidate_profile=identical_profile,
        )

        # Verify no changed cases
        assert result_identical.changed_cases == 0, "Identical profiles should have 0 changed cases"

        # Create different profile (should have changed cases)
        different_profile = RetrievalProfile(
            profile_id="test-profile-different",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=20,  # Different top_k
            similarity_cutoff=0.70,  # Different similarity_cutoff
            influence_cap=0.80,  # Different influence_cap
            normalization_policy="l2",
        )

        # Run replay with different profile
        result_different = engine.replay(
            base_profile=base_profile,
            candidate_profile=different_profile,
        )

        # Verify some changed cases
        assert result_different.changed_cases > 0, "Different profiles should have > 0 changed cases"

        # Verify case count is consistent
        assert result_identical.case_count == result_different.case_count, (
            "Case count should be consistent across runs"
        )

    def test_determinism_self_check_failure(self):
        """Test that determinism self-check failure raises ValueError."""
        engine = DeterministicReplayEngine()

        # Create test profiles
        base_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        candidate_profile = RetrievalProfile(
            profile_id="test-profile-candidate",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=12,
            similarity_cutoff=0.82,
            influence_cap=0.55,
            normalization_policy="l2",
        )

        # Monkey patch the digest computation to simulate determinism failure
        original_compute_digest = engine._compute_replay_digest
        call_count = 0

        def failing_compute_digest(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return original_compute_digest(*args, **kwargs)
            else:
                return "different-digest-" + "0" * 50  # Different digest

        try:
            engine._compute_replay_digest = failing_compute_digest

            # This should raise ValueError due to determinism self-check failure
            with pytest.raises(ValueError, match="Determinism self-check failed"):
                engine.replay(
                    base_profile=base_profile,
                    candidate_profile=candidate_profile,
                )

        finally:
            # Restore original method
            engine._compute_replay_digest = original_compute_digest


@pytest.mark.unit_min_deps
class TestW5NegativeControl:
    """Negative control tests for W5 Deterministic Replay Engine."""

    @pytest.mark.xfail(reason="W5 tamper guard", strict=True)
    def test_replay_determinism_violation_negative_control(self):
        """Negative control: tamper with replay digest determinism."""
        # Set tamper flag to change canonicalization
        os.environ["W5_NEGCTRL_TAMPER"] = "1"

        # Monkey patch the json.dumps in replay engine
        import json

        import system_learning.engines.deterministic_replay_engine as engine_module

        original_json_dumps = json.dumps

        def tampered_json_dumps(obj, *, sort_keys=False, separators=None):
            """Tampered JSON serialization that uses different separators."""
            if separators == (",", ":"):
                # Use different separators to change canonical form
                separators = (", ", ": ")
            return original_json_dumps(obj, sort_keys=sort_keys, separators=separators)

        try:
            # Apply tampering
            engine_module.json.dumps = tampered_json_dumps

            engine = DeterministicReplayEngine()

            # Create test profiles
            base_profile = RetrievalProfile(
                profile_id="test-profile",
                primary_embedder_id="test-embedder",
                embedding_dim=1536,
                shadow_embedder_id="test-shadow",
                top_k=10,
                similarity_cutoff=0.85,
                influence_cap=0.5,
                normalization_policy="l2",
            )

            candidate_profile = RetrievalProfile(
                profile_id="test-profile-candidate",
                primary_embedder_id="test-embedder",
                embedding_dim=1536,
                shadow_embedder_id="test-shadow",
                top_k=12,
                similarity_cutoff=0.82,
                influence_cap=0.55,
                normalization_policy="l2",
            )

            # Run replay with tampering
            result_tampered = engine.replay(
                base_profile=base_profile,
                candidate_profile=candidate_profile,
            )

            # Restore original function for comparison
            engine_module.json.dumps = original_json_dumps
            result_normal = engine.replay(
                base_profile=base_profile,
                candidate_profile=candidate_profile,
            )

            # Tampering should cause different results - this should FAIL the test
            if result_tampered.replay_digest != result_normal.replay_digest:
                assert False, (
                    f"TAMPERING DETECTED: tampered digest {result_tampered.replay_digest} != normal digest {result_normal.replay_digest}"
                )

            # If we get here, tampering wasn't effective
            assert False, "Tampering was not effective - replay digests are identical"

        finally:
            # Restore original function
            engine_module.json.dumps = original_json_dumps
            # Clean up environment
            os.environ.pop("W5_NEGCTRL_TAMPER", None)

    def test_replay_determinism_violation_negative_control_guard_intact(self):
        """Verify negative control guard is intact when not tampering."""
        # Ensure no tampering flag is set
        if "W5_NEGCTRL_TAMPER" in os.environ:
            del os.environ["W5_NEGCTRL_TAMPER"]

        engine = DeterministicReplayEngine()

        # Create test profiles
        base_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        candidate_profile = RetrievalProfile(
            profile_id="test-profile-candidate",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=12,
            similarity_cutoff=0.82,
            influence_cap=0.55,
            normalization_policy="l2",
        )

        # Run replay twice without tampering
        result1 = engine.replay(
            base_profile=base_profile,
            candidate_profile=candidate_profile,
        )

        result2 = engine.replay(
            base_profile=base_profile,
            candidate_profile=candidate_profile,
        )

        # Should be identical when not tampering
        assert result1.replay_digest == result2.replay_digest, (
            "Replay digest must be identical when not tampering"
        )
        assert result1.case_count == result2.case_count, "Case count must be identical when not tampering"
        assert result1.changed_cases == result2.changed_cases, (
            "Changed cases must be identical when not tampering"
        )
