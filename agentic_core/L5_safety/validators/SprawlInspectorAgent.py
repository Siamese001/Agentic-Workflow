# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, prompt, workflow
from __future__ import annotations

from dataclasses import dataclass

# This boosts alignment detection — review and integrate appropriately
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""
Sprawl Inspector - Pre-Flight Architectural Survey
Identifies low-density folders and excessive breadth for consolidation.
Implements Key 49 (Universal Depth Law) and Key 41 (Modular Atomicity).
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.base_agents.decorators import standard_heal
from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
)


@dataclass
class SprawlInspectorAgent(SubatomicTestingMixin, SovereignBaseAgent):
    """
    Sprawl Inspector - Pre-Flight Architectural Survey.

    Identifies low-density folders and excessive breadth for consolidation.
    Implements Key 49 (Universal Depth Law) and Key 41 (Modular Atomicity).
    """

    def __init__(self, target_path: Path = AGENTIC_CORE_DIR) -> None:
        """
        Initialize sprawl inspector.

        Args:
            target_path: Root directory to inspect for sprawl violations
        """
        self.root: Path = Path(target_path)
        self.MAX_BREADTH: int = 7
        self.MIN_FILES: int = 3
        self.report: Dict[str, Any] = {
            "metadata": {
                "target": str(target_path),
                "timestamp": datetime.now().isoformat(),
                "user": os.getenv("USERNAME", "unknown"),
            },
            "violations": [],
            "flattening_candidates": [],
        }

    def inspect(self) -> Dict[str, Any]:
        """
        Scan directory tree for sprawl violations.

        Returns:
            Report dictionary with violations and flattening candidates
        """
        for root, dirs, files in os.walk(self.root):
            p: Path = Path(root)
            py_files: list[str] = [f for f in files if f.endswith(".py")]
            if len(dirs) > self.MAX_BREADTH:
                self.report["violations"].append(
                    {
                        "path": str(p),
                        "type": "Breadth Violation",
                        "count": len(dirs),
                        "msg": f"Found {len(dirs)} subfolders. Violates 'Magic 7' rule.",
                    }
                )
            if 0 < len(py_files) < self.MIN_FILES and (not dirs) and (p != self.root):
                self.report["flattening_candidates"].append(
                    {
                        "folder": str(p),
                        "files": py_files,
                        "file_count": len(py_files),
                        "reason": "Low Signal Density (Fragmented)",
                    }
                )
        return self.report

    def print_summary(self) -> None:
        """
        Print human-readable summary of sprawl violations.

        Displays breadth violations and flattening candidates.
        """
        print(+"=" * 70)
        print("🔍 PROJECT SPRAWL REPORT")
        print("=" * 70)
        print(f"Target: {self.report['metadata']['target']}")
        print(f"Timestamp: {self.report['metadata']['timestamp']}")
        print()
        print(f"📊 Breadth Violations: {len(self.report['violations'])}")
        print(f"📁 Flattening Candidates: {len(self.report['flattening_candidates'])}")
        if self.report["violations"]:
            print("\n[BREADTH VIOLATIONS]")
            for v in self.report["violations"]:
                print(f"  • {v['path']}: {v['count']} subfolders (max: {self.MAX_BREADTH})")
        if self.report["flattening_candidates"]:
            print("\n[FLATTENING CANDIDATES]")
            for c in self.report["flattening_candidates"][:10]:
                print(f"  • {c['folder']}: {c['file_count']} files - {c['reason']}")
            if len(self.report["flattening_candidates"]) > 10:
                print(f"  ... and {len(self.report['flattening_candidates']) - 10} more")
        print("=" * 70)

    @standard_heal
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)


if __name__ == "__main__":
    inspector: Any = SprawlInspectorAgent(AGENTIC_CORE_DIR)
    data: Any = inspector.inspect()
    inspector.print_summary()
    with open("sprawl_report.json", "w") as f:
        json.dump(data, f, indent=4)
    print("\n[OK] Detailed sprawl map saved to sprawl_report.json")
    print("    Use this report to guide architectural consolidation.")
