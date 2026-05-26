---
plan_id: apps-rg-dry-run-migrate-delete-b9e4f2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg dry_run migrate-delete and quarantine open-scope burndown

Migrate all consumers off `apps_rg/runtime/dry_run/executive_summary_demo.py`, preserve non-product demo-harness proof semantics under test fixtures, then W11-gated delete of `runtime/dry_run/`. Closes deferred C1 from [apps-rg-quarantine-ssot-fanin-delete-c7e4a1](apps-rg-quarantine-ssot-fanin-delete-c7e4a1.md) and [quarantine_gated_delete_closeout_receipt.md](../docs/reports/apps_rg/quarantine_gated_delete_closeout_receipt.md).

> **plan_id discipline**: `apps-rg-dry-run-migrate-delete-b9e4f2` · markers use `plan=apps-rg-dry-run-migrate-delete-b9e4f2`

**Predecessor (COMPLETED):** [apps-rg-quarantine-ssot-fanin-delete-c7e4a1.md](apps-rg-quarantine-ssot-fanin-delete-c7e4a1.md) — C1 `MIGRATE_THEN_DELETE`, DELETE_READY=0

**Tools:** [quarantine_fanin_matrix.py](../tools/governance/quarantine_fanin_matrix.py) · [check_quarantine_ssot.py](../ops_scripts/ci/check_quarantine_ssot.py)

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: DONE
LAST_COMPLETED_WAVE: W6
LAST_UPDATED: 2026-05-24

PLAN_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 note="dry_run deleted; fixture at tests/fixtures/apps_rg/demo_harness_fixture.py"
WAVE_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=1 note="importer inventory doc"
WAVE_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=2 note="demo_harness_fixture"
WAVE_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=3 note="tests migrated"
WAVE_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=4 note="outside_main_entry_policy"
WAVE_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=5 note="dry_run/ removed"
WAVE_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=6 note="closeout receipt; check_quarantine_ssot PASS"

---

## Context (SCQA)

- **Situation** — `apps_rg/runtime/dry_run/` holds a single live module (`executive_summary_demo.py`) env-gated by `APPS_RG_ALLOW_DEMO_HARNESS`. Contract tests classify `dry_run/` as non-product (`KEEP_APPS_RG`). Fan-in matrix C1 verdict: **MIGRATE_THEN_DELETE** with test-only importers.
- **Complication** — Unit and contract tests import or subprocess `python -m apps_rg.runtime.dry_run.executive_summary_demo`. Policy modules (`outside_main_entry_policy.py`, `validate_exec_summary_graph_only_generation.py`) still reference the path. Deleting without migration breaks W7A boundary tests and deprecated-path quarantine SSOT.
- **Question** — How do we retire `runtime/dry_run/` without losing demo-harness non-product proof coverage?
- **Answer** — Extract harness behavior to `tests/fixtures/apps_rg/demo_harness_fixture.py` (or equivalent), migrate tests, refresh fan-in to `DELETE_READY`, then delete the directory and update CI/contracts to assert absence.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.2 | Baseline fan-in + importer inventory | ~15K | ADG sqlite available or static scan only | 🔲 TODO | Updated matrix; doc lists every importer |
| W2 | W2.1–W2.2 | Demo harness fixture extraction | ~25K | Fixture stays test-only; no product import | 🔲 TODO | `run_demo_harness()` callable from tests without `dry_run/` |
| W3 | W3.1–W3.3 | Test + contract migration | ~30K | Scoped pytest per wave | 🔲 TODO | Zero imports of `runtime.dry_run` |
| W4 | W4.1–W4.2 | Policy / denylist cleanup | ~12K | No behavior change to product spine | 🔲 TODO | No string refs to deleted module path |
| W5 | W5.1–W5.2 | W11-gated delete `dry_run/` | ~15K | W1 shows `C1_dry_run` DELETE_READY | 🔲 TODO | Directory absent; migration receipt |
| W6 | W6.1 | Proof + closeout | ~10K | — | 🔲 TODO | compileall + scoped gates PASS |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Re-run fan-in matrix | `tools/governance/quarantine_fanin_matrix.py` | Stale ADG optional | ~8K | 🔲 TODO |
| W1.2 | Importer inventory doc | `docs/reports/apps_rg/dry_run_importer_inventory_20260524.md` | Must list tests + policy | ~7K | 🔲 TODO |
| W2.1 | Extract `run_demo_harness` + stamp | `tests/fixtures/apps_rg/demo_harness_fixture.py` | Preserve `DEMO_HARNESS_*` contract | ~15K | 🔲 TODO |
| W2.2 | Env fail-closed subprocess helper | same + thin wrapper for subprocess tests | Match W7A boundary | ~10K | 🔲 TODO |
| W3.1 | Unit test migration | `test_demo_harness_fail_closed.py`, `test_section_evidence_w7a_shadow_proof_boundary.py`, `test_integrated_product_proof_gate.py` | Subprocess vs import | ~12K | 🔲 TODO |
| W3.2 | Contract boundary lists | `test_apps_rg_*_boundary.py`, `test_apps_rg_deprecated_path_quarantine.py`, `test_dispatch_callers_are_canonical_only.py`, `test_apps_rg_canonical_runtime_hygiene.py` | Flip KEEP → absent after W5 | ~10K | 🔲 TODO |
| W3.3 | Scoped pytest proof | selectors below | — | ~8K | 🔲 TODO |
| W4.1 | Policy denylist | `outside_main_entry_policy.py`, `validate_exec_summary_graph_only_generation.py` | Remove `executive_summary_demo` entry | ~6K | 🔲 TODO |
| W4.2 | Integrated evidence packaging | `integrated_lane_evidence_packaging.py` blocklist | Already asserts non-consumption | ~6K | 🔲 TODO |
| W5.1 | Delete `apps_rg/runtime/dry_run/` | entire tree | W11 checklist | ~8K | 🔲 TODO |
| W5.2 | CI SSOT update | `check_quarantine_ssot.py`, `check_apps_rg_runtime_path_inventory.py` | Remove from NON_PRODUCT_DIRS; assert gone | ~7K | 🔲 TODO |
| W6.1 | Closeout receipt | `docs/reports/apps_rg/dry_run_delete_closeout_receipt.md` | Link migration JSON | ~10K | 🔲 TODO |

