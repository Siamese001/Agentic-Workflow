"""Types and models for context_curator."""

from dataclasses import dataclass, field
from enum import Enum

class ContextPriority(Enum):
    """Priority levels for context chunks."""
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

class ContextType(Enum):
    """Types of context chunks."""
    SYSTEM_INSTRUCTION = 'system_instruction'
    SAFETY_POLICY = 'safety_policy'
    TASK_DESCRIPTION = 'task_description'
    CONVERSATION_HISTORY = 'conversation_history'
    RETRIEVED_KNOWLEDGE = 'retrieved_knowledge'
    TOOL_DOCUMENTATION = 'tool_documentation'
    EXAMPLE = 'example'

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
        return {'id': self.id, 'content': self.content, 'chunk_type': self.chunk_type.value, 'priority': self.priority.value, 'token_count': self.token_count, 'relevance_score': self.relevance_score, 'pinned': self.pinned, 'metadata': self.metadata}

@dataclass
class ContextWindow:
    """Managed context window."""
    chunks: List[ContextChunk]
    total_tokens: int
    max_tokens: int
    pinned_tokens: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'chunks': [c.to_dict() for c in self.chunks],
            'total_tokens': self.total_tokens,
            'max_tokens': self.max_tokens,
            'pinned_tokens': self.pinned_tokens,
            'available_tokens': self.max_tokens - self.total_tokens}
