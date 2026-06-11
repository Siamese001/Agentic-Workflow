---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\ratchet-and-adg-pipeline-remediation-c3e9a7.md'
original_relative_path: '_archive\\2026-05\\ratchet-and-adg-pipeline-remediation-c3e9a7.md'
source_sha256: e25d4734b6ea88804bf8caedf326da25fbe11df7f7798312f8f96507e719be23
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: ratchet-and-adg-pipeline-remediation-c3e9a7
plan_type: governance
parent_plan_id: adg-hotspot-test-coverage-b8e4f2
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# Ratchet and ADG pipeline remediation (W4A blockers)

Close **W4A CI ratchet / ADG plumbing gaps** raised under parent plan `adg-hotspot-test-coverage-b8e4f2`: L5 fan-in regressions, broken **prior** snapshot lineage for H2, and **repo-root** invocation of `check_l5_hotspot_fanin_ratchet.py` without ad hoc `PYTHONPATH`.

> **plan_id discipline**: filename stem = `ratchet-and-adg-pipeline-remediation-c3e9a7`; wave markers use `plan=ratchet-and-adg-pipeline-remediation-c3e9a7`.

---

## Parent linkage (W4A blockers)

| Parent | Role |
|--------|------|
| `.cursor/plans/adg-hotspot-test-coverage-b8e4f2.md` | **PARTIAL** at W4A — `W4A_W42_RATCHET_VERIFICATION: PARTIAL` |

**Primary evidence (read-only for this plan):**

| Artifact | Content |
|----------|---------|
| `artifacts/test_inventory/w4_ci_ratchet_verification.md` | L5 FAIL (3 paths), H2 prior-DB missing `mv_hotspot_centrality` on sentinel prior, G watchlist + AUDIT-2 pass; **addendum:** L5 repo-root invocation fixed (Child W3 — no `PYTHONPATH` required) |
| `artifacts/test_inventory/w1_adg_hotspot_coverage_evidence.md` | P2 `generate_full_adg` ratchet **178 > 162** |
| `artifacts/test_inventory/w3_app_hotspot_test_surface_map.md` | apps_rg / apps_exec reporting gaps (context only) |

**Regressed paths (exact, from W4A)** on snapshot `artifacts/adg/adg_indexed_05162026_0649.sqlite` vs `.cursor/config/l5_fanin_ratchet.json`:

1. `agentic_core/L5_safety/runtime_gates/types.py` — baseline **198**, current **206** (+8)
2. `agentic_core/L5_safety/config/structure_blueprint/ssot.py` — baseline **80**, current **84** (+4)
3. `agentic_core/L5_safety/enforcement/ingress_envelope_check.py` — baseline **49**, current **50** (+1)

**Follow-on child (L5 architecture reduction — excludes H2/sentinel):** `.cursor/plans/l5-fanin-architecture-reduction-e7c4a2.md`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: PARTIAL  
CURRENT_WAVE: —  
LAST_COMPLETED_WAVE: W3  
LAST_UPDATED: 2026-05-16  

WAVE_COMPLETE: plan=ratchet-and-adg-pipeline-remediation-c3e9a7 wave=1 note="artifacts/test_inventory/child_w1_l5_fanin_regression_triage.md +0 ratchet/source edits scope=w1-l5-classification"  
WAVE_COMPLETE: plan=ratchet-and-adg-pipeline-remediation-c3e9a7 wave=2 note="artifacts/test_inventory/child_w2_adg_snapshot_lineage_h2_preconditions.md H2_exit_1 root=99999999_prior_stub scope=w2-lineage-classification"  
WAVE_COMPLETE: plan=ratchet-and-adg-pipeline-remediation-c3e9a7 wave=3 note="artifacts/test_inventory/child_w3_ci_invocation_normalization.md sys.path bootstrap check_l5 PYTHONPATH=unset L5_exit_1 regressions H2_exit_1 prior_stub"  

---

## Context (SCQA)

