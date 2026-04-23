"""Publisher adapter — routes apps_eval results onto the canonical
MetaLearningBus FIFO singleton.

Prior state (per plan W1/W2 evidence):
    - `apps_eval` had exactly one import edge into `system_learning`
      (`regression_detector → get_sl_memory_bridge`) — a memory bridge,
      NOT a bus publish path.
    - No eval engine published scorecards, regression verdicts, or HITL
      decision-quality reports to either MetaLearningBus implementation.

This module fixes that by giving every eval engine a single import
point to hand results to the canonical process-level bus:

    from apps_eval.integrations.meta_bus_publisher import publish_eval_outcome
    publish_eval_outcome(kind="scorecard", payload=scorecard.model_dump())

The adapter is **additive**: it never mutates existing bus state; it only
enqueues fresh :class:`MetaLearningChangePackage` instances that downstream
drainers can pick up.

Design constraints
------------------
1. **Fail-open**: if the canonical bus import fails (e.g., in a minimal
   test env), we log and return a stub receipt — eval runs must never
   break because a bus is unavailable.
2. **Deterministic package hashing**: delegated to
   ``MetaLearningChangePackage.create`` which already performs
   sort-keyed SHA-256 hashing.
3. **No wall-clock dependency**: callers pass ``trace_id`` (or we mint a
   uuid4) — timestamps are the bus's concern.
4. **Single responsibility**: this adapter only normalises + publishes.
   It does NOT invoke downstream pipeline stages, apply functions, or
   trigger drain.

Plan reference: `.windsurf/plans/eval-meta-otel-gap-review-ef4a20.md`
Wave W2 (eval → bus wiring).
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Canonical outcome kinds (stable wire identifiers)
# ----------------------------------------------------------------------

KIND_SCORECARD = "eval.scorecard"
KIND_SUITE = "eval.suite"
KIND_REGRESSION = "eval.regression"
KIND_HITL_QUALITY = "eval.hitl_decision_quality"
KIND_RETRIEVAL = "eval.retrieval"
KIND_SCENARIO_BATCH = "eval.scenario_batch"


@dataclass(frozen=True)
class PublishReceipt:
    """Receipt returned from :func:`publish_eval_outcome`.

    ``ok`` is False when the canonical bus was unavailable and the call
    degraded to a log-only no-op. Callers SHOULD NOT use this as a retry
    signal — a degraded publish means the bus itself is misconfigured
    and will fail for subsequent calls too.
    """

    ok: bool
    kind: str
    trace_id: str
    package_hash: str


def _try_get_process_bus() -> Any | None:
    """Return the canonical process-level MetaLearningBus singleton, or None.

    Import is guarded because in a minimal test env the full
    `system_learning` tree may not be importable.
    """
    try:
        # guardian: allow-cross-layer-import -- apps_eval -> system_learning is the
        # documented publisher boundary (plan eval-meta-otel-gap-review-ef4a20 W2).
        # Kept lazy + fail-open so eval never hard-depends on system_learning.
        from system_learning.meta_learning.meta_learning_bus import get_process_bus

        return get_process_bus()
    except ImportError as exc:  # pragma: no cover - minimal env
        logger.info("meta_bus_publisher: canonical bus unavailable (%s)", exc)
        return None


def _try_build_package(trace_id: str, kind: str, payload: dict[str, Any]) -> Any | None:
    """Construct a MetaLearningChangePackage. Returns None on import error."""
    try:
        # guardian: allow-cross-layer-import -- see _try_get_process_bus rationale
        from system_learning.meta_learning.meta_learning_bus import (
            MetaLearningChangePackage,
        )

        return MetaLearningChangePackage.create(trace_id=trace_id, kind=kind, payload=payload)
    except ImportError as exc:  # pragma: no cover
        logger.info("meta_bus_publisher: change-package class unavailable (%s)", exc)
        return None


def publish_eval_outcome(
    *,
    kind: str,
    payload: dict[str, Any],
    trace_id: str | None = None,
) -> PublishReceipt:
    """Publish an evaluation outcome onto the canonical meta-learning bus.

    Args:
        kind: Outcome kind — use one of the ``KIND_*`` module constants.
        payload: JSON-serialisable outcome dictionary. Any
            :class:`pydantic.BaseModel` caller should pass
            ``.model_dump()`` (or ``.dict()`` for v1).
        trace_id: Optional caller-supplied trace id. When omitted we mint
            a fresh uuid4.

    Returns:
        :class:`PublishReceipt` documenting what was published. ``ok``
        is False when the bus import failed and the call degraded to a
        log-only no-op.

    Emits:
        Adds one :class:`MetaLearningChangePackage` to the canonical
        process-level FIFO queue. Downstream consumers (bus drainers /
        apply_next / process_traces) are unaffected.
    """
    if not kind:
        raise ValueError("meta_bus_publisher: kind is required")
    if not isinstance(payload, dict):
        raise TypeError(
            "meta_bus_publisher: payload must be a dict, got %s" % type(payload).__name__,
        )

    final_trace_id = trace_id or str(uuid.uuid4())

    pkg = _try_build_package(final_trace_id, kind, payload)
    if pkg is None:
        logger.warning(
            "meta_bus_publisher: degraded publish (package unavailable) kind=%s trace_id=%s",
            kind,
            final_trace_id,
        )
        return PublishReceipt(ok=False, kind=kind, trace_id=final_trace_id, package_hash="")

    bus = _try_get_process_bus()
    if bus is None:
        logger.warning(
            "meta_bus_publisher: degraded publish (bus unavailable) kind=%s trace_id=%s hash=%s",
            kind,
            final_trace_id,
            pkg.package_hash,
        )
        return PublishReceipt(ok=False, kind=kind, trace_id=final_trace_id, package_hash=pkg.package_hash)

    try:
        bus.enqueue(pkg)
    except (AttributeError, TypeError, RuntimeError) as exc:
        logger.warning(
            "meta_bus_publisher: enqueue failed kind=%s trace_id=%s err=%s",
            kind,
            final_trace_id,
            exc,
        )
        return PublishReceipt(ok=False, kind=kind, trace_id=final_trace_id, package_hash=pkg.package_hash)

    logger.info(
        "meta_bus_publisher: published kind=%s trace_id=%s hash=%s",
        kind,
        final_trace_id,
        pkg.package_hash,
    )
    return PublishReceipt(ok=True, kind=kind, trace_id=final_trace_id, package_hash=pkg.package_hash)


__all__ = [
    "KIND_HITL_QUALITY",
    "KIND_REGRESSION",
    "KIND_RETRIEVAL",
    "KIND_SCENARIO_BATCH",
    "KIND_SCORECARD",
    "KIND_SUITE",
    "PublishReceipt",
    "publish_eval_outcome",
]
