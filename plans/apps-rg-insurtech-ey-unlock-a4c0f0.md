# apps_rg — Unlock InsurTech & EY into Generated Role-Episode Lanes

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-06-08

Plan ID: `apps-rg-insurtech-ey-unlock-a4c0f0`
Status: Not Started
Created: 2026-06-08
Scope boundary: **apps_rg only.** No `agentic_core` edits, no other `apps_*`.
Parent: spun out of `apps-rg-aig-e2e-remediation-e4b7c1` W6 (user-authorized scope expansion 2026-06-08).

## Context (SCQA)

- **Situation:** InsurTech and EY are currently **locked-copy deterministic** sections (rendered
  verbatim from the base resume by `locked_copy_manifest.py`). The base resume holds the verbatim
  identity: **InsurTech Cloud Solutions — CTO — New York, NY — 2014-04→2017-03**; **Ernst & Young —
  Principal — New York, NY — 2009-10→2014-03**. Generated lanes (`insurtech_bullets`, `ey_bullets`,
  `insurtech_narrative`, `ey_narrative`) are declared in `section_execution_plan.py` but fail
  `REQUIRED_PROOF_ABSENT` — no InsurTech/EY proof inventory exists.
- **Complication:** The user authorized (2026-06-08) **unlocking** InsurTech/EY and generating them
  **exactly like Unify/IBM**: generate N candidate bullets, pick top-3, ground in graph skills tied
  to each employer's **time window** (CTO 2014-17, Principal 2009-14), enforced by **Exit Gates**.
  Company name / location / dates are copied **verbatim** from the base resume (not invented); the
  *skills grounding* comes from the augmented skills graph for that period. This means: (a) build the
  full IBM/Unify lane machinery for two new employers (~30 files), and (b) remove InsurTech/EY from
  the locked-copy deterministic path so generated lanes own them without duplication.
- **Question:** How to add two complete employer role-episode lanes faithfully (bundles → registry →
  bullet/narrative lanes → PA → graph-evidence → X2 gates → proof-pool wiring → unlock → tests →
  live E2E) without regressing IBM/Unify and without fabricating facts?
- **Answer:** A foundation-first, employer-at-a-time replication: build InsurTech end-to-end and prove
  it (bundles → wiring → X2 → standalone lane run), then clone to EY, then unlock locked-copy, then
  full AIG E2E. Bullet *identity/dates* are verbatim from base resume; *skills* are graph-node-backed.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1 | InsurTech + EY role-episode **bundle** data files (dependency root) | ~40k | base-resume identity verbatim; graph skill nodes exist for both periods | DONE | Both bundle JSONs validate; every `graph_skill_node_id` resolves in the skills graph — 5 tests green |
| W2 | P2 | **Registry + proof-pool wiring** so lanes resolve non-empty proof | ~35k | `ibm_graph_role_episode_registry` is a clean template | Not Started | `insurtech/ey_bullets` proof pool is non-empty; no more `REQUIRED_PROOF_ABSENT` |
| W3 | P3 | **Bullet lanes** (lane + PA + graph-evidence + hydration) for both | ~60k | bullet generation parameterized by employer | Not Started | `insurtech_bullets`/`ey_bullets` generate candidates → top-3 |
| W4 | P4 | **X2 Exit Gates** for both bullet lanes (+ narrative if separate) | ~45k | mirror `ibm_bullets_x2` with 3-bullet count | Not Started | X2 runs; bullet-count + metric-anchor + scope-isolation gates pass on valid output |
| W5 | P5 | **Narrative lanes** for both (6 modules each, mirror ibm_narrative_*) | ~50k | narrative consumes upstream bullets | Not Started | `insurtech_narrative`/`ey_narrative` generate from upstream bullets |
| W6 | P6 | **Unlock** InsurTech/EY from locked-copy; reconcile duplication | ~20k | generated path supersedes locked-copy for these two | Not Started | No double-render; locked-copy no longer owns insurtech/ey OR is explicitly the fallback |
| W7 | P7 | **Tests** (unit + contract) mirroring IBM/Unify + **live AIG E2E** | ~45k | external Claude key available | Not Started | unit/contract green; live run emits all 4 lanes with X1D/X2/X3, no REQUIRED_PROOF_ABSENT |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1 | Bundle data | `insurtech_role_episode_bundles.json`, `ey_role_episode_bundles.json` | graph-skill grounding to the right time window; metric promote/hold/exclude policy; no fabricated metrics | ~40k | In Progress |
| P2 | Registry + wiring | NEW `insurtech_/ey_graph_role_episode_registry.py`, NEW `insurtech_/ey_role_episode_evidence.py`; EDIT `proof_pool_resolver.py` | resolver employer fork; bundle validation | ~35k | Not Started |
| P3 | Bullet lanes | NEW `insurtech_/ey_bullets_lane.py`, `_pa.py`, `_graph_evidence.py`, `_canonical_hydration.py`; EDIT `employment_bullet_pool.py` (import IDs) | parameterize generation; verbatim identity vs graph skills | ~60k | Not Started |
| P4 | X2 gates | NEW `insurtech_/ey_bullets_x2.py` (+ narrative x2 if present) | 3-bullet count; metric-anchor rules; cross-employer scope isolation | ~45k | Not Started |
| P5 | Narrative lanes | NEW `insurtech_/ey_narrative_*` (lane, execution, runtime, defaults, metric_trim, pa) | upstream bullet dependency | ~50k | Not Started |
| P6 | Unlock | EDIT `locked_copy_manifest.py` (+ locked_copy_x2) | avoid double-render; preserve deterministic identity (company/dates) | ~20k | Not Started |
| P7 | Tests + E2E | NEW tests mirroring ibm/unify; live `python -m apps_rg` AIG run | needs Claude key; full 4-lane proof | ~45k | Not Started |

