"""Context Curator for Dynamic Context Window Management.

Phase 3 - Pillar 7: Context Engineering (Dynamic Curation)
Manages context window with pinning, relevance-based swapping, and constraint enforcement.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ContextPriority(Enum):
    """Priority levels for context chunks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ContextType(Enum):
    """Types of context chunks."""
    SYSTEM_INSTRUCTION = "system_instruction"
    SAFETY_POLICY = "safety_policy"
    TASK_DESCRIPTION = "task_description"
    CONVERSATION_HISTORY = "conversation_history"
    RETRIEVED_KNOWLEDGE = "retrieved_knowledge"
    TOOL_DOCUMENTATION = "tool_documentation"
    EXAMPLE = "example"


@dataclass
class ContextChunk:
    """Individual context chunk."""
    id: str
    content: str
    chunk_type: ContextType
    priority: ContextPriority
    token_count: int
    relevance_score: float = 0.0
    pinned: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "chunk_type": self.chunk_type.value,
            "priority": self.priority.value,
            "token_count": self.token_count,
            "relevance_score": self.relevance_score,
            "pinned": self.pinned,
            "metadata": self.metadata,
        }


@dataclass
class ContextWindow:
    """Managed context window."""
    chunks: List[ContextChunk]
    total_tokens: int
    max_tokens: int
    pinned_tokens: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunks": [c.to_dict() for c in self.chunks],
            "total_tokens": self.total_tokens,
            "max_tokens": self.max_tokens,
            "pinned_tokens": self.pinned_tokens,
            "available_tokens": self.max_tokens - self.total_tokens,
        }


