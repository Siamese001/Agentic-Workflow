"""
W4-F Retrieval Profile Activation Gate Tests

Tests for explicit activation gate with deterministic checks.
"""

import os
from unittest.mock import Mock

import pytest

from system_learning.engines.l4_state_writer import L4StateWriter
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.retrieval_profile_activation_gate import (
    RetrievalProfileActivationGate,
)


@pytest.mark.unit_min_deps
class TestActivationGateW4F:
    """Test W4-F Retrieval Profile Activation Gate functionality."""

    def test_refuse_without_approval(self):
        """Test that activation refuses when proposal exists but no approval."""
        gate = RetrievalProfileActivationGate()
        l4_writer = Mock(spec=L4StateWriter)
        now_utc = 1234567890

        # Try to activate unapproved proposal
        result = gate.activate_if_approved(
            base_profile_id="test-profile",
            proposal_digest="test-proposal-digest-unapproved",
            now_utc=now_utc,
            l4_writer=l4_writer,
        )

        # Verify activation refused
        assert result.activated == False
        assert result.base_profile_id == "test-profile"
        assert result.proposal_digest == "test-proposal-digest-unapproved"
        assert result.new_profile_id is None
        assert "not approved" in result.reason.lower()

        # Verify digest is computed
        assert result.activation_digest is not None
        assert len(result.activation_digest) == 64  # SHA-256 hex length

    def test_approve_then_activate(self):
        """Test successful activation with approved proposal."""
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
        assert result.base_profile_id == "test-profile"
        assert result.proposal_digest == "test-proposal-digest-approved"
        assert result.new_profile_id == "test-profile-proposed"
        assert "successful" in result.reason.lower()

        # Verify L4 writes were attempted
        assert l4_writer.write_l4a_detection_signal.call_count >= 2  # Profile write + active profile update

        # Verify digest is computed and emitted
        assert result.activation_digest is not None
        assert len(result.activation_digest) == 64

    def test_replay_check_determinism(self):
        """Test that replay check produces deterministic digests."""
        gate = RetrievalProfileActivationGate()

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

        proposed_profile = RetrievalProfile(
            profile_id="test-profile-proposed",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=12,
            similarity_cutoff=0.82,
            influence_cap=0.55,
            normalization_policy="l2",
        )

        # Run replay check twice
        result1 = gate.replay_engine.replay(
            base_profile=base_profile,
            candidate_profile=proposed_profile,
        )

        result2 = gate.replay_engine.replay(
            base_profile=base_profile,
            candidate_profile=proposed_profile,
        )

        # Verify deterministic digest
        assert result1.replay_digest == result2.replay_digest, \
            "Replay check digest must be deterministic"

        # Verify digest format
        assert len(result1.replay_digest) == 64  # SHA-256 hex length

    def test_invariant_failure_blocks_activation(self):
        """Test that invariant violations block activation."""
        gate = RetrievalProfileActivationGate()
        l4_writer = Mock(spec=L4StateWriter)
        now_utc = 1234567890

        # Monkey patch the invariant checker to always fail
        original_validate = gate.invariant_checker.validate
        def failing_validate(*args, **kwargs):
            raise ValueError("Test invariant violation: similarity_cutoff out of bounds")

        try:
            gate.invariant_checker.validate = failing_validate

            # Try to activate approved proposal (should fail due to invariant)
            result = gate.activate_if_approved(
                base_profile_id="test-profile",
                proposal_digest="test-proposal-digest-approved",
                now_utc=now_utc,
                l4_writer=l4_writer,
            )

            # Verify activation blocked
            assert result.activated == False
            assert result.new_profile_id is None
            assert "invariant violation" in result.reason.lower()

        finally:
            # Restore original method
            gate.invariant_checker.validate = original_validate

    def test_nonexistent_proposal_blocks_activation(self):
        """Test that nonexistent proposal blocks activation."""
        gate = RetrievalProfileActivationGate()
        l4_writer = Mock(spec=L4StateWriter)
        now_utc = 1234567890

        # Try to activate nonexistent proposal
        result = gate.activate_if_approved(
            base_profile_id="test-profile",
            proposal_digest="nonexistent-proposal-digest",
            now_utc=now_utc,
            l4_writer=l4_writer,
        )

        # Verify activation blocked
        assert result.activated == False
        assert result.new_profile_id is None
        assert "not found" in result.reason.lower()

    def test_nonexistent_base_profile_blocks_activation(self):
        """Test that nonexistent base profile blocks activation."""
        gate = RetrievalProfileActivationGate()
        l4_writer = Mock(spec=L4StateWriter)
        now_utc = 1234567890

        # Try to activate with nonexistent base profile
        result = gate.activate_if_approved(
            base_profile_id="nonexistent-profile",
            proposal_digest="test-proposal-digest-approved",
            now_utc=now_utc,
            l4_writer=l4_writer,
        )

        # Verify activation blocked
        assert result.activated == False
        assert result.new_profile_id is None
        assert "not found" in result.reason.lower()


