---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\apps-rg-quarantine-ssot-fanin-delete-c7e4a1.md'
original_relative_path: '_archive\\2026-05\\apps-rg-quarantine-ssot-fanin-delete-c7e4a1.md'
source_sha256: 09630f311e1e8427f9f87d5d7dfcf5e9748872de238869ece0f03ce5ea3065c5
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-quarantine-ssot-fanin-delete-c7e4a1
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# apps_rg quarantine SSOT reconcile, fan-in audit, and W11-gated delete

Reconcile stale W4/W11 quarantine documentation and CI with the post–dead-code-waves tree; produce a fan-in matrix for four high-risk `apps_rg` areas; execute deletions only where the W11 DELETE_GATE checklist passes (including tests).

> **plan_id discipline**: `apps-rg-quarantine-ssot-fanin-delete-c7e4a1` · markers use `plan=apps-rg-quarantine-ssot-fanin-delete-c7e4a1`

**Predecessors:** [w11_closeout_and_next_plan_handoff.md](../docs/reports/agent_inventory/w11_closeout_and_next_plan_handoff.md) · ADG dead-code waves A–D (`0f13fb3e69`) · [apps-rg-legacy-dependency-burndown-b7e4a2.md](apps-rg-legacy-dependency-burndown-b7e4a2.md) (successor, partial overlap)

**ADG snapshot baseline (re-index before W2 if tree changed):** `artifacts/adg/adg_indexed_05232026_1851.sqlite`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETED
CURRENT_WAVE: DONE
LAST_COMPLETED_WAVE: W3
LAST_UPDATED: 2026-05-24

PLAN_COMPLETE: plan=apps-rg-quarantine-ssot-fanin-delete-c7e4a1 note="W1 SSOT reconcile; W2 fan-in matrix DELETE_READY=0; W3 gated delete deferred dry_run"
WAVE_COMPLETE: plan=apps-rg-quarantine-ssot-fanin-delete-c7e4a1 wave=1 note="+43 tests, 6 files, scope=quarantine-ssot-reconcile"
WAVE_COMPLETE: plan=apps-rg-quarantine-ssot-fanin-delete-c7e4a1 wave=2 note="fanin matrix artifact, DELETE_READY=0"
WAVE_COMPLETE: plan=apps-rg-quarantine-ssot-fanin-delete-c7e4a1 wave=3 note="zero deletes per W11 gate; closeout receipt"

---

## Context (SCQA)

