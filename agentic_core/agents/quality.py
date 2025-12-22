from typing import Any, Optional, Protocol, Dict, List

import asyncio
import datetime
import os
import re
import time
from typing import Dict, List

from agentic_core.agents.base import SubAtomicAgent
from agentic_core.domain.constants import EXCLUDED_DIRS


class HygieneGuardian(SubAtomicAgent):
    """
    Unified Hygiene Agent.
    Merges GenerativeGuard (Key 45) and TheCurator (File Taxonomy).
    """

    GENERATIVE_PATTERNS = [
        r"_impl_impl_",
        r"generated_\d+",
        r"auto_\w+_\d+",
        r"temp_\w+_\d+"
    ]

    SCRIPT_CATEGORIES = {
        'maintenance', 'setup', 'migration', 'testing', 'archive'
    }

    IMMUTABLE_FILES = {
        'canon_validator_v2_agentic.py',
        'auto_canon.py',
        'setup.py',
        'README.md',
        'canon_validator_agentic.py'
    }

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Project Hygiene...")
        print(f"   [{self.name}] 🧹 Scanning for generative artifacts and hygiene violations...")
        await asyncio.sleep(0)
        await self._purge_generative_artifacts()
        self.ctx.signals.add("GENERATIVE_CLEAN")
        print(f"   [{self.name}] ✅ Project hygiene enforcement complete")

    async def _purge_generative_artifacts(self):
        violations = []
        for root, dirs, files in os.walk("."):
            if any(x in root for x in EXCLUDED_DIRS):
                continue
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path) and file.endswith('.py'):
                    for pattern in self.GENERATIVE_PATTERNS:
                        if re.search(pattern, file):
                            violations.append(file_path)
                            break

        if violations:
            print(f"   [CLEAN] Found {len(violations)} generative artifacts")
            for file_path in violations:
                try:
                    os.remove(file_path)
                    print(f"      DELETED: {file_path}")
                except Exception as e:
                    print(f"      Failed: {e}")
        else:
            self.ctx.report(self.name, 45, True, [])

    async def propose_hygiene_fix(self, file_path: str, issues: List[str]) -> str:
        """L5+ Use LLM with few-shot to propose hygiene fixes."""
        if not self.ctx.intelligence_enabled:
            return ""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return ""

        issues_summary = "\n".join([f"- {i}" for i in issues[:10]])

        prompt = f"""
{self.ctx.FEW_SHOT_HYGIENE}

<primary_issues>
{issues_summary}
</primary_issues>

<preserve_keywords>__all__, abstractmethod, @override, __init__, __new__, __del__</preserve_keywords>

<code_to_clean>
{content[:4000]}
</code_to_clean>

Apply the most relevant example above.
Prioritize:
- Remove unused imports
- Inline or remove unused variables
- Preserve __all__, abstract methods, dunder
- Simplify redundant boolean logic
- Remove obsolete comments only

Never remove docstrings, type hints, or intentional placeholders.
Be conservative: when in doubt, preserve.

RESPONSE FORMAT:
Return ONLY the cleaned Python code.
No unused imports. No dead variables.
Preserve __all__ and docstrings.
No trailing whitespace.
"""

        return await self.ctx.resilient_mutation(
            self.name, prompt, code=content, file_path=file_path, max_attempts=2
        )


class CodeStyleGuardian(SubAtomicAgent):
    """
    Unified Style & Cleanliness Agent.
    Merges CodeJanitor (Keys 10-16) and StyleGuardian (Keys 21, 47).
    """

    def can_run(self) -> bool:
        return "AST_VALID" in self.ctx.signals

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Code Style & Hygiene...")
        await asyncio.sleep(0)

        self._cleanup_empty_files()

        self.ctx.report(self.name, 11, *self._check_no_trailing_whitespace())
        self.ctx.report(self.name, 12, *self._check_no_missing_newline())
        self.ctx.report(self.name, 13, *self._check_no_tabs())

    def _cleanup_empty_files(self):
        """Remove empty files from the project."""
        count = 0
        for root, _, files in os.walk("."):
            if any(x in root for x in EXCLUDED_DIRS):
                continue
            for file in files:
                p = os.path.join(root, file)
                try:
                    if os.path.getsize(p) == 0:
                        os.remove(p)
                        count += 1
                except Exception:
                    pass
        if count:
            print(f"      Deleted {count} empty files.")

    def _check_no_trailing_whitespace(self):
        """Check for trailing whitespace."""
        violations = []
        for f in self.ctx.python_files:
            try:
                for i, line in enumerate(open(f, encoding='utf-8'), 1):
                    if line.endswith(' \n') or line.endswith('\t\n'):
                        violations.append(f"{f}:{i}")
            except Exception:
                pass
        return (not violations, violations)

    def _check_no_missing_newline(self):
        """Check for missing newline at end of file."""
        violations = []
        for f in self.ctx.python_files:
            try:
                with open(f, 'rb') as file:
                    content = file.read()
                    if content and not content.endswith(b'\n'):
                        violations.append(f)
            except Exception:
                pass
        return (not violations, violations)

    def _check_no_tabs(self):
        """Check for tab characters."""
        violations = []
        for f in self.ctx.python_files:
            try:
                for i, line in enumerate(open(f, encoding='utf-8'), 1):
                    if '\t' in line:
                        violations.append(f"{f}:{i}")
            except Exception:
                pass
        return (not violations, violations)


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
            print("   No files to check for performance")
            return

        print(f"   Analyzing performance in {len(target_files)} files...")

        perf_log = []
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue
            result = await self._scan_file(file_path)
            if result:
                perf_log.append(result)

        if perf_log:
            print(f"   Performance issues found in {len(perf_log)} files")
            self._save_performance_report(perf_log)
        else:
            print("   No performance issues detected")

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
