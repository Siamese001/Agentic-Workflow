"""
01_agentic_core/L1_cognition/__init__.py
L1 Cognition Layer - Core Cognitive Processing.

This layer handles the primary cognitive functions including:
- P1_retrieve: Context retrieval and information gathering
- P2_inspect: Structure and semantic inspection
- P3_aggregate: Action aggregation and execution
- P4_safety: Safety policy enforcement

Auto-hardened by WINDSURF v7 — Production-ready, type-safe, zero-loss.
"""

from __future__ import annotations

__version__ = "7.0.0"

# TODO[HUMAN_OWNER]: Legacy v10_7 imports removed - no clear mapping.
# Original imports attempted from non-existent submodules:
#   - .models (SpecialistDraftPacket, EvidenceClarificationRecord, etc.)
#   - .safety (PIISanitizerAgent, BiasDetectorAgent, etc.)
#   - .strategy (QueryComplexityClassifier, ToTStrategistAgent)
#   - .prompting (PromptEngineerAgent)
#   - .rag (RAG_SearchAgent)
#   - .drafting (StructureLeadAgent, NarrativeStylistAgent, etc.)
#   - .bullet (BulletEntityExtractionAgent, etc.)
#   - .hil (VirtualReviewerPersonaAgent, etc.)
# Decide whether to:
#   - Reimplement on subatomic architecture (P1-P4 phases), or
#   - Map to canonical 03_runtime/shared/ modules, or
#   - Remove these feature paths entirely.
# Affects:
#   - Any code importing from L1_cognition directly
#   - Legacy v10_7 agent implementations

# Subpackage structure (available for explicit imports):
# from 01_agentic_core.L1_cognition.P1_retrieve import ...
# from 01_agentic_core.L1_cognition.P2_inspect import ...
# from 01_agentic_core.L1_cognition.P3_aggregate import ...
# from 01_agentic_core.L1_cognition.P4_safety import ...

__all__ = [
    "__version__",
]
