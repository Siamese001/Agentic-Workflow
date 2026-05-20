"""apps_research Prompt Assembly binding using generic package-driven PA.

Consumes app-owned prompt profiles/templates, delegates to generic core binding.

W4 remediation (bundle-c1-blocker-remediation-a4f9e2):
- Fixed import: runtime.c0.c0_package_driven_grounding (was L1_cognition.c0_package_driven_grounding)
- Aligned signature to AppIngressRunner._run_profile_stages calling convention:
    pa_fn(route, l1_plan, fec, validated) -> CompiledPromptArtifact
- Extracts user_task from validated_request.app_payload instead of expecting a str arg
- Returns single CompiledPromptArtifact (unwraps tuple from generic binding)
"""
from __future__ import annotations

from typing import Any

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.c0.c0_package_driven_grounding import FinalEvidenceContract
from agentic_core.prompt_governance.pa_package_driven_binding import (
    pa_assemble_prompt_package_driven,
    CompiledPromptArtifact,
)


def pa_assemble_apps_research(
    route_contract: RouteContract,
    l1_plan: L1PlanContract,
    final_evidence: FinalEvidenceContract,
    validated_request: Any,
) -> CompiledPromptArtifact:
    """apps_research PA binding — matches AppIngressRunner._run_profile_stages contract.

    Called as: pa_fn(route, l1_plan, fec, validated) -> CompiledPromptArtifact

    Extracts user_task from validated_request.app_payload (target_company field).
    Delegates to generic package-driven PA; unwraps the tuple return.
    All prompt templates and profiles live in apps_research/config/ and apps_research/prompts/.
    """
    app_payload = getattr(validated_request, "app_payload", None) or {}
    if isinstance(app_payload, dict):
        user_task = (
            app_payload.get("target_company")
            or app_payload.get("topic")
            or ""
        )
    else:
        user_task = (
            getattr(app_payload, "target_company", None)
            or getattr(app_payload, "topic", None)
            or ""
        )

    from pathlib import Path

    _repo_root = Path(__file__).resolve().parents[2]
    prompt_profile_ref = str(
        _repo_root / "apps_research/config/domain_contract/prompt_profile.company_brief.v1.yaml"
    )

    artifact, _boundary_receipt, _security_receipt = pa_assemble_prompt_package_driven(
        l1_plan=l1_plan,
        route_contract=route_contract,
        final_evidence=final_evidence,
        user_task=user_task,
        prompt_profile_ref=prompt_profile_ref,
    )
    return artifact


# Legacy test import name (AG9 spine contract tests).
pa_compose_apps_research = pa_assemble_apps_research

__all__ = ["pa_assemble_apps_research", "pa_compose_apps_research"]
