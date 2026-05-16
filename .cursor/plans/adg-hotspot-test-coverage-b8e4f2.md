---
plan_id: adg-hotspot-test-coverage-b8e4f2
plan_type: governance
touches_agentic_core: true
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# ADG hotspot testing — coverage closure plan

Turn ADG-derived hotspot and test-gap signals into **appropriate** coverage: regenerated SSOT snapshots, behavioral tests for medium fan-in gaps (P3), app top fan-in mapping, optional runtime attestation, and CI ratchet verification. Baseline narrative: prior review of `docs/reports/test_hotspot_gaps_04252026.md`, `docs/reports/adg/*_hotspots_*.md`, and `tools/analysis/hotspot_coverage_report.py`.

> **plan_id discipline**: filename stem = `adg-hotspot-test-coverage-b8e4f2`; wave markers use `plan=adg-hotspot-test-coverage-b8e4f2`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: PARTIAL  
CURRENT_WAVE: W4  
LAST_COMPLETED_WAVE: W3  
LAST_UPDATED: 2026-05-16  
W4A_W42_RATCHET_VERIFICATION: PARTIAL  

**Child plan (L5 fan-in reduction — follow-on):** `.cursor/plans/l5-fanin-architecture-reduction-e7c4a2.md` — **planning + future implementation** for the **three** W4A L5 ratchet hotspots (`valid_architecture_regression`); **excludes** H2/sentinel lineage (separate work). Notion: `36227693-f55c-81fc-a35b-dea4f39b11d8`.

**Child plan (W4A remediation):** `.cursor/plans/ratchet-and-adg-pipeline-remediation-c3e9a7.md` — **PARTIAL overall**; waves **W1–W3 complete** for scoped classification + fixes; **L5 fan-in regressions** and **H2 prior lineage** remain open. Notion: `36227693-f55c-81e0-ac0d-f4e6a3e2475a`.

**Child remediation result (closeout 2026-05-16):**

| Child wave | Result | Evidence / outcome |
|------------|--------|---------------------|
| **W1** | Complete | All **3** L5 fan-in deltas classified **`valid_architecture_regression`**; no source/ratchet edits — `child_w1_l5_fanin_regression_triage.md` |
| **W2** | Partial | H2 **blocked**: prior resolver selects **`adg_indexed_99999999_9999.sqlite`** (no `mv_hotspot_centrality`); no compatible prior in-repo — `child_w2_adg_snapshot_lineage_h2_preconditions.md` |
| **W3** | Complete | L5 script **repo-root** runnable without `PYTHONPATH` (`sys.path` bootstrap); **verdict semantics unchanged** (L5 exit **1**, G **0**, H2 **1**, AUDIT-2 **0**) — `child_w3_ci_invocation_normalization.md` |

**W4A narrative:** `artifacts/test_inventory/w4_ci_ratchet_verification.md` **§8 Addendum** — L5 **no longer** requires ad hoc `PYTHONPATH`; L5 ratchet still **FAIL** on same 3 paths; H2 still **blocked** on prior stub.

**Unsettled (not PASS):** L5 architecture/baseline governance; ADG current/prior pairing for H2; on-disk `l5_fanin_ratchet.json` may be absent (`DEFAULT_RATCHET` fallback). Closeout rollup: `artifacts/test_inventory/ratchet_child_closeout_summary.md`.

**Not emitted:** `PLAN_COMPLETE` for this parent; no additional parent `WAVE_COMPLETE` lines beyond existing W1–W3 (W4 remains **PARTIAL**).

WAVE_COMPLETE: plan=adg-hotspot-test-coverage-b8e4f2 wave=1 note="evidence=artifacts/test_inventory/w1_adg_hotspot_coverage_evidence.md +0 tests +4 files scope=w1-baseline"  
WAVE_COMPLETE: plan=adg-hotspot-test-coverage-b8e4f2 wave=2 note="evidence=artifacts/test_inventory/w2_basename_collision_audit.md +27 tests tests/agentic_core/test_p3_w2_hotspot_behavior.py +4 files scope=w2-p3-behavior"  
WAVE_COMPLETE: plan=adg-hotspot-test-coverage-b8e4f2 wave=3 note="artifacts/test_inventory/w3_app_hotspot_test_surface_map.md +4 behavioral tests tests/unit/apps_underwriting_ai/validators/test_validators.py pytest exit 0 scope=w3-app-mapping-p4-policy"  

