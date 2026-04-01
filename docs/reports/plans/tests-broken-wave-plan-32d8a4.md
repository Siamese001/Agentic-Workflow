# Test Suite Burndown Wave Plan — 32d8a4

Fix every broken test under `tests/` in six hybrid waves, starting with collection blockers and then burning down the largest failure clusters while keeping each turn near the Kimi K2.5 safe operating cap.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | P1-COLLECT | Collection blockers and import guards | 222,601 | Collect-only blockers dominate the current error surface; import-guard conversions fit in one turn | YELLOW | `pytest --collect-only` has 0 errors; no active test path still relies on `except ImportError: pass` |
| Wave 2 | P2-CORE | L0/L2 core failure clusters | 222,402 | Routing/execution clusters are the highest-blast-radius failures after collection is clean | YELLOW | L0/L2 targeted tests stabilize; no new collection regressions are introduced |
| Wave 3 | P3-SAFETY | L5 safety/validator/enforcement failures | 220,434 | Safety validators and error-recovery guards can be isolated from lower-layer fixes | YELLOW | L5 safety suite passes or fails only on documented behavior gaps |
| Wave 4 | P4-LAYER | L4 state/memory + L3/L1 orchestration | 222,271 | State bridges and orchestration tests need fixture hardening and isolated rebaseline steps | YELLOW | State/orchestration tests collect cleanly and pass deterministically |
| Wave 5 | P5-E2E | E2E + integration suites | 220,732 | Integration waves inherit the cleaned lower-layer contracts and fixtures | YELLOW | E2E/integration suites pass or have explicit, intentional skips only |
| Wave 6 | P6-REBASELINE | Final rebaseline and residual cleanup | 215,233 | Remaining failures are mostly assertions, data-shape drift, and regression lock-in work | YELLOW | Full `pytest tests/` run returns 0 errors and no unplanned failures |

**Total: 1,323,673 projected tokens across 6 waves, all YELLOW**

## Subwave Breakdown

Subwaves are sequencing slices only; each wave keeps the same scope, targets, and wave-level token budget.

| Wave | Subwave A | Subwave B | Subwave C | Derisking Intent |
|------|-----------|-----------|-----------|-------------------|
| Wave 1 | Inventory remaining collection blockers and import surfaces | Convert guards to availability flags / `skipif` in the same files | Re-run `--collect-only` and narrow pytest slices to confirm 0 collection errors |
| Wave 2 | Map L0/L2 hotspots, fixtures, and shared contracts | Apply the smallest routing/execution fixes within the same target set | Rebaseline L0/L2 slices and confirm no collection regressions |
| Wave 3 | Isolate safety/validator failure classes and root causes | Patch the guards, validators, and handlers driving the wave failures | Re-run the safety subsets and confirm only explicit behavior gaps remain |
| Wave 4 | Audit state bridges, concurrency assumptions, and orchestration fixtures | Harden shared fixtures and isolate state leakage in the same scope | Rebaseline state/orchestration subsets and confirm deterministic collection |
| Wave 5 | Partition E2E/integration failures by contract boundary and environment dependency | Apply the minimal contract/fixture fixes for the targeted integration surface | Re-run E2E/integration subsets and confirm only intentional skips remain |
| Wave 6 | Inventory residual assertions, data-shape drift, and regression lock gaps | Close the remaining residual failures without widening scope | Run full-suite and collect-only proofs, then lock the branch on a clean rebaseline |

---

## SSOT-Compliant Plan Location

`docs/reports/plans/`

---

## Current Baseline & Evidence

- **Latest full pytest baseline**: `4,193 passed`, `3,241 failed`, `33 skipped`, `181 errors`
- **Latest collect-only signal**: `20 collection errors` in the non-E2E subset
- **ADG cache**: HOT / fresh, with `10,034` nodes and `726,409` edges
- **Kimi K2.5 budget thresholds**:
  - `WARNING_THRESHOLD = 197,000`
  - `SAFE_OPERATING_CAP = 223,000`
  - `HARD_MAX_CONTEXT = 262,000`
- **Estimator evidence**: all six waves were sized with `ContextWindowEstimator` and landed in the YELLOW zone

### Current failure clusters to burn down

