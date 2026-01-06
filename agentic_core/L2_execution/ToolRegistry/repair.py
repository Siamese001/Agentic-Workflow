from __future__ import annotations
import asyncio
'''Brief description of functionality and purpose.'''

import os
import re
from typing import Any, Dict, List, Optional, Protocol

from agentic_core.L2_execution.ToolRegistry.base import SubAtomicAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


# NAMING FIXED: INTELLIGENCE_THRESHOLD → intelligence_threshold
intelligence_threshold = os.getenv("INTELLIGENCE_THRESHOLD", "0.5")

# Optional AutoGen import for collective repair
try:
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False


# NAMING CANON ETERNAL — renamed inline for sovereign discovery — Phase 5 — 2025-12-30
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.schemas.models.anomaly_report import AnomalyReport, AnomalySeverity
from agentic_core.L3_orchestration.workflow_engines.TestPilotAgent import TestPilotAgent

class SherlockAgent(SubatomicTestingMixin, SubAtomicAgent, MCPHardenedMixin, HealerMixin):
    """
    ROLE: Root Cause Analysis. Triggered when TestPilot fails.
    Analyzes cross-file dependencies and fixes interaction bugs.
    
    L4 Checkpoint Integration:
    - Analysis state checkpointed for persistent debugging
    - Trace snapshots stored in L4 ledger
    """
    def __init__(self, context) -> None:
        super().__init__(context)
        self.triggered = False
        self.last_failure = None
        self._mcp_audit('init')

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
                    
        return self.triggered and self.last_failure is not None

    def trigger_investigation(self, modified_file: str, test_file: str, traceback: str):
        """Manually trigger an investigation from another agent (TestPilot)."""
        self.triggered = True
        self.last_failure = {
            'modified_file': modified_file,
            'test_file': test_file,
            'traceback': traceback
        }

    async def execute(self) -> None:
                    
        print(f"\nfrom agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n[>>>] {self.name} ACTIVATED: Investigating test failure...")
        # Replaced blocking calls with async sleep
        await asyncio.sleep(0)

        if not self.last_failure:
            print(f"   [!]  No failure context available")
            return

        await self._analyze_failure(self.last_failure)

    async def _analyze_failure(self, failure_info: dict):
        if not getattr(self.ctx, 'intelligence_enabled', False):
            return

        print(f"   [SCAN] Analyzing failure in {failure_info.get('test_file', 'unknown')}")

        # 1. Read files
        primary = failure_info.get('modified_file')
        traceback = failure_info.get('traceback', '')

        # Extract error file from traceback or default to primary
        error_file = self._extract_error_file(traceback) or primary

        files_content = {}
        for fpath in [primary, error_file]:
            if fpath and isinstance(fpath, str) and os.path.exists(fpath):
                files_content[fpath] = self.ctx.get_file_content(fpath)

        # 2. Formulate Prompt
        prompt = f"""
ROOT CAUSE ANALYSIS:
Test File: {failure_info.get('test_file')}
Modified File: {primary}
Traceback:
{traceback[:2000]}

Context:
{files_content.get(primary, '')[:2000]}

Task: Identify the root cause and provide a fixed version of {primary}.
Return ONLY the python code for {primary}.
"""
        # 3. Request Fix
        # Use resilient mutation capability
        fix = await self.ctx.resilient_mutation(self.name, prompt, code=files_content.get(primary, ""))

        if fix and fix != files_content.get(primary, ""):
            print(f"   🕵️ Sherlock proposing fix for {primary}")
            if self.ctx.write_compliant_file(primary, fix):
                if hasattr(self.ctx, 'modified_files'):
                    self.ctx.modified_files.add(primary)
                print(f"   [OK] Fix Applied")

    def _extract_error_file(self, traceback: str) -> Optional[str]:
        if not traceback:
            return None
        match = re.search(r'File "([^"]+)", line \d+', traceback)
        if match:
            return match.group(1)
        return None

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# NAMING CANON ETERNAL — renamed inline for sovereign discovery — Phase 5 — 2025-12-30
class TestPilotAgent(SubAtomicAgent):
    """
    ROLE: Integration Guardian. Runs pytest and triggers Sherlock on failure.
    """
    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        self.sherlock_ref: Optional[Sherlock] = None

    def set_sherlock(self, sherlock: Sherlock):
                    
        self.sherlock_ref = sherlock

    async def execute(self) -> None:
                    
        print(f"\n[>>>] {self.name} ACTIVATED: Verifying System Integrity...")
        await asyncio.sleep(0)

        # 1. Identify tests to run
        target_tests = set()
        modified_files = getattr(self.ctx, 'modified_files', set())

        if modified_files:
            for mod_file in modified_files:
                test_file = self._find_test_file(mod_file)
                if test_file:
                    target_tests.add(test_file)

        if not target_tests:
            return

    def _find_test_file(self, mod_file: str) -> Optional[str]:
        """Resolves test file mapping using naming conventions."""
        filename = os.path.basename(mod_file)
        test_path = os.path.join("tests", f"test_{filename}")
        return test_path if os.path.exists(test_path) else None

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


