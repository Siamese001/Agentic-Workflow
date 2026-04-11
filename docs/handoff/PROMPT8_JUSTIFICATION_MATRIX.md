# Prompt 8 Phase 1: Auto-Remediation Justification Matrix

> **Status:** Phase 1 Analysis Complete — Recommendation: Dry-Run Pilot Only  
> **Date:** 2026-04-10  
> **Scope:** Evaluate graph hotspot auto-remediation safety

---

## 1. Evaluation Criteria

| Criterion | Description | Weight |
|-----------|-------------|--------|
| **C1: Low blast radius** | Changes affect limited code surface | Required |
| **C2: Mechanically checkable** | Can verify correctness without deep semantic analysis | Required |
| **C3: Reversible** | Can rollback without data loss | Required |
| **C4: Testable with clear score improvement** | Before/after graph score delta is measurable | Required |
| **C5: No silent behavior change** | Changes are structural, not behavioral | Required |

**Safety Score:** 1-5 (5 = safest, 1 = unsafe)

---

## 2. Remediation Classes Ranked by Safety

### Class A: Generate Patch Suggestions (Human Approval)

| Aspect | Evaluation |
|--------|------------|
| **What it changes** | Produces `.patch` files with suggested edits |
| **Graph signal** | All hotspot types |
| **Safety score** | **5/5** |
| **Blast radius** | Zero (no automatic application) |
| **Mechanically checkable** | Yes (patch syntax validation) |
| **Reversible** | Yes (patch not applied) |
| **Testable score improvement** | Yes (can measure proposed change) |
| **Silent behavior change** | None (human reviews before apply) |
| **Failure modes** | Patch rejected by human |
| **Rollback plan** | N/A - nothing applied |
| **Expected score improvement** | N/A (suggestion only) |

**Verdict:** ✅ **SAFEST — Recommended as default behavior**

---

### Class B: Add Declarative __all__ / Export Boundaries

