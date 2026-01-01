"""SafetyBaseAgent — L5 Base with Healing Capability (Phase 3)

L5 Safety agents perform validation, enforcement, and compliance checking.
This base provides default-on healing via HealerMixin.

Table Decision (L5 Safety):
- Basic Self-Testing: YES (via _run_self_tests)
- Healing Capability: YES (via HealerMixin)
"""
from typing import Any, Dict, Optional
import logging

from agentic_core.common.healing.healer_mixin import HealerMixin

Logger = logging.getLogger(__name__)


# NOT_AN_AGENT — Base class for L5 agents, not a true agent itself
class SafetyBaseAgent(HealerMixin):
    """Base class for L5 Safety agents with healing capability.
    
    Provides:
    - Default-on healing via HealerMixin
    - Standard initialization pattern
    - Self-testing support
    
    L5 agents should inherit from this to get automatic healing.
    """
    
    def __init__(self, project_root=None, ctx=None):
        self.project_root = project_root
        self.ctx = ctx
        self.name = self.__class__.__name__
    
    def _run_self_tests(self) -> bool:
        """Phase 1: Self-testing for L5 compliance."""
        assert hasattr(self, 'name'), "Missing name"
        return True


__all__ = ["SafetyBaseAgent"]
