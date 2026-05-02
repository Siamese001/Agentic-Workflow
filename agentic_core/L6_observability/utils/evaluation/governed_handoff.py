"""DEPRECATED re-export shim — moved to ops_scripts/reports/governed_handoff.py.

This file is a backward-compatible re-export shim. The canonical module now
lives at ``ops_scripts.reports.governed_handoff`` (layer = L_OPS).

Migration history (l6-gravity-hybrid-7c4e2a W2a · session-burndown-2026-05-02-c8f3a4):
- Original location: agentic_core/L6_observability/utils/evaluation/governed_handoff.py (this file)
- New location: ops_scripts/reports/governed_handoff.py
- Reason: governed_handoff is reporter-class (publishes promotion packets to bus + commit seams).
  Per ADR-095, reporter-class files MUST land at L_OPS, not L6.

90-day deprecation calendar (constitutional §3):
- 2026-05-02: shim authored, consumers continue to work via re-export
- 2026-08-02: shim scheduled for deletion; consumers must migrate by then

Consumer migration path:
    Replace: ``from agentic_core.L6_observability.utils.evaluation.governed_handoff import X``
    With:    ``from ops_scripts.reports.governed_handoff import X``
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "agentic_core.L6_observability.utils.evaluation.governed_handoff is "
    "DEPRECATED (moved to ops_scripts.reports.governed_handoff per ADR-095). "
    "This shim will be removed 2026-08-02. Update imports to use the new path.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the canonical location.
from ops_scripts.reports.governed_handoff import (  # noqa: E402, F401
    BUS_ROLLOUT_SIGNAL,
    GovernedHandoffAgent,
    HandoffRecord,
    ROLLBACK_REQUIRED_KEYS,
    _now_epoch,
    _packet_to_bus_payload,
    _stable_id,
    _validate_rollback_metadata,
)
from ops_scripts.reports.governed_handoff import __all__  # noqa: E402, F401

