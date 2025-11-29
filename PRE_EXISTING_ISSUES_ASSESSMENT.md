# Pre-Existing Issues Assessment
## Technical Debt Identified After Repository Restructuring

**ASSESSMENT DATE:** November 28, 2025  
**SCOPE:** Analysis of pre-existing issues exposed during import testing

---

## CRITICAL FINDINGS

### 🚨 OUTREAST_ENGINE - SYSTEMATIC TECHNICAL DEBT

**ISSUE SEVERITY:** HIGH - Outreach engine is fundamentally broken  
**ROOT CAUSE:** Partial migration from LIC codebase with unresolved dependencies

**SPECIFIC ISSUES:**
1. **Missing 'core' module dependencies:** 26 files reference `from core.models.models import` and similar patterns
2. **Broken __init__.py imports:** Multiple class name mismatches between exports and actual implementations
3. **Incomplete architecture:** References to old project structure that was never fully migrated

**AFFECTED FILES:**
- `apps/outreach_engine/l2/execution.py` - Core execution layer broken
- `apps/outreach_engine/l1/*` - All planning layers have core dependencies
- `apps/outreach_engine/l2/*` - All execution layers have core dependencies  
- `apps/outreach_engine/l3/*` - All orchestration layers have core dependencies
- `apps/outreach_engine/l4/*` - All memory/state layers have core dependencies
- `apps/outreach_engine/l5/*` - All safety/validation layers have core dependencies

**FIXES APPLIED:**
- ✅ Fixed QueryPlan import in __init__.py (removed non-existent class)
- ✅ Fixed SectionTemplate import in __init__.py (replaced with MessageSection)

**REMAINING ISSUES:**
- ❌ 26 files with `from core` import dependencies need resolution
- ❌ Requires architectural redesign or core module recreation

---

### ⚠️ RESUME_ENGINE - MINOR DEPENDENCY ISSUE

**ISSUE SEVERITY:** LOW - Single dependency issue  
**ROOT CAUSE:** Missing RG_capabilities module

**SPECIFIC ISSUE:**
- `apps/resume_engine/l5/rg_safety_validator.py` references `from RG_capabilities.rg_atomic_spec import ATOMIC_RG_SPEC`

**STATUS:** Temporarily excluded from imports until RG_capabilities is located

---

## RECOMMENDATIONS

### IMMEDIATE ACTIONS:
1. **Document outreach_engine as non-functional** due to systematic dependency issues
2. **Focus on resume_engine functionality** as primary working application
3. **Search for RG_capabilities module** to resolve resume_engine safety validator

### FUTURE ARCHITECTURAL WORK:
1. **Outreach_engine requires complete architectural redesign** or core module recreation
2. **Consider outreach_engine as legacy code** requiring migration rather than fixes
3. **Resume_engine is production-ready** with minor dependency resolution needed

---

## FUNCTIONALITY STATUS

| Component | Status | Issues | Resolution Path |
|-----------|--------|--------|-----------------|
| apps.resume_engine | ✅ WORKING | RG_capabilities dependency | Locate module or create mock |
| apps.outreach_engine | ❌ BROKEN | 26 core dependencies, broken imports | Architectural redesign required |
| agentic_core.runtime | ✅ WORKING | None | N/A |
| agentic_core.config | ✅ WORKING | None | N/A |
| data.production_inputs | ✅ WORKING | None | N/A |
| docs.root | ✅ WORKING | None | N/A |

---

## CONCLUSION

**RESUME_ENGINE:** Primary application is functional with minor technical debt  
**OUTREAST_ENGINE:** Requires extensive architectural work beyond scope of pre-existing issue fixes  

**RECOMMENDATION:** Proceed with resume_engine as primary focus, document outreach_engine as legacy technical debt requiring future architectural redesign.
