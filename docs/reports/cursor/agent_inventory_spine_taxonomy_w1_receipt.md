# W1 Closeout — Four-Axis Taxonomy & Inventory-Only Registration

**Plan:** [agent-inventory-spine-taxonomy-b4e9f2.md](../../../.cursor/plans/agent-inventory-spine-taxonomy-b4e9f2.md)  
**ADR:** [ADR-088-product-spine-function-truth.md](../../architecture/adr/ADR-088-product-spine-function-truth.md)  
**Date:** 2026-05-25

## STATUS: PASS

W1 adds orthogonal spine axes and registers **118** `agentic_core` inventory rows from the runtime assessment. **Zero** `ARTIFACT_PROVEN` rows. Registration does **not** imply product-spine participation.

## Deliverables

| Phase | Output | Status |
|-------|--------|--------|
| W1.0 | Four enums + `AgentClassification` axes + merge layer | DONE |
| W1.1 | [agentic_core_w1_spine_axes.json](../../../agentic_core/L2_execution/types/data/agentic_core_w1_spine_axes.json) (118 rows, 87 TRUE_AGENT) | DONE |
| W1.2 | CI gate + pytest | DONE |

## FILES_CHANGED

- [agent_taxonomy_spine_axes.py](../../../agentic_core/L2_execution/types/agent_taxonomy_spine_axes.py)
- [agent_taxonomy_w1_merge.py](../../../agentic_core/L2_execution/types/agent_taxonomy_w1_merge.py)
- [agent_taxonomy_registry.py](../../../agentic_core/L2_execution/types/agent_taxonomy_registry.py)
- [agentic_core_w1_spine_axes.json](../../../agentic_core/L2_execution/types/data/agentic_core_w1_spine_axes.json)
- [build_agentic_core_w1_taxonomy_axes.py](../../../tools/governance/build_agentic_core_w1_taxonomy_axes.py)
- [check_agent_taxonomy_spine_invariants.py](../../../ops_scripts/ci/check_agent_taxonomy_spine_invariants.py)
- [test_agent_spine_invocation_claims.py](../../../tests/governance/test_agent_spine_invocation_claims.py)
- [test_agent_taxonomy_registry_w1.py](../../../tests/agentic_core/L2_execution/types/test_agent_taxonomy_registry_w1.py)

## COMMANDS_RUN

| Command | Result |
|---------|--------|
| `python tools/governance/build_agentic_core_w1_taxonomy_axes.py` | exit 0 — 118 rows, 87 TRUE_AGENT |
| `python -m pytest tests/governance/test_agent_spine_invocation_claims.py tests/agentic_core/L2_execution/types/test_agent_taxonomy_registry_w1.py tests/agentic_core/L2_execution/types/test_agent_taxonomy_registry.py -q -o addopts=` | exit 0 — **13 passed** |
| `python ops_scripts/ci/check_agent_taxonomy_spine_invariants.py` | exit 0 — PASS |

## TESTS_GATES

- `validate_taxonomy_spine_invariants` — 0 violations
- `agentic_core` TRUE_AGENT count ≥ 87
- 0 rows `product_spine_invocation_status=ARTIFACT_PROVEN`
- 0 `*Agent` rows with `inventory_role=PRODUCT_SPINE_FUNCTION`
- All `agentic_core` rows: `runtime_proof_class=NONE`, empty `spine_proof_ref`

## ARTIFACTS

- [agentic_core_w1_spine_axes.json](../../../agentic_core/L2_execution/types/data/agentic_core_w1_spine_axes.json)

## NOTES

- Mock `_spine_proof_run/` not used for `spine_proof_ref` (W1 forbidden).
- W2: archive `RootCustomsAgent`; preserve L6 snapshot shim documentation.
- W3 remains DEFERRED for live `ARTIFACT_PROVEN` proof.