# NAMING CANON ETERNAL — renamed inline for sovereign discovery — Phase 5 — 2025-12-30
class ToolsmithAgent(SubAtomicAgent):
    """
    ROLE: Dynamic Tool Forger.
    Creates diagnostic tools on-the-fly based on detected issues.
    L5 Dynamic Agency - self-extends capabilities.
    """

    async def execute(self) -> None:
                    
        print(f"\n[>>>] {self.name} ACTIVATED: Forging Diagnostic Tools...")
        await asyncio.sleep(0)

        if not self.ctx.intelligence_enabled:
            print("   [!]  Intelligence disabled - skipping tool forging")
            return

        needed_tools = self._analyze_needed_tools()

        if not needed_tools:
            print("   [OK] No diagnostic tools needed")
            return

        print(f"   [+] Forging {len(needed_tools)} diagnostic tool(s)...")

        for tool_spec in needed_tools:
            await self._forge_tool(tool_spec)

    def _analyze_needed_tools(self) -> list:
        """Analyze current issues to determine what tools are needed."""
        needed = []

        failures = [k for k, v in self.ctx.results.items() if not v.get('passed')]

        if len(failures) > 5:
            needed.append({
                'name': 'failure_analyzer',
                'purpose': 'Analyze patterns in recurring failures',
                'keys': failures[:10]
            })

        if hasattr(self.ctx, 'flapping_files') and self.ctx.flapping_files:
            needed.append({
                'name': 'flap_detector',
                'purpose': 'Detect and report flapping file patterns',
                'files': list(self.ctx.flapping_files)[:5]
            })

        return needed

    async def _forge_tool(self, tool_spec: dict):
        """Forge a diagnostic tool based on the specification."""
        tool_name = tool_spec['name']
        tool_purpose = tool_spec['purpose']

        print(f"   🔨 Forging: {tool_name}")

        prompt = f"""
Create a Python diagnostic tool for the following purpose:
Purpose: {tool_purpose}
Context: {tool_spec}

Requirements:
1. Single file, <100 lines
2. No external dependencies beyond stdlib
3. Clear output format
4. Include docstring explaining usage
5. Include if __name__ == '__main__' block

Return ONLY the Python code.
"""

        try:
            tool_code = await self.ctx.resilient_mutation(
                self.name, prompt, max_attempts=2
            )

            if tool_code:
                import time
                tool_dir = "scripts/diagnostic_tools"
                os.makedirs(tool_dir, exist_ok=True)

                timestamp = int(time.time())
                tool_path = os.path.join(tool_dir, f"{tool_name}_{timestamp}.py")

                if self.ctx.write_compliant_file(tool_path, tool_code):
                    print(f"   [OK] Forged: {tool_path}")
                else:
                    print(f"   [X] Failed to write tool (blocked by governor)")
        except Exception as e:
            print(f"   [X] Failed to forge {tool_name}: {e}")

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
