# State management - Functional implementation
from typing import Any, Dict, Optional
from datetime import datetime
import json

# Import the robust state manager we already created
from .rg_state_manager import ResumeStateManager

class StateManager:
    """Functional state manager that delegates to ResumeStateManager."""
    
    def __init__(self):
        self._delegate = ResumeStateManager()
        self._local_cache: Dict[str, Any] = {}

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value with caching."""
        # Check local cache first
        if key in self._local_cache:
            return self._local_cache[key]
        
        # Create a simple memory-based state for backward compatibility
        state_key = f"state_{key}"
        memories = self._delegate.memories
        
        if state_key in memories:
            value = memories[state_key].content.get("value", default)
            self._local_cache[key] = value
            return value
        
        return default

    def set_state(self, key: str, value: Any) -> bool:
        """Set state value with persistence."""
        try:
            # Update local cache
            self._local_cache[key] = value
            
            # Store in episodic memory for persistence
            state_key = f"state_{key}"
            import asyncio
            
            # Create memory content
            memory_content = {
                "key": key,
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "type": "state"
            }
            
            # Store asynchronously if possible, otherwise synchronously
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, create a task
                    asyncio.create_task(
                        self._delegate.store_memory(
                            memory_id=state_key,
                            content=memory_content,
                            episode_type="state",
                            tags=["state", key]
                        )
                    )
                else:
                    # If loop is not running, run synchronously
                    loop.run_until_complete(
                        self._delegate.store_memory(
                            memory_id=state_key,
                            content=memory_content,
                            episode_type="state",
                            tags=["state", key]
                        )
                    )
            except RuntimeError:
                # No event loop available, store directly
                self._delegate.memories[state_key] = type('Memory', (), {
                    'memory_id': state_key,
                    'content': memory_content,
                    'timestamp': datetime.now(),
                    'episode_type': 'state',
                    'tags': ['state', key]
                })()
            
            return True
            
        except Exception:
            # Fallback to local-only storage
            self._local_cache[key] = value
            return False

    def delete_state(self, key: str) -> bool:
        """Delete state value."""
        # Remove from local cache
        if key in self._local_cache:
            del self._local_cache[key]
        
        # Remove from persistent storage
        state_key = f"state_{key}"
        if state_key in self._delegate.memories:
            del self._delegate.memories[state_key]
            return True
        
        return False

    def list_keys(self) -> list:
        """List all state keys."""
        keys = set(self._local_cache.keys())
        
        # Add keys from persistent storage
        for memory_id in self._delegate.memories:
            if memory_id.startswith("state_"):
                key = memory_id[6:]  # Remove "state_" prefix
                keys.add(key)
        
        return list(keys)

    def clear_cache(self) -> None:
        """Clear local cache."""
        self._local_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get state manager statistics."""
        return {
            "cached_keys": len(self._local_cache),
            "persistent_keys": len([k for k in self._delegate.memories.keys() if k.startswith("state_")]),
            "total_keys": len(self.list_keys())
        }
