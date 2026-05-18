# apps_rg: SelectedRoleFactSet per-section proof substrate — implementation plan

**Slug:** `apps-rg-srfs-per-section-proof-b8e4a2`  
**Date:** 2026-05-18  
**Scope:** Expand SRFS from `executive_summary`-only to all generated section lanes (`headline`, `executive_summary`, `unify_bullets`, `unify_narrative`, `ibm_bullets`, `ibm_narrative`, `competencies`).  
**Entrypoint:** `python -m apps_rg --section <section>` only (no new entrypoints, standalone runners, or dispatchers).  
**Notion Plans DB:** Status **Completed** (retrospective row + full body synced 2026-05-18).

---

## CLOSEOUT (2026-05-18)

**W1–W7 implementation** plus **W8 verification** for section-level SRFS across the seven generated lanes is **closed** at the evidence class defined in the manifest.

- **Evidence SSOT:** `docs/reports/apps_rg/srfs_per_section_w1_w7_closeout_manifest.json`  
- **Proof class:** structural / fixture / offline-stub pytest only — **not** runtime certification, **not** live Qwen or judge quality proof.  
- **Product gaps (explicit):** `full_resume_srfs_supported` remains **false**; `modular_resume_generation.py` remains unwired; no full résumé R4 SRFS path is claimed.

---

## STATUS

**COMPLETED (section-level track).** The historical **PARTIAL** gate in this document referred to planning-time proof-ID policy before waves landed. Execution waves **W1–W8** are now backed by the closeout manifest and listed pytest bundles.

Remaining items are **product/aggregation** and **live-provider** concerns — tracked under **OPEN GAPS** and the manifest’s `open_gaps`, not as blocking section-level SRFS closure.

---

## W0.5 PROOF ID SEMANTICS AUDIT (completed)

**Goal:** Same ID namespace for SRFS allowlists and section `claim_ledger.source_fact_ids`.

### claim_ledger_id_field_used_by_section

| Section | Claim ledger proof field | Notes |
|--------|---------------------------|--------|
| headline | `claim_ledger[].source_fact_ids` | Compares to `allowed_fact_ids` (`headline_lane.ensure_claim_ledger`, `headline_x2`) |
| executive_summary | `claim_ledger[].source_fact_ids` | `executive_summary_lane` + `executive_summary_x2`; SRFS gates use allowed set from plan |
| unify_bullets | bullets + ledger: `source_fact_ids` | `unify_bullets_x2` |
| unify_narrative | `claim_ledger[].source_fact_ids` | Includes synthetic **`unify_narrative_base_001`** when role narrative present (`unify_narrative_lane`) |
| ibm_bullets | bullet + ledger IDs | `ibm_bullets_x2` |
| ibm_narrative | `claim_ledger[].source_fact_ids` | `ibm_narrative_x2` |
| competencies | `claim_ledger` + category `terms[].source_fact_id` / `source_fact_ids` | `competencies_x2` |

### selected_role_fact_set_id_fields_available

- Persisted slice rows: **`candidate_fact_id`** (required on `SelectedLedgerFactSlice` and master ledger rows per `candidate_fact_ledger.REQUIRED_LEDGER_FACT_FIELDS`).
- Executive SRFS path maps slice → plan fact: **`fact_id` = `candidate_fact_id`** (`exec_summary_srfs_integration.slice_row_to_plan_fact`).
- Allowed set for X2: base `fact_id` **plus** `{fact_id}_metric_{sha256[:8]}` when metrics present (`build_allowed_fact_ids_for_plan_facts`).

### Does candidate_fact_id equal “source_fact_id” for ledgers?

**Yes for employment bullet facts:** Base resume bullets use `bullet_id` (e.g. `bul_unify_001`); `collect_employment_bullets` stores that as row **`fact_id`**. Master candidate ledger uses **`candidate_fact_id`** for the same logical tokens (selection is bounded to ledger — `assert_selection_bounded_to_ledger`). Production SRFS is built from that ledger; **`candidate_fact_id` is the canonical proof token** models cite in `source_fact_ids`, consistent with non-SRFS pools.

