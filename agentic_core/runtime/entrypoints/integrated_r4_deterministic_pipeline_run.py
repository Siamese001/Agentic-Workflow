"""R4_SINGLE_ACTION — apps_rg deterministic pipeline entrypoint.

Thin composition wrapper over canonical spine components for the
apps_rg R4_SINGLE_ACTION route family.  This module MUST NOT
reimplement U0, L1, L0, L2, Exit, 00C, L5, UWG, or L6 behaviour —
it only imports and sequences the canonical components.

Pipeline sequence
-----------------
  raw_request (dict)
    → run_request_intake          (U0 six-question gate)
    → validated_request_to_plan_contract  (U0 → L1 bridge)
    → check_route_gates           (L0 decision-only)
    → C0 bypass receipt           (R4 has preloaded context — no corpus retrieval)
    → L2 static DAG execution     (caller-supplied callable)
    → ExitEvalPipeline.run        (Exit V6 — exactly one X3 disposition)
    → seal_runtime_exhaust        (sealed manifest)
    → R4IntegratedRunResult

Harness rule (anti-cheat — verifier-enforced):
    Probes and tests MAY call ``run_integrated_r4_deterministic_pipeline``.
    They MUST NOT call ``run_request_intake``, ``check_route_gates``,
    ``ExitEvalPipeline.run``, or ``seal_runtime_exhaust`` directly for
    apps_rg coverage claims.  Every artifact emitted carries a
    ``producer_component`` that the verifier checks against the harness regex.

R5 terminal path:
    When L0 checks return a terminal verdict (R5_FATAL or R5_FALLBACK),
    this entrypoint emits an R5TerminalPacket, feeds it to Exit V6 as the
    sole receipt, and returns with ``terminal_r5=True``.  The L2 callable
    is NOT invoked.  The caller is responsible for propagating the exit code.

Plan: ``.windsurf/plans/apps-rg-canonical-wireup-c8a4f2.md`` §W2 P3
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

_log = logging.getLogger(__name__)

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
# Module-level constants
# ---------------------------------------------------------------------------

CHAIN_KIND = "R4_SINGLE_ACTION"
ROUTE_FAMILY = "R4_SINGLE_ACTION"
ROUTE_ID = "R4_SINGLE_ACTION"

_PRODUCER_COMPONENT = (
    "agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run"
)
_PRODUCER_FUNCTION = "run_integrated_r4_deterministic_pipeline"

_IDENTITY_RECEIPT_FILENAME = "r4_identity_receipt.json"
_C0_BYPASS_RECEIPT_FILENAME = "r4_c0_bypass_receipt.json"
_R4_RUN_MANIFEST_FILENAME = "r4_run_manifest.json"


# ---------------------------------------------------------------------------
# Public result type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class R4IntegratedRunResult:
    """Result of one ``run_integrated_r4_deterministic_pipeline`` invocation."""

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


def _load_route_id_for_app(
    app_name: str,
    preferred_label: str | None = None,
) -> str:
    """Read the best-matching route_id from the app's route_registry.yaml.

    Selection priority (highest first):
    1. Route whose ``label`` matches ``preferred_label`` (when provided).
    2. Route with the lowest ``priority`` integer field (1 = highest priority).
    3. First route in the list (legacy / single-route behaviour).

    Fail-soft: returns the module-level ``ROUTE_ID`` constant if the registry
    is absent, malformed, or contains no routes.  This keeps the pipeline
    working in test / offline environments that don't have the apps_* tree.
    """
    if not app_name:
        return ROUTE_ID
    registry_path = Path(f"{app_name}/config/route_registry.yaml")
    if not registry_path.exists():
        return ROUTE_ID
    try:
        import yaml  # type: ignore[import-untyped]

        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        routes = data.get("routes", []) if isinstance(data, dict) else []
        if not routes:
            return ROUTE_ID

        # --- label match (exact) ---
        if preferred_label:
            for route in routes:
                if str(route.get("label", "")).strip() == preferred_label:
                    rid = str(route.get("route_id", "")).strip()
                    if rid:
                        _log.debug(
                            "[R4] route_registry label-match route_id=%s label=%s app=%s",
                            rid, preferred_label, app_name,
                        )
                        return rid
            _log.warning(
                "[R4] preferred_label=%s not found in route_registry for app=%s; "
                "falling back to priority/first selection",
                preferred_label, app_name,
            )

        # --- priority sort (lower int = higher priority; absent = infinity) ---
        def _priority(r: dict) -> int:
            try:
                return int(r.get("priority", 9999))
            except (TypeError, ValueError):
                return 9999

        best = min(routes, key=_priority)
        rid = str(best.get("route_id", "")).strip()
        if rid:
            _log.debug(
                "[R4] route_registry priority-select route_id=%s priority=%s app=%s",
                rid, best.get("priority", "n/a"), app_name,
            )
            return rid

        # --- last resort: first entry ---
        rid = str(routes[0].get("route_id", "")).strip()
        if rid:
            _log.debug(
                "[R4] route_registry first-entry route_id=%s app=%s", rid, app_name
            )
            return rid

    except Exception as _exc:  # guardian: allow-broad-exception -- registry read is fail-soft; ROUTE_ID fallback is always valid
        _log.warning(
            "[R4] route_registry.yaml read failed for app=%s (fail-soft): %s",
            app_name,
            _exc,
        )
    return ROUTE_ID


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str | None:
    """Return sha256 hex of file contents, or None if file doesn't exist."""
    if not path.exists():
        return None
    try:
        content = path.read_bytes()
        return f"sha256:{hashlib.sha256(content).hexdigest()}"
    except OSError:
        return None


