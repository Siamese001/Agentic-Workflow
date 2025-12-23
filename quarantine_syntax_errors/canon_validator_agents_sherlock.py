"""
Sherlock Agent - Root Cause Analyst.
Investigates test failures and proposes targeted fixes.
"""

import asyncio
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    pass

from agentic_core..base import SubAtomicAgent


class Sherlock(SubAtomicAgent):
    """
    ROLE: Root Cause Analyst.
    Investigates test failures and proposes targeted fixes.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Investigating Test Failures...")
        await asyncio.sleep(0)

        # Only run if there are test failures
        if "TEST_FAILURE" not in self.ctx.signals:
            print("   ✅ No test failures to investigate")
            return

        # Get failure details from context
        failure_details = self._get_failure_details()

        if not failure_details:
            print("   ⚠️  No failure details available")
            return

        print(f"   🔍 Analyzing {len(failure_details)} test failure(s)...")

        # Analyze each failure
        for failure in failure_details:
            await self._investigate_failure(failure)

    def _get_failure_details(self) -> List[dict]:
        """Extract failure details from context results."""
        failures = []
        for key, result in self.ctx.results.items():
            if not result.get('passed', True):
                details = result.get('details', [])
                if details:
                    failures.append({
                        'key': key,
                        'agent': result.get('agent', 'Unknown'),
                        'details': details[:5]  # Limit to first 5
                    })
        return failures

    async def _investigate_failure(self, failure: dict):
        """Investigate a single test failure."""
        print(f"   🔎 Investigating Key {failure['key']} ({failure['agent']})")

        # Extract file paths from failure details
        affected_files = self._extract_affected_files(failure['details'])

        if not affected_files:
            print(f"      No specific files identified")
            return

        print(f"      Affected files: {len(affected_files)}")

        # Propose fix using LLM if intelligence is enabled
        if self.ctx.intelligence_enabled:
            await self._propose_fix(failure, affected_files)

    def _extract_affected_files(self, details: List[str]) -> List[str]:
        """Extract file paths from failure details."""
        files = []
        for detail in details:
            # Look for file paths in the detail string
            if '.py' in detail:
                parts = detail.split(':')
                if parts and parts[0].endswith('.py'):
                    files.append(parts[0])
        return list(set(files))

    async def _propose_fix(self, failure: dict, affected_files: List[str]):
        """Use LLM to propose a fix for the failure."""
        if not affected_files:
            return

        # Read first affected file
        file_path = affected_files[0]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()[:2000]  # First 2000 chars
        except Exception:
            return

        prompt = f"""
Analyze this test failure and propose a fix.

Key: {failure['key']}
Agent: {failure['agent']}
Details: {failure['details'][:3]}

File content (first 2000 chars):
{content}

Propose a minimal fix. Output format:
FIX: <one-line description>
CONFIDENCE: <low|medium|high>
"""

        try:
            response = await self.ctx.resilient_mutation(
                self.name, prompt, max_attempts=1
            )
            if response:
                print(f"      💡 {response[:200]}...")
        except Exception as e:
            print(f"      ⚠️  Analysis failed: {e}")
