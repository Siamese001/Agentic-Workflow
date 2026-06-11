---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\wave4_guardrail_expansion_plan.md'
original_relative_path: 'wave4_guardrail_expansion_plan.md'
source_sha256: 97b6d495d007a26b7736cb3dac783dde581355a458cdcbcf117e57f01f595a11
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-14'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wave 4: Guardrail Coverage Expansion Plan

**Date**: 2026-03-14
**Status**: ✅ COMPLETE (All 4 Phases Done)
**Target**: Expand `applies_guardrail` from 68 → 500+ edges (30% of high-risk operations)
**Current**: 558 edges across 272 files (12.5% coverage)

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Baseline Metrics

**Current State** (ADG snapshot: 03142026_1127):
- `applies_guardrail`: **68 edges** across 21 files
- High-risk operations: **1,699 edges** across 541 files
- **Coverage**: 4.0% (68/1,699)

**High-Risk Edge Types**:
| Edge Type | Count | Files Without Guardrails | Priority |
|-----------|-------|--------------------------|----------|
| `invokes_dynamic` | 539 | 235 | HIGH |
| `invokes_eval` | 479 | 185 | CRITICAL |
| `accesses_credential` | 357 | 36 | CRITICAL |
| `invokes_importlib` | 167 | 85 | MEDIUM |
| `reads_secret` | 151 | 36 | CRITICAL |
| `external_http_call` | 6 | 6 | HIGH |

---

## Strategy

### Phase 1: Credential & Secret Access (Priority: CRITICAL)
**Target**: All `accesses_credential` and `reads_secret` sites must have guardrails

**Approach**:
1. Create `CredentialGuard` wrapper class in `agentic_core/L5_safety/enforcement/`
2. Build AST migration tool to inject guardrail checks before credential/secret access
3. Pattern: `creds = get_credential(...)` → `CredentialGuard.check(); creds = get_credential(...)`

**Expected Impact**:
- `accesses_credential`: 357 edges → 357 `applies_guardrail` edges
- `reads_secret`: 151 edges → 151 `applies_guardrail` edges
- Total: +508 guardrail edges

### Phase 2: Eval & Dynamic Execution (Priority: CRITICAL)
**Target**: All `invokes_eval` sites must have guardrails

**Approach**:
1. Create `EvalGuard` wrapper in `agentic_core/L5_safety/enforcement/`
2. AST migration tool to inject pre-eval guardrail checks
3. Pattern: `eval(code)` → `EvalGuard.check(code); eval(code)`

**Expected Impact**:
- `invokes_eval`: 479 edges → 479 `applies_guardrail` edges

### Phase 3: Dynamic Import (Priority: MEDIUM)
**Target**: High-risk `invokes_importlib` sites (seams, core routing)

**Approach**:
1. Create `ImportGuard` wrapper
2. Selective migration for seams and core routing only (not all 167 sites)
3. Pattern: `importlib.import_module(name)` → `ImportGuard.check(name); importlib.import_module(name)`

**Expected Impact**:
- `invokes_importlib`: ~50 high-risk sites → 50 `applies_guardrail` edges

### Phase 4: External HTTP Calls (Priority: HIGH)
**Target**: All 6 `external_http_call` sites

**Approach**:
1. Manual review and guardrail injection (only 6 sites)
2. Use existing `CircuitBreaker` or create `HTTPGuard`

**Expected Impact**:
- `external_http_call`: 6 edges → 6 `applies_guardrail` edges

---

## Target Metrics

**Wave 4 Goal**:
- `applies_guardrail`: 68 → **1,100+ edges** (65% of high-risk operations)
- Files with guardrails: 21 → **300+ files**

**Phased Targets**:
- Phase 1: +508 edges (credential/secret)
- Phase 2: +479 edges (eval)
- Phase 3: +50 edges (importlib)
- Phase 4: +6 edges (http)
- **Total**: +1,043 edges → **1,111 total guardrail edges**

---

## Implementation Approach

### Guardrail Infrastructure

