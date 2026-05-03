"""FEC producer registry — per-app producer of `final_evidence_contract`.

Context
-------
Parent plan `apps-eval-harness-parity-f8d4a2.md` W2.P1/P2 left a hook in
`ExitReviewPacket.final_evidence_contract` but no per-app producers. This
registry is the join point: each grounded app registers a producer that
reads from its run context and returns a FEC-shaped dict. If no producer
is registered for an app, the no-op default returns an empty dict,
preserving the current fail-open behavior.

Usage
-----
At app cert entry, before sealing L2:

    from apps_shared.cert.fec_producer import resolve_fec
    fec = resolve_fec(app_id="apps_qna", run_context=ctx)
    review_packet.final_evidence_contract = fec

Registration (per-app, typically at module import time):

    from apps_shared.cert.fec_producer import register_producer
    register_producer("apps_qna", my_qna_fec_producer)

Authority
---------
READ-ONLY. The registry never mutates run_context. FEC shape is validated
defensively — producers that return non-dict are coerced to empty dict
with a logged warning.

Plan: `.windsurf/plans/apps-eval-harness-residual-a2d9c7.md` W1.P1.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Callable, Dict, Mapping, Optional

Logger = logging.getLogger(__name__)

FecProducer = Callable[[Mapping[str, Any]], Dict[str, Any]]

_LOCK = threading.RLock()
_PRODUCERS: Dict[str, FecProducer] = {}


def _noop_producer(run_context: Mapping[str, Any]) -> Dict[str, Any]:
    """Default producer — returns empty FEC dict.

    Preserves existing fail-open behavior: Exit pipeline's X1D gate already
    treats empty FEC as NOT_APPLICABLE for non-grounded paths.
    """
    _ = run_context  # unused
    return {}


def register_producer(app_id: str, producer: FecProducer) -> None:
    """Register a FEC producer for an app. Last registration wins.

    Args:
        app_id: Canonical app id (e.g. ``"apps_qna"``).
        producer: Callable ``(run_context) -> dict`` returning FEC shape.
    """
    if not isinstance(app_id, str) or not app_id:
        raise ValueError("app_id must be a non-empty string")
    if not callable(producer):
        raise TypeError("producer must be callable")
    with _LOCK:
        _PRODUCERS[app_id] = producer
    Logger.info("[fec_producer] registered producer for app_id=%s", app_id)


def unregister_producer(app_id: str) -> bool:
    """Remove a registered producer. Returns True if a producer was removed."""
    with _LOCK:
        return _PRODUCERS.pop(app_id, None) is not None


def get_producer(app_id: str) -> FecProducer:
    """Return the registered producer for app_id, or the no-op default."""
    with _LOCK:
        return _PRODUCERS.get(app_id, _noop_producer)


def resolve_fec(app_id: str, run_context: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """Resolve FEC for app_id from run_context.

    Defensive: non-dict return values from producers are coerced to empty
    dict with a warning. This preserves Exit pipeline's contract that
    `final_evidence_contract` is always a dict (possibly empty).
    """
    ctx = run_context or {}
    producer = get_producer(app_id)
    try:
        result = producer(ctx)
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        Logger.warning(
            "[fec_producer] producer for app_id=%s raised %s: %s — returning empty FEC",
            app_id,
            type(exc).__name__,
            exc,
        )
        return {}
    if not isinstance(result, dict):
        Logger.warning(
            "[fec_producer] producer for app_id=%s returned non-dict (%s) — coerced to empty",
            app_id,
            type(result).__name__,
        )
        return {}
    return dict(result)


def registered_app_ids() -> tuple[str, ...]:
    """Snapshot of app_ids with registered producers."""
    with _LOCK:
        return tuple(sorted(_PRODUCERS.keys()))


def clear_registry() -> None:
    """Testing hook — clears all registered producers."""
    with _LOCK:
        _PRODUCERS.clear()


__all__ = [
    "FecProducer",
    "clear_registry",
    "get_producer",
    "register_producer",
    "registered_app_ids",
    "resolve_fec",
    "unregister_producer",
]
