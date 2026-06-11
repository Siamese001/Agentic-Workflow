---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg-architectural-violations-fix-plan-03242026.md'
original_relative_path: 'adg-architectural-violations-fix-plan-03242026.md'
source_sha256: eab75f4310f998ba9b1822b80f7213a7de583d64bbe0a93a07b868e7f1faf68c
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Architectural Violations Fix Plan

**Date:** 2026-03-24
**Status:** 📋 PLAN CREATED | 🔄 IMPLEMENTATION STARTING
**Objective:** Fix all architectural violations in ADG with prioritized approach

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


## 🎯 CURRENT STATE ASSESSMENT

### Known Architectural Issues
Based on previous analysis, we have identified several categories of violations:

1. **Layer Gravity Violations** (817 violations)
   - L0-L6 modules importing from L_RUNTIME layer
   - Violates rule: LN can only import from L0..LN

2. **Static/Runtime ADG Contamination**
   - Runtime relations in static ADG (502,628 edges)
   - Static relations in runtime ADG
   - Violates mental model separation

3. **Silent Swallower Violations** (12,562 violations)
   - ImportError silent swallows (6,952)
   - ValueError silent swallows (1,016)
   - Broad exception handling (2,379)

4. **Test Enforcement Violations** (65,350 violations)
   - Missing category markers (54,279)
   - Unmarked skips (7,589)
   - Import error patterns (3,480)

---

## 🚀 PRIORITIZATION MATRIX

### Priority 1: CRITICAL (Fix Immediately)
| Issue | Impact | Effort | Dependencies |
|-------|--------|-------|--------------|
| Layer Gravity Violations | HIGH | MEDIUM | None |
| Silent Swallower HIGH severity | HIGH | LOW | None |

### Priority 2: HIGH (Fix This Week)
| Issue | Impact | Effort | Dependencies |
|-------|--------|-------|--------------|
| Static/Runtime ADG Separation | HIGH | HIGH | New scanners |
| Test Enforcement HIGH severity | MEDIUM | MEDIUM | CI updates |

### Priority 3: MEDIUM (Fix Next Week)
| Issue | Impact | Effort | Dependencies |
|-------|--------|-------|--------------|
| Test Enforcement MEDIUM severity | MEDIUM | HIGH | Classification |
| Silent Swallower MEDIUM severity | MEDIUM | MEDIUM | Exception handling |

### Priority 4: LOW (Fix When Time Allows)
| Issue | Impact | Effort | Dependencies |
|-------|--------|-------|--------------|
| Test Enforcement LOW severity | LOW | HIGH | Documentation |
| Silent Swallower LOW severity | LOW | LOW | Comments |

---

## 📋 IMPLEMENTATION PLAN

### Phase 1: Critical Fixes (Day 1-2)

#### 1.1 Fix Layer Gravity Violations
**Problem:** 817 L0-L6 modules importing from L_RUNTIME

**Solution:** Create L_CONTRACTS layer for cross-layer interfaces

**Steps:**
1. Create `agentic_core/L_CONTRACTS/` directory
2. Move `lifecycle_trace_contract.py` to L_CONTRACTS
3. Update 817 import statements
4. Regenerate ADG to verify 0 layer violations

**Files to modify:** ~817 files
**Expected outcome:** 0 layer gravity violations

#### 1.2 Fix Silent Swallower HIGH Severity
**Problem:** 8,468 HIGH severity violations (ImportError, ValueError, etc.)

**Solution:** Replace with proper error handling

**Steps:**
1. Fix ImportError violations (6,952)
   - Add guardian comments for optional deps
   - Use pytest.importorskip in tests
2. Fix ValueError violations (1,016)
   - Add input validation
   - Proper error messages
3. Fix AttributeError/TypeError violations (397)
   - Fix programming errors

**Files to modify:** ~2,000 files
**Expected outcome:** 0 HIGH severity violations

### Phase 2: High Priority Fixes (Day 3-5)

#### 2.1 Static/Runtime ADG Separation
**Problem:** Runtime contamination in static ADG

**Solution:** Use clean scanners already created

**Steps:**
1. Deploy `truly_clean_static_adg.py` for production
2. Deploy `create_runtime_adg.py` for runtime collection
3. Update CI to use clean static ADG
4. Verify separation with evidence