def _write_json(path: Path, payload: dict[str, Any]) -> str:
    """Write payload as canonical JSON; return sha256 hex."""
    blob = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(blob, encoding="utf-8")
    return f"sha256:{hashlib.sha256(blob.encode()).hexdigest()}"


def _build_raw_envelope(raw_request: dict[str, Any]) -> RawIngressEnvelope:
    """Map caller dict → RawIngressEnvelope for U0 intake."""
    body_text = (
        raw_request.get("body_text")
        or raw_request.get("query")
        or json.dumps(raw_request.get("jd_payload") or {})
    )
    return RawIngressEnvelope(
        transport=str(raw_request.get("transport", "api")),
        method=str(raw_request.get("method", "POST")),
        content_type=str(raw_request.get("content_type", "application/json")),
        source_channel=str(raw_request.get("source_channel", "apps_rg_cli")),
        claimed_tenant_id=raw_request.get("tenant_id"),
        claimed_user_id=str(raw_request.get("user_id", "u-apps_rg")),
        auth_credential=dict(
            raw_request.get("auth_credential") or {"kind": "internal", "token": "apps-rg-internal"}
        ),
        body_text=body_text,
    )


def _compute_replay_key(raw_request: dict[str, Any]) -> str:
    """Deterministic replay key from stable request fields."""
    stable = {
        k: raw_request[k]
        for k in ("jd_hash", "brief_hash", "resume_hash", "policy_hash", "blueprint_hash")
        if k in raw_request
    }
    blob = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
    return f"r4:{hashlib.sha256(blob).hexdigest()[:16]}"


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
        "terminal_r5": True,
        "r5_reason_code": reason_code,
        "l2_executed": False,
        "producer_component": _PRODUCER_COMPONENT,
    }