| Aspect | Evaluation |
|--------|------------|
| **What it changes** | Adds `__all__` list to limit module exports |
| **Graph signal** | Chokepoint bridge (reduces fan-out visibility) |
| **Safety score** | **4/5** |
| **Blast radius** | Low (declarative only, doesn't change behavior) |
| **Mechanically checkable** | Yes (AST can verify `__all__` is list of strings) |
| **Reversible** | Yes (delete `__all__` line) |
| **Testable score improvement** | Yes (bridge score should decrease) |
| **Silent behavior change** | None (affects `from module import *` only) |
| **Failure modes** | Breaks `import *` usages (detectable by tests) |
| **Rollback plan** | Remove `__all__`, restore original exports |
| **Expected score improvement** | 10-30% bridge score reduction |

**Verdict:** ✅ **ACCEPTABLE for pilot with dry-run default**

---

### Class C: Move Type-Only Constants to Neutral Module

| Aspect | Evaluation |
|--------|------------|
| **What it changes** | Extracts type definitions/constants to shared types module |
| **Graph signal** | Reverse dependency (reduces coupling) |
| **Safety score** | **3/5** |
| **Blast radius** | Medium (cross-module imports change) |
| **Mechanically checkable** | Partial (type checking helps) |
| **Reversible** | Difficult (multiple modules updated) |
| **Testable score improvement** | Yes (reverse dep score decreases) |
| **Silent behavior change** | Low risk for type-only, higher for runtime constants |
| **Failure modes** | Circular imports, runtime errors, test failures |
| **Rollback plan** | Move back + update all importers (expensive) |
| **Expected score improvement** | 15-40% reverse dep score reduction |

**Verdict:** ⚠️ **CONDITIONAL — Only for truly type-only, no runtime behavior**

---

### Class D: Add Interface Abstraction (Protocol/ABC)

| Aspect | Evaluation |
|--------|------------|
| **What it changes** | Creates interface + redirects implementations |
| **Graph signal** | Chokepoint bridge (extracts interface boundary) |
| **Safety score** | **2/5** |
| **Blast radius** | High (multiple files, runtime dispatch changes) |
| **Mechanically checkable** | No (requires semantic understanding) |
| **Reversible** | Complex (multiple imports change) |
| **Testable score improvement** | Unclear (may increase complexity score) |
| **Silent behavior change** | Yes (dispatch behavior changes) |
| **Failure modes** | Import errors, dispatch failures, test breaks |
| **Rollback plan** | Inline interfaces + revert imports (very expensive) |
| **Expected score improvement** | Uncertain — may trade bridge for complexity |

**Verdict:** ❌ **REJECTED — Too complex, not mechanically checkable**

---

### Class E: Module Splitting (Responsibility Separation)

| Aspect | Evaluation |
|--------|------------|
| **What it changes** | Splits one module into multiple files |
| **Graph signal** | Reverse dependency, multi-signal hotspot |
| **Safety score** | **1/5** |
| **Blast radius** | Very high (all importers change) |
| **Mechanically checkable** | No (semantic analysis required) |
| **Reversible** | Very difficult (merge modules + revert imports) |
| **Testable score improvement** | Hard to isolate (scores shift around) |
| **Silent behavior change** | Yes (import paths change behavior) |
| **Failure modes** | Import errors, circular deps, test cascade failures |
| **Rollback plan** | Essentially full revert (prohibitively expensive) |
| **Expected score improvement** | Unclear — scores redistribute unpredictably |

**Verdict:** ❌ **REJECTED — Too risky, violates all safety criteria**

---

### Class F: Dependency Inversion

| Aspect | Evaluation |
|--------|------------|
| **What it changes** | Flips dependency direction, introduces abstractions |
| **Graph signal** | SCC cycle breaking, reverse dependency |
| **Safety score** | **1/5** |
| **Blast radius** | Very high (architecture change) |
| **Mechanically checkable** | No (requires deep semantic analysis) |
| **Reversible** | Very difficult (revert all direction changes) |
| **Testable score improvement** | Hard to predict (may create new hotspots) |
| **Silent behavior change** | Yes (initialization order, runtime behavior) |
| **Failure modes** | Infinite recursion, initialization errors, test failures |
| **Rollback plan** | Full architecture revert (extremely expensive) |
| **Expected score improvement** | Uncertain — may trade one problem for another |

**Verdict:** ❌ **REJECTED — Architecture change, not safe to automate**

---

## 3. Summary Ranking

| Rank | Class | Safety Score | Auto-Apply | Dry-Run | Recommendation |
|------|-------|--------------|------------|---------|----------------|
| 1 | **A: Patch suggestions** | 5/5 | ❌ No | ✅ Yes | **Default behavior** |
| 2 | **B: __all__ exports** | 4/5 | ⚠️ Conditional | ✅ Yes | **Pilot candidate** |
| 3 | **C: Type constants** | 3/5 | ❌ No | ⚠️ Conditional | Future consideration |
| 4 | D: Interface abstraction | 2/5 | ❌ No | ❌ No | Reject |
| 5 | E: Module splitting | 1/5 | ❌ No | ❌ No | Reject |
| 6 | F: Dependency inversion | 1/5 | ❌ No | ❌ No | Reject |

---

## 4. Explicit Recommendation

### PRIMARY RECOMMENDATION: **Dry-Run Patch Generation Only**

**Rationale:**
1. **Safety paramount:** Only Class A (patch suggestions) and Class B (`__all__` exports) meet safety criteria
2. **Human in the loop:** Even for Class B, human approval should be required
3. **Bounded risk:** Dry-run produces artifacts, doesn't change code
4. **Measurable:** Can validate graph score improvement before human review
5. **Reversible:** Human decides whether to apply; no automatic irreversible changes

### BOUNDED PILOT SCOPE (If Proceeding)

**Class B Pilot: Declarative `__all__` Export Boundaries**

- **Target signal:** Chokepoint bridge hotspots only
- **Protected layers:** Default deny (L0-L6, L_APP, L_SHARED, L_RUNTIME)
- **Allowlist:** Non-protected layers only (L_TOOLS, tests, experiments)
- **Safety gates:**
  1. Must be single-signal (bridge only, not multi-signal)
  2. No SCC involvement
  3. Score improvement measurable
  4. AST validation of `__all__` syntax
  5. Test pass verification on dry-run
- **Default mode:** Dry-run patch generation
- **Auto-apply:** DISABLED by default (human approval required)
- **Rollback:** Simple (remove `__all__` line)

---

## 5. Allowlist / Denylist Rules

### Explicit Denylist (Never Auto-Remediate)

| Category | Rule | Rationale |
|----------|------|-----------|
| **Protected layers** | Deny all auto-remediation in L0-L6, L_APP, L_SHARED, L_RUNTIME | Critical code too risky |
| **Multi-signal hotspots** | Deny auto-remediation if 2+ signals active | Complex interactions unpredictable |
| **SCC/cycles** | Deny auto-remediation on cycle-breaking | Architecture decision, not mechanical fix |
| **High blast radius** | Deny if blast radius > 200 | Change impact too broad |
| **Behavioral changes** | Deny if any runtime behavior change possible | Silent bugs unacceptable |

### Conditional Allowlist (Dry-Run OK, Auto-Apply Denied)

| Category | Rule | Conditions |
|----------|------|------------|
| **Declarative exports** | Allow `__all__` addition | Single-signal bridge, non-protected, type-only exports |
| **Patch generation** | Allow patch creation for human review | All hotspot types, any layer |

---

## 6. Phase 2 Decision

### GO: Implement Bounded Pilot for Class B

**Scope:**
- Dry-run patch generation for `__all__` export boundaries
- Target: Chokepoint bridge hotspots in non-protected layers
- Output: `.patch` files with human approval workflow
- No auto-apply on CI merges

**Success Criteria:**
1. Patch generation produces syntactically valid `__all__` lists
2. Bridge score improvement measurable in dry-run simulation
3. No test failures in dry-run validation
4. Human review workflow functional
5. No auto-apply without explicit human opt-in

### NO-GO: Stay Advisory-Only

**If any of:**
- Team decides human judgment always required
- Pilot complexity exceeds value
- Safety concerns remain unresolved

**Then:** Prompt 8 ends here with "advisory-only" policy locked.

---

## 7. Final Policy Statement

> **Graph hotspot auto-remediation is restricted to dry-run patch generation only.**
>
> **Auto-apply is prohibited for:**
> - All protected layers (L0-L6, L_APP, L_SHARED, L_RUNTIME)
> - All multi-signal hotspots
> - All SCC/cycle cases
> - All behavioral changes
>
> **Bounded pilot permitted:**
> - Declarative `__all__` exports for single-signal bridge hotspots
> - Non-protected layers only
> - Dry-run by default, human approval required for apply
>
> **Default behavior:** Generate patch suggestions for human review.

---

*Phase 1 Complete — Phase 2 bounded pilot justified for Class B only*
