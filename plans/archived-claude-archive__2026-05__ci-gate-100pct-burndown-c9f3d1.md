---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\ci-gate-100pct-burndown-c9f3d1.md'
original_relative_path: '_archive\\2026-05\\ci-gate-100pct-burndown-c9f3d1.md'
source_sha256: fe0a3598f5a1ac154096c6c508be188ca039fc8e6d4bf87106a0b4e2fc7f4c91
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: ci-gate-100pct-burndown-c9f3d1
plan_type: governance
---

# CI Gate 100% Burndown — P0 Closure (Final)

Closes the last remaining CI gate failure: `infra_wiring_scan` P0 structural violations. All P1/P2/P3 gates already green from prior plans.

**Created**: 2026-05-04 17:17 EDT.

---

## Context (SCQA)

- **Situation** — 8/9 CI gates PASS after `ci-gate-remediation-p2-p3-a7e4d9` and `ci-gate-deferred-scope-b8f5e1`. P1 structure policy, P2 ratchets (module_loc, uwg_bypass, unresolved_edges), P2 graph-layer evidence, P3 AG ledger, P3 10C proof — all green.
- **Complication** — `infra_wiring_scan.py` still fails: `v_p0_apps_direct_infra: 14`. File-scan portion is clean (19 pre-existing files whitelisted). The 14 violations come from the stale ADG snapshot (`adg_indexed_05042026_1701.sqlite`). ADG regeneration is blocked by a schema error: `entrypoint_kind` column missing from `nodes` table.
- **Question** — How do we fix the ADG schema, regenerate, and achieve 100% CI gate green?
- **Answer** — W1 (diagnose + fix ADG schema), W2 (regenerate ADG), W3 (verify infra_wiring_scan PASS + reduce P2 ceiling), W4 (final full-CI sweep).

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `ops_scripts/ci/infra_wiring_scan.py` | Last failing gate: 14 P0 structural violations | ❌ FAIL |
| `tools/generate_full_adg.py` | ADG regeneration | ❌ Schema error |
| `tools/generate/entrypoint_scanner.py` | Writes `entrypoint_kind` column to nodes | ⚠️ Source of schema issue |
| `tools/generate/truth_expansion_enricher.py` | Creates `module_entrypoints` table + `mv_entrypoint_kind_summary` | ✅ Reference |
| `ops_scripts/ci/check_snapshot_has_mvs.py` | Projection freshness post-regen | ✅ Currently PASS |

---

## Wave Structure

| Waves | Focus | Gates Targeted | Deliverable | Status |
|-------|-------|----------------|-------------|--------|
| W1 | Diagnose + Fix ADG Schema | `entrypoint_kind` column | Nodes table has `entrypoint_kind` column; regeneration runs clean | 🟡 Not Started |
| W2 | Regenerate ADG | Full ADG snapshot | Fresh `adg_indexed_<ts>.sqlite` with matching projection | 🟡 Not Started |
| W3 | Verify infra_wiring + Reduce Ceiling | `infra_wiring_scan.py`, `_P2_CEILING_DUPED` | 0 P0 violations; ceiling 3→1 | 🟡 Not Started |
| W4 | Final CI Sweep | All gates | `run_contract_gates.py` full green (0 FAIL) | 🟡 Not Started |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Diagnose entrypoint_kind schema error | `tools/generate/entrypoint_scanner.py`, `tools/generate/generate_full_adg.py` | Scanner writes to `nodes.entrypoint_kind` but column may not exist in schema DDL | ~0.5K | 🟡 Not Started |
| W1.P2 | Fix schema — add column or migration | `tools/generate/` DDL or migration | Add `entrypoint_kind TEXT` to nodes table; ensure idempotent | ~0.5K | 🟡 Not Started |
| W2.P1 | Regenerate ADG | `tools/generate_full_adg.py` | Full regeneration with progress bar; verify no errors | ~0.5K | 🟡 Not Started |
| W2.P2 | Verify projection freshness | `check_snapshot_has_mvs.py` | Canonical digest == projection digest | ~0.2K | 🟡 Not Started |
| W3.P1 | Verify infra_wiring_scan PASS | `infra_wiring_scan.py` | 0 P0 structural + 0 file-scan violations | ~0.3K | 🟡 Not Started |
| W3.P2 | Reduce P2_CEILING_DUPED 3→1 | `infra_wiring_scan.py` | Both definitions updated | ~0.1K | 🟡 Not Started |
| W4.P1 | Full CI sweep | `run_contract_gates.py` | All gates green; exit 0 | ~0.5K | 🟡 Not Started |

---

## Gap Register

| Gap ID | Description | Blocking | Owner | Resolution |
|--------|-------------|----------|-------|------------|
| G1 | Exact root cause of entrypoint_kind schema error | W1.P1 | TBD | Is column missing from DDL or is it a migration issue? |
| G2 | ADG regeneration time | W2.P1 | TBD | ~3-5 minutes; may need background execution |

---

## Non-Goals

- NOT modifying already-passing P1/P2/P3 gates
- NOT adding new gate criteria
- NOT implementing new app features
- NOT addressing P3 isolated experimental modules (design-correct, deferred indefinitely)

---

## Success Criteria

- [ ] W1: ADG schema fixed; regeneration runs without `entrypoint_kind` error
- [ ] W2: Fresh ADG snapshot with matching projection
- [ ] W3: `infra_wiring_scan.py` PASS (0 P0 structural + 0 file-scan)
- [ ] W3: `_P2_CEILING_DUPED` = 1
- [ ] W4: `run_contract_gates.py` exit 0, all gates green

---

## Related Plans

- **Parent**: `ci-gate-deferred-scope-b8f5e1` (Completed)
- **Grandparent**: `ci-gate-remediation-p2-p3-a7e4d9` (Completed)
- **Great-grandparent**: `ci-gate-remediation-p0-p3-f8d3c2` (Completed)
- **Dependencies**: ADG schema, entrypoint_scanner.py

---

## Notes

Created 2026-05-04 as final P0 closure plan. Only 1 gate remains failing.
All P1/P2/P3 gates already green from prior burndown plans.
ADG regeneration is the single blocking dependency.
