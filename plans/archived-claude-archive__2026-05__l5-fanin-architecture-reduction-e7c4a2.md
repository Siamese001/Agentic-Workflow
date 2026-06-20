---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\l5-fanin-architecture-reduction-e7c4a2.md'
original_relative_path: '_archive\\2026-05\\l5-fanin-architecture-reduction-e7c4a2.md'
source_sha256: 115a296ba1d9032ad3e6e81c51c8fc6915ad82be8f4bdd98159cc58bb0418237
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: l5-fanin-architecture-reduction-e7c4a2
plan_type: governance
parent_plan_id: adg-hotspot-test-coverage-b8e4f2
prior_sibling_plan_id: ratchet-and-adg-pipeline-remediation-c3e9a7
touches_agentic_core: true
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: artifacts/test_inventory/l5_fanin_w3a_ssot_barrel_reduction.md#author-gate
dod_exempt: false
---

# L5 fan-in architecture reduction (three ratchet hotspots)

**Planning-first child** under **PARTIAL** parent `adg-hotspot-test-coverage-b8e4f2`: reduce or **govern** fan-in on the **three** L5 paths classified **`valid_architecture_regression`** in `artifacts/test_inventory/child_w1_l5_fanin_regression_triage.md`, without **first** loosening ratchets, changing `DEFAULT_RATCHET`, or editing `l5_fanin_ratchet.json`.

> **plan_id discipline**: filename stem = `l5-fanin-architecture-reduction-e7c4a2`; wave markers use `plan=l5-fanin-architecture-reduction-e7c4a2`.

---

## Parent and lineage

| Role | Plan / artifact |
|------|-----------------|
| **Parent** | `.cursor/plans/adg-hotspot-test-coverage-b8e4f2.md` — **PARTIAL** (W4A ratchet verification not green) |
| **Prior child (W4A plumbing)** | `.cursor/plans/ratchet-and-adg-pipeline-remediation-c3e9a7.md` — **PARTIAL**; W1–W3 scoped complete; **H2 sentinel out of scope here** |
| **Gate** | `ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py` — queries `mv_hotspot_centrality` on latest `artifacts/adg/adg_indexed_*.sqlite` |
| **Classifier evidence** | `artifacts/test_inventory/child_w1_l5_fanin_regression_triage.md` |
| **Closeout rollup** | `artifacts/test_inventory/ratchet_child_closeout_summary.md` |
| **W4A CI narrative** | `artifacts/test_inventory/w4_ci_ratchet_verification.md` (§8 addendum: L5 runnable without `PYTHONPATH`; **still FAIL** on 3 regressions) |

### Hotspots in scope (exact paths)

| Path | W4A delta (baseline → current on `adg_indexed_05162026_0649.sqlite`) |
|------|----------------------------------------------------------------------|
| `agentic_core/L5_safety/runtime_gates/types.py` | 198 → **206** (+8) |
| `agentic_core/L5_safety/config/structure_blueprint/ssot.py` | 80 → **84** (+4) |
| `agentic_core/L5_safety/enforcement/ingress_envelope_check.py` | 49 → **50** (+1) |

**Ratchet file note:** `.cursor/config/l5_fanin_ratchet.json` is **often absent** on disk; the gate falls back to embedded **`DEFAULT_RATCHET`** in `check_l5_hotspot_fanin_ratchet.py`. This plan **does not** update that JSON or `DEFAULT_RATCHET` unless **W4** explicitly authorizes a governed baseline change **after** W1–W3 proof.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W3
LAST_COMPLETED_WAVE: W3C
LAST_UPDATED: 2026-05-25
NOTION_STATUS: Completed
NOTION_RECONCILED: 2026-05-25
PLAN_COMPLETED: 2026-05-25
PLAN_COMPLETE: plan=l5-fanin-architecture-reduction-e7c4a2 note="W3 implementation + ratchet PASS adg_indexed_05242026_2005.sqlite"
CLOSEOUT_RECEIPT: docs/reports/plans/active_backlog_closeout_receipt_20260525.md
RATCHET_PROOF: ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py exit=0 snapshot=adg_indexed_05242026_2005.sqlite
LAST_UPDATED: 2026-05-24
NOTION_STATUS: In Progress
NOTION_PAGE_ID: 36227693-f55c-81fc-a35b-dea4f39b11d8
NOTION_RECONCILED: 2026-05-24
ACTIVE_BACKLOG_MANIFEST: docs/reports/plans/active_in_progress_plans_manifest_20260524.md
ACTIVE_BACKLOG_ROLE: core_governance_independent

