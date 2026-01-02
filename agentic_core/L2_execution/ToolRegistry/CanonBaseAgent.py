from __future__ import annotations
"""Compatibility module - re-exports from ExecutionCanonBaseAgent.

This module provides backward compatibility for imports from 
agentic_core.L2_execution.ToolRegistry.CanonBaseAgent
"""
from typing import Dict, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.L2_execution.ToolRegistry.ExecutionCanonBaseAgent import *

@timeout(300)
def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
    """L2 execution/ToolRegistry - operational only."""
    if _call_path is None:
        _call_path = set()
    agent_name = "CanonBaseAgent"
    if agent_name in _call_path:
        return {"errors": 1, "cycle_detected": True}
    if depth > max_depth:
        return {"errors": 1, "depth_limited": True}
    _call_path.add(agent_name)
    try:
        print(f"[{agent_name}] L2 execution/ToolRegistry - operational only")
        return {"skipped": 1}
    finally:
        _call_path.discard(agent_name)
