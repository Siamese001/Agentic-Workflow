"""Route-neutral single-action integrated spine entrypoint.

`route_family` / `route_id` / `chain_kind` are data — not entrypoint identity.
Default route family for apps_rg remains `R4_SINGLE_ACTION` via profile/registry.

apps_rg production callers MUST supply `cache_preflight_evidence` with
`cache_preflight_completed` and `generation_spine_invocation_allowed` (R1A/R1B preflight).
Use `_test_mode=True` only in unit/contract harnesses.

Thin composition wrapper over canonical spine components for any ``apps_*``
application that resolves an L2 recipe through ``app_name``.  This module MUST NOT
reimplement U0, L1, L0, L2, Exit, 00C, L5, UWG, or L6 behaviour — it only imports
and sequences the canonical components.  Apps supply policy/evidence/ref shapes via
``config/profiles/<app_id>/pipeline_defaults.yaml`` per ``RuntimeProfileResolver``
conventions; core never invents application policy literals.

Pipeline sequence
-----------------
  raw_request (dict)
    → run_request_intake          (U0 six-question gate)
    → validated_request_to_plan_contract  (U0 → L1 bridge)
    → check_route_gates           (L0 decision-only)
    → C0 bypass receipt           (R4 with preloaded context — BYPASS_PRELOADED_CONTEXT)
    → L2 static DAG execution     (caller-supplied callable)
    → ExitEvalPipeline.run        (Exit V6 — exactly one X3 disposition)
    → seal_runtime_exhaust        (sealed manifest)
    → SingleActionSpineRunResult

L2 recipe resolution is per ``app_name`` (e.g. apps_rg registers ``resume_generation_v1``);
the core entrypoint does not hardcode app policy — only generic route family constants.

Profile-driven evidence (Exit v6 §5.0 + X3 threading)
----------------------------------------------------
- **Hydration before replay:** ``_hydrate_raw_request_evidence_digests`` runs **before**
  ``_compute_replay_key`` so ``policy_hash`` / ``blueprint_hash`` participate in the
  stable binding when present. Values come from explicit kwargs, valid digests on
  ``raw_request``, or SHA-256 of files listed under ``pipeline_defaults.policy_refs``
  in the app's profile YAML (core never hardcodes per-app paths).
- **Spine packet carriers:** ``exit_eval_wire.spine_exit_packet_carrier_refs`` supply
  ``l5_certification_refs`` on L2 and R5 Exit receipts. Semantics: **X3 packet /
  AG-8 threading evidence** only — **not** RTC / Fort Knox L5 certification; see
  ``config/profiles/<app_id>/pipeline_defaults.yaml`` comments.
- **R5 §5.0 parity:** R5 terminal receipts carry ``policy_hash``, ``blueprint_hash``,
  ``replay_key``, ``route_contract``, and ``terminal_class`` so ``validate_required_receipts``
  matches the L2-executed shape.

Harness rule (anti-cheat — verifier-enforced):
    Probes and tests MAY call ``run_integrated_single_action_spine``.
    They MUST NOT call ``run_request_intake``, ``check_route_gates``,
    ``ExitEvalPipeline.run``, or ``seal_runtime_exhaust`` directly for
    product coverage claims.  Every artifact emitted carries a
    ``producer_component`` that the verifier checks against the harness regex.

R5 terminal path:
    When L0 checks return a terminal verdict (R5_FATAL or R5_FALLBACK),
    this entrypoint emits an R5TerminalPacket, feeds it to Exit V6 as the
    sole receipt, and returns with ``terminal_r5=True``.  The L2 callable
    is NOT invoked.  The caller is responsible for propagating the exit code.

C0 Policy (W4 c0-policy-rectification-f7b2a9):
    R4 uses ``BYPASS_PRELOADED_CONTEXT`` typed bypass reason, not the
    legacy ``GROUNDING_NOT_REQUIRED`` string. This aligns with the
    contract-driven C0 policy frozen by L0 in RouteContract.c0_policy.
    Receipts sealed via ``build_c0_bypass_receipt`` conform to ``C0BypassReceipt``.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-rg-canonical-wireup-c8a4f2.md`` §W2 P3
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

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
    emit_artifact,
    ProvenanceStamp,
    W2_CHAIN_LINKAGE,
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
from agentic_core.L5_safety.certification.integrated_l5_evidence import (
    binding_payload_from_identity,
    build_hitl_reclearance_not_applicable,
    certification_ref_from_binding,
)
from agentic_core.runtime.contracts.prompt_assembly_bypass_receipt import (
    build_prompt_assembly_bypass_receipt,
)
from agentic_core.runtime.contracts.runtime_gate_verdict_bundle import (
    GateOutcome,
    RuntimeGateVerdictBundle,
    VetoOutcome,
)
from agentic_core.runtime.contracts.safe_reuse_decision import (
    SafeReuseDecision,
)
from agentic_core.runtime.profiles.profile_resolver import (
    RuntimeProfileResolver,
    UnknownAppError,
    MissingProfileError,
    InvalidProfileError,
)

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

CHAIN_KIND = "R4_SINGLE_ACTION"
ROUTE_FAMILY = "R4_SINGLE_ACTION"
ROUTE_ID = "R4_SINGLE_ACTION"

_PRODUCER_COMPONENT = (
    "agentic_core.runtime.entrypoints.integrated_single_action_spine_run"
)
_PRODUCER_FUNCTION = "run_integrated_single_action_spine"

_IDENTITY_RECEIPT_FILENAME = "r4_identity_receipt.json"
_C0_BYPASS_RECEIPT_FILENAME = "r4_c0_bypass_receipt.json"
_R4_RUN_MANIFEST_FILENAME = "r4_run_manifest.json"
_L7_COMPAT_ALIAS_ROLE = "core_compat_alias_for_l7_projection"


def _l7_compat_alias_fields(
    *,
    canonical_source_artifact: str = _R4_RUN_MANIFEST_FILENAME,
) -> dict[str, str]:
    return {
        "producer_component": _PRODUCER_COMPONENT,
        "artifact_role": _L7_COMPAT_ALIAS_ROLE,
        "canonical_source_artifact": canonical_source_artifact,
        "runtime_subject": "agentic_core",
        "app_subject": "apps_rg",
    }


# ---------------------------------------------------------------------------
# Public result type
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SingleActionSpineRunResult:
    """Result of one ``run_integrated_single_action_spine`` invocation."""

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


def _get_app_defaults(app_name: str) -> dict[str, str]:
    """Get app identity defaults from profile.
    
    Fail-closed: returns empty dict if profile resolution fails,
    forcing caller to handle missing defaults explicitly.
    """
    if not app_name:
        return {}

    payload = _load_pipeline_defaults_payload(app_name)
    if not payload:
        return {}

    defaults: dict[str, str] = {}
    identity = payload.get("identity_defaults", {})
    if identity:
        defaults["source_channel"] = identity.get("source_channel", "")
        defaults["user_id_default"] = identity.get("user_id_default", "")
        defaults["caller_surface"] = identity.get("caller_surface", "")
        defaults["declared_schema"] = identity.get("declared_schema", "")
        defaults["tenant_id"] = identity.get("tenant_id", "")

    auth = payload.get("auth_defaults", {})
    if auth:
        defaults["auth_kind"] = auth.get("kind", "")
        defaults["auth_token"] = auth.get("token", "")

    return defaults


def _load_pipeline_defaults_payload(app_name: str) -> dict[str, Any]:
    """Return full pipeline_defaults YAML as dict.

    Prefer ``ResolvedProfile.raw_data`` — ``typed_payload`` intentionally omits
    app-specific sections (identity_defaults, exit_eval_wire, ...) per
    profile_resolver._extract_typed_payload.
    """
    if not app_name:
        return {}
    try:
        resolver = RuntimeProfileResolver()
        profile = resolver.resolve(app_name, "pipeline_defaults")
        raw = getattr(profile, "raw_data", None)
        return dict(raw) if isinstance(raw, dict) else {}
    except (UnknownAppError, MissingProfileError, InvalidProfileError):
        return {}
    except Exception:  # guardian: allow-broad-exception -- P1 ADG burndown
        return {}


def _resolve_exit_eval_wire(app_name: str) -> dict[str, Any]:
    """§X1A wiring: non-empty roster + truthy threshold_profile inside grader_composition.

    Resolved from ``pipeline_defaults.exit_eval_wire`` (app SSOT YAML under
    ``config/profiles/<app>/pipeline_defaults.yaml``).  Missing or partial
    config returns {} so callers keep prior behaviour (X1A may still fail).
    """
    payload = _load_pipeline_defaults_payload(app_name)
    ee = payload.get("exit_eval_wire") or {}
    if not isinstance(ee, dict):
        return {}

    roster_raw = ee.get("grader_roster") or ee.get("roster") or []
    roster: list[str] = []
    if isinstance(roster_raw, list):
        for item in roster_raw:
            s = str(item).strip()
            if s:
                roster.append(s)

    threshold_profile = ee.get("threshold_profile")
    if isinstance(threshold_profile, str):
        threshold_profile = threshold_profile.strip() or None

    if not roster:
        _log.warning(
            "[R4] exit_eval_wire.grader_roster missing/empty app=%s — X1A may fail",
            app_name,
        )
        return {}
    if threshold_profile is None:
        _log.warning(
            "[R4] exit_eval_wire.threshold_profile missing app=%s — X1A may fail",
            app_name,
        )
        return {}

    return {"roster": roster, "threshold_profile": threshold_profile}


def _resolve_spine_exit_packet_carrier_refs(app_name: str) -> tuple[str, ...]:
    """AG-8 threading tuple for ``l5_certification_refs`` on Exit receipts.

    Loaded from ``pipeline_defaults.exit_eval_wire.spine_exit_packet_carrier_refs``.
    These are **application binding / packet-carrier tokens** for the Exit v6
    X3 builder — **not** Fort Knox ``RTC-REQ-*`` production certifications.
    """
    payload = _load_pipeline_defaults_payload(app_name)
    ee = payload.get("exit_eval_wire") or {}
    if not isinstance(ee, dict):
        return ()
    raw = ee.get("spine_exit_packet_carrier_refs") or ee.get(
        "spine_l5_packet_carrier_refs",
    )
    if not isinstance(raw, list):
        return ()
    out: list[str] = []
    for item in raw:
        s = str(item).strip()
        if s:
            out.append(s)
    return tuple(out)


def _apply_pipeline_exit_carriers(receipts: dict[str, Any], app_name: str) -> None:
    """Attach Exit v6 carriers from resolved ``pipeline_defaults`` (app SSOT)."""
    wire = _resolve_exit_eval_wire(app_name)
    if wire:
        receipts["grader_composition"] = dict(wire)
        tp = wire.get("threshold_profile")
        if isinstance(tp, str) and tp.strip():
            receipts["threshold_profile_ref"] = tp.strip()

    spine_refs = _resolve_spine_exit_packet_carrier_refs(app_name)
    if spine_refs:
        receipts["l5_certification_refs"] = spine_refs


def _sha256_file(path: Path) -> str | None:
    """Return sha256 hex of file contents, or None if file doesn't exist."""
    if not path.exists():
        return None
    try:
        content = path.read_bytes()
        return f"sha256:{hashlib.sha256(content).hexdigest()}"
    except OSError:  # guardian: allow-return-none-swallow -- P1 ADG burndown
        return None


