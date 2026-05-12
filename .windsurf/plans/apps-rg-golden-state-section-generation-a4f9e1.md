---
plan_id: apps-rg-golden-state-section-generation-a4f9e1
plan_type: architecture
authored_at: 2026-05-12
last_updated: 2026-05-12T06:15:00
status: Not Started
dod_exempt: false
parent_plan: apps-rg-exit-gate-fix-g24-hardening-d7c4b1
---

# apps_rg Golden State — Section-Level Generation + Spine Decoupling

Design plan for migrating `apps_rg` from single-pass whole-resume generation to section-level generation, scoring, and merging — and for moving all apps_rg dispatch and layer bindings out of `agentic_core` so it becomes a generic spine.

> ⛔ **THIS IS A DESIGN + PLANNING PLAN. NO runtime features, no gate weakening, no threshold tuning, no Golden State implementation may begin until this plan is explicitly transitioned to In Progress by the user.**

> **ADDENDUM (2026-05-12):** Tiered section-priority model added to prevent over-engineering low-signal resume sections. Not all sections receive bespoke rubrics.

---

## Context (SCQA)

**Situation:** `apps_rg` currently generates a resume in a single LLM call and scores the entire output at once. All dispatch and layer bindings live in `agentic_core`, making it app-specific code in the generic spine.

**Complication:** This single-pass architecture cannot independently optimize different resume sections (header, executive summary, experience bullets, competencies). Whole-resume scoring conflates good and weak sections. Meanwhile, `agentic_core` carries app-specific shims (dispatch, U0, C0, PA, L1, L2, Exit bindings) that belong in `apps_rg`.

**Question:** How do we migrate to section-level generation/scoring while simultaneously removing all apps_rg-specific code from `agentic_core`?

**Answer:** Define the target architecture first (this plan), then execute in waves. No code changes until design is approved.

---

## Hard Constraints (Non-Negotiable)

| Constraint | Rule |
|---|---|
| No gate weakening | G21/G22/G24/G26/G28 thresholds and logic must not change |
| No threshold tuning | G22 `factual_grounding` stays at 0.950; no per-section relaxation without explicit approval |
| No new `agentic_core` behavior | All new logic goes in `apps_rg`; core is a generic spine only |
| No Golden State implementation in this plan | This plan is design-only; implementation requires explicit wave approval |
| No dispatch leakage | `apps_rg_dispatch.py` and all `apps_rg_*_binding.py` files must migrate to `apps_rg/` |
| No equal-weight bespoke rubrics | P0 sections get bespoke X1B/X1D; P1/P2 use shared or basic scoring |
| Preserve section attribution | All scoring failures identify the specific section, even for P2 basic checks |

---

## Current Architecture (As-Built, 2026-05-12)

### Single-Pass Generation

```
apps_rg/__main__.py
  → agentic_core/runtime/entry/apps_rg_dispatch.py   [LEGACY SHIM — in wrong place]
      → U0: agentic_core/runtime/entry/u0_apps_rg_binding.py
      → L1: agentic_core/L1_cognition/apps_rg_l1_binding.py
      → L0: agentic_core/L0_routing/apps_rg_l0_binding.py
      → C0: agentic_core/runtime/c0/apps_rg_c0_binding.py
      → PA: agentic_core/prompt_governance/apps_rg_pa_binding.py
      → L2: agentic_core/L2_execution/apps_rg_l2_binding.py  [single LLM call for entire resume]
      → Exit: agentic_core/runtime/exit/apps_rg_exit_binding.py
```

**Generation unit:** One LLM call → one `master_resume_v2.16` JSON blob.

**Scoring unit:** Entire output scored at once:
- G21: schema validation on the whole JSON
- G22: `factual_grounding` across all claim-bearing values in the whole output
- G24: per-input hash distinctness (whole-run)
- G28: audit-ref coverage (whole-run)

**Weaknesses:**
- A weak executive summary can't be regenerated independently
- G22 factual grounding failures don't identify which section is the problem
- Header repair (G21) applies a single deterministic fix rather than section-aware generation
- All dispatch + bindings in `agentic_core` = app-specific code in generic spine

---

## Target Architecture (Golden State)

### Section-Level Generation + Scoring