**Not the same as a separate “C0 trace” column:** There is **no** distinct `source_fact_ids` array on `SelectedLedgerFactSlice`. Do **not** fake enforcement on a different field. Optional future: enrich rows with trace IDs **without** changing the X2 comparison namespace unless ledgers start emitting those IDs.

### Is load-time join to base/C0 required?

**Not required for ID namespace alignment** when SRFS rows are ledger-selected `candidate_fact_id` values. **Optional** join: assert each `candidate_fact_id` exists in base JSON + master ledger for hardening. **Required** for BLOCKED: if a section emits IDs that are **not** expressible from slice rows (synthetics), policy must either put them in SRFS JSON or refuse SRFS-required runs.

### Recommended canonical allowed ID set for X2 (SRFS mode)

- Start from slice rows: **`allowed_fact_ids = ∪ { candidate_fact_id, metric_derivatives }`** using the **same** `metric_derivative_fact_id` rule as `exec_summary_srfs_integration`.
- **Must match** what the model is instructed to emit in `source_fact_ids` for that section (including section synthetics if those sections stay in scope).

**Acceptance (W0.5):** X2 SRFS gates compare **`claim_ledger` / bullet `source_fact_ids`** to **`allowed_fact_ids` built from the slice**, not to unrelated namespaces. If a section needs IDs not present on slice rows, **STOP with BLOCKED** until SRFS contract includes them — no degraded gate.

---

## Loader backward compatibility (invariant)

- **Must accept both:**
  - `selected_facts_by_section.<section_id>` → **array** (current `asdict` / writer output)
  - `selected_facts_by_section.<section_id>.facts` → **array** (nested shape)
- **Do not** mandate writer migration in the same wave as loader unless **all** fixtures/tests are updated **and** both shapes are covered by tests.

---

## No-mixed-proof-mode (tested invariant)

When `--selected-role-fact-set` is supplied (SRFS **required** mode; default unless explicit opt-out flag documented + tested):

1. Every generated **section** run uses **only** its own SRFS slice for proof IDs (with metric derivatives per rules).
2. **Missing slice** → fail closed (early load or X2 explicit — prefer early).
3. **Base-resume fallback forbidden** unless `APPS_RG_SRFS_ALLOW_BASE_FALLBACK=1` (or similarly named) is **documented, off by default, and covered by tests**.
4. **Regression fixtures:** executive_summary SRFS + headline still using base pool → **must fail** (once wired).
5. **competencies** in SRFS mode: loose full-base `collect_employment_bullets` allowlist → **must fail** when SRFS path provided (slice-only allowlist).

---

## Section-only scope and reporting

- Implementation and proof claims in the W1–W8 bundle apply to **`python -m apps_rg --section <section>`** only unless explicitly extended.
- Every section report / runtime bundle carries: **`full_resume_srfs_supported: false`** until an R4/full-resume path passes SRFS through **and** tests prove it.
- Do **not** claim full résumé or empty-section R4 aggregation is SRFS-proven without that wiring.

---

## IMPLEMENTATION WAVES (with acceptance)

| Wave | Focus | Status (2026-05-18) |
|------|--------|---------------------|
| W0 | Baseline inventory | Done (this doc + historical gap matrix) |
| **W0.5** | **Proof ID semantics** | Done: audit above; implementation proven per W4/W3 tests |
| **W1** | Shared SRFS runtime module; thin exec wrapper | **Done** — contract + unit runtime tests |
| **W2** | CLI + `canonical_dispatch` threads SRFS to **all seven** lane runners | **Done** — `test_apps_rg_srfs_w2_canonical_threading` |
| **W3** | Per-lane SRFS adoption | **Done** — `test_apps_rg_srfs_w3_lane_adoption` |
| **W4** | X2 SRFS gates per section | **Done** — `test_apps_rg_srfs_w4_x2_slice_gates` |
| W5 | Prompt harmonization | **Done** — `test_apps_rg_srfs_w5_prompt_hierarchy` |
| W6 | Reporting metadata | **Done** — `test_apps_rg_srfs_w6_reporting` |
| W7 | Tests + fixtures + deterministic CLI smoke | **Done** — `test_apps_rg_srfs_w7_broader_fixtures` |
| W8 | Verification + honest evidence pack | **Done** — `srfs_per_section_w1_w7_closeout_manifest.json` |