- **Situation** — Parent W4A verified CI gates: graph watchlist delta and observability-on-high-fan-in pass; L5 hotspot fan-in ratchet **fails** on three L5 paths; H2 fan-in collapse **errors** on missing MV in **prior** sqlite. **W3:** `check_l5_hotspot_fanin_ratchet.py` now runs from repo root **without** manual `PYTHONPATH` (see `child_w3_ci_invocation_normalization.md`). Coverage ingest remains absent; `hotspot_coverage_priority.md` is not measured-coverage truth.
- **Complication** — Ratchet failure may be real architectural drift, ADG indexer/schema drift, or artifact lineage skew; H2 needs two **real** compatible snapshots; developers run scripts as `python ops_scripts/...` from repo root.
- **Question** — How do we **classify** L5 fan-in deltas, **repair** ADG current/prior pairing for H2, and **normalize** invocation—without weakening gates or thresholds?
- **Answer** — Evidence-first triage (W1), canonical snapshot pipeline alignment (W2), smallest-safe dispatch fix or documented canonical command (W3); baseline changes only after classified proof and governance (out of scope for silent threshold edits).

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Tests Added | Files Changed |
|------|-------|--------|-------------|---------------|
| W1 | L5 fan-in regression triage | ✅ DONE | — | `child_w1_l5_fanin_regression_triage.md` |
| W2 | ADG current/prior snapshot lineage | ⚠️ PARTIAL | n/a | `child_w2_adg_snapshot_lineage_h2_preconditions.md` (H2 still exit **1**) |
| W3 | CI invocation normalization | ✅ DONE | n/a | `check_l5_hotspot_fanin_ratchet.py` + `child_w3_ci_invocation_normalization.md` |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Lock W4A numbers + snapshot id + ratchet file revision | ✅ DONE |
| W1.2 | Per-path fan-in delta attribution (ADG queries / edge classes) | ✅ DONE |
| W1.3 | Classification matrix + proof bar for any baseline update | ✅ DONE |
| W2.1 | Prior snapshot resolver + schema inspect (`mv_hotspot_centrality`) | ✅ DONE |
| W2.2 | Document canonical generation path for indexed ADG + MV phase | ✅ DONE |
| W2.3 | Paired snapshot procedure; H2 green on real pair | ⚠️ BLOCKED (no 2nd real indexed snapshot; stub as prior) |
| W3.1 | Inventory `sys.path` / `-m` patterns in `ops_scripts/ci` | ✅ DONE |
| W3.2 | Choose implementation: path bootstrap vs module entry vs doc-only | ✅ DONE (`REPO_ROOT` insert; match sibling gates) |
| W3.3 | Record canonical command; verify from clean shell | ✅ DONE (`child_w3_ci_invocation_normalization.md`) |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|------------:|-------------|--------|------------------|
| W1 | W1.1–W1.3 | Classify 3 L5 regressions | ~4000 | ADG sqlite queryable | ✅ DONE | `artifacts/test_inventory/child_w1_l5_fanin_regression_triage.md`; **no** threshold edits |
| W2 | W2.1–W2.3 | Real prior/current ADG pair | ~5000 | P2 may still block regen until separately addressed | ⚠️ PARTIAL | Root cause documented (`prior_snapshot` vs `latest_sqlite` asymmetry + `99999999` stub); **H2 still fails** exit 1 until second compatible snapshot or operational stub removal / code fix (future) |
| W3 | W3.1–W3.3 | Repo-root runnable L5 check | ~2500 | Smallest change preferred | ✅ DONE | `check_l5_hotspot_fanin_ratchet.py` inserts `REPO_ROOT` like other W4A gates; verification in `child_w3_ci_invocation_normalization.md` (L5 still exit **1** on 3 regressions) |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|------------:|--------|
| W1.1 | Evidence lock | W4A artifact, sqlite, `l5_fanin_ratchet.json` | Stale copy/paste | ~800 | ✅ DONE |
| W1.2 | ADG attribution | `adg_sqlite` / sqlite queries on fan-in edges | Noise vs real deps | ~2000 | ✅ DONE |
| W1.3 | Classification + proof | plan section, optional ledger note | Baseline politics | ~1200 | ✅ DONE |
| W2.1 | Prior DB forensics | `ops_scripts/ci/_adg_snapshot_diff.py`, `artifacts/adg/` | Old partial snapshots | ~1500 | ✅ DONE |
| W2.2 | Generator truth | `tools/generate/generate_full_adg.py`, `phase_a_path_authority.py` MV | P2 blocked regen | ~2000 | ✅ DONE |
| W2.3 | Paired runbook | ops runbook or plan appendix | No synthetic DBs | ~1500 | ⚠️ PARTIAL |
| W3.1 | Dispatch audit | `ops_scripts/ci/*.py` import patterns | Inconsistent | ~600 | ✅ DONE |
| W3.2 | Decision | `check_l5_hotspot_fanin_ratchet.py` `sys.path` | Scope creep | ~900 | ✅ DONE |
| W3.3 | Verification | `child_w3_ci_invocation_normalization.md` | Windows vs POSIX | ~1000 | ✅ DONE |

---

## Out of scope

