#!/usr/bin/env python3
"""
L4 Memory Injection Bundles
Section 6: Prompt Governance - L4 Memory layer prompt injection bundles
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class MemoryPromptType(str, Enum):
    """Memory prompt injection type enumeration"""
    STATE_RETRIEVAL = "state_retrieval"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    TEMPORAL_CONTEXT = "temporal_context"
    MEMORY_CONSOLIDATION = "memory_consolidation"

@dataclass
class L4MemoryBundle:
    """L4 Memory layer injection bundle"""
    bundle_id: str
    prompt_type: MemoryPromptType
    templates: List[str]
    metadata: Dict[str, Any]
    
    def inject_memory_guidance(self, base_prompt: str, memory_context: Dict[str, Any]) -> str:
        """Inject L4 memory guidance into prompt"""
        guidance = self._generate_memory_guidance(memory_context)
        return f"{base_prompt}\n\nMemory Guidance:\n{guidance}"
    
    def _generate_memory_guidance(self, context: Dict[str, Any]) -> str:
        """Generate memory-specific guidance"""
        if self.prompt_type == MemoryPromptType.STATE_RETRIEVAL:
            return f"State Retrieval: Access relevant {context.get('state_type', 'execution state')} from memory"
        elif self.prompt_type == MemoryPromptType.KNOWLEDGE_GRAPH:
            return f"Knowledge Graph: Query {context.get('graph_entities', 'relevant entities')} and relationships"
        elif self.prompt_type == MemoryPromptType.TEMPORAL_CONTEXT:
            return f"Temporal Context: Consider {context.get('time_range', 'historical context')} and temporal relationships"
        elif self.prompt_type == MemoryPromptType.MEMORY_CONSOLIDATION:
            return f"Memory Consolidation: Integrate new information with existing {context.get('memory_structure', 'knowledge base')}"
        return ""

# Re-export components
__all__ = [
    'L4MemoryBundle', 'MemoryPromptType'
]
