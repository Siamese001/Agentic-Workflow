from __future__ import annotations
"""
Messaging & Communication Schemas
================================
Defines the communication protocols for Sovereign agents. 

This module supports a dual-layer messaging architecture:
1. Sovereign Messaging: High-integrity, immutable handoff models.
2. Residual Messaging: Lightweight, role-based runtime models for LLM compatibility.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from agentic_core.schemas.models.base import SovereignBaseModel

# ==========================================
# Core Message Types
# ==========================================

class MessageType(str, Enum):
    """Canonical message types for agent communication and LLM roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

# ==========================================
# Sovereign Messaging (High-Integrity)
# ==========================================

class AgentMessage(SovereignBaseModel):
    """
    Sovereign-grade message used for inter-agent handoffs.
    Inherits immutability and strict validation from SovereignBaseModel.
    """
    source: str
    destination: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

# ==========================================
# Residual Messaging (Runtime/LLM Compatibility)
# ==========================================

@dataclass
class ResidualAgentMessage:
    """
    Lightweight runtime message format discovered during Phase 2C sweep.
    Maintains compatibility with OpenAI-style role/content structures.
    """
    role: MessageType
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
