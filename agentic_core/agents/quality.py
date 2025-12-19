import asyncio
import os
import re
from typing import List

from agentic_core.agents.base import SubAtomicAgent
from apps_shared.domain.constants import EXCLUDED_DIRS


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
        await asyncio.sleep(0)
        await self._purge_generative_artifacts()
        self.ctx.signals.add("GENERATIVE_CLEAN")

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
            print(f"   🧹 Found {len(violations)} generative artifacts")
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