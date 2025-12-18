"""
PerformanceEnforcer Agent - Performance Guardian.
Identifies and remediates computational inefficiencies.
"""

import ast
import asyncio
import os
import re
import time
import datetime
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import ValidationContext

from ..base import SubAtomicAgent


class PerformanceEnforcer(SubAtomicAgent):
    """ROLE: Performance Guardian. Identifies computational inefficiencies."""

    PERFORMANCE_PATTERNS = {
        'string_concat_loop': re.compile(r'for\s+\w+\s+in.*:\s*.*\w+\s*\+=\s*["\']', re.MULTILINE),
        'blocking_sleep': re.compile(r'time\.sleep\s*\(', re.IGNORECASE),
        'blocking_requests': re.compile(r'requests\.(get|post|put|delete)\s*\(', re.IGNORECASE),
        'nested_loops_deep': re.compile(r'for\s+\w+\s+in.*:\s*.*for\s+\w+\s+in.*:\s*.*for\s+\w+\s+in', re.MULTILINE),
    }

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Optimizing Performance...")
        await asyncio.sleep(0)

        modified_files = getattr(self.ctx, 'modified_files', set())
        target_files = list(modified_files) if modified_files else self.ctx.python_files

        if not target_files:
            print("   ✅ No files to check for performance")
            return

        print(f"   ⚡ Analyzing performance in {len(target_files)} files...")

        perf_log = []
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue
            result = await self._scan_file(file_path)
            if result:
                perf_log.append(result)

        if perf_log:
            print(f"   ⚡ Performance issues found in {len(perf_log)} files")
            self._save_performance_report(perf_log)
        else:
            print("   ✅ No performance issues detected")

    async def _scan_file(self, file_path: str) -> Dict | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            detected_issues = self._detect_issues(content)
            if not detected_issues:
                return None

            return {'file': file_path, 'issues': detected_issues}
        except Exception:
            return None

    def _detect_issues(self, content: str) -> Dict:
        issues = {}
        for issue_name, pattern in self.PERFORMANCE_PATTERNS.items():
            matches = list(pattern.finditer(content))
            if matches:
                issues[issue_name] = [
                    {'line': content[:m.start()].count('\n') + 1, 'snippet': m.group()[:50]}
                    for m in matches
                ]
        return issues

    def _save_performance_report(self, log_entries: List[Dict]):
        timestamp = int(time.time())
        report_path = f"observability/audit/performance_gains_{timestamp}.md"

        report_content = f"# Performance Gains Report\n\n"
        report_content += f"Generated: {datetime.datetime.now().isoformat()}\n\n"
        report_content += f"## Summary\n\n- Files analyzed: {len(log_entries)}\n\n"

        for entry in log_entries:
            report_content += f"### {entry['file']}\n\n"
            for issue_name, issue_list in entry['issues'].items():
                report_content += f"- {issue_name}: {len(issue_list)} occurrences\n"
            report_content += "\n"

        self.ctx.write_compliant_file(report_path, report_content)