- Weakening gates, schemas, **ratchet JSON ceilings**, or CI enforcement thresholds.
- Fixing unrelated **P2** antipatterns except where W1 classification **explicitly** ties an L5 delta to a P2-class fix (separate governed work).
- **W4B** runtime attestation / OTel triangulation.
- Claiming **measured coverage** until coverage ingest exists.
- Creating `apps_rg_hotspots_*.md` or filling empty `apps_exec` ADG tables in static reports (remain deferred under parent W3 notes).

---

## Wave 1 — L5 fan-in regression triage

WAVE_ID: W1  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  

**Evidence:** `artifacts/test_inventory/child_w1_l5_fanin_regression_triage.md`

**Phases**: W1.1–W1.3 — ✅ DONE  

**Commands (recorded in artifact):**

- `git diff -- .cursor/config/l5_fanin_ratchet.json` → empty
- `$env:PYTHONPATH="<repo>"; python ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py --json` → exit **1**, three regressions
- SQLite: `mv_hotspot_centrality` + `edges`/`nodes` import attribution

**Outcome:** All three paths classified **`valid_architecture_regression`** (real import fan-in; MV consistent with edge counts). On-disk **`l5_fanin_ratchet.json` absent** locally—gate used script `DEFAULT_RATCHET`.

**Acceptance** — met per plan (no threshold/source edits).

---

## Wave 2 — ADG current/prior snapshot lineage repair

WAVE_ID: W2  
WAVE_STATUS: PARTIAL  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  

**Evidence:** `artifacts/test_inventory/child_w2_adg_snapshot_lineage_h2_preconditions.md`

**Phases**: W2.1–W2.3 — investigation **done**; H2 **not** green (exit **1**).

**Findings (abbrev):**

- **Current:** `artifacts/adg/adg_indexed_05162026_0649.sqlite` (has `mv_hotspot_centrality`).
- **Prior (resolver):** `artifacts/adg/adg_indexed_99999999_9999.sqlite` — **stub**; no `mv_hotspot_centrality`.
- **Cause:** `prior_snapshot()` glob includes sentinel; `latest_snapshot()` excludes it by id format.
- **Compatible second indexed snapshot in repo:** **none**.

**Commands:** recorded in artifact (`check_w6_fanin_collapse.py` default + `--help` both exit **1**; `latest_snapshot`/`prior_snapshot` introspection exit **0**).

**Acceptance:** Blocker **classified** with inventory; **no** DB/gate/source edits. Full “H2 exit 0 with real pair” **deferred** (P2 / second generation / operational stub policy).

---

## Wave 3 — CI invocation normalization

WAVE_ID: W3  
WAVE_STATUS: DONE  
WAVE_COMPLETE: YES  
AUTHORIZATION_STATUS: NOT_REQUIRED  

**Phases**: W3.1–W3.3 — ✅ DONE  

**Evidence:** `artifacts/test_inventory/child_w3_ci_invocation_normalization.md`

**Change:** `ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py` — after `REPO_ROOT`, mirror sibling gates:  
`if str(REPO_ROOT) not in sys.path: sys.path.insert(0, str(REPO_ROOT))`  
(imports `tools.adg.shared_modules.path_resolver` without requiring manual `PYTHONPATH`.)

**Verification** (repo root, `PYTHONPATH` unset / removed — PowerShell `Remove-Item Env:PYTHONPATH`):

| Gate | Exit |
|------|------|
| `python ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py --json` | **1** (3 regressions; **no** `ModuleNotFoundError`) |
| `python ops_scripts/ci/check_graph_watchlist_delta.py` | **0** |
| `python ops_scripts/ci/check_w6_fanin_collapse.py` | **1** (prior stub / `mv_hotspot_centrality` — Child W2) |
| `python ops_scripts/ci/check_observability_on_high_fanin.py` | **0** |

**Acceptance:** Met — import bootstrap only; no threshold/ratchet/H2 lineage edits.

---

## Closeout — scoped remediation waves complete; **PLAN_STATUS: PARTIAL**

**W1–W3 are complete for their scoped deliverables** (classification, lineage forensics, L5 CI invocation normalization). The **child plan stays PARTIAL** because material CI / architecture blockers from parent W4A **remain unresolved**.

### Unresolved blockers (not converted to PASS)

1. **L5 fan-in — valid architecture regressions** (W1 classified `valid_architecture_regression`; gate still **exit 1** vs embedded/`DEFAULT_RATCHET` baselines):
   - `agentic_core/L5_safety/runtime_gates/types.py`
   - `agentic_core/L5_safety/config/structure_blueprint/ssot.py`
   - `agentic_core/L5_safety/enforcement/ingress_envelope_check.py`
