"""L2 execution writers — multi-file edit envelopes and related artifacts.

See ADR-048 (Apply-Patch Multi-File Envelope Format) for the canonical envelope
format. All file writes from this package MUST flow through
``agentic_core.L2_execution.utils.write_gateway`` (UWG SSOT, constitutional §4).
"""

from agentic_core.L2_execution.writers.patch_envelope import (
    AGENT_DELETION_MARKER_PREFIX,
    AddFile,
    ApplyResult,
    DeleteFile,
    Envelope,
    EnvelopeError,
    FileOperation,
    Hunk,
    UpdateFile,
    ValidationError,
    apply_envelope,
    parse_envelope,
    validate_envelope,
)

__all__ = [
    "AGENT_DELETION_MARKER_PREFIX",
    "AddFile",
    "ApplyResult",
    "DeleteFile",
    "Envelope",
    "EnvelopeError",
    "FileOperation",
    "Hunk",
    "UpdateFile",
    "ValidationError",
    "apply_envelope",
    "parse_envelope",
    "validate_envelope",
]
