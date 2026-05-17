"""apps_research profile builder adapter — Bundle C canonical form.

Core binding imports live here (``*_adapter.py`` exempt from authority MV).
``profile_builder.py`` re-exports only.
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
from agentic_core.runtime.entry.u0_apps_research_binding import (
    u0_validate_apps_research,
)
from agentic_core.L0_routing.apps_research_l0_binding import l0_route_apps_research
from agentic_core.L1_cognition.apps_research_l1_binding import l1_plan_apps_research
from agentic_core.runtime.c0.apps_research_c0_binding import c0_retrieve_apps_research
from agentic_core.runtime.exit.apps_research_exit_binding import (
    exit_finalize_apps_research,
)
from agentic_core.prompt_governance.apps_research_pa_binding import (
    pa_assemble_apps_research,
)
from agentic_core.L2_execution.apps_research_l2_binding import (
    l2_execute_apps_research,
)

APPS_RESEARCH_REQUIRED_FIELDS: tuple[str, ...] = (
    "target_company",
)


def parse_payload(payload: Mapping[str, Any]) -> RequestEnvelope | None:
    """Convert a normalized payload dict into a typed RequestEnvelope for apps_research."""
    if not isinstance(payload, dict):
        return None

    target_company = payload.get("target_company") or None
    topic = (
        payload.get("topic")
        or (payload.get("user_constraints") or {}).get("topic")
        or None
    )

    if not target_company and not topic:
        return None

    user_constraints: dict[str, Any] = dict(payload.get("user_constraints") or {})
    if "topic" in payload:
        user_constraints["topic"] = payload["topic"]
    if "depth" in payload:
        user_constraints["depth"] = payload["depth"]

    try:
        ingress = AppsRgIngressPayload(
            app_id="apps_research",
            task_class="company_brief",
            target_company=target_company or topic,
            target_role=payload.get("target_role") or None,
            target_level=payload.get("target_level") or None,
            briefing_artifact_ref=payload.get("briefing_artifact_ref") or payload.get("manual_brief_path") or None,
            user_constraints=user_constraints,
            output_preferences=payload.get("output_preferences") or {},
            idempotency_key=payload.get("idempotency_key"),
        )
    except (TypeError, ValueError):
        return None

    return RequestEnvelope(
        payload=ingress,
        request_id=payload.get("request_id") or f"research-req-{uuid4().hex[:12]}",
        run_id=payload.get("run_id") or f"research-run-{uuid4().hex[:12]}",
        tenant_id=payload.get("tenant_id") or "apps_research",
        trace_id=payload.get("trace_id") or f"research-trace-{uuid4().hex[:16]}",
        submitted_at=datetime.now(timezone.utc).isoformat(),
    )


def build_app_runtime_contract() -> AppRuntimeProfile:
    """Construct and return the canonical AppRuntimeProfile for apps_research."""
    return AppRuntimeProfile(
        app_id="apps_research",
        required_fields=APPS_RESEARCH_REQUIRED_FIELDS,
        parse=parse_payload,
        u0=u0_validate_apps_research,
        l1=l1_plan_apps_research,
        l0=l0_route_apps_research,
        c0=c0_retrieve_apps_research,
        pa=pa_assemble_apps_research,
        l2=l2_execute_apps_research,
        exit=exit_finalize_apps_research,
        profile_version="1",
    )


__all__ = [
    "build_app_runtime_contract",
    "parse_payload",
    "APPS_RESEARCH_REQUIRED_FIELDS",
]
