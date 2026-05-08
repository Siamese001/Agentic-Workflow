# C0 Policy Rectification — Deferred Scope

**Parent Plan**: `c0-policy-rectification-f7b2a9` (Completed 2026-05-08)  
**Status**: Not Started  
**Created**: 2026-05-08

---

## 1. Purpose

This plan captures deferred scope from `c0-policy-rectification-f7b2a9` that was intentionally descoped to keep the parent plan bounded. Items here are future work, not current blockers.

---

## 2. Deferred Scope Items (from Parent Plan §16 Uncertainty Areas)

### DS-1: L3 Managed Workflow Step-Level C0 Policy Inheritance

**Parent Plan Reference**: Section 8 "Fix L3 managed workflow behavior"

**Description**:  
L3 step contracts must carry inherited or step-specific `c0_policy`. A managed workflow may contain:
- Steps that do not need grounding
- Steps that use preloaded context  
- Steps that require fresh C0 retrieval

**Current State**: Basic `c0_policy` structure exists, but L3 orchestration does not propagate step-level policies.

**Work Required**:
- Add `c0_policy` field to `StepContract` or equivalent
- Implement inheritance logic in L3 workflow engine
- Ensure L3 does not make implicit C0 decisions outside the contract

**Files Likely Affected**:
- `agentic_core/L3_orchestration/types/step_contract_types.py`
- `agentic_core/L3_orchestration/workflow_engine.py` (or equivalent)
- `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py`

**Acceptance Criteria**:
- [ ] L3 step can declare its own `c0_policy`
- [ ] Steps inherit parent workflow `c0_policy` when not specified
- [ ] Tests prove mixed workflows (some steps bypass, some retrieve)

---

### DS-2: Full Removal of Deprecated L1 preflight()

**Parent Plan Reference**: Section 2 "Refactor L1 C0 preflight logic"

**Description**:  
The legacy `preflight()` function in `L1_cognition/c0_context/preflight.py` is currently deprecated with `DeprecationWarning`. It should be fully removed after transition period.

**Current State**: Function shimmed to delegate to `analyze_grounding_advisory()`

**Work Required**:
- Identify all callers of deprecated `preflight()`
- Migrate callers to `analyze_grounding_advisory()`
- Remove deprecated function
- Update `__all__` exports

**Files Likely Affected**:
- `agentic_core/L1_cognition/c0_context/preflight.py`
- Any test files using legacy `preflight()`

**Acceptance Criteria**:
- [ ] Zero calls to deprecated `preflight()` in codebase
- [ ] Function removed from module
- [ ] Tests updated to use new advisory function

---

### DS-3: Additional R4-like Entrypoints Audit

**Parent Plan Reference**: Section 10 "Anti-pattern scan"

**Description**:  
The parent plan fixed `integrated_r4_deterministic_pipeline_run.py`. Other R4-like entrypoints may have similar hardcoded bypass issues.

**Files to Audit**:
- `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py`
- `agentic_core/runtime/entrypoints/integrated_safe_reuse_run.py`
- Any apps_* `__main__.py` with R4 routes

**Work Required**:
- Search for `build_c0_bypass_receipt` calls with hardcoded reasons
- Verify they use `RouteContract.c0_policy` or update them

**Acceptance Criteria**:
- [ ] All R4 entrypoints use typed bypass reasons
- [ ] No hardcoded `GROUNDING_NOT_REQUIRED` strings remain

---

### DS-4: Observability / OTEL Fields for C0 Policy Tracing

**Parent Plan Reference**: Section 8 "Observability and receipts"

**Description**:  
Add explicit OTEL/span fields showing C0 policy provenance.

**Required Fields**:
- `l1_grounding_required` (advisory signal)
- `route_c0_mode` (frozen decision)
- `evidence_contract_required` (PA enforcement trigger)
- `c0_preflight_status` (eligibility result)
- `c0_bypass_reason` (typed bypass reason)
- `c0_policy_decision_source` (traceability: L1_PLAN_DERIVED, CACHE_TERMINAL, etc.)

