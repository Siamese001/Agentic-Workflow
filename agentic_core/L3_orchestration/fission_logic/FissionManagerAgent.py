from __future__ import annotations
"""
FissionManagerAgent - Simple Task Decomposition (Legacy)
Consolidated 2026-01-06: Use WorkflowFissionManagerAgent for full implementation.
This is a simplified stub for backward compatibility.
"""
import logging
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.utils.core_extensions.timeout_decorator import timeout

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

# Import canonical implementation
from agentic_core.L3_orchestration.workflow_engines.WorkflowFissionManagerAgent import FissionManagerAgent as WorkflowFissionManagerAgent

# Legacy stub for backward compatibility
class _LegacyFissionManagerAgent(MCPHardenedMixin):
    """
    L3 Orchestration: The Task Splitter.
    Determines if a mission needs to be broken down into sub-atomic hops.
    """
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    async def decompose_task(self, Task: str) -> List[Dict]:
        """Splits a complex Task into a list of atomic contexts for SubatomicHops."""
        logging.info(f"FissionManagerAgent: Decomposed into {len(contexts)} atomic hops.")
        contexts = [
            {"hop_id": 1, "Task": f"Phase 1: {Task[:20]}..."},
            {"hop_id": 2, "Task": "Phase 2: Final synthesis."}
        ]
        return contexts

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L3 orchestration agent - invoke shared healing chain."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            # Invoke shared HealerMixin chain for diagnostics, rollback, MCP hardening
            super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
            print(f"[{agent_name}] L3 orchestration - healing chain invoked")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
