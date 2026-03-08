"""
RootHygieneValidatorAgent - L5 Pure Validator.

Read-only scan of root hygiene violations via RootHygieneAgent.scan_root_violations().
Emits structured results without mutating the filesystem.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class RootHygieneValidatorAgent:
    """L5 Certify-only validator for root directory hygiene violations."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()

    def scan_root_violations(self) -> dict[str, Any]:
        """Delegate to RootHygieneAgent.scan_root_violations (read-only)."""
        from agentic_core.L5_safety.reasoning.root_hygiene_healer import RootHygieneAgent

        agent = RootHygieneAgent(project_root=self.project_root, dry_run=True)
        return agent.scan_root_violations()
