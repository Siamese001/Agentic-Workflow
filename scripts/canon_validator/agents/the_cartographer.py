"""
TheCartographer Agent - Vector Embeddings Manager.
Manages code embeddings for semantic search and memory.
"""

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..base import SubAtomicAgent


class TheCartographer(SubAtomicAgent):
    """
    ROLE: Vector Embeddings Manager.
    Manages code embeddings for semantic search and memory.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Mapping Code Embeddings...")
        await asyncio.sleep(0)

        if not self.ctx.intelligence_enabled:
            print("   ⚠️  Intelligence disabled - skipping embedding generation")
            return

        # Get files to embed (prioritize modified files)
        target_files = list(self.ctx.modified_files) if self.ctx.modified_files else self.ctx.python_files[:50]

        if not target_files:
            print("   ✅ No files to embed")
            return

        print(f"   🗺️  Generating embeddings for {len(target_files)} files...")

        embedded_count = 0
        for file_path in target_files:
            if not file_path.endswith('.py'):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Generate embedding key
                key = f"code_{hash(file_path)}"

                # Upsert embedding
                await self.ctx.upsert_embedding(
                    key=key,
                    text=content[:4000],  # Limit to 4000 chars
                    metadata={'file_path': file_path, 'type': 'code'}
                )
                embedded_count += 1

            except Exception:
                continue

        print(f"   ✅ Embedded {embedded_count} files into vector store")


class TheOmniContext(SubAtomicAgent):
    """
    ROLE: Global Context Manager.
    Maintains a global context of the codebase for cross-file analysis.
    """

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Building Global Context...")
        await asyncio.sleep(0)

        if not self.ctx.intelligence_enabled:
            print("   ⚠️  Intelligence disabled - skipping context building")
            return

        # Build global context from all Python files
        context_parts = []

        for file_path in self.ctx.python_files[:100]:  # Limit to 100 files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract key information
                summary = self._extract_summary(file_path, content)
                if summary:
                    context_parts.append(summary)

            except Exception:
                continue

        # Store global context
        self.ctx.omni_context = "\n".join(context_parts[:50])
        print(f"   ✅ Built global context from {len(context_parts)} files")

    def _extract_summary(self, file_path: str, content: str) -> str:
        """Extract a brief summary of the file."""
        lines = content.split('\n')

        # Get module docstring if present
        docstring = ""
        if lines and lines[0].startswith('"""'):
            for i, line in enumerate(lines):
                if i > 0 and '"""' in line:
                    docstring = '\n'.join(lines[:i+1])
                    break

        # Get class/function names
        import ast
        try:
            tree = ast.parse(content)
            names = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    names.append(f"class {node.name}")
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):
                        names.append(f"def {node.name}")
            return f"{file_path}: {', '.join(names[:5])}"
        except Exception:
            return f"{file_path}: (parse error)"