```
apps_rg/__main__.py
  → apps_rg/runtime/dispatch/apps_rg_dispatch.py     [MOVED OUT of agentic_core]
      → apps_rg/runtime/bindings/u0_binding.py       [MOVED OUT]
      → apps_rg/runtime/bindings/l1_binding.py       [MOVED OUT]
      → apps_rg/runtime/bindings/l0_binding.py       [MOVED OUT]
      → apps_rg/runtime/bindings/c0_binding.py       [MOVED OUT]
      → apps_rg/runtime/section_planner.py           [NEW: decompose run → section specs]
      → per-section PA + L2 loop:
          for section in [header, executive_summary, experience_bullets, competencies, ...]:
              PA: apps_rg/runtime/bindings/pa_binding.py (section-scoped prompt)
              L2: generic agentic_core L2 (LLM call) — one per section
              Section scorer: apps_rg/runtime/scoring/section_scorer.py [NEW]
      → apps_rg/runtime/bindings/merge_binding.py    [NEW: merge section outputs]
      → Exit: apps_rg/runtime/bindings/exit_binding.py [MOVED OUT]
```

**Generation unit:** One LLM call per section. Sections are independent; failures in one section don't force full regeneration.

**Scoring unit (target):**
- **Section-level X1B/X1D scorer** evaluates each section independently before merge using tiered priority model (P0/P1/P2)
- **X1B scoring**: Did the section complete its assigned task, format, and instruction requirements? (task compliance)
- **X1D scoring**: Is the section actually good, grounded, specific, faithful, credible, and useful? (quality/value)
- `factual_grounding` applied per-section → precise identification of which section fails G22
- `header_block` validation applied per-section → G21 section-aware (not whole-resume repair)
- Whole-resume G24/G28 still run at merge time (these are whole-run invariants)

---

## Current vs Target Comparison

| Dimension | Current (Single-Pass) | Target (Section-Level) |
|---|---|---|
| **LLM calls** | 1 per run | N per run (one per section) |
| **Generation unit** | Entire resume JSON | Individual section |
| **X1B/X1D scoring** | Whole output | Per section, before merge |
| **G22 failure** | Whole run fails; no section attribution | Section fails; others can succeed |
| **G21 header repair** | Deterministic fallback on whole output | Per-section generation; repair not needed |
| **Dispatch location** | `agentic_core/runtime/entry/apps_rg_dispatch.py` | `apps_rg/runtime/dispatch/apps_rg_dispatch.py` |
| **Binding location** | `agentic_core/*/apps_rg_*_binding.py` (7 files) | `apps_rg/runtime/bindings/*.py` (7 files) |
| **`agentic_core` usage** | Contains app-specific dispatch + bindings | Generic spine only — no apps_rg code |
| **Section merging** | N/A (single output) | `merge_binding.py` assembles final JSON |
| **Retry granularity** | Full resume retry | Tiered retry: P0 (section-level retry), P1 (conditional retry), P2 (schema/factual only) |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | P1 | Architecture audit — map every apps_rg-specific file in `agentic_core`, classify as MIGRATE/KEEP | ~600 | ADG has current snapshot | ✅ DONE | All 14 files classified; 8 bindings + 4 contracts + 2 integration; W2 blockers identified |
| W2 | P2, P3 | Create dispatch; migrate bindings U0→L1→L0→C0→PA→L2→Exit (in that order) — shim backward compat | ~3,000 | No behavior change; existing tests pass | 🔲 TODO | `python -m apps_rg` exits 0 with identical output |
| W3 | P4 | Section planner design — define section spec schema, ordering, and PA scoping | ~1,200 | No LLM call changes yet; planner is pure-Python | 🔲 TODO | Section spec schema defined; unit tests for planner |
| W4 | P5 | Section-level PA + L2 loop — replace single LLM call with N-section loop | ~2,000 | Qwen vLLM Docker stack running | 🔲 TODO | Live run produces section-level artifacts; merge passes |
| W5 | P6 | Section-level X1B/X1D scorer with tiered retry policy, per-section G22 attribution, and no threshold drift | ~1,500 | Section artifacts from W4 | 🔲 TODO | Section failures attributed correctly; merge score correct |
| W6 | P7 | Gate verification — confirm G21/G22/G24/G28 unchanged; no threshold drift | ~600 | W5 complete | 🔲 TODO | All gates pass at same or higher pass rate than baseline |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| W1.P1 | Architecture audit | ADG + 14 files catalogued (8 bindings, 4 contracts, 2 integration) | Classified as MIGRATE/KEEP_GENERIC/LEGACY_SHIM; identified 5 W2 blockers | ~600 | ✅ DONE |
| W2.P2 | Create `apps_rg/runtime/` directory structure + migrate bindings | 7 binding files + dispatch (create new) | Migration order: U0→L1→L0→C0→PA→L2→Exit (deferred last); dispatch created fresh | ~1,500 | 🔲 TODO |
| W2.P3 | Add backward-compat shims in `agentic_core` → `apps_rg/runtime/` | 7 shim stubs in `agentic_core` | Shims must not break any CI gate; Exit shim temporary until Exit migrates last | ~1,500 | 🔲 TODO |
| W3.P4 | Section planner schema + unit tests | `apps_rg/runtime/section_planner.py` (new) | Define `SectionSpec`, ordering, PA-scoping contract | ~1,200 | 🔲 TODO |
| W4.P5 | N-section PA + L2 loop + section merge | `apps_rg/runtime/bindings/pa_binding.py`, `l2_binding.py`, `merge_binding.py` (new) | PA prompt must be scoped to section; L2 response must be section JSON not full resume | ~2,000 | 🔲 TODO |
| W5.P6 | Section-level X1B/X1D scorer | `apps_rg/runtime/scoring/section_scorer.py` (new) | Tiered scoring: P0 bespoke, P1 conditional, P2 basic; per-section G22 attribution; no threshold drift | ~1,500 | 🔲 TODO |
| W6.P7 | Gate verification + baseline comparison | All gate files, test suite | No threshold drift; G21/G22/G24/G28 pass rates at or above baseline | ~600 | 🔲 TODO |

