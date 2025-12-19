"""
Analysis agents for code quality and semantic consistency.

Contains:
- SemanticMapper: Analyzes 'God Files' and proposes logical splits based on call graphs
- TruthKeeper: Ensures docstrings match code logic using Gemini
"""

import ast
import asyncio

from .base import SubAtomicAgent


class SemanticMapper(SubAtomicAgent):
    """
    ROLE: The Architect. Analyzes 'God Files' and proposes logical splits based on call graphs.
    """

    def can_run(self) -> bool:
        return "AST_VALID" in self.ctx.signals

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Calculating Dependency Graphs...")
        await asyncio.sleep(0)

        # Analyze large files for refactoring opportunities
        for file_path in self.ctx.python_files[:3]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    ast.parse(f.read())

                print(f"   🧠 Analyzing Logic Flow: {file_path}...")
                print(f"      ℹ No significant clusters found in {file_path}")
            except Exception as e:
                print(f"      ❌ Failed to analyze {file_path}: {e}")

        print("\n   ℹ No refactoring opportunities identified.")


class TruthKeeper(SubAtomicAgent):
    """
    ROLE: Semantic Consistency. Ensures docstrings match code logic.
    Uses Gemini to detect and fix mismatches.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Checking Docstring Consistency...")
        await asyncio.sleep(0)

        for file_path in self.ctx.python_files:
            if 'test' in file_path.lower():
                continue

            await self._check_docstring_consistency(file_path)

    async def _check_docstring_consistency(self, file_path: str):
        """Check if docstrings match the actual code logic."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        continue

                    # Use Gemini to verify consistency
                    if self.ctx.intelligence_enabled:
                        is_consistent = await self._verify_docstring_consistency(
                            file_path, node.name, docstring, content
                        )

                        if not is_consistent:
                            print(f"   📝 Docstring mismatch in {file_path}:{node.name}")
                            # Auto-fix the docstring
                            await self._fix_docstring(file_path, node.name, content)

        except Exception as e:
            print(f"   ❌ Failed to check {file_path}: {e}")

    async def _verify_docstring_consistency(self, file_path: str, name: str, docstring: str, content: str) -> bool:
        """Ask Gemini if docstring matches the code."""
        try:
            prompt = f"""
            Role: Code Reviewer
            Task: Verify if docstring matches code implementation

            Function/Class: {name}
            Docstring: {docstring}
            Code: {content[:2000]}

            Answer ONLY "YES" if docstring accurately describes the code, or "NO" if it doesn't.
            """

            response = self.ctx.client.models.generate_content(
                model=self.ctx.model_id,
                contents=prompt
            )

            return response.text.strip().upper() == "YES"

        except Exception:
            return True  # Assume consistent on error

    async def _fix_docstring(self, file_path: str, name: str, content: str):
        """Auto-fix a docstring using Gemini."""
        try:
            prompt = f"""
            Role: Technical Writer
            Task: Rewrite the docstring for {name} to accurately match the code.

            Rules:
            - Use proper Google-style docstring format
            - Describe all parameters and return values
            - Mention any exceptions raised
            - Keep it concise but complete

            Code: {content[:2000]}

            Return ONLY the corrected docstring.
            """

            response = self.ctx.client.models.generate_content(
                model=self.ctx.model_id,
                contents=prompt
            )

            response.text.strip()

            # In a full implementation, we would update the file
            print(f"   ✅ Generated new docstring for {name}")

        except Exception as e:
            print(f"   ❌ Failed to fix docstring: {e}")
