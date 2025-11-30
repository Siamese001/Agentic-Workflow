"""
Long Term Memory Implementation
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import hashlib


@dataclass
class MemorySnapshot:
    """A snapshot of memory state"""
    snapshot_id: str
    data: Dict[str, Any]
    timestamp: datetime
    description: str
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class LongTermMemory:
    """Long term memory implementation with persistence and snapshots"""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path
        self.memory: Dict[str, Any] = {}
        self.snapshots: List[MemorySnapshot] = []
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.metadata: Dict[str, Any] = {
            "version": "1.0",
            "compression": False,
            "encryption": False
        }
        self.stats = {
            "total_sets": 0,
            "total_gets": 0,
            "total_deletes": 0,
            "snapshots_created": 0,
            "snapshots_restored": 0
        }
    
    def set(self, key: str, value: Any, category: str = "default") -> bool:
        """Store a value in long term memory"""
        try:
            # Create a structured memory entry
            memory_entry = {
                "value": value,
                "category": category,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "access_count": 0
            }
            
            self.memory[key] = memory_entry
            self.last_updated = datetime.now()
            self.stats["total_sets"] += 1
            
            # Auto-save if storage path is configured
            if self.storage_path:
                self._save_to_disk()
            
            return True
            
        except Exception:
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from long term memory"""
        if key not in self.memory:
            self.stats["total_gets"] += 1
            return default
        
        memory_entry = self.memory[key]
        memory_entry["access_count"] += 1
        memory_entry["updated_at"] = datetime.now().isoformat()
        
        self.stats["total_gets"] += 1
        return memory_entry["value"]
    
    def delete(self, key: str) -> bool:
        """Delete a value from long term memory"""
        if key in self.memory:
            del self.memory[key]
            self.last_updated = datetime.now()
            self.stats["total_deletes"] += 1
            
            if self.storage_path:
                self._save_to_disk()
            
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in memory"""
        return key in self.memory
    
    def update(self, key: str, value: Any) -> bool:
        """Update an existing value in memory"""
        if key in self.memory:
            memory_entry = self.memory[key]
            memory_entry["value"] = value
            memory_entry["updated_at"] = datetime.now().isoformat()
            self.last_updated = datetime.now()
            
            if self.storage_path:
                self._save_to_disk()
            
            return True
        return False
    
    def get_by_category(self, category: str) -> Dict[str, Any]:
        """Get all memory items by category"""
        result = {}
        for key, entry in self.memory.items():
            if entry.get("category") == category:
                result[key] = entry["value"]
        return result
    
    def get_categories(self) -> List[str]:
        """Get all categories in memory"""
        categories = set()
        for entry in self.memory.values():
            categories.add(entry.get("category", "default"))
        return list(categories)
    
    def search(self, query: str, search_keys: bool = True, search_values: bool = True) -> List[str]:
        """Search memory for items matching query"""
        results = []
        query_lower = query.lower()
        
        for key, entry in self.memory.items():
            match = False
            
            if search_keys and query_lower in key.lower():
                match = True
            
            if search_values:
                value_str = str(entry["value"]).lower()
                if query_lower in value_str:
                    match = True
            
            if match:
                results.append(key)
        
        return results
    
    def create_snapshot(self, description: str = "") -> str:
        """Create a snapshot of current memory state"""
        snapshot_id = hashlib.md5(
            f"{datetime.now().isoformat()}{len(self.memory)}".encode()
        ).hexdigest()[:8]
        
        snapshot = MemorySnapshot(
            snapshot_id=snapshot_id,
            data=self.memory.copy(),
            timestamp=datetime.now(),
            description=description or f"Snapshot {snapshot_id}"
        )
        
        self.snapshots.append(snapshot)
        self.stats["snapshots_created"] += 1
        
        return snapshot_id
    
    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore memory from a snapshot"""
        for snapshot in self.snapshots:
            if snapshot.snapshot_id == snapshot_id:
                self.memory = snapshot.data.copy()
                self.last_updated = datetime.now()
                self.stats["snapshots_restored"] += 1
                
                if self.storage_path:
                    self._save_to_disk()
                
                return True
        return False
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot"""
        for i, snapshot in enumerate(self.snapshots):
            if snapshot.snapshot_id == snapshot_id:
                del self.snapshots[i]
                return True
        return False
    
    def get_snapshots(self) -> List[Dict[str, Any]]:
        """Get all snapshots"""
        return [
            {
                "snapshot_id": s.snapshot_id,
                "description": s.description,
                "timestamp": s.timestamp.isoformat(),
                "data_size": len(s.data)
            }
            for s in self.snapshots
        ]
    
    def clear(self):
        """Clear all memory"""
        self.memory.clear()
        self.last_updated = datetime.now()
        
        if self.storage_path:
            self._save_to_disk()
    
    def _save_to_disk(self):
        """Save memory to disk (mock implementation)"""
        # In a real implementation, this would save to actual file
        pass
    
    def _load_from_disk(self):
        """Load memory from disk (mock implementation)"""
        # In a real implementation, this would load from actual file
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_items": len(self.memory),
            "categories": len(self.get_categories()),
            "snapshots": len(self.snapshots),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "stats": self.stats.copy(),
            "metadata": self.metadata.copy()
        }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get detailed memory information"""
        items = []
        for key, entry in self.memory.items():
            items.append({
                "key": key,
                "category": entry.get("category"),
                "created_at": entry.get("created_at"),
                "updated_at": entry.get("updated_at"),
                "access_count": entry.get("access_count", 0)
            })
        
        return {
            "items": items,
            "snapshots": self.get_snapshots(),
            "stats": self.get_stats()
        }
    
    def export_data(self) -> Dict[str, Any]:
        """Export all memory data"""
        return {
            "memory": self.memory.copy(),
            "snapshots": [
                {
                    "snapshot_id": s.snapshot_id,
                    "data": s.data,
                    "timestamp": s.timestamp.isoformat(),
                    "description": s.description
                }
                for s in self.snapshots
            ],
            "metadata": {
                "created_at": self.created_at.isoformat(),
                "last_updated": self.last_updated.isoformat(),
                "stats": self.stats.copy(),
                "config": self.metadata.copy()
            }
        }
    
    def import_data(self, data: Dict[str, Any]) -> bool:
        """Import memory data"""
        try:
            if "memory" in data:
                self.memory = data["memory"].copy()
            
            if "snapshots" in data:
                self.snapshots = []
                for snapshot_data in data["snapshots"]:
                    snapshot = MemorySnapshot(
                        snapshot_id=snapshot_data["snapshot_id"],
                        data=snapshot_data["data"],
                        timestamp=datetime.fromisoformat(snapshot_data["timestamp"]),
                        description=snapshot_data["description"]
                    )
                    self.snapshots.append(snapshot)
            
            if "metadata" in data:
                metadata = data["metadata"]
                self.created_at = datetime.fromisoformat(metadata["created_at"])
                self.last_updated = datetime.fromisoformat(metadata["last_updated"])
                self.stats = metadata["stats"].copy()
                self.metadata = metadata["config"].copy()
            
            return True
            
        except Exception:
            return False
    
    def __len__(self):
        return len(self.memory)
    
    def __contains__(self, key: str):
        return self.exists(key)
    
    def __str__(self):
        return f"LongTermMemory(items={len(self.memory)}, snapshots={len(self.snapshots)})"
    
    def __repr__(self):
        return self.__str__()
