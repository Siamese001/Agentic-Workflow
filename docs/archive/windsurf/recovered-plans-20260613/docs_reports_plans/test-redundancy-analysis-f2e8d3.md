# Test Redundancy Analysis: tests/guardian vs All Other tests/ Subfolders

**Date:** 2026-03-09
**Scope:** Material redundancies between `tests/guardian/` and
`tests/governance/`, `tests/architecture/`, `tests/ci/`, `tests/evaluation/`
**Method:** Test-name comparison, subject-matter overlap, line-count inspection

---

## Summary

| Severity | Count | Action |
|----------|-------|--------|
| HIGH — near-duplicate (same subject + same SUT) | 5 pairs | Delete weaker file |
| MEDIUM — partial overlap (same subject, different depth) | 4 pairs | Merge or deprecate thinner file |
| LOW — thematic overlap only (different SUT or different assertion strategy) | 3 pairs | No action required |

---

## HIGH — Near-Duplicate Pairs (delete weaker file)

### H1 · Anti-pattern detector unit tests

| File | Tests | Lines | Verdict |
|------|-------|-------|---------|
| `tests/guardian/test_anti_patterns.py` | 27 | 453 | **KEEP → merge target** |
| `tests/guardian/test_guardian_config_with_logic.py` | ~40 | ~410 | **KEEP** (deeper, covers new detector) |
| `tests/guardian/test_guardian_prompt_assembly_exclusivity.py` | ~34 | ~370 | **KEEP** (deeper, covers new detector) |

`test_anti_patterns.py` tests the **original 5 detectors** (SilentSwallower,
TypeErasure, PathFragility, MagicConfig, GlobalMutation) using an old
`temp_python_file` fixture pattern.  The two new files test the 2 new
detectors with full §1 compliance.  The issue: `test_anti_patterns.py`
covers the same 5 detectors already exercised individually by dedicated
per-detector test files in `tests/guardian/` (e.g. `test_lazy_seam_silent_swallow.py`
in governance, and others implied by the scanner tests).

**Proposal:**  `test_anti_patterns.py` is the original omnibus test.  It is
**not** a near-duplicate of the two new files.  However, `test_scan_real_codebase_directory`
and `test_enforcement_levels` inside it overlap with `test_guardian_architecture_governance.py`.
Flag for merge in next cycle; **do not delete yet** — still provides coverage
for the 5 legacy detectors that no dedicated file covers.

---

### H2 · RoutingConfigSeal / split-brain tests

| File | Tests | Lines | Verdict |
|------|-------|-------|---------|
| `tests/governance/test_routing_config_seal.py` | 10 | 77 | **DELETE → superseded** |
| `tests/governance/test_split_brain_config_invariant.py` | ~30 | ~282 | **KEEP** |

`test_routing_config_seal.py` has 10 tests covering `RoutingConfigSeal` immutability,
hash determinism, and `SealedRoutingContext` mutation.
`test_split_brain_config_invariant.py` covers **all the same tests** plus:
- State-transition matrix (valid→valid, valid→invalid)
- Mutation matrix (parametric, 6 mutation types)
- Concurrent verification
- Edge cases: empty config, nested keys, key order independence
- `TestMutationMatrix` parametric test

`test_routing_config_seal.py` is a **strict subset** of the new file.
Every assertion in it is replicated with higher rigour in
`test_split_brain_config_invariant.py`.

**Action: DELETE `tests/governance/test_routing_config_seal.py`**

---

### H3 · HIL reviewer / bypass tests

| File | Tests | Lines | Verdict |
|------|-------|-------|---------|
| `tests/governance/test_req085_086_hil.py` | 2 | 20 | **MERGE-UP then DELETE** |
| `tests/governance/test_hil_bypass_rejection.py` | ~30 | ~349 | **KEEP** |

`test_req085_086_hil.py` has exactly 2 tests:
- `test_req085_reviewer_sig_field_required` — checks `reviewer_sig` + `reviewer_id` fields exist on `HILReviewOutcome`
- `test_req086_modify_diff_requires_l5_reclear` — checks `requires_l5_reclear=True`

