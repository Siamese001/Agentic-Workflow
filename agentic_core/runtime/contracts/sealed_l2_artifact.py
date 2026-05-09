"""Sealed L2 Artifact — AG-RGGOV-W6 Core Contract

Canonical dataclass for L2 execution output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional


@dataclass(frozen=True, slots=True)
class SealedL2Artifact:
    """L2 execution output contract.

    Contains generated content and execution metadata.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    # Execution status
    execution_status: str  # completed, failed, aborted

    # Generated content
    generated_content: str = ""

    # State diff (for apps_rg: resume artifact)
    proposed_state_diff: Mapping[str, Any] = field(default_factory=dict)
    state_diff_authorized: bool = False

    # Execution metadata
    execution_timestamp: str = ""
    execution_duration_ms: int = 0
    sovereign_execution_receipt: str = ""

    # Provenance
    prompt_artifact_digest: str = ""
    contract_version: str = "W6.0"

    # Digest for downstream referencing
    compilation_hash: str = ""
