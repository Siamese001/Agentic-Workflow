"""Top-level §5 orchestrator — composes the eval spine into an ExitDecision.

Reads sealed artifact data + runtime metadata and produces:
  - a typed ``ExitDecision``
  - optionally an ``EscalationPacket`` when disposition == escalate_hitl

This module is pure logic. It does not call tools, does not mutate state,
and does not issue I/O beyond reading config files (rubric, policy YAMLs).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from agentic_core.L5_safety.eval_spine.budget_envelope import (
    BudgetConsumed,
    BudgetEnvelope,
    BudgetFit,
    check_fit,
)
from agentic_core.L5_safety.eval_spine.claim_extractor import analyze as analyze_claims
from agentic_core.L5_safety.eval_spine.escalation_packet import (
    EscalationPacket,
    EvidenceRef,
    OptionLedgerEntry,
    from_exit_decision,
)
from agentic_core.L5_safety.eval_spine.exit_decision import (
    BudgetReport,
    ExitDecision,
    FinalResponseMetrics,
    HallucinationMetric,
    OutputContractReport,
    QualityVerdict,
    SafetyFlags,
    TrajectoryMetrics,
)
from agentic_core.L5_safety.eval_spine.kill_switch import (
    KillSwitchHit,
    KillSwitchStore,
)
from agentic_core.L5_safety.eval_spine.output_contract_validator import validate
from agentic_core.L5_safety.eval_spine.trace_grader import (
    GraderInput,
    GraderOutput,
    TraceGrader,
)
from agentic_core.L5_safety.eval_spine.trajectory_metrics import compute_all


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class SealedArtifact:
    """Input to ``evaluate_exit`` — shape of an L2 sealed artifact."""

    request_id: str
    trace_id: str
    answer_text: str = ""
    artifact_payload: Any = None
    context_text: str = ""
    predicted_tool_calls: Sequence[Mapping[str, str]] = ()
    retry_count: int = 0
    failure: bool = False
    latency_ms: int = 0
    tokens_consumed: int = 0
    cost_usd_consumed: float = 0.0
    session_id: str | None = None
    tenant: str | None = None
    agent_class: str | None = None
    agent_version: str | None = None


@dataclass(frozen=True)
class ExitEvalPolicy:
    """Policy knobs consumed by ``evaluate_exit``."""

    policy_snapshot: str
    output_contract_ref: str | None = None
    reference_trajectory: Sequence[Mapping[str, str]] | None = None
    single_tool_names: Sequence[str] = ()
    expected_tools: frozenset[str] = frozenset()
    required_tools: frozenset[str] = frozenset()
    forbidden_tools: frozenset[str] = frozenset()
    handoff_required: bool = False
    handoff_fired: bool = False
    instruction_violations: tuple[str, ...] = ()
    policy_hits: tuple[str, ...] = ()
    rubric_version: str | None = None
    calibration_snapshot: str | None = None
    budget_deny_reroute_on_breach: bool = False
    hitl_deadline_seconds: int = 600
    approver_pool_default: str = "runtime_hitl"


@dataclass(frozen=True)
class ExitEvalResult:
    """Bundle returned by ``evaluate_exit``."""

    exit_decision: ExitDecision
    escalation_packet: EscalationPacket | None = None
    grader_output: GraderOutput | None = None
    kill_switch_hit: KillSwitchHit | None = None


def _derive_final_response(
    artifact: SealedArtifact,
) -> FinalResponseMetrics:
    report = analyze_claims(
        artifact.answer_text,
        context_text=artifact.context_text,
        tool_calls=artifact.predicted_tool_calls,
    )
    hallucination = HallucinationMetric(
        score_0_1=report.score_0_1,
        unsupported_claim_count=report.unsupported_claim_count,
        tool_grounded=report.tool_grounded,
    )
    return FinalResponseMetrics(hallucination=hallucination)


def _derive_trajectory(
    artifact: SealedArtifact,
    policy: ExitEvalPolicy,
) -> TrajectoryMetrics:
    metrics = compute_all(
        artifact.predicted_tool_calls,
        policy.reference_trajectory,
        single_tool_names=policy.single_tool_names,
    )
    return TrajectoryMetrics(
        failure=artifact.failure,
        latency_ms=artifact.latency_ms,
        tool_call_count=int(metrics["tool_call_count"]),  # type: ignore[arg-type]
        retry_count=artifact.retry_count,
        exact_match=metrics.get("exact_match"),  # type: ignore[arg-type]
        in_order_match=metrics.get("in_order_match"),  # type: ignore[arg-type]
        any_order_match=metrics.get("any_order_match"),  # type: ignore[arg-type]
        precision=metrics.get("precision"),  # type: ignore[arg-type]
        recall=metrics.get("recall"),  # type: ignore[arg-type]
        single_tool_use=metrics.get("single_tool_use"),  # type: ignore[arg-type]
    )


def _derive_budget(
    artifact: SealedArtifact,
    envelope: BudgetEnvelope,
) -> tuple[BudgetReport, BudgetFit]:
    consumed = BudgetConsumed(
        tokens=artifact.tokens_consumed,
        latency_ms=artifact.latency_ms,
        tool_calls=len(artifact.predicted_tool_calls),
        cost_usd=artifact.cost_usd_consumed,
    )
    fit = check_fit(consumed, envelope)
    report = BudgetReport(
        budget_fit=fit.budget_fit,
        tokens_envelope=envelope.tokens_max,
        tokens_consumed=consumed.tokens,
        latency_envelope_ms=envelope.latency_ms_max,
        latency_consumed_ms=consumed.latency_ms,
        tool_calls_envelope=envelope.tool_calls_max,
        tool_calls_consumed=consumed.tool_calls,
        cost_usd_envelope=envelope.cost_usd_max,
        cost_usd_consumed=consumed.cost_usd,
    )
    return report, fit


def _decide_disposition_and_reason(
    grader: GraderOutput,
    budget_fit: BudgetFit,
    output_contract: OutputContractReport,
    kill_hit: KillSwitchHit,
    policy: ExitEvalPolicy,
) -> tuple[str, str]:
    if kill_hit.hit:
        return ("deny_reroute" if kill_hit.on_hit == "deny_reroute" else "escalate_hitl",
                "grader.policy_halt")
    if grader.safety_violated:
        return "escalate_hitl", "grader.safety_violation"
    if not output_contract.required_form_satisfied and output_contract.contract_ref:
        return "deny_reroute", "grader.output_contract_fail"
    if grader.aggregate_verdict == "unknown":
        return "escalate_hitl", "grader.unknown_budget_exceeded"
    if not budget_fit.budget_fit:
        disposition = (
            "deny_reroute" if policy.budget_deny_reroute_on_breach else "escalate_hitl"
        )
        return disposition, "grader.budget_breach"
    if grader.instruction_violated:
        return "deny_reroute", "grader.instruction_violation"
    if grader.aggregate_verdict == "fail":
        return "deny_reroute", "grader.quality_fail"
    if grader.aggregate_verdict == "warn":
        return "allow_finish", "grader.ok"
    return "allow_finish", "grader.ok"


def _quality_verdict(grader: GraderOutput, budget_fit: BudgetFit) -> QualityVerdict:
    verdict: str = grader.aggregate_verdict
    if not budget_fit.budget_fit and verdict == "pass":
        verdict = "warn"
    if grader.safety_violated:
        verdict = "fail"
    narrowed: Any = verdict  # Literal narrowing handled by QualityVerdict's schema.
    numeric_scores = [
        float(r.score)
        for r in grader.per_dim
        if isinstance(r.score, (int, float))
    ]
    weighted = (sum(numeric_scores) / (5.0 * len(numeric_scores))) if numeric_scores else None
    return QualityVerdict(
        verdict=narrowed,
        weighted_score_0_1=weighted,
        confidence_0_1=1.0 - grader.unknown_fraction,
        unknown_fraction=grader.unknown_fraction,
    )


def evaluate_exit(
    artifact: SealedArtifact,
    envelope: BudgetEnvelope,
    policy: ExitEvalPolicy,
    *,
    kill_switch_store: KillSwitchStore | None = None,
    grader: TraceGrader | None = None,
) -> ExitEvalResult:
    """Produce an ExitDecision (and optional EscalationPacket) for a run."""
    final_response = _derive_final_response(artifact)
    trajectory = _derive_trajectory(artifact, policy)
    budget_report, budget_fit = _derive_budget(artifact, envelope)
    contract_result = validate(artifact.artifact_payload or artifact.answer_text,
                               policy.output_contract_ref)
    output_contract = OutputContractReport(
        required_form_satisfied=contract_result.required_form_satisfied,
        contract_ref=contract_result.contract_ref,
        violations=contract_result.violations,
    )

    ks_hit = KillSwitchHit(hit=False)
    if kill_switch_store is not None:
        ks_hit = kill_switch_store.hit(
            context={
                "tenant": artifact.tenant,
                "agent_class": artifact.agent_class,
            },
            request_id=artifact.request_id,
            trace_id=artifact.trace_id,
            policy_snapshot=policy.policy_snapshot,
        )

    active_grader = grader or TraceGrader()
    grader_input = GraderInput(
        sealed_artifact_text=artifact.answer_text,
        predicted_tool_calls=tuple(artifact.predicted_tool_calls),
        expected_tools=policy.expected_tools,
        required_tools=policy.required_tools,
        forbidden_tools=policy.forbidden_tools,
        handoff_required=policy.handoff_required,
        handoff_fired=policy.handoff_fired,
        instruction_violations=policy.instruction_violations,
        policy_hits=policy.policy_hits,
        budget_fit=budget_fit.budget_fit,
        retry_count=artifact.retry_count,
        context_text=artifact.context_text,
        calibration_snapshot=policy.calibration_snapshot,
    )
    grader_output = active_grader.grade(grader_input)

    disposition, reason_code = _decide_disposition_and_reason(
        grader_output, budget_fit, output_contract, ks_hit, policy
    )

    severity = grader_output.policy_hits and "high" or None
    if ks_hit.hit:
        severity = "critical"
    elif not budget_fit.budget_fit:
        severity = budget_fit.severity_band

    safety = SafetyFlags(
        policy_violation=grader_output.safety_violated,
        instruction_violation=grader_output.instruction_violated,
        policy_halt=ks_hit.hit,
        violated_rules=grader_output.policy_hits,
        severity_band=severity,  # type: ignore[arg-type]
    )
    quality = _quality_verdict(grader_output, budget_fit)

    decision = ExitDecision(
        request_id=artifact.request_id,
        trace_id=artifact.trace_id,
        emitted_at_utc=_utcnow_iso(),
        disposition=disposition,  # type: ignore[arg-type]
        reason_code=reason_code,
        final_response=final_response,
        trajectory=trajectory,
        safety=safety,
        budget=budget_report,
        quality=quality,
        output_contract=output_contract,
        session_id=artifact.session_id,
        tenant=artifact.tenant,
        agent_class=artifact.agent_class,
        agent_version=artifact.agent_version,
        policy_snapshot=policy.policy_snapshot,
        rubric_version=policy.rubric_version,
        judge_calibration_snapshot=policy.calibration_snapshot,
    )

    packet: EscalationPacket | None = None
    if decision.disposition == "escalate_hitl":
        packet = _mint_escalation(decision, reason_code, policy, ks_hit)

    return ExitEvalResult(
        exit_decision=decision,
        escalation_packet=packet,
        grader_output=grader_output,
        kill_switch_hit=ks_hit,
    )


def _mint_escalation(
    decision: ExitDecision,
    reason_code: str,
    policy: ExitEvalPolicy,
    ks_hit: KillSwitchHit,
) -> EscalationPacket:
    hitl_class = _map_reason_to_hitl_class(reason_code, decision)
    evidence: tuple[EvidenceRef, ...] = (
        EvidenceRef(kind="exit_decision", ref=decision.trace_id, summary=reason_code),
        EvidenceRef(kind="trajectory", ref=decision.trace_id),
    )
    options: tuple[OptionLedgerEntry, ...] = (
        OptionLedgerEntry(
            label="approve",
            description="Approve as-is and proceed.",
            recommendation="alternative",
            confidence_0_1=0.5,
            reversibility="action",
        ),
        OptionLedgerEntry(
            label="modify",
            description="Request modification and re-evaluation.",
            recommendation="recommended",
            confidence_0_1=0.7,
            reversibility="action",
        ),
        OptionLedgerEntry(
            label="reject",
            description="Reject and route back to a safer path.",
            recommendation="fallback",
            confidence_0_1=0.6,
            reversibility="read",
        ),
    )
    reason_detail = (
        f"Escalated because reason_code={reason_code}; "
        f"verdict={decision.quality.verdict}; "
        f"ks_hit={ks_hit.hit}"
    )
    return from_exit_decision(
        decision,
        hitl_class=hitl_class,
        reason_detail=reason_detail,
        evidence_refs=evidence,
        options_ledger=options,
        approver_pool=policy.approver_pool_default,
        fallback_directive="hold",
        deadline_seconds=policy.hitl_deadline_seconds,
        policy_snapshot=policy.policy_snapshot,
    )


def _map_reason_to_hitl_class(reason_code: str, _decision: ExitDecision) -> str:
    if reason_code == "grader.safety_violation":
        return "safety"
    if reason_code == "grader.policy_halt":
        return "policy_override"
    if reason_code == "grader.budget_breach":
        return "low_confidence"
    if reason_code == "grader.unknown_budget_exceeded":
        return "low_confidence"
    # Default: novel_context for anything else that reaches escalation.
    return "novel_context"


__all__ = [
    "ExitEvalPolicy",
    "ExitEvalResult",
    "SealedArtifact",
    "evaluate_exit",
]
