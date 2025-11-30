"""
Context Profile Configuration

Defines context management parameters and constraints for agentic operations
across the L1-L5 architecture.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class ContextType(str, Enum):
    """Context handling types."""
    CONVERSATION = "conversation"
    DOCUMENT = "document"
    CODE = "code"
    MULTIMODAL = "multimodal"


@dataclass
class ContextProfile:
    """Configuration for context parameters."""
    name: str
    context_type: ContextType = ContextType.CONVERSATION
    max_context_length: int = 4000
    context_window_size: int = 8000
    compression_enabled: bool = True
    semantic_chunking: bool = True
    priority_sections: List[str] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        
        # Set default priority sections based on context type
        if not self.priority_sections:
            if self.context_type == ContextType.CONVERSATION:
                self.priority_sections = ["recent_messages", "user_instructions"]
            elif self.context_type == ContextType.DOCUMENT:
                self.priority_sections = ["introduction", "conclusion", "key_points"]
            elif self.context_type == ContextType.CODE:
                self.priority_sections = ["imports", "main_function", "classes"]
            else:  # MULTIMODAL
                self.priority_sections = ["text_content", "structured_data"]


# Default context profiles
DEFAULT_CONTEXT_PROFILE = ContextProfile(
    name="default",
    context_type=ContextType.CONVERSATION
)

DOCUMENT_CONTEXT_PROFILE = ContextProfile(
    name="document",
    context_type=ContextType.DOCUMENT,
    max_context_length= 8000,
    context_window_size= 16000
)

CODE_CONTEXT_PROFILE = ContextProfile(
    name="code",
    context_type=ContextType.CODE,
    semantic_chunking=True
)

__all__ = [
    "ContextProfile",
    "ContextType",
    "DEFAULT_CONTEXT_PROFILE",
    "DOCUMENT_CONTEXT_PROFILE",
    "CODE_CONTEXT_PROFILE",
]
