"""
agentic_core/agents/repair.py
Depth: 3
Role: Active healing, root cause analysis, and diagnostic tool creation.
"""
import asyncio
import os
import sys
import subprocess
import time
import re
from typing import List, Optional, Dict

from agentic_core.agents.base import SubAtomicAgent
from apps_shared.utils.text_processing import clean_llm_code

# Optional AutoGen import for collective repair
try:
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
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
        await asyncio.sleep(0)
        
        if not self.last_failure:
            print(f"   ⚠️  No failure context available")
            return
        
        await self._analyze_failure(self.last_failure)

    async def _analyze_failure(self, failure_info: dict):
        if not self.ctx.intelligence_enabled:
            return

        print(f"   🔍 Analyzing failure in {failure_info['test_file']}")
        
        # 1. Read files
        primary = failure_info['modified_file']
        # Extract error file from traceback or default to primary
        error_file = self._extract_error_file(failure_info['traceback']) or primary
        
        files_content = {}
        for fpath in [primary, error_file]:
            if fpath and os.path.exists(fpath):
                files_content[fpath] = self.ctx.get_file_content(fpath)

        # 2. Formulate Prompt
        prompt = f"""
ROOT CAUSE ANALYSIS:
Test File: {failure_info['test_file']}
Modified File: {primary}
Traceback:
{failure_info['traceback'][:2000]}

Context:
{files_content.get(primary, '')[:2000]}

Task: Identify the root cause and provide a fixed version of {primary}.
Return ONLY the python code for {primary}.
"""
        # 3. Request Fix
        # If AutoGen is available, we could use conversational_repair here.
        # For now, we use the resilient mutation capability.
        fix = await self.ctx.resilient_mutation(self.name, prompt, code=files_content.get(primary, ""))
        
        if fix and fix != files_content.get(primary, ""):
            print(f"   🕵️ Sherlock proposing fix for {primary}")
            if self.ctx.write_compliant_file(primary, fix):
                self.ctx.modified_files.add(primary)
                print(f"   ✅ Fix Applied")

    def _extract_error_file(self, traceback: str) -> Optional[str]:
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
        if self.ctx.modified_files:
            for mod_file in self.ctx.modified_files:
                test_file = self._find_test_file(mod_file)
                if test_file: target_tests.add(test_file)
        
        if not target_tests:
            # If no specific tests found for mods, run all (or skip if preferred)
            # For safety in this refactor, let's skip if no specific targets to save time,
            # unless a signal forces it.
            if "TEST_FAILURE" not in self.ctx.signals:
                print("   ✅ No specific tests to run.")
                return

        # 2. Run Tests
        for test_file in target_tests:
            success = await self._run_test(test_file)
            if not success:
                self.ctx.signals.add("TEST_FAILURE")
                
    def _find_test_file(self, source_file: str) -> Optional[str]:
        # Simple heuristic mapping
        base = os.path.basename(source_file).replace('.py', '')
        candidates = [
            f"tests/test_{base}.py",
            f"tests/{base}_test.py",
            f"tests/shared/test_{base}.py"
        ]
        for c in candidates:
            if os.path.exists(c): return c
        return None

    async def _run_test(self, test_file: str) -> bool:
        print(f"   🚀 Running {test_file}...")
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pytest", test_file, "-v", "--tb=short",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            print(f"   ❌ Test Failed: {test_file}")
            traceback = stdout.decode() + stderr.decode()
            
            # Trigger Sherlock if available
            if self.sherlock_ref:
                # Assuming first modified file is the culprit for simplicity in this flow
                primary_mod = list(self.ctx.modified_files)[0] if self.ctx.modified_files else "unknown.py"
                self.sherlock_ref.trigger_investigation(primary_mod, test_file, traceback)
                # Execute Sherlock immediately to fix it
                await self.sherlock_ref.execute()
            return False
        
        print(f"   ✅ Test Passed: {test_file}")
        return True


class ToolsmithAgent(SubAtomicAgent):
    """
    ROLE: Dynamic Agency. Creates diagnostic scripts to probe systemic failures.
    """
    async def execute(self):
        # Only run if tests are failing and standard fixes failed
        if "TEST_FAILURE" not in self.ctx.signals:
            return

        print(f"\n[>>>] {self.name} ACTIVATED: Forging diagnostic tools...")
        
        prompt = """
        Create a standalone Python script to diagnose the current environment.
        Check: imports, python version, and disk space.
        Return ONLY Python code.
        """
        tool_code = await self.ctx.resilient_mutation(self.name, prompt)
        
        if tool_code:
            tool_path = f"scripts/diag_{int(time.time())}.py"
            if self.ctx.write_compliant_file(tool_path, tool_code):
                print(f"   🛠️  Tool Forged: {tool_path}")
