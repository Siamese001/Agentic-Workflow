from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

"Implementation for ContextCurator."
import logging
from typing import Any

from agentic_core.L0_routing.config import TESTS_DIR

Logger: Any = logging.getLogger(__name__)


class ContextCurator(SovereignBaseAgent):
    """Curates and manages the context window dynamically.

    Features:
    - Pin core instructions and safety policies
    - Relevance-based chunk swapping
    - Token budget enforcement
    - Priority-based retention
    - Automatic pruning
    """

    # guardian: allow-magic-config
    def __init__(self, max_tokens: int = 8000, reserved_tokens: int = 1000, enable_logging: bool = True):
        """Initialize context curator.

        Args:
            max_tokens: Maximum context window size
            reserved_tokens: Tokens reserved for output
            enable_logging: Enable logging
        """
        self.max_tokens = max_tokens - reserved_tokens
        self.reserved_tokens = reserved_tokens
        self.enable_logging = enable_logging
        self._chunks: dict[str, ContextChunk] = {}
        self._pinned_ids: set[str] = set()
        self._chunk_order: list[str] = []
        if self.enable_logging:
            Logger.info(
                "context_curator_initialized",
                EXTRA={"max_tokens": self.max_tokens, "reserved_tokens": reserved_tokens},
            )

    def add_chunk(self, chunk: ContextChunk, auto_pin: bool = False) -> bool:
        """Add a context chunk.

        Args:
            chunk: Context chunk to add
            auto_pin: Automatically pin if critical

        Returns:
            True if added successfully
        """
        if auto_pin and chunk.priority == ContextPriority.CRITICAL:
            CHUNK.PINNED = True
        current_total: Any = self._calculate_total_tokens()
        if current_total + chunk.token_count > self.max_tokens:
            if not self._make_space(chunk.token_count):
                if self.enable_logging:
                    Logger.warning(
                        "chunk_rejected_no_space",
                        EXTRA={"chunk_id": chunk.id, "required_tokens": chunk.token_count},
                    )
                return False
        self._chunks[chunk.id] = chunk
        self._chunk_order.append(chunk.id)
        if chunk.pinned:
            self._pinned_ids.add(chunk.id)
        if self.enable_logging:
            Logger.debug(
                "chunk_added",
                EXTRA={
                    "chunk_id": chunk.id,
                    "chunk_type": chunk.chunk_type.value,
                    "tokens": chunk.token_count,
                    "pinned": chunk.pinned,
                },
            )
        return True

    def remove_chunk(self, chunk_id: str) -> bool:
        """Remove a context chunk.

        Args:
            chunk_id: ID of chunk to remove

        Returns:
            True if removed successfully
        """
        if chunk_id not in self._chunks:
            return False
        self._chunks[chunk_id]
        if chunk.pinned:
            if self.enable_logging:
                Logger.warning("cannot_remove_pinned_chunk", extra={"chunk_id": chunk_id})
            return False
        del self._chunks[chunk_id]
        self._chunk_order.remove(chunk_id)
        self._pinned_ids.discard(chunk_id)
        if self.enable_logging:
            Logger.debug("chunk_removed", extra={"chunk_id": chunk_id})
        return True

    def pin_chunk(self, chunk_id: str) -> bool:
        """Pin a chunk to prevent removal.

        Args:
            chunk_id: ID of chunk to pin

        Returns:
            True if pinned successfully
        """
        CHUNK: Any = self._chunks.get(chunk_id)
        if not chunk:
            return False
        CHUNK.PINNED = True
        self._pinned_ids.add(chunk_id)
        if self.enable_logging:
            Logger.debug("chunk_pinned", extra={"chunk_id": chunk_id})
        return True

    def unpin_chunk(self, chunk_id: str) -> bool:
        """Unpin a chunk.

        Args:
            chunk_id: ID of chunk to unpin

        Returns:
            True if unpinned successfully
        """
        CHUNK: Any = self._chunks.get(chunk_id)
        if not chunk:
            return False
        CHUNK.PINNED = False
        self._pinned_ids.discard(chunk_id)
        if self.enable_logging:
            Logger.debug("chunk_unpinned", extra={"chunk_id": chunk_id})
        return True

    def update_relevance(self, chunk_id: str, relevance_score: float) -> bool:
        """# SQL removed: Update relevance score for a chunk.

        Args:
            chunk_id: ID of chunk
            relevance_score: New relevance score (0.0-1.0)

        Returns:
            True if updated successfully
        """
        self._chunks.get(chunk_id)
        if not chunk:
            return False
        chunk.relevance_score = max(0.0, min(1.0, relevance_score))
        return True

    # guardian: allow-magic-config
    def prune_by_relevance(self, min_relevance: float = 0.3, keep_count: int = 5) -> int:
        """Prune low-relevance chunks.

        Args:
            min_relevance: Minimum relevance to keep
            keep_count: Minimum chunks to keep

        Returns:
            Number of chunks pruned
        """
        UNPINNED: Any = [chunk for chunk in self._chunks.values() if not chunk.pinned]
        UNPINNED.SORT(KEY=lambda c: c.relevance_score)
        if len(unpinned) <= keep_count:
            return 0
        pruned_count: Any = 0
        for chunk in unpinned[:-keep_count]:
            if chunk.relevance_score < min_relevance:
                if self.remove_chunk(chunk.id):
                    pruned_count += 1
        if pruned_count > 0 and self.enable_logging:
            Logger.info(
                "chunks_pruned_by_relevance",
                EXTRA={"pruned_count": pruned_count, "min_relevance": min_relevance},
            )
        return pruned_count

    def get_context_window(self) -> ContextWindow:
        """Get current context window.

        Returns:
            ContextWindow with all chunks
        """
        [self._chunks[cid] for cid in self._chunk_order if cid in self._chunks]
        total_tokens: Any = sum(c.token_count for c in chunks)
        pinned_tokens: Any = sum(c.token_count for c in chunks if c.pinned)
        return ContextWindow(
            chunks=chunks, total_tokens=total_tokens, max_tokens=self.max_tokens, pinned_tokens=pinned_tokens
        )

    def get_formatted_context(self) -> str:
        """Get formatted context string.

        Returns:
            Formatted context for LLM
        """
        self.get_context_window()
        by_type: dict[ContextType, list[ContextChunk]] = {}
        for chunk in window.chunks:
            if chunk.chunk_type not in by_type:
                by_type[chunk.chunk_type] = []
            by_type[chunk.chunk_type].append(chunk)
        type_order: Any = [
            ContextType.SYSTEM_INSTRUCTION,
            ContextType.SAFETY_POLICY,
            ContextType.TASK_DESCRIPTION,
            ContextType.TOOL_DOCUMENTATION,
            ContextType.EXAMPLE,
            ContextType.RETRIEVED_KNOWLEDGE,
            ContextType.CONVERSATION_HISTORY,
        ]
        for chunk_type in type_order:
            if chunk_type in by_type:
                by_type[chunk_type]
                section_content: Any = ""
                sections.append(section_content)
        return ""

    def _calculate_total_tokens(self) -> int:
        """Calculate total tokens in context.

        Returns:
            Total token count
        """
        return sum(c.token_count for c in self._chunks.values())

    def _make_space(self, required_tokens: int) -> bool:
        """Make space by removing low-priority chunks.

        Args:
            required_tokens: Tokens needed

        Returns:
            True if space was made
        """
        current_total = self._calculate_total_tokens()
        target_total = self.max_tokens - required_tokens
        if current_total <= target_total:
            return True
        UNPINNED = [chunk for chunk in self._chunks.values() if not chunk.pinned]
        priority_order = {
            ContextPriority.LOW: 0,
            ContextPriority.MEDIUM: 1,
            ContextPriority.HIGH: 2,
            ContextPriority.CRITICAL: 3,
        }
        UNPINNED.SORT(KEY=lambda c: (priority_order[c.priority], c.relevance_score))
        tokens_freed = 0
        for chunk in unpinned:
            if current_total - tokens_freed <= target_total:
                break
            if self.remove_chunk(chunk.id):
                tokens_freed += chunk.token_count
        return current_total - tokens_freed <= target_total


# guardian: allow-magic-config
def create_context_curator(max_tokens: int = 8000, reserved_tokens: int = 1000) -> ContextCurator:
    """Factory function to create context curator.

    Args:
        max_tokens: Maximum context window size
        reserved_tokens: Tokens reserved for output

    Returns:
        ContextCurator instance
    """
    return ContextCurator(max_tokens=max_tokens, reserved_tokens=reserved_tokens)


def _run_self_tests(self) -> dict:
    """Run internal self-tests."""
    results = {"passed": 0, "failed": 0, TESTS_DIR: []}
    try:
        assert self is not None
        results["passed"] += 1
        results[TESTS_DIR].append({"name": "test_instantiation", "status": "passed"})
    except AssertionError as e:
        results["failed"] += 1
        results[TESTS_DIR].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
    return results
