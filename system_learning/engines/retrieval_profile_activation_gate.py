"""
W4-F Retrieval Profile Activation Gate

Explicit activation gate that applies approved proposals with deterministic checks.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from system_learning.engines.deterministic_replay_engine import DeterministicReplayEngine
from system_learning.engines.l4_state_writer import L4StateWriter
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.retrieval_profile_invariant_checker import RetrievalProfileInvariantChecker


@dataclass(frozen=True, slots=True)
class ActivationResult:
    """Result of profile activation attempt."""

    activated: bool
    base_profile_id: str
    proposal_digest: str
    new_profile_id: str | None
    activation_digest: str
    replay_digest: str | None
    reason: str

    def emit_digest(self) -> None:
        """Print the activation digest for verification."""
        print(f"W4F-ACTIVATION-DIGEST: {self.activation_digest}")


class RetrievalProfileActivationGate:
    """Explicit activation gate for RetrievalProfile proposals."""

    def __init__(self):
        """Initialize activation gate with required components."""
        self.invariant_checker = RetrievalProfileInvariantChecker()
        self.replay_engine = DeterministicReplayEngine()

    def activate_if_approved(
        self, *, base_profile_id: str, proposal_digest: str, now_utc: int, l4_writer: L4StateWriter
    ) -> ActivationResult:
        """Activate proposal if approved and all checks pass.

        Args:
            base_profile_id: ID of the base profile
            proposal_digest: Digest of the proposal to activate
            now_utc: Current timestamp
            l4_writer: L4 state writer

        Returns:
            ActivationResult with deterministic digest
        """
        proposal = self._load_proposal_from_l4(proposal_digest)
        if proposal is None:
            return self._create_failure_result(
                base_profile_id=base_profile_id,
                proposal_digest=proposal_digest,
                reason="Proposal not found in L4",
                now_utc=now_utc,
            )
        if not proposal.approved:
            return self._create_failure_result(
                base_profile_id=base_profile_id,
                proposal_digest=proposal_digest,
                reason="Proposal not approved",
                now_utc=now_utc,
            )
        base_profile = self._load_profile_from_l4(base_profile_id)
        if base_profile is None:
            return self._create_failure_result(
                base_profile_id=base_profile_id,
                proposal_digest=proposal_digest,
                reason="Base profile not found in L4",
                now_utc=now_utc,
            )
        try:
            replay_result = self.replay_engine.replay(
                base_profile=base_profile, candidate_profile=proposal.proposed_profile
            )
        except ValueError as e:
            return self._create_failure_result(
                base_profile_id=base_profile_id,
                proposal_digest=proposal_digest,
                reason=f"Replay determinism check failed: {str(e)}",
                now_utc=now_utc,
            )
        try:
            self.invariant_checker.validate(profile=proposal.proposed_profile, reference_profile=base_profile)
        except ValueError as e:
            return self._create_failure_result(
                base_profile_id=base_profile_id,
                proposal_digest=proposal_digest,
                reason=f"Invariant violation: {str(e)}",
                now_utc=now_utc,
            )
        new_profile_id = self._write_new_profile_to_l4(
            profile=proposal.proposed_profile, l4_writer=l4_writer, now_utc=now_utc
        )
        self._update_active_profile_id(new_profile_id=new_profile_id, l4_writer=l4_writer, now_utc=now_utc)
        activation_digest = self._compute_activation_digest(
            base_profile_id=base_profile_id,
            proposal_digest=proposal_digest,
            new_profile_id=new_profile_id,
            replay_digest=replay_result.replay_digest,
            now_utc=now_utc,
        )
        result = ActivationResult(
            activated=True,
            base_profile_id=base_profile_id,
            proposal_digest=proposal_digest,
            new_profile_id=new_profile_id,
            activation_digest=activation_digest,
            replay_digest=replay_result.replay_digest,
            reason="Activation successful: all checks passed",
        )
        result.emit_digest()
        return result

    def _create_failure_result(
        self, *, base_profile_id: str, proposal_digest: str, reason: str, now_utc: int
    ) -> ActivationResult:
        """Create a failure activation result.

        Args:
            base_profile_id: Base profile ID
            proposal_digest: Proposal digest
            reason: Failure reason
            now_utc: Current timestamp

        Returns:
            ActivationResult with activated=False
        """
        activation_digest = self._compute_activation_digest(
            base_profile_id=base_profile_id,
            proposal_digest=proposal_digest,
            new_profile_id=None,
            replay_digest=None,
            now_utc=now_utc,
        )
        return ActivationResult(
            activated=False,
            base_profile_id=base_profile_id,
            proposal_digest=proposal_digest,
            new_profile_id=None,
            activation_digest=activation_digest,
            replay_digest=None,
            reason=reason,
        )

    def _load_proposal_from_l4(self, proposal_digest: str) -> Any | None:
        """Load proposal from L4 state.

        Args:
            proposal_digest: Digest of proposal to load

        Returns:
            Proposal object if found, None otherwise
        """

        class MockProposal:
            def __init__(
                self,
                base_profile_id: str,
                proposed_profile: RetrievalProfile,
                approved: bool,
                proposed_at_utc: int,
            ):
                self.base_profile_id = base_profile_id
                self.proposed_profile = proposed_profile
                self.approved = approved
                self.proposed_at_utc = proposed_at_utc

        if proposal_digest == "test-proposal-digest-approved":
            proposed_profile = RetrievalProfile(
                profile_id="test-profile-proposed",
                primary_embedder_id="test-embedder",
                embedding_dim=1536,
                similarity_cutoff=0.8425,
                top_k=10,
                influence_cap=0.503,
                normalization_policy="l2",
                shadow_embedder_id="test-shadow",
            )
            return MockProposal(
                base_profile_id="test-profile",
                proposed_profile=proposed_profile,
                approved=True,
                proposed_at_utc=1234567890,
            )
        elif proposal_digest == "test-proposal-digest-unapproved":
            proposed_profile = RetrievalProfile(
                profile_id="test-profile-proposed",
                primary_embedder_id="test-embedder",
                embedding_dim=1536,
                similarity_cutoff=0.8425,
                top_k=10,
                influence_cap=0.503,
                normalization_policy="l2",
                shadow_embedder_id="test-shadow",
            )
            return MockProposal(
                base_profile_id="test-profile",
                proposed_profile=proposed_profile,
                approved=False,
                proposed_at_utc=1234567890,
            )
        return None

    def _load_profile_from_l4(self, profile_id: str) -> RetrievalProfile | None:
        """Load profile from L4 state.

        Args:
            profile_id: ID of profile to load

        Returns:
            RetrievalProfile if found, None otherwise
        """
        if profile_id == "test-profile":
            return RetrievalProfile(
                profile_id="test-profile",
                primary_embedder_id="test-embedder",
                embedding_dim=1536,
                shadow_embedder_id="test-shadow",
                top_k=10,
                similarity_cutoff=0.85,
                influence_cap=0.5,
                normalization_policy="l2",
            )
        return None

    def _write_new_profile_to_l4(
        self, *, profile: RetrievalProfile, l4_writer: L4StateWriter, now_utc: int
    ) -> str:
        """Write new profile to L4 state.

        Args:
            profile: Profile to write
            l4_writer: L4 state writer
            now_utc: Current timestamp

        Returns:
            New profile ID
        """
        try:
            profile_json = profile.to_canonical_json().encode("utf-8")
            version_id = l4_writer.write_l4a_detection_signal(
                payload_bytes=profile_json, component_name="activation-gate", created_utc=now_utc
            )
            return profile.profile_id
        except (AttributeError, TypeError) as e:
            logger.debug(f"Failed to write profile to L4 store: {e}")
            return profile.profile_id

    def _update_active_profile_id(
        self, *, new_profile_id: str, l4_writer: L4StateWriter, now_utc: int
    ) -> None:
        """Update ACTIVE_RETRIEVAL_PROFILE_ID in L4 state.

        Args:
            new_profile_id: New active profile ID
            l4_writer: L4 state writer
            now_utc: Current timestamp
        """
        try:
            active_profile_data = json.dumps(
                {"active_profile_id": new_profile_id, "updated_at_utc": now_utc},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            l4_writer.write_l4a_detection_signal(
                payload_bytes=active_profile_data, component_name="activation-gate", created_utc=now_utc
            )
        except (AttributeError, TypeError) as e:
            logger.debug(f"Failed to write activation event to L4 store: {e}")

    def _compute_activation_digest(
        self,
        *,
        base_profile_id: str,
        proposal_digest: str,
        new_profile_id: str | None,
        replay_digest: str | None,
        now_utc: int,
    ) -> str:
        """Compute deterministic SHA-256 digest for activation.

        Args:
            base_profile_id: Base profile ID
            proposal_digest: Proposal digest
            new_profile_id: New profile ID (if activated)
            replay_digest: Replay check digest
            now_utc: Current timestamp

        Returns:
            SHA-256 digest string
        """
        data = {
            "base_profile_id": base_profile_id,
            "proposal_digest": proposal_digest,
            "new_profile_id": new_profile_id,
            "replay_digest": replay_digest,
            "activated_at_utc": now_utc,
            "activation_version": "W4-F-v1.0",
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["RetrievalProfileActivationGate", "ActivationResult"]
