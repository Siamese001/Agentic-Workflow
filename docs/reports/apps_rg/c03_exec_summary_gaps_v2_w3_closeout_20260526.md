# C03 exec-summary gaps v2 — W3 closeout

**Plan:** [c03-exec-summary-gaps-v2-a8f2e1](../../.cursor/plans/c03-exec-summary-gaps-v2-a8f2e1.md)  
**Wave:** W3 (promotion transparency, DG-1=A preserved)

```text
STATUS: PASS
FILES_CHANGED:
- [c03_promotion_candidates.py](../../apps_rg/runtime/c0/c03_promotion_candidates.py)
- [c03_allowlist_coherence.py](../../apps_rg/runtime/c0/c03_allowlist_coherence.py)
- [proof_pool_resolver.py](../../apps_rg/runtime/proof_pool_resolver.py)
- [graph_skills_run_artifacts.py](../../apps_rg/runtime/graph_skills_run_artifacts.py)
- [executive_summary_lane.py](../../apps_rg/runtime/sections/executive_summary_lane.py)
- [section_spine_terminology.py](../../apps_rg/runtime/section_spine_terminology.py)
- [test_c03_promotion_candidates_w3.py](../../tests/unit/apps_rg/test_c03_promotion_candidates_w3.py)
- [test_exec_summary_c03_allowlist_coherence.py](../../tests/_apps_contract/test_exec_summary_c03_allowlist_coherence.py)
COMMANDS_RUN:
- pytest W3 slice (promotion + allowlist contract + graph artifacts) -> 9 passed
TESTS_GATES:
- tests/unit/apps_rg/test_c03_promotion_candidates_w3.py -> 4 passed
- tests/_apps_contract/test_exec_summary_c03_allowlist_coherence.py -> 3 passed
- tests/unit/apps_rg/test_graph_skills_run_artifacts.py -> 2 passed
ARTIFACTS: NONE (emitted on next exec_summary run as c03_promotion_candidates.json)
REPORTS_GENERATED:
- [c03_exec_summary_gaps_v2_w3_closeout_20260526.md](c03_exec_summary_gaps_v2_w3_closeout_20260526.md)
NOTES:
- promoted_fact_ids remains []; auto_promote_enabled=false. Fresh run dir proof in W5.
```

## W3.1 — `c03_promotion_candidates.json`

- Builder: [`c03_promotion_candidates.py`](../../apps_rg/runtime/c0/c03_promotion_candidates.py) — per filtered neighbor: `track_weight`, `jd_keyword_overlap`, `edge_distance`, `promotion_eligible=false`, `reason=pool_wins_dg1_a`.
- Embedded in `exec_summary_allowlist_receipt` + `proof_pool_metadata.c03_promotion_candidates`.
- Persisted via [`graph_skills_run_artifacts.py`](../../apps_rg/runtime/graph_skills_run_artifacts.py) and early lane write alongside allowlist receipt.

**Next:** W4 hop-path parity (optional/defer) or W5 Brown proof.
