# Graph Skills Degraded Readiness Guard

Generated: 2026-06-19

Scope: graph-skills W0 follow-up after merge/push of PR #427.

## Guard

The recurrence guard is recorded in the PR body and in the durable run receipt:
`artifacts/codex/run_receipts/apps-rg-graph-skills-w0-hardening-20260619.json`.

The guard is:

- Record degraded readiness explicitly.
- Keep verification scoped to pytest slices, `py_compile`, and in-session ADG health evidence.
- Do not expand a graph-skills PR into MCP/session bootstrap changes.

## Evidence

- Scoped tests passed:
  - `tests/unit/apps_rg/runtime/test_graph_evidence_contract.py`
  - `tests/unit/apps_rg/test_competencies_capability_bundle_wiring.py`
  - `tests/unit/apps_rg/test_competencies_authority_gates.py`
  - `tests/unit/apps_rg/test_competencies_x2_proof_quality.py`
  - `tests/unit/apps_rg/test_competencies_v3_e2e_hardening.py`
  - `tests/_apps_contract/test_apps_rg_competencies_x2_source_facts.py -k "not mock_slice_still_passes_x2_source_mapping"`
- Runtime compile passed:
  - `apps_rg/runtime/sections/graph_evidence_contract.py`
  - `apps_rg/runtime/validators/competencies_quality_x2.py`
- In-session ADG identity is healthy:
  - PID `22680`
  - startup nonce `0f50a3ee17d3`
  - snapshot `06192026_0917`
  - `redis_enabled=true`

## Notes

`codex_readiness.py --json` still fails in this session because `memory` and `vector_db` are not exposed and duplicate `context7`/`notion`/`playwright` cohorts remain blocked on host-attached PID proof. That failure is recorded as degraded evidence, not as a graph-skills regression.
