"""
LIC Outreach Company Research Executor Shim

Non-destructive shim that re-exports the original company research executor.
This allows Phase 5 refinement without touching core L2.
"""

# Re-export the original executor exactly as-is
from l2.company_research_executor import (
    CompanyResearchExecutor,
    CompanySearchConfig,
    CompanyResearchResult,
    KG_FALLBACK_ARCHETYPES
)

# Ensure all public interfaces are available
__all__ = [
    'CompanyResearchExecutor',
    'CompanySearchConfig', 
    'CompanyResearchResult',
    'KG_FALLBACK_ARCHETYPES'
]
