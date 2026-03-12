"""
HierarchyValidatorAgent - L5 Pure Validator.

Read-only scan of territory root violations via HierarchyAgent.scan_root_violations().
Emits structured results without mutating the filesystem.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class HierarchyValidatorAgent:
    """L5 Certify-only validator for hierarchy/territory root violations."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan_root_violations(self, target_territory: str | None=None) -> dict[str, Any]:
        """Delegate to HierarchyAgent.scan_root_violations (read-only)."""
        from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent
        agent = HierarchyAgent(project_root=self.project_root, healing_enabled=False)
        return agent.scan_root_violations(target_territory=target_territory)