- `tests/audit/test_error_path_coverage.py`
- `tests/unit/agentic_core/L0_routing/scripts/test_error_handler_adg.py`
- `tests/unit/agentic_core/L2_execution/types/test_mcp_error_types_adg.py`
- `tests/unit/agentic_core/L5_safety/enforcement/test_secure_error_handler_enforcer.py`
- `tests/unit/agentic_core/L5_safety/types/test_hardening_errors_adg.py`
- `tests/unit/agentic_core/L5_safety/validators/test_anti_pattern_scanner_validator_enhanced.py`
- `tests/unit/agentic_core/adg/extraction/test_parser_failure_audit.py`
- `tests/unit/apps_rg/types/test_AllProvidersDownError_adg.py`
- `tests/unit/test_imports_no_mro_error.py`
- `tests/unit/test_syntax_error_handling.py`
- `tests/unit/tools/adg/test_boilerplate_ratio_report.py`
- `tests/unit/tools/adg/test_hollow_file_cleanup.py`

---

## Gap Register

**GAP-1: Collection-time import failures**
- Optional imports still fail during collection in several test modules.
- Impact: pytest stops early, masking the real failure count and making rebaselines noisy.

**GAP-2: Core-layer blast radius**
- L0 routing and L2 execution have the largest reusable failure clusters.
- Impact: these failures fan out across many related tests and fixtures.

**GAP-3: Safety/validator brittleness**
- L5 tests still assume optional symbols and historical behavior without guarding availability.
- Impact: cross-cutting safety coverage remains unstable even when lower layers are healthy.

**GAP-4: State/orchestration coupling**
- L4 bridge tests and L3/L1 orchestration tests can leak state or rely on shared fixtures.
- Impact: failures become non-deterministic and harder to isolate.

**GAP-5: E2E/integration residue**
- E2E and integration suites depend on cleaned lower-layer APIs and stable fixtures.
- Impact: the last 20% of failures tends to hide in contract drift and environment assumptions.

**GAP-6: Rebaseline and regression lock**
- The suite needs a final proof run and evidence capture after each wave.
- Impact: without an explicit lock step, the same failures can re-enter the branch.

---

## Execution Plan

### Phase 1 — Collection blockers and import guards
**Scope**: Convert all remaining test-time `except ImportError: pass` patterns into availability flags plus `@pytest.mark.skipif` or fixture-level `pytest.skip(...)`. Remove collection-time type-hint references to optional imports in active test paths.

**Representative targets**:
- `tests/unit/agentic_core/planning/test_token_estimator_decorator.py`
- `tests/unit/agentic_core/planning/test_token_estimator_stress.py`
- `tests/unit/agentic_core/L0_routing/scripts/test_error_handler_adg.py`
- `tests/unit/agentic_core/L2_execution/types/test_mcp_error_types_adg.py`
- `tests/unit/agentic_core/L5_safety/enforcement/test_secure_error_handler_enforcer.py`
- `tests/unit/agentic_core/L5_safety/validators/test_anti_pattern_scanner_validator_enhanced.py`
- `tests/unit/agentic_core/adg/extraction/test_parser_failure_audit.py`

**Commands**:
```bash
python tools/adg_test_accelerator.py collection-safety --json docs/reports/adg_collection_analysis.json
python -m pytest tests/ --tb=short -q --maxfail=50
python -m pytest tests/unit/agentic_core/planning tests/unit/agentic_core/L0_routing tests/unit/agentic_core/L2_execution tests/unit/agentic_core/L5_safety -q
```

**Acceptance**:
- `pytest --collect-only` reports `0 errors`
- No active test path still uses silent `ImportError` fallthrough
- The wave stays within the `YELLOW` context budget and does not trigger `red/block`

---

### Phase 2 — L0/L2 core failure clusters
**Scope**: Burn the highest-blast-radius core clusters next, including routing, execution, apps_rg, and supporting error-type tests. Keep the batch focused on reusable import/fixture/contract fixes rather than one-off assertions.

