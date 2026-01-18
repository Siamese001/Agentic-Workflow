from __future__ import annotations
from dataclasses import dataclass
"""
ReportingAgent: Sovereign Compliance Diagnostic Visualizer

Provides runtime diagnostic reporting for canon compliance missions.
Generates:
- Territory scope summary (file counts per sovereign root)
- ASCII directory tree visualization (clean, excludes noise)
- Compliance metrics integration (via MetricsAgent)
- Combined diagnostic report

Directly replaces remaining utility functions from void_compliance.py:
  - get_folder_scope_summary()
  - generate_ascii_tree()

Placed in observability/compliance per SSOT semantic registry:
  "Compliance reporting, canon drift detection logs, and policy Violation records"

Depth: agentic_core/observability/compliance/reporting_agent.py
      → root/L1/L2/file.py → exactly 4 parts → Canon Key 3/12 compliant
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from datetime import datetime

from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    SOVEREIGN_EXCLUDED_FOLDERS,      # Comprehensive exclusion set (.git, venv, __pycache__, etc.)
)

# Additional reporting-specific exclusions (stubs, backups)
SCOPE_SUMMARY_EXCLUSIONS = {
    "stubs", "backups", ".sovereign_healing_backup", 
    "node_modules", ".pytest_cache", ".ruff_cache"
}

# Optional import: MetricsAgent from sibling territory
try:
    from agentic_core.L6_observability.metrics.MetricsAgent import metrics_agent as MetricsAgent
    METRICS_AGENT_AVAILABLE = True
except ImportError:  # MetricsAgent not implemented yet or optional
    METRICS_AGENT_AVAILABLE = False

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin

@dataclass
class ReportingAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Autonomous diagnostic agent for compliance reporting and visualization.
    Operates independently — no validation, only observation.
    Safe to run alongside or after ComplianceOrchestratorAgent.
    """

    def __init__(self, project_root: Path) -> None:
        """
        Initialize with project root.
        Combines all exclusion sets for consistent filtering.

        Technical note:
        - MetricsAgent is optional — ReportingAgent remains functional without it
        - Loose coupling prevents gravity drift
        """
        self.project_root = project_root.resolve()
        # Union of general sovereign exclusions + reporting-specific
        self.exclude_dirs = SOVEREIGN_EXCLUDED_FOLDERS | SCOPE_SUMMARY_EXCLUSIONS
        self.metrics_agent: Optional[MetricsAgent] = None

        if METRICS_AGENT_AVAILABLE:
            try:
                self.metrics_agent = MetricsAgent(self.project_root)
            except Exception as e:
                # Silent fallback — metrics optional
                print(f"[ReportingAgent] MetricsAgent init failed (optional): {e}")

    def get_folder_scope_summary(self) -> Dict[str, int]:
        """
        Generate territory scope summary.
        Counts .py files per top-level sovereign folder.
        Skips excluded/technical directories.

        Returns:
            Dict mapping folder name → Python file count

        Technical notes:
        - Uses rglob("*.py") for deep count (includes all nested files)
        - Filters top-level iteration only (not recursive folder scan)
        - Excludes hidden dirs and known noise (venv, .git, etc.)
        """
        summary: Dict[str, int] = {}

        for folder_path in self.project_root.iterdir():
            if not folder_path.is_dir():
                continue
            if folder_path.name in self.exclude_dirs:
                continue
            if folder_path.name.startswith('.'):
                continue

            # Count all .py files recursively within this root
            py_files = list(folder_path.rglob("*.py"))
            summary[folder_path.name] = len(py_files)

        return summary

    def generate_ascii_tree(self, max_depth: int = 3) -> str:
        """
        Generate clean ASCII directory tree visualization.

        Args:
            max_depth: Maximum depth to display (default 3 for clarity)

        Returns:
            Multi-line string with ASCII tree

        Technical notes:
        - Excludes all noise folders (same set as scope summary)
        - Sorts items for deterministic output
        - Uses standard tree connectors (├──, └──, │)
        - Starts from project root name
        """
        tree_lines: list = []
        start_path = self.project_root
        tree_lines.append(f"{start_path.name}/")

        def _walk_directory(current_path: Path, prefix: str = "", depth: int = 0) -> None:
            if depth >= max_depth:
                return

            # Get and sort meaningful children
            children = [
                item for item in current_path.iterdir()
                if item.name not in self.exclude_dirs
                and not item.name.startswith('.')
            ]
            children.sort(key=lambda x: (x.is_file(), x.name.lower()))

            for index, item in enumerate(children):
                is_last = index == len(children) - 1
                connector = "└── " if is_last else "├── "
                tree_lines.append(f"{prefix}{connector}{item.name}")

                if item.is_dir():
                    extension = "    " if is_last else "│   "
                    _walk_directory(item, prefix + extension, depth + 1)

        _walk_directory(start_path, depth=1)
        return "\nfrom agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n".join(tree_lines)

    def _get_compliance_metrics(self) -> Dict[str, Any]:
        """
        Pull live compliance metrics from MetricsAgent (if available).

        Expected metrics (defined in MetricsAgent):
        - compliance.total_violations (gauge)
        - compliance.violations_by_type (labels: type=location|naming|hierarchy|import|gravity)
        - compliance.compliance_rate (gauge 0-100)

        Returns:
            Dict of metrics or empty if unavailable
        """
        if not self.metrics_agent:
            return {}

        try:
            return {
                "total_violations": self.metrics_agent.get_counter("compliance.total_violations"),
                "violations_by_type": self.metrics_agent.get_labeled_counter("compliance.violations_by_type"),
                "compliance_rate": self.metrics_agent.get_gauge("compliance.compliance_rate"),
                "last_scan_timestamp": self.metrics_agent.get_metadata("compliance.last_scan"),
            }
        except Exception:
            return {}

    def run_diagnostic_report(self) -> Dict[str, Any]:
        """
        Generate complete diagnostic report.
        Combines:
        - Scope summary
        - ASCII tree
        - Live compliance metrics (from MetricsAgent)

        Returns:
            Dict with:
            - "scope_summary": file counts per root
            - "ascii_tree": full tree string
            - "compliance_metrics": quantitative metrics (if available)
            - "generated_at": timestamp (for logs)
        """
        report = {
            "scope_summary": self.get_folder_scope_summary(),
            "ascii_tree": self.generate_ascii_tree(),
            "compliance_metrics": self._get_compliance_metrics(),
            "generated_at": datetime.now().isoformat(),
        }

        # Add metadata about metrics availability
        report["metrics_available"] = METRICS_AGENT_AVAILABLE and bool(self.metrics_agent)

        return report

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """Observability agent - invoke shared healing chain."""
        if _call_path is None:
            _call_path = set()
        # Invoke shared HealerMixin chain for diagnostics, rollback, MCP hardening
        super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
        print(f"[{self.__class__.__name__}] Observability agent - healing chain invoked")
        return {"skipped": 1}


# PascalCase is now the canonical name
