"""
Advisor Execution Harness

Side-effect free execution of multiple advisors with validation.
Ensures deterministic outputs and contract compliance.
"""

from __future__ import annotations

from .advisors import get_available_advisors, run_advisor
from .arbitration_contract import AdvisorProposal


def run_advisors(task_dict: dict[str, str], advisor_ids: list[str]) -> list[AdvisorProposal]:
    """Run multiple advisors and return their proposals.

    Args:
        task_dict: Task description dictionary
        advisor_ids: List of advisor IDs to run

    Returns:
        List of AdvisorProposal objects

    Raises:
        ValueError: If any advisor_id is invalid
    """
    proposals = []

    for advisor_id in advisor_ids:
        # Validate advisor ID
        available = get_available_advisors()
        if advisor_id not in available:
            raise ValueError(f"Invalid advisor_id: {advisor_id}. Available: {available}")

        # Run advisor
        proposal = run_advisor(advisor_id, task_dict)

        # Validate proposal against contract
        _validate_proposal(proposal)

        proposals.append(proposal)

    return proposals


def _validate_proposal(proposal: AdvisorProposal) -> None:
    """Validate proposal meets contract requirements.

    Args:
        proposal: Proposal to validate

    Raises:
        ValueError: If proposal violates contract
    """
    # Basic validation is already done in AdvisorProposal.__post_init__

    # Additional validation for non-empty decision
    if not proposal.decision.strip():
        raise ValueError(f"Advisor {proposal.advisor_id} returned empty decision")

    # Validate confidence is in valid range
    if not (0 <= proposal.confidence <= 100):
        raise ValueError(f"Advisor {proposal.advisor_id} returned invalid confidence: {proposal.confidence}")

    # Validate rationale items are non-empty
    for i, rationale in enumerate(proposal.rationale):
        if not rationale.strip():
            raise ValueError(f"Advisor {proposal.advisor_id} returned empty rationale item at index {i}")

    # Validate risk items are non-empty
    for i, risk in enumerate(proposal.risks):
        if not risk.strip():
            raise ValueError(f"Advisor {proposal.advisor_id} returned empty risk item at index {i}")

    # Validate artifact items are non-empty
    for i, artifact in enumerate(proposal.artifacts):
        if not artifact.strip():
            raise ValueError(f"Advisor {proposal.advisor_id} returned empty artifact item at index {i}")


def run_all_advisors(task_dict: dict[str, str]) -> list[AdvisorProposal]:
    """Run all available advisors.

    Args:
        task_dict: Task description dictionary

    Returns:
        List of AdvisorProposal objects from all advisors
    """
    advisor_ids = get_available_advisors()
    return run_advisors(task_dict, advisor_ids)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "run_advisors",
    "run_all_advisors",
]
