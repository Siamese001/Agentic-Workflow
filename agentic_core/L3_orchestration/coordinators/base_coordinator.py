"""
HARDENED Base Coordinator - Foundation for Agent Consolidation

Restored: 2026-01-13 | Version: 2.0.0
Original: archives/unmapped_drift/20260107/agentic_core/common/coordinators/base_coordinator.py

Enforces:
- Healing chain preservation
- MCP hardening
- Consistent API
- Lazy initialization pattern
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict
import logging

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

log = logging.getLogger(__name__)


class WorkflowCoordinator(HealerMixin, MCPHardenedMixin, ABC):
    """
    HARDENED Base Coordinator
    
    Enforces:
    - Healing chain preservation
    - MCP hardening
    - Consistent API
    - Lazy initialization pattern
    """
    
    def __init__(self, project_root: Path | None = None):
        super().__init__()
        self.project_root = project_root or Path.cwd()
        self._initialized = False
    
    def _lazy_init(self) -> None:
        """Override for expensive setup."""
        if not self._initialized:
            self._initialize_components()
            self._initialized = True
    
    def _initialize_components(self) -> None:
        """Subclasses override for component registration."""
        pass
    
    @abstractmethod
    async def coordinate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Primary coordination method."""
        raise NotImplementedError
    
    def heal_repository(self, dry_run: bool = True, **kwargs) -> Dict[str, int]:
        """Preserve full healing chain."""
        return super().heal_repository(dry_run=dry_run, **kwargs)
