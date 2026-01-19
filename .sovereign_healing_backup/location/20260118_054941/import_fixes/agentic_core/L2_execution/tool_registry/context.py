from __future__ import annotations
import asyncio
'''Brief description of functionality and purpose.'''


from agentic_core.L2_execution.ToolRegistry.base import SubAtomicAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)



# NOT_AN_AGENT — context utility class, not a true agent — excluded from agent discovery
class OmniContext(SubAtomicAgent):
    """
    ROLE: Global Architectural Context. Concatenates all non-excluded .py files
    into a single context buffer for agents to consult.
    """

    def __init__(self, context):
        super().__init__(context)
        self.context_buffer = ""
        self.index = {}

    async def execute(self):
                    
        print(f"\n[>>>] {self.name} ACTIVATED: Building Global Context...")
        await asyncio.sleep(0)

        # Build context buffer from all Python files
        self._build_context_buffer()

        # Store in blackboard for other agents to use
        self.ctx.OmniContext = {
            'buffer': self.context_buffer,
            'index': self.index,
            'consult': self.consult
        }

        print(f"   📚 Built context: {len(self.context_buffer)} chars from {len(self.index)} files")

    def _build_context_buffer(self):
        """Build a concatenated buffer of all Python code."""
        sections = []

        for file_path in self.ctx.python_files:
            if file_path in self.ctx.skip_files:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Add file header
                sections.append(f"\n# FILE: {file_path}\n")
                sections.append(content)

                # Store index for quick lookups
                start_pos = len(''.join(sections[:-2]))
                end_pos = start_pos + len(content)
                self.index[file_path] = {
                    'start': start_pos,
                    'end': end_pos,
                    'content': content
                }
            except Exception as e:
                print(f"   [!]  Failed to read {file_path}: {e}")

        self.context_buffer = '\n'.join(sections)

    def consult(self, query: str) -> str:
        """Consult the global context for architectural patterns."""
        if not self.context_buffer:
            return "No context available"

        # Simple keyword-based consultation
        # In a full implementation, this would use semantic search
        results = []
        query_lower = query.lower()

        for file_path, info in self.index.items():
            content_lower = info['content'].lower()
            if any(word in content_lower for word in query_lower.split()):
                # Extract relevant snippet
                snippet = info['content'][:500]
                results.append(f"Found in {file_path}:\n{snippet}...\n")

        return '\n'.join(results[:3])  # Return top 3 results