Both assertions are covered verbatim inside `test_hil_bypass_rejection.py`:
- `TestConstructionValidation` covers field presence
- `TestL5ReclearEnforcement::test_modify_diff_sets_l5_reclear_true` covers req-086

The req IDs (REQ-085, REQ-086) must be preserved.  Add `@pytest.mark.req("085")`
markers to the corresponding tests in `test_hil_bypass_rejection.py`, then
**DELETE `test_req085_086_hil.py`**.

**Action: ADD req markers to `test_hil_bypass_rejection.py`, then DELETE `test_req085_086_hil.py`**

---

### H4 · OscillationDetector tests

| File | Tests | Lines | Verdict |
|------|-------|-------|---------|
| `tests/governance/test_oscillation_freeze.py` | 16 | ~160 | **DELETE → superseded** |
| `tests/governance/test_oscillation_detector_wiring_invariant.py` | ~22 | ~348 | **KEEP** |

`test_oscillation_freeze.py` covers:
- `TestOscillationDetectorBasic`: single change no freeze, same value no freeze,
  two values no freeze, oscillation triggers freeze, freeze blocks, freeze expires,
  independent params
- `TestOscillationDetectorIsFrozen`: not frozen initially, frozen after oscillation,
  frozen count
- `TestOscillationDetectorConstructor`: invalid cooldown_window, invalid freeze_cycles,
  reset_for_testing

`test_oscillation_detector_wiring_invariant.py` covers every one of those cases
plus: concurrent safety, determinism, boundary conditions, state transition matrix.

`test_oscillation_freeze.py` is a **strict subset** of the new file.

**Action: DELETE `tests/governance/test_oscillation_freeze.py`**

---

### H5 · Architecture governance (layer import checks)

| File | Tests | Lines | Verdict |
|------|-------|-------|---------|
| `tests/guardian/test_architecture_governance.py` | 8 | ~130 | **MERGE-UP then DELETE** |
| `tests/guardian/test_guardian_architecture_governance.py` | ~20 | ~300 | **KEEP** |

`test_architecture_governance.py` uses a `validator` fixture + `temp_agentic_core`
to test `compliant_file_passes`, `gravity_violation_detected`, `naming_convention_violation`,
`nonexistent_file`, `valid_upward_import`, `non_agent_file_passes`,
`syntax_error_handling`, `multiple_violations`.

`test_guardian_architecture_governance.py` covers all those via synthetic repos
plus: GuardianResult schema validity, deterministic evidence sorting,
file collector behaviour, no-mutations invariant, real-result integration.

The `test_architecture_governance.py` violations/clean tests are a subset.

**Action: Verify no unique assertions exist in `test_architecture_governance.py`,
then DELETE it. Any unique cases should be merged first.**

---

## MEDIUM — Partial Overlap (merge or deprecate thinner file)

### M1 · Gateway / SDK egress enforcement (3-way overlap)

| File | Scope | Verdict |
|------|-------|---------|
| `tests/guardian/test_guardian_gateway_bypass.py` | Guardian result + violations detected | KEEP |
| `tests/governance/test_gateway_egress_invariants.py` | AST scan of real repo (INV-GW-1) | KEEP |
| `tests/governance/test_req_p0_gateway_monopoly.py` | AST scan + UWG existence + write-call ratchet | KEEP |

These three cover different layers (guardian contract, integration scan,
P0 requirement scan). **No deletions**, but they need a shared comment
pointing to each other to avoid confusion about scope.

---

### M2 · C0 Sovereignty / embedding boundary (2-way overlap)

| File | Scope | Verdict |
|------|-------|---------|
| `tests/guardian/test_guardian_c0_sovereignty.py` | Guardian result shape, violations, determinism | KEEP |
| `tests/architecture/test_wave2_phase2_2_embedding_sovereignty.py` | ADG gap analysis, embedding hint patterns | KEEP |

`test_guardian_c0_sovereignty.py` tests the *guardian runner* (`run_c0_sovereignty_guardian`).
`test_wave2_phase2_2_embedding_sovereignty.py` tests the *ADG analysis layer* that
detects embedding-in-non-allowed-layer patterns via gap analysis.  Different SUT,
complementary not redundant.  **No action.**