## Verbatim base-resume identity (NOT invented — copied)

| Employer | Title | Location | Dates | employer_node_id |
|---|---|---|---|---|
| InsurTech Cloud Solutions | Chief Technology Officer | New York, NY | 2014-04 → 2017-03 | `employment_exp_insurtech_001` |
| Ernst & Young | Principal | New York, NY | 2009-10 → 2014-03 | `employment_exp_ey_001` |

## Grounding rule (constitutional)

- **Identity** (company, title, location, dates) = verbatim from base resume.
- **Skills/bullet content** = grounded in `augmented_skills_graph` nodes whose evidence falls in the
  employer's time window. No fabricated metrics; promotable metrics must be second-sourced, else HOLD.
- InsurTech/EY were locked precisely because their copy is sensitive — generated bullets must stay
  grounded and pass the same Exit Gates IBM/Unify do.

## Build spec (files)

**CREATE (~28):** 2 bundle JSON · 2 registry · 2 role-episode-evidence · 4 bullet modules ×2 employers
(lane/pa/graph_evidence/canonical_hydration) · 6 narrative modules ×2 · 4 dispatch re-exports · 2 X2
bullet validators · (narrative X2 if separate) · tests.
**EDIT (3–4):** `proof_pool_resolver.py` (employer fork), `employment_bullet_pool.py` (import IDs —
already stubbed), `locked_copy_manifest.py` (+ `locked_copy_x2.py`) for the unlock.

## Definition of Done

| # | Criterion | Verification |
|---|---|---|
| 1 | Both bundle JSONs validate against the role-episode schema; every `graph_skill_node_id` resolves | a coverage test loads bundles + asserts node existence |
| 2 | `insurtech_bullets`/`ey_bullets` proof pool is non-empty (no `REQUIRED_PROOF_ABSENT`) | proof-pool resolver unit test |
| 3 | Bullet lanes generate N candidates and select top-3 with graph-skill grounding | standalone lane run (dry/live) |
| 4 | X2 Exit Gates run for both lanes; bullet-count(3) + metric-anchor + scope-isolation pass on valid output, fail closed on empty | X2 unit tests mirroring ibm_bullets_x2 |
| 5 | Narrative lanes generate from upstream bullets | standalone narrative run |
| 6 | InsurTech/EY no longer double-render (generated vs locked-copy reconciled); identity stays verbatim | locked-copy reconciliation test |
| 7 | Smoke: `python -m apps_rg --target-company AIG ... --section insurtech_bullets` exits 0 (and ey/narratives) | live/dry section runs |
| 8 | Full AIG E2E emits all 4 lanes with X1D/X2/X3; `integrated_lane_evidence_status.json` has no missing InsurTech/EY lanes | full `python -m apps_rg` run + `summarize_e2e_run.py` |

Verification vs Deferral: items 1–2, 4, 6 are unit/contract-verifiable offline; items 3, 5, 7, 8 need
a live external-Claude run (key required) — those close in W7.

## Out Of Scope

- Editing `agentic_core` or other `apps_*`.
- Changing IBM/Unify lane behavior (template source only — read, don't modify).
- Inventing any InsurTech/EY metric or claim not grounded in base resume + skills graph.
