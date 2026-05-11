"""apps_research L2 execution binding using generic package-driven L2 executor.

Per plan apps-research-rich-content-runtime-customization-a1b2c3.

L2 is the SIXTH stage. Its job is to:
1. Consume CompiledPromptArtifact from PA
2. Execute through generic provider gateway via package-driven L2
3. Emit typed SealedL2Artifact for Exit to finalize

This binding is a THIN ADAPTER that delegates to the generic package-driven
L2 executor. All execution policy comes from apps_research-owned profiles.

Hard boundary:
- apps_research owns: l2_execution_profile, provider_profile, repair_profile
- agentic_core owns: generic L2 package-driven executor, provider gateway
"""
from __future__ import annotations

from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.c0.c0_package_driven_grounding import FinalEvidenceContract
from agentic_core.prompt_governance.pa_package_driven_binding import CompiledPromptArtifact
from agentic_core.L2_execution.l2_package_driven_executor import (
    l2_execute_package_driven,
    SealedL2Artifact,
)

APPS_RESEARCH_L2_CERT_REF: str = "l2-apps-research-company-brief-v1"


def l2_execute_apps_research(
    route_contract: RouteContract,
    final_evidence: FinalEvidenceContract,
    compiled_prompt: CompiledPromptArtifact,
) -> SealedL2Artifact:
    """
    apps_research L2 execution that delegates to generic package-driven executor.
    
    Consumes app-owned L2 execution, provider, and repair profiles.
    All execution policy declared in apps_research/config/domain_contract/.
    
    Args:
        route_contract: RouteContract from L0
        final_evidence: FinalEvidenceContract from C0
        compiled_prompt: CompiledPromptArtifact from PA
    
    Returns:
        SealedL2Artifact with full execution provenance
    
    Raises:
        TypeError: on bad input types
    """
    # App-owned profile refs
    l2_execution_profile_ref = "apps_research/config/domain_contract/l2_execution_profile.company_brief.v1.yaml"
    provider_profile_ref = "apps_research/config/domain_contract/provider_profile.company_brief.v1.yaml"
    repair_profile_ref = "apps_research/config/domain_contract/repair_profile.company_brief.v1.yaml"
    
    # Delegate to generic package-driven executor
    return l2_execute_package_driven(
        route_contract=route_contract,
        final_evidence=final_evidence,
        compiled_prompt=compiled_prompt,
        l2_execution_profile_ref=l2_execution_profile_ref,
        provider_profile_ref=provider_profile_ref,
        repair_profile_ref=repair_profile_ref,
    )


__all__ = [
    "APPS_RESEARCH_L2_CERT_REF",
    "l2_execute_apps_research",
]
