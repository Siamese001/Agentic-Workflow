"""R4_SINGLE_ACTION — apps_lic deterministic pipeline entrypoint.

Thin composition wrapper over the canonical R4 entrypoint, applying
apps_lic-specific identity binding.  This module MUST NOT reimplement
U0, L1, L0, L2, Exit, C0, L5, UWG, or L6 behaviour — it only imports
and sequences the canonical components.

Pipeline sequence
-----------------
  raw_request (dict)
    → _build_lic_envelope          (apps_lic source_channel binding)
    → run_request_intake           (U0 six-question gate)
    → validated_request_to_plan_contract  (U0 → L1 bridge)
    → check_route_gates            (L0 decision-only)
    → C0 bypass receipt            (R4 has preloaded context — no corpus retrieval)
    → L2 static DAG execution      (caller-supplied callable; defined in apps_lic_static_dag.yaml)
    → ExitEvalPipeline.run         (Exit V6 — exactly one X3 disposition)
    → seal_runtime_exhaust         (sealed manifest)
    → LicR4RunResult

Harness rule (anti-cheat — verifier-enforced):
    Probes and tests MAY call ``run_integrated_r4_lic_pipeline``.
    They MUST NOT call ``run_request_intake``, ``check_route_gates``,
    ``ExitEvalPipeline.run``, or ``seal_runtime_exhaust`` directly for
    apps_lic coverage claims.  Every artifact emitted carries a
    ``producer_component`` that the verifier checks against the harness regex.

R5 terminal path:
    When L0 checks return a terminal verdict (R5_FATAL or R5_FALLBACK),
    this entrypoint emits an R5TerminalPacket, feeds it to Exit V6 as the
    sole receipt, and returns with ``terminal_r5=True``.  The L2 callable
    is NOT invoked.  The caller is responsible for propagating the exit code.

Relationship to apps_rg entrypoint:
    ``integrated_r4_deterministic_pipeline_run`` owns the apps_rg identity
    (source_channel="apps_rg_cli", declared_schema="apps_rg_jd_v1").
    This module owns the apps_lic identity (source_channel="apps_lic_cli",
    declared_schema="apps_lic_outreach_v1").  The pipeline logic is identical;
    only the envelope and result type differ.

Plan: ``.windsurf/plans/apps-lic-canonical-spine-wireup-e7c2a5.md`` W2 P4
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Canonical spine imports — compose, do not reimplement
# ---------------------------------------------------------------------------
from agentic_core.L0_routing.intake.envelope import RawIngressEnvelope
from agentic_core.L0_routing.intake.pipeline import run_request_intake
from agentic_core.L0_routing.intake.validated_request import ValidatedRequest
from agentic_core.L1_cognition.bridges.u0_to_l1_plan import (
    validated_request_to_plan_contract,
)
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
)
from agentic_core.L3_orchestration.exit_eval.v6.pipeline import (
    ExitEvalPipeline,
    ExitEvalResult,
)
from agentic_core.runtime.artifacts.integrated_runtime_emitter import (
    compute_artifact_hash,
)
from agentic_core.runtime.artifacts.spine_proof_bundle import (
    git_commit_and_dirty,
    utc_iso_now,
)
from agentic_core.runtime.contracts.c0_bypass_receipt import (
    build_c0_bypass_receipt,
)
from agentic_core.runtime.contracts.identity import (
    build_runtime_identity_envelope,
)

# ---------------------------------------------------------------------------
# apps_lic identity constants
# ---------------------------------------------------------------------------

CHAIN_KIND = "R4_SINGLE_ACTION"
ROUTE_FAMILY = "R4_SINGLE_ACTION"
ROUTE_ID = "R4_SINGLE_ACTION"

APP_NAME = "apps_lic"
SOURCE_CHANNEL = "apps_lic_cli"
DECLARED_SCHEMA = "apps_lic_outreach_v1"
USER_ID_DEFAULT = "u-apps_lic"

_PRODUCER_COMPONENT = (
    "agentic_core.runtime.entrypoints.integrated_r4_lic_pipeline_run"
)
_PRODUCER_FUNCTION = "run_integrated_r4_lic_pipeline"

_IDENTITY_RECEIPT_FILENAME = "r4_lic_identity_receipt.json"
_C0_BYPASS_RECEIPT_FILENAME = "r4_lic_c0_bypass_receipt.json"
_R4_RUN_MANIFEST_FILENAME = "r4_lic_run_manifest.json"


# ---------------------------------------------------------------------------
# Public result type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LicR4RunResult:
    """Result of one ``run_integrated_r4_lic_pipeline`` invocation."""

    run_id: str
    request_id: str
    route_id: str
    x3_disposition: str          # V6Disposition.value
    terminal_r5: bool            # True when L0 emitted R5 terminal before L2
    terminal_r5_reason: str      # populated when terminal_r5=True
    artifact_dir: Path
    producer_component: str = _PRODUCER_COMPONENT
    fault: str = ""              # populated on unexpected internal error


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _write_json(path: Path, payload: dict[str, Any]) -> str:
    """Write payload as canonical JSON; return sha256 hex."""
    blob = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(blob, encoding="utf-8")
    return f"sha256:{hashlib.sha256(blob.encode()).hexdigest()}"


def _build_lic_envelope(raw_request: dict[str, Any]) -> RawIngressEnvelope:
    """Map caller dict → RawIngressEnvelope with apps_lic identity binding.

    apps_lic requests carry outreach-specific fields (recipient_class,
    channel, outreach_mode) rather than the JD-centric fields apps_rg uses.
    """
    body_text = (
        raw_request.get("body_text")
        or raw_request.get("query")
        or json.dumps(
            {
                k: raw_request[k]
                for k in (
                    "recipient_class",
                    "channel",
                    "outreach_mode",
                    "manifest_id",
                )
                if k in raw_request
            }
        )
    )
    return RawIngressEnvelope(
        transport=str(raw_request.get("transport", "cli")),
        method=str(raw_request.get("method", "POST")),
        content_type=str(raw_request.get("content_type", "application/json")),
        source_channel=str(raw_request.get("source_channel", SOURCE_CHANNEL)),
        claimed_tenant_id=raw_request.get("tenant_id"),
        claimed_user_id=str(raw_request.get("user_id", USER_ID_DEFAULT)),
        body_text=body_text,
        body_bytes=None,
        declared_schema=str(
            raw_request.get("declared_schema", DECLARED_SCHEMA)
        ),
        declared_content_length=len(body_text.encode()),
        attachments=None,
        modality_manifest=None,
    )


def _compute_replay_key(raw_request: dict[str, Any]) -> str:
    """Deterministic replay key from stable outreach request fields."""
    stable = {
        k: raw_request[k]
        for k in (
            "manifest_hash",
            "policy_hash",
            "blueprint_hash",
            "recipient_brief_ref",
            "resume_ref",
        )
        if k in raw_request
    }
    blob = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
    return f"r4_lic:{hashlib.sha256(blob).hexdigest()[:16]}"


def _build_r5_exit_receipts(
    *,
    run_id: str,
    request_id: str,
    trace_root: str,
    reason_code: str,
) -> dict[str, Any]:
    """Minimal receipts dict for an R5 terminal path through Exit V6."""
    return {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": ROUTE_ID,
        "chain_kind": CHAIN_KIND,
        "app_name": APP_NAME,
        "terminal_r5": True,
        "r5_reason_code": reason_code,
        "l2_executed": False,
        "producer_component": _PRODUCER_COMPONENT,
        "producer_function": _PRODUCER_FUNCTION,
        "timestamp_utc": _utc_now_iso(),
    }


def _build_l2_exit_receipts(
    *,
    run_id: str,
    request_id: str,
    trace_root: str,
    l2_result: Any,
    replay_key: str,
) -> dict[str, Any]:
    """Receipts dict for a successful L2 execution path through Exit V6."""
    return {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": ROUTE_ID,
        "chain_kind": CHAIN_KIND,
        "app_name": APP_NAME,
        "terminal_r5": False,
        "r5_reason_code": "",
        "l2_executed": True,
        "replay_key": replay_key,
        "producer_component": _PRODUCER_COMPONENT,
        "producer_function": _PRODUCER_FUNCTION,
        "l2_result_type": type(l2_result).__name__,
        "timestamp_utc": _utc_now_iso(),
    }


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


def run_integrated_r4_lic_pipeline(
    raw_request: dict[str, Any],
    *,
    app_name: str | None = None,
    l2_callable: Callable[[ValidatedRequest, Any], Any] | None = None,
    artifact_dir: Path | None = None,
    exit_pipeline: ExitEvalPipeline | None = None,
    run_id: str | None = None,
    _test_mode: bool = False,
) -> LicR4RunResult:
    """Run the apps_lic R4_SINGLE_ACTION pipeline end-to-end.

    Args:
        raw_request: Caller-supplied request dict with outreach fields
            (recipient_class, channel, outreach_mode, manifest_id, etc.).
        app_name: App identifier for core-owned L2 recipe resolution.
            Required when l2_callable is not provided.
        l2_callable: Optional caller-supplied L2 execution function.
            Only allowed with _test_mode=True.
        artifact_dir: Directory for run artifacts. Defaults to a temp path.
        exit_pipeline: Optional pre-configured ExitEvalPipeline. Defaults
            to a new instance.
        run_id: Optional explicit run ID. Defaults to a new UUID4.
        _test_mode: Internal flag to allow l2_callable injection for tests.

    Returns:
        LicR4RunResult with x3_disposition, terminal_r5, and artifact_dir.
    """
    run_id = run_id or str(uuid.uuid4())
    request_id = str(raw_request.get("request_id", uuid.uuid4()))
    trace_root = str(raw_request.get("trace_id", f"tr-lic-{run_id[:8]}"))
    replay_key = _compute_replay_key(raw_request)

    if artifact_dir is None:
        import tempfile
        artifact_dir = Path(tempfile.mkdtemp(prefix=f"apps_lic_r4_{run_id[:8]}_"))
    artifact_dir.mkdir(parents=True, exist_ok=True)

    if exit_pipeline is None:
        exit_pipeline = ExitEvalPipeline(app_name=APP_NAME)

    # ------------------------------------------------------------------
    # U0 — request intake (six-question gate)
    # ------------------------------------------------------------------
    envelope = _build_lic_envelope(raw_request)
    try:
        validated_request = run_request_intake(envelope)
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- U0 intake failures must produce a
        # fault result without crashing the caller; exit code 2 per plan §7
        return LicR4RunResult(
            run_id=run_id,
            request_id=request_id,
            route_id="U0_REJECTION",
            x3_disposition=V6Disposition.DENY.value,
            terminal_r5=True,
            terminal_r5_reason="SCHEMA_REJECTION",
            artifact_dir=artifact_dir,
            fault=str(exc),
        )

    # ------------------------------------------------------------------
    # L1 — plan contract
    # ------------------------------------------------------------------
    plan_contract = validated_request_to_plan_contract(validated_request)

    # ------------------------------------------------------------------
    # L0 — route gates (decision-only)
    # ------------------------------------------------------------------
    route_verdict = check_route_gates(validated_request, plan_contract)

    if getattr(route_verdict, "is_terminal", False):
        reason_code = getattr(route_verdict, "reason_code", "INVALID_ROUTE_CONTRACT")
        receipts = _build_r5_exit_receipts(
            run_id=run_id,
            request_id=request_id,
            trace_root=trace_root,
            reason_code=reason_code,
        )
        exit_result: ExitEvalResult = exit_pipeline.run(receipts)
        return LicR4RunResult(
            run_id=run_id,
            request_id=request_id,
            route_id=ROUTE_ID,
            x3_disposition=exit_result.x3_disposition.value,
            terminal_r5=True,
            terminal_r5_reason=reason_code,
            artifact_dir=artifact_dir,
        )

    # ------------------------------------------------------------------
    # C0 bypass receipt — R4 has preloaded context; no corpus retrieval
    # ------------------------------------------------------------------
    c0_bypass = build_c0_bypass_receipt(
        run_id=run_id,
        route_id=ROUTE_ID,
        reason="R4_SINGLE_ACTION_preloaded_manifest",
    )

    # ------------------------------------------------------------------
    # L2 recipe resolution — core-owned (caller may not inject callable)
    # ------------------------------------------------------------------
    if l2_callable is not None and not _test_mode:
        return LicR4RunResult(
            run_id=run_id,
            request_id=request_id,
            route_id=ROUTE_ID,
            x3_disposition=V6Disposition.DENY.value,
            terminal_r5=True,
            terminal_r5_reason="L2_CALLABLE_INJECTION_REJECTED",
            artifact_dir=artifact_dir,
            fault=(
                "L2_CALLABLE_INJECTION_REJECTED: Production callers must "
                "use app_name for recipe resolution. Direct l2_callable "
                "injection is only allowed with _test_mode=True."
            ),
        )

    if l2_callable is None:
        if not app_name:
            return LicR4RunResult(
                run_id=run_id,
                request_id=request_id,
                route_id=ROUTE_ID,
                x3_disposition=V6Disposition.DENY.value,
                terminal_r5=True,
                terminal_r5_reason="L2_RECIPE_RESOLUTION_FAILED",
                artifact_dir=artifact_dir,
                fault=(
                    "L2_RECIPE_RESOLUTION_FAILED: Either app_name or "
                    "l2_callable (with _test_mode=True) must be provided."
                ),
            )
        from agentic_core.runtime.l2_recipe_resolver import resolve_l2_recipe
        try:
            l2_callable = resolve_l2_recipe(app_name, raw_request)
        except KeyError as exc:
            return LicR4RunResult(
                run_id=run_id,
                request_id=request_id,
                route_id=ROUTE_ID,
                x3_disposition=V6Disposition.DENY.value,
                terminal_r5=True,
                terminal_r5_reason="L2_RECIPE_NOT_FOUND",
                artifact_dir=artifact_dir,
                fault=f"L2_RECIPE_NOT_FOUND:{exc}",
            )

    # ------------------------------------------------------------------
    # L2 — static DAG execution (core-resolved callable)
    # ------------------------------------------------------------------
    l2_result = l2_callable(validated_request, plan_contract)

    # ------------------------------------------------------------------
    # Exit V6 — exactly one X3 disposition
    # ------------------------------------------------------------------
    receipts = _build_l2_exit_receipts(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        l2_result=l2_result,
        replay_key=replay_key,
    )
    exit_result = exit_pipeline.run(receipts)

    # ------------------------------------------------------------------
    # Seal manifest to artifact_dir
    # ------------------------------------------------------------------
    manifest_payload = {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": ROUTE_ID,
        "chain_kind": CHAIN_KIND,
        "app_name": APP_NAME,
        "replay_key": replay_key,
        "x3_disposition": exit_result.x3_disposition.value,
        "producer_component": _PRODUCER_COMPONENT,
        "timestamp_utc": _utc_now_iso(),
    }
    _write_json(artifact_dir / _R4_RUN_MANIFEST_FILENAME, manifest_payload)

    return LicR4RunResult(
        run_id=run_id,
        request_id=request_id,
        route_id=ROUTE_ID,
        x3_disposition=exit_result.x3_disposition.value,
        terminal_r5=False,
        terminal_r5_reason="",
        artifact_dir=artifact_dir,
    )
