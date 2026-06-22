# ProceduralPattern:AppsRgCompetenciesGraphTraversalReceipt

- INVARIANT: apps_rg competencies bundle mode must not certify graph-backed competencies without a traversal sufficiency receipt and graph granularity gates.
- scope: apps_rg/runtime/validators/competencies_quality_x2.py, apps_rg/runtime/validators/competencies_x2.py, apps_rg/runtime/sections/competencies_lane_execution.py.
- enforcement: x2_competencies_graph_traversal_sufficiency; x2_competencies_graph_granularity_gates; tests/unit/apps_rg/test_competencies_capability_bundle_wiring.py.
- canonical_pattern: build `competencies_graph_traversal_sufficiency_receipt_v1` from `selected_graph_evidence_plan`, parsed rejected-neighbor audit, JD text, briefing text, and X1D judge rows; write `competencies_graph_traversal_sufficiency_receipt.json`.
- do_not_do: do not accept flat repeated confidence scores or selected-only graph IDs as proof of sufficient traversal.
- discovered: 2026-06-22, validated: 2026-06-22.