**Representative targets**:
- `tests/unit/agentic_core/L0_routing/scripts/test_error_handler_adg.py`
- `tests/unit/agentic_core/L0_routing/enforcement/test_traceability_contracts.py`
- `tests/unit/agentic_core/L0_routing/enforcement/test_traceability_contracts_adg.py`
- `tests/unit/agentic_core/L2_execution/types/test_mcp_error_types_adg.py`
- `tests/unit/apps_rg/types/test_AllProvidersDownError_adg.py`
- `tests/unit/apps_shared/scripts/test_fix_syntax_errors.py`

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L0_routing tests/unit/agentic_core/L2_execution tests/unit/apps_rg -q
python -m pytest tests/unit/agentic_core/L0_routing -q
python -m pytest tests/unit/agentic_core/L2_execution -q
```

**Acceptance**:
- Core-layer failures drop materially in the targeted subset
- No new collection regressions appear in L0/L2
- Any production-module change is followed by an ADG refresh and a focused rebaseline

---

### Phase 3 — L5 safety, validator, and enforcement failures
**Scope**: Stabilize safety-layer and validator tests, especially error-recovery guards, anti-pattern scanners, hardening errors, and secure error handlers. Treat these as cross-cutting contracts, not isolated one-off defects.

**Representative targets**:
- `tests/unit/agentic_core/L5_safety/enforcement/test_error_recovery_guardrail.py`
- `tests/unit/agentic_core/L5_safety/enforcement/test_error_recovery_strategy_adg.py`
- `tests/unit/agentic_core/L5_safety/enforcement/test_secure_error_handler_enforcer.py`
- `tests/unit/agentic_core/L5_safety/types/test_hardening_errors_adg.py`
- `tests/unit/agentic_core/L5_safety/validators/test_anti_pattern_scanner_validator_enhanced.py`
- `tests/unit/agentic_core/L5_safety/test_hollow_file_detector.py`

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L5_safety -q
python -m pytest tests/unit/agentic_core/L5_safety/enforcement tests/unit/agentic_core/L5_safety/validators -q
python -m pytest tests/unit/agentic_core/L5_safety/types -q
```

**Acceptance**:
- Safety tests pass or fail only on explicit behavior gaps, not missing symbols
- Validator fixtures are stable and deterministic
- The wave remains at `YELLOW` and does not exceed the safe cap

---

### Phase 4 — L4 state/memory plus L3/L1 orchestration
**Scope**: Fix state-bridge, memory, and orchestration failures that tend to cascade from shared fixtures, concurrency assumptions, or leaked state. Keep this wave tightly bounded and rebaseline after each sub-batch.

**Representative targets**:
- `tests/unit/agentic_core/L4_state/enforcement/test_graph_memory_bridge_concurrency.py`
- `tests/unit/agentic_core/L4_state/enforcement/test_graph_memory_bridge_isolation.py`
- `tests/unit/agentic_core/L4_state/memory/test_faiss_store.py`
- `tests/unit/agentic_core/L4_state/memory/test_l1_exact_cache.py`
- `tests/e2e/test_ptc_full_lifecycle_e2e.py`
- `tests/e2e/test_ptc_aggressive_hardening.py`
- `tests/integration/test_ptc_full_integration.py`

**Commands**:
```bash
python -m pytest tests/unit/agentic_core/L4_state -q
python -m pytest tests/e2e/test_ptc_* tests/integration/test_ptc_full_integration.py -q
python -m pytest tests/unit/agentic_core/L4_state tests/e2e tests/integration/test_ptc_full_integration.py -q
```

**Acceptance**:
- State isolation and concurrency tests are deterministic
- Orchestration tests no longer depend on hidden state leakage
- The targeted subset collects cleanly before moving to E2E work

---

### Phase 5 — E2E and integration suites
**Scope**: Burn down the remaining end-to-end and integration residue after the lower layers are stable. This wave should absorb runtime observability, HITL, code validation gates, redis retrieval, parser failure auditing, and other full-stack contracts.

**Representative targets**:
- `tests/e2e/test_runtime_adg_l6_observability_e2e.py`
- `tests/e2e/test_hitl_lifecycle_e2e.py`
- `tests/e2e/test_code_validation_gates_e2e.py`
- `tests/integration/agentic_core/test_redis_l1_retrieval_gate_e2e.py`
- `tests/integration/test_depth_violation_no_archive_invariant.py`
- `tests/unit/tools/adg/test_boilerplate_ratio_report.py`
- `tests/unit/tools/adg/test_hollow_file_cleanup.py`

**Commands**:
```bash
python -m pytest tests/e2e tests/integration tests/unit/agentic_core/adg tests/unit/tools/adg -q
python -m pytest tests/e2e/test_runtime_adg_l6_observability_e2e.py tests/e2e/test_hitl_lifecycle_e2e.py tests/e2e/test_code_validation_gates_e2e.py -q
python -m pytest tests/integration -q
```