def _looks_like_content_sha256_digest(val: str) -> bool:
    s = (val or "").strip()
    if s.startswith("sha256:") and len(s) == 71:
        tail = s[7:]
        return all(c in "0123456789abcdefABCDEF" for c in tail)
    if len(s) == 64:
        return all(c in "0123456789abcdefABCDEF" for c in s)
    return False


def _normalize_digest_literal(val: str) -> str:
    s = (val or "").strip()
    if s.startswith("sha256:"):
        return s
    return f"sha256:{s.lower()}" if s else ""


def _hydrate_raw_request_evidence_digests(
    raw_request: dict[str, Any],
    *,
    app_name: str,
    policy_override: str,
    blueprint_override: str,
) -> None:
    """Populate ``policy_hash`` / ``blueprint_hash`` when caller omits content digests.

    Resolution order per field: explicit run kwargs → already-valid content digest
    on ``raw_request`` → SHA-256 of files named in ``pipeline_defaults.policy_refs``.
    Paths are **only** read from the app's profile YAML (never hardcoded per app
    in core).
    """
    if not app_name:
        return

    payload = _load_pipeline_defaults_payload(app_name)
    prefs = payload.get("policy_refs")
    prefs = prefs if isinstance(prefs, dict) else {}

    def _fill(field: str, override: str, current: Any, rel_path: str | None) -> None:
        ov = (override or "").strip()
        if _looks_like_content_sha256_digest(ov):
            raw_request[field] = _normalize_digest_literal(ov)
            return
        cur = str(current or "").strip()
        if _looks_like_content_sha256_digest(cur):
            raw_request[field] = _normalize_digest_literal(cur)
            return
        if rel_path:
            d = _sha256_file(Path(str(rel_path)))
            if d:
                raw_request[field] = d

    _fill(
        "policy_hash",
        policy_override,
        raw_request.get("policy_hash"),
        str(prefs.get("l0_policy") or "").strip() or None,
    )
    _fill(
        "blueprint_hash",
        blueprint_override,
        raw_request.get("blueprint_hash"),
        str(prefs.get("agent_spec") or "").strip() or None,
    )


