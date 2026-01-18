"""
SovereignBaseAgent - Sovereign Single Source of Truth (SSOT) Root.

Provides foundational capabilities for agents with sovereign authority.
MCPHardenedMixin is now global to ALL agents via root injection.

MRO HARDENING:
- This is the ROOT of the agent hierarchy
- MCPHardenedMixin is injected HERE so all agents get MCP hardening
- Layer bases add specialized mixins BEFORE SovereignBaseAgent
- MRO Flow: Specialized -> Layer -> SovereignBaseAgent -> MCPHardenedMixin -> object
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional
import logging

from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L3_orchestration.fission_logic.subatomic_testing_mixin import SubatomicTestingMixin

logger = logging.getLogger(__name__)


@dataclass
class SovereignBaseAgent(SubatomicTestingMixin, MCPHardenedMixin):
    """
    Sovereign Single Source of Truth (SSOT) Root.
    
    MCPHardenedMixin is now global to all agents via root injection.
    This ensures EVERY agent in the L0-L6 hierarchy has MCP hardening.
    
    MRO HARDENING:
    - SovereignBaseAgent inherits from MCPHardenedMixin
    - Layer bases inherit from SovereignBaseAgent (+ specialized mixins)
    - Concrete agents inherit from layer bases (+ more specialized mixins)
    - MRO: Specialized -> Layer -> SovereignBaseAgent -> MCPHardenedMixin -> object
    """
    name: str = "SovereignAgent"
    
    def __post_init__(self) -> None:
        """
        Initialize sovereign agent with MCP hardening.
        
        The root stops the super() chain or passes to MCPHardenedMixin.
        
        MRO AUDITOR: Sets _sovereign_initialized sentinel for propagation verification.
        """
        # 1. Cooperative super() call (propagate to MCPHardenedMixin if it has __post_init__)
        if hasattr(super(), "__post_init__"):
            super().__post_init__()
        
        # 2. Set Sentinel for MRO Auditor - verifies initialization chain reached root
        self._sovereign_initialized = True
        
        # 3. Core sovereign initialization logic
        self._initialize_sovereign_state()
    
    def _initialize_sovereign_state(self) -> Any:
        """Initialize sovereign-specific state."""
        self._config: Dict[str, Any] = {}
        self._state: Dict[str, Any] = {}
        self._authority_level = 'standard'
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute the agent's main function."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def get_state(self, key: str) -> Optional[Any]:
        """Get state value."""
        return self._state.get(key)
    
    def set_state(self, key: str, value: Any) -> None:
        """Set state value."""
        self._state[key] = value
    
    def get_authority_level(self) -> str:
        """Get the agent's authority level."""
        return self._authority_level
    
    def elevate_authority(self, level: str) -> None:
        """Elevate the agent's authority level."""
        self._authority_level = level
        logger.info(f"Authority elevated to: {level}")
    
    def log_info(self, message: str) -> None:
        """Log an info message."""
        logger.info(f"[{self.name}] {message}")
    
    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        logger.warning(f"[{self.name}] {message}")
    
    def log_error(self, message: str) -> None:
        """Log an error message."""
        logger.error(f"[{self.name}] {message}")
    
    def log_feedback(self, workflow_id: str, action: str, status: str, details: Dict[str, Any] = None) -> None:
        """Log feedback for a workflow action."""
        logger.info(f"[{self.name}] Workflow {workflow_id}: {action} - {status} - {details or {}}")
    
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """
        Base heal_repository implementation - ROOT termination point.
        
        MRO HARDENING: This is the END of the heal_repository chain.
        Subclasses should call super().heal_repository() which eventually
        reaches here and terminates cleanly.
        """
        # ROOT: No super() call - we ARE the termination point
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        return {"violations": 0, "fixed": 0, "errors": 0, "skipped": 1}


__all__ = ['SovereignBaseAgent']
