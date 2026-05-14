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
    compiled_prompt: CompiledPromptArtifact,
) -> SealedL2Artifact:
    """apps_research L2 binding — matches AppIngressRunner._run_profile_stages contract.

    Called as: l2_fn(prompt_artifact) -> SealedL2Artifact

    W4 remediation (bundle-c1-blocker-remediation-a4f9e2):
    Runner calls l2_fn with only CompiledPromptArtifact. RouteContract and
    FinalEvidenceContract are not forwarded to L2 by the runner; the executor
    receives profile-ref defaults instead. App-owned profile refs supply all
    execution policy without requiring route/evidence passthrough.

    Raises:
        TypeError: on bad input types
    """
    if not isinstance(compiled_prompt, CompiledPromptArtifact):
        raise TypeError(
            f"l2_execute_apps_research: expected CompiledPromptArtifact, got {type(compiled_prompt)}"
        )

    l2_execution_profile_ref = "apps_research/config/domain_contract/l2_execution_profile.company_brief.v1.yaml"
    provider_profile_ref = "apps_research/config/domain_contract/provider_profile.company_brief.v1.yaml"
    repair_profile_ref = "apps_research/config/domain_contract/repair_profile.company_brief.v1.yaml"

    return l2_execute_package_driven(
        route_contract=None,
        final_evidence=None,
        compiled_prompt=compiled_prompt,
        l2_execution_profile_ref=l2_execution_profile_ref,
        provider_profile_ref=provider_profile_ref,
        repair_profile_ref=repair_profile_ref,
    )


__all__ = [
    "APPS_RESEARCH_L2_CERT_REF",
    "l2_execute_apps_research",
]