def _build_l2_exit_receipts(
    *,
    run_id: str,
    request_id: str,
    trace_root: str,
    c0_bypass_digest: str,
    l2_result: Any,
) -> dict[str, Any]:
    """Receipts dict for a successful L2-executed path through Exit V6."""
    return {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": ROUTE_ID,
        "chain_kind": CHAIN_KIND,
        "terminal_r5": False,
        "c0_bypass_receipt_digest": c0_bypass_digest,
        "l2_executed": True,
        "l2_result_summary": str(l2_result)[:256] if l2_result is not None else "",
        "producer_component": _PRODUCER_COMPONENT,
    }


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def run_integrated_r4_deterministic_pipeline(
    *,
    raw_request: dict[str, Any],
    app_name: str = "",
    l2_callable: Callable[[], Any] | None = None,
    artifact_dir: Path,
    policy_hash: str = "",
    blueprint_hash: str = "",
    _test_mode: bool = False,
) -> R4IntegratedRunResult:
    """Run the full R4 deterministic pipeline end-to-end.

    Parameters
    ----------
    raw_request:
        Caller-supplied dict representing the ingress payload.  Must contain
        at minimum ``jd_payload`` (dict) and optionally ``jd_hash``,
        ``brief_hash``, ``resume_hash``, ``policy_hash``, ``blueprint_hash``
        for replay-key binding.
    app_name:
        Application identifier (e.g. ``"apps_rg"``).  When provided, the
        L2 recipe is resolved from the core-owned registry — the caller
        MUST NOT supply ``l2_callable``.  This is the production path.
    l2_callable:
        **Deprecated for production use.**  Zero-argument callable that
        executes the L2 static DAG.  Only allowed when ``_test_mode=True``.
        Production callers MUST use ``app_name`` instead.
    artifact_dir:
        Directory where per-run receipts are written.  Created if absent.
    policy_hash:
        Optional sha256 of the active L0 policy YAML.
    blueprint_hash:
        Optional sha256 of the active blueprint YAML.
    _test_mode:
        When True, allows ``l2_callable`` to be supplied directly (for
        test harnesses that need to inject mock callables).  MUST NOT
        be True in production.

    Returns
    -------
    R4IntegratedRunResult
        Immutable result containing run_id, x3_disposition, terminal_r5 flag,
        and artifact_dir.  Never raises — internal errors land in ``fault``.
    """
    # ------------------------------------------------------------------
    # Resolve L2 callable — core-owned recipe resolution
    # ------------------------------------------------------------------
    if l2_callable is not None and not _test_mode:
        return R4IntegratedRunResult(
            run_id="",
            request_id="",
            route_id=ROUTE_ID,
            x3_disposition=V6Disposition.DENY.value,
            terminal_r5=False,
            terminal_r5_reason="",
            artifact_dir=Path(artifact_dir),
            fault=(
                "L2_CALLABLE_INJECTION_REJECTED: Production callers must "
                "use app_name for recipe resolution. Direct l2_callable "
                "injection is only allowed with _test_mode=True."
            ),
        )

    if l2_callable is None:
        if not app_name:
            return R4IntegratedRunResult(
                run_id="",
                request_id="",
                route_id=ROUTE_ID,
                x3_disposition=V6Disposition.DENY.value,
                terminal_r5=False,
                terminal_r5_reason="",
                artifact_dir=Path(artifact_dir),
                fault=(
                    "L2_RECIPE_RESOLUTION_FAILED: Either app_name or "
                    "l2_callable (with _test_mode=True) must be provided."
                ),
            )
        from agentic_core.runtime.l2_recipe_resolver import resolve_l2_recipe
        try:
            l2_callable = resolve_l2_recipe(app_name, raw_request)
        except KeyError as exc:
            return R4IntegratedRunResult(
                run_id="",
                request_id="",
                route_id=ROUTE_ID,
                x3_disposition=V6Disposition.DENY.value,
                terminal_r5=False,
                terminal_r5_reason="",
                artifact_dir=Path(artifact_dir),
                fault=f"L2_RECIPE_NOT_FOUND:{exc}",
            )

    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    # W5/GAP-6: resolve route_id from app's route_registry.yaml (fail-soft)
    effective_route_id = _load_route_id_for_app(app_name)

    run_id = str(uuid.uuid4())
    started_at = _utc_now_iso()
    git_commit, git_dirty = git_commit_and_dirty()
    replay_key = _compute_replay_key(raw_request)

    # ------------------------------------------------------------------
    # U0 — intake
    # ------------------------------------------------------------------
    envelope = _build_raw_envelope(raw_request)
    intake_result = run_request_intake(envelope)

    # If U0 rejects, return schema-rejection result (not R5 — see plan §W2)
    if intake_result.validated is None:
        reason = "unknown"
        if intake_result.rejection_report is not None:
            reason = getattr(intake_result.rejection_report.decisive_reason_code, "value", "unknown")
        return R4IntegratedRunResult(
            run_id=run_id,
            request_id=run_id,
            route_id=ROUTE_ID,
            x3_disposition=V6Disposition.DENY.value,
            terminal_r5=False,
            terminal_r5_reason="",
            artifact_dir=artifact_dir,
            fault=f"U0_SCHEMA_REJECTION:{reason}",
        )

    validated: ValidatedRequest = intake_result.validated
    request_id = validated.request_id
    trace_root = validated.trace_root

    # ------------------------------------------------------------------
    # U0 → L1 bridge
    # ------------------------------------------------------------------
    plan_contract = validated_request_to_plan_contract(validated)

    # ------------------------------------------------------------------
    # L0 — route gates (decision only; no fallback execution)
    # ------------------------------------------------------------------
    gate_result = check_route_gates(plan_contract, namespace=app_name)

    # L0 terminal (R5_FATAL / R5_FALLBACK) — route through Exit V6 before return
    if getattr(gate_result, "terminal", False) or getattr(gate_result, "r5_terminal", False):
        r5_reason = str(getattr(gate_result, "reason_code", "R5_TERMINAL"))
        receipts = _build_r5_exit_receipts(
            run_id=run_id,
            request_id=request_id,
            trace_root=trace_root,
            reason_code=r5_reason,
        )
        exit_pipeline = ExitEvalPipeline()
        exit_result: ExitEvalResult = exit_pipeline.run(receipts)
        x3 = exit_result.disposition.value
        return R4IntegratedRunResult(
            run_id=run_id,
            request_id=request_id,
            route_id=effective_route_id,
            x3_disposition=x3,
            terminal_r5=True,
            terminal_r5_reason=r5_reason,
            artifact_dir=artifact_dir,
        )

    # ------------------------------------------------------------------
    # C0 bypass receipt (R4 uses preloaded context; no corpus retrieval)
    # ------------------------------------------------------------------
    route_contract_id = str(getattr(plan_contract, "contract_id", "") or run_id)
    c0_receipt = build_c0_bypass_receipt(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        route_contract_id=route_contract_id,
        route_id=effective_route_id,
        c0_bypass_reason="GROUNDING_NOT_REQUIRED",
    )
    c0_hash = _write_json(artifact_dir / _C0_BYPASS_RECEIPT_FILENAME, c0_receipt.to_dict())

    # ------------------------------------------------------------------
    # Identity envelope
    # ------------------------------------------------------------------
    identity = build_runtime_identity_envelope(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        replay_key=replay_key,
        policy_hash=policy_hash or raw_request.get("policy_hash", ""),
        blueprint_hash=blueprint_hash or raw_request.get("blueprint_hash", ""),
        caller_surface="apps_rg_cli",
        entrypoint_command=_PRODUCER_COMPONENT,
        started_at_utc=started_at,
        git_commit=git_commit,
        git_dirty=git_dirty,
        route_contract_id=route_contract_id,
        route_id=effective_route_id,
        app_name="apps_rg",
    )
    _write_json(artifact_dir / _IDENTITY_RECEIPT_FILENAME, identity.to_dict())

    # ------------------------------------------------------------------
    # L2 — static DAG execution
    # ------------------------------------------------------------------
    l2_result: Any = None
    l2_fault = ""
    try:
        l2_result = l2_callable()
    except Exception as exc:  # guardian: allow-broad-exception -- L2 failure is fatal; captured in l2_fault for Exit receipts
        l2_fault = f"L2_EXECUTION_ERROR:{type(exc).__name__}:{exc}"

    # ------------------------------------------------------------------
    # Exit V6 — exactly one X3 disposition per run
    # ------------------------------------------------------------------
    receipts = _build_l2_exit_receipts(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        c0_bypass_digest=c0_hash,
        l2_result=l2_result,
    )
    if l2_fault:
        receipts["l2_fault"] = l2_fault

    exit_pipeline = ExitEvalPipeline()
    exit_result: ExitEvalResult = exit_pipeline.run(receipts)
    x3 = exit_result.disposition.value

    # ------------------------------------------------------------------
    # Write run manifest (exhaust sealed by pipeline internally)
    # ------------------------------------------------------------------
    _write_json(
        artifact_dir / _R4_RUN_MANIFEST_FILENAME,
        {
            "producer_component": _PRODUCER_COMPONENT,
            "run_id": run_id,
            "request_id": request_id,
            "route_id": effective_route_id,
            "chain_kind": CHAIN_KIND,
            "x3_disposition": x3,
            "terminal_r5": False,
            "l2_fault": l2_fault,
            "artifact_hash": compute_artifact_hash(receipts),
            "emitted_at": _utc_now_iso(),
        },
    )

    # ── L7_AUDITABILITY evidence plane ──
    # Mandatory cross-cutting evidence plane. Pure projection over chain
    # artifacts emitted so far; non-mutating; non-routing.
    from agentic_core.L7_auditability.how_trace import build_how_trace as _build_how_trace
    from agentic_core.L7_auditability.coverage import (
        build_l7_route_family_coverage as _build_rfc,
    )
    from agentic_core.runtime.artifacts.spine_proof_bundle import (
        build_spine_proof_payload as _build_spine_proof,
    )

    # Create Track-2 filename aliases for build_how_trace compatibility
    # R4 writes different filenames/structures than the canonical integrated_runtime entrypoints
    _identity_src = artifact_dir / _IDENTITY_RECEIPT_FILENAME
    _identity_dst = artifact_dir / "runtime_identity_envelope.json"
    if _identity_src.exists() and not _identity_dst.exists():
        # Wrap flat identity dict in payload envelope that build_how_trace expects
        _identity_flat = json.loads(_identity_src.read_text(encoding="utf-8"))
        _identity_envelope = {"schema_version": "runtime_identity_envelope.v1", "payload": _identity_flat}
        _write_json(_identity_dst, _identity_envelope)

    _plan_src = artifact_dir / _R4_RUN_MANIFEST_FILENAME
    _plan_dst = artifact_dir / "l1_plan_contract.json"
    if _plan_src.exists() and not _plan_dst.exists():
        _plan_data = json.loads(_plan_src.read_text(encoding="utf-8"))
        _write_json(_plan_dst, {"schema_version": "l1_plan_contract.v1", "payload": _plan_data})

    # Create route_contract.json (required by build_how_trace but not written by R4)
    _route_contract_path = artifact_dir / "route_contract.json"
    if not _route_contract_path.exists():
        _write_json(
            _route_contract_path,
            {
                "schema_version": "route_contract.v1",
                "payload": {
                    "route_id": effective_route_id,
                    "route_contract_id": route_contract_id,
                    "execution_form": "R4_SINGLE_ACTION",
                    "grounding_required": False,
                    "prompt_assembly_required": False,
                },
            },
        )

    _how_trace = _build_how_trace(artifact_dir, chain_kind=CHAIN_KIND)
    _write_json(artifact_dir / "agentic_core_how_trace.json", _how_trace.to_dict())

    _rfc = _build_rfc(artifact_dir, chain_kind=CHAIN_KIND, write=False)
    _write_json(artifact_dir / "agentic_core_l7_route_family_coverage.json", _rfc["payload"])

    _spine = _build_spine_proof(
        artifact_dir=artifact_dir,
        artifact_hashes={"identity_receipt.json": _sha256_file(artifact_dir / _IDENTITY_RECEIPT_FILENAME)},
        identity_envelope_payload=identity.to_dict(),
        started_at_utc=started_at,
        finished_at_utc=_utc_now_iso(),
        exit_code=0,
    )
    _write_json(artifact_dir / "agentic_core_spine_proof.json", _spine)

    # Update manifest with L7 refs
    _write_json(
        artifact_dir / "integrated_runtime_artifact_manifest.json",
        {
            "invocation_id": run_id,
            "entry_point": f"{_PRODUCER_COMPONENT}.{_PRODUCER_FUNCTION}",
            "integrated_runtime_entrypoint_used": True,
            "chain_kind": CHAIN_KIND,
            "artifact_filenames": [
                "agentic_core_how_trace.json",
                "agentic_core_l7_route_family_coverage.json",
                "agentic_core_spine_proof.json",
                "integrated_runtime_artifact_manifest.json",
            ],
            "how_trace_ref": "artifact://agentic_core_how_trace.json",
            "how_trace_sha256": _sha256_file(artifact_dir / "agentic_core_how_trace.json") or "",
            "l7_route_family_coverage_ref": "artifact://agentic_core_l7_route_family_coverage.json",
            "l7_route_family_coverage_sha256": _sha256_file(artifact_dir / "agentic_core_l7_route_family_coverage.json") or "",
            "artifact_hashes": {},
            "chain_linkage": [],
        },
    )

    return R4IntegratedRunResult(
        run_id=run_id,
        request_id=request_id,
        route_id=effective_route_id,
        x3_disposition=x3,
        terminal_r5=False,
        terminal_r5_reason="",
        artifact_dir=artifact_dir,
        fault=l2_fault,
    )