- **Situation** — W4 quarantine (May 2026) stubbed 132+ `apps_rg` files; W11 classified 13 candidates with **DELETE_READY = 0**. Hard-delete closeouts removed `reasoning/`, `*_dispatch.py` tails, and many stubs. ADG waves A–D removed isolated orphans. Contract tests and CI still reference removed paths or expect `RuntimeError(QUARANTINE)` where imports now yield `ModuleNotFoundError` or succeed (`integrations/hops` is live again).
- **Complication** — Planning artifacts ([apps_rg_quarantine_u0_packet_coverage_audit.md](../artifacts/apps_rg/apps_rg_quarantine_u0_packet_coverage_audit.md), [test_quarantined_paths_raise_runtime_error.py](../tests/_apps_contract/test_quarantined_paths_raise_runtime_error.py)) disagree with disk. Deleting `dry_run/`, `internal/`, `hops/`, or `engines/` without fan-in + test migration would break CI and narrative tests.
- **Question** — How do we refresh quarantine SSOT, measure real blast radius, and delete only code that passes W11 gates?
- **Answer** — Three waves: (1) reconcile registries/tests/CI to current tree; (2) ADG + static fan-in matrix with per-path verdict; (3) minimal gated delete/archive batch with receipts—no bulk delete from stale audits.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.4 | Quarantine SSOT reconcile (tests, CI, docs index) | ~25K | No product behavior change in W1 | ✅ DONE | Drift doc + contract tests + narrow CI gate |
| W2 | W2.1–W2.3 | Fan-in matrix: dry_run, internal, hops, engines | ~30K | Latest ADG sqlite available | ✅ DONE | fanin matrix JSON/MD; DELETE_READY=0 |
| W3 | W3.1–W3.3 | W11-gated delete/archive + test migration | ~40K | W2 verdicts approved for delete | ✅ DONE | No deletes (0 DELETE_READY); closeout receipt |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | Inventory drift report | `tests/_apps_contract/*quarantine*`, `ops_scripts/ci/check_apps_rg_runtime_path_inventory.py` | W0A tests vs ModuleNotFoundError | ~8K | 🔲 TODO |
| W1.2 | Update CI `QUARANTINE_DIRS` / `QUARANTINED_PATHS` | CI gate + import-graph test | Remove `reasoning/`, `_quarantine/`; fix hops classification | ~6K | 🔲 TODO |
| W1.3 | Rewrite import-time quarantine tests | `test_quarantined_paths_raise_runtime_error.py`, `test_w4_quarantine_bypass.py` (subset) | Assert absent OR stub; not missing modules | ~6K | 🔲 TODO |
| W1.4 | SSOT doc patch (index only) | `deprecation_quarantine_plan.md` addendum or `docs/reports/apps_rg/quarantine_ssot_20260524.md` | W4 audit marked superseded | ~5K | 🔲 TODO |
| W2.1 | ADG fan-in query | `mv_hotspot_centrality` + `adg_edge_fanin` per candidate | Stale snapshot risk | ~10K | 🔲 TODO |
| W2.2 | Static grep fan-in (tests+CI+product) | `_w11_fanin_scan.py` pattern for 4 areas | Complement ADG | ~10K | 🔲 TODO |
| W2.3 | Verdict table + review packet | `artifacts/governance/quarantine_fanin_matrix_*.json` | Author-Gate if hops→DELETE | ~10K | 🔲 TODO |
| W3.1 | Test migration (pre-delete) | Per W2 MIGRATE rows | dry_run harness, internal e2e | ~15K | 🔲 TODO |
| W3.2 | Gated delete/archive batch | Paths with DELETE_GATE=all checks | Receipt in `artifacts/governance/migration_receipts/` | ~15K | 🔲 TODO |
| W3.3 | Proof + closeout | compileall, contract gates, plan markers | No full-suite pytest requirement | ~10K | 🔲 TODO |

---

## Out Of Scope

- Re-running full `tests/_apps_contract/` (7000+ tests) as a gate; use scoped selectors only
- `agentic_core` `validation_orchestrator` retirement (separate plan; W9/W11 ARCHIVE_CANDIDATE_AFTER_30D)
- `apps_shared` `subatomic_hop_util` signal-stub wiring (W4 NEEDS_DECISION)
- Notion/archive content under gitignored `archives/` (document references only)
- Broad ADG re-index of entire repo (only refresh if W2 fan-in contradicts snapshot)

---

## Wave 1 — Quarantine SSOT reconcile

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — Test/CI/doc alignment only; no runtime product path changes.

**Phases**:
- **W1.1** — Drift inventory | ~8K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — CI + `QUARANTINED_PATHS` sync | ~6K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — Contract test rewrite | ~6K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.4** — SSOT doc addendum | ~5K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Published drift table: path × {doc says | disk | test expects | action}
- `check_apps_rg_runtime_path_inventory.py` `QUARANTINE_DIRS` matches disk (no phantom `apps_rg/reasoning/`, `apps_rg/_quarantine/` unless restored)
- `pytest tests/_apps_contract/test_quarantined_paths_raise_runtime_error.py tests/_apps_contract/test_import_graph_no_quarantine.py -q` → 0 failures
- `python ops_scripts/ci/check_apps_rg_runtime_path_inventory.py` → exit 0 (or documented allowlist update with receipt)

### W1.1 — Drift inventory

**Scope**: Compare four sources without editing product code.

| Source | Path |
|--------|------|
| W7 live registry | [test_apps_rg_deprecated_path_quarantine.py](../tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py) |
| W0A import quarantine | [test_quarantined_paths_raise_runtime_error.py](../tests/_apps_contract/test_quarantined_paths_raise_runtime_error.py) |
| CI inventory | [check_apps_rg_runtime_path_inventory.py](../ops_scripts/ci/check_apps_rg_runtime_path_inventory.py) |
| May W4 audit | [apps_rg_quarantine_u0_packet_coverage_audit.md](../artifacts/apps_rg/apps_rg_quarantine_u0_packet_coverage_audit.md) |