---

## Definition of Done

| ID | Criterion | Verification | Status |
|---|---|---|---|
| DoD-1 | Zero apps_rg-specific files remain in `agentic_core` (no `apps_rg_*_binding.py`, no `apps_rg_dispatch.py`) | `rg -l "apps_rg" agentic_core/` returns only generic imports | 🔲 TODO |
| DoD-2 | `python -m apps_rg [canonical args]` exits 0 with `exit_status=success` after all bindings moved | Live smoke run | 🔲 TODO |
| DoD-3 | Section-level generation: live run produces per-section artifacts (`section_header.json`, `section_exec_summary.json`, etc.) | Artifact inspection | 🔲 TODO |
| DoD-4 | G22 `factual_grounding` threshold unchanged at 0.950; per-section scores visible in gate receipt | `07_gate_mesh_result.json` inspection | 🔲 TODO |
| DoD-5 | G21/G22/G24/G28 pass rate at or above `rg-run-c68e95637652` baseline | Baseline comparison report | 🔲 TODO |
| DoD-6 | `pytest tests/_apps_contract/ -x` — all tests pass; zero new failures | pytest output | 🔲 TODO |
| DoD-7 | `python -m apps_rg --dry-run [canonical args]` exits 0 (APPS-DRYRUN gate) | CI gate green | 🔲 TODO |

### Verification-vs-Deferral

| Item | Verified | Deferred |
|---|---|---|
| G22 threshold lowering | ❌ | **Permanently deferred** — do not lower below 0.950 |
| Section retry on G22 fail | ❌ | Deferred to W5 or later sub-plan |
| Multi-candidate ensemble | ❌ | Deferred — not in scope |
| Section-level G26 no_fabrication | ❌ | Deferred — whole-run only for now |
| Shim removal from `agentic_core` | ❌ | Deferred to wave after W2 (shims in W2 are temporary) |

---

## Gap Register

| ID | Description | Severity | Wave | Status |
|---|---|---|---|---|
| GAP-GS-1 | `apps_rg_dispatch.py` does NOT exist in `agentic_core` (only .pyc) — must be created in `apps_rg/runtime/dispatch/` | High | W2 | ✅ RESOLVED — W1B disposition: CREATE (not migrate) |
| GAP-GS-2 | 7 `apps_rg_*_binding.py` files in `agentic_core` — app-specific code in generic spine | High | W2 | 🔲 Open — W2 migration order hardened |
| GAP-GS-2a | Exit binding circular import risk (imports from `apps_rg_exit_evidence_builder`) | High | W2 | ✅ MITIGATED — W1B: defer Exit migration until last |
| GAP-GS-2b | Prerequisite gate imports from `apps_rg.prerequisites.briefing_validator` | Medium | W2 | ✅ ACCEPTED — Keep as LEGACY_SHIM in agentic_core |
| GAP-GS-3 | Single LLM call produces entire resume — no section-level failure attribution | Medium | W4 | 🔲 Open |
| GAP-GS-4 | G22 `factual_grounding` scorer operates on whole output — can't identify which section causes failure | Medium | W5 | 🔲 Open |
| GAP-GS-5 | No section-level X1B/X1D scorer — only whole-resume scoring exists | Medium | W5 | 🔲 Open |
| GAP-GS-6 | No tiered section priority — risk of over-engineering low-signal sections | Medium | W3 | 🔲 Open |

