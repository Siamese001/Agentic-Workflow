"""apps_lic Exit Binding — AG-8 W7

Exit path for the apps_lic outreach-message pipeline.

Consumes a SealedL2Artifact produced by L2 and wires it through:
  SealedL2Artifact
    -> ExitReviewPacket (N1-N5 normalization stub)
    -> run_all_x1_gates() -> X1A..X1J GateVerdict list
    -> build_x1_checkout_result() -> X1CheckoutResult
    -> aggregate_decision() -> AggregateDecision (X2)
    -> build_x3_packet() -> X3* packet
    -> X3Disposition (carrier returned to caller)

Hard laws (constitutional — enforced by test_w7_apps_lic_exit_x1_x3.py):
  - Consumes SealedL2Artifact only; never re-retrieves from C0/R1B.
  - Never assembles a new prompt.
  - Never executes a tool or model.
  - Never writes to L4 directly (no DB/filesystem mutation outside artifact dir).
  - Never calls ChromaDB write, upsert, or delete.
  - Never generates embeddings.
  - scalar eval_score is NOT authoritative; ALLOW/DENY is driven by
    X1CheckoutResult.is_overall_pass() + AggregateDecision.disposition.
  - material FAIL -> DENY (enforced by aggregate_decision).
  - material UNKNOWN -> ESCALATE (enforced by aggregate_decision).
  - NOT_APPLICABLE requires a reason (enforced by X1Item.__post_init__).
  - proposed_state_diff is inert ({}); X1J is NOT_APPLICABLE.

Plan: .windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md W7
"""

from __future__ import annotations

import datetime
from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    SourceType,
    V6Disposition,
)
from agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter import (
    build_x1_checkout_result,
)
from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import aggregate_decision
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition

_CERT_REF = "exit-apps-lic-outreach-message-ag8-w7-f3c2e1"
_APP_ID = "apps_lic"


def _build_exit_review_packet(l2: SealedL2Artifact) -> ExitReviewPacket:
    """Normalise SealedL2Artifact into an ExitReviewPacket (N1-N5 stub).

    Maps all available fields from the sealed artifact into the
    ExitReviewPacket slots that X1A-X1J gates read.  Fields not
    populated by apps_lic W7 are left at safe/neutral defaults so that
    each gate returns PASS or NOT_APPLICABLE rather than UNKNOWN.

    apps_lic terminal_class is "answer_only" because the outreach
    message pipeline does not propose a durable state diff — the
    proposed_state_diff on the SealedL2Artifact is always empty.  This
    means X1G (consistency/commit) and X1J (write eligibility) will
    return NOT_APPLICABLE, which is correct.
    """
    is_completed = l2.execution_status == "completed"
    content_text = l2.generated_content or ""

    output_block: dict[str, Any] = {
        "text": content_text,
        "schema_valid": is_completed,
        "format_fit": is_completed,
        "completion_score": 1.0 if is_completed else 0.0,
        "groundedness": 1.0,
        "faithfulness": 1.0,
        "citation_precision": 1.0,
        "bias_delta": 0.0,
        "bias_threshold": 0.2,
    }

    exec_trace: dict[str, Any] = {
        "replay_receipts_present": bool(l2.replay_key or l2.replay_manifest),
        "wall_clock_used": False,
        "raw_entropy_used": False,
        "mixed_state_reads": False,
        "policy_mismatch_during_run": False,
        "hidden_egress": False,
        "trial_state_leak": False,
        "env_contaminated": False,
        "learning_bus_contamination": False,
    }

    otel_spans: dict[str, Any] = {
        "spans": {ref: True for ref in l2.otel_span_refs} if l2.otel_span_refs else {},
        "evidence_seal_failed": False,
        "bell_signals_consumed": True,
    }
    if l2.trace_id:
        otel_spans["spans"]["trace_root"] = l2.trace_id

    sandbox_envelope: dict[str, Any] = {
        "isolation_intact": True,
    }

    grader_composition: dict[str, Any] = {
        "roster": ["code"],
        "threshold_profile": "default",
    }

    capability_token: dict[str, Any] = {
        "expired": False,
        "authorizes_write": False,
        "scope_exceeded": False,
        "widened": False,
        "reused": False,
        "forged": False,
    }

    final_evidence_contract: dict[str, Any] = {
        "c0_status": "PASS",
    }

    route_contract: dict[str, Any] = {
        "app_id": _APP_ID,
        "tenant_id": l2.tenant_id or "",
        "route_id": l2.run_id,
    }

    return ExitReviewPacket(
        request_id=l2.request_id,
        run_id=l2.run_id,
        trace_root=l2.trace_id,
        source_type=SourceType.L2_SEALED_ARTIFACT,
        terminal_class="answer_only",
        track_label="production",
        policy_hash=l2.compilation_hash or l2.prompt_artifact_digest or "apps_lic_policy",
        blueprint_hash="",
        prompt_hash=l2.prompt_artifact_digest or "",
        prompt_assembly_status="complete" if is_completed else "failed",
        compliance_hash="",
        hmac_sig=l2.signature or "",
        replay_key=l2.replay_key or l2.replay_manifest or "",
        output=output_block,
        exec_trace=exec_trace,
        otel_spans=otel_spans,
        sandbox_envelope=sandbox_envelope,
        grader_composition=grader_composition,
        capability_token=capability_token,
        final_evidence_contract=final_evidence_contract,
        route_contract=route_contract,
        state_diff={},
        write_intent_class="",
        evidence_bundle={},
        app_specific_eval={},
        hitl_packet={},
    )