---

## Open Scope Inventory (from quarantine closeout)

### In scope (this plan)

| ID | Item | Current state | Target |
|----|------|---------------|--------|
| C1 | `apps_rg/runtime/dry_run/` | Live demo module | **Deleted** after migration |
| T1 | `test_demo_harness_fail_closed.py` | imports `executive_summary_demo` | uses fixture |
| T2 | `test_section_evidence_w7a_shadow_proof_boundary.py` | subprocess + import demo | fixture / helper |
| T3 | Contract tests listing `dry_run/` | KEEP_APPS_RG / boundary allowlist | assert absent post-W5 |
| P1 | `outside_main_entry_policy.py` | blocks `python -m apps_rg.runtime.dry_run.` | remove or redirect |
| P2 | `validate_exec_summary_graph_only_generation.py` | denylist string | remove |
| CI1 | `check_quarantine_ssot.py` | expects `dry_run` exists | expect absent |

### Explicitly out of scope

| Item | Reason |
|------|--------|
| `artifacts/apps_rg/benchmarks/dry_run/` | L6 benchmark examples; unrelated path |
| `runtime/internal/`, `integrations/hops/`, `engines/` | Fan-in **KEEP**; no delete |
| `apps_rg/__main__.py` `--dry-run` CLI flag | Product CLI semantics; not `runtime/dry_run/` |
| PA/W9 `dry_run_*` pytest fixtures | Fixture naming; not demo harness path |
| Full `tests/_apps_contract/` suite | Scoped selectors only |
| Restore `integrations/hops/_ensemble_runner.py` | Separate hops debt (see Gap Register) |

### Optional follow-up (split if Author-Gate needed)

| ID | Item | Notes |
|----|------|-------|
| H1 | `tests/apps_rg/integrations/hops/test_ensemble_runner.py` | Imports missing `_ensemble_runner.py`; collection/import failure — triage delete vs restore stub in dedicated micro-plan |

---

## Out Of Scope

- Re-indexing full ADG repo (optional W1.1 only if cheap)
- Deleting `runtime/internal/` or narrative `hops/` live code
- `agentic_core` validation_orchestrator retirement
- Obsolete skipped-test purge across entire repo (mention only if discovered during W3)

---

