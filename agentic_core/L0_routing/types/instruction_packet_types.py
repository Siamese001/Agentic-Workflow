"""Instruction Packet Types - Stub implementation for test compatibility."""
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class InstructionPacket:
    """Instruction packet."""
    packet_id: str = ""
    instruction: str = ""
    context: Dict[str, Any] = None
    metadata: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None
    path: Optional[str] = None
    intent_class: Optional[str] = None
    prompt: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    required_mixins: Optional[tuple] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class PromptInstructionPacket:
    """Prompt instruction packet."""
    packet_id: str
    prompt: str
    context: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


__all__ = ["InstructionPacket", "PromptInstructionPacket"]
