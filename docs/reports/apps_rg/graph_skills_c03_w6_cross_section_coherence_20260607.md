# W6 Cross-Section Graph Coherence Receipt

Date: 2026-06-07

Plan: graph-skills-quality-enhancement-c4e8a1

## Scope

W6 adds an aggregate cross-section graph coherence gate for apps_rg generated resume sections. The gate uses the W5 materiality summary contract to evaluate whether native C0.3 and role-episode graph metadata is materially reflected across the assembled resume.

## Changes

- Added `build_cross_section_graph_coherence_receipt` in `apps_rg/runtime/aggregation/cross_section_x2.py`.
- Added `check_cross_section_graph_coherence` and wired it into `run_cross_section_x2_gates`.
- Exported the new helpers from `apps_rg/runtime/aggregation/__init__.py`.
- Added `tests/unit/apps_rg/test_cross_section_graph_coherence_w6.py`.
- Restored the W5 runtime materiality hooks that were absent from the live working tree while the W5 test file was present:
  - `apps_rg/runtime/graph_skills_utilization_scorer.py`
  - `apps_rg/runtime/dispatch/input_authority_prompt_block.py`
  - `apps_rg/runtime/judges/grade_only_judge_packet.py`
  - `apps_rg/runtime/judges/executive_summary_judge_packet.py`
  - `apps_rg/runtime/judges/policy_backed_section_judges.py`

## Gate Behavior

Gate id: `x2_cross_section_graph_coherence`

- `PASS`: active graph metadata is materially used with sufficient breadth across sections and graph skills.
- `WARN`: graph metadata exists but breadth is thin, or a section has metadata-only graph context.
- `WARN` for no graph metadata, to keep this aggregate signal advisory and avoid destabilizing older assembly fixtures.

The gate embeds an `apps_rg.cross_section_graph_coherence_receipt.v1` receipt in `cross_section_x2_gate_outputs.json`.

## ADG

ADG MCP was unavailable during W6 (`Transport closed`). Static repo inspection was used as the fallback.

## Verification

Command:

```text
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/unit/apps_rg/test_graph_binding_materiality_w5.py tests/unit/apps_rg/test_cross_section_graph_coherence_w6.py tests/unit/apps_rg/test_section_judge_policy.py tests/unit/apps_rg/test_targeting_binding_parity_w3.py tests/unit/apps_rg/test_x1d_judge_transport_parity.py -q -o addopts=
```

Result:

```text
66 passed, 4 warnings
```
