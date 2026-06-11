---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\tests-subfolders-ssot-harmonization-d0cb16.md'
original_relative_path: 'tests-subfolders-ssot-harmonization-d0cb16.md'
source_sha256: 5ec2dcde806fe60a3a382581d78c13cef925d262f0f9b214ebd24aae02688f9e
recovered_status: LOST_RECOVERED
last_commit: '9221ba8dcca'
last_commit_date: '2026-04-04 08:30:33 -0400'
created_date: '2026-04-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Tests Subfolders SSOT Harmonization

This plan fully harmonizes the `tests/` SSOT with approved folder policy, single-owner deduplication rules, and concrete migration steps so every prior feedback item is explicitly covered.

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| Wave 1 | W1-P1 to W1-P3 | Final decision lock + baseline drift inventory | 20,230 (GREEN) | `ContextWindowEstimator` run with current repo context and harmonization prompts | Planned | Final approved taxonomy and drift map are explicit and non-contradictory |
| Wave 2 | W2-P1 to W2-P3 | SSOT edits in `tests` territory constants | 20,232 (GREEN) | Edit scope is only `tests` territory in `_constants.py` | Planned | SSOT top-level list and unit mirror definitions match approved policy |
| Wave 3 | W3-P1 to W3-P3 | Ownership routing + migration matrix | 20,229 (GREEN) | No new top-level `knowledge/` or `tools/` categories | Planned | Every overlapping/drift folder has one canonical owner target |
| Wave 4 | W4-P1 to W4-P3 | `unit_min_deps` consolidation + `architecture` cleanup | 20,230 (GREEN) | Placeholder architecture tests can be re-homed/retired without policy regression | Planned | `tests/architecture` contains only genuine structural invariants |
| Wave 5 | W5-P1 to W5-P3 | Validation gates + rollback + closure report | 20,230 (GREEN) | Validation commands and acceptance checks execute from repo root | Planned | Policy, mapping, and completion evidence all pass |

**Token estimator source:** `agentic_core/planning/token_estimator.py` (`ContextWindowEstimator.estimate_step_tokens`)  
**Total projected:** 101,151 tokens (all GREEN)

---

## Scope and Hard Constraints

- In scope: `tests/` territory policy in `agentic_core/L5_safety/config/structure_blueprint/_constants.py`.
- In scope: deduplication policy between top-level `tests/*` and `tests/unit/*` mirror lanes.
- In scope: migration routing plan for non-SSOT and overlapping folders.
- Out of scope: non-`tests` territory restructuring.
- Must not create new top-level SSOT categories `tests/knowledge` or `tests/tools`.
- Must preserve SSOT-first structure ownership and avoid duplicate owners.

---

## Final Target Taxonomy (Authoritative)

### Top-level `tests` SSOT subfolders (retain/add)

- `_config`
- `adg`
- `architecture`
- `ci`
- `e2e`
- `evaluation`
- `governance`
- `guardian`
- `infrastructure`
- `integration`
- `ops_scripts`
- `performance`
- `smoke`
- `unit`
- `unit_min_deps`

### Top-level `tests` SSOT subfolders (remove/not present)

- Remove obsolete: `core`, `goldens`
- Remove/avoid low-signal lanes: `misc`, `behavioral`, `helpers`, `fixtures`, `snapshots`, `stress`, `contracts`, `enforcement`, `ssot_equivalence`, `sovereign_hardening`, `support`, `scripts`
- Remove from SSOT (not justified): `integration_full_deps`
- Remove from top-level SSOT ownership: `knowledge`, `tools`, `reasoning`, `system`, `audit` (re-home by type/owner)

---

## Single-Owner Dedup Policy

- **Rule 1:** Top-level `tests/*` folders own test-type lanes and cross-cutting suites.
- **Rule 2:** `tests/unit/*` owns module-mirror unit tests.
- **Rule 3:** A domain may appear in both top-level and unit trees only if ownership differs by test intent (cross-cutting vs isolated unit), never as duplicate catch-alls.
- **Rule 4:** `knowledge` and `tools` are not top-level SSOT lanes; they route under existing type lanes.

### Overlap ownership decisions