WAVE_COMPLETE: plan=l5-fanin-architecture-reduction-e7c4a2 wave=1 note="artifacts/test_inventory/l5_fanin_w1_dependency_attribution.md ADG+rg attribution 3 targets 206+84+50 edges L5_EXIT_1 unchanged scope=w1-read-only"  
WAVE_COMPLETE: plan=l5-fanin-architecture-reduction-e7c4a2 wave=2 note="artifacts/test_inventory/l5_fanin_w2_reduction_design.md facade+barrel-collapse design 3 targets sequencing=ssot→ingress→types Author-Gate=W3 scope=w2-design-only"  

**W3 implementation (3A–3C) evidence:** artifacts for ssot barrel, ingress facade, runtime_gate contracts (see W3A–W3C records below). **Overall plan** remains **IN_PROGRESS / PARTIAL** until ADG regen + ratchet exit 0 or **W4** baseline decision.

*(No `WAVE_COMPLETE: wave=3` lump-sum marker — use W3A–W3C execution records + artifacts as proof.)*

---

## Context (SCQA)

- **Situation** — L5 fan-in ratchet **fails** on three modules; imports are **real** (not MV noise), per W1 triage. Parent and prior child remain **PARTIAL**; CI invocation for L5 is fixed.
- **Complication** — Fan-in may mix production/runtime imports with tests, tooling, barrels, and type-only edges; reductions must **not** change **GateVerdict** semantics or move authority into Exit/UWG/L4/“00C” per **out-of-scope** list below.
- **Question** — What is the **smallest** structural change (or a **governed** acceptance of residual fan-in) that restores ratchet health **or** documents a baseline policy with proof?
- **Answer** — W1 attribution → W2 design → W3 implementation (when authorized) → W4 baseline governance **only** if residual fan-in is intentional **after** real reduction attempts.

---

## Out of scope (explicit)

- **H2** prior snapshot / `99999999` sentinel / `prior_snapshot()` lineage — **separate** plan.
- **Coverage ingest** and `hotspot_coverage_priority.md` as measured coverage truth.
- **`apps_rg`** hotspot markdown generation.
- **Broad L5 rewrite** or wholesale re-layering.
- **Moving authority** from L5 into 00C, Exit, UWG, or L4.
- **Changing `GateVerdict` semantics** or weakening any gate/schema/threshold.
- **Editing** `DEFAULT_RATCHET`, `l5_fanin_ratchet.json`, CI scripts, or sqlite DBs **except** as **explicitly authorized** in **W4** (baseline only) after proof.

---

## Wave progress

| Wave | Focus | Status | Primary artifact |
|------|-------|--------|------------------|
| W1 | Dependency fan-in attribution | ✅ DONE | `artifacts/test_inventory/l5_fanin_w1_dependency_attribution.md` |
| W2 | Reduction design (no implementation) | ✅ DONE | `artifacts/test_inventory/l5_fanin_w2_reduction_design.md` |
| W3 | Implementation (W3A–W3C) | 🟢 **SLICES DONE** | **3A–3C artifacts**; ratchet **still FAIL** until ADG regen / W4 |
| W4 | Governed baseline decision (optional) | 🔲 TODO | Decision packet / governance record only if W3 leaves intentional residual |

---

## W1 execution record (2026-05-16)

**Evidence:** `artifacts/test_inventory/l5_fanin_w1_dependency_attribution.md`

**Outcome:** All three targets have **full unique-importer tables** (59 + 13 + 19 sources), SQL replay, layer rollups, `rg` cross-check notes, and W2 hypotheses. **No** source/CI/ratchet/DB edits.

**Remaining gaps (for W2):** ADG `L_UNKNOWN` on `apps_qna/__main__.py`; `SovereignBaseAgent` edge symbol `_SEF` anomaly; dynamic/TYPE_CHECKING not exhaustively classified.

