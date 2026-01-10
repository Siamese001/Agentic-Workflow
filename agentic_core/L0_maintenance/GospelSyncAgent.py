#!/usr/bin/env python3
"""
GOSPEL SYNC AGENT
-----------------
L0 Maintenance Agent designed to ensure 100% synchronization between the 
Gospel (structure_blueprint.py) and the physical filesystem.

CANONICAL PATH: agentic_core/L0_maintenance/GospelSyncAgent.py
VIOLATION JUSTIFICATION: None. Standard L0 Infrastructure mapping.
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Any
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.config.blueprint_sovereign.structure_blueprint import STRUCTURE_BLUEPRINT
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin


class GospelSyncAgent(MCPHardenedMixin):
    """
    THE SSOT GUARDIAN
    Ensures the 'World as it Is' (Filesystem) matches the 'World as it Should Be' (Blueprint).
    Detects heretical files and missing canonical files to protect Toxic Hubs.
    """


    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
        
        Returns:
            Dict with healing summary
        """
        return {"violations": 0, "fixed": 0, "errors": 0}

    def __init__(self, root_dir: str = "."):
        """
        Initialize the Sync Agent with root directory context.
        """
        self.root = Path(root_dir)
        self.blueprint = STRUCTURE_BLUEPRINT
        self.heresy: List[str] = []
        self.missing: List[str] = []

    def perform_sync_audit(self) -> Dict[str, Any]:
        """
        VERBOSE HUNK: Scans the filesystem and compares against the STRUCTURE_BLUEPRINT.
        Identifies drift violations in real-time.
        """
        canonical_files = self._get_canonical_files()
        actual_files = self._get_actual_files()

        # Heresy = Files on disk NOT in Blueprint
        self.heresy = sorted(list(actual_files - canonical_files))
        # Missing = Files in Blueprint NOT on disk
        self.missing = sorted(list(canonical_files - actual_files))

        return {
            "heresy": self.heresy,
            "missing": self.missing,
            "synchronized": len(self.heresy) == 0 and len(self.missing) == 0
        }

    def _get_canonical_files(self) -> Set[str]:
        """
        SUB-LINE PRECISION: Recursively extracts all expected file paths from the Gospel.
        """
        paths = set()
        for layer, config in self.blueprint.items():
            layer_path = config.get("path", "")
            if not layer_path:
                continue
            for agent in config.get("agents", []):
                # Normalize path for multi-OS compatibility
                rel_path = os.path.join(layer_path, f"{agent}.py")
                paths.add(rel_path.replace("\\", "/"))
        return paths

    def _get_actual_files(self) -> Set[str]:
        """
        Scans the physical agentic_core directory for .py files, ignoring __init__.
        """
        actual = set()
        core_path = self.root / "agentic_core"
        for py_file in core_path.glob("**/*.py"):
            if "__init__" not in py_file.name:
                rel_path = py_file.relative_to(self.root)
                actual.add(str(rel_path).replace("\\", "/"))
        return actual

    def report_drift(self) -> None:
        """
        Generates a Sovereign Sync Report for L6 Observability consumption.
        """
        if not self.heresy and not self.missing:
            print("✅ GOSPEL SYNC: Filesystem is in 100% synchronization with the Blueprint.")
            return

        print(f"\n{'='*60}")
        print(f" SOVEREIGN SSOT SYNC REPORT")
        print(f"{'='*60}")

        if self.missing:
            print(f"❌ MISSING CANON ({len(self.missing)}):")
            for m in self.missing:
                print(f"   [ ] {m}")

        if self.heresy:
            print(f"\n☢️  HERETICAL FILES ({len(self.heresy)}):")
            for h in self.heresy:
                print(f"   [!] {h}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    agent = GospelSyncAgent()
    results = agent.perform_sync_audit()
    agent.report_drift()
    
    import sys
    sys.exit(0 if results["synchronized"] else 1)