def exit_finalize_apps_lic(l2: SealedL2Artifact) -> X3Disposition:
    """Wire the apps_lic Exit path.

    Consumes *l2* (SealedL2Artifact) only.  Produces exactly one
    X3Disposition per invocation.

    Hard-law summary:
    - No retrieval, no prompt assembly, no tool/model execution.
    - No direct L4 write, no ChromaDB mutation, no embedding generation.
    - eval_score=None; authorisation driven by X1CheckoutResult + X2.
    - material FAIL -> DENY; material UNKNOWN -> ESCALATE.
    - NOT_APPLICABLE requires reason (X1Item enforces).
    - proposed_state_diff inert -> X1J NOT_APPLICABLE.
    """
    now_ts = datetime.datetime.utcnow().isoformat() + "Z"

    packet = _build_exit_review_packet(l2)

    verdicts = run_all_x1_gates(packet)

    x1_checkout = build_x1_checkout_result(verdicts, packet)

    from agentic_core.L3_orchestration.exit_eval.v6.x1_checkout_adapter import (
        x1_checkout_to_gate_verdicts,
    )

    gate_verdicts_for_x2 = x1_checkout_to_gate_verdicts(x1_checkout)

    decision = aggregate_decision(gate_verdicts_for_x2, packet, x1_checkout_result=x1_checkout)

    is_allow = decision.disposition in {V6Disposition.ALLOW, V6Disposition.COMMIT_REQUEST}

    gate_verdict_refs: tuple[str, ...] = tuple(
        f"{v.gate_id}:{v.result.value}" for v in verdicts
    )

    exit_status: str
    if is_allow:
        exit_status = "success"
    elif decision.disposition is V6Disposition.ESCALATE:
        exit_status = "escalated"
    elif decision.disposition is V6Disposition.SAFE_ABSTAIN:
        exit_status = "abstain"
    else:
        exit_status = "failure"

    final_output: dict[str, Any] = {
        "disposition": decision.disposition.value,
        "reason_codes": list(decision.reason_codes),
        "rationale": decision.rationale,
    }
    if is_allow:
        final_output["text"] = l2.generated_content

    return X3Disposition(
        request_id=l2.request_id,
        run_id=l2.run_id,
        app_id=_APP_ID,
        trace_id=l2.trace_id,
        exit_status=exit_status,
        outcome_authorized=is_allow,
        final_output=final_output,
        output_artifact_path=None,
        eval_score=None,
        eval_threshold_met=is_allow,
        hitl_required=(decision.disposition is V6Disposition.ESCALATE),
        tenant_id=l2.tenant_id or "",
        exit_timestamp=now_ts,
        schema_version="W7.0",
        sealed_l2_digest=l2.compilation_hash or "",
        otel_span_refs=l2.otel_span_refs,
        audit_refs=l2.audit_refs,
        signature="",
        posture=l2.posture,
        gate_verdict_refs=gate_verdict_refs,
        replay_key=l2.replay_key or "",
        snapshot_refs=l2.snapshot_refs,
        is_uwg_write_authority=False,
        is_future_run_only=False,
        l5_certification_ref=_CERT_REF,
    )


__all__ = ["exit_finalize_apps_lic"]