**Ratchet:** Still **exit 1** — not a plan regression; W1 is read-only.

---

## W2 execution record (2026-05-16)

**Evidence:** `artifacts/test_inventory/l5_fanin_w2_reduction_design.md`

**Design summary (one primary recommendation each):**

| Target | Primary recommendation |
|--------|------------------------|
| `runtime_gates/types.py` | **Stable narrow contract facade** (new module; retarget gate/runtime/test imports) |
| `structure_blueprint/ssot.py` | **Collapse duplicate import paths** (shrink `__init__` mega-import; direct ssot / L0 migration) |
| `enforcement/ingress_envelope_check.py` | **Stable narrow contract facade** (thin entry module; adapters import facade) |

**W3 sequence:** 3A **ssot/barrel** → 3B **ingress facade** → 3C **`types` facade** (largest blast). **Author-Gate required** for W3. **Baseline / ratchet JSON** — **deferred** to W4 only with proof.

**Remaining gaps:** ADG refresh post-W3C for numeric fan-in; **W4** if ratchet still fails; archived plans under `.cursor/plans` may still reference legacy import paths (non-runtime).

---

## W1 — Dependency fan-in attribution (spec)

**Goal:** For **each** of the three paths, enumerate **inbound importers** with enough structure to drive a reduction design.

**W1.1 ADG / edge inventory**

- Use canonical ADG snapshot (e.g. `artifacts/adg/adg_indexed_05162026_0649.sqlite` or successor) and approved query paths (`edges`, `nodes`, `mv_hotspot_centrality` as needed).
- For each hotspot: list importer modules with **layer** (L0–L6, apps_*, `tests`, `tools`, `docs`, etc.) and **app** affiliation where applicable.

**W1.2 Classification dimensions**

- **Production vs non-production:** separate **runtime / production** imports from **tests**, **docs**, **reports**, **generated code**, and **tooling**.
- **Import shape:** tag each edge (or importer group) as **direct-to-leaf**, **barrel / re-export**, **convenience import**, **type-only** (`TYPE_CHECKING` / annotation-only), or **avoidable coupling** (heuristic — document confidence).

**W1.3 Evidence artifact**

- **Output:** `artifacts/test_inventory/l5_fanin_w1_dependency_attribution.md`
- Must include: per-path tables or sections, methodology, snapshot id, and explicit **unknowns / limits** (e.g. dynamic imports not in ADG).

**W1 acceptance**

- All **three** paths have attributed fan-in with layer + prod vs non-prod split and import-shape tags (even if some tags are “unknown”).
- Artifact on disk at path above.
- **No** source, CI, ratchet, or DB edits in W1.

---

## W2 — Reduction design

**Goal:** For **each** path, pick **exactly one** primary recommendation (may combine sub-tactics in narrative, but **one** labeled lead).

**Allowed recommendation labels (choose one per path):**

1. **Stable narrow contract facade** — new or existing thin module; importers retarget to facade over time.
2. **Move shared type to lower-risk neutral contract module** — types live where fan-in is cheaper; L5 re-exports deprecated path if needed (migration doc).
3. **Collapse duplicate import paths** — merge barrels / remove redundant entrypoints.
4. **Protocol / interface substitution** — replace concrete imports with `Protocol` or interface module.
5. **Governed high-fan-in acceptance** — intentional concentration; **requires** W4-style proof outline (not baseline edit in W2).
6. **No-op with proof** — demonstrate fan-in is already minimal / illusory after attribution corrections (rare; high bar).

**W2 constraints**

- **No implementation** in W2 unless a **separate** explicit authorization is recorded (default: **design only**).
- **No** H2 / sentinel / coverage work.
- **Output:** `artifacts/test_inventory/l5_fanin_w2_reduction_design.md` with per-path: chosen recommendation, rationale, blast radius sketch, **migration notes** for W3, and **risks** (including tests to add in W3).

**W2 acceptance**

- Artifact exists; each path has one clear lead recommendation and explicit **non-goals**.
- **No** source, CI, ratchet, or DB edits in W2.

---

## W3 — Implementation wave (after W1 / W2 evidence)

**Preconditions**

