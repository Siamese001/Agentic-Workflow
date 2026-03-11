"""
HierarchyValidatorAgent - L5 Pure Validator.

Read-only scan of territory root violations via HierarchyAgent.scan_root_violations().
Emits structured results without mutating the filesystem.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class HierarchyValidatorAgent:
    """L5 Certify-only validator for hierarchy/territory root violations."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan_root_violations(self, target_territory: str | None = None) -> dict[str, Any]:
        """Delegate to HierarchyAgent.scan_root_violations (read-only)."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

        agent = HierarchyAgent(project_root=self.project_root, healing_enabled=False)
        return agent.scan_root_violations(target_territory=target_territory)
