from __future__ import annotations

"\nPerception Node - Sub-atomic Input Processing\n\nHandles input parsing, context preparation, intent classification,\nand memory retrieval. Isolated from reasoning and action logic.\n"
import asyncio
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class PerceptionNode:
    """
    Sub-atomic perception node - input/context processing.

    Responsibilities:
    - Parse user input
    - Classify intent
    - Retrieve relevant memory
    - Prepare context for reasoning
    """

    def __init__(self):
        """Initialize perception node."""
        self.inputs_processed = 0
        self.cache: dict[str, dict[str, Any]] = {}

    def process(self, raw_input: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Process raw input into perceived state.

        Args:
            raw_input: Raw user input
            context: Current context

        Returns:
            Perceived state with query, intent, memory
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "PerceptionNode.process")

        self.inputs_processed += 1
        query = self._parse_query(raw_input)
        intent = self._classify_intent(query, raw_input)
        relevant_memory = self._retrieve_relevant_memory(query, context)
        perceived = {
            "query": query,
            "intent": intent,
            "relevant_memory": relevant_memory,
            "input_type": raw_input.get("type", "text"),
            "confidence": self._estimate_confidence(query, intent),
        }
        return perceived

    async def process_async(self, raw_input: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """
        Asynchronous input processing.

        Args:
            raw_input: Raw user input
            context: Current context

        Returns:
            Perceived state
        """
        query = await asyncio.to_thread(self._parse_query, raw_input)
        intent = await asyncio.to_thread(self._classify_intent, query, raw_input)
        relevant_memory = await asyncio.to_thread(self._retrieve_relevant_memory, query, context)
        perceived = {
            "query": query,
            "intent": intent,
            "relevant_memory": relevant_memory,
            "input_type": raw_input.get("type", "text"),
            "confidence": self._estimate_confidence(query, intent),
        }
        return perceived

    def _parse_query(self, raw_input: dict[str, Any]) -> str:
        """
        Parse raw input into query string.

        Args:
            raw_input: Raw input

        Returns:
            Parsed query
        """
        if isinstance(raw_input, dict):
            return raw_input.get("user_query", raw_input.get("text", ""))
        return str(raw_input)

    def _classify_intent(self, query: str, raw_input: dict[str, Any]) -> str:
        """
        Classify user intent from query.

        Args:
            query: Parsed query
            raw_input: Raw input

        Returns:
            Intent classification
        """
        query_lower = query.lower()
        if any(word in query_lower for word in ["what", "how", "why", "explain"]):
            return "reasoning"
        elif any(word in query_lower for word in ["do", "execute", "run", "perform"]):
            return "action"
        elif any(word in query_lower for word in ["remember", "recall", "memory"]):
            return "memory"
        else:
            return "general"

    def _retrieve_relevant_memory(self, query: str, context: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Retrieve relevant memory for query.

        Args:
            query: Query string
            context: Current context

        Returns:
            List of relevant memory items
        """
        memory_items = []
        if "memory" in context:
            memory_items = context.get("memory", [])
        return memory_items

    def _estimate_confidence(self, query: str, intent: str) -> float:
        """
        Estimate confidence in perception.

        Args:
            query: Parsed query
            intent: Classified intent

        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.5
        confidence += min(0.3, len(query) / 100.0)
        if intent in ["reasoning", "action", "memory"]:
            confidence += 0.2
        return min(1.0, confidence)

    def get_statistics(self) -> dict[str, Any]:
        """Get perception statistics."""
        return {"inputs_processed": self.inputs_processed, "cache_size": len(self.cache)}
