"""
W4-E Retrieval Profile Proposal Manager

Manages deterministic proposal creation and approval tracking.
"""


from system_learning.engines.policy_recommendation_engine import PolicyRecommendation
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.retrieval_profile_proposal import (
    RetrievalProfileProposal,
    create_proposal_digest,
)
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class RetrievalProfileProposalManager:
    """Manages RetrievalProfile proposals with deterministic creation and approval tracking."""

    def create_proposal(
        self,
        *,
        recommendation: PolicyRecommendation,
        active_profile: RetrievalProfile,
        now_utc: int,
    ) -> RetrievalProfileProposal:
        """Create a deterministic proposal from policy recommendation.

        Args:
            recommendation: Policy recommendation from W4-D
            active_profile: Current active RetrievalProfile
            now_utc: Current timestamp

        Returns:
            RetrievalProfileProposal with deterministic digest
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalProfileProposalManager.create_proposal")

        # Apply recommended changes to create proposed profile
        proposed_profile = self._apply_recommendation_to_profile(
            recommendation=recommendation,
            base_profile=active_profile,
        )

        # Create recommended changes dictionary (deltas)
        recommended_changes = {}
        for param, new_value in recommendation.recommended_changes.items():
            if hasattr(active_profile, param):
                old_value = getattr(active_profile, param)
                recommended_changes[param] = round(new_value - old_value, 6)

        # Compute deterministic digest
        deterministic_digest = create_proposal_digest(
            base_profile_id=active_profile.profile_id,
            proposed_profile=proposed_profile,
            recommended_changes=recommended_changes,
            proposed_at_utc=now_utc,
        )

        return RetrievalProfileProposal(
            base_profile_id=active_profile.profile_id,
            proposed_profile=proposed_profile,
            recommended_changes=recommended_changes,
            approved=False,  # Initial proposals are unapproved
            proposed_at_utc=now_utc,
            deterministic_digest=deterministic_digest,
        )

    def set_approval(
        self,
        *,
        proposal_digest: str,
        approved: bool,
        now_utc: int,
    ) -> None:
        """Set approval status for a proposal.

        This method records the approval decision but does NOT activate
        the proposed profile. Activation is handled separately.

        Args:
            proposal_digest: Digest of the proposal to approve/reject
            approved: True to approve, False to reject
            now_utc: Current timestamp
        """
        # In a real implementation, this would write to L4 state
        # For now, this is a no-op placeholder
        # The approval is recorded via L4StateWriter.write_l4c_retrieval_profile_proposal_approval
        pass

    def get_latest_proposal(
        self,
        *,
        base_profile_id: str,
    ) -> RetrievalProfileProposal | None:
        """Get the latest proposal for a base profile.

        Args:
            base_profile_id: ID of the base profile

        Returns:
            Latest proposal if exists, None otherwise
        """
        # In a real implementation, this would read from L4 state
        # For now, return None as placeholder
        return None

    def _apply_recommendation_to_profile(
        self,
        *,
        recommendation: PolicyRecommendation,
        base_profile: RetrievalProfile,
    ) -> RetrievalProfile:
        """Apply recommended changes to create proposed profile.

        Args:
            recommendation: Policy recommendation with changes
            base_profile: Base profile to modify

        Returns:
            New RetrievalProfile with applied changes
        """
        # Start with base profile values
        profile_id = f"{base_profile.profile_id}_proposed_{recommendation.deterministic_digest[:8]}"
        primary_embedder_id = base_profile.primary_embedder_id
        embedding_dim = base_profile.embedding_dim
        similarity_cutoff = base_profile.similarity_cutoff
        top_k = base_profile.top_k
        influence_cap = base_profile.influence_cap
        normalization_policy = base_profile.normalization_policy
        shadow_embedder_id = base_profile.shadow_embedder_id
        hybrid_alpha = base_profile.hybrid_alpha

        # Apply recommended changes with bounds checking
        for param, new_value in recommendation.recommended_changes.items():
            if param == "similarity_cutoff":
                # Ensure similarity_cutoff stays within valid bounds
                similarity_cutoff = max(0.1, min(1.0, round(new_value, 6)))
            elif param == "influence_cap":
                # Ensure influence_cap stays within valid bounds
                influence_cap = max(0.0, min(1.0, round(new_value, 6)))
            elif param == "top_k":
                # Ensure top_k stays within valid bounds
                top_k = max(1, min(1000, int(round(new_value))))

        # Create proposed profile
        proposed_profile = RetrievalProfile(
            profile_id=profile_id,
            primary_embedder_id=primary_embedder_id,
            embedding_dim=embedding_dim,
            similarity_cutoff=similarity_cutoff,
            top_k=top_k,
            influence_cap=influence_cap,
            normalization_policy=normalization_policy,
            shadow_embedder_id=shadow_embedder_id,
            hybrid_alpha=hybrid_alpha,
        )

        return proposed_profile


# Export public interface
__all__ = [
    'RetrievalProfileProposalManager',
]