2. **H2 prior snapshot lineage** (W2):
   - Prior resolver selects **`artifacts/adg/adg_indexed_99999999_9999.sqlite`** (sentinel stub).
   - That artifact **lacks** `mv_hotspot_centrality`; **no compatible prior** with the MV exists in-repo alongside current indexed snapshot.
3. **`l5_fanin_ratchet.json` absent on disk** in this clone — `check_l5_hotspot_fanin_ratchet.py` falls back to script **`DEFAULT_RATCHET`**; restore/verify on canonical branch when tightening baselines under governance.

**Closeout evidence:** `artifacts/test_inventory/ratchet_child_closeout_summary.md`  
**Not claimed:** child plan PASS overall, parent W4 PASS, or full W4A green.

---

## Gap Register

- **G-P2**: Parent W1 P2 ratchet **178 > 162** may still block fresh ADG — H2 pairing may depend on resolving or using blessed historical snapshots.
- **G-COV**: Coverage ingest absent — do not use `hotspot_coverage_priority.md` as proof of test adequacy.
- **G-RATCHET-JSON**: `.cursor/config/l5_fanin_ratchet.json` **missing on disk** in this clone—`check_l5` uses `DEFAULT_RATCHET`; restore/verify on canonical branch.
- **G-H2-PRIOR**: `prior_snapshot()` selects `adg_indexed_99999999_9999.sqlite` (no `mv_hotspot_centrality`) when it coexists with one real indexed file — see `child_w2_adg_snapshot_lineage_h2_preconditions.md`.

---

## Definition of Done

| # | Criterion | Verification | Status |
|---|-----------|--------------|--------|
| DoD-1 | Child plan on disk (this path) | `.cursor/plans/ratchet-and-adg-pipeline-remediation-c3e9a7.md` | DONE |
| DoD-2 | Notion Plans row created | `create_plan_in_notion` → `page_id=36227693-f55c-81e0-ac0d-f4e6a3e2475a`, Status=Not Started | DONE |
| DoD-3 | Parent links child | Parent plan “Child plans” lists this slug | DONE |
| DoD-4 | W4A paths + evidence linked | Tables in §Parent linkage match `w4_ci_ratchet_verification.md` | DONE |
| DoD-5 | Smoke: L5 script help | `python ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py --help` → exit 0 | DONE |
| DoD-6 | W1 triage artifact | `artifacts/test_inventory/child_w1_l5_fanin_regression_triage.md` | DONE |
| DoD-7 | W2 lineage + H2 preconditions | `artifacts/test_inventory/child_w2_adg_snapshot_lineage_h2_preconditions.md` | DONE |
| DoD-8 | W3 CI invocation + proof | `artifacts/test_inventory/child_w3_ci_invocation_normalization.md` | DONE |

**Verification-vs-Deferral**

| Item | Verify now | Defer |
|------|------------|-------|
| L5 baseline tighten/`--update` after refactor | — | After W1 classification + governance |
| Full `adg_gates.run` bundle | Optional spot-check | Exhaustive in separate CI hygiene task |
| Notion backlog row for apps_rg hotspots | — | Parent W3 / future ADG slice |

---

## Related artifacts

- `.cursor/plans/adg-hotspot-test-coverage-b8e4f2.md`
- `artifacts/test_inventory/child_w2_adg_snapshot_lineage_h2_preconditions.md`
- `artifacts/test_inventory/child_w1_l5_fanin_regression_triage.md`
- `artifacts/test_inventory/child_w3_ci_invocation_normalization.md`
- `artifacts/test_inventory/w4_ci_ratchet_verification.md`
- `artifacts/test_inventory/ratchet_child_closeout_summary.md`
- **Follow-on (L5 fan-in architecture):** `.cursor/plans/l5-fanin-architecture-reduction-e7c4a2.md`
- `artifacts/test_inventory/w1_adg_hotspot_coverage_evidence.md`
- `.cursor/config/l5_fanin_ratchet.json`
- `ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py`
- `ops_scripts/ci/check_w6_fanin_collapse.py`
- `ops_scripts/ci/_adg_snapshot_diff.py`
- `tools/generate/generate_full_adg.py`

PLAN_CREATED: slug=ratchet-and-adg-pipeline-remediation-c3e9a7 path=.cursor/plans/ratchet-and-adg-pipeline-remediation-c3e9a7.md status=Not Started  
NOTION_PLAN_PAGE_ID: 36227693-f55c-81e0-ac0d-f4e6a3e2475a
