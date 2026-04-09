"""ADG SQLite Materialized View Layer.

Produces 38 physical materialized tables across 4 implementation phases:
    Phase A — Critical path, authority/sovereignty, lifecycle, topology seeds
    Phase B — Capability/egress, tool/agent shape, task-contract/action-safety
    Phase C — Trace/replay/eval, determinism/provenance, exemption/debt
    Phase D — Snapshot baseline + historical regression diffs

Entry point: materialize_all_views(sqlite_path) -> dict[str, int]
"""

from pathlib import Path

from tools.generate.materialized_views.orchestrator import materialize_all_views

__all__ = ["materialize_all_views"]
