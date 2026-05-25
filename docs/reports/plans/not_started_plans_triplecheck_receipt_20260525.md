# Not Started plans — triple-check receipt (2026-05-25)

Notion Plans DB query: **6** rows with `Status = Not Started`.

## Summary

| Slug | Verdict | Notion after sync |
|------|---------|-------------------|
| [10c-proof-bundle-current-head-a8f4c2](../../.cursor/plans/10c-proof-bundle-current-head-a8f4c2.md) | **COMPLETE** — bundles regen + gate PASS | **Completed** |
| [l0-l3-parent-gap-remediation-a7f3e2](../../.cursor/plans/l0-l3-parent-gap-remediation-a7f3e2.md) | **VALID** — no `l3_binding`, no §7 CI validators | **Waiting** |
| [l0-routing-v15-only-cutover-c9e2f1](../../.cursor/plans/l0-routing-v15-only-cutover-c9e2f1.md) | **VALID** — v12 bridge still in L0_routing | **Waiting** |
| [apps-rg-parallel-section-orchestration-f2a8c4](../../.cursor/plans/apps-rg-parallel-section-orchestration-f2a8c4.md) | **VALID** — serial modular lanes; not superseded by section spine | **Waiting** |
| [semantic-cache-fingerprint-proof-c9f1a3](../../.cursor/plans/semantic-cache-fingerprint-proof-c9f1a3.md) | **VALID optional** — plan DoD open; cert tooling exists elsewhere | **Waiting** |
| [fortknox-runtime-dual-track-b7c4e2](../../.cursor/plans/fortknox-runtime-dual-track-b7c4e2.md) | **VALID** — skill exists; plan W0–W4 not executed | **Waiting** |

## Proof (10c only)

```text
python tools/requirements/emit_proof_bundles.py --regenerate-all -> 198 bundles @ git_head=1f8195f1
python ops_scripts/ci/check_10c_pilot_proof_evidence.py --skip-pytest -> 198/198 PASS
```

Artifact: [10c_pilot_proof_evidence.md](../../artifacts/requirements/10c_pilot_proof_evidence.md)

## Repo checks (why others stay Waiting)

| Plan | Evidence still open |
|------|---------------------|
| l0-l3 | `apps_rg/runtime/bindings/l3_binding.py` absent; `check_l0_parent_invariants.py` absent |
| l0-v15 | `agentic_core/L0_routing` still documents v12 bridge path |
| parallel | No `managed_section_lane_dispatcher`; `modular_resume_generation` serial loop |
| semantic-cache | No `artifacts/governance/*fingerprint*` per plan DoD |
| fortknox | Plan waves W0–W4 TODO; partial coverage via [fortknox-evidence skill](../../.cursor/skills/fortknox-evidence/SKILL.md) only |

## Related disk hygiene (not in Not Started query)

| Slug | Action |
|------|--------|
| [apps-rg-exit-disposition-smoke-b7e2d9](../../.cursor/plans/apps-rg-exit-disposition-smoke-b7e2d9.md) | Already **Retired** in Notion; disk updated SUPERSEDED (`exit_disposition_receipt.json`) |

## Honest note

Five plans cannot be marked **Completed** without multi-wave `agentic_core` / apps_rg engineering. They are reclassified to **Waiting** with `Waiting For` text so Not Started queue is clear.