**Work Required**:
- Add fields to OTEL span emitters in C0 pipeline
- Update `otel_ingest_to_runtime_adg` to capture new fields
- Add to PA boundary check spans

**Files Likely Affected**:
- `agentic_core/runtime/prove_requirements/otel_emitter.py`
- `agentic_core/L0_routing/c0_retrieval/preflight.py` (span emission)
- `agentic_core/prompt_governance/prompt_assembly/pa0_boundary.py`

---

### DS-5: Backward Compatibility / Migration Strategy

**Parent Plan Reference**: Section 16 "Uncertainty Areas"

**Description**:  
Existing `RouteContract` instances without `c0_policy` field need migration strategy.

**Options**:
1. Lazy migration: Code checks for `None` and derives from legacy fields (current approach)
2. Eager migration: Background job rewrites existing contracts
3. Hard cutoff: Require c0_policy after flag date

**Work Required**:
- Decide strategy
- Implement migration tooling if eager
- Set deprecation timeline
- Document breaking changes

---

### DS-6: Additional PA Stages (PA4, PA7) C0 Policy Enforcement

**Parent Plan Reference**: Section 7 "Fix Prompt Assembly boundary"

**Description**:  
Parent plan updated `pa0_boundary.py`. Other PA stages may need similar C0 policy awareness.

**Files to Review**:
- `agentic_core/prompt_governance/prompt_assembly/pa4_validation.py`
- `agentic_core/prompt_governance/prompt_assembly/pa7_dispatch_states.py`
- `agentic_core/prompt_governance/orchestrator.py`

**Work Required**:
- Audit for C0-related validation
- Ensure consistency with pa0_boundary enforcement

---

### DS-7: Production Rollout Monitoring

**Parent Plan Reference**: N/A - operational concern

**Description**:  
Monitoring for C0 policy enforcement in production.

**Metrics to Track**:
- Rate of `c0_policy=None` fallback (should decrease over time)
- Bypass reason distribution (typed vs legacy)
- PA boundary rejection rate by reason
- C0 preflight eligibility rate by c0_mode

**Work Required**:
- Add dashboard queries
- Set up alerts for unexpected bypass rates
- Weekly report on C0 policy adoption

---

## 3. Wave Structure

| Wave | Scope | Files | Est. Tokens | Status |
|------|-------|-------|-------------|--------|
| W1 | L3 step-level c0_policy | L3 orchestration types, workflow engine | ~4k | **Completed** |
| W2 | Remove deprecated preflight() | L1 preflight, tests | ~2k | **Completed** |
| W3 | Audit additional entrypoints | R4-like entrypoints | ~2k | Not Started |
| W4 | OTEL observability | C0 pipeline, PA boundary | ~3k | Not Started |
| W5 | Migration strategy + docs | Ops docs, deprecation timeline | ~2k | Not Started |

---

## 4. Dependencies

- **Parent plan must be merged to main** (DONE 2026-05-08, commit 9dc8317c21)
- **CI gates green** on parent plan changes
- **No production incidents** from parent plan changes for 7+ days

---

## 5. Non-Goals

- Do NOT add new C0 modes beyond the 5 existing (RETRIEVE_REQUIRED, BYPASS_*)
- Do NOT change RouteContract shape (only add step-level in L3)
- Do NOT implement C0 retrieval internals (out of scope)
- Do NOT modify L2/L5/L6 for this deferred work

---

## 6. Acceptance Criteria for This Plan

- [ ] All DS items have implementation plans or tickets
- [ ] At least 2 waves completed before plan considered "Live"
- [ ] No deferred item blocks parent plan acceptance

---

## 7. References

- Parent Plan: `.windsurf/plans/c0-policy-rectification-f7b2a9.md`
- Commit: `9dc8317c21` (c0-policy-rectification-f7b2a9: Single authoritative C0 policy path)
- Notion Parent: https://www.notion.so/c0-policy-rectification-f7b2a9-35a27693f55c81b3aaebcf61b7661395
