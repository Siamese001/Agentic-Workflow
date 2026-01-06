# NEW FILE: Root base class for all agents (L0-L5)
# Location: agentic_core/base_agents/SovereignBaseAgent.py
# Purpose: Single root of truth providing:
#   - Mandatory HealerMixin
#   - Standardized dataclass initialization with ValidationContext
#   - Real logging (log_info / log_warning / log_error)
#   - can_run() based on context signals
#   - Abstract async execute() enforcement
#   - Basic _run_self_tests() (override per layer/agent)
#   - Standardized heal_repository() with cycle/depth protection
#
# All layer-specific bases will inherit from this (Phase 3).
# Agents inherit from their layer base → implicit Sovereign features.

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from agentic_core.L4_state.validation_context.ValidationContext import ValidationContext
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.redis_cache_mixin import RedisCacheMixin
from agentic_core.utils.core_extensions.pinecone_vector_mixin import PineconeVectorMixin


@dataclass
class SovereignBaseAgent(ABC, HealerMixin, RedisCacheMixin, PineconeVectorMixin):
    """Root base class for ALL agents across L0-L5.
    
    Provides universal infrastructure:
    - Healing (HealerMixin)
    - Redis caching (RedisCacheMixin) - with graceful degradation
    - Pinecone vectors (PineconeVectorMixin) - with graceful degradation
    - Real logging (replaces former stubs)
    - Context + signal-based can_run()
    - Standardized name
    - Abstract async execution contract
    - Basic self-testing
    - Protected heal_repository()
    """
    ctx: ValidationContext
    debug_mode: bool = False
    
    name: str = field(init=False)
    
    def __post_init__(self) -> None:
        self.name = self.__class__.__name__
    
    def log_info(self, msg: str) -> None:
        print(f"[{self.name}] INFO: {msg}")
    
    def log_warning(self, msg: str) -> None:
        print(f"[{self.name}] WARNING: {msg}")
    
    def log_error(self, msg: str) -> None:
        print(f"[{self.name}] ERROR: {msg}")
    
    def can_run(self) -> bool:
        """Default gating - skip if critical failure signal present."""
        return "CRITICAL_FAIL" not in self.ctx.signals
    
    @abstractmethod
    async def execute(self) -> Any:
        """All agents MUST implement async execution."""
        raise NotImplementedError(f"{self.name} must implement async execute()")
    
    def _run_self_tests(self) -> bool:
        """Basic structural self-tests - override for layer-specific checks."""
        assert hasattr(self, "name"), "Missing name attribute"
        assert hasattr(self, "ctx"), "Missing ctx attribute"
        return True
    
    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: Optional[set] = None,
    ) -> Dict[str, int]:
        """Standardized healing with shared HealerMixin chain invocation."""
        if _call_path is None:
            _call_path = set()
        
        if self.name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        
        _call_path.add(self.name)
        try:
            # Invoke shared HealerMixin chain for diagnostics, rollback, MCP hardening
            super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
            self.log_info("Healing chain invoked")
            return {"skipped": 1}
        finally:
            _call_path.discard(self.name)
