# W3 Closeout — Live spine proof (no mock backfill)

**Plan:** [agent-inventory-spine-taxonomy-b4e9f2.md](../../../.cursor/plans/agent-inventory-spine-taxonomy-b4e9f2.md)  
**Evaluation:** [agent_inventory_w3_class_identity_evaluation.md](agent_inventory_w3_class_identity_evaluation.md)  
**Report:** [w3_live_spine_proof_report.json](../../../artifacts/reports/agent_inventory/_w3_live_spine_proof_run/w3_live_spine_proof_report.json)  
**Date:** 2026-05-25

## STATUS: PARTIAL

Live production-path spine executed; **zero** `*Agent` class strings in artifacts; taxonomy **not** updated to `ARTIFACT_PROVEN`. L2 modular recipe failed on lane prerequisite policy (expected without full prior-lane run dirs).

## W3 hardening compliance

| Rule | Result |
|------|--------|
| No backfill from `_spine_proof_run/` mock harness | OK — separate `_w3_live_spine_proof_run/` |
| `_test_mode=False`, no `l2_callable` injection | OK |
| `runtime_proof_class=LIVE_RUNTIME_PROOF` | OK |
| `mock_mode_detected=false` in spine proof | OK |
| `taxonomy_artifact_proven_updates=0` | OK |
| Decision 1: class identity on HOW | **Deferred** (see evaluation MD) |

## W3.0 outcomes

- **vLLM preflight:** reachable (`http://127.0.0.1:8000/v1`)
- **Cache preflight:** miss → generation allowed (`ENTRYPOINT_CANONICAL_DISPATCH`)
- **Spine:** `run_id=b6f4fc5a-9f54-459f-83ec-ae863763238d`, `x3=X3A`, fault `L2_EXECUTION_ERROR` (modular R4 lane policy)
- **Artifacts:** 21 JSON files including `agentic_core_how_trace.json`, `agentic_core_spine_proof.json`
- **A1:** `a1_invoked_agent_classes=0`

## FILES_CHANGED

- [run_w3_live_spine_proof.py](../../../tools/governance/run_w3_live_spine_proof.py)
- [agent_inventory_w3_class_identity_evaluation.md](agent_inventory_w3_class_identity_evaluation.md)
- [agent_inventory_spine_taxonomy_w3_receipt.md](agent_inventory_spine_taxonomy_w3_receipt.md)
- [w3_live_spine_proof_report.json](../../../artifacts/reports/agent_inventory/_w3_live_spine_proof_run/w3_live_spine_proof_report.json) (generated)
- [_w3_live_spine_proof_run/](../../../artifacts/reports/agent_inventory/_w3_live_spine_proof_run/) (generated spine artifacts)

## COMMANDS_RUN

| Command | Result |
|---------|--------|
| `python tools/governance/run_w3_live_spine_proof.py` | exit 1 (L2 lane fault) — report written; live path exercised |
| `python docs/reports/agent_inventory/_generate_runtime_assessment.py` | exit 0 — assessment MD/JSON regenerated |
| `python -m pytest tests/governance/test_agent_spine_invocation_claims.py -q -o addopts=` | exit 0 — **4 passed** |
| `python ops_scripts/ci/check_agent_taxonomy_spine_invariants.py` | PASS — `ARTIFACT_PROVEN=0` |

## TESTS_GATES

| Command | Result |
|---------|--------|
| `python ops_scripts/ci/check_agent_taxonomy_spine_invariants.py` | PASS |
| `tests/governance/test_agent_spine_invocation_claims.py` | 4 passed |

## NOTES

- **PARTIAL** because L2 did not complete a green modular R4 lane chain; proof goal was live path + A1 scan, not resume generation success.
- Full green integrated product proof remains `PYTEST_APPS_RG_INTEGRATED_LIVE=1` / `python -m apps_rg` (no `--section`) — out of scope for inventory taxonomy.
- Do not set any taxonomy row to `ARTIFACT_PROVEN` from this run.