**Acceptance**:
- E2E/integration suites pass or have only explicit intentional skips
- No hidden collection errors remain in the runtime/observability path
- The wave still stays within `YELLOW` budget boundaries

---

### Phase 6 — Final rebaseline, cleanup, and regression lock
**Scope**: Run the full test suite, capture the final rebaseline, prune temporary debug artifacts, and lock the branch against regression. Use this wave to close the loop on any residual assertion/data-shape issues that were masked until the lower waves stabilized.

**Representative targets**:
- Residual failures from `tests/audit/test_error_path_coverage.py`
- Residual failures from `tests/unit/test_imports_no_mro_error.py`
- Residual failures from `tests/unit/test_syntax_error_handling.py`
- Residual failures from `tests/adg/test_adg_hardening_verification.py`
- Any remaining `tests/unit/*` assertion drift after waves 1–5

**Commands**:
```bash
python -m pytest tests/ -q
python -m pytest tests/ --collect-only -q
python -m pytest tests/ --tb=short -q --maxfail=20
```

**Acceptance**:
- `pytest tests/` returns `0 errors`
- No unplanned failures remain
- The rebaseline is documented with before/after counts and ADG evidence

---

## Rules

1. **Collection first, then blast radius**: clear collection blockers before chasing assertion noise.
2. **Stay under budget**: each wave must remain at or below `SAFE_OPERATING_CAP = 223,000` and never cross `HARD_MAX_CONTEXT = 262,000`.
3. **Do not widen scope casually**: keep production changes minimal and only when the test failure proves the source is the root cause.
4. **Rebaseline between waves**: every wave ends with a focused pytest run and a scope check.
5. **Refresh ADG after structural changes**: if imports, fixtures, or shared contracts move, regenerate ADG and compare the delta.
6. **Keep fixes atomic**: prefer small, reviewable batches over broad unbounded edits.

---

## ADG Impact Assessment

- This plan changes import hygiene, fixture gating, and test contracts, so ADG refreshes are required after each wave.
- Use the hot ADG cache to validate that no unexpected layer inversions or new edges appear after a batch.
- If a wave touches production code, capture the dependency delta before starting the next wave.
- Scope drift should fail closed: unexpected files after a wave mean the batch is paused and decontaminated before continuing.

---

## Rollback Strategy

1. Revert only the current wave batch with `git restore --source=HEAD --worktree --staged <files>` if a fix introduces regressions.
2. If a wave contaminates adjacent files, revert the wave checkpoint commit and re-run the scoped subset.
3. After rollback, run the targeted pytest subset and `--collect-only` again before resuming the next wave.

---

## Success Criteria

- [ ] `pytest --collect-only` under `tests/` reports `0 errors`
- [ ] The six waves all remain `GREEN` or `YELLOW` by `ContextWindowEstimator`
- [ ] `pytest tests/` completes with `0 errors` and no unplanned failures
- [ ] All remaining broken tests are either fixed or explicitly quarantined with root cause and owner
- [ ] ADG is refreshed and the final rebaseline is captured in a report

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---:|---|
| Collection errors | 0 | `python -m pytest tests/ --collect-only -q` |
| Full-suite errors | 0 | `python -m pytest tests/ -q` |
| Wave budgets | `<= 223,000` projected tokens per wave | `ContextWindowEstimator` output |
| Red waves | 0 | Wave table status column |
| ADG freshness | HOT | ADG cache status before/after each batch |

---

## Implementation Commands

```bash
python tools/adg_test_accelerator.py collection-safety --json docs/reports/adg_collection_analysis.json
python -m pytest tests/ --tb=short -q --maxfail=50
python -m pytest tests/unit/agentic_core/L0_routing tests/unit/agentic_core/L2_execution tests/unit/agentic_core/L5_safety -q
python -m pytest tests/unit/agentic_core/L4_state tests/e2e tests/integration -q
python -m pytest tests/ -q
```

---

## Evidence Notes

- The estimator run used the repo’s `ContextWindowEstimator` thresholds and produced six YELLOW waves with projected totals of `222,601`, `222,402`, `220,434`, `222,271`, `220,732`, and `215,233` tokens.
- The current pytest baseline and failure clusters were captured before drafting this plan so the wave order reflects the largest live patterns first.
- The hybrid strategy intentionally front-loads collection blockers, then attacks the biggest failure clusters to maximize burndown rate while staying inside the Kimi K2.5 safe operating cap.