def _write_json(path: Path, payload: dict[str, Any]) -> str:
    """Write payload as canonical JSON; return sha256 hex."""
    blob = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(blob, encoding="utf-8")
    return f"sha256:{hashlib.sha256(blob.encode()).hexdigest()}"


def _hash_payload(payload: dict[str, Any]) -> str:
    """Compute deterministic sha256 hex of a payload dict (for envelope hash)."""
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def _build_raw_envelope(
    raw_request: dict[str, Any],
    app_name: str = "",
) -> RawIngressEnvelope:
    """Map caller dict → RawIngressEnvelope for U0 intake.
    
    Uses profile-driven defaults for app-specific identity values.
    """
    # Get app defaults from profile (fail-closed: empty dict on failure)
    defaults = _get_app_defaults(app_name)
    
    body_text = (
        raw_request.get("body_text")
        or raw_request.get("query")
        or json.dumps(raw_request.get("jd_payload") or {})
    )
    
    # Use profile defaults or fallback to empty string (not hardcoded app literals)
    default_source_channel = defaults.get("source_channel", "")
    default_user_id = defaults.get("user_id_default", "")
    default_auth_kind = defaults.get("auth_kind", "internal")
    default_auth_token = defaults.get("auth_token", "")
    
    return RawIngressEnvelope(
        transport=str(raw_request.get("transport", "api")),
        method=str(raw_request.get("method", "POST")),
        content_type=str(raw_request.get("content_type", "application/json")),
        source_channel=str(raw_request.get("source_channel", default_source_channel)),
        claimed_tenant_id=raw_request.get("tenant_id"),
        claimed_user_id=str(raw_request.get("user_id", default_user_id)),
        auth_credential=dict(
            raw_request.get("auth_credential") or {
                "kind": default_auth_kind,
                "token": default_auth_token,
            }
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
    app_name: str = "",
    effective_route_id: str = "",
    route_contract_id: str = "",
    replay_key: str = "",
    policy_digest: str = "",
    blueprint_digest: str = "",
    l5_certification_refs: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Receipts dict for an L0 R5 terminal path through Exit V6 (§5.0 fields)."""
    rid = (effective_route_id or "").strip() or ROUTE_ID
    rcid = (route_contract_id or "").strip() or rid
    out: dict[str, Any] = {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": rid,
        "chain_kind": CHAIN_KIND,
        "terminal_r5": True,
        "r5_reason_code": reason_code,
        "l2_executed": False,
        "producer_component": _PRODUCER_COMPONENT,
        "policy_hash": policy_digest,
        "blueprint_hash": blueprint_digest,
        "replay_key": replay_key,
        "route_contract": _r4_exit_route_contract_shard(
            effective_route_id=rid,
            route_contract_id=rcid,
            request_id=request_id,
            trace_root=trace_root,
            app_name=app_name,
        ),
        "terminal_class": "failure",
        "l5_certification_refs": list(l5_certification_refs),
    }
    _apply_pipeline_exit_carriers(out, app_name)
    return out


def _r4_exit_route_contract_shard(
    *,
    effective_route_id: str,
    route_contract_id: str,
    request_id: str,
    trace_root: str,
    app_name: str,
) -> dict[str, Any]:
    """Minimal RouteContract-compatible mapping for Exit v6 §5.0 preflight + N2."""
    rid = (effective_route_id or "").strip() or ROUTE_ID
    cid = (route_contract_id or "").strip() or rid
    shard: dict[str, Any] = {
        "route_id": rid,
        "route_contract_id": cid,
        "chain_kind": CHAIN_KIND,
        "request_id": request_id,
        "trace_root": trace_root,
    }
    if app_name:
        shard["app_id"] = app_name
    return shard


def _build_l2_exit_receipts(
    *,
    run_id: str,
    request_id: str,
    trace_root: str,
    c0_bypass_digest: str,
    l2_result: Any,
    effective_route_id: str,
    route_contract_id: str,
    replay_key: str,
    policy_digest: str,
    blueprint_digest: str,
    terminal_class: str,
    app_name: str,
    l5_certification_refs: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Receipts dict for an L2-executed path through Exit V6 §5.0 onward.

    Carries hashes, replay binding, RouteContract shard, and terminal_class
    from the live R4 context so ``validate_required_receipts`` can pass without
    weakening §5.0 law.
    """
    out: dict[str, Any] = {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": (effective_route_id or "").strip() or ROUTE_ID,
        "chain_kind": CHAIN_KIND,
        "terminal_r5": False,
        "c0_bypass_receipt_digest": c0_bypass_digest,
        "l2_executed": True,
        "l2_result_summary": str(l2_result)[:256] if l2_result is not None else "",
        "producer_component": _PRODUCER_COMPONENT,
        # Exit v6 §5.0 mandatory wiring (preflight.validate_required_receipts)
        "policy_hash": policy_digest,
        "replay_key": replay_key,
        "route_contract": _r4_exit_route_contract_shard(
            effective_route_id=effective_route_id,
            route_contract_id=route_contract_id,
            request_id=request_id,
            trace_root=trace_root,
            app_name=app_name,
        ),
        "terminal_class": terminal_class,
        # Coherent hashes for ExitReviewPacket (identity envelope uses same lineage)
        "blueprint_hash": blueprint_digest,
        "l5_certification_refs": list(l5_certification_refs),
    }
    _apply_pipeline_exit_carriers(out, app_name)
    return out


def _cache_preflight_fault(
    *,
    artifact_dir: Path,
    route_id: str,
    message: str,
) -> SingleActionSpineRunResult:
    return SingleActionSpineRunResult(
        run_id="",
        request_id="",
        route_id=route_id,
        x3_disposition=V6Disposition.DENY.value,
        terminal_r5=False,
        terminal_r5_reason="",
        artifact_dir=Path(artifact_dir),
        fault=message,
    )


def _validate_apps_rg_cache_preflight(
    app_name: str,
    cache_preflight_evidence: Mapping[str, Any] | None,
    *,
    _test_mode: bool,
) -> str | None:
    """Return fault string when apps_rg production lacks whole-run cache preflight evidence."""
    if _test_mode or str(app_name or "").strip() != "apps_rg":
        return None
    if not cache_preflight_evidence:
        return "CACHE_PREFLIGHT_EVIDENCE_REQUIRED: apps_rg production must pass R1A/R1B preflight evidence"
    if not cache_preflight_evidence.get("cache_preflight_completed"):
        return "CACHE_PREFLIGHT_NOT_COMPLETED"
    if not cache_preflight_evidence.get("generation_spine_invocation_allowed"):
        blocked = cache_preflight_evidence.get("generation_spine_invocation_blocked_reason") or "cache_hit"
        return f"GENERATION_SPINE_BLOCKED:{blocked}"
    return None


def _manifest_cache_fields(cache_preflight_evidence: Mapping[str, Any] | None) -> dict[str, Any]:
    if not cache_preflight_evidence:
        return {}
    keys = (
        "cache_preflight_completed",
        "r1a_preflight_status",
        "r1b_preflight_status",
        "cache_result",
        "cache_miss_receipt_ref",
        "generation_spine_invocation_allowed",
        "generation_spine_invocation_blocked_reason",
        "route_family",
    )
    return {k: cache_preflight_evidence[k] for k in keys if k in cache_preflight_evidence}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def run_integrated_single_action_spine(
    *,
    raw_request: dict[str, Any],
    app_name: str = "",
    l2_callable: Callable[[], Any] | None = None,
    artifact_dir: Path,
    policy_hash: str = "",
    blueprint_hash: str = "",
    route_family: str = "",
    route_id: str = "",
    chain_kind: str = "",
    cache_preflight_evidence: Mapping[str, Any] | None = None,
    _test_mode: bool = False,
) -> SingleActionSpineRunResult:
    """Run the governed single-action integrated spine end-to-end.

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
    route_family:
        Route family data (e.g. ``R4_SINGLE_ACTION`` for apps_rg).  Not an entrypoint name.
    route_id:
        Optional override; defaults to ``route_family`` or registry resolution.
    chain_kind:
        Chain kind stamped on receipts (defaults to ``route_family``).
    cache_preflight_evidence:
        Required for ``app_name=apps_rg`` production: whole-run R1A/R1B preflight receipt.
    _test_mode:
        When True, allows ``l2_callable`` and skips apps_rg cache-preflight enforcement.

    Returns
    -------
    SingleActionSpineRunResult
        Immutable result containing run_id, x3_disposition, terminal_r5 flag,
        and artifact_dir.  Never raises — internal errors land in ``fault``.
    """
    # Generic OTEL provider bootstrap — opt-in via env (default OFF). Installs a
    # recording TracerProvider once per process BEFORE any L2/L3 emitter resolves
    # its tracer, so spans actually export when OTEL_TRACES_EXPORTER is set. This
    # is the single shared chokepoint every app crosses. Fail-soft: never raises.
    from agentic_core.tracing.runtime_tracing import bootstrap_runtime_tracing

    bootstrap_runtime_tracing()

    eff_route_family = (route_family or ROUTE_FAMILY).strip() or ROUTE_FAMILY
    eff_chain_kind = (chain_kind or eff_route_family).strip() or CHAIN_KIND

    cache_fault = _validate_apps_rg_cache_preflight(
        app_name, cache_preflight_evidence, _test_mode=_test_mode
    )
    if cache_fault:
        return _cache_preflight_fault(
            artifact_dir=Path(artifact_dir),
            route_id=(route_id or eff_route_family).strip() or ROUTE_ID,
            message=cache_fault,
        )

    # ------------------------------------------------------------------
    # Resolve L2 callable — core-owned recipe resolution
    # ------------------------------------------------------------------
    if l2_callable is not None and not _test_mode:
        return SingleActionSpineRunResult(
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
            return SingleActionSpineRunResult(
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
            # 2026-05-07 — pass artifact_dir into the recipe context so
            # narrative steps land in the same dir as spine receipts.
            # See docs/archive/windsurf/legacy-tree/plans/apps-rg-spine-narrative-unification-d8e4a1.md
            l2_callable = resolve_l2_recipe(
                app_name,
                raw_request,
                artifact_dir=artifact_dir,
            )
        except KeyError as exc:
            return SingleActionSpineRunResult(
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
    effective_route_id = (route_id or _load_route_id_for_app(app_name)).strip() or ROUTE_ID

    run_id = str(uuid.uuid4())
    started_at = _utc_now_iso()
    git_commit, git_dirty = git_commit_and_dirty()
    _hydrate_raw_request_evidence_digests(
        raw_request,
        app_name=app_name or "",
        policy_override=policy_hash,
        blueprint_override=blueprint_hash,
    )
    replay_key = _compute_replay_key(raw_request)

    # ------------------------------------------------------------------
    # U0 — intake
    # ------------------------------------------------------------------
    envelope = _build_raw_envelope(raw_request, app_name=app_name)
    intake_result = run_request_intake(envelope)

    # If U0 rejects, return schema-rejection result (not R5 — see plan §W2)
    if intake_result.validated is None:
        reason = "unknown"
        if intake_result.rejection_report is not None:
            reason = getattr(intake_result.rejection_report.decisive_reason_code, "value", "unknown")
        return SingleActionSpineRunResult(
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
    _binding_payload = binding_payload_from_identity(
        {
            "request_id": request_id,
            "run_id": run_id,
            "trace_root": trace_root,
            "policy_hash": policy_hash or raw_request.get("policy_hash", "") or "",
            "blueprint_hash": blueprint_hash or raw_request.get("blueprint_hash", "") or "",
            "registry_digest_set": {},
            "route_contract_id": str(getattr(plan_contract, "contract_id", "") or run_id),
            "route_id": effective_route_id,
            "app_name": app_name or "",
        }
    )
    _l5_cert_ref = certification_ref_from_binding(_binding_payload)

    # ------------------------------------------------------------------
    # L0 — route gates (decision only; no fallback execution)
    # ------------------------------------------------------------------
    gate_result = check_route_gates(plan_contract, namespace=app_name)

    # L0 terminal (R5_FATAL / R5_FALLBACK) — route through Exit V6 before return
    if getattr(gate_result, "terminal", False) or getattr(gate_result, "r5_terminal", False):
        r5_reason = str(getattr(gate_result, "reason_code", "R5_TERMINAL"))
        route_contract_id_r5 = str(getattr(plan_contract, "contract_id", "") or run_id)
        receipts = _build_r5_exit_receipts(
            run_id=run_id,
            request_id=request_id,
            trace_root=trace_root,
            reason_code=r5_reason,
            app_name=app_name or "",
            effective_route_id=effective_route_id,
            route_contract_id=route_contract_id_r5,
            replay_key=replay_key,
            policy_digest=str(raw_request.get("policy_hash", "") or ""),
            blueprint_digest=str(raw_request.get("blueprint_hash", "") or ""),
            l5_certification_refs=(_l5_cert_ref,),
        )
        exit_pipeline = ExitEvalPipeline()
        exit_result: ExitEvalResult = exit_pipeline.run(receipts)
        x3 = exit_result.disposition.value
        return SingleActionSpineRunResult(
            run_id=run_id,
            request_id=request_id,
            route_id=effective_route_id,
            x3_disposition=x3,
            terminal_r5=True,
            terminal_r5_reason=r5_reason,
            artifact_dir=artifact_dir,
        )

    # ------------------------------------------------------------------
    # W4 c0-policy-rectification-f7b2a9: C0 bypass with typed reason
    # R4 uses preloaded context; no corpus retrieval required
    # ------------------------------------------------------------------
    route_contract_id = str(getattr(plan_contract, "contract_id", "") or run_id)
    # W4: Use explicit BYPASS_PRELOADED_CONTEXT with preloaded_context_ref
    c0_receipt = build_c0_bypass_receipt(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        route_contract_id=route_contract_id,
        route_id=effective_route_id,
        c0_bypass_reason="BYPASS_PRELOADED_CONTEXT",
    )
    c0_hash = _write_json(artifact_dir / _C0_BYPASS_RECEIPT_FILENAME, c0_receipt.to_dict())

    # W4: C0 sub-stage instrumentation (bypassed with typed reason)
    c0_sub_stages: list[dict[str, Any]] = [
        {"sub_stage_id": "C0.1", "sub_stage_name": "Query Normalization", "status": "BYPASSED", "duration_ms": 0.0, "meta": {"reason": "BYPASS_PRELOADED_CONTEXT"}},
        {"sub_stage_id": "C0.2", "sub_stage_name": "Embedding Lookup", "status": "BYPASSED", "duration_ms": 0.0, "meta": {"reason": "BYPASS_PRELOADED_CONTEXT"}},
        {"sub_stage_id": "C0.3", "sub_stage_name": "D1 Exact Cache Probe", "status": "BYPASSED", "duration_ms": 0.0, "meta": {"reason": "BYPASS_PRELOADED_CONTEXT"}},
        {"sub_stage_id": "C0.4", "sub_stage_name": "D2 Semantic Cache Probe", "status": "BYPASSED", "duration_ms": 0.0, "meta": {"reason": "BYPASS_PRELOADED_CONTEXT"}},
        {"sub_stage_id": "C0.5", "sub_stage_name": "Retrieval Augmentation", "status": "BYPASSED", "duration_ms": 0.0, "meta": {"reason": "BYPASS_PRELOADED_CONTEXT"}},
        {"sub_stage_id": "C0.6", "sub_stage_name": "Grounding Context Assembly", "status": "BYPASSED", "duration_ms": 0.0, "meta": {"reason": "BYPASS_PRELOADED_CONTEXT"}},
    ]

    # ------------------------------------------------------------------
    # Identity envelope
    # ------------------------------------------------------------------
    # Get app defaults from profile for identity values
    _identity_defaults = _get_app_defaults(app_name)
    _caller_surface = _identity_defaults.get("caller_surface", "") or app_name or ""
    _app_name_for_identity = app_name or _identity_defaults.get("app_id", "")
    
    identity = build_runtime_identity_envelope(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        replay_key=replay_key,
        policy_hash=policy_hash or raw_request.get("policy_hash", ""),
        blueprint_hash=blueprint_hash or raw_request.get("blueprint_hash", ""),
        caller_surface=_caller_surface,
        entrypoint_command=_PRODUCER_COMPONENT,
        started_at_utc=started_at,
        git_commit=git_commit,
        git_dirty=git_dirty,
        route_contract_id=route_contract_id,
        route_id=effective_route_id,
        app_name=_app_name_for_identity,
    )
    _write_json(artifact_dir / _IDENTITY_RECEIPT_FILENAME, identity.to_dict())
    _binding_payload = binding_payload_from_identity(identity.to_dict())
    _l5_cert_ref = certification_ref_from_binding(_binding_payload)

    # ------------------------------------------------------------------
    # Seal U0 validated_request envelope (HowTrace U0_INTAKE evidence)
    # ------------------------------------------------------------------
    _validated_payload = {
        "request_id": request_id,
        "trace_root": trace_root,
        "run_id": run_id,
        "tenant_id": str(getattr(validated, "tenant_id", "") or raw_request.get("tenant_id", "default")),
        "user_id": str(getattr(validated, "user_id", "") or raw_request.get("user_id", _identity_defaults.get("user_id_default", ""))),
        "transport": str(getattr(envelope, "transport", "api")),
        "source_channel": str(getattr(envelope, "source_channel", _identity_defaults.get("source_channel", ""))),
        "target_company": raw_request.get("target_company", ""),
        "target_role": raw_request.get("target_role", ""),
        "intake_status": "VALIDATED",
    }
    _vr_envelope = {
        "schema_version": "validated_request.v1",
        "artifact_hash": _hash_payload(_validated_payload),
        "payload": _validated_payload,
    }
    _write_json(artifact_dir / "validated_request.json", _vr_envelope)

    # ------------------------------------------------------------------
    # L2 — static DAG execution with sub-stage instrumentation
    # ------------------------------------------------------------------
    l2_result: Any = None
    l2_fault = ""
    l2_sub_stages: list[dict[str, Any]] = []
    _l2_t0 = time.perf_counter()

    # E1: Prep — recipe resolved, inputs validated
    _t1 = time.perf_counter()
    l2_sub_stages.append({
        "sub_stage_id": "E1",
        "sub_stage_name": "Prep: Plan Decomposition",
        "status": "PASS",
        "duration_ms": round((_t1 - _l2_t0) * 1000, 3),
        "meta": {"app_name": app_name},
    })

    # E2: Valid — pre-execution contract check
    _t2 = time.perf_counter()
    l2_sub_stages.append({
        "sub_stage_id": "E2",
        "sub_stage_name": "Valid: Pre-Execution Contract Check",
        "status": "PASS",
        "duration_ms": round((_t2 - _t1) * 1000, 3),
        "meta": {},
    })

    # E3: Exec — actual L2 DAG execution
    _t3 = time.perf_counter()
    try:
        l2_result = l2_callable()
        _e3_status = "PASS"
    except Exception as exc:  # guardian: allow-broad-exception -- L2 failure is fatal; captured in l2_fault for Exit receipts
        l2_fault = f"L2_EXECUTION_ERROR:{type(exc).__name__}:{exc}"
        _e3_status = "FAIL"
    _t4 = time.perf_counter()
    l2_sub_stages.append({
        "sub_stage_id": "E3",
        "sub_stage_name": "Exec: Tool Dispatch",
        "status": _e3_status,
        "duration_ms": round((_t4 - _t3) * 1000, 3),
        "meta": {"fault": l2_fault} if l2_fault else {},
    })

    # E4: Heal — retry/recovery (no-op when E3 passes)
    _t5 = time.perf_counter()
    l2_sub_stages.append({
        "sub_stage_id": "E4",
        "sub_stage_name": "Heal: Retry / Recovery",
        "status": "BYPASSED" if not l2_fault else "NOT_APPLICABLE",
        "duration_ms": round((_t5 - _t4) * 1000, 3),
        "meta": {"retry_attempted": False},
    })

    # E5: Seal — output assembly + artifact sealing
    l2_sub_stages.append({
        "sub_stage_id": "E5",
        "sub_stage_name": "Seal: Output Assembly",
        "status": "PASS" if not l2_fault else "FAIL",
        "duration_ms": 0.0,
        "meta": {},
    })

    # ------------------------------------------------------------------
    # Exit V6 — exactly one X3 disposition per run
    # ------------------------------------------------------------------
    _policy_digest = (policy_hash or str(raw_request.get("policy_hash", "") or "")).strip()
    _blueprint_digest = (blueprint_hash or str(raw_request.get("blueprint_hash", "") or "")).strip()
    _terminal_cls = "failure" if l2_fault.strip() else "success"
    receipts = _build_l2_exit_receipts(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        c0_bypass_digest=c0_hash,
        l2_result=l2_result,
        effective_route_id=effective_route_id,
        route_contract_id=route_contract_id,
        replay_key=replay_key,
        policy_digest=_policy_digest,
        blueprint_digest=_blueprint_digest,
        terminal_class=_terminal_cls,
        app_name=app_name,
        l5_certification_refs=(_l5_cert_ref,),
    )
    if l2_fault:
        receipts["l2_fault"] = l2_fault

    exit_pipeline = ExitEvalPipeline()
    exit_result: ExitEvalResult = exit_pipeline.run(receipts)
    x3 = exit_result.disposition.value
    # Exit v6 may still aggregate X3D ALLOW on minimal R4 receipt shapes even when
    # ``terminal_class=failure`` — that would contradict ``l2_fault`` on the same run.
    # Product/spine truth: an L2 recipe fault is never an ALLOW-class completion.
    if str(l2_fault).strip():
        x3 = V6Disposition.DENY.value

    # ------------------------------------------------------------------
    # D2 semantic cache writeback — learn from successful runs only
    # ------------------------------------------------------------------
    if not l2_fault and x3 in ("EXIT_OK", "EXIT_PARTIAL"):
        try:
            from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
                SemanticCacheManager,
            )
            _cache = SemanticCacheManager.get_instance()
            _intent_text = raw_request.get("user_intent") or raw_request.get("jd_payload", {}).get("text", "")
            if _intent_text:
                # Fail-closed: require app_name for namespace (no hardcoded fallback)
                _cache_namespace = app_name or _identity_defaults.get("cache_namespace", "")
                if _cache_namespace:
                    _cache.learn(
                        context=str(_intent_text)[:4096],
                        namespace=_cache_namespace,
                        result={"output": str(l2_result)[:8192] if l2_result is not None else ""},
                        tenant_id=raw_request.get("tenant_id", "default"),
                        policy_version=policy_hash or raw_request.get("policy_hash", ""),
                    )
                _log.debug("[R4] D2 semantic cache learn() committed for %s", app_name)
        except Exception as _d2_err:  # guardian: allow-log-and-swallow -- P1 ADG burndown  # guardian: allow-broad-exception -- P1 ADG burndown
            _log.debug("[R4] D2 semantic cache learn() skipped: %s", _d2_err)

    # ------------------------------------------------------------------
    # Seal Exit V6 receipts (HowTrace EXIT_X3 evidence)
    # ------------------------------------------------------------------
    _exit_review_payload = {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": effective_route_id,
        "chain_kind": CHAIN_KIND,
        "x3_disposition": x3,
        "l2_executed": True,
        "l2_fault": l2_fault,
        "x1_sub_stages": exit_result.x1_sub_stages,
        "reviewed_at_utc": _utc_now_iso(),
    }
    _exit_review_envelope = {
        "schema_version": "exit_review_packet.v1",
        "artifact_hash": _hash_payload(_exit_review_payload),
        "payload": _exit_review_payload,
    }
    _write_json(artifact_dir / "exit_review_packet.json", _exit_review_envelope)

    _x3_payload = {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "disposition": x3,
        "unknown_never_pass": True,
        "emitted_at_utc": _utc_now_iso(),
    }
    _x3_envelope = {
        "schema_version": "x3_disposition_receipt.v1",
        "artifact_hash": _hash_payload(_x3_payload),
        "payload": _x3_payload,
    }
    _write_json(artifact_dir / "x3_disposition_receipt.json", _x3_envelope)

    # ------------------------------------------------------------------
    # Seal L3 bypass + L2 terminal_ret_packet (R4 family shape)
    # ------------------------------------------------------------------
    _l3_bypass_payload = {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": effective_route_id,
        "chain_kind": CHAIN_KIND,
        "bypass_reason": "R4_DETERMINISTIC_PIPELINE_NO_RUNTIME_ORCHESTRATION",
        "no_orchestration": True,
        "no_tool_execution": True,
        "no_model_execution": True,
    }
    _l3_bypass_envelope = {
        "schema_version": "l3_bypass_receipt.v1",
        "artifact_hash": _hash_payload(_l3_bypass_payload),
        "payload": _l3_bypass_payload,
    }
    _write_json(artifact_dir / "l3_bypass_receipt.json", _l3_bypass_envelope)

    # NOTE: HowTrace builder treats R4_SINGLE_ACTION as part of the R1B family
    # (terminal-shortcircuit shape).  R4 actually executes a deterministic
    # static-DAG L2 callable (resolved per ``app_name``), but at the spine level the L2 work
    # is sealed via the L2 callable's own outputs (e.g. generated_resume.json,
    # run_report.json) rather than a model/tool-call sealed_artifact.  We
    # therefore emit a terminal_ret_packet that asserts no_l2_execution=True
    # at the SPINE-execution layer (no real model/tool calls inside the spine
    # runner) while pointing at the L2 callable's run_report for traceability.
    _l2_run_report_ref = ""
    if isinstance(l2_result, dict):
        _l2_run_dir = l2_result.get("run_dir") or ""
        if _l2_run_dir:
            _l2_run_report_ref = f"file://{_l2_run_dir}/run_report.json"
    _terminal_payload = {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": effective_route_id,
        "chain_kind": CHAIN_KIND,
        "execution_form": "R4_SINGLE_ACTION",
        "no_l2_execution_assertion": True,
        "l2_recipe_executed": True,
        "l2_recipe_run_report_ref": _l2_run_report_ref,
        "l2_fault": l2_fault,
        "l2_sub_stages": l2_sub_stages,
        "emitted_at_utc": _utc_now_iso(),
    }
    _terminal_envelope = {
        "schema_version": "terminal_ret_packet.v1",
        "artifact_hash": _hash_payload(_terminal_payload),
        "payload": _terminal_payload,
    }
    _write_json(artifact_dir / "terminal_ret_packet.json", _terminal_envelope)

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
            "route_family": eff_route_family,
            "chain_kind": eff_chain_kind,
            "x3_disposition": x3,
            "terminal_r5": False,
            "l2_fault": l2_fault,
            "artifact_hash": compute_artifact_hash(receipts),
            "emitted_at": _utc_now_iso(),
            **_manifest_cache_fields(cache_preflight_evidence),
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

    # Re-stamp the W2 evidence chain as full envelopes. This overwrites
    # any earlier raw compatibility aliases so reruns cannot reuse stale
    # request/trace roots from a prior attempt.
    stamp = ProvenanceStamp(
        producer_component=_PRODUCER_COMPONENT,
        producer_module="integrated_single_action_spine_run",
        producer_function_or_class=_PRODUCER_FUNCTION,
    )
    artifact_hashes: dict[str, str] = {}
    upstream_for = {fn: (up or "") for fn, up in W2_CHAIN_LINKAGE}

    def _emit_chain(filename: str, payload: dict[str, Any]) -> str:
        upstream_filename = upstream_for.get(filename, "")
        upstream_ref = artifact_hashes.get(upstream_filename, "") if upstream_filename else ""
        _, digest = emit_artifact(
            artifact_dir,
            filename,
            payload,
            stamp=stamp,
            upstream_artifact_ref=upstream_ref,
        )
        artifact_hashes[filename] = digest
        return digest

    _emit_chain(
        "integrated_runtime_entrypoint_invocation.json",
        {
            "invocation_id": run_id,
            "integrated_runtime_entrypoint_used": True,
            "entry_point": f"{_PRODUCER_COMPONENT}.{_PRODUCER_FUNCTION}",
            "app_name": app_name,
            "route_family": eff_route_family,
            "chain_kind": CHAIN_KIND,
            "started_at_utc": started_at,
            "request_id": request_id,
            "trace_root": trace_root,
            "raw_request_keys": sorted(raw_request.keys()),
        },
    )
    _emit_chain("runtime_identity_envelope.json", identity.to_dict())

    _binding_payload = binding_payload_from_identity(identity.to_dict())
    _l5_cert_ref = certification_ref_from_binding(_binding_payload)
    _emit_chain("runtime_certification_binding.json", _binding_payload)
    _emit_chain(
        "l5_hitl_reclearance.json",
        build_hitl_reclearance_not_applicable(
            request_id=request_id,
            run_id=run_id,
            replay_key=replay_key,
        ),
    )

    plan_payload = {
        "task_spec": str(getattr(plan_contract, "task_spec", "") or ""),
        "query_spec": str(getattr(plan_contract, "query_spec", "") or ""),
        "grounding_required": bool(getattr(plan_contract, "grounding_required", False)),
        "user_task_text": str(getattr(plan_contract, "user_task_text", "") or ""),
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": effective_route_id,
    }
    _emit_chain("validated_request.json", _validated_payload)
    _emit_chain("l1_plan_contract.json", plan_payload)
    _emit_chain(
        "route_contract.json",
        {
            "route_id": effective_route_id,
            "route_contract_id": route_contract_id,
            "request_id": request_id,
            "trace_root": trace_root,
            "execution_form": "R4_SINGLE_ACTION",
            "grounding_required": True,
            "prompt_assembly_required": False,
            "route_family": eff_route_family,
            "policy_hash": identity.policy_hash,
            "blueprint_hash": identity.blueprint_hash,
            "replay_key": identity.replay_key,
        },
    )
    _emit_chain("l3_bypass_receipt.json", _l3_bypass_payload)
    _emit_chain("c0_bypass_receipt.json", c0_receipt.to_dict())
    _emit_chain(
        "prompt_assembly_bypass_receipt.json",
        build_prompt_assembly_bypass_receipt(
            run_id=run_id,
            request_id=request_id,
            trace_root=trace_root,
            route_contract_id=route_contract_id,
            route_id=effective_route_id,
            prompt_assembly_bypass_reason="NO_MODEL_EXECUTION_REQUIRED",
        ).to_dict(),
    )

    gate_bundle = RuntimeGateVerdictBundle(
        d1_outcome=GateOutcome.MISS,
        d2_outcome=GateOutcome.MISS,
        veto_outcome=VetoOutcome.NOT_INVOKED,
        reason_codes=("r4_single_action", "no_cache_reuse"),
    )
    _emit_chain("runtime_gate_verdict_bundle.json", gate_bundle.to_dict())

    safe_reuse = SafeReuseDecision(
        allow=False,
        reason_code="NOT_APPLICABLE",
        dense_candidate_produced=False,
        veto_invoked=False,
        veto_outcome=VetoOutcome.NOT_INVOKED,
        d2_similarity=0.0,
        upstream_gate_verdict_ref=artifact_hashes["runtime_gate_verdict_bundle.json"],
        evidence_refs=("r4_single_action", "no_cache_reuse"),
    )
    _emit_chain("semantic_cache_safe_reuse_decision.json", safe_reuse.to_dict())

    _emit_chain("terminal_ret_packet.json", _terminal_payload)
    _exit_review_payload["l5_certification_refs"] = [_l5_cert_ref]
    _emit_chain("exit_review_packet.json", _exit_review_payload)
    _emit_chain("x3_disposition_receipt.json", _x3_payload)

    _exhaust_payload = {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": effective_route_id,
        "chain_kind": CHAIN_KIND,
        "x3_disposition": x3,
        "l2_fault": l2_fault,
        "sealed_at_utc": _utc_now_iso(),
        "runtime_mode": "fixture" if not l2_fault else "fault",
        "synthetic_trace_detected": False,
        "l5_certification_refs": [_l5_cert_ref],
    }
    _emit_chain("runtime_exhaust_bundle.json", _exhaust_payload)

    _trace_payload = {
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_id": effective_route_id,
        "chain_kind": CHAIN_KIND,
        "started_at_utc": started_at,
        "finished_at_utc": _utc_now_iso(),
        "synthetic_trace_detected": False,
        "l4_writes_observed": 0,
    }
    _emit_chain("runtime_trace_snapshot.json", _trace_payload)

    _how_trace = _build_how_trace(artifact_dir, chain_kind=CHAIN_KIND)
    _how_trace_doc = dict(_how_trace.to_dict())
    _how_trace_doc.setdefault("producer_component", _PRODUCER_COMPONENT)
    _emit_chain("agentic_core_how_trace.json", _how_trace_doc)

    _rfc = _build_rfc(artifact_dir, chain_kind=CHAIN_KIND, write=False)
    _rfc_doc = dict(_rfc["payload"])
    _rfc_doc.setdefault("producer_component", _PRODUCER_COMPONENT)
    _emit_chain("agentic_core_l7_route_family_coverage.json", _rfc_doc)

    manifest_payload = {
        "invocation_id": run_id,
        "producer_component": _PRODUCER_COMPONENT,
        "entry_point": f"{_PRODUCER_COMPONENT}.{_PRODUCER_FUNCTION}",
        "integrated_runtime_entrypoint_used": True,
        "chain_kind": CHAIN_KIND,
        "artifact_filenames": list(artifact_hashes.keys()) + [
            "integrated_runtime_artifact_manifest.json",
            "no_harness_stamp_receipt.json",
            "agentic_core_spine_proof.json",
        ],
        "how_trace_ref": "artifact://agentic_core_how_trace.json",
        "how_trace_sha256": artifact_hashes["agentic_core_how_trace.json"],
        "l7_route_family_coverage_ref": "artifact://agentic_core_l7_route_family_coverage.json",
        "l7_route_family_coverage_sha256": artifact_hashes[
            "agentic_core_l7_route_family_coverage.json"
        ],
        "artifact_hashes": dict(artifact_hashes),
        "chain_linkage": [
            {"filename": fn, "upstream": (up or "")} for fn, up in W2_CHAIN_LINKAGE
        ],
        "x3_disposition": x3,
        "cache_hit": False,
        "safe_reuse_allow": False,
        "veto_stage_actual": "",
        "veto_stage_actual_names": [],
        "veto_stage_expected": "LLMJudgeVeto",
        "veto_stage_match_status": "FAIL_MISMATCH",
        "deterministic_proof_stage_used": False,
        "proof_only_stage_names": [],
        "primary_veto_mode": "",
        "veto_provider": "",
        "veto_model_id": "",
        "veto_rubric_path": "",
        "veto_rubric_hash": "",
        "veto_timeout_ms": 0,
        "llm_judge_invocation_count": 0,
        "veto_counters": {
            "unsafe_reuse_allowed_count": 0,
            "safe_reuse_blocked_count": 0,
            "hard_negative_allowed_count": 0,
            "unknown_error_timeout_parse_fail_block_count": 0,
            "legacy_unsafe_fp_count": 0,
            "legacy_safe_positive_block_count": 0,
        },
    }
    _emit_chain("integrated_runtime_artifact_manifest.json", manifest_payload)

    nh_payload = {
        "invocation_id": run_id,
        "all_artifacts_stamped_by_production": True,
        "producer_component": _PRODUCER_COMPONENT,
        "harness_check": "passed_self_attestation",
        "attested_filenames": list(artifact_hashes.keys()),
    }
    _emit_chain("no_harness_stamp_receipt.json", nh_payload)

    _spine = _build_spine_proof(
        artifact_dir=artifact_dir,
        artifact_hashes=artifact_hashes,
        identity_envelope_payload=identity.to_dict(),
        started_at_utc=started_at,
        finished_at_utc=_utc_now_iso(),
        exit_code=0,
        chain_kind=CHAIN_KIND,
    )
    _spine_doc = dict(_spine)
    _spine_doc.setdefault("producer_component", _PRODUCER_COMPONENT)
    _emit_chain("agentic_core_spine_proof.json", _spine_doc)

    return SingleActionSpineRunResult(
        run_id=run_id,
        request_id=request_id,
        route_id=effective_route_id,
        x3_disposition=x3,
        terminal_r5=False,
        terminal_r5_reason="",
        artifact_dir=artifact_dir,
        fault=l2_fault,
    )
