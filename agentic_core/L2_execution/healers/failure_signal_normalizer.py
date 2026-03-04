"""Failure Signal Normalizer — compose embedding-ready text from a healing action dict.

Converts a raw healing_action dict (as stored in state_mgr.state["healing_actions"])
into a normalized text string suitable for embedding via BAAI/bge-m3.

Design invariants:
- Pure function: no side effects, no I/O.
- Deterministic: identical inputs always produce identical outputs.
- Stdlib only: no external dependencies.
- Separation of concerns: metadata (territory, agent) is captured separately from
  the text that is embedded — matching the Embedding Lifecycle architecture.
"""

from __future__ import annotations

import hashlib
import math
import struct

_FALLBACK_DIMS = 16
_FALLBACK_TRUNC = 200


def normalize_failure_signal(action: dict) -> str:
    """Compose a normalized embedding-input text from a healing action dict.

    The normalized text encodes the *semantic content* of the failure —
    failure type, the gate that triggered it, the agent that handled it,
    and (when present) the first 200 chars of error_message / stack_trace.
    Territory and other metadata are captured separately (not embedded) per
    the Embedding Lifecycle architecture (territory is metadata, not content).

    Field priority:
      1. failure_type / routing_tier — stable category string (uppercased)
      2. routing_gate   — specific check ID that triggered the failure;
                          more structured and semantic than fix_summary alone
      3. agent          — healer that processed the event
      4. fix_summary    — optional human-readable description of the repair
      5. error_message  — first 200 chars of the raw error message (D1)
      6. stack_trace    — first 200 chars of the exception stack trace (D1)

    Args:
        action: A healing action dict as stored in
            state_mgr.state["healing_actions"].  Expected keys (all
            optional with safe defaults):
              - "type" / "routing_tier": failure category string
              - "routing_gate": specific gate/check identifier (e.g. "gate:import_boundary_check")
              - "agent": healer identifier
              - "fix_summary": human-readable repair description
              - "error_message": raw error string (enrichment field)
              - "stack_trace": exception traceback text (enrichment field)

    Returns:
        A normalized ASCII text string for embedding, e.g.:
        "IMPORT_BOUNDARY_VIOLATION gate:import_boundary_check DependencyRepairAgent yaml config loader"
    """
    failure_type: str = action.get("type") or action.get("routing_tier") or "UNKNOWN"
    routing_gate: str = action.get("routing_gate") or ""
    agent: str = action.get("agent") or "unknown_agent"
    fix_summary: str = action.get("fix_summary") or ""
    error_message: str = str(action.get("error_message") or "")[:_FALLBACK_TRUNC]
    stack_trace: str = str(action.get("stack_trace") or "")[:_FALLBACK_TRUNC]

    parts: list[str] = [failure_type.upper()]
    if routing_gate and routing_gate != "N/A":
        parts.append(routing_gate)
    parts.append(agent)
    if fix_summary:
        parts.append(fix_summary)
    if error_message:
        parts.append(error_message)
    if stack_trace:
        parts.append(stack_trace)

    return " ".join(p.strip() for p in parts if p.strip())


def extract_failure_metadata(action: dict) -> dict:
    """Extract metadata fields that are stored alongside (not embedded into) the vector.

    These fields are stored as metadata in the vector DB record per the
    Embedding Lifecycle architecture: territory, invariant ids, repo context.

    Args:
        action: A healing action dict.

    Returns:
        Dict of metadata fields to store alongside the failure_vector.
    """
    return {
        "territory": action.get("territory", "unknown"),
        "routing_digest": action.get("routing_digest"),
        "confidence_score": action.get("confidence"),
        "routing_tier": action.get("routing_tier", "DETERMINISTIC"),
        "outcome": action.get("outcome", "UNKNOWN"),
        "timestamp": action.get("timestamp"),
    }


def generate_fallback_vector(text: str) -> list[float]:
    """Produce a deterministic 16-dimensional L2-normalised fallback vector.

    Used when bge-m3 is unavailable (BMG_EMBEDDINGS_ENABLED=false) to ensure
    failure_vector is never None. The vector carries no semantic meaning but
    preserves determinism and allows FAISS storage to proceed.

    The vector is tagged with ``vector_source="hash-fallback"`` metadata by
    the caller; downstream novelty/cluster logic MUST NOT interpret it as a
    real semantic embedding (enforced by VectorSourceMismatchError in C3).

    Args:
        text: The normalized failure signal text (output of normalize_failure_signal).

    Returns:
        A 16-dimensional L2-normalised list[float]. Never empty, never None.
        Two consecutive calls with identical text always return identical output.
    """
    digest = hashlib.sha256(text.encode("utf-8", errors="replace")).digest()
    raw: list[float] = []
    for i in range(0, _FALLBACK_DIMS * 2, 2):
        val = struct.unpack_from("<H", digest, i % len(digest))[0]
        raw.append(float(val))
    norm = math.sqrt(sum(v * v for v in raw)) or 1.0
    return [v / norm for v in raw]


__all__ = [
    "normalize_failure_signal",
    "extract_failure_metadata",
    "generate_fallback_vector",
]
