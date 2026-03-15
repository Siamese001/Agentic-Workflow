from __future__ import annotations

import asyncio

"Brief description of functionality and purpose."
from agentic_core.L2_execution.reasoning.base import SubAtomicAgent

from agentic_core.L0_routing.config.path_constants import DEFAULT_SLEEP
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "OmniContext.execute")

        print(f"\n[>>>] {self.name} ACTIVATED: Building Global Context...")
        await asyncio.sleep(DEFAULT_SLEEP)
        self._build_context_buffer()
        self.ctx.OmniContext = {"buffer": self.context_buffer, "index": self.index, "consult": self.consult}
        print(f"   📚 Built context: {len(self.context_buffer)} chars from {len(self.index)} files")

    def _build_context_buffer(self):
        """Build a concatenated buffer of all Python code."""
        sections = []
        for file_path in self.ctx.python_files:
            if file_path in self.ctx.skip_files:
                continue
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                sections.append(f"\n# FILE: {file_path}\n")
                sections.append(content)
                start_pos = len("".join(sections[:-2]))
                end_pos = start_pos + len(content)
                self.index[file_path] = {"start": start_pos, "end": end_pos, "content": content}
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"   [!]  Failed to read {file_path}: {e}")
        self.context_buffer = "\n".join(sections)

    def consult(self, query: str) -> str:
        """Consult the global context for architectural patterns."""
        if not self.context_buffer:
            return "No context available"
        results = []
        query_lower = query.lower()
        for file_path, info in self.index.items():
            content_lower = info["content"].lower()
            if any(word in content_lower for word in query_lower.split()):
                snippet = info["content"][:500]
                results.append(f"Found in {file_path}:\n{snippet}...\n")
        return "\n".join(results[:3])
