"""L3 Orchestration Layer - Workflow Coordination and Management

This layer provides orchestration capabilities for both resume and outreach workflows.
Re-exports robust implementations from the engine modules to maintain architectural compliance.
"""

from __future__ import annotations

# Resume Orchestration imports
from agentic_core.resume_engine.l3_orchestration.orchestrators import *  # noqa: F401,F403

# Outreach Orchestration imports  
from agentic_core.outreach_engine.l3_orchestration.orchestrators import *  # noqa: F401,F403

# Core orchestration interfaces
from agentic_core.outreach_engine.l3_orchestration.orchestrators.lic_orchestrator import (
    LICOrchestrator,
    RecipientProfile,
    LICPipelineResult,
)  # noqa: F401

from agentic_core.outreach_engine.l3_orchestration.orchestrators.lic_outreach_orchestrator import (
    OutreachOrchestrator,
)  # noqa: F401

from agentic_core.resume_engine.l3_orchestration.orchestrators.rg_kg_retrieval_orchestrator import (
    ResumeKGOrchestrator,
)  # noqa: F401

__all__ = [
    # Outreach orchestration classes
    "LICOrchestrator",
    "OutreachOrchestrator",
    "RecipientProfile",
    "LICPipelineResult",
    # Resume orchestration classes
    "ResumeKGOrchestrator",
]
