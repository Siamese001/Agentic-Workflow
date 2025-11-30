"""L4 Memory/State Layer - Data Persistence and Retrieval

This layer provides memory, state management, and RAG capabilities for both resume and outreach workflows.
Re-exports robust implementations from the engine modules to maintain architectural compliance.
"""

from __future__ import annotations

# Resume Memory/State imports
from agentic_core.resume_engine.l4_memory_state.memory import *  # noqa: F401,F403
from agentic_core.resume_engine.l4_memory_state.rag import *  # noqa: F401,F403

# Outreach Memory/State imports
from agentic_core.outreach_engine.l4_memory_state.memory import *  # noqa: F401,F403
from agentic_core.outreach_engine.l4_memory_state.rag import *  # noqa: F401,F403

# Core memory interfaces
from agentic_core.resume_engine.l4_memory_state.memory.rg_state_manager import (
    ResumeStateManager,
)  # noqa: F401

from agentic_core.resume_engine.l4_memory_state.rag.rg_rag_engine import (
    ResumeRAGEngine,
)  # noqa: F401

from agentic_core.outreach_engine.l4_memory_state.memory.lic_memory import (
    OutreachMemoryManager,
)  # noqa: F401

from agentic_core.outreach_engine.l4_memory_state.rag.lic_rag_policies import (
    get_rag_policy,
)  # noqa: F401

__all__ = [
    # Resume memory classes
    "ResumeStateManager",
    "ResumeRAGEngine",
    # Outreach memory classes
    "OutreachMemoryManager",
    "get_rag_policy",
]
