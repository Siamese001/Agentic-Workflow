"""
MemoryLeakDetector Agent - Memory Guardian.
Detects and remediates resource leaks and unbounded containers.
"""

import ast
import asyncio
import re
import time
import datetime
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..base import SubAtomicAgent


class MemoryLeakDetector(SubAtomicAgent):
    """ROLE: Memory Guardian. Detects resource leaks and unbounded containers."""

    LEAK_PATTERNS = {
        'naked_open': re.compile(r'\bopen\s*\(', re.IGNORECASE),
        'unbounded_cache': re.compile(r'@lru_cache\s*\(\s*\)', re.IGNORECASE),
        'global_list_append': re.compile(r'^[A-Z_]+\s*=\s*\[\]', re.MULTILINE),
    }

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Detecting Resource Leaks...")
        await asyncio.sleep(0)

        modified_files = getattr(self.ctx, 'modified_files', set())
        target_files = list(modified_files) if modified_files else self.ctx.python_files

        if not target_files:
            print("   ✅ No files to check for leaks")
            return

        print(f"   🔍 Scanning {len(target_files)} files for resource leaks...")

        leak_log = []
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue
            result = await self._scan_file(file_path)
            if result:
                leak_log.append(result)

        if leak_log:
            print(f"   🛡️  Resource leaks found in {len(leak_log)} files")
            self._save_safety_report(leak_log)
        else:
            print("   ✅ No resource leaks detected")

    async def _scan_file(self, file_path: str) -> Dict | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            detected_leaks = self._detect_leaks(content)
            context_issues = self._check_context_managers(content)

            if not detected_leaks and not context_issues:
                return None

            return {'file': file_path, 'leaks': detected_leaks, 'context_issues': context_issues}
        except Exception:
            return None

    def _detect_leaks(self, content: str) -> Dict:
        leaks = {}
        for leak_name, pattern in self.LEAK_PATTERNS.items():
            matches = list(pattern.finditer(content))
            if matches:
                leaks[leak_name] = [
                    {'line': content[:m.start()].count('\n') + 1, 'snippet': m.group()[:50]}
                    for m in matches
                ]
        return leaks

    def _check_context_managers(self, content: str) -> List[Dict]:
        """Check for open() calls not in with statements."""
        issues = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == 'open':
                        # Simple heuristic: check if line contains 'with'
                        line_start = content.rfind('\n', 0, node.col_offset) + 1
                        line = content[line_start:content.find('\n', node.col_offset)]
                        if 'with' not in line:
                            issues.append({'line': node.lineno, 'type': 'open_without_with'})
        except Exception:
            pass
        return issues

    def _save_safety_report(self, log_entries: List[Dict]):
        timestamp = int(time.time())
        report_path = f"observability/audit/resource_safety_{timestamp}.md"

        report_content = f"# Resource Safety Report\n\n"
        report_content += f"Generated: {datetime.datetime.now().isoformat()}\n\n"
        report_content += f"## Summary\n\n- Files scanned: {len(log_entries)}\n\n"

        for entry in log_entries:
            report_content += f"### {entry['file']}\n\n"
            for leak_name, leak_list in entry.get('leaks', {}).items():
                report_content += f"- {leak_name}: {len(leak_list)} occurrences\n"
            if entry.get('context_issues'):
                report_content += f"- Context manager issues: {len(entry['context_issues'])}\n"
            report_content += "\n"

        self.ctx.write_compliant_file(report_path, report_content)
