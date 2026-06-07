"""
Compat shim: apps_lic.engines.* → reasoning (renamed in 2026-Q1 refactor).

AG-RGGOV-9: REMOVED all apps_rg imports. Core aliases must NOT point to
apps_rg runtime engines, orchestrators, planners, hops, or executors.

apps_rg is now declarative-ingress-only. If core needs apps_rg data,
it references declarative profiles at apps_rg/profiles/*.yaml.

All apps_rg runtime imports have been QUARANTINED per AG-RGGOV-8 and AG-RGGOV-9.

REMOVED imports (QUARANTINED):
- REMOVED: BrandComplianceAgent, CampaignPlannerAgent, ContentStrategyAgent
- REMOVED: ContentQualityAgent, RgHealingOrchestrator, RgReflectionAgent
- REMOVED: RgResumeOrchestrator, ResumeAssemblyAgent, ResumeEnhancementOrchestrator
- REMOVED: All apps_rg/integrations/hops/*, All apps_rg/prompt_assembly/*
- REMOVED: All apps_rg/cert/*, All apps_rg/enforcement/*, All apps_rg/validators/*

See: docs/archive/windsurf/legacy-tree/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19

W7 CLEANUP (2026-05-11): Removed 4 dead Wave-10 imports that raised ModuleNotFoundError:
- REMOVED: CampaignBalanceAgent (file deleted Wave 10)
- REMOVED: DeliverabilityAgent (file deleted Wave 10)
- REMOVED: Hop1ProfileAnalysisAgent (file deleted Wave 10)
- REMOVED: Hop2ResearchAgent (file deleted Wave 10)
Retained 3 live agents still present in apps_lic/reasoning/.
"""

# AG-RGGOV-9: apps_lic imports preserved (different app, out of scope)
# Only agents confirmed present in apps_lic/reasoning/ as of W7 cleanup.
from apps_lic.reasoning.GovernanceShieldAgent import GovernanceShieldAgent  # noqa: F401
from apps_lic.reasoning.LicHealingOrchestrator import LicHealingOrchestrator  # noqa: F401
from apps_lic.reasoning.LicReflectionAgent import LicReflectionAgent  # noqa: F401

# AG-RGGOV-9: All apps_rg imports REMOVED
# No apps_rg symbols may be exported from core aliases

__all__ = [
    # apps_lic exports — live agents only (W7 cleanup removed deleted Wave-10 agents)
    "GovernanceShieldAgent",
    "LicHealingOrchestrator",
    "LicReflectionAgent",
    # AG-RGGOV-9: All apps_rg exports REMOVED
]
