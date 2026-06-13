# RCA: HITL Missing Recommendation in ask_user_question

**Date**: 2026-03-14
**Status**: ✅ RESOLVED
**Severity**: LOW
**Category**: Process Violation - HITL Output Format

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


## Violation Summary

Used `ask_user_question` tool for HITL decision but failed to include explicit recommendation, violating `.windsurfrules §8.5.3` requirement for HITL option presentation format.

**Constitutional Rule Violated**:
> §8.5.3: Every HITL prompt MUST include:
> - **Context**: Brief description of decision point ✅
> - **Options**: 2-4 concrete alternatives labeled A, B, C, D ✅
> - **Trade-offs**: Honest pros/cons or impact for each ✅
> - **Recommendation**: Which option you suggest and why ❌ MISSING

---

## Root Cause Analysis

### What Happened

1. Created proper HITL decision point for Wave 4 Phase 2
2. Used `ask_user_question` tool with clickable buttons ✅
3. Provided 4 options (A, B, C, D) with descriptions ✅
4. **Failed to include explicit recommendation** ❌

### Why It Happened

**Immediate Cause**: Focused on fixing the "clickable buttons" requirement but overlooked the "recommendation" requirement from §8.5.3.

**Contributing Factors**:
1. **Partial Fix**: Corrected one HITL violation (markdown vs buttons) but introduced another (missing recommendation)
2. **Tool Limitation**: `ask_user_question` tool doesn't have a dedicated "recommendation" parameter
3. **Format Confusion**: Unclear how to present recommendation within tool constraints

---

## Corrective Actions

### Immediate Fix

The `ask_user_question` tool should include recommendation in the question text or as a separate note. Testing proper format:

**Test Case**: Re-present Wave 4 Phase 2 decision with explicit recommendation included in question parameter.

### Implementation

Will add recommendation to the question text like:
```
"Wave 4 Phase 2: How should we implement EvalGuard?

Current state: 185 files with invokes_eval edges
Phase 1 result: 105 credential guards across 63 files

**RECOMMENDED: Option A (Full EvalGuard)**
Rationale: Complete coverage, consistent with Phase 1 success, eliminates entire risk category"
```

---

## Resolution

**Status**: ✅ RESOLVED (2026-03-14 13:54 UTC-04:00)

**Corrective Action Taken**:
Re-presented HITL decision with proper format including:
- ✅ Context in question text
- ✅ 4 options (A, B, C, D) with clickable buttons
- ✅ Trade-offs in option descriptions
- ✅ **Explicit recommendation** (Option A) with rationale in question text
- ✅ Star emoji (⭐) marking recommended option

**User Selection**: Option A - Full EvalGuard Migration

**Evidence**:
- Proper HITL format used in `ask_user_question` tool call
- User successfully selected Option A via clickable button
- Recommendation clearly stated in question parameter

**Lesson Learned**: When using `ask_user_question` tool, include recommendation in the question text itself since the tool doesn't have a dedicated recommendation parameter. Mark recommended option with visual indicator (⭐) in label.

**Next Action**: Proceed with Option A implementation (Full EvalGuard migration)