---

## Relationship to Backlog

The 10 backlog items in `artifacts/apps_rg/next_apps_rg_golden_state_backlog.md` map to this plan as follows:

| Backlog Item | Plan Wave |
|---|---|
| GS-01: Move `apps_rg_dispatch.py` to `apps_rg/runtime/dispatch/` | W2 |
| GS-02: Move 7 `apps_rg_*_binding.py` to `apps_rg/runtime/bindings/` | W2 |
| GS-03: Remove `agentic_core` shims after binding migration | Post-W2 sub-plan |
| GS-04: Section planner schema | W3 |
| GS-05: N-section PA prompt scoping | W4 |
| GS-06: N-section L2 loop | W4 |
| GS-07: Section merge contract | W4 |
| GS-08: Section-level X1B/X1D scorer | W5 |
| GS-09: Per-section G22 attribution | W5 |
| GS-10: Gate verification baseline comparison | W6 |

---

## Non-Goals (Explicit Fence)

The following are **explicitly forbidden** in this plan and must not be implemented:

- ❌ Lowering G22 `factual_grounding` threshold below 0.950
- ❌ Weakening G21, G24, G26, G28 gates in any way
- ❌ Adding new runtime features to `agentic_core`
- ❌ Implementing section retry without explicit wave approval
- ❌ Multi-candidate ensemble generation
- ❌ Any code changes before W1.P1 architecture audit is complete and reviewed
- ❌ Starting Wave 2 before this plan is transitioned to `In Progress` by the user
- ❌ Equal-weight bespoke rubric for every resume section — P2 sections use basic checks only

---

## Architecture Classification

| Component | Location (Current) | Location (Target) | Classification |
|---|---|---|---|
| `apps_rg_dispatch.py` | **Does not exist** (only .pyc remnant) | `apps_rg/runtime/dispatch/` | **CREATE** (not migrate) — W1B disposition |
| `apps_rg_exit_binding.py` | `agentic_core/runtime/exit/` | `apps_rg/runtime/bindings/` | `LEGACY_SHIM` → migrate |
| `apps_rg_l2_binding.py` | `agentic_core/L2_execution/` | `apps_rg/runtime/bindings/` | `LEGACY_SHIM` → migrate |
| `apps_rg_pa_binding.py` | `agentic_core/prompt_governance/` | `apps_rg/runtime/bindings/` | `LEGACY_SHIM` → migrate |
| `u0_apps_rg_binding.py` | `agentic_core/runtime/entry/` | `apps_rg/runtime/bindings/` | `LEGACY_SHIM` → migrate |
| `apps_rg_l0_binding.py` | `agentic_core/L0_routing/` | `apps_rg/runtime/bindings/` | `LEGACY_SHIM` → migrate |
| `apps_rg_l1_binding.py` | `agentic_core/L1_cognition/` | `apps_rg/runtime/bindings/` | `LEGACY_SHIM` → migrate |
| `section_planner.py` | (new) | `apps_rg/runtime/` | `NEW — app-owned` |
| `section_scorer.py` | (new) | `apps_rg/runtime/scoring/` | `NEW — app-owned` |
| Generic L2 executor | `agentic_core/L2_execution/` | stays | `GENERIC_INFRASTRUCTURE` |
| G21/G22/G24/G26/G28 gates | `agentic_core/` | stays | `GENERIC_INFRASTRUCTURE — DO NOT MOVE` |

---

## W1B Blocker Disposition Summary

**Status:** ✅ COMPLETE — W2 readiness assessed, blockers dispositioned, migration order hardened

### Blockers Resolved

