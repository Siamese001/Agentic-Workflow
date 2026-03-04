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


def normalize_failure_signal(action: dict) -> str:
    """Compose a normalized embedding-input text from a healing action dict.

    The normalized text encodes the *semantic content* of the failure —
    the failure type and the agent that handled it. Territory and other
    metadata are captured separately (not embedded) per the Embedding
    Lifecycle architecture.

    Args:
        action: A healing action dict as stored in
            state_mgr.state["healing_actions"].  Expected keys (all
            optional with safe defaults):
              - "type" / "routing_tier": failure category string
              - "agent": healer identifier
              - "fix_summary": human-readable repair description

    Returns:
        A normalized ASCII text string for embedding, e.g.:
        "IMPORT_BOUNDARY_VIOLATION DependencyRepairAgent yaml config loader"
    """
    failure_type: str = action.get("type") or action.get("routing_tier") or "UNKNOWN"
    agent: str = action.get("agent") or "unknown_agent"
    fix_summary: str = action.get("fix_summary") or ""

    parts = [failure_type.upper(), agent]
    if fix_summary:
        parts.append(fix_summary)

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


__all__ = [
    "normalize_failure_signal",
    "extract_failure_metadata",
]