- `adg`
  - `tests/adg/*`: cross-cutting ADG behavior, graph invariants, multi-component checks
  - `tests/unit/agentic_core/adg/*` and/or `tests/unit/tools/adg/*`: isolated module unit tests
- `evaluation`
  - `tests/evaluation/*`: evaluation pipeline and scoring integration behavior
  - `tests/unit/*/evaluation-*` style unit tests remain under module mirrors
- `knowledge`
  - No top-level owner
  - Canonical owner: `tests/unit/agentic_core/knowledge/*`
- `tools`
  - No top-level owner
  - Canonical owners: `tests/unit/tools/*` (unit), `tests/integration/tools/*` (integration)

---

## Canonical `tests/unit/agentic_core` Mirror Roots

The root mirror list must include existing approved roots and explicitly include `embeddings`.

Required root entries:
- `L0_routing`
- `L1_cognition`
- `L2_execution`
- `L3_orchestration`
- `L4_state`
- `L5_safety`
- `L6_observability`
- `agents`
- `base_agents`
- `config`
- `core`
- `embeddings`
- `interfaces`
- `knowledge`
- `prompt_governance`
- `runtime`
- `seams`
- `utils`

---

## Migration Matrix (Source → Canonical Owner)

| Source | Action | Destination | Owner Rationale |
|---|---|---|---|
| `tests/knowledge/test_intake_clerk.py` | Move | `tests/unit/agentic_core/knowledge/.../test_intake_clerk.py` | Unit-like module behavior, deterministic local IO |
| `tests/tools/memory/test_adg_memory_server.py` (unit assertions) | Split/Move | `tests/unit/tools/memory/` | Unit lane owner for deterministic API and persistence behavior |
| `tests/tools/memory/test_adg_memory_server.py` (runtime assertions) | Split/Move | `tests/integration/tools/memory/` | Integration lane owner for runtime/component interaction |
| `tests/unit/consolidated/unit_min_deps/*` | Consolidate/Move | `tests/unit_min_deps/*` | Single canonical minimal-dependency owner |
| `tests/integration_full_deps/*` | Retire/Re-home | `tests/integration/*` if real; else remove placeholders | Avoid redundant top-level lane with no sustained signal |
| Placeholder files in `tests/architecture/*` | Re-home or retire | Appropriate type lane; keep only invariant tests in `architecture/` | `architecture/` must be structural invariants only |

---

## Execution Plan

### W1-P1 — Lock Decisions
**Scope:** Freeze final approved folder policy and ownership rules.

**Actions:**
1. Confirm final retain/add list for top-level `tests` SSOT.
2. Confirm full remove/not-present list including low-signal lanes.
3. Confirm no top-level `knowledge`/`tools` policy.

**Acceptance:** Final taxonomy and constraints are unambiguous.

### W1-P2 — Baseline Evidence Snapshot
**Scope:** Capture drift and overlap evidence before edits.

**Actions:**
1. Enumerate current `tests/` folders.
2. Enumerate `tests/unit/*` overlaps.
3. Record placeholder architecture and `integration_full_deps` status.

**Acceptance:** Drift inventory maps all current folders to target decisions.

### W1-P3 — Triple-Check Feedback Lock
**Scope:** Ensure each prior user feedback item maps to a phase/action.

**Actions:**
1. Build feedback coverage matrix (included below).
2. Add acceptance checks per feedback item.
3. Mark uncovered items as blockers (none expected after rewrite).

**Acceptance:** Zero uncovered feedback items.

### W2-P1 — SSOT Top-Level List Update
**Scope:** Update `tests.subfolders` entries in `_constants.py`.

**Actions:**
1. Remove `core`, `goldens`, `integration_full_deps`, and low-signal top-level entries.
2. Keep/add approved lanes: `adg`, `ci`, `evaluation`, `smoke`, `infrastructure`, `ops_scripts` and required existing lanes.
3. Ensure no top-level `knowledge`/`tools` additions.

**Acceptance:** Top-level SSOT list matches Final Target Taxonomy exactly.

### W2-P2 — Unit Mirror Root Normalization
**Scope:** Ensure `tests/unit/agentic_core` mirror root list is complete.

