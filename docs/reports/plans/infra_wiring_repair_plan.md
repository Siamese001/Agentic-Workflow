# Infrastructure Wiring Repair Plan
**Generated:** 2026-04-08
**Purpose:** Prioritized surgical repair plan for infrastructure wiring violations

## Executive Summary

This document contains the prioritized repair plan for all detected infrastructure wiring violations. Fixes are ordered by severity and impact, with exact file/symbol evidence, architecture law violations, minimal remediation steps, and expected ADG edge changes.

**Total Violations to Fix:** 1
**Priority Order:** P0 → P1 → P2 → P3
**Estimated Total Effort:** LOW (single file, well-defined replacement pattern)

---

## Repair Priority Order

### Priority 1: apps_* to Raw Infra Violations (P0 HARD FAIL)
**Violations:** 1
**Effort:** LOW
**Risk:** MEDIUM
**Timeline:** Immediate

### Priority 2: Raw Write/Provider/Network Bypasses (P0 HARD FAIL)
**Violations:** 0
**Effort:** N/A
**Risk:** N/A
**Timeline:** N/A

### Priority 3: Missing Control-Plane Choke Points (P1 HARDENING FAIL)
**Violations:** 0
**Effort:** N/A
**Risk:** N/A
**Timeline:** N/A

### Priority 4: Critical Dormant Infra on Runtime Spine (P1 HARDENING FAIL)
**Violations:** 0
**Effort:** N/A
**Risk:** N/A
**Timeline:** N/A

### Priority 5: Adapter Duplication (P2 WARNING)
**Violations:** 0
**Effort:** N/A
**Risk:** N/A
**Timeline:** N/A

### Priority 6: Experimental Cleanup (P3 WATCH)
**Violations:** 0
**Effort:** N/A
**Risk:** N/A
**Timeline:** N/A

---

## Detailed Repair Plans

### Repair #001: Fix apps_rfp Direct ChromaDB Import

**Violation ID:** #001
**Severity:** P0 HARD FAIL
**Priority:** 1 (Highest)
**Status:** PENDING

**File Evidence:**
- **File:** `apps_rfp/engines/proposal_retrieval_engine.py`
- **Current Import Pattern:** `import chromadb` or `from chromadb import ...`
- **Current Usage Pattern:** Direct ChromaDB client instantiation

**Architecture Law Violated:**
> apps_* surfaces must not directly own raw infrastructure clients unless explicitly architecture-approved.

**Current ADG Edge Path:**
```
apps_rfp/engines/proposal_retrieval_engine.py → chromadb (bypasses L4 adapter)
```

**Expected ADG Edge After Repair:**
```
apps_rfp/engines/proposal_retrieval_engine.py → agentic_core/L4_state/utils/client/chroma_client.py → chromadb
```

**Minimal Remediation Steps:**

**Step 1: Read current file to understand usage pattern**
- Read `apps_rfp/engines/proposal_retrieval_engine.py` completely
- Identify all ChromaDB usage locations (imports, client instantiation, method calls)
- Document current API surface used

**Step 2: Add L4 adapter import**
- Remove: `import chromadb` or `from chromadb import ...`
- Add: `from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient`

**Step 3: Replace client instantiation**
- Find: `chromadb.PersistentClient(path=...)` or similar
- Replace with: `SovereignChromaClient(persist_dir=...)`

**Step 4: Update method calls to use adapter interface**
- Adapter methods: `get_collection()`, `add_documents()`, `query()`, `get_collection_stats()`, `list_collections()`, `delete_collection()`
- Verify method signatures match current usage
- Update call sites if needed

**Step 5: Remove fallback embedding logic if present**
- SovereignChromaClient has built-in fallback embeddings
- Remove any custom embedding generation code if redundant

**Step 6: Test the changes**
- Run pytest on apps_rfp tests
- Verify proposal retrieval still works
- Check for any runtime errors

**Step 7: Verify ADG edge update**
- Regenerate ADG after fix
- Verify new edge path: `apps_rfp → L4_chroma_client → chromadb`
- Confirm old direct edge removed

