# W5 PA/Judge Graph Binding Materiality Receipt

Date: 2026-06-07

Plan: graph-skills-quality-enhancement-c4e8a1

## Scope

W5 routes graph binding materiality into shared prompt assembly and judge packet surfaces for apps_rg generated resume sections.

## Changes

- Added `build_graph_binding_materiality_summary` in `apps_rg/runtime/graph_skills_utilization_scorer.py`.
- Added `GRAPH_BINDING_MATERIALITY_SUMMARY` to PA compiled prompts through `apps_rg/runtime/dispatch/input_authority_prompt_block.py`.
- Added `graph_binding_materiality_summary` and `metadata_only_graph_context_is_insufficient` to generic grade-only judge packets in `apps_rg/runtime/judges/grade_only_judge_packet.py`.
- Added the same materiality packet surface to executive-summary judge packets in `apps_rg/runtime/judges/executive_summary_judge_packet.py`.
- Added optional passthrough parameters to `apps_rg/runtime/judges/policy_backed_section_judges.py`.

## Contract

The summary is compact deterministic JSON:

- `PENDING_CANDIDATE_OUTPUT` at PA time when graph metadata exists before generation.
- `PASS` when native C0.3 facts and/or role-episode bundle bindings are materially cited by candidate output or claim ledger.
- `FAIL` when graph metadata exists but the candidate is metadata-only and does not cite/use corresponding facts, role bundles, or graph skill IDs.
- `NO_GRAPH_BINDING_METADATA` when no native C0.3 or role-episode metadata is present.

## ADG

ADG MCP was unavailable during W5 (`Transport closed`). Static repo inspection was used as the fallback.

## Verification

Command:

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/unit/apps_rg/test_graph_binding_materiality_w5.py tests/unit/apps_rg/test_section_judge_policy.py tests/unit/apps_rg/test_targeting_binding_parity_w3.py tests/unit/apps_rg/test_x1d_judge_transport_parity.py -q -o addopts=
```

Result:

```text
63 passed, 4 warnings
```
