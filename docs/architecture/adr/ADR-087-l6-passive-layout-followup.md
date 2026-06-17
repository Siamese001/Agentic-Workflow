# ADR-087: L6 Passive Layout Follow-Up (Promotion + OTEL Nest)

**Status:** Accepted  
**Date:** 2026-05-25  
**Plan:** [l6-reorg-deferred-followup-f3a9c2](../../.claude/plans/l6-reorg-deferred-followup-f3a9c2.md) W1

## Decisions executed

### W1.1 — Promotion consumer → active root

- **Move:** `agentic_core/L6_observability/promotion/` → `agentic_core/L6_system_learning/promotion/`
- **Rationale:** `generic_l6_profile_consumer` encodes 06.7 UWG promotion semantics (active-adjacent).
- **Importer updated:** `apps_lic/runtime/bindings/promo_binding.py`

### W1.2 — OTEL modules nested under `runtime_trace/`

- **Move:** `cascade_telemetry`, `consensus_otel`, `heal_router_otel`, `otel_runtime_ingest` → `runtime_trace/`
- **Compat:** Thin re-export shims at prior root paths (no dual trees).

## Verification

- `python tools/_oneoff/l6_e2e_closeout_verify.py` after W1–W4 batch.
