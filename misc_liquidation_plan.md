# Misc Liquidation: Zero-Misc Distribution Plan

**Scan Date:** 2026-02-05T09:58:01.735864
**Target Directory:** `docs/reports/misc/`
**Total Files:** 231

---

## Executive Summary

**Classified:** 227 files (98.3%)
**Unclassified:** 4 files (1.7%)

---

## Distribution Plan

### audit/ (✅ EXISTING)

**File Count:** 86

**Top Signals:**
- `keyword:ssot` (46 files)
- `keyword:violation` (38 files)
- `keyword:compliance` (34 files)
- `keyword:audit` (29 files)
- `keyword:integrity` (13 files)

**Sample Files:**
- `agent_discovery_trigger_model.md` (confidence: 6)
- `agent_integrity_audit.md` (confidence: 10)
- `AI_CHECKING_AI_FORENSIC_AUDIT_REPORT.md` (confidence: 6)
- `APP_FILE_RELOCATION_PLAN_FINAL.md` (confidence: 4)
- `ARCHITECTURAL_REVIEW_REGENERATED.md` (confidence: 4)
- ... and 81 more

### assessments/ (✅ EXISTING)

**File Count:** 67

**Top Signals:**
- `keyword:analysis` (58 files)
- `keyword:architecture` (28 files)
- `keyword:recommendation` (16 files)
- `keyword:assessment` (9 files)
- `keyword:gap` (8 files)

**Sample Files:**
- `ACTUAL_STRUCTURE_ALIGNMENT_ANALYSIS.md` (confidence: 4)
- `AGENTIC_CORE_STREAMLINING_RECOMMENDATIONS.md` (confidence: 4)
- `ALL_RECOMMENDATIONS_IMPLEMENTATION_COMPLETE.md` (confidence: 4)
- `APPS_RG_INTEGRATION_ASSESSMENT.md` (confidence: 6)
- `APPS_RG_LIC_MIRRORED_STRUCTURE_RECOMMENDATIONS.md` (confidence: 4)
- ... and 62 more

### legacy/ (🆕 NEW CATEGORY)

**File Count:** 27

**Top Signals:**
- `keyword:phase` (17 files)
- `keyword:legacy` (15 files)
- `keyword:old` (10 files)
- `keyword:archived` (6 files)
- `keyword:deprecated` (5 files)

**Sample Files:**
- `AGENT_DEPRECATION_ANALYSIS_REPORT.md` (confidence: 6)
- `agent_disposition_analysis.json` (confidence: 3)
- `ARCHIVE_APPROVAL_RCA_REPORT.md` (confidence: 4)
- `ARCHIVE_RESTORATION_PLAN.md` (confidence: 4)
- `CORE_EVICTION_DISPOSITION_REPORT.md` (confidence: 5)
- ... and 22 more

### coverage/ (✅ EXISTING)

**File Count:** 23

**Top Signals:**
- `keyword:test` (23 files)
- `keyword:coverage` (9 files)
- `header:## Test Results` (3 files)
- `keyword:quality` (3 files)

**Sample Files:**
- `BOUNDARY_STRESS_TEST_FINDINGS.md` (confidence: 5)
- `CACHE_CLEANUP_SYSTEM.md` (confidence: 2)
- `CONVERGENCE_LOOP_TEST_REPORT.md` (confidence: 4)
- `DASHBOARD_OUTLIER_DETECTION_PLAN.md` (confidence: 6)
- `DASHBOARD_TESTING.md` (confidence: 4)
- ... and 18 more

### missions/ (✅ EXISTING)

**File Count:** 8

**Top Signals:**
- `keyword:runtime` (6 files)
- `keyword:mission` (6 files)
- `keyword:execution` (3 files)
- `header:# Mission` (2 files)

**Sample Files:**
- `DASHBOARD_META_LEARNING_GUIDE.md` (confidence: 4)
- `phase10_l1_cognition_scaling_report.md` (confidence: 5)
- `phase9_autonomous_evolution_report.md` (confidence: 5)
- `runtime_state_guard_implementation.md` (confidence: 2)
- `SOVEREIGN_HARDENING_V2_FINAL_SUMMARY.md` (confidence: 6)
- ... and 3 more