**Actions:**
1. Verify required root entries.
2. Ensure `embeddings` is present.
3. Remove mirror roots that conflict with single-owner policy.

**Acceptance:** Mirror roots are complete, deduplicated, and policy-consistent.

### W2-P3 — SSOT Consistency Pass
**Scope:** Align nearby purposes/notes with updated policy.

**Actions:**
1. Adjust folder purpose text where ownership semantics changed.
2. Ensure no stale references to removed lanes.
3. Validate ordering/readability for future maintainers.

**Acceptance:** No stale contradictory policy text remains.

### W3-P1 — Ownership Routing
**Scope:** Apply single-owner policy to every overlap.

**Actions:**
1. Route top-level overlap folders by intent owner.
2. Route module-owned unit tests into mirror lanes.
3. Document split rules for mixed tests.

**Acceptance:** Every overlap has one canonical owner rule.

### W3-P2 — Migration Planning
**Scope:** Produce move/retire map with destination and rationale.

**Actions:**
1. List explicit source-to-destination moves.
2. Tag each move as `move`, `split`, `retire`, or `re-home`.
3. Define prerequisites for mixed-test splits.

**Acceptance:** Migration matrix is execution-ready.

### W3-P3 — `integration_full_deps` Disposition
**Scope:** Finalize treatment of `tests/integration_full_deps`.

**Actions:**
1. Keep lane out of SSOT.
2. Re-home any real full-deps integration tests to `tests/integration/*` with markers.
3. Retire placeholders.

**Acceptance:** No orphan policy lane; real tests remain discoverable.

### W4-P1 — `unit_min_deps` Consolidation
**Scope:** Remove duplicate ownership between `tests/unit/consolidated/unit_min_deps` and `tests/unit_min_deps`.

**Actions:**
1. Canonicalize on `tests/unit_min_deps`.
2. Move residual tests from consolidated mirror path.
3. Retire empty redundant folder chain.

**Acceptance:** Single owner for minimal-dependency tests.

### W4-P2 — `architecture` Purity Cleanup
**Scope:** Keep only true structural invariant tests in `tests/architecture`.

**Actions:**
1. Keep real invariant tests (e.g., phantom-folder regression checks).
2. Re-home placeholder/non-invariant tests by behavior.
3. Retire placeholders that add no signal.

**Acceptance:** `tests/architecture` contains only genuine architecture invariants.

### W4-P3 — Safety Review of Re-homed Tests
**Scope:** Confirm moved tests still align with markers and lane semantics.

**Actions:**
1. Verify marker fidelity (`unit`, `integration`, etc.).
2. Verify import/runtime requirements still match lane intent.
3. Record residual exceptions.

**Acceptance:** No semantic regressions from re-homing.

### W5-P1 — Validation Commands
**Scope:** Run targeted checks for policy and test discovery.

**Commands:**
```bash
python -m pytest tests/ --collect-only -q
python ops_scripts/hooks/windsurf_plan_ci.py
```

**Acceptance:** Collection succeeds and plan CI checks pass.

### W5-P2 — Rollback Checkpoint Strategy
**Scope:** Define precise rollback points around SSOT/migration edits.

**Actions:**
1. Checkpoint after SSOT constants edit.
2. Checkpoint after migration moves.
3. Define selective rollback commands per phase.

**Acceptance:** Any phase can be reversed without collateral revert.

### W5-P3 — Closure and Evidence
**Scope:** Produce final closure summary proving all feedback satisfied.

**Actions:**
1. Complete feedback coverage matrix with `Done` status.
2. Capture final folder taxonomy snapshot.
3. Record open risks (if any) and follow-up tasks.

**Acceptance:** 100% feedback closure is evidenced.

---

## Rules

- Enforce type-first lanes at top level (`unit`, `integration`, `e2e`, etc.).
- Enforce single-owner mapping; no duplicate catch-all ownership.
- Do not add top-level `knowledge` or `tools` lanes.
- Keep `tests/architecture` strictly for structural invariants.
- Keep `tests/unit_min_deps` as the sole minimal-dependency owner.

---

## Success Criteria

