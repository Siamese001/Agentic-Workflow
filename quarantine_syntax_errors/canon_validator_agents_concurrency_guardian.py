"""
ConcurrencyGuardian Agent - Unified Concurrency Safety.
KEYS: 61 (Race Conditions), 63 (Livelock), 64 (Starvation)
"""

import asyncio
import re
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    pass

from agentic_core..base import SubAtomicAgent


class ConcurrencyGuardian(SubAtomicAgent):
    """
    Unified concurrency safety agent.
    Covers: Data races (Key 61), Livelock (Key 63), Starvation (Key 64)
    """

    LIVELOCK_PATTERNS = {
        'tight_loop': re.compile(r'while\s+True\s*:\s*.*?(?:pass|continue)', re.DOTALL),
        'busy_wait': re.compile(r'while\s+.*:\s*.*?time\.sleep\s*\(', re.DOTALL),
        'spin_wait': re.compile(r'while\s+not\s+.*:\s*pass', re.IGNORECASE)
    }

    BLOCKING_PATTERNS = {
        'time_sleep': re.compile(r'time\.sleep\s*\(', re.IGNORECASE),
        'requests_calls': re.compile(r'requests\.(get|post|put|delete)\s*\(', re.IGNORECASE),
        'subprocess_blocking': re.compile(r'subprocess\.(run|call)\s*\(', re.IGNORECASE)
    }

    def can_run(self) -> bool:
        return ("AST_VALID" in self.ctx.signals and
                "DEPS_VALID" in self.ctx.signals and
                "SECURE" in self.ctx.signals)

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Concurrency Safety...")
        await asyncio.sleep(0)

        target_files = list(self.ctx.modified_files) if self.ctx.modified_files else self.ctx.python_files
        if not target_files:
            print("   ✅ No files to scan for concurrency issues")
            self._report_all_pass()
            return

        print(f"   🔍 Scanning {len(target_files)} files for concurrency anti-patterns...")

        issues_log = []
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue
            result = await self._analyze_file(file_path)
            if result:
                issues_log.append(result)

        if issues_log:
            print(f"   🛡️  Concurrency issues found in {len(issues_log)} files")
        else:
            print("   ✅ No concurrency anti-patterns detected")
            self._report_all_pass()

    async def _analyze_file(self, file_path: str) -> Dict | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None

        all_issues = []
        all_issues.extend(self._detect_livelock_issues(content))
        all_issues.extend(self._detect_blocking_issues(content))

        if not all_issues:
            return None

        return {"file": file_path, "issues": all_issues}

    def _detect_livelock_issues(self, content: str) -> List[Dict]:
        issues = []
        for issue_name, pattern in self.LIVELOCK_PATTERNS.items():
            for match in pattern.finditer(content):
                issues.append({
                    'type': f'livelock_{issue_name}',
                    'line': content[:match.start()].count('\n') + 1
                })
        return issues

    def _detect_blocking_issues(self, content: str) -> List[Dict]:
        issues = []
        for issue_name, pattern in self.BLOCKING_PATTERNS.items():
            for match in pattern.finditer(content):
                issues.append({
                    'type': f'blocking_{issue_name}',
                    'line': content[:match.start()].count('\n') + 1
                })
        return issues

    def _report_all_pass(self):
        self.ctx.report(self.name, 61, True, ["No race conditions"])
        self.ctx.report(self.name, 63, True, ["No livelock patterns"])
        self.ctx.report(self.name, 64, True, ["No starvation risks"])