### security/ (✅ EXISTING)

**File Count:** 7

**Top Signals:**
- `keyword:safety` (6 files)
- `keyword:guardrails` (3 files)
- `keyword:security` (3 files)
- `keyword:hardened` (3 files)
- `header:# Security` (1 files)

**Sample Files:**
- `AGENT_CONSOLIDATION_COMPLETION_REPORT.md` (confidence: 4)
- `AGENT_OVERLAP_ANALYSIS_REPORT.md` (confidence: 4)
- `COGNITION_HEALTH_ANALYSIS.md` (confidence: 4)
- `HARDENED_CORE_REFINERY_REPORT.md` (confidence: 7)
- `HARDENED_ULTRA_FILE_DIFF.md` (confidence: 6)
- ... and 2 more

### telemetry/ (✅ EXISTING)

**File Count:** 6

**Top Signals:**
- `keyword:observability` (4 files)
- `keyword:metrics` (3 files)
- `keyword:dashboard` (2 files)
- `keyword:performance` (1 files)
- `header:## Performance` (1 files)

**Sample Files:**
- `BROKEN_IMPORTS_SAMPLE.md` (confidence: 2)
- `DASHBOARD_QA_CHECKLIST.md` (confidence: 2)
- `legacy_artifacts_optimization_report.md` (confidence: 5)
- `mcp_integration_sovereignty_2026.md` (confidence: 4)
- `territory_classification.md` (confidence: 4)
- ... and 1 more

### governance/ (🆕 NEW CATEGORY)

**File Count:** 3

**Top Signals:**
- `keyword:registry` (3 files)
- `keyword:mapping` (2 files)
- `keyword:governance` (1 files)
- `keyword:manifest` (1 files)

**Sample Files:**
- `CORE_HYGIENE_AGENTS_IMPLEMENTATION_REPORT.md` (confidence: 4)
- `DATA_DOCS_STRUCTURE_PROPOSAL.md` (confidence: 6)
- `STRUCTURE_BLUEPRINT_HARDENING_V2_SUMMARY.md` (confidence: 4)

### ⚠️ Unclassified Files

**File Count:** 4

**Recommendation:** Manual review or create `docs/reports/misc_archive/` for truly uncategorizable files

**Sample Files:**
- `DUAL_GATE_CONFLICT_REMEDIATION_REPORT.md`
- `FILE_CLASSIFICATION_MIGRATION_GUIDE.md`
- `FORWARD_ROLLING_RECURSION_FIXES_SUMMARY.md`
- `PRECOMMIT_RCA_FIX_SUMMARY.md`

---

## Proposed Actions

### Existing Categories (Move to existing L4 folders)

- **audit/**: 86 files → `docs/reports/audit/`
- **assessments/**: 67 files → `docs/reports/assessments/`
- **coverage/**: 23 files → `docs/reports/coverage/`
- **telemetry/**: 6 files → `docs/reports/telemetry/`
- **security/**: 7 files → `docs/reports/security/`
- **missions/**: 8 files → `docs/reports/missions/`

### New Categories (Create new L4 folders)

- **legacy/**: 27 files → `docs/reports/legacy/` (NEW)
- **governance/**: 3 files → `docs/reports/governance/` (NEW)

---

## Constitutional Amendment Required

If new categories are approved, update `structure_blueprint_config.py`:

```python
"docs": {
    "subfolders": {
        "reports": {
            "subfolders": {
                "assessments": {...},
                "audit": {...},
                "coverage": {...},
                "security": {...},
                "telemetry": {...},
                "missions": {...},
                "legacy": {"purpose": "Deprecated artifacts and documentation"},
                "governance": {"purpose": "Governance artifacts and documentation"},
            }
        }
    }
}
```

---

## ⚠️ DECISION GATE: AWAITING APPROVAL

Review the distribution plan above before proceeding to execution.