---

## Context (SCQA)

- **Situation** — Static ADG reports exist (`test_hotspot_gaps`, per-app hotspot markdown). The joined **hotspot × coverage** report is produced by `tools/analysis/hotspot_coverage_report.py` when snapshot contains `mv_hotspot_coverage_risk` (see sibling plan `hotspot-coverage-pipeline-c4e8d2`). Many edges appear static-only until runtime OTel fills the three-bucket view.
- **Complication** — Basename match (`test_<leaf>.py`) is not proof of behavior; P3 lists modules with fan-in 2–4 still worth closing; app hotspot reports list **dependency heat**, not pytest ownership.
- **Question** — How do we ensure **appropriate** tests for the highest-value hotspots without mistaking file naming for coverage?
- **Answer** — Regenerate SSOT, consume **priority bands** from `mv_hotspot_coverage_risk` when available, close P3 with **import-correct** behavioral tests, map app fan-in to **canonical test surfaces**, optionally improve runtime attestation, and keep **ratchet gates** honest.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | Baseline ADG + hotspot×coverage artifact | ✅ DONE | — | evidence + report + log |
| W2 | Agentic_core P3 gaps + collision audit | ✅ DONE | +27 | `test_p3_w2_hotspot_behavior.py` + audit md + 2 core fixes |
| W3 | App hotspots → canonical tests + P4 policy | ✅ DONE | +4 (validators composite) | `w3_app_hotspot_test_surface_map.md` + `test_validators.py` |
| W4 | Runtime attestation (optional) + CI ratchets | ⚠️ PARTIAL | — | `w4_ci_ratchet_verification.md` (W4A W4.2 only) |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Regenerate ADG snapshot | ✅ DONE |
| W1.2 | Run `hotspot_coverage_report.py`; archive snapshot id | ✅ DONE |
| W1.3 | Regenerate or update committed gap markdown (optional) | 🔲 DEFERRED |
| W2.1 | Implement tests for 17 P3 modules (see test_hotspot_gaps) | ✅ DONE |
| W2.2 | Basename collision audit + fixes | ✅ DONE |
| W3.1 | Per `docs/reports/adg/apps_*_hotspots_*.md`: map top fan-in paths | ✅ DONE |
| W3.2 | Add or extend tests under `tests/unit/<app>/`, `tests/<app>/`, contract | ✅ DONE |
| W3.3 | P4 (fan-in 1) triage policy — churn/layer-based queue | ✅ DONE |
| W4.1 | Optional: OTel/runtime ADG to reduce static-only bucket | 🔲 TODO |
| W4.2 | Verify `check_l5_hotspot_fanin_ratchet` and related gates | ⚠️ PARTIAL (evidence: `w4_ci_ratchet_verification.md`; L5 FAIL; H2 blocked) |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 | W1.1–W1.3 | Latest `artifacts/adg/*.sqlite`; `hotspot_coverage_priority.md`; snapshot provenance | ~4000 | `generate_full_adg` may fail ratchet | ✅ DONE | Evidence: `w1_adg_hotspot_coverage_evidence.md`; report at `artifacts/test_inventory/hotspot_coverage_priority.md` (explicit `--adg`; regen failed P2 ratchet, located snapshot) |
| W2 | W2.1–W2.2 | Close P3 test gaps; collision audit | ~9000 | seed list from `test_hotspot_gaps` | ✅ DONE | `tests/agentic_core/test_p3_w2_hotspot_behavior.py`; `artifacts/test_inventory/w2_basename_collision_audit.md`; pytest 27 passed (`-o addopts=`) |
| W3 | W3.1–W3.3 | App fan-in heat → owned tests; P4 policy | ~7000 | App hotspot markdown current for targeted apps | ✅ DONE | `artifacts/test_inventory/w3_app_hotspot_test_surface_map.md`; P4 policy section; +4 `DecisionPacketValidator` tests; no `apps_*/tests/` |
| W4 | W4.1–W4.2 | Runtime triangulation optional; CI | ~5000 | OTel/runtime store available if W4.1 executed | ⚠️ PARTIAL | W4A: L5 hotspot fan-in ratchet **FAIL** on `adg_indexed_05162026_0649.sqlite`; G watchlist + AUDIT-2 pass; H2 **blocked** (prior sentinel lacks `mv_hotspot_centrality`); L5 **import hazard cleared** (Child W3 — repo root, no `PYTHONPATH`); W4.1 not run |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| W1.1 | Regenerate ADG | `tools/generate/`, `artifacts/adg/` | P2 ratchet blocked regen | ~1500 | ✅ DONE (attempted; fail — see evidence) |
| W1.2 | Hotspot × coverage report | `tools/analysis/hotspot_coverage_report.py`, `artifacts/test_inventory/` | Default glob picks stub sqlite | ~1000 | ✅ DONE (`--adg` dated snapshot) |
| W1.3 | Refresh static gap markdown | `docs/reports/test_hotspot_gaps_*.md` | optional | ~1500 | 🔲 DEFERRED |
| W2.1 | P3 module tests | `tests/agentic_core/test_p3_w2_hotspot_behavior.py` | Core fixes for testability | ~5000 | ✅ DONE |
| W2.2 | Collision audit | `artifacts/test_inventory/w2_basename_collision_audit.md` | 3 basename/routing false positives | ~4000 | ✅ DONE |
| W3.1 | App hotspot inventory | `docs/reports/adg/apps_*_hotspots_*.md` | N apps × top symbols | ~2000 | ✅ DONE |
| W3.2 | App test mapping | `tests/unit/<app>/`, `tests/<app>/`, `_apps_contract` | Provider/network deps | ~3000 | ✅ DONE |
| W3.3 | P4 triage policy | planning only + backlog IDs | 230 modules — scope control | ~2000 | ✅ DONE |
| W4.1 | Runtime attestation | `system_learning/runtime_adg`, OTel | Optional; decoupled | ~3000 | 🔲 TODO |
| W4.2 | CI ratchet verification | `ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py`, contract gates | Env-specific | ~2000 | ⚠️ PARTIAL — see `artifacts/test_inventory/w4_ci_ratchet_verification.md` |

