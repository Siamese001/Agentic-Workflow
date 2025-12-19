import asyncio
import os
import re
import sys
from typing import Optional

from agentic_core.agents.base import SubAtomicAgent

# Use environment variables for configuration
INTELLIGENCE_THRESHOLD = os.getenv("INTELLIGENCE_THRESHOLD", "0.5")

# Optional AutoGen import for collective repair
try:
    import autogen
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False


class Sherlock(SubAtomicAgent):
    """
    ROLE: Root Cause Analysis. Triggered when TestPilot fails.
    Analyzes cross-file dependencies and fixes interaction bugs.
    """
    def __init__(self, context):
        super().__init__(context)
        self.triggered = False
        self.last_failure = None

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

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Investigating test failure...")
        # Replaced blocking calls with async sleep
        await asyncio.sleep(0)
        
        if not self.last_failure:
            print(f"   ⚠️  No failure context available")
            return
        
        await self._analyze_failure(self.last_failure)

    async def _analyze_failure(self, failure_info: dict):
        if not getattr(self.ctx, 'intelligence_enabled', False):
            return

        print(f"   🔍 Analyzing failure in {failure_info.get('test_file', 'unknown')}")
        
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
                print(f"   ✅ Fix Applied")

    def _extract_error_file(self, traceback: str) -> Optional[str]:
        if not traceback:
            return None
        match = re.search(r'File "([^"]+)", line \d+', traceback)
        if match:
            return match.group(1)
        return None


class TestPilot(SubAtomicAgent):
    """
    ROLE: Integration Guardian. Runs pytest and triggers Sherlock on failure.
    """
    def __init__(self, ctx):
        super().__init__(ctx)
        self.sherlock_ref: Optional[Sherlock] = None

    def set_sherlock(self, sherlock: Sherlock):
        self.sherlock_ref = sherlock

    async def execute(self):
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