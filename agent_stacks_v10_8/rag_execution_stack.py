"""Layer-pure Action/RAG stack wrapper for v10.8."""

from __future__ import annotations

from typing import Any, Dict, Optional

from stacks_v10_7.rag import RAG_SearchAgent


class RAGExecutionStack:
    """RAG wrapper that delegates to the v10.7 conductor."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode
        self._rag_agent = RAG_SearchAgent(context, debug_mode)

    async def run_async(
        self, state: Dict[str, Any], _workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute the v10.7 RAG conductor without altering behavior."""

        return await self._rag_agent.run_async(state)
