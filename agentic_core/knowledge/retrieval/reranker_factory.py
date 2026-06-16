"""Reranker factory — env-driven selection between heuristic and cross-encoder.

Canonical entry point for all call sites that need a reranker. Resolves the
``RERANKER`` env var to either the fast heuristic SeniorLibrarianReranker or
an explicitly configured CrossEncoderReranker, then returns
a process-level singleton of the chosen implementation.

Env knob ``RERANKER`` values
----------------------------
* unset / "auto" (default) — heuristic only. Matches historical behavior so
  no existing code path changes output unless the operator opts in.
* "heuristic" — explicit heuristic selection; same as default.
* "cross_encoder" — two-stage chain (heuristic pre-filter + CrossEncoder).
  Requires ``BGE_RERANKER_MODEL`` to be set to a real CrossEncoder model id.
  Falls back to heuristic at runtime if the cross-encoder deps are missing
  (CrossEncoderReranker handles this gracefully via its own fallback path).
* "none" / "off" — returns ``None`` so callers can conditionally skip rerank.

Why env-driven and not config-file-driven
-----------------------------------------
Rerank selection is a runtime knob that differs across deployment contexts:
CI wants heuristic-only (no torch deps pinned), dev boxes want cross-encoder
(GPU available), shadow-eval runs want to flip between both for A/B. An env
var is the least-ceremonious way to express that without plumbing a config
object through every retrieval caller. ADR-046 §Decision item 3 makes this
the canonical selection path.

Thread safety
-------------
Lock-protected singleton init. Each concrete reranker is itself thread-safe
for rerank() calls once constructed.
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Any

from agentic_core.knowledge.retrieval.senior_librarian_reranker import (
    SeniorLibrarianReranker,
)

logger = logging.getLogger(__name__)


_LOCK = threading.Lock()
_HEURISTIC: SeniorLibrarianReranker | None = None
_CROSS_ENCODER: Any | None = None


def _resolve_mode() -> str:
    """Return the normalized mode string from ``RERANKER`` env var.

    Unknown values log a warning and degrade to "heuristic" rather than
    raising — better to keep retrieval running than to crash on a typo.
    """
    raw = os.environ.get("RERANKER", "auto").strip().lower()
    valid = {"auto", "heuristic", "cross_encoder", "none", "off"}
    if raw not in valid:
        logger.warning(
            "Unknown RERANKER mode %r; valid: %s. Falling back to heuristic.",
            raw,
            sorted(valid),
        )
        return "heuristic"
    return raw


def get_reranker() -> Any | None:
    """Return the reranker selected by ``RERANKER`` env, or ``None`` if disabled.

    Return types:
        * SeniorLibrarianReranker — heuristic path
        * CrossEncoderReranker — two-stage chain
        * None — rerank disabled (caller should skip the rerank stage)

    Both non-None return types expose the same ``rerank(query, candidates, top_k)``
    signature so the caller can treat them as interchangeable.
    """
    mode = _resolve_mode()
    if mode in {"none", "off"}:
        return None
    if mode == "cross_encoder":
        return _get_cross_encoder()
    # auto / heuristic / any fallthrough
    return _get_heuristic()


def _get_heuristic() -> SeniorLibrarianReranker:
    """Process-level singleton heuristic reranker."""
    global _HEURISTIC
    if _HEURISTIC is None:
        with _LOCK:
            if _HEURISTIC is None:
                _HEURISTIC = SeniorLibrarianReranker()
    return _HEURISTIC


def _get_cross_encoder() -> Any:
    """Process-level singleton two-stage reranker.

    Lazily imports CrossEncoderReranker to keep torch out of the import
    graph for deployments that never opt into cross-encoder mode.
    """
    global _CROSS_ENCODER
    if _CROSS_ENCODER is None:
        with _LOCK:
            if _CROSS_ENCODER is None:
                from agentic_core.knowledge.retrieval.cross_encoder_reranker import (  # noqa: PLC0415
                    CrossEncoderReranker,
                )

                _CROSS_ENCODER = CrossEncoderReranker()
    return _CROSS_ENCODER


def reset_for_testing() -> None:
    """Clear singletons — test-only helper."""
    global _HEURISTIC, _CROSS_ENCODER
    with _LOCK:
        _HEURISTIC = None
        _CROSS_ENCODER = None


__all__ = ["get_reranker", "reset_for_testing"]