---

## Out of scope

- Weakening gates or schemas to pass tests.
- Full elimination of all P4 (fan-in 1) gaps in one pass.
- Replacing sibling plan `hotspot-coverage-pipeline-c4e8d2` (coverage ingest / MV build) unless this plan explicitly extends it.

---

## Wave 1 — Baseline SSOT and priority report

WAVE_ID: W1  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  

**W1 evidence**: `artifacts/test_inventory/w1_adg_hotspot_coverage_evidence.md`

**Outcome**:

- Regenerate: **failed** (`python tools/generate/generate_full_adg.py` exit `1`, P2 ratchet 178 > 162).
- Locate: **`artifacts/adg/adg_indexed_05162026_0649.sqlite`** (Phase F `mv_hotspot_coverage_risk` **present**).
- Report: `python tools/analysis/hotspot_coverage_report.py --adg artifacts/adg/adg_indexed_05162026_0649.sqlite --out artifacts/test_inventory/hotspot_coverage_priority.md` → exit `0`, `Wrote: artifacts/test_inventory/hotspot_coverage_priority.md`, `total nodes scored: 4104`. Coverage ingest still **absent** (0 measured) — see report warnings; `hotspot-coverage-pipeline-c4e8d2` still gates meaningful bands.

---

## Wave 2 — Agentic_core P3 + collisions

WAVE_ID: W2  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  

**Phases**: W2.1–W2.2  

**Evidence**: `artifacts/test_inventory/w2_basename_collision_audit.md`  

**Commands** (exact):

```text
python -m pytest tests/agentic_core/test_p3_w2_hotspot_behavior.py -q --tb=short -o addopts=
```

→ **exit code 0**, **27 passed** (2026-05-16 local).

**Files**:

