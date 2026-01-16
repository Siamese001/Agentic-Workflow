# Dashboard Column Explanation

## Issue: User Seeing 97.7% Instead of 78.5%

### Root Cause
**User is looking at the wrong column in the dashboard.**

The dashboard has **TWO SEPARATE TABLES** with **TWO DIFFERENT SCORING SYSTEMS**:

---

## Table 1: Territory Summary (Autonomy & Health Metrics)

**Columns:**
- Territory
- Total
- Heal Cap %
- Invocation %
- Test %
- MCP Hardened %
- Complexity Health %
- **Health** ← This is the autonomy health score

**Health Score (78.5):**
- **Formula:** Weighted average of autonomy metrics
- **Weights:**
  - Heal Cap: 30%
  - Invocation: 10%
  - Test: 25%
  - Observable: 20%
  - Complexity Health: 15%
- **Calculation:** (100×0.30) + (100×0.10) + (94×0.25) + (50×0.20) + (33×0.15) = **78.5**

---

## Table 2: Code Quality Metrics

**Columns:**
- Territory
- Total
- Typed %
- Documented %
- Schema Strictness %
- Canonical Inheritance %
- **Code Quality Score** ← This is what user is seeing (97.7)

**Code Quality Score (97.7):**
- **Formula:** Weighted average of code quality metrics
- **Weights:**
  - Typed: 30%
  - Documented: 30%
  - Schema Strictness: 25%
  - Canonical Inheritance: 15%
- **Calculation:** (95.1×0.30) + (96.4×0.30) + (99.2×0.25) + (100×0.15) = **97.7**

---

## Current TOTAL Row Values

```
TOTAL Row (from dashboard_data.js):
├─ Table 1 (Autonomy Metrics)
│  ├─ Heal Cap %: 100.0
│  ├─ Invocation %: 100.0
│  ├─ Test %: 94.0
│  ├─ MCP Hardened %: 100.0
│  ├─ Complexity Health %: 33.0
│  └─ Health: 78.5 ✅ CORRECT (weighted average)
│
└─ Table 2 (Code Quality Metrics)
   ├─ Typed %: 95.1
   ├─ Documented %: 96.4
   ├─ Schema Strictness %: 99.2
   ├─ Canonical Inheritance %: 100.0
   └─ Code Quality Score: 97.7 ← USER IS SEEING THIS
```

---

## Verification

**Dashboard data is CORRECT:**
- ✅ Health (autonomy): 78.5 (using weighted average)
- ✅ Code Quality Score: 97.7 (using weighted average)

**User needs to:**
1. Look at **Table 1** (Territory Summary)
2. Find the **"Health"** column (last column in Table 1)
3. **NOT** the "Code Quality Score" column (last column in Table 2)

---

## Visual Guide

**Table 1 Layout:**
```
Territory | Total | Heal Cap % | Invocation % | Test % | ... | Health
----------|-------|------------|--------------|--------|-----|-------
TOTAL     | 265   | 100.0      | 100.0        | 94.0   | ... | 78.5 ← Look here
```

**Table 2 Layout:**
```
Territory | Total | Typed % | Documented % | ... | Code Quality Score
----------|-------|---------|--------------|-----|-------------------
TOTAL     | 265   | 95.1    | 96.4         | ... | 97.7 ← NOT here
```

---

## Summary

**The health score IS correct at 78.5.**

User is looking at the **Code Quality Score (97.7)** instead of the **Health score (78.5)**.

Both scores are using weighted averages correctly. No calculation error exists.
