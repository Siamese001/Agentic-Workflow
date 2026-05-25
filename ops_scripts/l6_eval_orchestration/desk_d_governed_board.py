"""DEPRECATED re-export shim — moved to ops_scripts/reports/desk_d_governed_board.py.

This file is a backward-compatible re-export shim. The canonical module now
lives at ``ops_scripts.reports.desk_d_governed_board`` (layer = L_OPS).

Migration history (l6-gravity-hybrid-7c4e2a W2c · session-burndown-2026-05-02-c8f3a4):
- Original location: agentic_core/L6_observability/utils/engines/desk_d_governed_board.py (this file)
- New location: ops_scripts/reports/desk_d_governed_board.py
- Reason: Desk D Governed Board is reporter-class (processes human decisions -> DPO pairs,
  emits learning reports, feeds RLHF optimizer). Per ADR-095, reporter-class files MUST
  land at L_OPS, not L6.

Path D HITL Meta-Learning preservation:
- The 3 guardian comments added 2026-05-02 (W3) at L3 + L5 HumanDecisionArtifact import
  sites are preserved at the canonical L_OPS path (copy retained them).
- Module-level lifecycle trace emissions (_emit_reads_policy_state, _emit_captures_pattern, etc.)
  fire from the canonical L_OPS file at import time — surface name "desk_d_governed_board"
  remains stable, so meta-learning chain wires correctly.
- Lazy import of system_learning.engines.rlhf_optimizer_impl still deferred inside
  _get_rlhf_optimizer() at canonical path; no L6->L_SL gravity introduced.

90-day deprecation calendar (constitutional §3):
- 2026-05-02: shim authored, consumers continue to work via re-export
- 2026-08-02: shim scheduled for deletion; consumers must migrate by then

Consumer migration path:
    Replace: ``from agentic_core.L6_observability.utils.engines.desk_d_governed_board import X``
    With:    ``from ops_scripts.reports.desk_d_governed_board import X``
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "agentic_core.L6_observability.utils.engines.desk_d_governed_board is "
    "DEPRECATED (moved to ops_scripts.reports.desk_d_governed_board per ADR-095). "
    "This shim will be removed 2026-08-02. Update imports to use the new path.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export full public surface from the canonical location.
from ops_scripts.reports.desk_d_governed_board import (  # noqa: E402, F401
    BoardDecisionType,
    BoardMetrics,
    BoardProcessingResult,
    DeskDGovernedBoard,
    DPOFeedbackRecord,
    get_desk_d_board,
    reset_desk_d_board,
    # Private helpers occasionally used by tests
    _get_rlhf_optimizer,
)
from ops_scripts.reports.desk_d_governed_board import __all__  # noqa: E402, F401
