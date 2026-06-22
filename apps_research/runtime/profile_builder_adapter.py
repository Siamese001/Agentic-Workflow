"""apps_research profile builder adapter — Bundle C canonical form.

Core binding imports live here (``*_adapter.py`` exempt from authority MV).
``profile_builder.py`` re-exports only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
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
from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
)
from agentic_core.runtime.contracts.sealed_l2_artifact import (
    SealedL2Artifact as ContractSealedL2Artifact,
)
from agentic_core.runtime.contracts.x3_disposition import X3Disposition
from agentic_core.runtime.exit.apps_research_exit_binding import (
    exit_finalize_apps_research,
)
from agentic_core.prompt_governance.apps_research_pa_binding import pa_assemble_apps_research
from agentic_core.L2_execution.apps_research_l2_binding import (
    APPS_RESEARCH_L2_CERT_REF,
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
            manual_brief_path=payload.get("manual_brief_path")
            or payload.get("briefing_artifact_ref")
            or None,
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


@dataclass(frozen=True)
class _IngressExitResult:
    disposition: X3Disposition


def _map_l2_sealed_to_contract(sealed: Any) -> ContractSealedL2Artifact:
    """Adapt package-driven L2 SealedL2Artifact to AG9 contract SealedL2Artifact."""
    output_content = getattr(sealed, "output_content", None)
    if output_content:
        generated_content = json.dumps(output_content)
    else:
        generated_content = getattr(sealed, "generated_content", "") or "{}"

    execution_status = getattr(sealed, "execution_status", "failed")
    if execution_status == "SUCCESS":
        execution_status = "completed"

    return ContractSealedL2Artifact(
        request_id=sealed.request_id,
        run_id=sealed.run_id,
        app_id=getattr(sealed, "app_id", "apps_research"),
        trace_id=sealed.trace_id,
        execution_status=execution_status,
        generated_content=generated_content,
        tenant_id=getattr(sealed, "tenant_id", ""),
        compilation_hash=getattr(sealed, "seal_hash", "")
        or getattr(sealed, "compilation_hash", ""),
        prompt_artifact_digest=getattr(sealed, "prompt_hash", ""),
        proposed_state_diff=dict(getattr(sealed, "proposed_state_diff", None) or {}),
        l5_certification_ref=getattr(sealed, "l5_certification_ref", None)
        or APPS_RESEARCH_L2_CERT_REF,
    )


def exit_finalize_apps_research_ingress(
    sealed: Any,
    *,
    target_company: str | None = None,
    target_role: str | None = None,
    output_directory: str | None = None,
    writeback_policy: Any = None,
) -> _IngressExitResult:
    """AppIngressRunner exit hook — maps runner kwargs to AG9 exit binding."""
    _ = (target_company, target_role, output_directory, writeback_policy)
    contract_sealed = _map_l2_sealed_to_contract(sealed)
    prompt = CompiledPromptArtifact(
        request_id=contract_sealed.request_id,
        run_id=contract_sealed.run_id,
        app_id=contract_sealed.app_id,
        trace_id=contract_sealed.trace_id,
        compilation_hash=contract_sealed.prompt_artifact_digest,
        evidence_digest=getattr(sealed, "evidence_digest", ""),
        tenant_id=contract_sealed.tenant_id,
        l5_certification_ref="pa-package-driven-v1",
    )
    disposition = exit_finalize_apps_research(contract_sealed, prompt)
    return _IngressExitResult(disposition=disposition)


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
        exit=exit_finalize_apps_research_ingress,
        profile_version="1",
    )


__all__ = [
    "build_app_runtime_contract",
    "parse_payload",
    "APPS_RESEARCH_REQUIRED_FIELDS",
]
