"""
Runtime Shared Cache - Stub module for backwards compatibility.
"""
from typing import Any, Dict, Optional


class Cache:
    """Simple in-memory cache."""
    def __init__(self):
        self._data: Dict[str, Any] = {}
    
    def get(self, key: str) -> Optional[Any]:
        return self._data.get(key)
    
    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
    
    def delete(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
    
    def clear(self) -> None:
        self._data.clear()


__all__ = ['Cache']