**Code Changes Required:**

**Before (Expected Pattern):**
```python
import chromadb
from chromadb import PersistentClient

class ProposalRetrievalEngine:
    def __init__(self, persist_dir="artifacts/chromadb"):
        self.client = PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection("proposals")
    
    def query(self, query_text, n_results=10):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results
```

**After (Required Pattern):**
```python
from agentic_core.L4_state.utils.client.chroma_client import SovereignChromaClient

class ProposalRetrievalEngine:
    def __init__(self, persist_dir="artifacts/chromadb"):
        self.client = SovereignChromaClient(persist_dir=persist_dir)
        self.collection = self.client.get_collection("proposals")
    
    def query(self, query_text, n_results=10):
        results = self.client.query(
            collection_name="proposals",
            query_texts=[query_text],
            n_results=n_results
        )
        return results
```

**Risk Assessment:**
- **Breaking Risk:** MEDIUM - API surface differs between raw client and adapter
- **Effort:** LOW - Single file, well-defined replacement pattern
- **Regression Risk:** LOW - Adapter provides equivalent functionality
- **Test Coverage:** Unknown - need to verify tests exist

**Verification Steps:**
1. Run `pytest tests/unit/apps_rfp/` to verify no test failures
2. Run `pytest tests/integration/apps_rfp/` to verify integration tests pass
3. Manually test proposal retrieval if integration tests not available
4. Regenerate ADG: `python tools/generate_full_adg.py`
5. Query ADG to verify edge path update
6. Run violation detection scan to confirm fix

**Rollback Plan:**
If the fix causes issues:
1. Revert file to original version
2. Add guardian exemption comment: `# guardian: allow-raw-infra -- apps_rfp ChromaDB direct import pending adapter refactoring`
3. Document exemption in ratchet tracking
4. Schedule follow-up refactoring

**Estimated Time:** 30-60 minutes
**Dependencies:** None (standalone fix)

---

## No Additional Repairs Required

**P0 Violations:** 1 (addressed above)
**P1 Violations:** 0
**P2 Violations:** 0
**P3 Violations:** 0

All other infrastructure surfaces are properly wired according to the ownership matrix.

---

## Post-Repair Verification Checklist

### Code Verification
- [ ] Direct ChromaDB import removed
- [ ] SovereignChromaClient import added
- [ ] Client instantiation updated
- [ ] Method calls updated to adapter interface
- [ ] No syntax errors
- [ ] No import errors

### Test Verification
- [ ] Unit tests pass (`pytest tests/unit/apps_rfp/`)
- [ ] Integration tests pass (`pytest tests/integration/apps_rfp/`)
- [ ] No test failures introduced
- [ ] Proposal retrieval functionality verified

### ADG Verification
- [ ] ADG regenerated successfully
- [ ] New edge path verified: `apps_rfp → L4_chroma_client → chromadb`
- [ ] Old direct edge removed
- [ ] No new violations introduced

### Compliance Verification
- [ ] Violation detection scan passes
- [ ] apps_rfp no longer flagged for direct ChromaDB import
- [ ] Overall compliance score updated to 100%

---

## Uncertainties and Assumptions

### Uncertainties
1. **Current Code Pattern:** Exact current implementation unknown without file read
2. **Test Coverage:** Unknown if tests exist for proposal_retrieval_engine.py
3. **API Compatibility:** Unknown if adapter provides all required methods
4. **Dependencies:** Unknown if other parts of apps_rfp depend on direct ChromaDB usage

### Assumptions
1. **Single File:** Violation contained to single file (proposal_retrieval_engine.py)
2. **Adapter Completeness:** SovereignChromaClient provides all required functionality
3. **Test Availability:** Tests exist and will pass after fix
4. **No Side Effects:** Fix will not break other parts of apps_rfp

---

## Next Steps

1. **Execute Repair #001:** Fix apps_rfp direct ChromaDB import
2. **Verify Fix:** Run verification checklist
3. **Phase 5:** Design CI ratchet and scorecard to prevent regression
4. **Final Report:** Summarize wave completion and compliance improvement
