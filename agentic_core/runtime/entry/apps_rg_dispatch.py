"""apps_rg-specific dispatch/parse/required_fields callables for AppIngressRunner.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §5 (re-opens c8b3e1 W6/W7).

These three callables are the thin glue between AppIngressRunner's generic
ingress envelope flow and the apps_rg domain runtime. They are pure
functions — no provider calls, no LLM logic, no state writes.

W2 (this file) lands the callable shape and a STUB dispatcher that emits a
well-formed X3Disposition with exit_status='stub_pending_w3'. The real
U0 -> L1 -> L0 -> [C0] -> [PA] -> L2 -> Exit pipeline binding lands in W3.

This is the W4 governance pattern from c8b3e1 §4.1: apps_rg builds an
ingress payload; core dispatches it; apps_rg never plans/routes/executes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

import json
import logging
from pathlib import Path

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    RequestEnvelope,
)
from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
    AppsRgAuthorityViolation,
)
from agentic_core.runtime.contracts.x3_disposition import X3Disposition
from agentic_core.L0_routing.apps_rg_l0_binding import l0_route_apps_rg
from agentic_core.L1_cognition.apps_rg_l1_binding import l1_plan_apps_rg
from agentic_core.L2_execution.apps_rg_l2_binding import l2_execute_apps_rg
from agentic_core.prompt_governance.apps_rg_pa_binding import pa_compose_apps_rg
from agentic_core.runtime.c0.apps_rg_c0_binding import c0_retrieve_apps_rg
from agentic_core.runtime.entry.u0_apps_rg_binding import (
    APPS_RG_TASK_CLASS,
    u0_validate_apps_rg,
)
from agentic_core.runtime.exit.apps_rg_exit_binding import (
    exit_finalize_apps_rg,
    _resolve_repo_root as _exit_resolve_repo_root,
    _safe_run_dirname,
    _ARTIFACT_BASE_DIR_RELPATH,
)
from agentic_core.runtime.contracts.otel_lifecycle_bridge import (
    install_bridge,
    get_bridge,
)

_DISPATCH_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Required fields — the payload keys that MUST be present and non-empty
# for AppIngressRunner to dispatch the request without surfacing a
# ClarificationRequired. Per c8b3e1 §4.1, target_company OR target_role
# AND a resume source are the minimum. AppIngressRunner only validates
# string-non-empty; we relax the OR-rules in parse() below.
# ---------------------------------------------------------------------------
APPS_RG_REQUIRED_FIELDS: tuple[str, ...] = (
    "target_company",
    "target_role",
)


# ---------------------------------------------------------------------------
# parse() — convert the normalized payload dict into a typed RequestEnvelope.
# Returns None to surface ClarificationRequired when payload cannot be parsed.
# ---------------------------------------------------------------------------
def apps_rg_parse(payload: Mapping[str, Any]) -> RequestEnvelope | None:
    """Build RequestEnvelope from a normalized payload dict.

    Returns None when:
      - payload is missing both target_company and target_role
      - payload is missing both source_resume_ref and source_resume_text
      - dataclass construction fails (validation error in __post_init__)
    """
    if not isinstance(payload, dict):
        return None

    target_company = payload.get("target_company") or None
    target_role = payload.get("target_role") or None
    source_resume_ref = payload.get("source_resume_ref") or None
    source_resume_text = payload.get("source_resume_text") or None

    # Per AppsRgIngressPayload.__post_init__ invariant:
    #   at least one of (target_company, target_role) or (source_resume_ref, source_resume_text)
    if not (target_company or target_role):
        if not (source_resume_ref or source_resume_text):
            return None

    try:
        ingress = AppsRgIngressPayload(
            target_company=target_company,
            target_role=target_role,
            target_level=payload.get("target_level"),
            source_resume_ref=source_resume_ref,
            source_resume_text=source_resume_text,
            job_description_ref=payload.get("job_description_ref"),
            job_description_text=payload.get("job_description_text"),
            candidate_profile_path=payload.get("candidate_profile_path"),
            manual_brief_path=payload.get("manual_brief_path"),
            auto_research_internal=bool(payload.get("auto_research_internal", False)),
            auto_research_tavily=bool(payload.get("auto_research_tavily", False)),
            research_via=payload.get("research_via"),
            user_constraints=payload.get("user_constraints", {}) or {},
            output_preferences=payload.get("output_preferences", {}) or {},
            idempotency_key=payload.get("idempotency_key"),
        )
    except (TypeError, ValueError):
        return None

    return RequestEnvelope(
        payload=ingress,
        request_id=payload.get("request_id") or f"rg-req-{uuid4().hex[:12]}",
        run_id=payload.get("run_id") or f"rg-run-{uuid4().hex[:12]}",
        # W1 P1.2: tenant_id flows into envelope so U0 can stamp ValidatedRequest (D6)
        tenant_id=payload.get("tenant_id") or "",
        trace_id=payload.get("trace_id") or f"rg-trace-{uuid4().hex[:16]}",
        submitted_at=datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# OTEL span emission helper (W3 P3.1)
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Stage output persistence — write every stage's contract to the run dir
# ---------------------------------------------------------------------------
def _ensure_run_dir(run_id: str, timestamp_iso: str) -> Path:
    """Create and return the run directory for stage outputs."""
    repo_root = _exit_resolve_repo_root()
    dirname = _safe_run_dirname(run_id, timestamp_iso)
    run_dir = repo_root / _ARTIFACT_BASE_DIR_RELPATH / dirname
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _save_stage_output(run_dir: Path, stage: str, data: Any) -> None:
    """Persist a stage's contract output as JSON to run_dir/<stage>.json.

    All stage outputs live alongside final artifacts (generated_resume.json,
    run_metadata.json) in the same run directory for full audit trail.

    Fail-soft: never raise into the pipeline on serialization or I/O error.
    """
    try:
        run_dir.mkdir(parents=True, exist_ok=True)
        out_path = run_dir / f"{stage}.json"

        # Serialize: dataclass → dict, or use as-is if already a dict/mapping.
        if hasattr(data, "__dataclass_fields__"):
            from dataclasses import asdict
            serializable = asdict(data)
        elif hasattr(data, "model_dump"):
            serializable = data.model_dump(mode="python")
        elif isinstance(data, dict):
            serializable = data
        else:
            serializable = {"repr": repr(data)}

        def _default(obj: Any) -> Any:
            if isinstance(obj, Path):
                return str(obj)
            if isinstance(obj, (set, frozenset, tuple)):
                return list(obj)
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            return str(obj)

        out_path.write_text(
            json.dumps(serializable, indent=2, default=_default),
            encoding="utf-8",
        )
    except Exception:  # guardian: allow-broad-exception -- stage persistence is best-effort; must never block the pipeline
        _DISPATCH_LOGGER.debug("Failed to save stage output for %s", stage, exc_info=True)


def _emit_stage_span(stage: str, trace_id: str, status: str = "OK") -> None:
    """Emit a zero-duration marker span for pipeline stage telemetry."""
    bridge = get_bridge()
    if bridge is None:
        return
    import time
    import uuid
    now_ns = time.time_ns()
    span = {
        "trace_id": trace_id,
        "span_id": uuid.uuid4().hex[:16],
        "parent_span_id": None,
        "name": f"apps_rg.{stage}",
        "kind": "INTERNAL",
        "start_time_ns": now_ns,
        "end_time_ns": now_ns,
        "ts_utc": now_ns // 1_000_000,
        "duration_ms": 0.0,
        "status_code": status,
        "attributes": {
            "layer": stage.split("_")[0] if "_" in stage else stage,
            "app_id": "apps_rg",
            "stage": stage,
        },
        "events": [],
    }
    bridge._spans.append(span)


# ---------------------------------------------------------------------------
# dispatch() — invoke the apps_rg pipeline with the parsed RequestEnvelope.
# Returns an X3Disposition.
#
# W2 STUB: returns exit_status='stub_pending_w3' to prove the pipeline
# is reachable end-to-end. W3 replaces this with the real U0 -> L1 -> L0 ->
# [C0] -> [PA] -> L2 -> Exit chain via per-layer bindings.
# ---------------------------------------------------------------------------
def apps_rg_dispatch(envelope: RequestEnvelope) -> X3Disposition:
    """Dispatch the apps_rg request through the core runtime pipeline.

    Pipeline progress (per plan apps-rg-runtime-wiring-completion-d4e8a1 §6):
        ✅ W3.P1 — U0 ingress validator         (real)
        ✅ W3.P2 — L1 plan contract              (real)
        ✅ W3.P3 — L0 route contract             (real)
        ✅ W3.P4 — [C0] grounding / [PA] prompt  (real)
        ✅ W3.P5 — L2 execution + Exit           (real, L2 stub-mode)

    All 5 W3 phases landed. exit_status='success' on happy path; Exit
    writes the artifact under artifacts/apps_rg/runs/<ts_runid>/. Real
    LLM dispatch (replacing L2 stub) lands in W5.

    Each landed stage replaces a 'pending' marker in the disposition until
    the entire chain is real and exit_status='success'.
    """
    # W3 P3.1: Install OTEL bridge for span collection (noop if already installed)
    install_bridge(root_trace_id=envelope.trace_id, app_id="apps_rg")

    # Create run directory early so all stages can write their outputs.
    _dispatch_ts = datetime.now(timezone.utc).isoformat()
    run_dir = _ensure_run_dir(envelope.run_id, _dispatch_ts)

    # Save the parse/envelope output as stage 0.
    _save_stage_output(run_dir, "00_parse_envelope", {
        "request_id": envelope.request_id,
        "run_id": envelope.run_id,
        "trace_id": envelope.trace_id,
        "tenant_id": getattr(envelope, "tenant_id", ""),
        "submitted_at": getattr(envelope, "submitted_at", ""),
        "payload_type": type(envelope.payload).__name__,
    })

    if not isinstance(envelope, RequestEnvelope):
        # Defensive: wrong shape from parse() — surface as error disposition
        _emit_stage_span("dispatch_error", envelope.trace_id or "unknown", "ERROR")
        return X3Disposition(
            request_id="unknown",
            run_id="unknown",
            app_id="apps_rg",
            trace_id="unknown",
            exit_status="error",
            outcome_authorized=False,
            final_output={"error": "apps_rg_dispatch received non-RequestEnvelope"},
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-bad-envelope",
        )

    # ----------------------------------------------------------------- U0
    try:
        validated_request = u0_validate_apps_rg(envelope)
        _emit_stage_span("U0_validate", envelope.trace_id, "OK")
        _save_stage_output(run_dir, "01_U0_validated_request", validated_request)
    except AppsRgAuthorityViolation as violation:
        _emit_stage_span("U0_validate", envelope.trace_id, "ERROR")
        return X3Disposition(
            request_id=envelope.request_id,
            run_id=envelope.run_id,
            app_id="apps_rg",
            trace_id=envelope.trace_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "U0",
                "rejection_reason": "authority_violation",
                "detail": str(violation),
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-u0-authority-violation",
        )

    # ----------------------------------------------------------------- L1
    try:
        l1_plan = l1_plan_apps_rg(validated_request)
        _emit_stage_span("L1_plan", envelope.trace_id, "OK")
        _save_stage_output(run_dir, "02_L1_plan_contract", l1_plan)
    except (TypeError, ValueError) as l1_err:
        _emit_stage_span("L1_plan", envelope.trace_id, "ERROR")
        return X3Disposition(
            request_id=validated_request.request_id,
            run_id=validated_request.run_id,
            app_id="apps_rg",
            trace_id=validated_request.trace_id,
            tenant_id=validated_request.tenant_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "L1",
                "rejection_reason": "l1_planning_error",
                "detail": str(l1_err),
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-l1-planning",
        )

    # ----------------------------------------------------------------- L0
    try:
        route = l0_route_apps_rg(l1_plan)
        _emit_stage_span("L0_route", envelope.trace_id, "OK")
        _save_stage_output(run_dir, "03_L0_route_contract", route)
    except (TypeError, ValueError) as l0_err:
        _emit_stage_span("L0_route", envelope.trace_id, "ERROR")
        return X3Disposition(
            request_id=l1_plan.request_id,
            run_id=l1_plan.run_id,
            app_id="apps_rg",
            trace_id=l1_plan.trace_id,
            tenant_id=l1_plan.tenant_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "L0",
                "rejection_reason": "l0_routing_error",
                "detail": str(l0_err),
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-l0-routing",
        )

    # ----------------------------------------------------------------- C0 (conditional)
    fec = None
    if route.grounding_required:
        try:
            # AG-2 (apps-rg-app-payload-consumption-wiring-b3a449 W4.P4.3):
            # pass validated_request — C0 reads jd/resume content from
            # validated_request.app_payload, NOT from envelope.payload.
            fec = c0_retrieve_apps_rg(route, validated_request)
            _emit_stage_span("C0_retrieve", envelope.trace_id, "OK")
            _save_stage_output(run_dir, "04_C0_evidence_contract", fec)
        except (TypeError, ValueError, OSError) as c0_err:
            _emit_stage_span("C0_retrieve", envelope.trace_id, "ERROR")
            return X3Disposition(
                request_id=route.request_id,
                run_id=route.run_id,
                app_id="apps_rg",
                trace_id=route.trace_id,
                exit_status="failure",
                outcome_authorized=False,
                final_output={
                    "stage": "C0",
                    "rejection_reason": "c0_retrieval_error",
                    "detail": str(c0_err),
                },
                exit_timestamp=datetime.now(timezone.utc).isoformat(),
            )

    # ----------------------------------------------------------------- PA (conditional)
    prompt_artifact = None
    if route.model_generation_required:
        # PA requires a FinalEvidenceContract; if grounding wasn't requested we
        # build an empty FEC so the PA binding stays pure-typed.
        if fec is None:
            from agentic_core.runtime.contracts.final_evidence_contract import (
                FinalEvidenceContract as _FEC,
            )
            fec = _FEC(
                request_id=route.request_id,
                run_id=route.run_id,
                app_id=route.app_id,
                trace_id=route.trace_id,
                evidence_collection_timestamp=datetime.now(timezone.utc).isoformat(),
                schema_version="W3.P4",
                l5_certification_ref="c0-apps-rg-no-grounding-required",
            )
        try:
            # AG-2 (apps-rg-app-payload-consumption-wiring-b3a449 W4.P4.3):
            # pass validated_request — PA reads target / output / provenance
            # directives from validated_request.app_payload via L1 projections.
            prompt_artifact = pa_compose_apps_rg(route, l1_plan, fec, validated_request)
            _emit_stage_span("PA_compose", envelope.trace_id, "OK")
            _save_stage_output(run_dir, "05_PA_compiled_prompt", prompt_artifact)
        except (TypeError, ValueError) as pa_err:
            _emit_stage_span("PA_compose", envelope.trace_id, "ERROR")
            return X3Disposition(
                request_id=route.request_id,
                run_id=route.run_id,
                app_id="apps_rg",
                trace_id=route.trace_id,
                exit_status="failure",
                outcome_authorized=False,
                final_output={
                    "stage": "PA",
                    "rejection_reason": "pa_assembly_error",
                    "detail": str(pa_err),
                },
                exit_timestamp=datetime.now(timezone.utc).isoformat(),
            )

    # ----------------------------------------------------------------- L2
    if prompt_artifact is None:
        # No model generation requested — skip L2/Exit, emit pipeline-complete
        # disposition without an artifact write. This is the path for any
        # future task class that doesn't need an LLM.
        _emit_stage_span("dispatch_complete_no_gen", envelope.trace_id, "OK")
        return X3Disposition(
            request_id=route.request_id,
            run_id=route.run_id,
            app_id="apps_rg",
            trace_id=route.trace_id,
            tenant_id=route.tenant_id,
            exit_status="success",
            outcome_authorized=True,
            final_output={
                "stage": "U0_L1_L0_C0_PASSED_NO_GEN",
                "task_class": validated_request.task_class,
                "note": "model_generation_required=false — L2/Exit skipped",
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-no-gen-complete",
        )

    try:
        sealed = l2_execute_apps_rg(prompt_artifact)
        _emit_stage_span("L2_execute", envelope.trace_id, "OK")
        _save_stage_output(run_dir, "06_L2_sealed_artifact", sealed)
    except (TypeError, ValueError) as l2_err:
        _emit_stage_span("L2_execute", envelope.trace_id, "ERROR")
        return X3Disposition(
            request_id=route.request_id,
            run_id=route.run_id,
            app_id="apps_rg",
            trace_id=route.trace_id,
            tenant_id=route.tenant_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "L2",
                "rejection_reason": "l2_execution_error",
                "detail": str(l2_err),
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-l2-execution",
        )

    # ----------------------------------------------------------------- Exit
    # Patch B: pass fec (FinalEvidenceContract) through to Exit so factual_grounding
    # can be computed.  fec is None when grounding_required=False (generate_scratch);
    # exit_finalize_apps_rg handles None gracefully (factual_grounding stays absent).
    try:
        disposition = exit_finalize_apps_rg(sealed, prompt_artifact, fec=fec)
        _emit_stage_span("Exit_finalize", envelope.trace_id, "OK")
        _save_stage_output(run_dir, "07_Exit_disposition", disposition)
        return disposition
    except (TypeError, ValueError, OSError) as exit_err:
        return X3Disposition(
            request_id=route.request_id,
            run_id=route.run_id,
            app_id="apps_rg",
            trace_id=route.trace_id,
            tenant_id=route.tenant_id,
            exit_status="failure",
            outcome_authorized=False,
            final_output={
                "stage": "EXIT",
                "rejection_reason": "exit_finalization_error",
                "detail": str(exit_err),
                "sealed_compilation_hash": sealed.compilation_hash,
            },
            exit_timestamp=datetime.now(timezone.utc).isoformat(),
            l5_certification_ref="dispatch-error-exit-finalization",
        )

__all__ = [
    "APPS_RG_REQUIRED_FIELDS",
    "apps_rg_parse",
    "apps_rg_dispatch",
]