## Wave 1 — Baseline fan-in and importer inventory

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Commands**:

```bash
python tools/governance/quarantine_fanin_matrix.py
# Optional: refresh ADG then re-run if tree changed since 05232026_1851
```

**Acceptance**:
- `C1_dry_run` row documents test importers only (no product importers)
- `docs/reports/apps_rg/dry_run_importer_inventory_20260524.md` lists every file from static grep + matrix

---

## Wave 2 — Demo harness fixture extraction

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Design constraints**:
- Fixture module lives under `tests/fixtures/` (never imported from `apps_rg/` product code)
- Reuse `apps_rg.runtime.non_product_proof_stamp` (`DEMO_HARNESS_ENV`, `DEMO_HARNESS_PROOF_CLASSIFICATION`)
- Emit same `demo_harness_proof.json` shape as today for W7A tests

**Acceptance**:
- `pytest tests/unit/apps_rg/test_demo_harness_fail_closed.py -q` passes against fixture (before W5 delete)

---

## Wave 3 — Test and contract migration

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Primary files**:

- [test_demo_harness_fail_closed.py](../tests/unit/apps_rg/test_demo_harness_fail_closed.py)
- [test_section_evidence_w7a_shadow_proof_boundary.py](../tests/unit/apps_rg/test_section_evidence_w7a_shadow_proof_boundary.py)
- [test_integrated_product_proof_gate.py](../tests/unit/apps_rg/test_integrated_product_proof_gate.py)
- [test_apps_rg_deprecated_path_quarantine.py](../tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py)
- [test_apps_rg_generation_model_env_boundary.py](../tests/_apps_contract/test_apps_rg_generation_model_env_boundary.py)
- [test_apps_rg_exit_uwg_l4_no_bypass_boundary.py](../tests/_apps_contract/test_apps_rg_exit_uwg_l4_no_bypass_boundary.py)
- [test_apps_rg_canonical_runtime_hygiene.py](../tests/_apps_contract/test_apps_rg_canonical_runtime_hygiene.py)
- [test_dispatch_callers_are_canonical_only.py](../tests/unit/apps_rg/test_dispatch_callers_are_canonical_only.py)

**Scoped proof**:

```bash
pytest tests/unit/apps_rg/test_demo_harness_fail_closed.py tests/unit/apps_rg/test_section_evidence_w7a_shadow_proof_boundary.py tests/unit/apps_rg/test_integrated_product_proof_gate.py tests/unit/apps_rg/test_integrated_lane_evidence_packaging.py -q
pytest tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py tests/_apps_contract/test_quarantined_paths_raise_runtime_error.py -q
```

**Acceptance**:
- `rg 'runtime\.dry_run|executive_summary_demo' apps_rg tests ops_scripts` → only W5-pending docs or explicit absent-path assertions

---

## Wave 4 — Policy and packaging cleanup

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Acceptance**:
- No production module references `executive_summary_demo` path strings
- [test_integrated_lane_evidence_packaging.py](../tests/unit/apps_rg/test_integrated_lane_evidence_packaging.py) still passes

---

## Wave 5 — W11-gated delete

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**W11 DELETE_GATE** (all required before `git rm -r apps_rg/runtime/dry_run/`):

- [ ] Fan-in matrix `delete_ready_ids` contains `C1_dry_run`
- [ ] Zero pytest imports under deleted path
- [ ] No `python -m apps_rg.runtime.dry_run` in policy allowlists
- [ ] Migration receipt JSON under `artifacts/governance/migration_receipts/`
- [ ] `python -m compileall apps_rg apps_shared -q` exit 0

**Post-delete CI**:
- Remove `apps_rg/runtime/dry_run` from `NON_PRODUCT_DIRS` in [check_apps_rg_runtime_path_inventory.py](../ops_scripts/ci/check_apps_rg_runtime_path_inventory.py)
- Update [check_quarantine_ssot.py](../ops_scripts/ci/check_quarantine_ssot.py) to assert directory absent (or remove C1 from live-dirs list)
- Update [test_quarantined_paths_raise_runtime_error.py](../tests/_apps_contract/test_quarantined_paths_raise_runtime_error.py) — `dry_run/` → `ModuleNotFoundError` / not on disk

---

## Wave 6 — Proof and closeout

WAVE_ID: W6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Commands**:

```bash
python -m compileall agentic_core apps_rg apps_shared -q
python ops_scripts/ci/check_no_shadow_spine.py
python ops_scripts/ci/check_quarantine_ssot.py
python tools/governance/quarantine_fanin_matrix.py
```

**Acceptance**:
- Closeout: `docs/reports/apps_rg/dry_run_delete_closeout_receipt.md`
- `PLAN_COMPLETE` marker emitted

---

## Gap Register

**GAP-1: Large `executive_summary_demo.py` (~2k LOC)**
- May shrink fixture to minimal stub implementing only `run_demo_harness` + env gate used by tests
- Impact: W2 token estimate may grow if full port required

**GAP-2: ADG snapshot staleness**
- Re-index before W5 if other deletes landed on `main`
- Impact: False DELETE_READY if not refreshed

**GAP-3: `test_ensemble_runner.py` import failure**
- Missing `_ensemble_runner.py` on disk; unrelated to dry_run but open quarantine-adjacent debt
- Impact: Defer to H1 micro-plan unless trivial delete in W3

**GAP-4: `check_apps_rg_runtime_path_inventory.py` broad `__main__` failures**
- Pre-existing; do not block this plan on full inventory gate
- Impact: Use `check_quarantine_ssot.py` + scoped pytest for proof

---

## Definition of Done

DoD-1: Importer inventory published on disk
- Evidence: [dry_run_importer_inventory_20260524.md](../docs/reports/apps_rg/dry_run_importer_inventory_20260524.md) exists with test/policy/CI rows
- Status: TODO

DoD-2: Demo harness fixture replaces product `dry_run` module for tests
- Evidence: `pytest tests/unit/apps_rg/test_demo_harness_fail_closed.py tests/unit/apps_rg/test_section_evidence_w7a_shadow_proof_boundary.py -q` → 0 failed (pre-delete)
- Status: TODO

DoD-3: `apps_rg/runtime/dry_run/` deleted from repo
- Evidence: `git ls-files apps_rg/runtime/dry_run` empty; fan-in matrix `C1_dry_run.exists_on_disk=false`
- Status: TODO

DoD-4: CI quarantine SSOT reflects absence
- Evidence: `python ops_scripts/ci/check_quarantine_ssot.py` exit 0; scoped contract tests PASS
- Status: TODO

DoD-5: Smoke — no shadow spine regression
- Evidence: `python ops_scripts/ci/check_no_shadow_spine.py` exit 0
- Status: TODO

DoD-6: Plan registered in Notion Plans DB
- Evidence: `PLAN_CREATED` marker; Notion row slug=`apps-rg-dry-run-migrate-delete-b9e4f2`
- Status: TODO

### Verification vs deferral

| Item | Verify in this plan | Defer |
|------|---------------------|-------|
| C1 dry_run delete | W5–W6 | — |
| internal / hops / engines | — | KEEP per prior matrix |
| hops `_ensemble_runner` restore | — | H1 optional |
| Full contract suite | — | Scoped pytest |

---

## Marker Quick Reference

```
PLAN_CREATED: slug=apps-rg-dry-run-migrate-delete-b9e4f2 path=.cursor/plans/apps-rg-dry-run-migrate-delete-b9e4f2.md status=Not Started
WAVE_START: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=1
WAVE_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=1 note="fanin+importer inventory"
WAVE_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=2 note="demo harness fixture"
WAVE_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=3 note="+N tests migrated"
WAVE_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=4 note="policy cleanup"
WAVE_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=5 note="dry_run deleted"
WAVE_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 wave=6 note="closeout receipt"
PLAN_COMPLETE: plan=apps-rg-dry-run-migrate-delete-b9e4f2 note="dry_run migrate-delete done"
```

---

## References

- [quarantine_gated_delete_closeout_receipt.md](../docs/reports/apps_rg/quarantine_gated_delete_closeout_receipt.md)
- [quarantine_ssot_reconcile_20260524.md](../docs/reports/apps_rg/quarantine_ssot_reconcile_20260524.md)
- [apps-rg-quarantine-ssot-fanin-delete-c7e4a1.md](apps-rg-quarantine-ssot-fanin-delete-c7e4a1.md)
- [non_product_proof_stamp.py](../apps_rg/runtime/non_product_proof_stamp.py)