**Commands**:
```bash
python -c "from pathlib import Path; paths=['apps_rg/runtime/dry_run','apps_rg/runtime/internal','apps_rg/integrations/hops','apps_rg/engines','apps_rg/reasoning','apps_rg/_quarantine'];
[print(p, (Path(p).exists())) for p in paths]"
pytest tests/_apps_contract/test_quarantined_paths_raise_runtime_error.py -q --tb=no
```

**Known drift (seed for inventory — verify in W1.1)**:

| Path | W4 audit | Disk (2026-05-24) | Test expectation | W1 action |
|------|----------|-------------------|------------------|-----------|
| `apps_rg/reasoning/` | Quarantined | **Absent** | `test_reasoning_package_removed` | Remove from CI `QUARANTINE_DIRS` |
| `apps_rg/_quarantine/` | 3 stubs | **Absent** | `QUARANTINED_PATHS` lists 3 files | Tests → assert path missing |
| `integrations/gates/online_judges` | Stub | **Absent** | Expect QUARANTINE import error | Test → `ModuleNotFoundError` or remove case |
| `integrations/hops/` | Stub | **Live** | W4 expects QUARANTINE | Reclassify **ACTIVE** or add new quarantine policy |
| `engines/judges/…` | Stub | **Absent** | QUARANTINE import test | Remove or assert absent |
| `runtime/dry_run/` | Quarantine | **Live** (`executive_summary_demo.py`) | KEEP_APPS_RG + harness tests | KEEP until W3 migration |

### W1.2 — CI and import-graph sync

**Files**:
- [check_apps_rg_runtime_path_inventory.py](../ops_scripts/ci/check_apps_rg_runtime_path_inventory.py) — `QUARANTINE_DIRS`, `CANONICAL_QUARANTINED_PATHS`, `DENIED_RUNTIME_SURFACES`
- [test_import_graph_no_quarantine.py](../tests/_apps_contract/test_import_graph_no_quarantine.py) — `QUARANTINED_PATHS`

**Rules**:
- Drop directories that do not exist unless classified `DENIED` (must-not-return)
- Add `apps_rg/integrations/hops/` to **ACTIVE** or explicit `LEGACY` with notice if narrative pipeline remains product-adjacent
- Keep [test_apps_rg_deprecated_path_quarantine.py](../tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py) as W7 SSOT for `dry_run/`, `internal/`

### W1.3 — Contract test rewrite

**Pattern for removed modules** (replace QUARANTINE import tests):
```python
with pytest.raises(ModuleNotFoundError):
    importlib.import_module("apps_rg.integrations.gates.online_judges")
```

**Pattern for live non-product paths** (dry_run): keep env-gated harness tests; document in NON_PRODUCT_PROOF_MARKERS.

**Pattern for hops**: Either (a) remove AG-RGGOV-8 import-block tests and replace with static scan for forbidden hop runners, or (b) re-quarantine hops behind `RuntimeError` stubs — **requires Author-Gate in W2 if (b)**.

### W1.4 — SSOT doc addendum

Emit [docs/reports/apps_rg/quarantine_ssot_reconcile_20260524.md](../docs/reports/apps_rg/quarantine_ssot_reconcile_20260524.md) with:
- Supersedes table (W4 audit sections → current classification)
- Link to W7 registry as **runtime path** SSOT
- Link to W11 DELETE_GATE as **delete authorization** SSOT

---

## Wave 2 — Fan-in matrix (four areas)

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — ADG queries | ~10K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Static importer scan | ~10K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** — Verdict table | ~10K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Artifact: `artifacts/governance/quarantine_fanin_matrix_20260524.json` + `.md`
- Each row: `path`, `fan_in_adg`, `fan_in_static_tests`, `fan_in_product`, `classification`, `verdict` ∈ {KEEP, KEEP_TEST_SUPPORT, MIGRATE_THEN_DELETE, DELETE_READY, DEFER}
- Explicit note where ADG snapshot predates commit `0f13fb3e69`

### W2.1 — ADG fan-in

**Candidates** (directory or file roots):

| ID | Path | W11 prior |
|----|------|-----------|
| C1 | `apps_rg/runtime/dry_run/` | QUARANTINE_30D / KEEP_APPS_RG |
| C2 | `apps_rg/runtime/internal/` | TEST_SUPPORT_ONLY |
| C3 | `apps_rg/integrations/hops/` | QUARANTINE (stale) → remeasure |
| C4 | `apps_rg/engines/` (4 `.py` files) | Partial live + unit tests |