- `l5_fanin_w1_dependency_attribution.md` and `l5_fanin_w2_reduction_design.md` are **complete** and reviewed.
- **Author-Gate** or equivalent approval if `core_addition_author_gate_required` / spine policy applies (this plan flags `touches_agentic_core: true`).

**Goals**

- **Smallest safe** import-path / module-boundary changes per W2.
- **No** intentional change to L5 **gate behavior** or **GateVerdict** semantics.
- **Preserve** public contracts unless a **documented** migration path (deprecation shim, re-export timeline) is in the design artifact.

---

## W3A execution record (2026-05-16) — `structure_blueprint` barrel only

**Scope:** W3A per plan sequencing (ssot / package `__init__`); **no** edits to `runtime_gates/types.py`, `ingress_envelope_check.py`, ratchet JSON, `DEFAULT_RATCHET`, or ADG generation.

**Evidence:** `artifacts/test_inventory/l5_fanin_w3a_ssot_barrel_reduction.md`  
**Migration receipt:** `artifacts/governance/migration_receipts/20260516_l5_w3a_structure_blueprint_barrel.json`

**Source change (summary):** `structure_blueprint/__init__.py` — replaced static `from ssot import (...)` mega-import with `_SSOT_LAZY_NAMES` + `__getattr__` lazy delegation to `ssot` submodule + `__dir__` for introspection parity with `__all__`.

**Tests:** `pytest tests/agentic_core/L5_safety/config/structure_blueprint -q -o addopts=` → **48 passed** (includes new `test_package_shim_ssot.py`).

**L5 ratchet:** `python ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py --json` → **exit 1**; regressions remain on `types.py`, `ssot.py`, `ingress_envelope_check.py` vs embedded baselines. **Measured** on stale snapshot: `mv_hotspot_centrality.fan_in` for `ssot.py` still **84** until ADG refresh; structural edge collapse is evidenced in source, not yet in DB.

**Blockers for W3 “complete”:** optional ADG regen for numeric proof on `ssot.py` / `types.py` / `ingress` fan-in post-facades.

---

## W3B execution record (2026-05-16) — `ingress` facade

**Scope:** W3B per plan — **ingress** narrow facade; **no** `runtime_gates/types.py`, ratchet, `DEFAULT_RATCHET`, ADG generation, or CI threshold edits.

**Evidence:** `artifacts/test_inventory/l5_fanin_w3b_ingress_facade_reduction.md`  
**Migration receipt:** `artifacts/governance/migration_receipts/20260516_l5_w3b_ingress_facade.json`

**Source change (summary):** New `agentic_core/L5_safety/enforcement/ingress.py`; runtime adapters, `rejection_response`, app runners/entrypoints, and selected tests retargeted from `ingress_envelope_check` to `ingress` for stable types. Implementation module unchanged.

**Tests:** `pytest tests/unit/agentic_core/L5_safety/enforcement -q -o addopts=` → **730 passed**, 2 skipped; `pytest tests/_apps_contract/test_w1_qna_spine_migration.py -q -o addopts=` → **43 passed**.

**L5 ratchet:** `check_l5_hotspot_fanin_ratchet.py --json` → **exit 1**; regressions unchanged on stale snapshot; **structural** direct-import reduction evidenced via `rg` (runtime/apps no longer import `ingress_envelope_check`).

**Blockers for plan closeout:** ADG regeneration + `check_l5_hotspot_fanin_ratchet.py` exit 0 **or** **W4** governed baseline; parent/prior child remain PARTIAL until parent acceptance.

---

## W3C execution record (2026-05-16) — `runtime_gates/contracts` facade

**Scope:** W3C only — **`contracts.py`** + import retargets; **no** ingress/ssot edits; **no** ratchet / CI threshold / DB / ADG generation.

**Evidence:** `artifacts/test_inventory/l5_fanin_w3c_runtime_gate_types_facade_reduction.md`  
**Migration receipt:** `artifacts/governance/migration_receipts/20260516_l5_w3c_runtime_gate_types_facade.json`

**Source change (summary):** New `contracts.py`; ~60 files now import public gate types via **`contracts`**; **`types.py`** definitions unchanged (+ docstring pointer).

