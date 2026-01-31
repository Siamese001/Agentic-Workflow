# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, memory, orchestrator, workflow
from __future__ import annotations

import asyncio
from dataclasses import dataclass

# This boosts alignment detection — review and integrate appropriately
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"""Brief description of functionality and purpose."""

import os
import re
from typing import Any

from agentic_core.L2_execution.tool_registry.base import SubAtomicAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth


# NAMING FIXED: INTELLIGENCE_THRESHOLD → intelligence_threshold
intelligence_threshold = os.getenv("INTELLIGENCE_THRESHOLD", "0.5")

# Optional AutoGen import for collective repair
try:
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False


# NAMING CANON ETERNAL — renamed inline for sovereign discovery — Phase 5 — 2025-12-30
from agentic_core.schemas.models.anomaly_report import AnomalyReport

from agentic_core.base_agents.decorators import standard_heal
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class SherlockAgent(SubatomicTestingMixin, SovereignBaseAgent, SubAtomicAgent):
    """
    ROLE: Root Cause Analysis. Triggered when TestPilot fails.
    Analyzes cross-file dependencies and fixes interaction bugs.

    L4 Checkpoint Integration:
    - Analysis state checkpointed for persistent debugging
    - Trace snapshots stored in L4 ledger
    """

    def __init__(self, context: Any) -> None:
        """Initialize the instance."""
        super().__init__(context)
        self.triggered = False
        self.last_failure = None
        self._mcp_audit("init")

    def _perform_healing(self, anomaly: AnomalyReport) -> bool:
        """Perform healing for diagnostic anomalies."""
        self._mcp_audit("healing_start", payload=anomaly.to_dict())

        if anomaly.type == "diagnostic_corruption":
            # Reset diagnostic state
            self.triggered = False
            self.last_failure = None
            self._mcp_audit("healing_success")
            return True

        return False

    def can_run(self) -> bool:
        """Execute can_run operation."""
        return self.triggered and self.last_failure is not None

    def trigger_investigation(self, modified_file: str, test_file: str, traceback: str) -> Any:
        """Manually trigger an investigation from another agent (TestPilot)."""
        self.triggered = True
        self.last_failure = {
            "modified_file": modified_file,
            "test_file": test_file,
            "traceback": traceback,
        }

    async def execute(self) -> None:
        """Execute execute operation."""
        print()
        # Replaced blocking calls with async sleep
        await asyncio.sleep(0)

        if not self.last_failure:
            print("   [!]  No failure context available")
            return

        await self._analyze_failure(self.last_failure)

    async def _analyze_failure(self, failure_info: dict) -> Any:
        """Analyze failure."""
        if not getattr(self.ctx, "intelligence_enabled", False):
            return

        print(f"   [SCAN] Analyzing failure in {failure_info.get('test_file', 'unknown')}")

        # 1. Read files
        primary = failure_info.get("modified_file")
        traceback = failure_info.get("traceback", "")

        # Extract error file from traceback or default to primary
        error_file = self._extract_error_file(traceback) or primary

        files_content = {}
        for fpath in [primary, error_file]:
            if fpath and isinstance(fpath, str) and os.path.exists(fpath):
                files_content[fpath] = self.ctx.get_file_content(fpath)

        # 2. Formulate Prompt
        prompt = f"""
ROOT CAUSE ANALYSIS:
Test File: {failure_info.get("test_file")}
Modified File: {primary}
Traceback:
{traceback[:2000]}

Context:
{files_content.get(primary, "")[:2000]}

Task: Identify the root cause and provide a fixed version of {primary}.
Return ONLY the python code for {primary}.
"""
        # 3. Request Fix
        # Use resilient mutation capability
        fix = await self.ctx.resilient_mutation(
            self.name, prompt, code=files_content.get(primary, "")
        )

        if fix and fix != files_content.get(primary, ""):
            print(f"   🕵️ Sherlock proposing fix for {primary}")
            if self.ctx.write_compliant_file(primary, fix):
                if hasattr(self.ctx, "modified_files"):
                    self.ctx.modified_files.add(primary)
                print("   [OK] Fix Applied")

    def _extract_error_file(self, traceback: str) -> str | None:
        """Extract error file."""
        if not traceback:
            return None
        match = re.search(r'File "([^"]+)", line \d+', traceback)
        if match:
            return match.group(1)
        return None

    @standard_heal
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by SherlockAgent.

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

        # Default implementation - SherlockAgent provides diagnostic analysis
        try:
            return {
                "status": "skipped",
                "details": f"SherlockAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"SherlockAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


# Legacy classes removed 2026-01-06 - use standalone TestPilotAgent.py and ToolsmithAgent.py
# from agentic_core.L2_execution.tool_registry.ToolsmithAgent import ToolsmithAgent
