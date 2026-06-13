# RCA: Wave Table and Token Estimates Validation Failure

**Date:** 2026-03-27  
**Severity:** HIGH — 100% failure rate across 855 plans  
**Status:** 🔍 INVESTIGATION — Root cause identified  

---

## Violation

CI plan validation reports **854/855 plans invalid** due to missing wave structure tables and token estimates, violating `.windsurfrules §10.1` and `§10.2`.

**Key metrics from latest CI run:**
- Total Plans: 855
- Valid Plans: 1 (0.1%)
- Invalid Plans: 854 (99.9%)
- Plans with Warnings: 620

**Primary failure modes:**
1. Missing `## Wave Structure` section (680+ plans)
2. Wave table not found after section (650+ plans)
3. Missing token estimates in table (600+ plans)
4. Encoding errors preventing validation (50+ plans)

---

## Root Cause Analysis

### Proximate Causes

**1. Legacy Plans Pre-Date Standards**
- Majority of plans created before §10 standards existed
- No retroactive validation applied until recent CI gate
- Plans follow various historical formats (RCA, gap analysis, implementation notes)

**2. No Migration Path for Legacy Plans**
- CI validation enabled without bulk migration strategy
- No automated tool to add wave tables to existing plans
- Manual remediation impractical at scale (850+ plans)

**3. Encoding Issues Blocking Validation**
- 50+ plans have UTF-8 encoding errors (0x90, 0x8f bytes)
- `charmap` codec failures prevent validation script from reading files
- Likely from copy-paste from Windows editors or binary contamination

### Systemic Causes

**1. CI Gate Deployed Without Remediation**
- `ci_validate_plans.py` deployed in strict mode before legacy plan remediation
- No grace period or phased rollout for existing content
- Immediate 100% failure rate expected and occurred

**2. Validation Script Too Rigid**
- `validate_plan_format.py` requires exact section names and table format
- No accommodation for plan types that don't need waves (e.g., RCA reports)
- Binary pass/fail with no partial compliance recognition

**3. No Plan Type Differentiation**
- All `.md` files in `docs/reports/plans/` treated as "execution plans"
- RCAs, gap analyses, and investigation reports don't need wave tables
- One-size-fits-all validation inappropriate for diverse document types

---

## Evidence

### CI Validation Report Excerpt
```
### docs\reports\plans\accelerators_top5_evidence.md
- Missing required section: ## Wave Structure
- Missing required section: ## Rules
- Missing required section: ## Success Criteria
- Wave table not found after '## Wave Structure' section
```

### Encoding Failures
```
### .windsurf\plans\adg-violation-waterfall-hardened-c64079.md
- Error reading plan: 'charmap' codec can't decode byte 0x90 in position 6461
```

### Validation Pattern in `tools/validate_plan_format.py`
```python
REQUIRED_SECTIONS = [
    "## Wave Structure",
    "## Rules", 
    "## Success Criteria"
]
```

---

## Corrective Actions

### Immediate (T0)

**1. Categorize Plans by Type**
```bash
# Classify all plans
python tools/categorize_plans.py --output artifacts/plan_classification.json
```

**Expected categories:**
- Execution Plans (need wave table) ~200
- RCA Reports (no waves needed) ~300
- Gap Analyses (no waves needed) ~200
- Investigation Reports (no waves needed) ~150

**2. Fix Encoding Issues**
```bash
# Repair UTF-8 encoding errors
python tools/fix_plan_encoding.py --dry-run
python tools/fix_plan_encoding.py --execute
```

**3. Update Validation Script**
- Modify `validate_plan_format.py` to skip wave requirements for non-execution plans
- Add plan type detection based on filename patterns
- Implement graduated validation (strict for new, lenient for legacy)

### Short-term (T1)

**4. Bulk Migration for Execution Plans**
```bash
# Add wave tables to execution plans only
python tools/add_wave_tables_to_legacy_plans.py --type execution --dry-run
python tools/add_wave_tables_to_legacy_plans.py --type execution --execute
```

**5. Grandfather Clause Implementation**
- Add creation date check to validation
- Plans created before 2026-03-01 exempt from wave requirements
- New plans (post-standard) subject to strict validation

### Long-term (T2)

**6. Plan Type Registry**
```yaml
# .windsurf/config/plan_types.yaml
execution:
  requires_wave_table: true
  requires_token_estimates: true
  required_sections: ["## Wave Structure", "## Rules", "## Success Criteria"]
  
rca:
  requires_wave_table: false
  requires_token_estimates: false
  required_sections: ["## Violation", "## Root Cause", "## Corrective Actions"]
```

**7. Smart Validation**
- Detect plan type from content and filename
- Apply type-appropriate validation rules
- Provide specific guidance per plan type

---

## Implementation Commands

```bash
# Phase 1: Triage and categorize
python tools/categorize_plans.py
python tools/fix_plan_encoding.py --execute

# Phase 2: Update validation logic
git checkout -b fix/plan-validation-types
# Edit tools/validate_plan_format.py
# Edit .windsurf/rules/.windsurfrules §10.4

# Phase 3: Bulk migrate execution plans
python tools/add_wave_tables_to_legacy_plans.py --type execution --dry-run
python tools/add_wave_tables_to_legacy_plans.py --type execution --execute

# Phase 4: Verify
python tools/ci_validate_plans.py --report-only
```

---

## Success Criteria

- [ ] Encoding errors fixed (0 decode failures)
- [ ] Plan categorization complete (100% classified)
- [ ] Validation updated with type awareness
- [ ] Execution plans have wave tables (100% compliance)
- [ ] Non-execution plans exempt from wave requirements
- [ ] CI validation pass rate ≥ 95%
- [ ] New plan template includes wave table by default

---

## Rollback Strategy

If validation changes cause issues:
1. Revert `tools/validate_plan_format.py` to previous version
2. Disable CI plan validation gate temporarily
3. Restore from backup: `artifacts/ci/plan_validation_report_pre_fix.md`
4. Re-deploy with phased approach

---

## Status

🔍 **IN PROGRESS** — Investigation complete, remediation in progress  
⚠️ **IMMEDIATE ACTION REQUIRED** — 854 plans failing CI validation  
✅ **ROOT CAINE IDENTIFIED** — Legacy plans + rigid validation + no migration path
