"""
W4-E Retrieval Profile Proposal System

Stages W4-D advisory recommendations into deterministic proposal sets
requiring explicit approval (HITL) without mutating active profile.
"""

import hashlib
import json
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from system_learning.engines.retrieval_profile import RetrievalProfile


@dataclass(frozen=True, slots=True)
class RetrievalProfileProposal:
    """Deterministic proposal for RetrievalProfile changes.

    Stages W4-D advisory recommendations into explicit proposal sets
    that require human approval before activation.
    """

    base_profile_id: str
    proposed_profile: RetrievalProfile
    recommended_changes: dict[str, float]
    approved: bool
    proposed_at_utc: int
    deterministic_digest: str

    def emit_digest(self) -> None:
        """Print the proposal digest for determinism verification."""
        print(f"W4E-PROPOSAL-DIGEST: {self.deterministic_digest}")

    def to_canonical_json(self) -> str:
        """Convert to canonical JSON for deterministic serialization."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalProfileProposal.to_canonical_json")

        data = {
            "base_profile_id": self.base_profile_id,
            "proposed_profile": json.loads(self.proposed_profile.to_canonical_json()),
            "recommended_changes": {k: round(v, 6) for k, v in self.recommended_changes.items()},
            "approved": self.approved,
            "proposed_at_utc": self.proposed_at_utc,
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def create_approved_copy(self, approved_at_utc: int) -> "RetrievalProfileProposal":
        """Create an approved copy of this proposal.

        Args:
            approved_at_utc: Timestamp when approval was granted

        Returns:
            New proposal with approved=True and updated digest
        """
        approved_proposal = RetrievalProfileProposal(
            base_profile_id=self.base_profile_id,
            proposed_profile=self.proposed_profile,
            recommended_changes=self.recommended_changes,
            approved=True,
            proposed_at_utc=self.proposed_at_utc,
            deterministic_digest=self._compute_approved_digest(approved_at_utc),
        )
        return approved_proposal

    def _compute_approved_digest(self, approved_at_utc: int) -> str:
        """Compute digest for approved proposal."""
        data = {
            "base_profile_id": self.base_profile_id,
            "proposed_profile": json.loads(self.proposed_profile.to_canonical_json()),
            "recommended_changes": {k: round(v, 6) for k, v in self.recommended_changes.items()},
            "approved": True,
            "proposed_at_utc": self.proposed_at_utc,
            "approved_at_utc": approved_at_utc,
            "proposal_version": "W4-E-v1.0",
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def create_proposal_digest(
    base_profile_id: str,
    proposed_profile: RetrievalProfile,
    recommended_changes: dict[str, float],
    proposed_at_utc: int,
) -> str:
    """Compute deterministic SHA-256 digest for proposal.

    Args:
        base_profile_id: ID of the base profile being modified
        proposed_profile: The proposed new profile
        recommended_changes: Dictionary of parameter changes
        proposed_at_utc: Timestamp when proposal was created

    Returns:
        SHA-256 digest string
    """
    data = {
        "base_profile_id": base_profile_id,
        "proposed_profile": json.loads(proposed_profile.to_canonical_json()),
        "recommended_changes": {k: round(v, 6) for k, v in sorted(recommended_changes.items())},
        "approved": False,
        "proposed_at_utc": proposed_at_utc,
        "proposal_version": "W4-E-v1.0",
    }
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


__all__ = ["RetrievalProfileProposal", "create_proposal_digest"]
