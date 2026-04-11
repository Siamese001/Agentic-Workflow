"""ADG SQLite Materialized View Layer.

Produces 42 physical materialized tables across 4 implementation phases (Phase A includes mv_handoff_witness_tiers, mv_cross_cutting_witness_tiers, mv_local_heal_first_breaches, mv_observability_interference_breaches):
    Phase A — Critical path, authority/sovereignty, lifecycle, topology seeds
    Phase B — Capability/egress, tool/agent shape, task-contract/action-safety
    Phase C — Trace/replay/eval, determinism/provenance, exemption/debt
    Phase D — Snapshot baseline + historical regression diffs

Entry point: materialize_all_views(sqlite_path) -> dict[str, int]
"""

from pathlib import Path

from tools.generate.materialized_views.orchestrator import materialize_all_views

__all__ = ["materialize_all_views"]
