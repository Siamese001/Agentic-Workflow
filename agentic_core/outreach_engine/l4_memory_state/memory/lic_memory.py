from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class OutreachMemory:
    """Represents an outreach memory entry."""
    memory_id: str
    content: Dict[str, Any]
    timestamp: datetime
    campaign_id: Optional[str] = None
    recipient_id: Optional[str] = None
    memory_type: str = "generic"

    def __post_init__(self):
        if not self.content:
            self.content = {}

class LICMemory:
    """Minimal functional LIC memory implementation."""

    def __init__(self):
        self.memories: Dict[str, OutreachMemory] = {}
        self.campaign_index: Dict[str, List[str]] = {}
        self.recipient_index: Dict[str, List[str]] = {}

    def process(self, *args, **kwargs) -> Any:
        """Process LIC memory operations."""
        operation = kwargs.get("operation", "status")
        
        if operation == "store":
            return self.store_memory(**kwargs)
        elif operation == "retrieve":
            return self.retrieve_memories(**kwargs)
        elif operation == "delete":
            return self.delete_memory(**kwargs)
        else:
            return {
                "status": "ready",
                "total_memories": len(self.memories),
                "campaigns": len(self.campaign_index),
                "recipients": len(self.recipient_index),
                "processed": True
            }

    def store_memory(self, memory_id: str, content: Dict[str, Any],
                    campaign_id: Optional[str] = None,
                    recipient_id: Optional[str] = None,
                    memory_type: str = "generic") -> Dict[str, Any]:
        """Store a new outreach memory."""
        memory = OutreachMemory(
            memory_id=memory_id,
            content=content,
            timestamp=datetime.now(),
            campaign_id=campaign_id,
            recipient_id=recipient_id,
            memory_type=memory_type
        )
        
        self.memories[memory_id] = memory
        
        # Update indexes
        if campaign_id:
            if campaign_id not in self.campaign_index:
                self.campaign_index[campaign_id] = []
            self.campaign_index[campaign_id].append(memory_id)
        
        if recipient_id:
            if recipient_id not in self.recipient_index:
                self.recipient_index[recipient_id] = []
            self.recipient_index[recipient_id].append(memory_id)
        
        return {
            "status": "stored",
            "memory_id": memory_id,
            "processed": True
        }

    def retrieve_memories(self, campaign_id: Optional[str] = None,
                         recipient_id: Optional[str] = None,
                         memory_type: Optional[str] = None,
                         limit: int = 10) -> Dict[str, Any]:
        """Retrieve memories with optional filtering."""
        candidate_ids = None
        
        if campaign_id and campaign_id in self.campaign_index:
            candidate_ids = set(self.campaign_index[campaign_id])
        
        if recipient_id and recipient_id in self.recipient_index:
            recipient_ids = set(self.recipient_index[recipient_id])
            if candidate_ids is not None:
                candidate_ids &= recipient_ids
            else:
                candidate_ids = recipient_ids
        
        if candidate_ids is None:
            candidate_ids = set(self.memories.keys())
        
        # Apply additional filters
        results = []
        for memory_id in candidate_ids:
            if memory_id in self.memories:
                memory = self.memories[memory_id]
                
                if memory_type and memory.memory_type != memory_type:
                    continue
                
                results.append({
                    "memory_id": memory.memory_id,
                    "content": memory.content,
                    "timestamp": memory.timestamp.isoformat(),
                    "campaign_id": memory.campaign_id,
                    "recipient_id": memory.recipient_id,
                    "memory_type": memory.memory_type
                })
        
        # Sort by timestamp (most recent first) and limit
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "status": "retrieved",
            "memories": results[:limit],
            "count": len(results[:limit]),
            "processed": True
        }

    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Delete a specific memory."""
        if memory_id not in self.memories:
            return {"status": "not_found", "processed": True}
        
        memory = self.memories[memory_id]
        
        # Remove from indexes
        if memory.campaign_id and memory.campaign_id in self.campaign_index:
            self.campaign_index[memory.campaign_id].remove(memory_id)
            if not self.campaign_index[memory.campaign_id]:
                del self.campaign_index[memory.campaign_id]
        
        if memory.recipient_id and memory.recipient_id in self.recipient_index:
            self.recipient_index[memory.recipient_id].remove(memory_id)
            if not self.recipient_index[memory.recipient_id]:
                del self.recipient_index[memory.recipient_id]
        
        # Remove from main storage
        del self.memories[memory_id]
        
        return {
            "status": "deleted",
            "memory_id": memory_id,
            "processed": True
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "total_memories": len(self.memories),
            "campaigns": len(self.campaign_index),
            "recipients": len(self.recipient_index),
            "memory_types": list(set(m.memory_type for m in self.memories.values()))
        }

# Alias for facade import compatibility
OutreachMemoryManager = LICMemory
