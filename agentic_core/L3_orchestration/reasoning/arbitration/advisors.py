"""
Multi-Agent Advisors

Pure function advisors that provide deterministic recommendations.
No I/O, no side effects, fully deterministic outputs.
"""

from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

from .arbitration_contract import AdvisorProposal


def risk_averse_advisor(task: dict[str, str]) -> AdvisorProposal:
    """Risk-averse advisor that prioritizes safety.

    Args:
        task: Task dictionary with task details

    Returns:
        AdvisorProposal with risk-averse recommendation
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "risk_averse_advisor", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "risk_averse_advisor", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "risk_averse_advisor")
    task_kind = task.get("task_kind", "unknown")
    if task_kind == "planning":
        decision = "create_detailed_plan"
        rationale = [
            "Detailed planning reduces uncertainty",
            "Step-by-step approach minimizes errors",
            "Documentation enables review",
        ]
        risks = ["Planning may take longer", "Over-planning can delay execution"]
        artifacts = ["plan.md", "checklist.md"]
        confidence = 85
    elif task_kind == "execution":
        decision = "execute_with_validation"
        rationale = [
            "Validation catches errors early",
            "Incremental execution reduces risk",
            "Rollback capability preserved",
        ]
        risks = ["Validation adds overhead", "Slower than direct execution"]
        artifacts = ["validation_log.json", "rollback_plan.md"]
        confidence = 90
    else:
        decision = "proceed_with_caution"
        rationale = ["Unknown task type requires caution", "Conservative approach minimizes risk"]
        risks = ["May be overly conservative", "Could miss optimization opportunities"]
        artifacts = ["risk_assessment.md"]
        confidence = 70
    return AdvisorProposal(
        advisor_id="risk_averse",
        decision=decision,
        confidence=confidence,
        rationale=rationale,
        risks=risks,
        artifacts=artifacts,
    )


def throughput_advisor(task: dict[str, str]) -> AdvisorProposal:
    """Throughput advisor that prioritizes speed and efficiency.

    Args:
        task: Task dictionary with task details

    Returns:
        AdvisorProposal with throughput-focused recommendation
    """
    task_kind = task.get("task_kind", "unknown")
    if task_kind == "planning":
        decision = "create_minimal_plan"
        rationale = [
            "Minimal planning enables faster start",
            "Just-in-time detail collection",
            "Iterative refinement possible",
        ]
        risks = ["May miss important details", "Requires more adaptation during execution"]
        artifacts = ["minimal_plan.md"]
        confidence = 75
    elif task_kind == "execution":
        decision = "execute_directly"
        rationale = ["Direct execution is fastest", "No validation overhead", "Maximum throughput"]
        risks = ["Errors may propagate further", "Harder to rollback changes"]
        artifacts = ["execution_log.json"]
        confidence = 80
    else:
        decision = "proceed_optimally"
        rationale = ["Optimal approach maximizes efficiency", "Assumes reasonable risk tolerance"]
        risks = ["May underestimate risks", "Could require rework"]
        artifacts = ["optimization_plan.md"]
        confidence = 65
    return AdvisorProposal(
        advisor_id="throughput",
        decision=decision,
        confidence=confidence,
        rationale=rationale,
        risks=risks,
        artifacts=artifacts,
    )


ADVISORS: dict[str, callable] = {"risk_averse": risk_averse_advisor, "throughput": throughput_advisor}


def get_available_advisors() -> list[str]:
    """Get list of available advisor IDs.

    Returns:
        List of advisor IDs in deterministic order
    """
    return sorted(ADVISORS.keys())


def run_advisor(advisor_id: str, task: dict[str, str]) -> AdvisorProposal:
    """Run a single advisor and return its proposal.

    Args:
        advisor_id: ID of advisor to run
        task: Task dictionary

    Returns:
        AdvisorProposal from the advisor

    Raises:
        ValueError: If advisor_id is not recognized
    """
    if advisor_id not in ADVISORS:
        raise ValueError(f"Unknown advisor: {advisor_id}")
    advisor_func = ADVISORS[advisor_id]
    proposal = advisor_func(task)
    if proposal.advisor_id != advisor_id:
        raise ValueError(f"Advisor {advisor_id} returned proposal with wrong ID: {proposal.advisor_id}")
    return proposal