**Commands**:
```bash
# After optional re-index:
python docs/reports/agent_inventory/_w11_fanin_scan.py  # adapt candidate list
# Or sqlite:
# SELECT resolved_path, fan_in, fan_out FROM mv_hotspot_centrality ...
```

### W2.2 — Static scan

Grep importers in `apps_rg/`, `tests/`, `ops_scripts/`, `agentic_core/runtime/entry/` for:
- `runtime.dry_run`, `runtime.internal`, `integrations.hops`, `apps_rg.engines`

Cross-check [tests/apps_rg/integrations/hops/](../tests/apps_rg/integrations/hops/), [tests/unit/apps_rg/engines/](../tests/unit/apps_rg/engines/), [test_demo_harness_fail_closed.py](../tests/unit/apps_rg/test_demo_harness_fail_closed.py).

### W2.3 — Verdict table (review packet)

| Verdict | Meaning | W3 allowed? |
|---------|---------|-------------|
| DELETE_READY | All W11 DELETE_GATE checks pass | Yes |
| MIGRATE_THEN_DELETE | Product fan-in 0; tests/CI remain | W3.1 then W3.2 |
| KEEP_TEST_SUPPORT | Non-product but tested | No delete |
| KEEP | Product or narrative pipeline | No delete |
| DEFER | Author-Gate or successor plan | No delete |

**Human review checkpoint** before W3: approve rows with DELETE_READY or MIGRATE_THEN_DELETE only.

---

## Wave 3 — W11-gated delete / archive

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED_IF_DELETE
CHECKPOINT: C

**Authorization**: Author-Gate when W2 recommends deleting `hops/` or any path with product fan-in > 0.

**Phases**:
- **W3.1** — Test migration | ~15K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Delete/archive batch | ~15K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.3** — Proof + receipt | ~10K | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**W11 DELETE_GATE checklist** (all required per path):

- [ ] ADG/static import fan-in = 0 (product + tests + CI)
- [ ] No pytest imports module under delete
- [ ] No `python -m apps_rg` default path references
- [ ] No runtime proof receipt names path as SSOT
- [ ] Rollback plan documented
- [ ] `python -m compileall agentic_core apps_rg apps_shared -q` exit 0
- [ ] Scoped W10/boundary tests pass
- [ ] Migration receipt: `artifacts/governance/migration_receipts/<ts>_quarantine_gated_delete.json`

**Acceptance**:
- Zero paths deleted without DELETE_READY verdict from W2
- Post-delete: `check_no_shadow_spine.py` exit 0
- Scoped pytest (wave-scoped list from W2 matrix) → PASS
- Closeout receipt: `docs/reports/apps_rg/quarantine_gated_delete_closeout_receipt.md`

### W3.1 — Test migration (expected hotspots)

| Area | Tests to migrate/remove before delete |
|------|--------------------------------------|
| `dry_run/` | `test_demo_harness_fail_closed.py`, `test_section_evidence_w7a_shadow_proof_boundary.py` |
| `internal/` | E2E/preflight importing `lane_batch`, assemblers (grep `runtime.internal`) |
| `hops/` | `tests/apps_rg/integrations/hops/*` — only if verdict is DELETE |
| `engines/` | `tests/unit/apps_rg/engines/*` — only if verdict is DELETE |

### W3.2 — Likely outcomes (hypothesis — W2 confirms)

| Path | Expected verdict | Notes |
|------|------------------|-------|
| `dry_run/` | MIGRATE_THEN_DELETE | Demo env-gated; not product PASS |
| `internal/` | KEEP_TEST_SUPPORT or MIGRATE | Post-lane helpers; hard-delete receipt classified TEST_SUPPORT |
| `hops/` | KEEP or DEFER | Currently imports OK; narrative tests active |
| `engines/` | KEEP or MIGRATE | 4 files + unit tests; not W4 stubs |

**Do not delete** env hatches (`stub_only`, `legacy_full_resume`, mock-judge flags) — policy KEEP per W11.

### W3.3 — Proof commands

```bash
python -m compileall agentic_core apps_rg apps_shared apps_eval -q
python ops_scripts/ci/check_no_shadow_spine.py
python ops_scripts/ci/check_apps_rg_runtime_path_inventory.py
pytest tests/_apps_contract/test_apps_rg_deprecated_path_quarantine.py tests/_apps_contract/test_quarantined_paths_raise_runtime_error.py tests/_apps_contract/test_import_graph_no_quarantine.py -q
```