class ContextCurator:
    """Curates and manages the context window dynamically.
    
    Features:
    - Pin core instructions and safety policies
    - Relevance-based chunk swapping
    - Token budget enforcement
    - Priority-based retention
    - Automatic pruning
    """
    
    def __init__(
        self,
        max_tokens: int = 8000,
        reserved_tokens: int = 1000,
        enable_logging: bool = True,
    ):
        """Initialize context curator.
        
        Args:
            max_tokens: Maximum context window size
            reserved_tokens: Tokens reserved for output
            enable_logging: Enable logging
        """
        self.max_tokens = max_tokens - reserved_tokens
        self.reserved_tokens = reserved_tokens
        self.enable_logging = enable_logging
        
        self._chunks: Dict[str, ContextChunk] = {}
        self._pinned_ids: Set[str] = set()
        self._chunk_order: List[str] = []
        
        if self.enable_logging:
            logger.info(
                "context_curator_initialized",
                extra={
                    "max_tokens": self.max_tokens,
                    "reserved_tokens": reserved_tokens,
                }
            )
    
    def add_chunk(
        self,
        chunk: ContextChunk,
        auto_pin: bool = False,
    ) -> bool:
        """Add a context chunk.
        
        Args:
            chunk: Context chunk to add
            auto_pin: Automatically pin if critical
            
        Returns:
            True if added successfully
        """
        # Auto-pin critical chunks
        if auto_pin and chunk.priority == ContextPriority.CRITICAL:
            chunk.pinned = True
        
        # Check if fits
        current_total = self._calculate_total_tokens()
        if current_total + chunk.token_count > self.max_tokens:
            # Try to make space
            if not self._make_space(chunk.token_count):
                if self.enable_logging:
                    logger.warning(
                        "chunk_rejected_no_space",
                        extra={
                            "chunk_id": chunk.id,
                            "required_tokens": chunk.token_count,
                        }
                    )
                return False
        
        # Add chunk
        self._chunks[chunk.id] = chunk
        self._chunk_order.append(chunk.id)
        
        if chunk.pinned:
            self._pinned_ids.add(chunk.id)
        
        if self.enable_logging:
            logger.debug(
                "chunk_added",
                extra={
                    "chunk_id": chunk.id,
                    "chunk_type": chunk.chunk_type.value,
                    "tokens": chunk.token_count,
                    "pinned": chunk.pinned,
                }
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
        
        chunk = self._chunks[chunk_id]
        
        # Cannot remove pinned chunks
        if chunk.pinned:
            if self.enable_logging:
                logger.warning(
                    "cannot_remove_pinned_chunk",
                    extra={"chunk_id": chunk_id}
                )
            return False
        
        del self._chunks[chunk_id]
        self._chunk_order.remove(chunk_id)
        self._pinned_ids.discard(chunk_id)
        
        if self.enable_logging:
            logger.debug(
                "chunk_removed",
                extra={"chunk_id": chunk_id}
            )
        
        return True
    
    def pin_chunk(self, chunk_id: str) -> bool:
        """Pin a chunk to prevent removal.
        
        Args:
            chunk_id: ID of chunk to pin
            
        Returns:
            True if pinned successfully
        """
        chunk = self._chunks.get(chunk_id)
        if not chunk:
            return False
        
        chunk.pinned = True
        self._pinned_ids.add(chunk_id)
        
        if self.enable_logging:
            logger.debug(
                "chunk_pinned",
                extra={"chunk_id": chunk_id}
            )
        
        return True
    
    def unpin_chunk(self, chunk_id: str) -> bool:
        """Unpin a chunk.
        
        Args:
            chunk_id: ID of chunk to unpin
            
        Returns:
            True if unpinned successfully
        """
        chunk = self._chunks.get(chunk_id)
        if not chunk:
            return False
        
        chunk.pinned = False
        self._pinned_ids.discard(chunk_id)
        
        if self.enable_logging:
            logger.debug(
                "chunk_unpinned",
                extra={"chunk_id": chunk_id}
            )
        
        return True
    
    def update_relevance(
        self,
        chunk_id: str,
        relevance_score: float,
    ) -> bool:
        """Update relevance score for a chunk.
        
        Args:
            chunk_id: ID of chunk
            relevance_score: New relevance score (0.0-1.0)
            
        Returns:
            True if updated successfully
        """
        chunk = self._chunks.get(chunk_id)
        if not chunk:
            return False
        
        chunk.relevance_score = max(0.0, min(1.0, relevance_score))
        
        return True
    
    def prune_by_relevance(
        self,
        min_relevance: float = 0.3,
        keep_count: int = 5,
    ) -> int:
        """Prune low-relevance chunks.
        
        Args:
            min_relevance: Minimum relevance to keep
            keep_count: Minimum chunks to keep
            
        Returns:
            Number of chunks pruned
        """
        # Get unpinned chunks sorted by relevance
        unpinned = [
            chunk for chunk in self._chunks.values()
            if not chunk.pinned
        ]
        unpinned.sort(key=lambda c: c.relevance_score)
        
        # Keep minimum count
        if len(unpinned) <= keep_count:
            return 0
        
        # Prune low-relevance chunks
        pruned_count = 0
        for chunk in unpinned[:-keep_count]:
            if chunk.relevance_score < min_relevance:
                if self.remove_chunk(chunk.id):
                    pruned_count += 1
        
        if pruned_count > 0 and self.enable_logging:
            logger.info(
                "chunks_pruned_by_relevance",
                extra={
                    "pruned_count": pruned_count,
                    "min_relevance": min_relevance,
                }
            )
        
        return pruned_count
    
    def get_context_window(self) -> ContextWindow:
        """Get current context window.
        
        Returns:
            ContextWindow with all chunks
        """
        chunks = [self._chunks[cid] for cid in self._chunk_order if cid in self._chunks]
        total_tokens = sum(c.token_count for c in chunks)
        pinned_tokens = sum(c.token_count for c in chunks if c.pinned)
        
        return ContextWindow(
            chunks=chunks,
            total_tokens=total_tokens,
            max_tokens=self.max_tokens,
            pinned_tokens=pinned_tokens,
        )
    
    def get_formatted_context(self) -> str:
        """Get formatted context string.
        
        Returns:
            Formatted context for LLM
        """
        window = self.get_context_window()
        
        sections = []
        
        # Group by type
        by_type: Dict[ContextType, List[ContextChunk]] = {}
        for chunk in window.chunks:
            if chunk.chunk_type not in by_type:
                by_type[chunk.chunk_type] = []
            by_type[chunk.chunk_type].append(chunk)
        
        # Format each type
        type_order = [
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
                chunks = by_type[chunk_type]
                section_content = "\n\n".join(c.content for c in chunks)
                sections.append(section_content)
        
        return "\n\n---\n\n".join(sections)
    
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
        
        # Get unpinned chunks sorted by priority and relevance
        unpinned = [
            chunk for chunk in self._chunks.values()
            if not chunk.pinned
        ]
        
        # Sort by priority (low first) then relevance (low first)
        priority_order = {
            ContextPriority.LOW: 0,
            ContextPriority.MEDIUM: 1,
            ContextPriority.HIGH: 2,
            ContextPriority.CRITICAL: 3,
        }
        unpinned.sort(key=lambda c: (priority_order[c.priority], c.relevance_score))
        
        # Remove chunks until space is made
        tokens_freed = 0
        for chunk in unpinned:
            if current_total - tokens_freed <= target_total:
                break
            
            if self.remove_chunk(chunk.id):
                tokens_freed += chunk.token_count
        
        return current_total - tokens_freed <= target_total


def create_context_curator(
    max_tokens: int = 8000,
    reserved_tokens: int = 1000,
) -> ContextCurator:
    """Factory function to create context curator.
    
    Args:
        max_tokens: Maximum context window size
        reserved_tokens: Tokens reserved for output
        
    Returns:
        ContextCurator instance
    """
    return ContextCurator(
        max_tokens=max_tokens,
        reserved_tokens=reserved_tokens,
    )
