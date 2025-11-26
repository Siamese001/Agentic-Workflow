"""
LIC Outreach Contact Research Executor Shim

Non-destructive shim that re-exports the original contact research executor.
This allows Phase 5 refinement without touching core L2.
"""

# Re-export the original executor exactly as-is
from l2.contact_research_executor import (
    ContactResearchExecutor,
    ContactSearchConfig,
    ContactResearchResult,
    RefinementTaskResult
)

# Ensure all public interfaces are available
__all__ = [
    'ContactResearchExecutor',
    'ContactSearchConfig',
    'ContactResearchResult', 
    'RefinementTaskResult'
]