- `tests/agentic_core/test_p3_w2_hotspot_behavior.py` — behavioral tests; canonical imports per P3 row.
- `agentic_core/L2_execution/types/ml_write_intent_types.py` — fix `execute()` guardrail target (`intent.target_path` AttributeError).
- `agentic_core/L1_cognition/reasoning/reasoning_plan.py` — import `get_clock` for `plan_epoch` default (NameError on `ReasoningPlan.create`).

**Remaining gaps** (explicit, not W2 scope): async/query_planner LLM paths; `choose_execution_strategy` full stack; live Redis ctor; `ReasoningContext.create()` LayerSegment constant mismatch (test avoided factory).

---

## Wave 3 — Apps + P4 policy

WAVE_ID: W3  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  

**Phases**: W3.1–W3.3  

**Primary artifact**: `artifacts/test_inventory/w3_app_hotspot_test_surface_map.md`

**Commands** (exact):

```text
Get-ChildItem -Path "docs/reports/adg" -Filter "apps_*_hotspots_*.md" | Select-Object -ExpandProperty Name
python -m pytest tests/unit/apps_underwriting_ai/validators/test_validators.py -q --tb=short -o addopts=
```

→ PowerShell listing **exit 0** (2026-05-16 local).  
→ pytest **exit 0**, **5 passed** (`-o addopts=` clears inherited `pytest.ini` addopts).

**Files**:

- `artifacts/test_inventory/w3_app_hotspot_test_surface_map.md` — per-app hotspot mapping, `apps_rg` missing-report note, `apps_exec` empty ADG tables note, **P4 triage policy** section.
- `tests/unit/apps_underwriting_ai/validators/test_validators.py` — **4 behavioral tests** for `DecisionPacketValidator` (skip aggregation, blocking errors, rubric warning non-blocking).

**Acceptance** — met:

- Six apps with `apps_*_hotspots_*.md` mapped (`*_20260510T212855Z.md` slice); canonical surface per row or explicit `skip_with_reason`.
- P4 closure explicitly deferred; ranked triage policy recorded.
- No `apps_*/tests/` paths; no gate/ratchet edits.

**Remaining gaps** (explicit, not W3 scope):

- `apps_rg` has no ADG hotspot markdown in `docs/reports/adg/`.
- `apps_exec` hotspot report has empty fan-in/fan-out (snapshot/report gap) — spine mapped via `tests/governance/test_apps_exec_spine.py`.
- P2 ADG ratchet still blocks `generate_full_adg`; measured coverage ingest still absent.

---

## Wave 4 — Runtime (optional) + CI

WAVE_ID: W4  
WAVE_STATUS: PARTIAL  
WAVE_COMPLETE: NO  
AUTHORIZATION_STATUS: NOT_REQUIRED  

**Phases**: W4.1–W4.2  

**W4A (W4.2 only, 2026-05-16)** — evidence: **`artifacts/test_inventory/w4_ci_ratchet_verification.md`**

| Gate | Command (repo root) | Exit | Outcome |
|------|---------------------|------|---------|
| L5 help | `python ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py --help` | 0 | PASS |
| L5 gate | `python ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py` (repo root; `PYTHONPATH` unset) | 1 | **FAIL** — 3 fan-in regressions vs `DEFAULT_RATCHET` / `.cursor/config/l5_fanin_ratchet.json` on `adg_indexed_05162026_0649.sqlite` (Child W3: **no** `ModuleNotFoundError`) |
| G watchlist delta | `python ops_scripts/ci/check_graph_watchlist_delta.py` | 0 | PASS |
| H2 fan-in collapse | `python ops_scripts/ci/check_w6_fanin_collapse.py` | 1 | **BLOCKED** — **prior** `adg_indexed_99999999_9999.sqlite` lacks `mv_hotspot_centrality` |
| AUDIT-2 high fan-in | `python ops_scripts/ci/check_observability_on_high_fanin.py` | 0 | PASS (ratchet at baseline) |

**Historical (pre–Child W3):** L5 without `PYTHONPATH` raised `ModuleNotFoundError` — see `w4_ci_ratchet_verification.md` **§2–§3** and **§8** addendum.

**W4.1:** not executed (runtime attestation deferred).

**Acceptance (wave-level):** not met — L5 hotspot fan-in ratchet is **not** green. Full W4 **PASS** requires ratchet green **or** explicit governed baseline update (out of W4A scope).

