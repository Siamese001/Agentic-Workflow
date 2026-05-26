# C03 exec-summary gaps v2 — W4 closeout

**Plan:** [c03-exec-summary-gaps-v2-a8f2e1](../../.cursor/plans/c03-exec-summary-gaps-v2-a8f2e1.md)  
**Wave:** W4 (hop-path parity)

```text
STATUS: PASS
FILES_CHANGED:
- [c03_hop_path_materialization.py](../../apps_rg/runtime/c0/c03_hop_path_materialization.py)
- [c03_graphrag_bound.py](../../apps_rg/runtime/c03_graphrag_bound.py)
- [proof_pool_resolver.py](../../apps_rg/runtime/proof_pool_resolver.py)
- [c0_graph_lane_receipt.py](../../apps_rg/runtime/spine/c0_graph_lane_receipt.py)
- [section_spine_terminology.py](../../apps_rg/runtime/section_spine_terminology.py)
- [test_c03_hop_path_w4.py](../../tests/unit/apps_rg/test_c03_hop_path_w4.py)
- [test_exec_summary_c03_allowlist_coherence.py](../../tests/_apps_contract/test_exec_summary_c03_allowlist_coherence.py)
COMMANDS_RUN:
- pytest W4 slice -> 16 passed
TESTS_GATES:
- test_c03_hop_path_w4.py (5) + classification (8) + allowlist contract (3) -> 16 passed
ARTIFACTS: NONE (c0_graph_lane_receipt hop fields on next run)
REPORTS_GENERATED:
- [c03_exec_summary_gaps_v2_w4_closeout_20260526.md](c03_exec_summary_gaps_v2_w4_closeout_20260526.md)
NOTES:
- graph_hop_paths_count now counts materialized hop paths, not incident-edge refs.
- graph_incident_edge_refs_count preserved separately for honesty.
```

## W4.1 — Hop-path materialization

- [`c03_hop_path_materialization.py`](../../apps_rg/runtime/c0/c03_hop_path_materialization.py): `materialize_c03_hop_paths`, `attach_track_weighted_hop_paths_to_c03_bound`.
- Exec-summary proof pool attaches hop paths after pool-wins filter (allowed facts only).
- [`c0_graph_lane_receipt.py`](../../apps_rg/runtime/spine/c0_graph_lane_receipt.py): emits `graph_hop_paths_by_fact_id`, `graph_expansion_mode`, semantics fields.

**Next:** W5 Brown runtime + final closeout.
