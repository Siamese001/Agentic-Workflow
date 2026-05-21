"""L2 execution binding for apps_lic `outreach_message` managed workflow.

L2 is the SEVENTH stage of the pipeline. Its job is to:

1. Consume the bounded L3StepContract and optional CompiledPromptArtifact
   handed off by L3.
2. Wrap HopPipelineExecutor.run(REGISTRY) as ONE bounded execution packet
   (the full 9-stage HOP DAG is treated as a single L2 step).
3. Emit a SealedL2Artifact that:
   - preserves evidence_refs, prompt_refs, tool_call_refs, model_call_refs,
     provider_receipts, otel_span_refs, replay_manifest, audit_manifest_ref
   - carries proposed_state_diff = None (inert — no durable state committed)
   - sets state_diff_authorized = False (no L4 write authority)
   - threads tenant_id, sandbox/egress/allowed fields from RouteContract

AG-8 W6 invariants (apps-lic-ag8-golden-template-adoption-f3c2e1):
    - L2 receives the bounded L3StepContract (no_durable_commit_authority=True).
    - L2 wraps HopPipelineExecutor.run(REGISTRY) only — no other execution.
    - L2 emits SealedL2Artifact with proposed_state_diff inert (None).
    - L2 does NOT commit durable state.
    - L2 does NOT write L4 directly.
    - L2 does NOT mutate ChromaDB.
    - L2 does NOT generate embeddings.

HARD LAWS (AG-8 W6):
    - state_diff_authorized=False always.
    - is_uwg_write_authority=False always.
    - ChromaDB is never imported or called.
    - No embedding model calls.
    - L4 state writes are never performed.
    - Fail-soft: on HOP pipeline failure, emit SealedL2Artifact with
      execution_status='stub_fallback' rather than crashing the chain.

Plan: .windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W6)
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Optional

from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.origin import Origin
from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import L3StepContract

_LOGGER = logging.getLogger(__name__)

APPS_LIC_L2_CERT_REF: str = "l2-apps-lic-outreach-message-ag8-w6-f3c2e1"

_EXECUTION_FORM_MANAGED: str = "managed_workflow"


def _sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _build_evidence_refs(
    fec: FinalEvidenceContract,
) -> tuple[str, ...]:
    """Collect evidence refs from FEC for opaque-ref preservation."""
    refs: list[str] = []
    if fec.compilation_hash:
        refs.append(f"fec:{fec.compilation_hash[:24]}")
    for item in fec.evidence_items:
        if item.chunk_digest and item.chunk_digest != "NOT_APPLICABLE":
            refs.append(f"chunk:{item.chunk_digest[:24]}")
    return tuple(refs)


def _build_prompt_refs(
    prompt: Optional[CompiledPromptArtifact],
) -> tuple[str, ...]:
    """Collect prompt artifact refs for opaque-ref preservation."""
    if prompt is None:
        return ()
    refs: list[str] = []
    if prompt.compilation_hash:
        refs.append(f"pa:{prompt.compilation_hash[:24]}")
    if prompt.replay_manifest_ref:
        refs.append(f"rpm:{prompt.replay_manifest_ref[:24]}")
    return tuple(refs)


def _build_replay_manifest(
    step: L3StepContract,
    route: RouteContract,
    run_record_id: str,
) -> str:
    """Build a replay manifest ref tying together all replay inputs."""
    payload = _canonical_json({
        "replay_key": step.replay_key,
        "idempotency_key": step.idempotency_key,
        "workflow_id": step.workflow_id,
        "node_id": step.node_id,
        "run_id": route.run_id,
        "run_record_id": run_record_id,
        "snapshot_id": step.snapshot_id,
    })
    return f"rman:{_sha256_hex(payload)[:24]}"


def _build_audit_manifest_ref(
    step: L3StepContract,
    execution_status: str,
    run_record_id: str,
) -> str:
    """Build an audit manifest ref binding step contract to execution outcome."""
    payload = _canonical_json({
        "step_contract_hash": step.step_contract_hash,
        "workflow_id": step.workflow_id,
        "node_id": step.node_id,
        "execution_status": execution_status,
        "run_record_id": run_record_id,
    })
    return f"aman:{_sha256_hex(payload)[:24]}"


def _build_model_call_refs(run_record_id: str, checkpoints: tuple) -> tuple[str, ...]:
    """Build model call refs from HOP pipeline checkpoints."""
    refs: list[str] = []
    for cp in checkpoints:
        cp_name = getattr(cp, "stage_name", None) or ""
        cp_id = getattr(cp, "stage_id", 0)
        status = getattr(cp, "status", None)
        if status is not None and str(status) in ("COMPLETED", "StageStatus.COMPLETED"):
            refs.append(f"mref:{run_record_id[:8]}:stage{cp_id}:{cp_name[:12]}")
    return tuple(refs)


def _build_provider_receipts(run_record_id: str) -> tuple[str, ...]:
    """Build provider receipt refs (one per run for apps_lic HOP pipeline)."""
    digest = _sha256_hex(run_record_id)[:16]
    return (f"prov:apps_lic:{digest}",)


def _invoke_hop_pipeline(
    step: L3StepContract,
    route: RouteContract,
    fec: FinalEvidenceContract,
    prompt: Optional[CompiledPromptArtifact],
) -> tuple[str, Any, Any]:
    """Invoke HopPipelineExecutor.run(REGISTRY) as one bounded execution packet.

    Returns (execution_status, hop_run_record, generated_content).

    Hard laws:
    - Only HopPipelineExecutor.run(REGISTRY) is invoked — no other entry point.
    - No direct L4 writes, no ChromaDB calls, no embedding generation.
    - On failure: returns ('stub_fallback', None, None) — never raises.
    """
    from apps_lic.config.hop_pipeline import REGISTRY
    from apps_shared.orchestration import HopPipelineExecutor

    # Build the initial context from FEC + prompt + route
    context: dict[str, Any] = {
        "run_id": route.run_id,
        "request_id": route.request_id,
        "tenant_id": route.tenant_id,
        "trace_id": route.trace_id,
        "workflow_id": step.workflow_id,
        "node_id": step.node_id,
        "step_contract_id": step.step_contract_id,
        "capability_token": step.capability_token_requirement,
        "sandbox_envelope": step.sandbox_envelope_requirement,
        "allowed_tools": list(route.allowed_tools),
        "allowed_models": list(route.allowed_models),
        # C0 evidence as data only — no instruction authority
        "evidence_bundle": {
            "compilation_hash": fec.compilation_hash,
            "tenant_id": fec.tenant_id,
            "evidence_items": [
                {
                    "source_id": item.source_id,
                    "source_type": item.source_type,
                    "citation_anchor": item.citation_anchor,
                    "support_status": item.support_status,
                }
                for item in fec.evidence_items
            ],
        },
        # PA prompt artifact (data only, carried by reference)
        "prompt_artifact_digest": (
            prompt.compilation_hash if prompt is not None else ""
        ),
        "campaign_request": {
            "route_id": route.route_id,
            "execution_form": route.execution_form,
            "route_family": route.route_family,
        },
    }

    executor = HopPipelineExecutor(REGISTRY)
    try:
        run_record = executor.run(context)
    except Exception as exc:  # guardian: allow-broad-exception -- L2 fail-soft; HOP pipeline errors must not crash the contract chain
        _LOGGER.warning(
            "[apps_lic L2] HopPipelineExecutor raised: %s — emitting stub_fallback",
            exc,
        )
        return "stub_fallback", None, None

    if run_record.success:
        final_ctx = run_record.final_context or {}
        generated_content = final_ctx.get("draft_message", "") or ""
        return "completed", run_record, generated_content
    else:
        return "stub_fallback", run_record, None


def l2_execute_apps_lic(
    route: RouteContract,
    fec: FinalEvidenceContract,
    step: L3StepContract,
    prompt: Optional[CompiledPromptArtifact] = None,
) -> SealedL2Artifact:
    """Execute one bounded apps_lic L2 step and emit a SealedL2Artifact.

    Wraps ``HopPipelineExecutor.run(REGISTRY)`` as the sole execution
    entrypoint. Never commits durable state. Never writes L4. Never mutates
    ChromaDB. Never generates embeddings.

    Args:
        route:  RouteContract from L0 (execution_form='managed_workflow').
        fec:    FinalEvidenceContract from C0.
        step:   L3StepContract handed off by the L3 binding.
        prompt: CompiledPromptArtifact from PA (may be None for dry runs).

    Returns:
        SealedL2Artifact with all opaque-ref carrier fields preserved.

    Raises:
        TypeError:  if argument types are wrong.
        ValueError: if route.execution_form != 'managed_workflow'.
    """
    if not isinstance(route, RouteContract):
        raise TypeError(
            f"l2_execute_apps_lic expected RouteContract, got {type(route).__name__}"
        )
    if not isinstance(fec, FinalEvidenceContract):
        raise TypeError(
            f"l2_execute_apps_lic expected FinalEvidenceContract, got "
            f"{type(fec).__name__}"
        )
    if not isinstance(step, L3StepContract):
        raise TypeError(
            f"l2_execute_apps_lic expected L3StepContract, got {type(step).__name__}"
        )
    if route.execution_form != _EXECUTION_FORM_MANAGED:
        raise ValueError(
            f"l2_execute_apps_lic: route.execution_form must be "
            f"'{_EXECUTION_FORM_MANAGED}', got {route.execution_form!r}"
        )

    # Hard law: step must declare no durable commit authority.
    if not step.no_durable_commit_authority:
        raise ValueError(
            "l2_execute_apps_lic: step.no_durable_commit_authority must be True; "
            "L2 must not receive a step with durable commit authority"
        )

    start_ms = time.monotonic()
    execution_ts = datetime.now(timezone.utc).isoformat()

    # Invoke the single approved execution entrypoint.
    execution_status, run_record, generated_content = _invoke_hop_pipeline(
        step=step,
        route=route,
        fec=fec,
        prompt=prompt,
    )

    duration_ms = int((time.monotonic() - start_ms) * 1000)

    # Derive run_record_id for ref binding.
    run_record_id = (
        getattr(run_record, "run_id", None) or f"rr:{route.run_id[:16]}"
    )

    # Collect checkpoints for model_call_refs.
    checkpoints = (
        getattr(run_record, "checkpoints", ())
        if run_record is not None
        else ()
    )

    # -----------------------------------------------------------------------
    # Opaque-ref carrier fields — preserved as required by W6 spec.
    # -----------------------------------------------------------------------
    evidence_refs = _build_evidence_refs(fec)
    prompt_refs = _build_prompt_refs(prompt)
    replay_manifest = _build_replay_manifest(step, route, run_record_id)
    audit_manifest_ref = _build_audit_manifest_ref(
        step, execution_status, run_record_id
    )
    model_call_refs = _build_model_call_refs(run_record_id, checkpoints)
    provider_receipts = _build_provider_receipts(run_record_id)

    # tool_call_refs: carry capability token as the tool authorization ref
    tool_call_refs = (
        f"tcr:{_sha256_hex(step.capability_token_requirement)[:16]}",
    )

    # otel_span_refs: forward any route-level span refs + a new L2 span ref
    l2_span_ref = f"otel:l2:apps_lic:{_sha256_hex(route.run_id)[:16]}"
    otel_span_refs = tuple(route.otel_span_refs) + (l2_span_ref,)

    # -----------------------------------------------------------------------
    # Compilation hash: binds evidence → prompt → sealed artifact chain.
    # -----------------------------------------------------------------------
    compilation_payload = _canonical_json({
        "fec_hash": fec.compilation_hash,
        "pa_hash": (prompt.compilation_hash if prompt else ""),
        "step_hash": step.step_contract_hash,
        "run_id": route.run_id,
    })
    compilation_hash = _sha256_hex(compilation_payload)

    # prompt_artifact_digest: taken directly from PA compilation_hash if present.
    prompt_artifact_digest = (
        prompt.compilation_hash if prompt is not None else ""
    )

    # sovereign_execution_receipt: carries HOP pipeline run record id.
    sovereign_execution_receipt = (
        f"hop_run:{run_record_id}"
        if execution_status == "completed"
        else f"stub:{route.run_id[:16]}"
    )

    # generated_content_origin: model-generated draft (HOP pipeline output).
    generated_content_origin = Origin.MODEL_GENERATION

    # -----------------------------------------------------------------------
    # Emit SealedL2Artifact — proposed_state_diff=None (inert, no L4 write).
    # -----------------------------------------------------------------------
    sealed = SealedL2Artifact(
        request_id=route.request_id,
        run_id=route.run_id,
        app_id=route.app_id,
        trace_id=route.trace_id,
        execution_status=execution_status,
        generated_content=generated_content or "",
        generated_content_origin=generated_content_origin,
        proposed_state_diff={},                   # inert — no durable commit
        state_diff_authorized=False,              # hard law: no L4 write authority
        execution_timestamp=execution_ts,
        execution_duration_ms=duration_ms,
        sovereign_execution_receipt=sovereign_execution_receipt,
        tenant_id=route.tenant_id or "apps_lic",
        # Capability / sandbox / egress — threaded from RouteContract.
        sandbox_required=route.sandbox_required,
        egress_policy_ref=route.egress_policy_ref,
        allowed_tools=route.allowed_tools,
        allowed_models=route.allowed_models,
        allowed_networks=route.allowed_networks,
        allowed_file_roots=route.allowed_file_roots,
        # Provenance chain.
        prompt_artifact_digest=prompt_artifact_digest,
        compilation_hash=compilation_hash,
        schema_version="W6.0",
        # Observability.
        otel_span_refs=otel_span_refs,
        audit_refs=tuple(route.audit_refs),
        # Governance.
        posture=route.posture,
        gate_verdict_refs=tuple(route.gate_verdict_refs),
        # Replay / snapshot.
        replay_key=step.replay_key,
        snapshot_refs=tuple(route.snapshot_refs),
        # L5 certification ref.
        l5_certification_ref=APPS_LIC_L2_CERT_REF,
        # Write authority — always False; apps_lic L2 emits only proposed_state_diff.
        is_uwg_write_authority=False,
        is_future_run_only=False,
        # Opaque-ref carrier fields (W6 requirement).
        evidence_refs=evidence_refs,
        prompt_refs=prompt_refs,
        tool_call_refs=tool_call_refs,
        model_call_refs=model_call_refs,
        provider_receipts=provider_receipts,
        replay_manifest=replay_manifest,
        audit_manifest_ref=audit_manifest_ref,
    )

    _LOGGER.debug(
        "[apps_lic L2] sealed artifact: status=%s run_id=%s duration_ms=%d "
        "evidence_refs=%d prompt_refs=%d model_call_refs=%d",
        execution_status,
        route.run_id,
        duration_ms,
        len(evidence_refs),
        len(prompt_refs),
        len(model_call_refs),
    )

    return sealed


__all__ = [
    "APPS_LIC_L2_CERT_REF",
    "l2_execute_apps_lic",
]
