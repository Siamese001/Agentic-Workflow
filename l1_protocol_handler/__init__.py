"""
L1 Protocol Handler - Stub module for backwards compatibility.
"""
from typing import Any, Dict, List, Optional


class ProtocolHandler:
    """Handler for L1 protocols."""
    def __init__(self):
        self._handlers = {}
    
    def register(self, protocol: str, handler: callable) -> None:
        self._handlers[protocol] = handler
    
    def handle(self, protocol: str, data: Any) -> Any:
        if protocol not in self._handlers:
            raise ValueError(f"Protocol not found: {protocol}")
        return self._handlers[protocol](data)


__all__ = ['ProtocolHandler']
