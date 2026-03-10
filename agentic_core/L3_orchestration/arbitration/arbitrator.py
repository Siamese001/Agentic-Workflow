"""
Multi-Agent Arbitrator

Deterministic scoring and tie-breaking system for multi-agent arbitration.
Implements fixed scoring rules with deterministic selection.
"""

from __future__ import annotations

from .arbitration_contract import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AdvisorProposal,
    ArbitrationDecision,
    ArbitrationInput,
)


class Arbitrator:
    """Deterministic arbitrator for multi-agent decisions."""

    def __init__(self):
        """Initialize arbitrator with default scoring rules."""
        pass

    def calculate_score(self, proposal: AdvisorProposal) -> int:
        """Calculate deterministic score for a proposal.

        Scoring rules:
        - Base = confidence
        - +2 per rationale item (cap 10)
        - -3 per risk item (cap 15)
        - +1 per artifact (cap 5)

        Args:
            proposal: Advisor proposal to score

        Returns:
            Calculated score
        """
        score = proposal.confidence

        # Add rationale bonus (capped at 10)
        rationale_bonus = min(len(proposal.rationale) * 2, 10)
        score += rationale_bonus

        # Subtract risk penalty (capped at 15)
        risk_penalty = min(len(proposal.risks) * 3, 15)
        score -= risk_penalty

        # Add artifact bonus (capped at 5)
        artifact_bonus = min(len(proposal.artifacts) * 1, 5)
        score += artifact_bonus

        return score

    def arbitrate(self, input_data: ArbitrationInput) -> ArbitrationDecision:
        """Perform deterministic arbitration on proposals.

        Args:
            input_data: Arbitration input with proposals

        Returns:
            Selected decision with score breakdown

        Raises:
            ValueError: If no proposals provided
        """
        if not input_data.proposals:
            raise ValueError("No proposals provided for arbitration")

        # Calculate scores for all proposals
        scored_proposals = []
        score_breakdown = {}

        for proposal in input_data.proposals:
            score = self.calculate_score(proposal)
            scored_proposals.append((score, proposal))
            score_breakdown[proposal.advisor_id] = score

        # Sort by deterministic tie-break order:
        # 1) Higher score
        # 2) Higher confidence
        # 3) Lexicographically smallest advisor_id
        scored_proposals.sort(
            key=lambda x: (
                -x[0],  # Negative for descending score
                -x[1].confidence,  # Negative for descending confidence
                x[1].advisor_id,  # Ascending advisor_id
            )
        )

        # Select best proposal
        best_score, best_proposal = scored_proposals[0]

        # Merge rationale and risks from all proposals (deterministic ordering)
        all_rationale = []
        all_risks = []

        for _, proposal in scored_proposals:
            all_rationale.extend(proposal.rationale)
            all_risks.extend(proposal.risks)

        # Sort for deterministic output
        merged_rationale = sorted(set(all_rationale))  # Remove duplicates, sort
        merged_risks = sorted(set(all_risks))  # Remove duplicates, sort

        return ArbitrationDecision(
            selected_advisor_id=best_proposal.advisor_id,
            selected_decision=best_proposal.decision,
            score_breakdown=score_breakdown,
            merged_rationale=merged_rationale,
            merged_risks=merged_risks,
        )


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "Arbitrator",
]
