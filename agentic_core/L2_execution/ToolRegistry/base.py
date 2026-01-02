from __future__ import annotations
"""Compatibility module - re-exports from ExecutionCanonBaseAgent.

This module provides backward compatibility for imports from 
agentic_core.L2_execution.ToolRegistry.base
"""
from agentic_core.L2_execution.ToolRegistry.ExecutionCanonBaseAgent import *


class SubAtomicAgent:
    """Base class for SubAtomic agents - stub for compatibility."""
    
    def __init__(self, project_root=None, context=None):
        self.project_root = project_root
        self.context = context
    
    async def heal_violation(self, file_path, **kwargs):
        """Stub heal_violation method."""
        return {"healed": False, "reason": "SubAtomicAgent stub"}
    
    def execute(self, **kwargs):
        """Stub execute method."""
        return {"executed": False, "reason": "SubAtomicAgent stub"}
