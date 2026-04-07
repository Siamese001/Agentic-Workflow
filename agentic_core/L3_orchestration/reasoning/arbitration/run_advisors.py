"""
Advisor Execution Harness

Side-effect free execution of multiple advisors with validation.
Ensures deterministic outputs and contract compliance.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

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
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "run_advisors", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "run_advisors", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "run_advisors")
    proposals = []
    for advisor_id in advisor_ids:
        available = get_available_advisors()
        if advisor_id not in available:
            raise ValueError(f"Invalid advisor_id: {advisor_id}. Available: {available}")
        proposal = run_advisor(advisor_id, task_dict)
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
    if not proposal.decision.strip():
        raise ValueError(f"Advisor {proposal.advisor_id} returned empty decision")
    if not 0 <= proposal.confidence <= 100:
        raise ValueError(f"Advisor {proposal.advisor_id} returned invalid confidence: {proposal.confidence}")
    for i, rationale in enumerate(proposal.rationale):
        if not rationale.strip():
            raise ValueError(f"Advisor {proposal.advisor_id} returned empty rationale item at index {i}")
    for i, risk in enumerate(proposal.risks):
        if not risk.strip():
            raise ValueError(f"Advisor {proposal.advisor_id} returned empty risk item at index {i}")
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


__all__ = ["run_advisors", "run_all_advisors"]
