"""L2 Execution Layer - Task Execution and Coordination

This layer provides execution capabilities for both resume and outreach workflows.
Re-exports robust implementations from the engine modules to maintain architectural compliance.
"""

from __future__ import annotations

# Resume Execution imports
from agentic_core.resume_engine.l2_execution.executors import *  # noqa: F401,F403

# Outreach Execution imports  
from agentic_core.outreach_engine.l2_execution.executors import *  # noqa: F401,F403

# Core execution interfaces
from agentic_core.resume_engine.l2_execution.executors.rg_message_generation_executor import (
    ResumeMessageGenerationExecutor,
)  # noqa: F401

from agentic_core.resume_engine.l2_execution.executors.rg_triplet_extraction_executor import (
    TripletExtractionExecutor,
)  # noqa: F401

from agentic_core.outreach_engine.l2_execution.executors.lic_message_generation_executor import (
    OutreachMessageGenerationExecutor,
)  # noqa: F401

from agentic_core.outreach_engine.l2_execution.executors.lic_company_research_executor import (
    CompanyResearchExecutor,
)  # noqa: F401

from agentic_core.outreach_engine.l2_execution.executors.lic_contact_research_executor import (
    ContactResearchExecutor,
)  # noqa: F401

__all__ = [
    # Resume execution classes
    "ResumeMessageGenerationExecutor",
    "TripletExtractionExecutor",
    # Outreach execution classes
    "OutreachMessageGenerationExecutor", 
    "CompanyResearchExecutor",
    "ContactResearchExecutor",
]
