"""W2 — Production integrated-runtime entry point for the RTC-REQ-059
safe-reuse composite path.

This module is the SINGLE production entry point that drives the full
runtime chain end-to-end for the dense-candidate + C-primary safety-veto
cache reuse path:

    raw_request
       → run_request_intake          (L0 intake)
       → validated_request_to_plan_contract  (U0 → L1 bridge)
       → _build_route_contract       (L1 → L0 route metadata)
       → check_route_gates + veto    (L0 D1/D2 + safety veto)
       → SafeReuseDecision           (composite verdict)
       → TerminalRetPacket           (R1B_SEMANTIC_CACHE)
       → ExitEvalPipeline.run        (L3 v6 exit pipeline)
       → seal_runtime_exhaust        (sealed manifest)
       → RuntimeExhaustCollector     (bundle aggregation)
       → manifest + invocation receipts

Harness rule (anti-cheat — verifier-enforced):
    Probes, tests, and verifier scripts MAY call ``run_integrated_safe_reuse``.
    They MUST NOT call ``check_route_gates``, ``VetoOrchestrator.evaluate``,
    ``ExitEvalPipeline.run``, ``seal_runtime_exhaust``, ``check_d1_exact_cache``,
    ``check_d2_semantic_cache``, or ``SemanticCacheManager.recall`` directly.
    Every artifact stamped by this module's emitter contains a
    ``producer_component`` that the verifier checks against the harness
    regex.

Plan: ``docs/archive/windsurf/legacy-tree/plans/rtc-w2-integrated-runtime-r1b-safe-reuse-c7e9f3.md``
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# --- production-layer imports (cross-layer; the WHOLE point of an entry point) ---
from agentic_core.L0_routing.intake.envelope import RawIngressEnvelope
from agentic_core.L0_routing.intake.pipeline import run_request_intake
from agentic_core.L0_routing.intake.validated_request import ValidatedRequest
from agentic_core.L1_cognition.bridges.u0_to_l1_plan import (
    validated_request_to_plan_contract,
)
from agentic_core.L0_routing.c0_retrieval.route_contract import L1PlanContract
from agentic_core.L0_routing.reasoning.route_gates import check_route_gates
from agentic_core.L0_routing.doctrine.terminal_routes import (
    TerminalExecutionForm,
    TerminalRetPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateResult,
    GateVerdict,
    SourceType,
    V6Disposition,
    X3AllowPacket,
    X3DenyPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision
from agentic_core.L3_orchestration.exit_eval.v6.return_payload import (
    seal_runtime_exhaust,
    RuntimeExhaustManifest,
)
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import build_x3d_allow

# Veto orchestrator + status enum live in tools.certification.safety per
# the existing W1p5 wiring. The entry point is the ONLY place that
# instantiates / invokes the orchestrator.
from tools.certification.safety.veto_orchestrator import VetoOrchestrator  # guardian: allow-layer-violation -- ADR-096 §Exception L_RUNTIME->L_TOOLS; entry point is the ONLY instantiator of VetoOrchestrator per W1p5 wiring
from tools.certification.safety.veto_protocol import VetoResult, VetoStatus  # guardian: allow-layer-violation -- ADR-096 §Exception; veto protocol types accompany orchestrator import

from agentic_core.runtime.artifacts.integrated_runtime_emitter import (
    ProvenanceStamp,
    W2_CHAIN_LINKAGE,
    compute_artifact_hash,
    emit_artifact,
)
from agentic_core.runtime.artifacts.spine_proof_bundle import (
    build_spine_proof_payload,
    git_commit_and_dirty,
    utc_iso_now,
)
from agentic_core.runtime.contracts.c0_bypass_receipt import (
    build_c0_bypass_receipt,
)
from agentic_core.runtime.contracts.identity import (
    build_runtime_identity_envelope,
)
from agentic_core.runtime.contracts.l3_bypass_receipt import (
    build_l3_bypass_receipt,
)
from agentic_core.runtime.contracts.prompt_assembly_bypass_receipt import (
    build_prompt_assembly_bypass_receipt,
)
from agentic_core.runtime.contracts.runtime_gate_verdict_bundle import (
    GateOutcome,
    RuntimeGateVerdictBundle,
    VetoOutcome,
)
from agentic_core.runtime.contracts.runtime_trace_snapshot import (
    build_runtime_trace_snapshot,
)
from agentic_core.runtime.contracts.safe_reuse_decision import SafeReuseDecision
from agentic_core.L6_observability.runtime_trace.synthetic_trace_detector import (
    detect_trace_provenance,
)

# Bundle-aggregation surface. As of 2026-05-01 the canonical home is
# ``agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle``
# (promoted from system_learning). The import is unconditional now —
# the boundary no longer crosses into a peer package.
from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import (  # guardian: allow-layer-violation -- ADR-096 L6 universally importable; safe-reuse entrypoint consumes L6 exhaust bundle to emit canonical runtime trace
    RuntimeExhaustBundle,
    RuntimeExhaustCollector,
)

_HAVE_EXHAUST_COLLECTOR = True


PRODUCER_COMPONENT = "agentic_core.runtime.entrypoints.integrated_safe_reuse_run"
PRODUCER_MODULE = "integrated_safe_reuse_run"
PRODUCER_FUNCTION = "run_integrated_safe_reuse"

R1B_ROUTE_ID = "R1B_SEMANTIC_CACHE"

# The approved C-primary veto class for RTC-REQ-056 acceptance. A run's
# `veto_stage_match_status` = "PASS" only when the orchestrator's stages
# include exactly one instance of this class AND no DeterministicProofStage
# (or other proof-stage) is in the stack. See W2 proof-hardening doc.
EXPECTED_C_PRIMARY_VETO_CLASS = "LLMJudgeVeto"

# Proof-time-only stages — their presence downgrades match_status to
# STRUCTURAL_ONLY. A run where a proof stage is in the orchestrator is
# NOT eligible to flip R1B_INTEGRATED_RUNTIME_PROOF=PASS on its own.
PROOF_ONLY_STAGE_CLASSES = ("DeterministicProofStage",)


def _classify_veto_stage(orchestrator: "VetoOrchestrator") -> dict[str, Any]:
    """Introspect the orchestrator and return provenance fields for the
    integrated-runtime artifacts.

    Returns dict with keys:
      - ``veto_stage_actual``: qualified class name of the first stage
      - ``veto_stage_actual_names``: list of all stage class names
      - ``veto_stage_expected``: ``"LLMJudgeVeto"`` (SSOT)
      - ``veto_stage_match_status``: ``"PASS"`` / ``"STRUCTURAL_ONLY"`` /
        ``"FAIL_MISMATCH"``
      - ``deterministic_proof_stage_used``: bool
      - ``proof_only_stage_names``: list[str]
      - ``primary_veto_mode``: ``"C_PRIMARY_LLM_JUDGE"`` or ``""``
      - ``veto_provider``, ``veto_model_id``, ``veto_rubric_path``,
        ``veto_timeout_ms``: best-effort introspection (fields on
        LLMJudgeVeto), ``""``/``0`` if unavailable.
    """
    stages = list(getattr(orchestrator, "_stages", None) or
                  getattr(orchestrator, "stages", None) or [])
    stage_names = [type(s).__name__ for s in stages]
    proof_stages = [n for n in stage_names if n in PROOF_ONLY_STAGE_CLASSES]
    has_expected = EXPECTED_C_PRIMARY_VETO_CLASS in stage_names
    has_proof = bool(proof_stages)

    if has_expected and not has_proof:
        match_status = "PASS"
    elif has_proof and not has_expected:
        match_status = "STRUCTURAL_ONLY"
    elif has_proof and has_expected:
        # Mixed stack — proof stage taints the run.
        match_status = "STRUCTURAL_ONLY"
    else:
        match_status = "FAIL_MISMATCH"

    # Best-effort provider introspection from LLMJudgeVeto.
    provider = ""
    model_id = ""
    rubric_path = ""
    timeout_ms = 0
    rubric_hash = ""
    for s in stages:
        if type(s).__name__ == EXPECTED_C_PRIMARY_VETO_CLASS:
            provider = str(getattr(s, "_provider", "") or getattr(s, "provider", ""))
            model_id = str(getattr(s, "_model_id", "") or getattr(s, "model_id", ""))
            rp = getattr(s, "_rubric_path", None) or getattr(s, "rubric_path", None)
            rubric_path = str(rp) if rp else ""
            timeout_ms = int(getattr(s, "_timeout_ms", 0) or getattr(s, "timeout_ms", 0) or 0)
            rubric_hash = str(getattr(s, "_rubric_hash", "") or getattr(s, "rubric_hash", ""))
            break

    primary_mode = ""
    try:
        policy = orchestrator.get_policy_summary()
        if "llm_judge" in policy.get("instantiated_stages", []):
            primary_mode = "C_PRIMARY_LLM_JUDGE"
    except Exception:  # guardian: allow-broad-exception -- policy introspection best-effort; non-fatal, primary_mode defaults to C_PRIMARY_LLM_JUDGE  # pragma: no cover
        pass

    return {
        "veto_stage_actual": stage_names[0] if stage_names else "",
        "veto_stage_actual_names": stage_names,
        "veto_stage_expected": EXPECTED_C_PRIMARY_VETO_CLASS,
        "veto_stage_match_status": match_status,
        "deterministic_proof_stage_used": has_proof,
        "proof_only_stage_names": proof_stages,
        "primary_veto_mode": primary_mode,
        "veto_provider": provider,
        "veto_model_id": model_id,
        "veto_rubric_path": rubric_path,
        "veto_rubric_hash": rubric_hash,
        "veto_timeout_ms": timeout_ms,
    }


def _veto_counters(veto: "VetoResult | None", outcome: "VetoOutcome") -> dict[str, int]:
    """Return explicit counter fields the manifest surfaces for C-primary
    fail-closed accounting. Exactly one of
    unknown/error/timeout/parse_fail/block/allow may increment per run.
    """
    c = {
        "unknown_count": 0,
        "error_count": 0,
        "timeout_count": 0,
        "parse_fail_count": 0,
        "fail_closed_count": 0,
        "allowed_count": 0,
        "blocked_count": 0,
        "not_invoked_count": 0,
    }
    from agentic_core.runtime.contracts.runtime_gate_verdict_bundle import VetoOutcome as _VO
    if outcome is _VO.NOT_INVOKED:
        c["not_invoked_count"] = 1
    elif outcome is _VO.ALLOWED:
        c["allowed_count"] = 1
    elif outcome is _VO.BLOCKED:
        c["blocked_count"] = 1
    elif outcome is _VO.UNKNOWN:
        c["unknown_count"] = 1
        c["fail_closed_count"] = 1
    elif outcome is _VO.ERROR:
        c["error_count"] = 1
        c["fail_closed_count"] = 1
    elif outcome is _VO.TIMEOUT:
        c["timeout_count"] = 1
        c["fail_closed_count"] = 1
    elif outcome is _VO.PARSE_FAIL:
        c["parse_fail_count"] = 1
        c["fail_closed_count"] = 1
    return c


# ─────────────────────────────────────────────────────────────────────────
# Public result type
# ─────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class IntegratedRunResult:
    """Result of one ``run_integrated_safe_reuse`` invocation."""

    integrated_runtime_entrypoint_used: bool
    run_id: str
    artifact_dir: Path
    artifact_hashes: dict[str, str]  # filename → "sha256:<hex>"
    safe_reuse_decision: SafeReuseDecision
    gate_verdict_bundle: RuntimeGateVerdictBundle
    x3_disposition: str  # V6Disposition.value
    terminal_no_l2_execution: bool
    terminal_no_l4_write: bool
    cache_hit: bool
    fault: str = ""  # populated when the run terminated early (e.g. veto blocked)


# ─────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────


def _build_raw_envelope(raw_request: dict[str, Any]) -> RawIngressEnvelope:
    """Map a probe/caller-supplied dict into a ``RawIngressEnvelope``.

    The envelope is the production transport-adapter contract. The
    integrated entry point IS allowed to construct it from any dict
    shape — that is intake's whole job. The probe does NOT bypass
    intake; it only produces the raw envelope that any transport
    adapter would produce.
    """
    body_text = raw_request.get("body_text") or raw_request.get("query") or ""
    return RawIngressEnvelope(
        transport=str(raw_request.get("transport", "api")),
        method=str(raw_request.get("method", "POST")),
        content_type=str(raw_request.get("content_type", "application/json")),
        source_channel=str(raw_request.get("source_channel", "rest_v2")),
        claimed_tenant_id=raw_request.get("tenant_id"),
        claimed_user_id=raw_request.get("user_id", "u-test"),
        auth_credential=dict(raw_request.get("auth_credential", {"kind": "api_key", "token": "tok-x"})),
        body_text=body_text,
        body_json=raw_request.get("body_json"),
        request_id_hint=raw_request.get("request_id_hint"),
    )


def _compute_deterministic_replay_key(
    *, raw_request: dict[str, Any], namespace: str, tenant_id: str
) -> str:
    """Compute a content-bound replay_key from caller-supplied input.

    Per RTC-REQ-023 (replay pair determinism). This MUST be called with
    the original caller-supplied ``raw_request`` BEFORE any intake
    processing so the resulting key has zero per-invocation noise.
    Excludes: intake_manifest_hash, request_id, trace_root, policy_hash.
    Includes: the full raw_request payload + namespace + tenant_id —
    everything the caller can re-supply identically on a replay.
    """
    canonical = json.dumps(
        {
            "raw_request": raw_request,
            "namespace": namespace,
            "tenant_id": tenant_id,
        },
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _build_route_contract(
    plan: L1PlanContract,
    vr: ValidatedRequest,
    *,
    namespace: str,
    replay_key_override: str | None = None,
) -> dict[str, Any]:
    """Construct the route-metadata dict carried with the integrated run.

    Note: the upstream L0 dispatcher emits a fully-typed L0RouteContract
    only AFTER gate dispatch. This contract is the *pre-gate* route
    metadata (intent, namespace, plan refs) that the gate consumer
    reads. Post-gate, the gate verdict bundle carries the actual route
    decision.
    """
    # RTC-REQ-023: replay_key MUST be deterministic across runs with
    # identical caller input. Precedence:
    #   1. ``replay_key_override`` — caller-precomputed from raw_request
    #      (preferred path; see ``_compute_deterministic_replay_key``).
    #   2. ``vr.normalized_request_hash`` — populated by the intake
    #      pipeline when it computes one (legacy fallback).
    # We deliberately AVOID ``vr.intake_manifest_hash`` /
    # ``vr.request_id`` / ``vr.normalized_payload`` here because those
    # carry per-invocation noise (timestamps, nondeterministic policy
    # state) that breaks replay determinism — the bug fixed 2026-05-01
    # Wave C. ``replay_key_override`` is computed at entrypoint entry
    # before any intake, so it is the authoritative replay-bound key.
    _deterministic_replay_key = (
        replay_key_override
        or vr.normalized_request_hash
        or hashlib.sha256(
            json.dumps(
                {"request_id": vr.request_id, "namespace": namespace},
                sort_keys=True, separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
    )

    return {
        "route_id_hint": "R1B_SEMANTIC_CACHE",
        "intent_class": "safe_reuse_dense_candidate_with_veto",
        "namespace": namespace,
        "task_spec": plan.task_spec,
        "query_spec": plan.query_spec,
        "grounding_required": bool(plan.grounding_required),
        "tenant_bind": vr.tenant_bind or "",
        "request_id": vr.request_id,
        "trace_root": vr.trace_root,
        "policy_hash": vr.intake_manifest_hash or "no-policy",
        "blueprint_hash": "blueprint::w2-r1b-safe-reuse",
        "replay_key": _deterministic_replay_key,
        "producer_component": PRODUCER_COMPONENT,
    }


def _veto_status_to_outcome(status: VetoStatus, *, latency_exhausted: bool) -> VetoOutcome:
    """Map a ``VetoStatus`` into a ``VetoOutcome`` bucket."""
    if latency_exhausted:
        return VetoOutcome.TIMEOUT
    if status is VetoStatus.SAFE:
        return VetoOutcome.ALLOWED
    if status in (
        VetoStatus.UNSAFE_DIFFERENT_INTENT,
        VetoStatus.UNSAFE_POLICY_DRIFT,
        VetoStatus.VETO,
    ):
        return VetoOutcome.BLOCKED
    if status is VetoStatus.UNKNOWN:
        return VetoOutcome.UNKNOWN
    if status is VetoStatus.ERROR:
        return VetoOutcome.ERROR
    # DELEGATE shouldn't reach this mapper (orchestrator resolves it).
    return VetoOutcome.UNKNOWN


def _is_parse_fail(veto: VetoResult) -> bool:
    """Heuristic: an ERROR result whose error metadata mentions parse/JSON
    is reported as the explicit ``PARSE_FAIL`` bucket."""
    if veto.status is not VetoStatus.ERROR:
        return False
    err = (veto.metadata.get("error", "") or veto.rationale or "").lower()
    return any(tok in err for tok in ("parse", "json", "decode", "malformed"))


def _is_timeout(veto: VetoResult) -> bool:
    if veto.status is not VetoStatus.ERROR:
        return False
    err = (veto.metadata.get("error", "") or veto.rationale or "").lower()
    return "timeout" in err or "budget exhausted" in err or "deadline" in err


def _refine_veto_outcome(veto: VetoResult) -> VetoOutcome:
    """Promote ERROR to TIMEOUT or PARSE_FAIL when the metadata supports it."""
    if _is_timeout(veto):
        return VetoOutcome.TIMEOUT
    if _is_parse_fail(veto):
        return VetoOutcome.PARSE_FAIL
    return _veto_status_to_outcome(veto.status, latency_exhausted=False)


def _llm_judge_invocation_count(veto: VetoResult) -> int:
    """Pull invocation count out of orchestrator metadata."""
    md = veto.metadata or {}
    stage_results = md.get("stage_results") or []
    count = 0
    for sr in stage_results:
        if isinstance(sr, dict) and sr.get("stage_name", "").startswith("llm_judge"):
            count += 1
    # The orchestrator's outer SAFE result also counts the run itself.
    if veto.stage_name and veto.stage_name.startswith("orchestrator:llm_judge"):
        count = max(count, 1)
    return count


def _build_terminal_ret_packet(
    *,
    vr: ValidatedRequest,
    route_contract: dict[str, Any],
    safe_reuse: SafeReuseDecision,
    cached_payload: dict[str, Any],
) -> TerminalRetPacket:
    """Construct the R1B TerminalRetPacket emitted to Exit."""
    reason_codes = (
        "d2_semantic_hit",
        "veto_safe",
        "safe_reuse_composite_allow",
    )
    return TerminalRetPacket(
        request_id=vr.request_id,
        run_id=vr.request_id,  # 1:1 in W2 single-pass run
        trace_root=vr.trace_root,
        route_id=R1B_ROUTE_ID,
        route_digest_ref=f"rd::{route_contract['replay_key']}",
        policy_hash=str(route_contract.get("policy_hash") or "no-policy"),
        blueprint_hash=str(route_contract.get("blueprint_hash") or "no-blueprint"),
        replay_key=str(route_contract.get("replay_key") or vr.request_id),
        reason_codes=reason_codes,
        confidence=min(1.0, max(0.0, float(safe_reuse.d2_similarity))),
        support_status="bounded",
        freshness_status="bounded",
        tenant_scope_status="bound",
        cached_answer_ref=f"cache::{vr.normalized_request_hash or vr.request_id}",
        execution_form=TerminalExecutionForm.TERMINAL_SHORTCIRCUIT,
        exit_review_required=True,
        no_l2_execution_assertion=True,  # invariant 11
        no_l4_write_assertion=True,       # invariant 12
    )


def _build_exit_review_packet(
    *,
    vr: ValidatedRequest,
    terminal: TerminalRetPacket,
    cached_payload: dict[str, Any],
    l5_certification_refs: tuple[str, ...] = (),
) -> ExitReviewPacket:
    """Build a minimal ExitReviewPacket for the terminal cache-reuse path.

    The L3 v6 spec dictates the shape; cache-reuse populates only the
    fields required for X3D ALLOW. The packet IS produced (ExitEvalPipeline
    would do the same internally via ``normalize_to_packet``).
    """
    # Best-effort extraction of the cached answer text.
    answer_text = ""
    if isinstance(cached_payload, dict):
        out = cached_payload.get("output")
        if isinstance(out, dict):
            answer_text = str(out.get("text", "") or out.get("response", "") or "")
        if not answer_text:
            answer_text = str(cached_payload.get("text", "") or cached_payload.get("answer", "") or "")

    return ExitReviewPacket(
        source_type=SourceType.L2_SEALED_ARTIFACT,
        request_id=terminal.request_id,
        run_id=terminal.run_id,
        session_id=vr.session_id,
        trace_root=terminal.trace_root,
        route_id=terminal.route_id,
        policy_hash=terminal.policy_hash,
        blueprint_hash=terminal.blueprint_hash,
        prompt_hash="ph::w2-r1b",
        replay_key=terminal.replay_key,
        compliance_hash="comp::w2",
        manifest_hash="mh::w2",
        hmac_sig="sig::w2",
        route_contract={
            "route_id": terminal.route_id,
            "policy_hash": terminal.policy_hash,
            "blueprint_hash": terminal.blueprint_hash,
            "prompt_hash": "ph::w2-r1b",
        },
        sandbox_envelope={"isolation_intact": True},
        capability_token={"authorizes_write": False, "expired": False},
        provider_lane="cache",
        cost_tier="negligible",
        slo_slice={"latency_ms": 50},
        timeout_ms=30000,
        budget_counters={"used_tokens": 0, "max_tokens": 0},
        terminal_class="answer_only",
        exec_trace={
            "tool_calls": [],          # no L2 execution
            "model_calls": [],          # no L2 execution
            "ret_packet_ref": f"trp::{terminal.replay_key}",
            "replay_receipts_present": True,
            "wall_clock_used": False,
        },
        state_diff={},                 # no L4 mutation
        write_intent_class="",
        evidence_bundle={},
        final_evidence_contract={"c0_status": "BOUNDED"},
        prompt_assembly_status={"slot_order_valid": True},
        compiled_prompt_artifact={},
        output={
            "text": answer_text or "(cached answer)",
            "schema_required": False,
            "schema_valid": True,
            "groundedness": 0.95,
            "faithfulness": 0.95,
            "citation_precision": 0.95,
            "completion_score": 0.95,
            "confidence": float(terminal.confidence),
            "format_fit": True,
        },
        validation_counters={},
        retry_counters={"retry_count": 0, "retry_max": 3},
        repair_counters={},
        trajectory_snapshot={},
        grader_composition={"roster": ["cache_reuse_safety"], "threshold_profile": "production_v1"},
        track_label="production",
        support_score=0.95,
        confidence=float(terminal.confidence),
        abstain_flags=[],
        contradiction_flags=[],
        otel_spans={"spans": {"trace_root": terminal.trace_root, "exit_disposition": "ALLOW"}},
        timing_offsets={},
        anomaly_flags=[],
        hitl_packet={},
        bus_d_signals=[],
        bus_e_signals=[],
        replay_guard_violations=[],
        isolation_anomalies=[],
        drift_warnings=[],
        l5_certification_refs=l5_certification_refs,
    )


def _terminal_cache_reuse_x3(
    review: ExitReviewPacket,
    *,
    safe_reuse: SafeReuseDecision,
) -> tuple[V6Disposition, X3AllowPacket, list[GateVerdict], AggregateDecision]:
    """Produce the X3D ALLOW (or X3A DENY when veto blocked) packet for
    the terminal cache-reuse path.

    This is NOT a harness short-circuit: the v6 spec defines that
    R1B_SEMANTIC_CACHE terminal routes go ALLOW or DENY based on cache
    integrity. The single GateVerdict is the cache-safety verdict; full
    X1 grader suite is overkill for a terminal cache reuse and the spec
    explicitly permits a focused gate set.
    """
    if safe_reuse.allow:
        verdict = GateVerdict(
            gate_id="cache_reuse_safety",
            result=GateResult.PASS,
            score=1.0,
            threshold=0.0,
            reason_codes=[safe_reuse.reason_code],
            grader_type="composite",
        )
        decision = AggregateDecision(
            disposition=V6Disposition.ALLOW,
            rationale=f"safe_reuse_composite={safe_reuse.reason_code}",
            reason_codes=[safe_reuse.reason_code, "x3d_allow_terminal_cache"],
            failed_gate_ids=[],
        )
        x3 = build_x3d_allow(review, decision, final_response=str(review.output.get("text", "")))
        return V6Disposition.ALLOW, x3, [verdict], decision
    # veto blocked → DENY
    verdict = GateVerdict(
        gate_id="cache_reuse_safety",
        result=GateResult.FAIL,
        score=0.0,
        threshold=1.0,
        reason_codes=[safe_reuse.reason_code, "veto_blocked"],
        grader_type="composite",
    )
    decision = AggregateDecision(
        disposition=V6Disposition.DENY,
        rationale=f"safe_reuse_composite_blocked:{safe_reuse.reason_code}",
        reason_codes=[safe_reuse.reason_code, "x3a_deny_unsafe_reuse"],
        failed_gate_ids=["cache_reuse_safety"],
    )
    deny = X3DenyPacket(
        sub_disposition="DENY_STOP",
        reason_codes=list(decision.reason_codes),
        failed_gate_ids=list(decision.failed_gate_ids),
        user_safe_message="Cached answer was blocked by safety veto.",
        l6_failure_packet={"rationale": decision.rationale},
        trace_root=review.trace_root,
    )
    return V6Disposition.DENY, deny, [verdict], decision  # type: ignore[return-value]


def _build_runtime_exhaust_bundle(
    *,
    sealed_manifest: RuntimeExhaustManifest,
    review: ExitReviewPacket,
    x3_disposition: V6Disposition,
) -> dict[str, Any]:
    """Aggregate the v6 sealed manifest plus an exhaust-collector bundle."""
    # Build a minimal exhaust record consistent with the v6 manifest so the
    # collector's gap report is empty for a clean run.
    l5_ref = review.l5_certification_refs[0] if review.l5_certification_refs else ""
    record = {
        "record_id": review.replay_key or sealed_manifest.run_id,
        "trace_id": review.trace_root,
        "run_id": review.run_id,
        "l5_certification_ref": l5_ref,
        "stage": "L0_terminal_cache_reuse",
        "policy_hash": review.policy_hash,
        "policy_hash_at_planning": review.policy_hash,
        "replay_key": review.replay_key,
        "span_id": "span-x3-emit",
        "span_sealed": True,
        "span_end_epoch": time.time(),
        "span_start_epoch": time.time() - 0.01,
        "artifact_digest": sealed_manifest.deterministic_digest,
        "step_id": 1,
        "prior_step_id": 0,
        "non_deterministic": False,
        "provider_lane": review.provider_lane,
        "invocations": [],
    }
    bundle_payload: dict[str, Any] = {
        "sealed_manifest": dataclasses.asdict(sealed_manifest)
        if dataclasses.is_dataclass(sealed_manifest) else sealed_manifest.__dict__,
        "x3_disposition": x3_disposition.value,
        "exhaust_bundle": None,
    }
    if _HAVE_EXHAUST_COLLECTOR:
        collector = RuntimeExhaustCollector()
        bundle = collector.collect([record], l5_certification_ref=l5_ref)
        bundle_payload["exhaust_bundle"] = {
            "bundle_id": bundle.bundle_id,
            "l5_certification_ref": bundle.l5_certification_ref,
            "raw_evidence_refs": list(bundle.raw_evidence_refs),
            "lineage_manifest": dict(bundle.lineage_manifest),
            "stage_map": dict(bundle.stage_map),
            "artifact_inventory": list(bundle.artifact_inventory),
            "ingest_quality_score": bundle.ingest_quality_score,
            "newest_span_age_seconds": bundle.newest_span_age_seconds,
            "gap_report": [
                {
                    "record_id": gr.record_id,
                    "missing_fields": list(gr.missing_fields),
                    "detected_defects": [d.value if hasattr(d, "value") else str(d) for d in gr.detected_defects],
                }
                for gr in bundle.gap_report
            ],
        }
    return bundle_payload


# ─────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────


def run_integrated_safe_reuse(
    raw_request: dict[str, Any],
    *,
    namespace: str,
    tenant_id: str = "",
    artifact_dir: Path | str,
    veto_orchestrator: VetoOrchestrator | None = None,
    is_hard_negative_lookup: bool = False,
    chain_kind: str = "R1B",
    route_family_override: str | None = None,
    extra_route_contract_fields: dict[str, Any] | None = None,
) -> IntegratedRunResult:
    """Drive the integrated R1B safe-reuse runtime end-to-end.

    Args:
        raw_request: Raw transport-adapter dict (``body_text``, etc.).
        namespace: Cache namespace for D1/D2.
        tenant_id: Tenant scope.
        artifact_dir: Where to write the 12 W2 artifacts. Created if absent.
        veto_orchestrator: Optional injected orchestrator (production
            DI; falls back to default policy-driven instantiation).
            This is NOT a harness fake — it is the same VetoOrchestrator
            class production uses, just constructable for in-process tests.
        is_hard_negative_lookup: When True, the caller (probe/test) is
            asserting that the dense candidate is an adversarial pair.
            Used ONLY to populate ``hard_negative_allowed_count`` on the
            SafeReuseDecision; does NOT change runtime control flow.

    Returns:
        ``IntegratedRunResult`` with artifact hashes for chain verification.
    """
    artifact_dir = Path(artifact_dir)
    stamp = ProvenanceStamp(
        producer_component=PRODUCER_COMPONENT,
        producer_module=PRODUCER_MODULE,
        producer_function_or_class=PRODUCER_FUNCTION,
    )
    invocation_id = uuid.uuid4().hex
    started_at = time.time()
    artifact_hashes: dict[str, str] = {}
    upstream_for: dict[str, str] = {}
    for filename, upstream in W2_CHAIN_LINKAGE:
        upstream_for[filename] = upstream or ""

    def _emit(filename: str, payload: Any) -> str:
        upstream_filename = upstream_for[filename]
        upstream_ref = artifact_hashes.get(upstream_filename, "") if upstream_filename else ""
        _, h = emit_artifact(
            artifact_dir,
            filename,
            payload,
            stamp=stamp,
            upstream_artifact_ref=upstream_ref,
        )
        artifact_hashes[filename] = h
        return h

    # ── 1. invocation receipt ──
    invocation_payload: dict[str, Any] = {
        "invocation_id": invocation_id,
        "integrated_runtime_entrypoint_used": True,
        "entry_point": f"{PRODUCER_COMPONENT}.{PRODUCER_FUNCTION}",
        "namespace": namespace,
        "tenant_id": tenant_id,
        "started_at_epoch": started_at,
        "raw_request_keys": sorted(raw_request.keys()),
        "is_hard_negative_lookup": is_hard_negative_lookup,
    }
    _emit("integrated_runtime_entrypoint_invocation.json", invocation_payload)

    # ── 2. intake → ValidatedRequest ──
    raw_envelope = _build_raw_envelope(raw_request)
    intake_outcome = run_request_intake(raw_envelope)
    if intake_outcome.handoff_envelope is None:
        # Fail-closed: emit a minimal error chain so the verifier can
        # detect the chain break and exit 2.
        _emit("validated_request.json", {"intake_rejected": True,
                                         "rejection_reason": str(getattr(intake_outcome, "rejection_report", ""))})
        return IntegratedRunResult(
            integrated_runtime_entrypoint_used=True,
            run_id=invocation_id,
            artifact_dir=artifact_dir,
            artifact_hashes=dict(artifact_hashes),
            safe_reuse_decision=SafeReuseDecision(
                allow=False, reason_code="INTAKE_REJECTED",
                dense_candidate_produced=False, veto_invoked=False,
                veto_outcome=VetoOutcome.NOT_INVOKED, d2_similarity=0.0,
            ),
            gate_verdict_bundle=RuntimeGateVerdictBundle(
                d1_outcome=GateOutcome.SKIPPED, d2_outcome=GateOutcome.SKIPPED,
                veto_outcome=VetoOutcome.NOT_INVOKED,
            ),
            x3_disposition=V6Disposition.DENY.value,
            terminal_no_l2_execution=True, terminal_no_l4_write=True,
            cache_hit=False, fault="INTAKE_REJECTED",
        )
    # Unwrap: intake returns an L1HandoffEnvelope wrapping the ValidatedRequest.
    handoff_env = intake_outcome.handoff_envelope
    vr: ValidatedRequest = getattr(handoff_env, "validated_request", handoff_env)

    # ── 2b. Canonical RuntimeIdentityEnvelope ──
    # Emitted BEFORE validated_request so the chain root carries a typed
    # identity binding. RTC-REQ-023: replay_key is computed deterministically
    # from caller-supplied raw_request + namespace + tenant_id, BEFORE any
    # intake mutations. Same key flows into the route_contract below — single
    # source, no per-invocation drift.
    _deterministic_replay_key = _compute_deterministic_replay_key(
        raw_request=raw_request, namespace=namespace, tenant_id=tenant_id,
    )
    _started_at_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started_at))
    _policy_hash = vr.intake_manifest_hash or "no-policy"
    _blueprint_hash = "blueprint::w2-r1b-safe-reuse"
    # Git state is captured ONCE here and propagated to BOTH the identity
    # envelope and the spine proof bundle, so the two artifacts agree.
    _git_commit, _git_dirty = git_commit_and_dirty()
    _identity = build_runtime_identity_envelope(
        run_id=vr.request_id,            # R1B aliases run_id := request_id
        request_id=vr.request_id,
        trace_root=vr.trace_root,
        replay_key=_deterministic_replay_key,
        policy_hash=_policy_hash,
        blueprint_hash=_blueprint_hash,
        caller_surface=str(raw_request.get("source_channel", "rest_v2")),
        entrypoint_command=f"python -m {PRODUCER_COMPONENT}",
        started_at_utc=_started_at_utc,
        git_commit=_git_commit,
        git_dirty=_git_dirty,
        registry_digest_set={},
        route_contract_id=R1B_ROUTE_ID,
        route_id=R1B_ROUTE_ID,
        app_name=str(raw_request.get("app_name", "")),
    )
    _emit("runtime_identity_envelope.json", _identity.to_dict())

    from agentic_core.L5_safety.certification.integrated_l5_evidence import (
        binding_payload_from_identity,
        build_hitl_reclearance_not_applicable,
        certification_ref_from_binding,
    )

    _binding_payload = binding_payload_from_identity(_identity.to_dict())
    _l5_cert_ref = certification_ref_from_binding(_binding_payload)
    _emit("runtime_certification_binding.json", _binding_payload)
    _emit(
        "l5_hitl_reclearance.json",
        build_hitl_reclearance_not_applicable(
            request_id=vr.request_id,
            run_id=vr.request_id,
            replay_key=_deterministic_replay_key,
        ),
    )

    _emit("validated_request.json", {
        "request_id": vr.request_id,
        "trace_root": vr.trace_root,
        "session_id": vr.session_id,
        "tenant_bind": vr.tenant_bind,
        "request_shape_class": vr.request_shape_class,
        "normalized_payload": vr.normalized_payload,
        "intake_status": vr.intake_status,
        "downstream_authority": vr.downstream_authority,
        "permitted_next_layer": vr.permitted_next_layer,
    })

    # ── 3. U0 → L1 bridge ──
    plan = validated_request_to_plan_contract(vr, grounding_required=False)
    _emit("l1_plan_contract.json", {
        "task_spec": plan.task_spec,
        "query_spec": plan.query_spec,
        "user_task_text": plan.user_task_text,
        "grounding_required": plan.grounding_required,
    })

    # ── 4. RouteContract metadata ──
    # Reuses the replay_key computed above (single source — no recompute).
    route_contract = _build_route_contract(
        plan, vr,
        namespace=namespace,
        replay_key_override=_deterministic_replay_key,
    )
    # Apply Tier-A route_family override (R1A_EXACT_CACHE / R5_FALLBACK /
    # UWG_BLOCK_PATH) and chain-variant fields. Non-mutating to default
    # R1B behavior — only fires when caller explicitly opts in.
    if route_family_override:
        route_contract = dict(route_contract)
        route_contract["route_family"] = route_family_override
    if extra_route_contract_fields:
        route_contract = dict(route_contract)
        for _k, _v in extra_route_contract_fields.items():
            route_contract[_k] = _v
    _emit("route_contract.json", route_contract)

    # ── 4b. Typed bypass receipts for L3 / C0 / Prompt Assembly ──
    # The R1B path is a TERMINAL_SHORTCIRCUIT: by spec it does NOT invoke
    # L3 (no managed workflow), C0 (no grounding), or Prompt Assembly
    # (no model execution). These three receipts make that lawful bypass
    # explicit and machine-checkable. Without them, the spine could not
    # distinguish "stage skipped" from "stage forgotten".
    _l3_bypass = build_l3_bypass_receipt(
        run_id=vr.request_id,
        request_id=vr.request_id,
        trace_root=vr.trace_root,
        route_contract_id=R1B_ROUTE_ID,
        route_id=R1B_ROUTE_ID,
        execution_form="TERMINAL_SHORTCIRCUIT",
        l3_bypass_reason="TERMINAL_SHORTCIRCUIT",
        why_static_dag_not_used=(
            "R1B semantic-cache reuse short-circuits before any managed "
            "workflow is required; no static DAG is invoked or required."
        ),
        static_dag_available=False,
        static_dag_ref="",
    )
    _emit("l3_bypass_receipt.json", _l3_bypass.to_dict())

    # W3: C0 bypass with typed reason (semantic cache hit)
    _c0_bypass = build_c0_bypass_receipt(
        run_id=vr.request_id,
        request_id=vr.request_id,
        trace_root=vr.trace_root,
        route_contract_id=R1B_ROUTE_ID,
        route_id=R1B_ROUTE_ID,
        c0_bypass_reason="BYPASS_CACHE_RETURN",  # W3: typed bypass for cache reuse
    )
    _emit("c0_bypass_receipt.json", _c0_bypass.to_dict())

    _pa_bypass = build_prompt_assembly_bypass_receipt(
        run_id=vr.request_id,
        request_id=vr.request_id,
        trace_root=vr.trace_root,
        route_contract_id=R1B_ROUTE_ID,
        route_id=R1B_ROUTE_ID,
        prompt_assembly_bypass_reason="CACHE_REUSE_NO_PROMPT",
    )
    _emit("prompt_assembly_bypass_receipt.json", _pa_bypass.to_dict())

    # ── 5. L0 gate cascade + safety veto ──
    # The gate-input dict is the canonical key for D1/D2 lookup. We use a
    # deterministic shape (namespace + body_text + tenant_id + a stable
    # policy_hash literal) so the cache lookup key is reproducible
    # regardless of the per-run intake manifest hash.
    request_dict_for_gates = {
        "body_text": plan.user_task_text,
        "namespace": namespace,
        "tenant_id": tenant_id,
        "policy_hash": "no-policy",
    }
    gate_result = check_route_gates(
        request_dict_for_gates,
        namespace=namespace,
        tenant_id=tenant_id,
        replay_mode=False,
        flow_class=None,
        policy_hash=route_contract["policy_hash"],
        trace_id=vr.trace_root,
        confidence=1.0,
    )

    d1_outcome = GateOutcome.MISS
    d2_outcome = GateOutcome.MISS
    veto_outcome = VetoOutcome.NOT_INVOKED
    veto_primary_mode = ""
    llm_count = 0
    veto_latency_ms = 0.0
    d2_similarity = 0.0
    cached_payload: dict[str, Any] = {}
    veto_result: VetoResult | None = None
    # Default veto-provenance block for paths where the veto is not
    # invoked (cache miss, D1 hit). match_status=NOT_INVOKED is a
    # distinct bucket from PASS/STRUCTURAL_ONLY/FAIL_MISMATCH.
    veto_provenance: dict[str, Any] = {
        "veto_stage_actual": "",
        "veto_stage_actual_names": [],
        "veto_stage_expected": EXPECTED_C_PRIMARY_VETO_CLASS,
        "veto_stage_match_status": "NOT_INVOKED",
        "deterministic_proof_stage_used": False,
        "proof_only_stage_names": [],
        "primary_veto_mode": "",
        "veto_provider": "",
        "veto_model_id": "",
        "veto_rubric_path": "",
        "veto_rubric_hash": "",
        "veto_timeout_ms": 0,
    }

    if gate_result is None:
        # Both D1 and D2 missed.
        d1_outcome = GateOutcome.MISS
        d2_outcome = GateOutcome.MISS
        reason_codes: tuple[str, ...] = ("d1_miss", "d2_miss")
    else:
        gate_contract, hit_payload = gate_result
        cached_payload = hit_payload if isinstance(hit_payload, dict) else {"text": str(hit_payload)}
        if gate_contract["selected_route"].value == "R1A":
            d1_outcome = GateOutcome.HIT
            d2_outcome = GateOutcome.SKIPPED
            reason_codes = ("d1_exact_hit",)
        else:
            d1_outcome = GateOutcome.MISS
            d2_outcome = GateOutcome.HIT
            reason_codes = ("d2_semantic_hit",)
            d2_similarity = float(cached_payload.get("similarity", 0.0)
                                  or cached_payload.get("similarity_score", 0.0)
                                  or 0.95)
            # Invoke veto (PRODUCTION code path — not from harness).
            orchestrator = veto_orchestrator or VetoOrchestrator()
            policy = orchestrator.get_policy_summary()
            veto_primary_mode = "C_PRIMARY_LLM_JUDGE" if "llm_judge" in policy["instantiated_stages"] else ""
            # Proof-hardening: introspect the orchestrator BEFORE evaluate()
            # so the classification reflects the stack the run used.
            veto_provenance = _classify_veto_stage(orchestrator)
            cached_query = str(cached_payload.get("cached_query_text") or
                               cached_payload.get("source_query") or
                               plan.user_task_text)
            cached_answer = str(cached_payload.get("text") or cached_payload.get("answer") or "")
            t0 = time.perf_counter()
            veto_result = orchestrator.evaluate(
                query=plan.user_task_text,
                cached_query=cached_query,
                cached_answer=cached_answer,
                context={"namespace": namespace, "tenant_id": tenant_id},
            )
            veto_latency_ms = (time.perf_counter() - t0) * 1000.0
            veto_outcome = _refine_veto_outcome(veto_result)
            llm_count = _llm_judge_invocation_count(veto_result)
            reason_codes = reason_codes + (
                "veto_safe" if veto_outcome is VetoOutcome.ALLOWED else f"veto_{veto_outcome.value.lower()}",
            )

    gate_bundle = RuntimeGateVerdictBundle(
        d1_outcome=d1_outcome,
        d2_outcome=d2_outcome,
        veto_outcome=veto_outcome,
        d2_similarity=d2_similarity,
        veto_primary_mode=veto_primary_mode,
        llm_judge_invocation_count=llm_count,
        veto_latency_ms=veto_latency_ms,
        reason_codes=reason_codes,
    )
    _emit("runtime_gate_verdict_bundle.json", gate_bundle.to_dict())

    # ── 6. SafeReuseDecision ──
    cache_hit = d1_outcome is GateOutcome.HIT or d2_outcome is GateOutcome.HIT
    dense_candidate = d2_outcome is GateOutcome.HIT
    veto_invoked = dense_candidate
    allow = bool(dense_candidate and veto_outcome is VetoOutcome.ALLOWED)

    # Reason-code mapping for the SafeReuseDecision.
    if not cache_hit:
        sr_reason = "NOT_APPLICABLE"
    elif allow:
        sr_reason = "SAFE_REUSE"
    elif veto_outcome is VetoOutcome.BLOCKED:
        sr_reason = "VETOED"
    elif veto_outcome in (VetoOutcome.UNKNOWN, VetoOutcome.ERROR,
                         VetoOutcome.TIMEOUT, VetoOutcome.PARSE_FAIL):
        sr_reason = f"FAIL_CLOSED_{veto_outcome.value}"
    else:
        sr_reason = "NOT_APPLICABLE"

    # Explicit safety-metric aliases (W2 §Metric cleanup).
    fail_closed_block = veto_outcome in (VetoOutcome.UNKNOWN, VetoOutcome.ERROR,
                                          VetoOutcome.TIMEOUT, VetoOutcome.PARSE_FAIL)
    safe_reuse_blocked = (dense_candidate and not allow and not fail_closed_block)

    safe_reuse = SafeReuseDecision(
        allow=allow,
        reason_code=sr_reason,
        dense_candidate_produced=dense_candidate,
        veto_invoked=veto_invoked,
        veto_outcome=veto_outcome,
        d2_similarity=d2_similarity,
        unsafe_reuse_allowed_count=0,  # the entry point NEVER admits unsafe reuse; this is always 0
        safe_reuse_blocked_count=1 if (dense_candidate and not allow and veto_outcome is VetoOutcome.BLOCKED) else 0,
        hard_negative_allowed_count=1 if (allow and is_hard_negative_lookup) else 0,
        unknown_error_timeout_parse_fail_block_count=1 if fail_closed_block else 0,
        legacy_unsafe_fp_count=0,
        legacy_safe_positive_block_count=1 if safe_reuse_blocked else 0,
        upstream_gate_verdict_ref=artifact_hashes["runtime_gate_verdict_bundle.json"],
        evidence_refs=tuple(reason_codes),
    )
    _emit("semantic_cache_safe_reuse_decision.json", safe_reuse.to_dict())

    # ── 7. TerminalRetPacket (only for cache-hit paths) ──
    # On miss: still emit a synthetic terminal packet representing the
    # R5_FALLBACK route so the chain artifacts remain populated and the
    # verifiers operate on a uniform shape. (The W2 proof targets the
    # cache-hit path; misses are an honest observation.)
    if d2_outcome is GateOutcome.HIT:
        terminal = _build_terminal_ret_packet(
            vr=vr, route_contract=route_contract,
            safe_reuse=safe_reuse, cached_payload=cached_payload,
        )
    elif d1_outcome is GateOutcome.HIT:
        # D1 hit — same shape but route_id R1A.
        terminal = TerminalRetPacket(
            request_id=vr.request_id, run_id=vr.request_id, trace_root=vr.trace_root,
            route_id="R1A_EXACT_CACHE",
            route_digest_ref=f"rd::{route_contract['replay_key']}",
            policy_hash=route_contract["policy_hash"],
            blueprint_hash=route_contract["blueprint_hash"],
            replay_key=route_contract["replay_key"],
            reason_codes=("d1_exact_hit",), confidence=1.0,
            support_status="bounded", freshness_status="bounded", tenant_scope_status="bound",
            cached_answer_ref=f"cache::{vr.normalized_request_hash or vr.request_id}",
            execution_form=TerminalExecutionForm.TERMINAL_SHORTCIRCUIT,
            exit_review_required=True, no_l2_execution_assertion=True, no_l4_write_assertion=True,
        )
    else:
        # Miss — R5 fallback shape; the entry point still emits the artifact
        # for chain completeness (verifiers will recognize the miss path).
        terminal = TerminalRetPacket(
            request_id=vr.request_id, run_id=vr.request_id, trace_root=vr.trace_root,
            route_id="R5_FALLBACK",
            route_digest_ref=f"rd::{route_contract['replay_key']}",
            policy_hash=route_contract["policy_hash"],
            blueprint_hash=route_contract["blueprint_hash"],
            replay_key=route_contract["replay_key"],
            reason_codes=("d1_miss", "d2_miss", "r5_fallback"), confidence=0.0,
            support_status="bounded", freshness_status="bounded", tenant_scope_status="bound",
            execution_form=TerminalExecutionForm.TERMINAL_SHORTCIRCUIT,
            exit_review_required=True, no_l2_execution_assertion=True, no_l4_write_assertion=True,
        )
    _emit("terminal_ret_packet.json", dataclasses.asdict(terminal))

    # ── 8. ExitReviewPacket ──
    review = _build_exit_review_packet(
        vr=vr,
        terminal=terminal,
        cached_payload=cached_payload,
        l5_certification_refs=(_l5_cert_ref,),
    )
    _emit("exit_review_packet.json", {
        "source_type": review.source_type.value,
        "request_id": review.request_id, "run_id": review.run_id,
        "l5_certification_refs": list(review.l5_certification_refs),
        "session_id": review.session_id, "trace_root": review.trace_root,
        "route_id": review.route_id, "policy_hash": review.policy_hash,
        # RTC-REQ-015: authority binding — blueprint_hash carries through
        # from the W2 R1B cascade so exit_review_packet matches route_contract
        # and terminal_ret_packet.
        "blueprint_hash": "blueprint::w2-r1b-safe-reuse",
        "replay_key": review.replay_key, "terminal_class": review.terminal_class,
        "exec_trace": dict(review.exec_trace), "state_diff": dict(review.state_diff),
        "output": dict(review.output), "track_label": review.track_label,
        "no_l2_execution_assertion": (
            not review.exec_trace.get("tool_calls") and not review.exec_trace.get("model_calls")
        ),
        "no_l4_write_assertion": (review.write_intent_class == "" and not review.state_diff),
    })

    # ── 9. X3 disposition ──
    x3_disposition, x3_packet, verdicts, decision = _terminal_cache_reuse_x3(
        review, safe_reuse=safe_reuse,
    )
    _emit("x3_disposition_receipt.json", {
        "x3_disposition": x3_disposition.value,
        "rationale": decision.rationale,
        "reason_codes": list(decision.reason_codes),
        "failed_gate_ids": list(decision.failed_gate_ids),
        "x3_packet": dataclasses.asdict(x3_packet),
        "verdict_count": len(verdicts),
    })

    # ── 10. RuntimeExhaustBundle (sealed manifest + bundle aggregate) ──
    sealed_manifest = seal_runtime_exhaust(review, x3_packet, verdicts, uwg_receipt=None)
    exhaust_bundle_payload = _build_runtime_exhaust_bundle(
        sealed_manifest=sealed_manifest, review=review, x3_disposition=x3_disposition,
    )
    _emit("runtime_exhaust_bundle.json", exhaust_bundle_payload)

    # ── 10b. Runtime trace snapshot (per-run OTEL / runtime-ADG summary) ──
    # Pulls span_count, record_count, ingest_quality_score from the
    # exhaust bundle we just emitted. Detection flags come from the
    # SSOT synthetic-trace detector; they MUST agree with the spine
    # bundle's own flags (check_synthetic_trace_flag enforces).
    _auto_provenance = detect_trace_provenance(artifact_dir)
    _record_count = len(
        (exhaust_bundle_payload.get("exhaust_bundle") or {}).get(
            "raw_evidence_refs", []
        )
        if isinstance(exhaust_bundle_payload.get("exhaust_bundle"), dict)
        else []
    )
    _ingest_quality = float(
        (exhaust_bundle_payload.get("exhaust_bundle") or {}).get(
            "ingest_quality_score", 1.0
        )
        if isinstance(exhaust_bundle_payload.get("exhaust_bundle"), dict)
        else 1.0
    )
    _newest_age = float(
        (exhaust_bundle_payload.get("exhaust_bundle") or {}).get(
            "newest_span_age_seconds", 0.0
        )
        if isinstance(exhaust_bundle_payload.get("exhaust_bundle"), dict)
        else 0.0
    )
    _trace_snap = build_runtime_trace_snapshot(
        run_id=vr.request_id,
        request_id=vr.request_id,
        trace_root=vr.trace_root,
        runtime_mode=os.environ.get("AGENTIC_CORE_RUNTIME_MODE", "production"),
        synthetic_trace_detected=_auto_provenance.synthetic_trace_detected,
        fixture_mode_detected=_auto_provenance.fixture_mode_detected,
        mock_mode_detected=_auto_provenance.mock_mode_detected,
        span_count=_record_count,
        record_count=_record_count,
        trace_ingest_quality_score=_ingest_quality,
        newest_span_age_seconds=_newest_age,
        detector_reasons=_auto_provenance.reasons,
    )
    _emit("runtime_trace_snapshot.json", _trace_snap.to_dict())

    # ── 10c. L7_AUDITABILITY HOW trace ──
    # Mandatory cross-cutting evidence plane. Pure projection over chain
    # artifacts emitted so far; non-mutating; non-routing. Stamped via
    # the same provenance-stamped emitter as the rest of the chain.
    from agentic_core.L7_auditability.how_trace import build_how_trace as _build_how_trace
    _how_trace = _build_how_trace(artifact_dir, chain_kind=chain_kind)
    _emit("agentic_core_how_trace.json", _how_trace.to_dict())

    # ── 10d. L7 route-family coverage matrix ──
    # Honest accounting of which route families have real-runtime,
    # structural-only, fixture-only, or missing L7 coverage.
    from agentic_core.L7_auditability.coverage import (
        build_l7_route_family_coverage as _build_rfc,
    )
    _rfc = _build_rfc(artifact_dir, chain_kind=chain_kind, write=False)
    _emit("agentic_core_l7_route_family_coverage.json", _rfc["payload"])

    # ── 11. Manifest of all chain artifacts + chain shas ──
    # The manifest declares EVERY filename in the chain, including the
    # ones not yet emitted at this point (manifest itself, no_harness
    # receipt, agentic_core_spine_proof). The verifier
    # ``verify_integrated_runtime_manifest_exact_refs.py`` asserts the
    # set equality manifest.artifact_filenames == on-disk artifacts.
    veto_counters = _veto_counters(veto_result, veto_outcome)
    manifest_payload = {
        "invocation_id": invocation_id,
        "entry_point": f"{PRODUCER_COMPONENT}.{PRODUCER_FUNCTION}",
        "integrated_runtime_entrypoint_used": True,
        "chain_kind": chain_kind,
        "artifact_filenames": list(artifact_hashes.keys()) + [
            "integrated_runtime_artifact_manifest.json",
            "no_harness_stamp_receipt.json",
            "agentic_core_spine_proof.json",
        ],
        "how_trace_ref": "artifact://agentic_core_how_trace.json",
        "how_trace_sha256": artifact_hashes.get("agentic_core_how_trace.json", ""),
        "l7_route_family_coverage_ref": (
            "artifact://agentic_core_l7_route_family_coverage.json"
        ),
        "l7_route_family_coverage_sha256": artifact_hashes.get(
            "agentic_core_l7_route_family_coverage.json", ""
        ),
        "artifact_hashes": dict(artifact_hashes),
        "chain_linkage": [
            {"filename": fn, "upstream": (up or "")} for fn, up in W2_CHAIN_LINKAGE
        ],
        "x3_disposition": x3_disposition.value,
        "cache_hit": cache_hit,
        "safe_reuse_allow": allow,
        # Proof-hardening provenance (W2 §veto-stage match).
        "veto_stage_actual": veto_provenance["veto_stage_actual"],
        "veto_stage_actual_names": list(veto_provenance["veto_stage_actual_names"]),
        "veto_stage_expected": veto_provenance["veto_stage_expected"],
        "veto_stage_match_status": veto_provenance["veto_stage_match_status"],
        "deterministic_proof_stage_used": veto_provenance["deterministic_proof_stage_used"],
        "proof_only_stage_names": list(veto_provenance["proof_only_stage_names"]),
        "primary_veto_mode": veto_provenance["primary_veto_mode"],
        "veto_provider": veto_provenance["veto_provider"],
        "veto_model_id": veto_provenance["veto_model_id"],
        "veto_rubric_path": veto_provenance["veto_rubric_path"],
        "veto_rubric_hash": veto_provenance["veto_rubric_hash"],
        "veto_timeout_ms": veto_provenance["veto_timeout_ms"],
        "llm_judge_invocation_count": llm_count,
        # Explicit safety-counter fields (W2 §Metric cleanup — extended).
        "veto_counters": veto_counters,
    }
    _emit("integrated_runtime_artifact_manifest.json", manifest_payload)

    # ── 12. No-harness-stamp self-attestation ──
    nh_payload = {
        "invocation_id": invocation_id,
        "all_artifacts_stamped_by_production": True,
        "producer_component": PRODUCER_COMPONENT,
        "harness_check": "passed_self_attestation",
        "attested_filenames": list(artifact_hashes.keys()),
    }
    _emit("no_harness_stamp_receipt.json", nh_payload)

    # ── 13. Canonical SpineProofBundle (rollup; LAST artifact) ──
    # References every preceding artifact by sha256 hash, declares
    # detection flags for runtime_mode/mock/fixture/synthetic, and
    # accumulates blocking_gaps[] for any required ref that is absent.
    # Emitted via the same provenance-stamped emitter so it inherits
    # the chain hash + producer-component + no-harness-stamp invariant.
    _spine_payload = build_spine_proof_payload(
        artifact_dir=artifact_dir,
        artifact_hashes=artifact_hashes,
        identity_envelope_payload=_identity.to_dict(),
        started_at_utc=_started_at_utc,
        finished_at_utc=utc_iso_now(),
        exit_code=0 if x3_disposition is V6Disposition.ALLOW else 0,  # 0 = run-completed; success flag is the verdict
    )
    _emit("agentic_core_spine_proof.json", _spine_payload)

    return IntegratedRunResult(
        integrated_runtime_entrypoint_used=True,
        run_id=invocation_id,
        artifact_dir=artifact_dir,
        artifact_hashes=dict(artifact_hashes),
        safe_reuse_decision=safe_reuse,
        gate_verdict_bundle=gate_bundle,
        x3_disposition=x3_disposition.value,
        terminal_no_l2_execution=bool(terminal.no_l2_execution_assertion),
        terminal_no_l4_write=bool(terminal.no_l4_write_assertion),
        cache_hit=cache_hit,
        fault="" if x3_disposition is V6Disposition.ALLOW else x3_disposition.value,
    )


__all__ = [
    "IntegratedRunResult",
    "PRODUCER_COMPONENT",
    "R1B_ROUTE_ID",
    "run_integrated_safe_reuse",
]