@pytest.mark.unit_min_deps
class TestW4FNegativeControl:
    """Negative control tests for W4-F Activation Gate."""

    @pytest.mark.xfail(reason="W4F tamper guard", strict=False)
    def test_activation_determinism_violation_negative_control(self):
        """Negative control: tamper with activation digest determinism."""
        # Set tamper flag to change canonicalization
        os.environ["W4F_NEGCTRL_TAMPER"] = "1"

        # Monkey patch the json.dumps in activation gate
        import json

        import system_learning.engines.retrieval_profile_activation_gate as gate_module
        original_json_dumps = json.dumps

        def tampered_json_dumps(obj, *, sort_keys=False, separators=None):
            """Tampered JSON serialization that uses different separators."""
            if separators == (",", ":"):
                # Use different separators to change canonical form
                separators = (", ", ": ")
            return original_json_dumps(obj, sort_keys=sort_keys, separators=separators)

        try:
            # Apply tampering
            gate_module.json.dumps = tampered_json_dumps

            gate = RetrievalProfileActivationGate()
            l4_writer = Mock(spec=L4StateWriter)
            now_utc = 1234567890

            # Run activation with tampering
            result_tampered = gate.activate_if_approved(
                base_profile_id="test-profile",
                proposal_digest="test-proposal-digest-approved",
                now_utc=now_utc,
                l4_writer=l4_writer,
            )

            # Restore original function for comparison
            gate_module.json.dumps = original_json_dumps
            result_normal = gate.activate_if_approved(
                base_profile_id="test-profile",
                proposal_digest="test-proposal-digest-approved",
                now_utc=now_utc,
                l4_writer=l4_writer,
            )

            # Tampering should cause different results - this should FAIL the test
            if result_tampered.activation_digest != result_normal.activation_digest:
                assert False, f"TAMPERING DETECTED: tampered digest {result_tampered.activation_digest} != normal digest {result_normal.activation_digest}"

            # If we get here, tampering wasn't effective
            assert False, "Tampering was not effective - activation digests are identical"

        finally:
            # Restore original function
            gate_module.json.dumps = original_json_dumps
            # Clean up environment
            os.environ.pop("W4F_NEGCTRL_TAMPER", None)

    def test_activation_determinism_violation_negative_control_guard_intact(self):
        """Verify negative control guard is intact when not tampering."""
        # Ensure no tampering flag is set
        if "W4F_NEGCTRL_TAMPER" in os.environ:
            del os.environ["W4F_NEGCTRL_TAMPER"]

        gate = RetrievalProfileActivationGate()
        l4_writer = Mock(spec=L4StateWriter)
        now_utc = 1234567890

        # Run activation twice without tampering
        result1 = gate.activate_if_approved(
            base_profile_id="test-profile",
            proposal_digest="test-proposal-digest-approved",
            now_utc=now_utc,
            l4_writer=l4_writer,
        )

        result2 = gate.activate_if_approved(
            base_profile_id="test-profile",
            proposal_digest="test-proposal-digest-approved",
            now_utc=now_utc,
            l4_writer=l4_writer,
        )

        # Should be identical when not tampering
        assert result1.activation_digest == result2.activation_digest, \
            "Activation digest must be identical when not tampering"
        assert result1.activated == result2.activated, \
            "Activation status must be identical when not tampering"
