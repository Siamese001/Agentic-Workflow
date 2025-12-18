"""
TheStrategist Agent - Proactive Architecture Analyst.
Identifies code smells and proposes refactors.
"""

import ast
import asyncio
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    pass

from ..base import SubAtomicAgent


class TheStrategist(SubAtomicAgent):
    """
    ROLE: Proactive Architecture. Identifies code smells and proposes refactors.
    Runs only if all other validation phases pass (Phase 10: Optimization).
    """

    def can_run(self) -> bool:
        """Only run if all validations passed."""
        if not self.ctx.results:
            return False
        return all(r.get("passed", False) for r in self.ctx.results.values())

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Analyzing Architectural Patterns...")
        await asyncio.sleep(0)

        if not self.ctx.omni_context:
            print(f"   ⚠️  No global context available - skipping")
            return

        await self._analyze_code_smells()

    async def _analyze_code_smells(self):
        """Identify and propose fixes for code smells."""
        if not self.ctx.intelligence_enabled:
            print(f"   🧠 Intelligence disabled - skipping code smell analysis")
            return

        print(f"   🔍 Scanning for code smells...")

        for file_path in self.ctx.python_files:
            if 'test' in file_path.lower():
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                smells = self._detect_code_smells(file_path, content)

                if smells:
                    await self._propose_refactor(file_path, content, smells)

            except Exception as e:
                print(f"   ❌ Failed to analyze {file_path}: {e}")

    def _detect_code_smells(self, file_path: str, content: str) -> List[str]:
        """Detect various code smells in the content."""
        smells = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # God Class detection
                if isinstance(node, ast.ClassDef):
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if len(methods) > 15:
                        smells.append(f"God Class: {node.name} has {len(methods)} methods")

                    # Large Class detection
                    if hasattr(node, 'end_lineno'):
                        lines = node.end_lineno - node.lineno
                        if lines > 500:
                            smells.append(f"Large Class: {node.name} is {lines} lines")

                # Long Parameter List
                elif isinstance(node, ast.FunctionDef):
                    args = len(node.args.args)
                    if args > 10:
                        smells.append(f"Long Parameter List: {node.name} has {args} params")

                    # Long Method
                    if hasattr(node, 'end_lineno'):
                        lines = node.end_lineno - node.lineno
                        if lines > 100:
                            smells.append(f"Long Method: {node.name} is {lines} lines")

        except Exception:
            pass

        return smells

    async def _propose_refactor(self, file_path: str, content: str, smells: List[str]):
        """Propose a refactoring solution for detected smells."""
        print(f"   📝 Proposing refactor for {file_path}:")
        for smell in smells:
            print(f"      - {smell}")

        prompt = f"""
Role: Senior Architect
Context: Analyzing code for architectural improvements.

File: {file_path}
Code Smells Detected:
{chr(10).join(f"- {s}" for s in smells)}

Task: Propose a refactoring to address these code smells.
Consider design patterns like Strategy, Repository, or Command patterns.

Provide the refactored code in a single Python code block.
"""

        try:
            response = await self.ctx.resilient_mutation(self.name, prompt, max_attempts=1)

            if response:
                # Save proposal
                proposal_file = f"{file_path}.refactor_proposal"
                proposal_content = f"# Refactoring Proposal for {file_path}\n\n"
                proposal_content += f"## Code Smells Detected:\n\n"
                proposal_content += f"{chr(10).join(f'- {s}' for s in smells)}\n\n"
                proposal_content += f"## Proposed Solution:\n\n{response}"

                if self.ctx.write_compliant_file(proposal_file, proposal_content):
                    print(f"   ✅ Refactor proposal saved: {proposal_file}")

        except Exception as e:
            print(f"   ❌ Failed to generate refactor proposal: {e}")
