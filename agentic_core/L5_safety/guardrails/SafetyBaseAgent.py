from __future__ import annotations
"""SafetyBaseAgent — L5 Base with Healing Capability (Phase 3)

L5 Safety agents perform validation, enforcement, and compliance checking.
This base provides default-on healing via HealerMixin.

Table Decision (L5 Safety):
- Basic Self-Testing: YES (via _run_self_tests)
- Healing Capability: YES (via HealerMixin)
"""
from typing import Any, Dict, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout
import logging

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

Logger = logging.getLogger(__name__)


# NOT_AN_AGENT — Base class for L5 agents, not a true agent itself
class SafetyBaseAgent(SovereignBaseAgent):
    """Base class for L5 Safety agents with healing capability.
    
    Provides:
    - Default-on healing via SovereignBaseAgent
    - Real logging (log_info/warning/error)
    - Standard initialization pattern
    - Self-testing support
    
    L5 agents should inherit from this to get automatic healing.
    """
    
    def __init__(self, project_root=None, ctx=None, **kwargs):
        super().__init__(ctx=ctx or kwargs.get("ctx"))  # Root handles name
        self.project_root = project_root
    
    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L5 compliance."""
        assert hasattr(self, 'name'), "Missing name"
        return True


    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L5 safety base - operational only."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()
        
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            self.log_info("L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


__all__ = ["SafetyBaseAgent"]
