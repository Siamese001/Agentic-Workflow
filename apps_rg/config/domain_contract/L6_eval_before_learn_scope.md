# L6 eval-before-learn scope (apps_rg)

**Plan:** `pa-exec-flowchart-gap-f2a8c3` wave 7  
**REQ:** REQ-L6-EVAL-BEFORE-LEARN-001

## Policy

- L6 shadow ingest runs **only after** sealed post-run exhaust (`runtime_exhaust_bundle.json` on section lanes; core `RuntimeExhaustBundle` on integrated).
- L6 **must not** rescue, mutate, or re-authorize the current run (no X3/Exit override).
- **Promotion** to durable learning or production config requires human eval labels + gauntlet — **not** satisfied by shadow packet assembly alone.

## Section lanes (modular CLI)

| Surface | Status |
|---------|--------|
| `exit_disposition_receipt.json` | Canonical exit X3 |
| `runtime_exhaust_bundle.json` | Post-exit exhaust for L6 |
| `l6_shadow_handoff_receipt.json` | Proves handoff boundary before shadow |
| `build_l6_shadow_package` | Shadow eval packet only; `promotion_allowed: false` |

**N/A (honest):** Full eval + gauntlet promotion pipeline for section-only runs is deferred until stratified human labels exist (see `docs/reports/apps_rg/l6_benchmark_collection_workflow_w4.md`).

## Integrated spine

Governed exit (W6) emits core `RuntimeExhaustBundle` with `created_after_exit=True`.  
`ingest_integrated_exhaust_for_l6_shadow` validates that bundle before any L6 consumer.

## Escape hatch

`APPS_RG_GOVERNED_L6_SHADOW_SKIP=1` — disables governed preconditions (dev/tests only).
