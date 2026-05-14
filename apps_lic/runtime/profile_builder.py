"""apps_lic profile builder — Bundle C canonical form.

Builds AppRuntimeProfile for apps_lic with all stage binding refs.
AppIngressRunner(profile=profile).run(payload) sequences those refs directly;
no app-owned dispatch callable.

All stages default to None — AppIngressRunner uses core defaults.
No app-specific logic may be added to agentic_core in exchange for this file.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping
from uuid import uuid4

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    RequestEnvelope,
)
from agentic_core.runtime.entry.app_ingress_runner import AppRuntimeProfile
from agentic_core.L1_cognition.apps_lic_l1_binding import l1_plan_apps_lic
from agentic_core.L0_routing.apps_lic_l0_binding import l0_route_apps_lic
from agentic_core.runtime.c0.apps_lic_c0_binding import c0_retrieve_apps_lic
from agentic_core.prompt_governance.apps_lic_pa_binding import pa_compose_apps_lic
from agentic_core.L2_execution.apps_lic_l2_binding import l2_execute_apps_lic
from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
from apps_lic.runtime.u0.shim import u0_lic_shim as u0_validate_apps_lic

APPS_LIC_REQUIRED_FIELDS: tuple[str, ...] = (
    "recipient_class",
    "channel",
    "outreach_mode",
)


def parse_payload(payload: Mapping[str, Any]) -> RequestEnvelope | None:
    """Convert a normalized payload dict into a typed RequestEnvelope for apps_lic.

    Signature matches AppRuntimeProfile.parse:
        (payload: Mapping[str, Any]) -> RequestEnvelope | None
    Returns None when payload cannot be parsed (surfaces ClarificationRequired).
    """
    if not isinstance(payload, dict):
        return None

    recipient_class = payload.get("recipient_class") or None
    channel = payload.get("channel") or None
    outreach_mode = payload.get("outreach_mode") or None

    if not (recipient_class or channel or outreach_mode):
        return None

    user_constraints: dict[str, Any] = dict(payload.get("user_constraints") or {})
    user_constraints["recipient_class"] = recipient_class
    user_constraints["channel"] = channel
    user_constraints["outreach_mode"] = outreach_mode
    if payload.get("manual_brief"):
        user_constraints["manual_brief"] = payload["manual_brief"]
    if payload.get("manifest_id"):
        user_constraints["manifest_id"] = payload["manifest_id"]
    if payload.get("manifest_hash"):
        user_constraints["manifest_hash"] = payload["manifest_hash"]

    try:
        ingress = AppsRgIngressPayload(
            app_id="apps_lic",
            task_class="outreach",
            target_company=payload.get("target_company") or None,
            target_role=payload.get("target_role") or recipient_class,
            target_level=payload.get("target_level") or None,
            manual_brief_path=payload.get("manual_brief") or None,
            user_constraints=user_constraints,
            output_preferences=payload.get("output_preferences") or {},
            idempotency_key=payload.get("request_id"),
        )
    except (TypeError, ValueError):
        return None

    return RequestEnvelope(
        payload=ingress,
        request_id=payload.get("request_id") or f"lic-req-{uuid4().hex[:12]}",
        run_id=payload.get("run_id") or f"lic-run-{uuid4().hex[:12]}",
        tenant_id=payload.get("tenant_id") or "apps_lic",
        trace_id=payload.get("trace_id") or f"lic-trace-{uuid4().hex[:16]}",
        submitted_at=datetime.now(timezone.utc).isoformat(),
    )


def build_app_runtime_contract() -> AppRuntimeProfile:
    """Construct and return the canonical AppRuntimeProfile for apps_lic.

    All stage bindings are wired with app-owned callables.
    U0 uses u0_lic_shim to bridge RequestEnvelope -> ValidatedRequest.
    AppIngressRunner sequences stages directly; no app-owned dispatch callable.

    Returns
    -------
    AppRuntimeProfile
        Ready to pass as AppIngressRunner(profile=profile).run(payload).
    """
    return AppRuntimeProfile(
        app_id="apps_lic",
        required_fields=APPS_LIC_REQUIRED_FIELDS,
        parse=parse_payload,
        u0=u0_validate_apps_lic,
        l1=l1_plan_apps_lic,
        l0=l0_route_apps_lic,
        c0=c0_retrieve_apps_lic,
        pa=pa_compose_apps_lic,
        l2=l2_execute_apps_lic,
        exit=exit_finalize_apps_lic,
        profile_version="1",
    )


__all__ = [
    "build_app_runtime_contract",
    "parse_payload",
    "APPS_LIC_REQUIRED_FIELDS",
]
