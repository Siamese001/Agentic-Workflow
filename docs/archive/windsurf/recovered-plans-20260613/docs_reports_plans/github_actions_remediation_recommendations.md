# GitHub Actions Remediation Recommendations

**⚠️ STATUS: COMPLETED** - The workflows referenced in this document have been deleted.

**Generated:** 2025-02-22
**Purpose:** Specific remediation actions for each stale workflow

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Priority Matrix

| Workflow | Impact | Effort | Priority | Action |
|----------|--------|--------|----------|--------|
| `dashboard-freshness.yml` | High | High | P1 | DELETE |
| `mcp-sovereignty.yml` | High | High | P1 | DELETE |
| `pascal-sovereignty.yml` | Low | Medium | P3 | DELETE |
| `ssot-enforcement.yml` | Medium | Low | P2 | FIX |

---

## 1. `dashboard-freshness.yml` - **DELETE**

**Recommendation: DELETE ENTIRELY**

**Rationale:**
- References 4 non-existent scripts
- Dashboard validation logic appears obsolete
- `scripts/` directory is essentially empty (only `tools/` subdirectory)
- Dashboard freshness checking is likely handled elsewhere

**Action:**
```bash
git rm .github/workflows/dashboard-freshness.yml
```

**Alternative (if dashboard validation is still needed):**
Complete rewrite required:
- Move validation logic to `ops_scripts/ci/`
- Update all script references
- Fix dashboard validator paths
- Update to actions@v4/v5 and Python 3.12

---

## 2. `mcp-sovereignty.yml` - **DELETE**

**Recommendation: DELETE ENTIRELY**

**Rationale:**
- References non-existent `blueprint_sovereign` directory
- Neo4j configuration paths are wrong
- MCP hardening appears to be handled by other workflows
- Credential scanning is redundant with other security checks

**Action:**
```bash
git rm .github/workflows/mcp-sovereignty.yml
```

**Alternative (if MCP sovereignty is still needed):**
- Update Neo4j config paths to actual locations
- Fix `blueprint_sovereign` directory references
- Update credential scanning logic
- Modernize actions and Python version

---

## 3. `pascal-sovereignty.yml` - **DELETE**

**Recommendation: DELETE ENTIRELY**

**Rationale:**
- `run_pascal_enforcer.py` script doesn't exist
- PascalCase enforcement appears abandoned
- External API dependency (Gemini) adds complexity
- No evidence of ongoing PascalCase compliance needs

**Action:**
```bash
git rm .github/workflows/pascal-sovereignty.yml
```

**Alternative (if PascalCase enforcement is desired):**
- Create or locate `run_pascal_enforcer.py`
- Update actions and Python version
- Remove external API dependency
- Clarify enforcement scope

---

## 4. `ssot-enforcement.yml` - **FIX**

**Recommendation: REPAIR AND KEEP**

**Rationale:**
- SSOT enforcement is still relevant
- Only missing one validator script
- Low effort to fix
- Complements other SSOT workflows

**Required Changes:**

### 4.1 Update Actions Versions
```yaml
- uses: actions/checkout@v4  # was v3
- uses: actions/setup-python@v5  # was v4
  with:
    python-version: '3.12'  # was 3.11
```

### 4.2 Fix Validator Reference
Current (broken):
```yaml
python -m agentic_core.L5_safety.validators.ssot_folder_check
```

Find actual validator or replace with:
```yaml
python -m agentic_core.L5_safety.config.structure_blueprint._verify
```

### 4.3 Alternative: Consolidate with `ssot_verify.yml`
Consider merging functionality since both verify SSOT compliance.

---

## Implementation Plan

### Phase 1: Immediate Cleanup (Day 1)
```bash
# Delete broken workflows
git rm .github/workflows/dashboard-freshness.yml
git rm .github/workflows/mcp-sovereignty.yml
git rm .github/workflows/pascal-sovereignty.yml
git commit -m "ci: remove 3 broken GitHub Actions workflows"
```

### Phase 2: Fix SSOT Enforcement (Day 1-2)
1. Update `ssot-enforcement.yml` with correct validator path
2. Update actions to v4/v5
3. Update Python to 3.12
4. Test workflow on feature branch

### Phase 3: Validation (Day 2)
1. Run all workflows in test environment
2. Verify no remaining broken references
3. Update documentation

---

## Risk Assessment

### Deleting Workflows - LOW RISK
- These workflows are already broken and failing
- No active CI/CD depends on them
- Removal improves CI health

### Fixing SSOT Enforcement - LOW RISK
- Simple path correction
- No logic changes required
- Backup workflow (`ssot_verify.yml`) provides redundancy

---

## Post-Remediation State

**Expected Result:**
- **Total Workflows:** 9 (down from 12)
- **Healthy Workflows:** 9 (up from 8)
- **Broken Workflows:** 0 (down from 4)
- **CI Health:** 100%

**Benefits:**
- Faster CI execution (fewer workflows)
- Cleaner maintenance surface
- No more false-negative failures
- Consistent actions/Python versions

---

## Long-term Prevention

1. **Add workflow validation to pre-commit**
2. **Quarterly workflow review process**
3. **Automated script existence checks**
4. **Standardize workflow templates**

---

**Next Step:** Execute Phase 1 cleanup immediately to restore CI health.

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

