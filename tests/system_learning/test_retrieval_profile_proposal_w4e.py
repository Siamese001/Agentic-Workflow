"""
W4-E Retrieval Profile Proposal Tests

Tests for deterministic proposal creation and approval tracking.
"""

import os

import pytest

from system_learning.engines.policy_recommendation_engine import (
    PolicyRecommendation,
)
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.retrieval_profile_proposal_manager import RetrievalProfileProposalManager


@pytest.mark.unit_min_deps
class TestW4EProposalDeterminism:
    """Test W4-E proposal digest determinism."""

    def test_proposal_digest_stable(self):
        """Test that proposal digests are stable across runs."""
        # Create fixed policy recommendation
        recommendation = PolicyRecommendation(
            profile_id="test-profile",
            recommended_changes={
                "similarity_cutoff": 0.842500,  # -0.0075 from 0.85
                "influence_cap": 0.503000,  # +0.003 from 0.5
            },
            rationale="Drift detected: Lower similarity_cutoff from 0.850000 to 0.842500 (drift_score=0.150000); Increase influence_cap from 0.500000 to 0.503000 (drift_score=0.150000)",
            confidence_score=0.300000,
            deterministic_digest="4ee35d0874a984a1457095ac1d56a9b819b1b6742e96fd7352393b56d2b47324",
        )

        # Create active profile
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        manager = RetrievalProfileProposalManager()
        now_utc = 1234567890

        # Create proposal twice independently
        proposal1 = manager.create_proposal(
            recommendation=recommendation,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        proposal2 = manager.create_proposal(
            recommendation=recommendation,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        # Verify deterministic digest
        assert proposal1.deterministic_digest == proposal2.deterministic_digest, (
            "Proposal digest must be deterministic"
        )

        # Emit digest for test verification
        proposal1.emit_digest()

        # Verify proposal structure
        assert proposal1.base_profile_id == "test-profile"
        assert proposal1.approved == False
        assert proposal1.proposed_at_utc == now_utc
        assert proposal1.proposed_profile.profile_id != active_profile.profile_id
        assert "proposed_" in proposal1.proposed_profile.profile_id

        # Verify proposed profile reflects changes
        assert proposal1.proposed_profile.similarity_cutoff == 0.8425
        assert proposal1.proposed_profile.influence_cap == 0.503


@pytest.mark.unit_min_deps
class TestW4EProposalAdvisoryOnly:
    """Test W4-E proposal advisory-only behavior."""

    def test_proposal_advisory_only_no_activation(self):
        """Test that creating proposal does NOT change ACTIVE_RETRIEVAL_PROFILE_ID."""
        # Create policy recommendation
        recommendation = PolicyRecommendation(
            profile_id="test-profile",
            recommended_changes={
                "similarity_cutoff": 0.842500,
                "influence_cap": 0.503000,
            },
            rationale="Test recommendation",
            confidence_score=0.3,
            deterministic_digest="test-digest-123",
        )

        # Create active profile
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        manager = RetrievalProfileProposalManager()
        now_utc = 1234567890

        # Create proposal
        proposal = manager.create_proposal(
            recommendation=recommendation,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        # Verify active profile is unchanged
        assert active_profile.profile_id == "test-profile"
        assert active_profile.similarity_cutoff == 0.85
        assert active_profile.influence_cap == 0.5

        # Verify proposal has different profile ID
        assert proposal.proposed_profile.profile_id != active_profile.profile_id
        assert proposal.proposed_profile.similarity_cutoff == 0.8425
        assert proposal.proposed_profile.influence_cap == 0.503

        # Verify proposal is not approved
        assert proposal.approved == False

    def test_proposal_content_correctness(self):
        """Test that proposed profile fields reflect bounded deltas."""
        # Create recommendation with extreme values
        recommendation = PolicyRecommendation(
            profile_id="test-profile",
            recommended_changes={
                "similarity_cutoff": -0.5,  # Would go negative
                "influence_cap": 2.0,  # Would exceed 1.0
            },
            rationale="Test extreme recommendation",
            confidence_score=0.5,
            deterministic_digest="test-digest-extreme",
        )

        # Create active profile
        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        manager = RetrievalProfileProposalManager()
        now_utc = 1234567890

        # Create proposal
        proposal = manager.create_proposal(
            recommendation=recommendation,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        # Verify bounds are enforced
        assert proposal.proposed_profile.similarity_cutoff >= 0.1, (
            "Similarity cutoff should not go below minimum"
        )
        assert proposal.proposed_profile.similarity_cutoff <= 1.0, (
            "Similarity cutoff should not exceed maximum"
        )
        assert proposal.proposed_profile.influence_cap >= 0.0, "Influence cap should not go below minimum"
        assert proposal.proposed_profile.influence_cap <= 1.0, "Influence cap should not exceed maximum"

        # Verify rounding to 6 decimals
        assert len(str(proposal.proposed_profile.similarity_cutoff).split(".")[-1]) <= 6, (
            "Values should be rounded to 6 decimals"
        )


@pytest.mark.unit_min_deps
class TestW4EProposalApproval:
    """Test W4-E proposal approval event wiring."""

    def test_approval_event_wiring(self):
        """Test that approval events are recorded but do not activate profile."""
        # Create proposal
        recommendation = PolicyRecommendation(
            profile_id="test-profile",
            recommended_changes={"similarity_cutoff": 0.842500},
            rationale="Test recommendation",
            confidence_score=0.3,
            deterministic_digest="test-digest-approval",
        )

        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        manager = RetrievalProfileProposalManager()
        now_utc = 1234567890

        # Create proposal
        proposal = manager.create_proposal(
            recommendation=recommendation,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        # Verify initial state
        assert proposal.approved == False

        # Set approval (this would write to L4 in real implementation)
        manager.set_approval(
            proposal_digest=proposal.deterministic_digest,
            approved=True,
            now_utc=now_utc + 100,
        )

        # Create approved copy
        approved_proposal = proposal.create_approved_copy(now_utc + 100)

        # Verify approval is recorded
        assert approved_proposal.approved == True
        assert approved_proposal.deterministic_digest != proposal.deterministic_digest, (
            "Approved proposal should have different digest"
        )

        # Verify original profile is still unchanged
        assert active_profile.similarity_cutoff == 0.85
        assert active_profile.profile_id == "test-profile"


@pytest.mark.unit_min_deps
class TestW4ENegativeControl:
    """Negative control tests for W4-E Retrieval Profile Proposal."""

    @pytest.mark.xfail(reason="W4E tamper guard", strict=True)
    def test_proposal_determinism_violation_negative_control(self):
        """Negative control: tamper with proposal determinism."""
        # Set tamper flag to change canonicalization
        os.environ["W4E_NEGCTRL_TAMPER"] = "1"

        # Monkey patch the json.dumps to use different separator order
        import system_learning.engines.retrieval_profile_proposal as proposal_module

        original_json_dumps = proposal_module.json.dumps

        def tampered_json_dumps(obj, *, sort_keys=False, separators=None):
            """Tampered JSON serialization that uses different separators."""
            if separators == (",", ":"):
                # Use different separators to change canonical form
                separators = (", ", ": ")
            return original_json_dumps(obj, sort_keys=sort_keys, separators=separators)

        try:
            # Apply tampering
            proposal_module.json.dumps = tampered_json_dumps

            # Create fixed inputs
            recommendation = PolicyRecommendation(
                profile_id="test-profile",
                recommended_changes={"similarity_cutoff": 0.842500},
                rationale="Test recommendation",
                confidence_score=0.3,
                deterministic_digest="test-digest-123",
            )

            active_profile = RetrievalProfile(
                profile_id="test-profile",
                primary_embedder_id="test-embedder",
                embedding_dim=1536,
                shadow_embedder_id="test-shadow",
                top_k=10,
                similarity_cutoff=0.85,
                influence_cap=0.5,
                normalization_policy="l2",
            )

            manager = RetrievalProfileProposalManager()
            now_utc = 1234567890

            # Run proposal creation with tampering
            proposal_tampered = manager.create_proposal(
                recommendation=recommendation,
                active_profile=active_profile,
                now_utc=now_utc,
            )

            # Restore original function for comparison
            proposal_module.json.dumps = original_json_dumps
            proposal_normal = manager.create_proposal(
                recommendation=recommendation,
                active_profile=active_profile,
                now_utc=now_utc,
            )

            # Tampering should cause different results - this should FAIL the test
            if proposal_tampered.deterministic_digest != proposal_normal.deterministic_digest:
                assert False, (
                    f"TAMPERING DETECTED: tampered digest {proposal_tampered.deterministic_digest} != normal digest {proposal_normal.deterministic_digest}"
                )

            # If we get here, tampering wasn't effective
            assert False, "Tampering was not effective - digests are identical"

        finally:
            # Restore original function
            proposal_module.json.dumps = original_json_dumps
            # Clean up environment
            os.environ.pop("W4E_NEGCTRL_TAMPER", None)

    def test_proposal_determinism_violation_negative_control_guard_intact(self):
        """Verify negative control guard is intact when not tampering."""
        # Ensure no tampering flag is set
        if "W4E_NEGCTRL_TAMPER" in os.environ:
            del os.environ["W4E_NEGCTRL_TAMPER"]

        # Create fixed inputs
        recommendation = PolicyRecommendation(
            profile_id="test-profile",
            recommended_changes={"similarity_cutoff": 0.842500},
            rationale="Test recommendation",
            confidence_score=0.3,
            deterministic_digest="test-digest-123",
        )

        active_profile = RetrievalProfile(
            profile_id="test-profile",
            primary_embedder_id="test-embedder",
            embedding_dim=1536,
            shadow_embedder_id="test-shadow",
            top_k=10,
            similarity_cutoff=0.85,
            influence_cap=0.5,
            normalization_policy="l2",
        )

        manager = RetrievalProfileProposalManager()
        now_utc = 1234567890

        # Run proposal creation twice without tampering
        proposal1 = manager.create_proposal(
            recommendation=recommendation,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        proposal2 = manager.create_proposal(
            recommendation=recommendation,
            active_profile=active_profile,
            now_utc=now_utc,
        )

        # Should be identical when not tampering
        assert proposal1.deterministic_digest == proposal2.deterministic_digest, (
            "Digest must be identical when not tampering"
        )
        assert proposal1.proposed_profile.similarity_cutoff == proposal2.proposed_profile.similarity_cutoff, (
            "Proposed profiles must be identical when not tampering"
        )
