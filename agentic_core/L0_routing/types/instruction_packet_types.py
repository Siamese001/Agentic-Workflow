"""Instruction Packet Types - Stub implementation for test compatibility."""
from dataclasses import dataclass
from typing import Any


@dataclass
class InstructionPacket:
    """Instruction packet."""
    packet_id: str = ""
    instruction: str = ""
    context: dict[str, Any] = None
    metadata: dict[str, Any] | None = None
    trace_id: str | None = None
    path: str | None = None
    intent_class: str | None = None
    prompt: str | None = None
    config: dict[str, Any] | None = None
    required_mixins: tuple | None = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class PromptInstructionPacket:
    """Prompt instruction packet."""
    packet_id: str
    prompt: str
    context: dict[str, Any]
    metadata: dict[str, Any] | None = None


__all__ = ["InstructionPacket", "PromptInstructionPacket"]