| Blocker | Disposition | W2 Impact |
|---------|-------------|-----------|
| BLK-W2-1: Dispatch missing source | ✅ **ACCEPTED** | Create `apps_rg/runtime/dispatch/apps_rg_dispatch.py` fresh (not migrate) |
| BLK-W2-2: Exit evidence circular risk | ✅ **MITIGATED** | Defer Exit migration until **last** (after L2); use hardened order |
| BLK-W2-3: Prerequisite gate import | ✅ **ACCEPTED** | Keep gate in `agentic_core` as LEGACY_SHIM; approved L0 coupling point |
| BLK-W2-4: Core→app imports | ✅ **REFINED** | Only 3 actual imports (not 19); classified and dispositioned |
| BLK-W2-5: Integrated pipeline ownership | ✅ **DECIDED** | Pipeline stays in `agentic_core` (generic spine); apps_rg owns dispatch only |

### Core→App Import Classification (3 files, not 19)

| File | Import | Classification |
|------|--------|----------------|
| `L0_routing/apps_rg_l0_binding.py` | `from apps_rg.activation_policy import ...` | LEGACY_SHIM_ALLOWED_TEMPORARILY — becomes internal after move |
| `L0_routing/gates/apps_rg_prerequisite_gate.py` | `from apps_rg.prerequisites.briefing_validator import ...` | CORE_BOUNDARY_VIOLATION — keep in core temporarily |
| `runtime/exit/apps_rg_exit_binding.py` | `from apps_rg.exit.apps_rg_exit_evidence_builder import ...` | CONTRACT_ONLY_ALLOWED — Exit must import evidence builders |

### Hardened W2 Migration Order

```
Step 1:  U0 binding (least dependencies)
Step 2:  L1 binding (consumes U0 output)
Step 3:  L0 binding (consumes L1 output; imports activation_policy → internal after move)
Step 4:  C0 binding (consumes L0 output)
Step 5:  PA binding (consumes C0 output)
Step 6:  L2 binding (consumes PA output)
Step 7:  Exit binding (consumes L2 output; **DEFERRED LAST** due to evidence_builder imports)
Step 8:  CREATE dispatch (apps_rg/runtime/dispatch/apps_rg_dispatch.py) — orchestrates all 7 bindings
```

### W2 Readiness Verdict

**✅ SAFE TO START** with hardened migration order. Exit deferred last resolves circular import risk.

**Artifact:** `artifacts/apps_rg/golden_state_w1b_blocker_disposition.md`

---

## Tiered Section-Priority Model (Design Addendum)

To prevent over-engineering low-signal resume sections, the Golden State architecture adopts a three-tier priority model for section-level scoring.

### Tier Definitions

| Tier | Sections | X1B/X1D Treatment | Retry Policy |
|------|----------|-------------------|--------------|
| **P0** | headline, executive_summary, unify_narrative, competencies_ats, IBM | Bespoke section-specific X1B and X1D scorer profiles | Section-level retry/regeneration on X1B or X1D failure |
| **P1** | InsurTech, EY | Shared "experience-section" X1B/X1D rubric by default; promoted to bespoke when target role activates domain | Retry only when promoted OR on factual/schema failure |
| **P2** | Early Career, Education, low-signal certifications/background | Basic checks only (existence, structure, compactness, factuality) | No retry for subjective quality; repair only schema/factual failures |

### P1 Promotion Conditions

P1 sections promote to bespoke scoring when the target role matches one of these domains:
- `insurance` (exact match)
- `InsurTech` (exact match, case-insensitive)
- `financial services AI`
- `regulated transformation`
- `model governance`
- `advisory / consulting transformation`
- `risk / compliance / controls`

Promotion is determined at planning time (W3 section planner) by inspecting `target_role_profile.industry` and `target_role_profile.domain_keywords`.

### SectionSpec Schema (Updated)

```python
@dataclass(frozen=True)
class SectionSpec:
    section_id: str                          # canonical ID
    priority_tier: Literal["P0", "P1", "P2"]  # tier assignment
    scorer_profile_id: str                   # X1B/X1D rubric reference
    retry_policy: RetryPolicy                # tiered retry configuration
    
    # P1 only: conditions that trigger bespoke promotion
    promotion_conditions: Optional[List[str]] = None  # e.g., ["industry=insurance", "domain=InsurTech"]
    
    # X1B vs X1D clarification
    x1b_checklist: List[str] = field(default_factory=list)  # task completion requirements
    x1d_quality_dims: Optional[List[str]] = None  # None for P2 (basic only)
```