---

## Gap Register

**GAP-1: W4 quarantine audit stale vs disk**
- 132 stub claim; many paths hard-deleted or un-stubbed (hops live)
- Impact: Wrong delete list if audit used without W1 reconcile

**GAP-2: ADG snapshot vs post–wave-A–D tree**
- `05232026_1851` predates dead-code commit; re-index before W2 verdicts
- Impact: False DELETE_READY if fan-in not refreshed

**GAP-3: `archives/` gitignored**
- W4 originals not in repo; cannot verify MANIFEST from git
- Impact: Archive-only rollback relies on local/archive store

**GAP-4: hops governance ambiguity**
- AG-RGGOV-8 tests expect QUARANTINE; module imports successfully
- Impact: W1.3 may need Author-Gate (re-stub vs reclassify ACTIVE)

---

## Definition of Done

DoD-1: W1 drift inventory on disk at `docs/reports/apps_rg/quarantine_ssot_reconcile_20260524.md`
- Evidence: file exists; table covers ≥10 path rows
- Status: TODO

DoD-2: CI/quarantine contract tests aligned with disk
- Evidence: `pytest tests/_apps_contract/test_quarantined_paths_raise_runtime_error.py tests/_apps_contract/test_import_graph_no_quarantine.py -q` → 0 failed
- Status: TODO

DoD-3: Fan-in matrix artifact published
- Evidence: `artifacts/governance/quarantine_fanin_matrix_20260524.json` with verdict per C1–C4
- Status: TODO

DoD-4: W3 deletes only DELETE_READY paths (or explicit DEFER with no deletes)
- Evidence: migration receipt JSON + `quarantine_gated_delete_closeout_receipt.md`; git diff scoped to approved paths
- Status: TODO

DoD-5: Plan registered in Notion Plans DB with Status trackable
- Evidence: `PLAN_CREATED` marker; Notion row Slug=`apps-rg-quarantine-ssot-fanin-delete-c7e4a1`
- Status: TODO

### Verification vs deferral

| Item | Verify in this plan | Defer |
|------|---------------------|-------|
| Quarantine SSOT / CI / contract tests | W1 | — |
| Fan-in for 4 areas | W2 | — |
| Gated delete | W3 | — |
| `validation_orchestrator` archive | — | Separate core plan |
| Full apps_contract suite | — | Scoped pytest only |
| `apps-rg-legacy-dependency-burndown` overlap | Coordinate | Merge if duplicate scope discovered |

---

## Marker Quick Reference

```
PLAN_CREATED: slug=apps-rg-quarantine-ssot-fanin-delete-c7e4a1 path=.cursor/plans/apps-rg-quarantine-ssot-fanin-delete-c7e4a1.md status=Not Started
WAVE_START: plan=apps-rg-quarantine-ssot-fanin-delete-c7e4a1 wave=1
WAVE_COMPLETE: plan=apps-rg-quarantine-ssot-fanin-delete-c7e4a1 wave=1 note="+N tests, N files, scope=quarantine-ssot-reconcile"
WAVE_COMPLETE: plan=apps-rg-quarantine-ssot-fanin-delete-c7e4a1 wave=2 note="fanin matrix artifact"
WAVE_COMPLETE: plan=apps-rg-quarantine-ssot-fanin-delete-c7e4a1 wave=3 note="gated delete receipt"
PLAN_COMPLETE: plan=apps-rg-quarantine-ssot-fanin-delete-c7e4a1 note="quarantine SSOT + fan-in + gated delete"
```

---

## References

- [w11_gated_archive_delete_plan.md](../docs/reports/agent_inventory/w11_gated_archive_delete_plan.md) — DELETE_GATE / ARCHIVE_GATE
- [deprecation_quarantine_plan.md](../docs/reports/agent_inventory/deprecation_quarantine_plan.md) — classification legend
- [w6_w9_quarantine_and_e2_boundary.md](../docs/reports/agent_inventory/w6_w9_quarantine_and_e2_boundary.md) — W7 path classes
- [hard_delete_residual_shadow_module_paths_closeout_receipt.md](../docs/reports/apps_rg/hard_delete_residual_shadow_module_paths_closeout_receipt.md) — internal/ dispatch state
