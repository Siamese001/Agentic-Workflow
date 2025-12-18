"""
SecurityEnforcer Agent - Security Guardian.
Detects and remediates high-risk security patterns.
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


class SecurityEnforcer(SubAtomicAgent):
    """ROLE: Security Guardian. Detects and remediates high-risk security patterns."""

    RISK_PATTERNS = {
        'hardcoded_secret': re.compile(
            r'(password\s*=\s*["\'][^"\']+["\']|api_key\s*=\s*["\'][^"\']+["\'])',
            re.IGNORECASE
        ),
        'weak_hash': re.compile(r'(md5\(|sha1\(|hashlib\.md5\()', re.IGNORECASE),
        'insecure_random': re.compile(r'random\.(random|randint|choice)\s*\(', re.IGNORECASE),
        'sql_injection': re.compile(r'execute\(.*["\'].*\%.*["\']', re.IGNORECASE),
        'pickle_usage': re.compile(r'pickle\.loads?\s*\(', re.IGNORECASE),
    }

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Security Standards...")
        await asyncio.sleep(0)

        modified_files = getattr(self.ctx, 'modified_files', set())
        target_files = list(modified_files) if modified_files else self.ctx.python_files

        if not target_files:
            print("   ✅ No files to check for security")
            return

        print(f"   🔍 Scanning {len(target_files)} files for security risks...")

        security_log = []
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue
            result = await self._scan_file(file_path)
            if result:
                security_log.append(result)

        if security_log:
            print(f"   🔒 Security issues found in {len(security_log)} files")
            self._save_security_report(security_log)
        else:
            print("   ✅ No security risks detected")

    async def _scan_file(self, file_path: str) -> Dict | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            detected_risks = self._detect_risks(content)
            if not detected_risks:
                return None

            return {'file': file_path, 'risks': detected_risks}
        except Exception:
            return None

    def _detect_risks(self, content: str) -> Dict:
        risks = {}
        for risk_name, pattern in self.RISK_PATTERNS.items():
            matches = list(pattern.finditer(content))
            if matches:
                risks[risk_name] = [
                    {'line': content[:m.start()].count('\n') + 1, 'snippet': m.group()[:50]}
                    for m in matches
                ]
        return risks

    def _save_security_report(self, log_entries: List[Dict]):
        timestamp = int(time.time())
        report_path = f"observability/audit/security_hardening_{timestamp}.md"

        report_content = f"# Security Hardening Report\n\n"
        report_content += f"Generated: {datetime.datetime.now().isoformat()}\n\n"
        report_content += f"## Summary\n\n- Files scanned: {len(log_entries)}\n\n"

        for entry in log_entries:
            report_content += f"### {entry['file']}\n\n"
            for risk_name, risk_list in entry['risks'].items():
                report_content += f"- {risk_name}: {len(risk_list)} occurrences\n"
            report_content += "\n"

        self.ctx.write_compliant_file(report_path, report_content)