---

## Gap Register

- **G1**: `mv_hotspot_coverage_risk` absent in snapshot → priority report cannot rank by coverage; unblock via `hotspot-coverage-pipeline-c4e8d2` or document manual prioritization.
- **G2**: Basename collisions obscure true gaps → W2.2 must resolve or annotate.
- **G3**: App tests need live providers → use contracts + fixtures; keep deterministic apps_rg content law where applicable.
- **G4**: Runtime bucket empty → static-only classification dominates; do not over-interpret until W4.1.
- **G5**: `apps_rg` has no `apps_rg_hotspots_*.md` under `docs/reports/adg/` → W3 mapping deferred for that app.
- **G6**: `apps_exec` ADG hotspot tables empty in `*_20260510T212855Z.md` → rely on governance spine tests until snapshot/report fixed.
- **G7**: **L5 hotspot fan-in ratchet regressions** on latest snapshot (`runtime_gates/types.py`, `structure_blueprint/ssot.py`, `ingress_envelope_check.py`) — see `w4_ci_ratchet_verification.md`.
- **G8**: **H2 fan-in collapse** gate errors on **prior** snapshot (`mv_hotspot_centrality` missing) — refresh prior ADG or align gate preconditions.

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|-----------|--------------|--------|
| DoD-1 | Plan file on disk (this path) | `.cursor/plans/adg-hotspot-test-coverage-b8e4f2.md` exists | DONE |
| DoD-2 | Notion Plans DB row created | `create_plan_in_notion` → `page_id=36227693-f55c-81ec-af54-c49132313ff2`, `Status=Not Started` | DONE |
| DoD-3 | Report tool smoke | `python tools/analysis/hotspot_coverage_report.py --help` exits 0 | DONE |
| DoD-4 | W1 complete: ADG path + report artifact or documented skip | `artifacts/test_inventory/w1_adg_hotspot_coverage_evidence.md` | DONE |
| DoD-5 | W2–W4 acceptance criteria met | W2–W3 done; W4 **PARTIAL** — W4.2 verified, L5 ratchet FAIL; H2 blocked; Child W3 L5 invocation fixed | PARTIAL |

**Verification-vs-Deferral**

| Item | Verify now | Defer |
|------|------------|--------|
| Full P4 closure (230 modules) | — | Yes — use triage policy W3.3 |
| Runtime triplet attestation | — | Optional W4.1 |
| Regenerating every historical `docs/reports/adg/*` markdown | Partial — refresh when snapshot changes | Full archive optional |

---

## Marker Quick Reference

```
WAVE_START: plan=adg-hotspot-test-coverage-b8e4f2 wave=<N>
WAVE_COMPLETE: plan=adg-hotspot-test-coverage-b8e4f2 wave=<N> note="+N tests, N files, scope=<summary>"
PLAN_COMPLETE: plan=adg-hotspot-test-coverage-b8e4f2 note="<final outcome>"
```

---

## Related artifacts

- `docs/reports/test_hotspot_gaps_04252026.md`
- `docs/reports/adg/*_hotspots_20260510T212855Z.md`
- `docs/reports/adg/THREE_BUCKET_GAP_REPORT.md`
- `.cursor/plans/hotspot-coverage-pipeline-c4e8d2.md`
- `tools/analysis/hotspot_coverage_report.py`
- `artifacts/test_inventory/w4_ci_ratchet_verification.md`
- `artifacts/test_inventory/ratchet_child_closeout_summary.md`
- **Child (L5 architecture):** `.cursor/plans/l5-fanin-architecture-reduction-e7c4a2.md`
- **Child (W4A plumbing):** `.cursor/plans/ratchet-and-adg-pipeline-remediation-c3e9a7.md` (W4A ratchet + ADG pipeline remediation; **PARTIAL** closeout)

PLAN_CREATED: slug=adg-hotspot-test-coverage-b8e4f2 path=.cursor/plans/adg-hotspot-test-coverage-b8e4f2.md status=Not Started  
NOTION_PLAN_PAGE_ID: 36227693-f55c-81ec-af54-c49132313ff2
