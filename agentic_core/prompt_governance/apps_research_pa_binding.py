"""apps_research Prompt Assembly binding using generic package-driven PA.

Consumes app-owned prompt profiles/templates, delegates to generic core binding.
"""
from __future__ import annotations

from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.L1_cognition.c0_package_driven_grounding import FinalEvidenceContract
from agentic_core.prompt_governance.pa_package_driven_binding import (
    pa_assemble_prompt_package_driven,
    CompiledPromptArtifact,
    PromptBoundaryReceipt,
    AssemblySecurityReceipt,
)


def pa_assemble_apps_research(
    l1_plan: L1PlanContract,
    route_contract: RouteContract,
    final_evidence: FinalEvidenceContract,
    user_task: str,
) -> tuple[CompiledPromptArtifact, PromptBoundaryReceipt, AssemblySecurityReceipt]:
    """
    apps_research Prompt Assembly that consumes app-owned prompt profiles.
    
    Delegates to generic package-driven core PA binding.
    All prompt templates and profiles live in apps_research/config/ and apps_research/prompts/.
    
    Uses canonical slot order: S0-D0-I0-E0-C0-M0-U0-H0-R0
    """
    # Use default prompt profile for apps_research company_brief
    prompt_profile_ref = "apps_research/config/domain_contract/prompt_profile.company_brief.v1.yaml"
    
    return pa_assemble_prompt_package_driven(
        l1_plan=l1_plan,
        route_contract=route_contract,
        final_evidence=final_evidence,
        user_task=user_task,
        prompt_profile_ref=prompt_profile_ref,
    )


__all__ = ["pa_assemble_apps_research"]