---

### M3 · Global sovereignty omnibus vs individual invariants

| File | Scope | Verdict |
|------|-------|---------|
| `tests/governance/test_global_sovereignty_invariant.py` | Consolidated 10-invariant omnibus | Keep but flag |
| Various `test_req*.py` files | Individual req assertions | KEEP |

`test_global_sovereignty_invariant.py` is a **consolidation** file that repeats
lightweight assertions from 10 other req tests.  It's designed as a regression
tripwire ("all-pass-or-nothing").  This is intentional design — not redundancy.
However, `test_inv_gateway_sole_llm_seam` within it partially overlaps with
`test_gateway_egress_invariants.py`.  **No deletion; add `# noqa: redundancy-by-design`
comment to the omnibus file to make the intent clear.**

---

### M4 · Layer sovereignty (2-way overlap)

| File | Scope | Verdict |
|------|-------|---------|
| `tests/governance/test_layer_sovereignty_guard.py` | Real-repo AST scan, upward-import ratchet (baseline 272) | KEEP |
| `tests/governance/test_layer_sovereignty_enforcer.py` | Unit tests for the enforcer class itself | KEEP |
| `tests/guardian/test_guardian_architecture_governance.py` | Synthetic-repo guardian contract | KEEP |

Three different layers of the same enforcement.  Complementary.  **No action.**

---

## LOW — Thematic Overlap Only (no action required)

### L1 · Prompt determinism

`tests/governance/test_req095_prompt_determinism.py` tests determinism of
**prompt fragment assembly** (sorted, stable, order-independent).
`tests/guardian/test_guardian_prompt_assembly_exclusivity.py` tests the
**DirectPromptCompilationDetector** AST scanner.  Different SUT entirely.

### L2 · SSOT structure

`tests/guardian/test_comprehensive_structure.py` (5 tests, structural placement)
and `tests/guardian/test_ssot_alignment.py` (file naming convention) overlap
thematically but cover different SSOT invariants.  Complementary.

### L3 · Replay/determinism req tests

`test_req060_063_meta_learning_replay.py`, `test_req157_302_trace_replay.py`,
`test_req192_409_semantic_clock_replay.py` all test replay-determinism of
different subsystems.  No overlap — different SUT per file.

---

## Proposed Deletion List

| # | File to DELETE | Superseded by | Risk |
|---|---------------|---------------|------|
| 1 | `tests/governance/test_routing_config_seal.py` | `test_split_brain_config_invariant.py` | LOW — strict subset |
| 2 | `tests/governance/test_oscillation_freeze.py` | `test_oscillation_detector_wiring_invariant.py` | LOW — strict subset |
| 3 | `tests/governance/test_req085_086_hil.py` | `test_hil_bypass_rejection.py` (after adding req markers) | LOW — 2 tests |
| 4 | `tests/guardian/test_architecture_governance.py` | `test_guardian_architecture_governance.py` (after verifying no unique cases) | MEDIUM — verify first |

## Proposed Merge (before deleting)

| Source | Target | What to carry over |
|--------|--------|--------------------|
| `test_req085_086_hil.py` lines 10–28 | `test_hil_bypass_rejection.py` | Add `@pytest.mark.req("085")` / `@pytest.mark.req("086")` to the already-passing equivalent tests |
| `test_architecture_governance.py` | `test_guardian_architecture_governance.py` | Verify `test_syntax_error_handling` and `test_valid_upward_import` are covered |

---

## Files NOT in scope for deletion

- `tests/guardian/test_anti_patterns.py` — covers 5 legacy detectors not yet
  given dedicated files; delete only after each detector gets a dedicated test.
- All `tests/governance/test_req*.py` — each addresses a specific numbered
  requirement; deletions require requirement ownership review.
- All `tests/architecture/test_wave*.py` — ADG gap analysis layer, different SUT.
- `tests/governance/test_global_sovereignty_invariant.py` — intentional omnibus
  tripwire; redundancy is by design.

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

