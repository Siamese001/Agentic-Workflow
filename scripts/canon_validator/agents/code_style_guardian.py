"""
CodeStyleGuardian Agent - Unified Style & Cleanliness Enforcer.
Merges CodeJanitor (Keys 10-16) and StyleGuardian (Keys 21, 47).
"""

import ast
import asyncio
import os
import re
from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..base import SubAtomicAgent
from ..config import EXCLUDED_DIRS


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
        self.ctx.report(self.name, 10, *self._check_line_length())
        self.ctx.report(self.name, 15, *self._check_magic_numbers())
        self.ctx.report(self.name, 16, *self._check_nesting_depth())

        doc_violations = await self._check_documentation()
        self.ctx.report(self.name, 21, len(doc_violations) == 0, doc_violations)

        naming_violations = await self._check_naming()
        self.ctx.report(self.name, 47, len(naming_violations) == 0, naming_violations)

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
            print(f"      🗑️  Deleted {count} empty files.")

    def _check_line_length(self) -> Tuple[bool, List[str]]:
        """Check for lines exceeding 150 characters."""
        violations = []
        for f in self.ctx.python_files:
            try:
                for i, line in enumerate(open(f, encoding='utf-8'), 1):
                    if len(line.rstrip()) > 150:
                        violations.append(f"{f}:{i}")
            except Exception:
                pass
        return (not violations, violations)

    def _check_magic_numbers(self) -> Tuple[bool, List[str]]:
        """Check for magic numbers in code."""
        violations = []
        allowed = {0, 1, -1, 2, 10, 100, 200, 404, 500, 1000, 0.0, 1.0, 0.5}
        for f in self.ctx.python_files:
            if 'test' in f:
                continue
            try:
                tree = ast.parse(open(f, encoding='utf-8').read())
                for n in ast.walk(tree):
                    if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
                        if n.value not in allowed:
                            violations.append(f"{f}:{n.lineno}")
            except Exception:
                pass
        return (not violations, violations)

    def _check_nesting_depth(self) -> Tuple[bool, List[str]]:
        """Check for excessive indentation (nesting depth)."""
        violations = []
        for f in self.ctx.python_files:
            try:
                for i, line in enumerate(open(f, encoding='utf-8'), 1):
                    if (len(line) - len(line.lstrip())) > 40:
                        violations.append(f"{f}:{i}")
            except Exception:
                pass
        return (not violations, violations)

    def _check_no_trailing_whitespace(self) -> Tuple[bool, List[str]]:
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

    def _check_no_missing_newline(self) -> Tuple[bool, List[str]]:
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

    def _check_no_tabs(self) -> Tuple[bool, List[str]]:
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

    async def _check_documentation(self) -> List[str]:
        """Check for missing module docstrings."""
        violations = []
        for file_path in self.ctx.python_files:
            if 'test_' in file_path or file_path.endswith('__init__.py'):
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                if not ast.get_docstring(tree):
                    violations.append(f"{file_path}: Missing module docstring")
            except Exception:
                pass
        return violations

    async def _check_naming(self) -> List[str]:
        """Check for PascalCase class names."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                            violations.append(
                                f"{file_path}:{node.lineno}: Class '{node.name}' should be PascalCase"
                            )
            except Exception:
                pass
        return violations

    async def propose_style_fix(self, file_path: str, violations: List[str]) -> str:
        """L5+ Use LLM with few-shot to propose style fixes."""
        if not self.ctx.intelligence_enabled:
            return ""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return ""

        violations_summary = "\n".join([f"- {v}" for v in violations[:10]])

        prompt = f"""
{self.ctx.FEW_SHOT_STYLE}

<primary_issues>
{violations_summary}
</primary_issues>

<code_to_fix>
{content[:4000]}
</code_to_fix>

Apply the most relevant example above.
Prioritize:
- Correct isort sections
- Black-compatible line wrapping
- Full type hints
- f-strings
- Google-style docstrings
- PEP8 naming

Preserve all logic and comments.

RESPONSE FORMAT:
Return ONLY the reformatted Python code.
Exact black formatting. No trailing whitespace.
No explanations. No markdown outside code block.
"""

        return await self.ctx.resilient_mutation(
            self.name, prompt, code=content, file_path=file_path, max_attempts=2
        )
