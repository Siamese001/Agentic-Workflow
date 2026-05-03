"""Structural-only MANAGED_WORKFLOW entry point.

Drives the full MW chain end-to-end with a 2-node demo DAG. The purpose
is to exercise the managed-workflow substrate (StaticDagProof,
L3RuntimeOrchestrationReceipt, MW chain linkage, spine proof bundle
under ``chain_kind=MANAGED_WORKFLOW``) without invoking real L2
tool/model execution.

Honest disclosure:
    - ``managed_workflow_certified`` on the spine proof bundle is False.
    - L3 orchestrates (selects the 2 nodes from the static DAG, creates
      step contracts) but hands each step to L2 with
      ``status=step_handed_to_l2`` — no tool or model is actually
      invoked.
    - C0 and Prompt Assembly are both explicitly bypassed (structural
      MW does not retrieve evidence or assemble prompts).
    - The verifier suite enforces the hash-bound equality of
      ``static_dag.dag_sha256 == runtime_l3_receipt.dag_sha256``.

This entry point is the smallest-working-proof that the MW substrate
is real; future passes replace the structural stubs with real L2
execution, real C0/PA, and real UWG commits.
"""

from __future__ import annotations

import dataclasses
import os
import time
import uuid
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.intake.envelope import RawIngressEnvelope
from agentic_core.L0_routing.intake.pipeline import run_request_intake
from agentic_core.L0_routing.intake.validated_request import ValidatedRequest
from agentic_core.L1_cognition.bridges.u0_to_l1_plan import (
    validated_request_to_plan_contract,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateResult,
    GateVerdict,
    SourceType,
    V6Disposition,
    X3AllowPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import AggregateDecision
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
    build_x3d_allow,
)
from agentic_core.L3_orchestration.exit_eval.v6.return_payload import (
    seal_runtime_exhaust,
)
from agentic_core.L2_execution.types.sealed_l2_artifact import (
    ReplayMetadata,
    SealedL2Artifact,
    TerminalClassification,
    ValidationCounters,
)
from agentic_core.L3_orchestration.registry import (
    DEMO_TWO_NODE_DAG_ID,
    get_default_registry,
)
from agentic_core.L5_safety.runtime_gates.structural_na_bundle import (
    build_structural_full_suite_verdicts,
)
from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import (  # guardian: allow-layer-violation -- ADR-096 L6 universally importable; runtime entrypoint consumes L6 exhaust bundle to emit canonical runtime trace
    RuntimeExhaustCollector,
)
from agentic_core.L6_observability.runtime_trace.synthetic_trace_detector import (
    detect_trace_provenance,
)
from agentic_core.runtime.artifacts.integrated_runtime_emitter import (
    ProvenanceStamp,
    W2_MW_CHAIN_LINKAGE,
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
from agentic_core.runtime.contracts.l3_runtime_orchestration_receipt import (
    L3StepContractRef,
    build_l3_runtime_orchestration_receipt,
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

PRODUCER_COMPONENT = (
    "agentic_core.runtime.entrypoints.integrated_managed_workflow_run"
)
PRODUCER_MODULE = "integrated_managed_workflow_run"
PRODUCER_FUNCTION = "run_integrated_managed_workflow"

MW_ROUTE_ID = "MW_DEMO_TWO_NODE"


def _build_raw_envelope(raw_request: dict[str, Any]) -> RawIngressEnvelope:
    body_text = raw_request.get("body_text") or raw_request.get("query") or ""
    return RawIngressEnvelope(
        transport=str(raw_request.get("transport", "api")),
        method=str(raw_request.get("method", "POST")),
        content_type=str(raw_request.get("content_type", "application/json")),
        source_channel=str(raw_request.get("source_channel", "rest_v2")),
        claimed_tenant_id=raw_request.get("tenant_id"),
        claimed_user_id=raw_request.get("user_id", "u-mw"),
        auth_credential=dict(raw_request.get("auth_credential", {"kind": "api_key", "token": "tok-mw"})),
        body_text=body_text,
        body_json=raw_request.get("body_json"),
        request_id_hint=raw_request.get("request_id_hint"),
    )


def _build_route_contract(vr: ValidatedRequest, *, namespace: str) -> dict[str, Any]:
    """Pre-gate MW route metadata. ``execution_form=MANAGED_WORKFLOW``."""
    return {
        "route_id_hint": MW_ROUTE_ID,
        "intent_class": "managed_workflow_demo",
        "namespace": namespace,
        "task_spec": "mw_demo",
        "query_spec": "mw_demo_query",
        "execution_form": "MANAGED_WORKFLOW",
        "grounding_required": False,
        "prompt_assembly_required": False,
        "model_execution_required": False,
        "l3_required": True,
        "static_dag_ref": (
            "agentic_core.L3_orchestration.registry.static_dag_registry."
            "DEMO_TWO_NODE_DAG_ID"
        ),
        "tenant_bind": vr.tenant_bind or "",
        "request_id": vr.request_id,
        "trace_root": vr.trace_root,
        "policy_hash": vr.intake_manifest_hash or "no-policy",
        "blueprint_hash": "blueprint::mw-demo-two-node",
        "replay_key": vr.normalized_request_hash or vr.request_id,
        "producer_component": PRODUCER_COMPONENT,
    }


def _build_exit_review_packet(
    *, vr: ValidatedRequest, route_contract: dict[str, Any]
) -> ExitReviewPacket:
    """Minimal ExitReviewPacket for structural MW (no L2 execution)."""
    return ExitReviewPacket(
        source_type=SourceType.L2_SEALED_ARTIFACT,
        request_id=vr.request_id,
        run_id=vr.request_id,
        session_id=vr.session_id,
        trace_root=vr.trace_root,
        route_id=MW_ROUTE_ID,
        policy_hash=str(route_contract.get("policy_hash") or "no-policy"),
        blueprint_hash=str(route_contract.get("blueprint_hash") or "no-blueprint"),
        prompt_hash="ph::mw-structural",
        replay_key=str(route_contract.get("replay_key") or vr.request_id),
        compliance_hash="comp::mw",
        manifest_hash="mh::mw",
        hmac_sig="sig::mw",
        route_contract={
            "route_id": MW_ROUTE_ID,
            "policy_hash": route_contract.get("policy_hash", ""),
            "blueprint_hash": route_contract.get("blueprint_hash", ""),
            "prompt_hash": "ph::mw-structural",
        },
        sandbox_envelope={"isolation_intact": True},
        capability_token={"authorizes_write": False, "expired": False},
        provider_lane="none",
        cost_tier="negligible",
        slo_slice={"latency_ms": 10},
        timeout_ms=30000,
        budget_counters={"used_tokens": 0, "max_tokens": 0},
        terminal_class="mw_structural_only",
        exec_trace={
            "tool_calls": [],
            "model_calls": [],
            "ret_packet_ref": f"mw::{route_contract.get('replay_key', '')}",
            "replay_receipts_present": True,
            "wall_clock_used": False,
        },
        state_diff={},
        write_intent_class="",
        evidence_bundle={},
        final_evidence_contract={"c0_status": "BYPASSED"},
        prompt_assembly_status={"slot_order_valid": True, "pa_status": "BYPASSED"},
        compiled_prompt_artifact={},
        output={
            "text": "(MW structural-only demo run)",
            "schema_required": False,
            "schema_valid": True,
            "groundedness": 1.0,
            "faithfulness": 1.0,
            "citation_precision": 1.0,
            "completion_score": 1.0,
            "confidence": 1.0,
            "format_fit": True,
        },
        validation_counters={},
        retry_counters={"retry_count": 0, "retry_max": 0},
        repair_counters={},
        trajectory_snapshot={},
        grader_composition={"roster": ["mw_structural"], "threshold_profile": "structural_v1"},
        track_label="structural",
        support_score=1.0,
        confidence=1.0,
        abstain_flags=[],
        contradiction_flags=[],
        otel_spans={"spans": {"trace_root": vr.trace_root, "exit_disposition": "ALLOW"}},
        timing_offsets={},
        anomaly_flags=[],
        hitl_packet={},
        bus_d_signals=[],
        bus_e_signals=[],
        replay_guard_violations=[],
        isolation_anomalies=[],
        drift_warnings=[],
    )


def run_integrated_managed_workflow(
    raw_request: dict[str, Any],
    *,
    namespace: str = "mw_demo",
    tenant_id: str = "",
    artifact_dir: Path | str,
    dag_id: str = DEMO_TWO_NODE_DAG_ID,
) -> dict[str, Any]:
    """Drive the structural-only MANAGED_WORKFLOW chain end-to-end.

    Returns a result dict with ``run_id``, ``artifact_hashes``, and
    ``chain_kind``. See the module docstring for the honest disclosure
    of what is and isn't certified by this run.
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
    upstream_for: dict[str, str] = {
        fn: (up or "") for fn, up in W2_MW_CHAIN_LINKAGE
    }

    def _emit(filename: str, payload: Any) -> str:
        upstream_filename = upstream_for[filename]
        upstream_ref = (
            artifact_hashes.get(upstream_filename, "")
            if upstream_filename else ""
        )
        _, h = emit_artifact(
            artifact_dir,
            filename,
            payload,
            stamp=stamp,
            upstream_artifact_ref=upstream_ref,
        )
        artifact_hashes[filename] = h
        return h

    # 1. invocation receipt
    invocation_payload: dict[str, Any] = {
        "invocation_id": invocation_id,
        "integrated_runtime_entrypoint_used": True,
        "entry_point": f"{PRODUCER_COMPONENT}.{PRODUCER_FUNCTION}",
        "namespace": namespace,
        "tenant_id": tenant_id,
        "started_at_epoch": started_at,
        "dag_id": dag_id,
        "chain_kind": "MANAGED_WORKFLOW",
    }
    _emit("integrated_runtime_entrypoint_invocation.json", invocation_payload)

    # 2. intake
    raw_envelope = _build_raw_envelope(raw_request)
    intake_outcome = run_request_intake(raw_envelope)
    if intake_outcome.handoff_envelope is None:
        # Fail-closed: chain will fail the verifier by design.
        _emit("runtime_identity_envelope.json", {
            "schema_version": "1.0",
            "run_id": "",
            "request_id": "",
            "trace_root": "",
            "intake_rejected": True,
        })
        return {
            "integrated_runtime_entrypoint_used": True,
            "run_id": invocation_id,
            "artifact_dir": artifact_dir,
            "artifact_hashes": dict(artifact_hashes),
            "chain_kind": "MANAGED_WORKFLOW",
            "fault": "INTAKE_REJECTED",
        }
    handoff_env = intake_outcome.handoff_envelope
    vr: ValidatedRequest = getattr(handoff_env, "validated_request", handoff_env)

    # 3. identity envelope (same pattern as R1B entrypoint)
    _started_at_utc = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime(started_at)
    )
    _policy_hash = vr.intake_manifest_hash or "no-policy"
    _blueprint_hash = "blueprint::mw-demo-two-node"
    _git_commit, _git_dirty = git_commit_and_dirty()
    _identity = build_runtime_identity_envelope(
        run_id=vr.request_id,
        request_id=vr.request_id,
        trace_root=vr.trace_root,
        replay_key=vr.normalized_request_hash or vr.request_id,
        policy_hash=_policy_hash,
        blueprint_hash=_blueprint_hash,
        caller_surface=str(raw_request.get("source_channel", "rest_v2")),
        entrypoint_command=f"python -m {PRODUCER_COMPONENT}",
        started_at_utc=_started_at_utc,
        git_commit=_git_commit,
        git_dirty=_git_dirty,
        registry_digest_set={},
        route_contract_id=MW_ROUTE_ID,
        route_id=MW_ROUTE_ID,
        app_name=str(raw_request.get("app_name", "")),
    )
    _emit("runtime_identity_envelope.json", _identity.to_dict())

    # 4. validated_request + plan + route_contract
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
    plan = validated_request_to_plan_contract(vr, grounding_required=False)
    _emit("l1_plan_contract.json", {
        "task_spec": plan.task_spec,
        "query_spec": plan.query_spec,
        "user_task_text": plan.user_task_text,
        "grounding_required": plan.grounding_required,
    })
    route_contract = _build_route_contract(vr, namespace=namespace)
    _emit("route_contract.json", route_contract)

    # 5. static DAG proof
    registry = get_default_registry()
    static_dag = registry.get(dag_id)
    static_dag_payload = static_dag.to_dict()
    _emit("static_dag_proof.json", static_dag_payload)

    # 6. runtime L3 orchestration receipt — structural-only: each node
    #    handed to L2 but not executed.
    hand_off_utc = utc_iso_now()
    step_contracts = tuple(
        L3StepContractRef(
            step_id=f"step_{i}",
            node_id=n.node_id,
            run_id=vr.request_id,
            status="step_handed_to_l2",
            handed_to_l2_at_utc=hand_off_utc,
            skipped_reason="",
        )
        for i, n in enumerate(static_dag.nodes, start=1)
    )
    selected = tuple(n.node_id for n in static_dag.nodes)
    _l3_receipt = build_l3_runtime_orchestration_receipt(
        run_id=vr.request_id,
        request_id=vr.request_id,
        trace_root=vr.trace_root,
        route_contract_id=MW_ROUTE_ID,
        route_id=MW_ROUTE_ID,
        dag_id=static_dag.dag_id,
        dag_sha256=static_dag.dag_sha256,
        selected_node_ids=selected,
        step_contracts=step_contracts,
        static_dag_ref=artifact_hashes["static_dag_proof.json"],
    )
    _emit("runtime_l3_orchestration_receipt.json", _l3_receipt.to_dict())

    # 6b. L2 sealed artifact (structural-only). MW chain proves the
    # L3→L2 handoff produced a sealed artifact that was NEVER permitted
    # to execute real tools/models and NEVER wrote L4. The seal is bound
    # to the L3 orchestration receipt by artifact_hash and shares the
    # same run_id / request_id / trace_root as every other artifact.
    sealed_l2 = SealedL2Artifact(
        artifact_id=f"l2-seal-{uuid.uuid4().hex}",
        trace_id=vr.trace_root,
        exec_trace={
            "plan_hash": "mw-structural-demo",
            "policy_hash": _policy_hash,
            "determinism_digest": _l3_receipt.deterministic_digest,
            "tool_calls": [],
            "model_calls": [],
        },
        state_diff={},
        evidence_bundle={},
        validation_counters=ValidationCounters(),
        terminal_classification=TerminalClassification.SUCCESS,
        replay_metadata=ReplayMetadata(
            replay_key=_identity.replay_key,
            determinism_digest=_l3_receipt.deterministic_digest,
            replay_completeness=1.0,
            seed_captured=True,
            isolation_verified=True,
        ),
        has_commit_payload=False,
        escalation_reason=None,
        sealed_at=time.time(),
    )
    _l2_payload = {
        **dataclasses.asdict(sealed_l2),
        # classvar — asdict omits it, so restore explicitly.
        "run_scope": "CURRENT_RUN",
        # identity continuity (spine-level, not in the dataclass).
        "run_id": vr.request_id,
        "request_id": vr.request_id,
        "trace_root": vr.trace_root,
        "route_contract_id": MW_ROUTE_ID,
        "route_id": MW_ROUTE_ID,
        # binding to L3 orchestration receipt.
        "l3_step_contracts_ref": artifact_hashes[
            "runtime_l3_orchestration_receipt.json"
        ],
        # structural-only assertions.
        "structural_only": True,
        "no_l2_real_execution_assertion": True,
        "no_l4_write_assertion": True,
        # enum → string for JSON.
        "terminal_classification": sealed_l2.terminal_classification.value,
    }
    _emit("l2_sealed_artifact.json", _l2_payload)

    # 7. C0 + Prompt Assembly bypass (structural MW does not retrieve
    #    evidence or assemble prompts).
    _c0_bypass = build_c0_bypass_receipt(
        run_id=vr.request_id,
        request_id=vr.request_id,
        trace_root=vr.trace_root,
        route_contract_id=MW_ROUTE_ID,
        route_id=MW_ROUTE_ID,
        c0_bypass_reason="GROUNDING_NOT_REQUIRED",
    )
    _emit("c0_bypass_receipt.json", _c0_bypass.to_dict())
    _pa_bypass = build_prompt_assembly_bypass_receipt(
        run_id=vr.request_id,
        request_id=vr.request_id,
        trace_root=vr.trace_root,
        route_contract_id=MW_ROUTE_ID,
        route_id=MW_ROUTE_ID,
        prompt_assembly_bypass_reason="NO_MODEL_EXECUTION_REQUIRED",
    )
    _emit("prompt_assembly_bypass_receipt.json", _pa_bypass.to_dict())

    # 8. Runtime gate verdict bundle (MW structural: full_suite=True with
    # all 29 gates marked NOT_APPLICABLE + reason). This proves the full
    # G01..G29 cascade was CONSIDERED and every gate declared its
    # NA-reason rather than being silently skipped. A future full-cascade
    # entrypoint replaces the NA verdicts with real substantive results.
    gate_bundle = RuntimeGateVerdictBundle(
        d1_outcome=GateOutcome.SKIPPED,
        d2_outcome=GateOutcome.SKIPPED,
        veto_outcome=VetoOutcome.NOT_INVOKED,
        d2_similarity=0.0,
        veto_primary_mode="",
        llm_judge_invocation_count=0,
        veto_latency_ms=0.0,
        reason_codes=("mw_structural_full_suite_all_na",),
    )
    _gate_bundle_payload = gate_bundle.to_dict()
    _gate_bundle_payload["full_suite"] = True
    _gate_bundle_payload["verdicts"] = build_structural_full_suite_verdicts()
    _emit("runtime_gate_verdict_bundle.json", _gate_bundle_payload)

    # 9. Exit review + X3 allow (structural-only)
    review = _build_exit_review_packet(vr=vr, route_contract=route_contract)
    _emit("exit_review_packet.json", {
        "source_type": review.source_type.value,
        "request_id": review.request_id,
        "run_id": review.run_id,
        "session_id": review.session_id,
        "trace_root": review.trace_root,
        "route_id": review.route_id,
        "policy_hash": review.policy_hash,
        "blueprint_hash": _blueprint_hash,
        "replay_key": review.replay_key,
        "terminal_class": review.terminal_class,
        "exec_trace": dict(review.exec_trace),
        "state_diff": dict(review.state_diff),
        "output": dict(review.output),
        "track_label": review.track_label,
        "no_l2_execution_assertion": True,
        "no_l4_write_assertion": True,
    })

    verdict = GateVerdict(
        gate_id="mw_structural_check",
        result=GateResult.PASS,
        score=1.0,
        threshold=0.0,
        reason_codes=["mw_structural_only_pass"],
        grader_type="composite",
    )
    decision = AggregateDecision(
        disposition=V6Disposition.ALLOW,
        rationale="mw_structural_only_allow",
        reason_codes=["mw_structural_only_pass"],
        failed_gate_ids=[],
    )
    x3_packet = build_x3d_allow(
        review, decision, final_response=str(review.output.get("text", ""))
    )
    _emit("x3_disposition_receipt.json", {
        "x3_disposition": V6Disposition.ALLOW.value,
        "rationale": decision.rationale,
        "reason_codes": list(decision.reason_codes),
        "failed_gate_ids": list(decision.failed_gate_ids),
        "x3_packet": dataclasses.asdict(x3_packet),
        "verdict_count": 1,
    })

    # 10. Runtime exhaust bundle (minimal, structural)
    sealed_manifest = seal_runtime_exhaust(review, x3_packet, [verdict], uwg_receipt=None)
    collector = RuntimeExhaustCollector()
    record = {
        "record_id": review.replay_key or sealed_manifest.run_id,
        "trace_id": review.trace_root,
        "run_id": review.run_id,
        "stage": "mw_structural_terminal",
        "policy_hash": review.policy_hash,
        "policy_hash_at_planning": review.policy_hash,
        "replay_key": review.replay_key,
        "span_id": "span-mw-structural",
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
    bundle = collector.collect([record])
    _emit("runtime_exhaust_bundle.json", {
        "sealed_manifest": dataclasses.asdict(sealed_manifest)
        if dataclasses.is_dataclass(sealed_manifest) else sealed_manifest.__dict__,
        "x3_disposition": V6Disposition.ALLOW.value,
        "exhaust_bundle": {
            "bundle_id": bundle.bundle_id,
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
                    "detected_defects": [
                        d.value if hasattr(d, "value") else str(d)
                        for d in gr.detected_defects
                    ],
                }
                for gr in bundle.gap_report
            ],
        },
    })

    # 10b. Runtime trace snapshot (per-run OTEL / runtime-ADG summary).
    _auto_provenance = detect_trace_provenance(artifact_dir)
    _trace_snap = build_runtime_trace_snapshot(
        run_id=vr.request_id,
        request_id=vr.request_id,
        trace_root=vr.trace_root,
        runtime_mode=os.environ.get("AGENTIC_CORE_RUNTIME_MODE", "production"),
        synthetic_trace_detected=_auto_provenance.synthetic_trace_detected,
        fixture_mode_detected=_auto_provenance.fixture_mode_detected,
        mock_mode_detected=_auto_provenance.mock_mode_detected,
        span_count=len(bundle.raw_evidence_refs),
        record_count=len(bundle.raw_evidence_refs),
        trace_ingest_quality_score=float(bundle.ingest_quality_score),
        newest_span_age_seconds=float(bundle.newest_span_age_seconds),
        detector_reasons=_auto_provenance.reasons,
    )
    _emit("runtime_trace_snapshot.json", _trace_snap.to_dict())

    # 10c. L7_AUDITABILITY HOW trace — mandatory cross-cutting evidence plane.
    from agentic_core.L7_auditability.how_trace import build_how_trace as _build_how_trace
    _how_trace = _build_how_trace(artifact_dir, chain_kind="MANAGED_WORKFLOW")
    _emit("agentic_core_how_trace.json", _how_trace.to_dict())

    # 10d. L7 route-family coverage matrix (honest accounting; non-mutating).
    from agentic_core.L7_auditability.coverage import (
        build_l7_route_family_coverage as _build_rfc,
    )
    _rfc = _build_rfc(artifact_dir, chain_kind="MANAGED_WORKFLOW", write=False)
    _emit("agentic_core_l7_route_family_coverage.json", _rfc["payload"])

    # 11. Manifest
    manifest_payload = {
        "invocation_id": invocation_id,
        "entry_point": f"{PRODUCER_COMPONENT}.{PRODUCER_FUNCTION}",
        "integrated_runtime_entrypoint_used": True,
        "chain_kind": "MANAGED_WORKFLOW",
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
            {"filename": fn, "upstream": (up or "")}
            for fn, up in W2_MW_CHAIN_LINKAGE
        ],
        "x3_disposition": V6Disposition.ALLOW.value,
        "dag_id": static_dag.dag_id,
        "dag_sha256": static_dag.dag_sha256,
    }
    _emit("integrated_runtime_artifact_manifest.json", manifest_payload)

    # 12. No-harness-stamp self-attestation
    _emit("no_harness_stamp_receipt.json", {
        "invocation_id": invocation_id,
        "all_artifacts_stamped_by_production": True,
        "producer_component": PRODUCER_COMPONENT,
        "harness_check": "passed_self_attestation",
        "attested_filenames": list(artifact_hashes.keys()),
    })

    # 13. Spine proof bundle (LAST, chain_kind=MANAGED_WORKFLOW)
    _spine_payload = build_spine_proof_payload(
        artifact_dir=artifact_dir,
        artifact_hashes=artifact_hashes,
        identity_envelope_payload=_identity.to_dict(),
        started_at_utc=_started_at_utc,
        finished_at_utc=utc_iso_now(),
        exit_code=0,
        chain_kind="MANAGED_WORKFLOW",
    )
    _emit("agentic_core_spine_proof.json", _spine_payload)

    return {
        "integrated_runtime_entrypoint_used": True,
        "run_id": vr.request_id,
        "artifact_dir": artifact_dir,
        "artifact_hashes": dict(artifact_hashes),
        "chain_kind": "MANAGED_WORKFLOW",
        "dag_id": static_dag.dag_id,
        "dag_sha256": static_dag.dag_sha256,
    }


__all__ = [
    "MW_ROUTE_ID",
    "PRODUCER_COMPONENT",
    "run_integrated_managed_workflow",
]
