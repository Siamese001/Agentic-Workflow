from __future__ import annotations

from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.tools import write_gateway as _wg

"\nSprawl Inspector - Pre-Flight Architectural Survey\nIdentifies low-density folders and excessive breadth for consolidation.\nImplements Key 49 (Universal Depth Law) and Key 41 (Modular Atomicity).\n"
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint import AGENTIC_CORE_DIR
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.utils.decorators_compat_util import standard_heal


@dataclass
class SprawlInspectorAgent(SovereignBaseAgent):
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

    # guardian: allow-type-erasure
    def inspect(self) -> Dict[str, Any]:
        """
        Scan directory tree for sprawl violations.

        Returns:
            Report dictionary with violations and flattening candidates
        """
        for root, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
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
    # guardian: allow-type-erasure
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by SprawlInspectorAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"SprawlInspectorAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"SprawlInspectorAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


if __name__ == "__main__":
    inspector: Any = SprawlInspectorAgent(AGENTIC_CORE_DIR)
    data: Any = inspector.inspect()
    inspector.print_summary()
    _wg.write_json("sprawl_report.json", data, indent=4)
    print("\n[OK] Detailed sprawl map saved to sprawl_report.json")
    print("    Use this report to guide architectural consolidation.")
