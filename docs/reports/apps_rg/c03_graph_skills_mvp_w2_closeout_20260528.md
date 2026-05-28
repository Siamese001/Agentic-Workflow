# C0.3 Graph-Skills MVP — W2 Closeout (2026-05-28)

Plan: `c03-graph-skills-mvp-b4f9a2`

## Shipped

| Seam | Change |
|------|--------|
| Judge packet | Per-fact `graph_proof_refs` (`claim_support_graph_refs` + `source_resume_files`) and `executive_capability_phrases` via `enrich_allowed_fact_packet_for_judges` + `graph_bindings` from FEC bridge |
| Rubric | `GRADE_ONLY_INSTRUCTION` + `GRAPH_ONLY_GRADE_ONLY_RUBRIC` authorize graph_proof_refs union grading |
| SQLite projection | `resolve_role_family_projection` parses `targeting_keywords`, `track_weight_profile`, `proof_policy_note` |
| PA prompt | `GRAPH_TARGETING_KEYWORDS=` line in `format_evidence_capsule_c0_block` |
| X2 alignment | `enrich_parsed_for_x2` passes `briefing_text` + `briefing_source=RUN_SPECIFIC` into `merge_graph_targeting_jd_alignment` |

## Runtime proof

- Run: [exec_summary_20260528_102651](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260528_102651)
- `PRODUCT_STATUS`: X3_ALLOW
- `x1d_anthropic_claude` score: 4.0
- `executive_summary_judge_packet_post_x2.json`: `graph_proof_refs` populated (e.g. `fact_consulting_001`)
- `x2_gate_outputs.json`: `briefing_targeting_supplement` non-empty
- `compiled_prompt.txt`: contains `GRAPH_TARGETING_KEYWORDS` and `GRAPH_TARGETING_FOR_PA`

## Audit tool follow-up (ARCH-G2)

`tools/cursor/audit_c01_c07_graph_skills_apps_rg.py` does not yet verify per-signal consumption (`graph_proof_refs`, `targeting_keywords`, `briefing_targeting_supplement`). Add checks in a follow-up plan `c03-audit-depth-*`.

## Tests

```bash
python -m pytest tests/unit/apps_rg/test_c03_graph_skills_mvp.py tests/unit/apps_rg/test_executive_summary_judge_packet_display_override.py -q -p pytest_timeout
```

12 passed (2026-05-28).