---

## PROOF ACCOUNTING (mandatory labels)

Implementation and run reports **must** distinguish:

1. **Structural / fixture proof** — JSON shape, loader, allowlist math, unit X2 with synthetic ledgers.
2. **Mocked plumbing** — offline stub, `--mock-judges`, provider mock; **not** certification.
3. **Real runtime proof** — live provider path where allowed, non-mock judges per policy, artifacts + ALLOW/disposition as repo defines.

**Do not** claim runtime certification from mock, fixture-only, or offline stub execution.

---

## BASELINE_FINDINGS (historical — pre-closeout snapshot)

Captured at plan authoring before lane work landed. Implementation now supersedes this list; see **AS-OF-CLOSEOUT** matrix below.

### CLI

- **`apps_rg/__main__.py`** — `--selected-role-fact-set` threaded for all section lanes.

### Canonical dispatch

- **`canonical_dispatch.py`** — all seven `_run_*_from_cli` paths receive `selected_role_fact_set` where applicable.

### SRFS integration

- **`exec_summary_srfs_integration.py`** / **`executive_summary_lane.py`** — thin wrapper pattern; other lanes use shared `selected_role_fact_set.py`.

### SelectedRoleFactSet artifact

- **`selected_role_fact_set.py`** — `selected_facts_by_section` lists slices with **`candidate_fact_id`**; see W0.5.

---

## AS-OF-CLOSEOUT — SECTION MATRIX (2026-05-18)

| section | runner | SRFS path threaded | slice / allowlist | X2 SRFS slice gates | normalized reporting (W6) |
|--------|--------|:------------------:|-------------------|---------------------|---------------------------|
| headline | headline lane | yes | yes | yes | yes |
| executive_summary | exec lane | yes | yes | yes | yes |
| unify_bullets | unify lane | yes | yes | yes | yes |
| unify_narrative | unify narr | yes | yes | yes | yes |
| ibm_bullets | ibm lane | yes | yes | yes | yes |
| ibm_narrative | ibm narr | yes | yes | yes | yes |
| competencies | comp lane | yes | yes | yes | yes |

---

## TARGET DESIGN (summary)

- **`apps_rg/runtime/sections/selected_role_fact_set.py`** — load (dual shape), slice, `build_allowed_fact_ids_for_section`, `build_section_fact_plan`, `validate_section_slice_required`.
- **`exec_summary_srfs_integration.py`** — thin wrapper.
- Fail-closed SRFS required mode; optional documented flag for base fallback **only** with tests.

---

## OPEN GAPS (post–W8)

1. **Full résumé / R4:** `modular_resume_generation.py` unwired; `full_resume_srfs_supported` remains false until R4 passes SRFS end-to-end with tests.
2. **Live provider:** no live Qwen / quality / certification proof in the W8 bundle.
3. **Aggregation:** multi-section receipt aggregation for a single consumer remains a separate audit concern (see `docs/reports/apps_rg/apps_rg_post_section_aggregation_gap_20260517.md` if still relevant).
4. **Synthetic / section-specific IDs:** continuing policy discipline for tokens not on slice rows (fail-closed or explicit SRFS inclusion).

---

## FUTURE_VERIFICATION COMMANDS

```bash
python -m pytest tests/_apps_contract/test_apps_rg_srfs_w7_broader_fixtures.py -q --tb=short --override-ini="addopts="
# … full bundle: see closeout manifest commands_run
```

---

## Plan SSOT and Notion

- **Canonical plan file (repo):** `.cursor/plans/apps-rg-srfs-per-section-proof-b8e4a2.md`
- **Human-readable mirror (optional):** `docs/reports/apps_rg/apps_rg_srfs_per_section_proof_plan_full.md` (same content; SSOT remains `.cursor/plans`)
- **Notion:** Plans DB row **Slug** = `apps-rg-srfs-per-section-proof-b8e4a2`; **Plan File Path** matches `.cursor/plans/...` above; **Status** = Completed.

---

## Implementation discipline

Work proceeded in **narrow waves** (W1 → … → W8) with wave-level pytest proof. No broad refactors. **Section-level track complete** per manifest; further work is R4 wiring and live-runtime proof only if explicitly scoped.