**Tests:** `pytest tests/unit/agentic_core/L5_safety/runtime_gates tests/runtime_gates -q -o addopts=` → **447 passed**.

**L5 ratchet:** `check_l5_hotspot_fanin_ratchet.py --json` → **exit 1** on stale snapshot; **structural** `rg`: direct `types` import limited to **`contracts.py`** (+ non-runtime orphan plans).

**W3A–W3C implementation scope:** complete; **plan status** remains **IN_PROGRESS** pending ADG/ratchet/W4 per markers above.

---

**Verification**

- **Targeted pytest** for touched modules / contracts.
- **`python ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py --json`** from repo root (no `PYTHONPATH`) — expect trend toward **pass**; **do not claim PASS** in narrative until exit **0** and evidence logged.
- ADG refresh / snapshot id recorded if fan-in numbers are used as proof.

**W3 acceptance**

- Evidence: commands, exit codes, snapshot id, file list.
- **Still no** ratchet JSON / `DEFAULT_RATCHET` edits unless rolled into **W4** authorization.

---

## W4 — Governed baseline decision (residual fan-in only)

**When:** Fan-in remains **above** embedded/default threshold **after** W3 **and** residual concentration is **intentional** (or economically unavoidable with documented trade-offs).

**Allowed outputs (documentation + governance only in-plan unless org policy permits file edit)**

- Proposed **`l5_fanin_ratchet.json`** delta or **`--update`** runbook — **not executed** in this plan unless **explicitly authorized**.
- Proof bundle must include:

  1. **Classified importer list** (from W1, updated post-W3).
  2. **Architectural justification** (why fan-in is acceptable).
  3. **Tests green** (scope named).
  4. **No gate weakening** attestation (peer or Author-Gate).
  5. **Ratchet delta understood** (before/after fan-in numbers, snapshot ids).
  6. **Owner approval marker** (role/name/date per org template).

**W4 acceptance**

- Decision record exists (plan section + optional ledger/ref); **no silent** baseline bump.

---

## Definition of Done (planning phase)

| # | Criterion | Verification | Status |
|---|-----------|--------------|--------|
| DoD-1 | This plan file on disk | `.cursor/plans/l5-fanin-architecture-reduction-e7c4a2.md` | DONE |
| DoD-2 | Parent + prior child cross-linked | — | DONE |
| DoD-3 | Notion Plans row | `36227693-f55c-81fc-a35b-dea4f39b11d8` | DONE |
| DoD-4 | W1 artifact | `artifacts/test_inventory/l5_fanin_w1_dependency_attribution.md` | DONE |
| DoD-5 | W2 reduction design | `artifacts/test_inventory/l5_fanin_w2_reduction_design.md` | DONE |
| DoD-6 | W3 implementation + ratchet trend | 3A–3C done + pytest exit 0; ratchet **pending** ADG regen | 🟡 PARTIAL |

---

## Related artifacts

- `.cursor/plans/adg-hotspot-test-coverage-b8e4f2.md`
- `.cursor/plans/ratchet-and-adg-pipeline-remediation-c3e9a7.md`
- `artifacts/test_inventory/child_w1_l5_fanin_regression_triage.md`
- `artifacts/test_inventory/ratchet_child_closeout_summary.md`
- `artifacts/test_inventory/w4_ci_ratchet_verification.md`
- `artifacts/test_inventory/l5_fanin_w1_dependency_attribution.md`
- `artifacts/test_inventory/l5_fanin_w2_reduction_design.md`
- `artifacts/test_inventory/l5_fanin_w3a_ssot_barrel_reduction.md`
- `artifacts/test_inventory/l5_fanin_w3b_ingress_facade_reduction.md`
- `artifacts/test_inventory/l5_fanin_w3c_runtime_gate_types_facade_reduction.md`
- `artifacts/governance/migration_receipts/20260516_l5_w3c_runtime_gate_types_facade.json`

PLAN_CREATED: slug=l5-fanin-architecture-reduction-e7c4a2 path=.cursor/plans/l5-fanin-architecture-reduction-e7c4a2.md status=Not Started  
NOTION_PLAN_PAGE_ID: 36227693-f55c-81fc-a35b-dea4f39b11d8
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