- [ ] `core/` and `goldens/` removed from SSOT `tests` subfolders.
- [ ] Low-signal top-level lanes removed from SSOT (`misc`, `behavioral`, `helpers`, `fixtures`, `snapshots`, `stress`, `contracts`, `enforcement`, `ssot_equivalence`, `sovereign_hardening`, `support`, `scripts`).
- [ ] Approved top-level lanes present (`adg`, `ci`, `evaluation`, `smoke`, `infrastructure`, `ops_scripts`).
- [ ] No top-level `knowledge` or `tools` category in SSOT.
- [ ] `tests/unit/agentic_core` root mirror list explicitly includes `embeddings`.
- [ ] `tests/unit/consolidated/unit_min_deps` consolidated into `tests/unit_min_deps`.
- [ ] `tests/integration_full_deps` removed from SSOT; valid tests re-homed or placeholders retired.
- [ ] `tests/architecture` contains only genuine structural invariant tests.
- [ ] Overlap between top-level and `tests/unit/*` resolved with documented single-owner rules.

---

## Rollback Strategy

1. Revert only the `tests` territory hunk(s) in `agentic_core/L5_safety/config/structure_blueprint/_constants.py`.
2. Revert migration moves by phase checkpoint (W3/W4) rather than full tree reset.
3. Re-run collection and policy diff to verify restoration.
4. Re-open unresolved ownership decisions only if acceptance criteria fail.

---

## Acceptance Matrix

| Metric | Target | Verification |
|---|---|---|
| SSOT top-level harmonization | Final Target Taxonomy exactly matched | `_constants.py` diff inspection |
| Low-signal lane removal | All listed low-signal lanes absent from SSOT | `_constants.py` tests subfolders inspection |
| Approved lane inclusion | `adg`, `ci`, `evaluation`, `smoke`, `infrastructure`, `ops_scripts` present | `_constants.py` inspection |
| Dedup ownership | Each overlap has one canonical owner rule | Single-Owner Dedup section + migration matrix |
| `embeddings` mirror completeness | `tests/unit/agentic_core/embeddings` listed | `_constants.py` unit mirror roots |
| `unit_min_deps` canonicalization | Only `tests/unit_min_deps` remains owner | tree + migration evidence |
| `architecture` purity | Placeholder tests removed/re-homed | `tests/architecture/` content audit |
| `integration_full_deps` disposition | Not in SSOT; no orphan placeholder lane | `_constants.py` + migration evidence |

---

## Triple-Check Feedback Coverage

| Feedback Item | Covered In Plan | Status |
|---|---|---|
| Remove obsolete `core`, `goldens` | Final Target Taxonomy; W2-P1; Success Criteria | Covered |
| Add approved lanes (`adg`, `ci`, `evaluation`, `smoke`, `infrastructure`, `ops_scripts`) | Final Target Taxonomy; W2-P1; Acceptance Matrix | Covered |
| Remove low-signal/noisy top-level folders | Final Target Taxonomy remove list; W2-P1; Success Criteria | Covered |
| No top-level `knowledge` or `tools` | Scope constraints; Single-Owner Policy; W2-P1 | Covered |
| Deduplicate top-level vs unit overlap by single-owner | Single-Owner Dedup Policy; W3-P1/W3-P2 | Covered |
| Consolidate `tests/unit/consolidated/unit_min_deps` → `tests/unit_min_deps` | Migration Matrix; W4-P1; Success Criteria | Covered |
| Clean placeholder tests in `tests/architecture` | Migration Matrix; W4-P2; Success Criteria | Covered |
| Keep only real architecture invariants | W4-P2; Rules; Acceptance Matrix | Covered |
| Update `tests/unit/agentic_core` mirror list with `embeddings` | Canonical mirror roots; W2-P2; Success Criteria | Covered |
| Decide `integration_full_deps` necessity and disposition | Final Target Taxonomy; W3-P3; Success Criteria | Covered |
| Best-practice guidance on `tests/tools` vs `tests/unit/tools` | Single-Owner overlap decisions; Migration Matrix | Covered |
| Provide detailed multi-wave execution plan + migration matrix | Full W1-W5 plan + Migration Matrix section | Covered |
