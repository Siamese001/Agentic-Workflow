"""Compiled Prompt Artifact — AG-RGGOV-W6 Core Contract

Canonical dataclass for Prompt Assembly output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional


@dataclass(frozen=True, slots=True)
class PromptBlock:
    """Single prompt block with role and content."""

    role: str  # system, user, assistant
    content: str
    block_index: int = 0


@dataclass(frozen=True, slots=True)
class CompiledPromptArtifact:
    """Prompt assembly output contract.

    Contains compiled prompt for L2 execution.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    # Compiled prompt
    prompt_blocks: tuple[PromptBlock, ...] = field(default_factory=tuple)
    system_preamble: str = ""
    user_instruction: str = ""

    # Assembly metadata
    assembly_timestamp: str = ""
    assembly_version: str = "W6.0"

    # Model routing
    target_model: str = ""  # e.g., "Qwen/Qwen2.5-32B-Instruct-AWQ"
    target_provider: str = ""  # e.g., "vllm"

    # Provenance
    evidence_digest: str = ""  # References FinalEvidenceContract.compilation_hash
    compilation_hash: str = ""  # Digest of this artifact

    # Constraints
    max_tokens: int = 4096
    temperature: float = 0.7