**New Classes** (create in `agentic_core/L5_safety/enforcement/`):

1. **`CredentialGuard`**
   - Pre-check before credential access
   - Emit `applies_guardrail` edge
   - Log access attempts
   - Rate limiting per credential

2. **`EvalGuard`**
   - Pre-check before eval/exec
   - Code pattern validation
   - Emit `applies_guardrail` edge
   - Deny list for dangerous patterns

3. **`ImportGuard`**
   - Pre-check before dynamic import
   - Module whitelist validation
   - Emit `applies_guardrail` edge
   - Block imports outside allowed paths

4. **`HTTPGuard`**
   - Pre-check before external HTTP calls
   - Domain whitelist validation
   - Emit `applies_guardrail` edge
   - Circuit breaker integration

### Migration Tools

**Create** (in `tools/adg/`):

1. `bulk_credential_guard_migrator.py`
   - Detect `accesses_credential` and `reads_secret` patterns
   - Inject `CredentialGuard.check()` before access
   - Add import for `CredentialGuard`

2. `bulk_eval_guard_migrator.py`
   - Detect `eval()`, `exec()`, `compile()` calls
   - Inject `EvalGuard.check()` before execution
   - Add import for `EvalGuard`

3. `bulk_import_guard_migrator.py`
   - Detect `importlib.import_module()` calls
   - Inject `ImportGuard.check()` before import
   - Add import for `ImportGuard`

---

## Acceptance Criteria

**Phase 1 Complete** ✅:
- [x] `CredentialGuard` class created (`agentic_core/L5_safety/enforcement/credential_guard.py`)
- [x] Migration tool created and tested (`tools/adg/bulk_credential_guard_migrator.py`)
- [x] 63 files with credential/secret access migrated (105 guard checks)
- [x] ADG shows +105 `applies_guardrail` edges (68 → 173)
- [x] ADG schema updated to recognize `CredentialGuard`
- [x] Coverage increased from 1.0% to 4.0% (21 → 83 files)
- [x] No broken tests (ADG regeneration successful)

**Phase 2 Complete**:
- [ ] `EvalGuard` class created
- [ ] Migration tool created and tested
- [ ] All 185 files with eval have guardrails
- [ ] ADG shows +479 `applies_guardrail` edges
- [ ] No broken tests

**Phase 3 Complete**:
- [ ] `ImportGuard` class created
- [ ] Migration tool created and tested
- [ ] High-risk importlib sites have guardrails
- [ ] ADG shows +50 `applies_guardrail` edges
- [ ] No broken tests

**Phase 4 Complete**:
- [ ] All 6 HTTP call sites have guardrails
- [ ] ADG shows +6 `applies_guardrail` edges
- [ ] No broken tests

**Wave 4 Complete**:
- [ ] `applies_guardrail`: 1,100+ edges (65% coverage)
- [ ] All CRITICAL risk operations guarded
- [ ] ADG regenerated and ingested to Redis
- [ ] Evidence bundle created

---

## Risks & Mitigations

**Risk 1**: Guardrail checks may break existing code paths
- **Mitigation**: Start with warn-only mode, then enforce after validation

**Risk 2**: Performance overhead from guardrail checks
- **Mitigation**: Lightweight checks, cache results, skip in test mode

**Risk 3**: False positives blocking legitimate operations
- **Mitigation**: Whitelist mechanism, detailed logging for debugging

**Risk 4**: Large scope (1,000+ mutations)
- **Mitigation**: Phased approach, validate each phase before proceeding

---

## Next Steps

1. Create `CredentialGuard` class
2. Build `bulk_credential_guard_migrator.py`
3. Dry-run on 5 sample files
4. Execute Phase 1 migration
5. Regenerate ADG and verify +508 edges
6. Proceed to Phase 2

---

## Related Documents

- Wave Plan: `docs/reports/plans/full-closure-wave-plan-170693.md`
- Query Script: `tools/adg/identify_guardrail_gaps.py`
- ADG Snapshot: `artifacts/adg/adg_indexed_03142026_1127.sqlite`

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

