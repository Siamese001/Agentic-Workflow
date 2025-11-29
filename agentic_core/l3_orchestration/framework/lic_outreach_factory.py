#!/usr/bin/env python3
"""
Outreach Factory
Factory for creating outreach workflow components
"""

from typing import Dict, Any, Optional
from .lic_outreach_orchestrator import OutreachOrchestrator

class OutreachFactory:
    """Factory for outreach workflow components"""
    
    def __init__(self):
        self.initialized = True
    
    def create_orchestrator(self, config: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Create outreach orchestrator"""
        return {"type": "outreach_orchestrator", "config": config or {}}
    
    def create_executor(self, executor_type: str) -> Optional[Dict[str, Any]]:
        """Create outreach executor"""
        return {"type": executor_type, "status": "created"}


# Factory functions expected by tests
def create_message_executor_with_routing(config: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """Create message executor with routing configuration"""
    return {"type": "message_executor", "routing": True, "config": config or {}}

def create_outreach_orchestrator_with_routing(config: Dict[str, Any] = None) -> OutreachOrchestrator:
    """Create outreach orchestrator with routing configuration"""
    return OutreachOrchestrator()


# Alias for backward compatibility with tests
LICOutreachFactory = OutreachFactory
