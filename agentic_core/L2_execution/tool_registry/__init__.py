from __future__ import annotations
"""
L2 Execution: Tool Registry (SSOT)
Pattern: Builder/Healer agents (Validation + Healing)
Rule: All agents here must inherit from HealerMixin.

DEPRECATION WARNING: ToolRegistry (PascalCase) is legacy and scheduled 
for consolidation in Phase 4. Use this snake_case path for all new imports.

Status: CANONICAL snake_case location
Location: agentic_core/L2_execution/tool_registry/
Documentation: PHASE4_TOOLREGISTRY_CONSOLIDATION_RISKS.md
"""

from .context import RegistryContext
from .SubAtomicAgent import SubAtomicAgent
from .utils import tool_vault

__all__ = [
    "RegistryContext",
    "SubAtomicAgent",
    "tool_vault",
]