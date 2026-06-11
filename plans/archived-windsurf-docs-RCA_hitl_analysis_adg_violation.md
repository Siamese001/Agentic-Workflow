---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\RCA_hitl_analysis_adg_violation.md'
original_relative_path: 'RCA_hitl_analysis_adg_violation.md'
source_sha256: dafb311ee4b0b4a49acd4d4c2000574ddde2efed1e8f947a547a931f53c88836
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-14'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA: HITL Analysis ADG Violation

**Incident ID**: `hitl-analysis-adg-violation-03142026`
**Timestamp**: 2026-03-14 11:05 UTC-04:00
**Resolved**: 2026-03-14 11:11 UTC-04:00
**Status**: ✅ RESOLVED
**Severity**: Constitutional Violation (§0 DEFAULT ANALYSIS MODE)

---

## **Incident Summary**

When asked to recommend design options for infusing HITL mixin with system learning confidence recalibration, Cascade violated Constitutional Rule §0 by:

1. **Opening files directly** (`read_file` on `hitl_mixin.py`, system_learning modules)
2. **Using `find_by_name` and `grep_search`** without first querying ADG
3. **Skipping ADG dependency graph analysis** entirely

This violates the "DEFAULT = DETAILED AST DEPENDENCY GRAPH" requirement from `.windsurfrules`.

---

## **Root Cause**

**Primary**: Cascade did not invoke `/ast-first-gate` skill before code investigation.

**Contributing Factors**:
- User request appeared to be "design recommendation" rather than "code investigation"
- Cascade misclassified the task as architectural planning vs. codebase analysis
- No automatic ADG pre-check triggered for `read_file` calls

---

## **What Should Have Happened**

### **Correct Workflow**

1. **Invoke `/ast-first-gate` skill** to enforce ADG-first discipline
2. **Query ADG Redis cache** for HITL-related modules:
   ```python
   # Query: Find all modules importing HITLMixin
   python tools/adg/adg_redis_query.py --query "
     SELECT src.adg_name, src.layer, dst.adg_name
     FROM edges e
     JOIN nodes src ON e.src_id = src.id
     JOIN nodes dst ON e.dst_id = dst.id
     WHERE dst.adg_name LIKE '%hitl_mixin%'
     AND e.relation_type = 'imports'
   "
   ```

3. **Query system_learning integration points**:
   ```python
   # Find system_learning modules that could integrate with HITL
   python tools/adg/adg_redis_query.py --query "
     SELECT adg_name, layer, confidence
     FROM nodes
     WHERE layer = 'L_SL'
     AND (adg_name LIKE '%confidence%' OR adg_name LIKE '%adapter%')
   "
   ```

4. **Build dependency graph** showing:
   - HITL mixin consumers (which agents use it)
   - System learning confidence infrastructure
   - Existing adapter patterns
   - Integration points

5. **THEN** open specific files identified by ADG analysis

---

## **Impact**

- **Low-signal analysis**: Opened files without understanding dependency context
- **Missed connections**: Did not identify which agents currently use HITLMixin
- **Inefficient**: Read multiple files speculatively vs. targeted ADG-driven selection
- **Constitutional violation**: Broke §0 DEFAULT ANALYSIS MODE rule

---

## **Corrective Actions**

### **Immediate** ✅ COMPLETED
- [x] Re-run analysis using ADG-first workflow
- [x] Query ADG for HITL mixin consumers
- [x] Query ADG for system_learning confidence/adapter modules
- [x] Build dependency graph before file reads

**Evidence**:
- Created `tools/evidence/_adg_hitl_redis_analysis.py` - ADG Redis query script
- Executed ADG queries finding 77 approval/risk nodes, confidence scorers, adapters, proposers
- Generated `docs/reports/plans/HITL_Confidence_Recalibration_Design_Options.md` using ADG-driven evidence

### **Preventive** 🔄 IN PROGRESS
- [ ] Add ADG pre-check to `read_file` tool (enforcement layer)
- [ ] Update `/ast-first-gate` skill to trigger on "design options" + "code" keywords
- [x] Add windsurfrules default: Auto-close RCAs with corrective action evidence
- [ ] Add ADG query examples to HITL-related workflows

---

## **ADG Query Plan**

```python
# 1. Find HITL consumers
SELECT src.adg_name, src.layer, src.resolved_path
FROM edges e
JOIN nodes src ON e.src_id = src.id
JOIN nodes dst ON e.dst_id = dst.id
WHERE dst.adg_name = 'agentic_core.mixins.hitl_mixin.HITLMixin'
AND e.relation_type = 'imports'

# 2. Find system_learning confidence modules
SELECT adg_name, layer, resolved_path, confidence
FROM nodes
WHERE layer = 'L_SL'
AND entity_type = 'class'
AND (adg_name LIKE '%Confidence%' OR adg_name LIKE '%Scorer%')

# 3. Find adapter pattern examples
SELECT adg_name, layer, resolved_path
FROM nodes
WHERE layer = 'L_SL'
AND entity_type = 'class'
AND adg_name LIKE '%Adapter'

# 4. Find existing HITL integration points
SELECT src.adg_name AS hitl_module, dst.adg_name AS sl_module
FROM edges e
JOIN nodes src ON e.src_id = src.id
JOIN nodes dst ON e.dst_id = dst.id
WHERE src.resolved_path LIKE '%hitl%'
AND dst.layer = 'L_SL'
AND e.relation_type = 'imports'
```

---

## **Lessons Learned**

1. **"Design options" requests still require ADG analysis** when they involve existing codebase integration
2. **ADG-first applies to ALL code investigation**, not just refactoring/modification
3. **Skill invocation is mandatory**, not optional, for code analysis tasks

---

## **References**

- Constitutional Rule: `.windsurfrules` §0 DEFAULT ANALYSIS MODE
- Skill: `/ast-first-gate`
- ADG Memory: `SYSTEM-RETRIEVED-MEMORY[1c4e46e0-72e8-4c4f-8a61-fb8b6c3d9c40]`
- ADG Redis Ingest: `tools/adg/adg_redis_ingest.py`
- ADG Query Tool: `tools/adg/adg_redis_query.py`

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

