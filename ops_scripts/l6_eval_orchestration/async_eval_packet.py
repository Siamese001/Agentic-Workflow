"""DEPRECATED re-export shim — moved to ops_scripts/reports/async_eval_packet.py.

This file is a backward-compatible re-export shim. The canonical module now
lives at ``ops_scripts.reports.async_eval_packet`` (layer = L_OPS).

Migration history (l6-gravity-hybrid-7c4e2a W2b · session-burndown-2026-05-02-c8f3a4):
- Original location: agentic_core/L6_observability/utils/evaluation/async_eval_packet.py (this file)
- New location: ops_scripts/reports/async_eval_packet.py
- Reason: async_eval_packet is reporter-class (queues + seals future-run evaluation packets
  for downstream L6 shadow pipeline + governed_handoff consumption).
  Per ADR-095, reporter-class files MUST land at L_OPS, not L6.

90-day deprecation calendar (constitutional §3):
- 2026-05-02: shim authored, consumers continue to work via re-export
- 2026-08-02: shim scheduled for deletion; consumers must migrate by then

Consumer migration path:
    Replace: ``from agentic_core.L6_observability.utils.evaluation.async_eval_packet import X``
    With:    ``from ops_scripts.reports.async_eval_packet import X``

NOTE: a parallel implementation at ``agentic_core/L3_orchestration/utils/async_eval_packet.py``
exists with diverged shape (ShadowEvalPacket, different ingester semantics). That L3 duplicate
is a SEPARATE SSOT-consolidation issue captured as DEFERRED_SCOPE:
l3-l6-async-eval-packet-consolidation. This W2b shim does NOT touch the L3 duplicate.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "agentic_core.L6_observability.utils.evaluation.async_eval_packet is "
    "DEPRECATED (moved to ops_scripts.reports.async_eval_packet per ADR-095). "
    "This shim will be removed 2026-08-02. Update imports to use the new path.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export full public surface from the canonical location.
from ops_scripts.reports.async_eval_packet import (  # noqa: E402, F401
    # Dataclasses
    AsyncEvalPacket,
    CommitReceipt,
    HumanFeedbackRecord,
    ShadowEvalPacket,
    # Ingester classes
    AsyncEvalIngester,
    ShadowEvalIngester,
    # Singleton accessors
    get_async_eval_ingester,
    get_shadow_eval_ingester,
    reset_async_eval_ingester,
    reset_shadow_eval_ingester,
    # Packet builders / enqueuers
    build_shadow_eval_packet,
    enqueue_shadow_eval_packet,
    ingest_eval_packet,
    # Private helpers / constants (some consumers use these)
    _stable_id,
    _QUEUE_MAXSIZE,
)
from ops_scripts.reports.async_eval_packet import __all__  # noqa: E402, F401
