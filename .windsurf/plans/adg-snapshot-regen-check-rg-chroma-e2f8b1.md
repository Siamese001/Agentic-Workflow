---
plan_id: adg-snapshot-regen-check-rg-chroma-e2f8b1
plan_type: infra
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# ADG Snapshot Regeneration — Unblock CHECK-RG-CHROMA

Regenerate the stale ADG snapshot so `snapshot_graph_layer_completeness` passes and
`run_contract_gates.py --gate CHECK-RG-CHROMA` reaches the actual CHECK-RG-CHROMA gate.

**Prior context**: `runner-preflight-unblock-3b7d4a` cleared all four unconditional
pre-flight gates. The one remaining blocker is `snapshot_graph_layer_completeness`
(`mv_*=4 < min=30`). This plan addresses only that.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W1
CURRENT_WAVE_STATUS: IN_PROGRESS
LAST_COMPLETED_WAVE: none
LAST_UPDATED: 2026-05-13

---

## Context

`run_contract_gates.py` runs a fifth unconditional pre-flight gate after the four fixed by
`runner-preflight-unblock-3b7d4a`:

```
snapshot_graph_layer_completeness gate:
  snapshot   : adg_indexed_05102026_1319.sqlite
  mv_*       :    4 (min 30)
  [FAIL] mv_* count 4 < MIN_MV_TABLES=30
```

The snapshot is stale. `generate_full_adg.py` must re-run to produce a fresh snapshot
with all materialized views populated. This is purely an artifact regeneration — no source
code changes required.

---

## Wave 1 — Regenerate ADG snapshot

WAVE_ID: W1
WAVE_STATUS: IN_PROGRESS
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED

**Phases**:
- **W1.1** — Baseline verification: confirm only blocker is snapshot_graph_layer_completeness | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Run `python tools/generate_full_adg.py` | PHASE_STATUS: TODO
- **W1.3** — Re-run `run_contract_gates.py --gate CHECK-RG-CHROMA`, record verdict | PHASE_STATUS: TODO
- **W1.4** — Git diff scope verification | PHASE_STATUS: TODO
- **W1.5** — Classify any new downstream failure explicitly | PHASE_STATUS: TODO

**Acceptance**:
- `snapshot_graph_layer_completeness` exits 0 (`mv_*` ≥ 30)
- `run_contract_gates.py --gate CHECK-RG-CHROMA` reaches the CHECK-RG-CHROMA gate
- No agentic_core files modified
- No `c0_binding.py` touches
- Chroma plan remains closed

---

## Files In Scope

- `artifacts/adg/` — new snapshot written by `generate_full_adg.py` (artifact, not source)

## Files Out Of Scope (hard constraint)

- `agentic_core/` — DO NOT TOUCH
- `apps_rg/runtime/bindings/c0_binding.py` — DO NOT TOUCH
- `.windsurf/plans/apps-rg-chroma-ingestion-wiring-c7f2d9.md` — DO NOT REOPEN
- `ops_scripts/ci/infra_wiring_scan.py` — already fixed, DO NOT REGRESS
- `ops_scripts/ci/executor_theater_gate.py` — already fixed, DO NOT REGRESS
- `ops_scripts/ci/baselines/graph_layer_evidence_baseline.json` — already fixed, DO NOT REGRESS

---

## Receipts

### W1.1 — Baseline (pre-regeneration)

```
PLACEHOLDER — to be filled after baseline run
```

### W1.2 — generate_full_adg.py

```
PLACEHOLDER — to be filled after generation
```

### W1.3 — Post-regeneration runner result

```
PLACEHOLDER — to be filled after re-run
```

### W1.4 — Git diff scope

```
PLACEHOLDER — to be filled after regeneration
```

---

## Definition of Done

| # | Criterion | Verified |
|---|-----------|---------|
| DoD-1 | `snapshot_graph_layer_completeness` exits 0 (`mv_*` ≥ 30) | ⏳ |
| DoD-2 | `run_contract_gates.py --gate CHECK-RG-CHROMA` reaches CHECK-RG-CHROMA gate | ⏳ |
| DoD-3 | New snapshot `mv_*` count ≥ 30 recorded in receipt | ⏳ |
| DoD-4 | No agentic_core or c0_binding.py changes | ⏳ |
| DoD-5 | Any new downstream failure explicitly classified | ⏳ |

| Criterion | Disposition |
|-----------|-------------|
| Smoke-run DoD row | N/A — artifact regeneration only, no source code changed |
| Chroma plan reopened | NEVER |