> **Implementation note:** `RetryPolicy` is constructed by the section planner using `build_retry_policy(priority_tier)`, not inside the `SectionSpec` field default. This avoids the circular reference issue where `priority_tier` is referenced before the instance is fully constructed.

### X1B vs X1D Clarification

| Dimension | X1B (Task Compliance) | X1D (Quality/Value) |
|-----------|----------------------|---------------------|
| **Question** | Did the section complete its assigned task, format, and instruction requirements? | Is the section actually good, grounded, specific, faithful, credible, and useful? |
| **Checks** | - Required fields present<br>- Format constraints met<br>- Instruction adherence<br>- Structural validity | - Factual grounding (G22)<br>- Specificity (concrete vs vague)<br>- Faithfulness to source resume<br>- Credibility of claims<br>- Utility for interview conversion |
| **Failure mode** | Section incomplete or malformed | Section present but weak, generic, or unconvincing |
| **Retry** | P0/P1: regenerate; P2: repair | P0: regenerate; P1: regenerate if promoted; P2: no retry |

### P2 Basic Checks (No Bespoke Rubric)

P2 sections receive these checks only:
1. **Section existence**: Required section is present
2. **Accurate structure**: Role/company/date fields correctly formatted
3. **Compact length**: Within token/line budget
4. **No unsupported claims**: All claims traceable to source resume
5. **No narrative drift**: Section doesn't contradict current AI/platform positioning
6. **No distraction**: Section doesn't dilute high-signal content

### Scorer Profile Mapping

| Section | Default Profile | Promoted Profile | Notes |
|---------|-----------------|------------------|-------|
| headline | `rg_headline_x1bd` | — | P0 bespoke |
| executive_summary | `rg_exec_summary_x1bd` | — | P0 bespoke |
| unify_narrative | `rg_narrative_x1bd` | — | P0 bespoke |
| competencies_ats | `rg_competencies_x1bd` | — | P0 bespoke |
| IBM | `rg_ibm_x1bd` | — | P0 bespoke |
| InsurTech | `shared_experience_x1bd` | `rg_insurtech_x1bd` | P1 conditional |
| EY | `shared_experience_x1bd` | `rg_ey_x1bd` | P1 conditional |
| Early Career | `basic_compactness` | — | P2 basic only |
| Education | `basic_compactness` | — | P2 basic only |
| certifications_low_signal | `basic_compactness` | — | P2 basic only |

---

## Acceptance Criteria

The hardened design satisfies these acceptance criteria:

| ID | Criterion | Verification Method |
|----|-----------|---------------------|
| AC-1 | P0 sections have bespoke X1B/X1D scorer profiles | Review SectionSpec.scorer_profile_id for P0 sections |
| AC-2 | InsurTech and EY use shared `shared_experience_x1bd` profile unless activated by target_role_profile | Unit test: promotion_conditions matching logic |
| AC-3 | Early Career uses `basic_compactness` checks only — no bespoke X1B/X1D | Review SectionSpec for P2 sections |
| AC-4 | G22 `factual_grounding` threshold remains at 0.950 for all claim-bearing sections | Hard constraint verification; no threshold drift |
| AC-5 | No new `agentic_core` behavior added — all scoring logic lives in `apps_rg/runtime/scoring/` | ADG query: `apps_rg` nodes only; no new `agentic_core` edges |
| AC-6 | Plan remains design-only — no runtime code changes | File diff inspection; only markdown modified |
| AC-7 | Tests can verify tier assignment deterministically | SectionSpec includes deterministic promotion logic; testable without LLM |
| AC-8 | Section-level attribution preserved for all failures — scorer identifies specific section ID | SectionSpec.section_id threaded through all scorer receipts |
| AC-9 | Retry policy by tier is explicit and enforceable | RetryPolicy dataclass with boolean flags; built by planner, not field default |
| AC-10 | Non-goal documented: "No equal-weight bespoke rubric for every resume section" | Explicit non-goal in plan §Non-Goals |
| AC-11 | No X1D-only scorer naming remains in design | All references updated to X1B/X1D or section_scorer.py |
| AC-12 | Section-level retry for P0 (not whole-resume retry) | P0 retry policy specifies section-level regeneration only |
