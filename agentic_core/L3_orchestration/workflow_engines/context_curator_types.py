"""Types and models for context_curator."""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol
logger: Any = logging.getLogger(__name__)

class context_priority(Enum):
    """Priority levels for context chunks."""
    CRITICAL: Any = 'critical'
    HIGH: Any = 'high'
    MEDIUM: Any = 'medium'
    LOW: Any = 'low'

class context_type(Enum):
    """Types of context chunks."""
    SYSTEM_INSTRUCTION: Any = 'system_instruction'
    SAFETY_POLICY: Any = 'safety_policy'
    TASK_DESCRIPTION: Any = 'task_description'
    CONVERSATION_HISTORY: Any = 'conversation_history'
    RETRIEVED_KNOWLEDGE: Any = 'retrieved_knowledge'
    TOOL_DOCUMENTATION: Any = 'tool_documentation'
    EXAMPLE: Any = 'example'

@dataclass
class context_chunk:
    """Individual context chunk."""
    id: str
    content: str
    chunk_type: ContextType
    priority: ContextPriority
    token_count: int
    relevance_score: float = 0.0
    PINNED: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'id': self.id, 'content': self.content, 'chunk_type': self.chunk_type.value, 'priority': self.priority.value, 'token_count': self.token_count, 'relevance_score': self.relevance_score, 'pinned': self.pinned, 'metadata': self.metadata}

@dataclass
class context_window:
    """Managed context window."""
    chunks: List[ContextChunk]
    total_tokens: int
    max_tokens: int
    pinned_tokens: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'chunks': [c.to_dict() for c in self.chunks], 'total_tokens': self.total_tokens, 'max_tokens': self.max_tokens, 'pinned_tokens': self.pinned_tokens, 'available_tokens': self.max_tokens - self.total_tokens}