"""ADG SQLite materialized-view layer.

Physical tables are rebuilt in dependency order:

- Phase A — critical path, authority/sovereignty, lifecycle, topology seeds
- Phase B — capability/egress, tool/agent shape, task/action safety
- Phase C — trace/replay/eval, determinism/provenance, exemption/debt
- Phase D — snapshot baseline and historical regression deltas
- Phase E — graph-intelligence approximations inside canonical SQLite
- Phase F — graph-hotspot × measured-coverage risk
- Phase G — confidence-aware repository health and remediation hotspots

Entry point: ``materialize_all_views(sqlite_path) -> dict[str, int]``.
"""

from tools.generate.materialized_views.orchestrator import materialize_all_views

__all__ = ["materialize_all_views"]
