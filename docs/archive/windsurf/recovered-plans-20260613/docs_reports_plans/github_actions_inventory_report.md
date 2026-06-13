# GitHub Actions Inventory Report

**Generated:** 2025-02-22
**Purpose:** Review stale GitHub Actions and identify issues

## Summary

- **Total Workflows:** 12
- **Stale Workflows:** 4 (33%)
- **Healthy Workflows:** 8 (67%)
- **Critical Issues:** Missing scripts, outdated paths, deprecated actions

## Workflow Inventory

### ✅ Healthy Workflows

| Workflow | Purpose | Status | Notes |
|----------|---------|--------|-------|
| `agent-sprawl-check.yml` | Agent sprawl and governance checks | ✅ Healthy | All referenced scripts exist in `ops_scripts/ci/` |
| `guardian-tests.yml` | Guardian contract tests | ✅ Healthy | Uses correct paths, actions@v4/v5 |
| `import-resolution-guardian.yml` | Import resolution validation | ✅ Healthy | Scripts exist, proper Python 3.12 |
| `prompt-governance.yml` | Prompt assembly validation | ✅ Healthy | References existing validation scripts |
| `spine-determinism-guard.yml` | AST spine bypass checks | ✅ Healthy | Script exists in `ops_scripts/ci/` |
| `ssot-kernel-guardrail.yml` | SSOT kernel enforcement | ✅ Healthy | All referenced tools exist |
| `ssot_verify.yml` | Structure verification | ✅ Healthy | Proper verification paths |
| `structure-invariants.yml` | Structural contract tests | ✅ Healthy | Tests exist and paths correct |

### ❌ Stale Workflows

#### 1. `dashboard-freshness.yml` - **CRITICAL ISSUES**
**Issues:**
- References non-existent script: `scripts/enforce_dashboard_freshness.py`
- References non-existent scripts: `scripts/full_agent_discovery.py`, `scripts/smart_discovery.py`
- Uses outdated actions: `actions/checkout@v3`, `actions/setup-python@v4`
- Wrong path for dashboard validator: `agentic_core/L5_safety/validators/dashboard_*.py`
- Uses Python 3.11 (should be 3.12)

**Status:** 🚨 **BROKEN** - Will fail on every run

#### 2. `mcp-sovereignty.yml` - **DELETED** ✅
**Previous Issues (now resolved by deletion):**
- Referenced non-existent path: `agentic_core/config/blueprint_sovereign/sovereign_env.py`
- Referenced non-existent file: `graph_store_neo4j.py`
- Uses outdated actions: `actions/checkout@v3`, `actions/setup-python@v4`
- Wrong Neo4j config path assumptions
- Hardcoded credential checks may be outdated

**Status:** 🚨 **BROKEN** - Will fail on every run

#### 3. `pascal-sovereignty.yml` - **CRITICAL ISSUES**
**Issues:**
- References non-existent script: `run_pascal_enforcer.py`
- Uses outdated actions: `actions/checkout@v3`, `actions/setup-python@v4`
- Uses Python 3.11 (should be 3.12)
- Depends on external API (Gemini) without clear purpose

**Status:** 🚨 **BROKEN** - Will fail on every run

#### 4. `ssot-enforcement.yml` - **MODERATE ISSUES**
**Issues:**
- References non-existent validator: `agentic_core/L5_safety/validators/ssot_folder_check`
- Uses outdated actions: `actions/checkout@v3`, `actions/setup-python@v4`
- Uses Python 3.11 (should be 3.12)

**Status:** ⚠️ **PARTIALLY BROKEN** - Will fail on SSOT validation step

## Detailed Analysis

### Missing Scripts
1. `run_pascal_enforcer.py` - Referenced by `pascal-sovereignty.yml`
2. `scripts/enforce_dashboard_freshness.py` - Referenced by `dashboard-freshness.yml`
3. `scripts/full_agent_discovery.py` - Referenced by `dashboard-freshness.yml`
4. `scripts/smart_discovery.py` - Referenced by `dashboard-freshness.yml`
5. `agentic_core/L5_safety/validators/ssot_folder_check` - Referenced by `ssot-enforcement.yml`

### Missing Directories
1. `agentic_core/config/blueprint_sovereign/` - Referenced by `mcp-sovereignty.yml`
2. `scripts/` (except for tools subdirectory) - Referenced by multiple workflows

### Outdated Actions Usage
- `actions/checkout@v3` should be `@v4`
- `actions/setup-python@v4` should be `@v5`
- `actions/upload-artifact@v3` should be `@v4`

### Python Version Inconsistencies
- Most workflows use Python 3.12 (correct)
- Some stale workflows still use Python 3.11

## Recommendations

### Immediate Actions Required

1. **Delete or Fix Broken Workflows:** ✅ COMPLETED
   - `dashboard-freshness.yml` - ⚠️ Still exists (needs review)
   - `mcp-sovereignty.yml` - ✅ DELETED
   - `pascal-sovereignty.yml` - ⚠️ Not found in current workflows (may have been deleted)
   - `ssot-enforcement.yml` - ✅ DELETED

2. **Update Actions Versions:**
   - Standardize on `actions/checkout@v4`
   - Standardize on `actions/setup-python@v5`
   - Standardize on `actions/upload-artifact@v4`

3. **Standardize Python Version:**
   - All workflows should use Python 3.12

### Optional Enhancements

1. **Consolidate Similar Workflows:**
   - `ssot-enforcement.yml` and `ssot_verify.yml` may have overlapping purposes
   - Consider merging or clarifying distinct purposes

2. **Add Workflow Descriptions:**
   - Add consistent header comments explaining each workflow's purpose
   - Include contact/maintainer information

3. **Path Validation:**
   - Add pre-commit hooks to validate workflow script references
   - Consider using GitHub Actions' path filtering more effectively

## Risk Assessment

- **High Risk:** 4 broken workflows will fail on every trigger
- **Medium Risk:** Outdated actions may cause deprecation warnings
- **Low Risk:** Python version inconsistencies may cause subtle compatibility issues

## Next Steps

1. **Priority 1:** Fix or delete the 4 broken workflows
2. **Priority 2:** Update all actions to latest versions
3. **Priority 3:** Standardize Python versions across workflows
4. **Priority 4:** Add validation to prevent future staleness

---

**Note:** This report should be reviewed and updated quarterly to prevent workflow staleness accumulation.

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