**Files to modify:** CI configuration, ADG generation scripts
**Expected outcome:** 100% static/runtime separation

#### 2.2 Test Enforcement HIGH Severity
**Problem:** 7,589 unmarked skips affecting test reliability

**Solution:** Add proper markers and fix skip patterns

**Steps:**
1. Add @pytest.mark.core/optional/external markers
2. Remove inappropriate skips from core tests
3. Replace try/except ImportError with importorskip

**Files to modify:** ~1,000 test files
**Expected outcome:** Deterministic test execution

### Phase 3: Medium Priority Fixes (Week 2)

#### 3.1 Test Enforcement MEDIUM Severity
**Problem:** 54,279 missing category markers, 2,379 broad exceptions

**Solution:** Systematic marker addition and exception narrowing

**Steps:**
1. Bulk classify tests by directory patterns
2. Add @pytest.mark.core to unit/integration tests
3. Replace `except Exception` with specific types
4. Manual review of edge cases

**Files to modify:** ~10,000 files
**Expected outcome:** 100% test classification

#### 3.2 Silent Swallower MEDIUM Severity
**Problem:** 2,379 broad exception violations

**Solution:** Narrow exception types

**Steps:**
1. Replace `except Exception` with specific types
2. Add proper error handling for each case
3. Document legitimate silent swallows

**Files to modify:** ~2,000 files
**Expected outcome:** Precise exception handling

### Phase 4: Low Priority Cleanup (Week 3)

#### 4.1 Test Enforcement LOW Severity
**Problem:** 1,715 violations need documentation

**Solution:** Add guardian comments and review

**Steps:**
1. Add guardian comments for legitimate cases
2. Review and remove unnecessary silent swallows
3. Update documentation

**Files to modify:** ~1,000 files
**Expected outcome:** Full compliance

---

## 🛠️ IMPLEMENTATION STRATEGY

### Daily Targets
- **Day 1:** Fix layer gravity violations (817 files)
- **Day 2:** Fix silent swallower HIGH severity (2,000 files)
- **Day 3:** Deploy clean ADG separation
- **Day 4:** Fix test enforcement HIGH severity (1,000 files)
- **Day 5:** Validate critical fixes

### Weekly Targets
- **Week 1:** All Priority 1 & 2 fixes complete
- **Week 2:** All Priority 3 fixes complete
- **Week 3:** All Priority 4 fixes complete

### Quality Gates
1. **Layer gravity:** 0 violations
2. **Silent swallows:** 0 HIGH severity
3. **ADG separation:** 100% compliance
4. **Test enforcement:** 0 HIGH severity

---

## 📊 SUCCESS METRICS

### Before Fixes
- **Layer violations:** 817
- **Silent swallows HIGH:** 8,468
- **ADG contamination:** 502,628 runtime edges in static
- **Test violations HIGH:** 7,589

### After Fixes (Target)
- **Layer violations:** 0
- **Silent swallows HIGH:** 0
- **ADG contamination:** 0 (perfect separation)
- **Test violations HIGH:** 0

### Compliance Improvement
- **Architectural integrity:** 100%
- **Error handling quality:** Significantly improved
- **Test reliability:** Deterministic
- **ADG accuracy:** Pure static/runtime separation

---

## 🚀 EXECUTION PLAN

### Immediate Actions (Today)
1. **Create L_CONTRACTS layer**
2. **Start layer gravity fixes**
3. **Begin silent swallower fixes**

### This Week
1. **Complete all critical fixes**
2. **Deploy clean ADG separation**
3. **Fix test enforcement issues**

### Validation
1. **Run architectural compliance checks**
2. **Generate evidence reports**
3. **Update documentation**

---

## 📞 NEXT STEPS

### Start Implementation
1. **Execute Phase 1.1:** Layer gravity fixes
2. **Execute Phase 1.2:** Silent swallower fixes
3. **Validate critical fixes**

### Monitoring Progress
1. **Daily progress reports**
2. **Violation count tracking**
3. **Quality gate verification**

### Documentation
1. **Update architectural policies**
2. **Create fix procedures**
3. **Train on compliance**

---

**This plan provides a clear, prioritized approach to fixing all ADG architectural violations. Critical fixes will be completed first, followed by systematic improvement of the entire codebase.**

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

