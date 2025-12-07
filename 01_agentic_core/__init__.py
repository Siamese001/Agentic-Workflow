"""
01_agentic_core/__init__.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: 0a76ec9b8658917737eb654b36482d05a1285fe64bc2bf3ef5c32ad606e81dde
"""


from __future__ import annotations

__version__ = "7.0.0"
__author__ = "Agentic Workflow Team"

# TODO[HUMAN_OWNER]: Legacy v10_7 imports removed - no clear mapping.
# Original imports attempted from non-existent submodules:
#   - .models (SpecialistDraftPacket, SpecialistCritique, etc.)
#   - .safety (PIISanitizerAgent, BiasDetectorAgent, etc.)
#   - .workflow (WorkflowContext, MainGraphState, etc.)
#   - .agents (BaseAgent, SpecialistAgent)
#   - .utils (track_metrics, detect_bias)
#   - .hil (VirtualReviewerPersonaAgent, etc.)
# Decide whether to:
#   - Reimplement on subatomic architecture (L1-L5/P1-P4), or
#   - Map to canonical 03_runtime/shared/ modules, or
#   - Remove these feature paths entirely.
# Affects:
#   - Any code importing from 01_agentic_core directly
#   - Legacy v10_7 compatibility layer

# Subpackage structure (available for explicit imports):
# from 01_agentic_core.L1_cognition import ...
# from 01_agentic_core.L2_execution import ...
# from 01_agentic_core.L3_orchestration import ...
# from 01_agentic_core.L4_memory import ...
# from 01_agentic_core.L5_safety import ...

__all__ = [
    "__version__",
    "__author__",
]
