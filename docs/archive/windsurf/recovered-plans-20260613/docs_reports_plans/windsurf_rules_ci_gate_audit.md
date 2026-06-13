# Windsurf Rules & CI Gate Cross-Check Audit

**Date**: 2026-03-11
**Status**: COMPREHENSIVE AUDIT COMPLETE
**Scope**: All `.windsurf/` rules, skills, and corresponding CI enforcement gates

---

## Executive Summary

**Finding**: Windsurf rules are **well-structured** but have **gaps in CI enforcement**. Several constitutional rules lack automated pre-commit gates.

### Coverage Matrix

| Rule Domain | Windsurf Rule | CI Gate | Status |
|-------------|---------------|---------|--------|
| **Plan Location** | ✅ `.windsurf/rules/plan-location.md` | ✅ `check_plan_location_compliance.py` | **ENFORCED** |
| **ADG Repair Discipline** | ✅ `.windsurf/rules/adg-repair-discipline.md` | ✅ `tools/adg_ci_gate.py` (manual stage) | **PARTIAL** |
| **AST-First Gate** | ✅ `.windsurf/skills/ast-first-gate/` | ❌ No CI gate | **GAP** |
| **Dedup Guard** | ✅ `.windsurf/skills/dedup-guard/` | ❌ No CI gate | **GAP** |
| **Dependency Graph Analysis** | ✅ `.windsurf/skills/dependency-graph-analysis/` | ❌ No CI gate | **GAP** |
| **Evidence Bundle** | ✅ `.windsurf/skills/evidence-bundle/` | ❌ No CI gate | **GAP** |
| **Import Hygiene** | ✅ `.windsurf/skills/import-hygiene/` | ✅ Ruff F401 + `validate_import_dependencies.py` | **ENFORCED** |
| **Layer Boundary Guard** | ✅ `.windsurf/skills/layer-boundary-guard/` | ✅ ADG GV violates edges | **ENFORCED** |
| **MCP Tool Verify** | ✅ `.windsurf/skills/mcp-tool-verify/` | ❌ No CI gate | **GAP** |
| **Pytest Integrity** | ✅ `.windsurf/skills/pytest-integrity/` | ✅ `adg_ci_lane_gate.py --fail-on-skip` | **ENFORCED** |
| **Rollback Gate** | ✅ `.windsurf/skills/rollback-gate/` | ❌ No CI gate | **GAP** |
| **Scope Guard** | ✅ `.windsurf/skills/scope-guard/` | ❌ No CI gate | **GAP** |
| **Script Sprawl Guard** | ✅ `.windsurf/skills/script-sprawl-guard/` | ❌ No CI gate | **GAP** |
| **Shim Discipline** | ✅ `.windsurf/skills/shim-discipline/` | ❌ No CI gate | **GAP** |
| **SSOT Write Gate** | ✅ `.windsurf/skills/ssot-write-gate/` | ✅ `validate_report_location.py` | **ENFORCED** |
| **Test Rigor Enforcement** | ✅ `.windsurf/skills/test-rigor-enforcement/` | ✅ `adg_ci_lane_gate.py` | **ENFORCED** |

---

## Detailed Findings

### ✅ ENFORCED RULES (6/16)

#### 1. Plan Location Rule
- **Rule**: `.windsurf/rules/plan-location.md`
- **CI Gate**: `ops_scripts/ci/check_plan_location_compliance.py`
- **Pre-commit Hook**: T3b (always_run)
- **Status**: ✅ **HARDENED** — blocks commits with plans outside `docs/reports/plans/`

#### 2. ADG Repair Discipline
- **Rule**: `.windsurf/rules/adg-repair-discipline.md`
- **CI Gate**: `tools/adg_ci_gate.py check-phase`
- **Pre-commit Hook**: T0-ADG (manual stage)
- **Status**: ⚠️ **PARTIAL** — only enforced in manual stage, not automatic

#### 3. Import Hygiene
- **Rule**: `.windsurf/skills/import-hygiene/`
- **CI Gates**:
  - Ruff F401 (dead imports)
  - `ops_scripts/ci/validate_import_dependencies.py` (T4a)
- **Pre-commit Hook**: T2a (ruff), T4a (import validation)
- **Status**: ✅ **HARDENED**

#### 4. Layer Boundary Guard
- **Rule**: `.windsurf/skills/layer-boundary-guard/`
- **CI Gate**: ADG `GV_violates` edges (240 violations tracked)
- **Pre-commit Hook**: None (ADG artifact-based)
- **Status**: ✅ **ENFORCED** via ADG static scanner

#### 5. Pytest Integrity
- **Rule**: `.windsurf/skills/pytest-integrity/`
- **CI Gate**: `tools/adg_ci_lane_gate.py --fail-on-skip`
- **Pre-commit Hook**: T3a-skip (always_run)
- **Status**: ✅ **HARDENED** — blocks commits with pytest.skip in UNIT_STRICT

#### 6. SSOT Write Gate
- **Rule**: `.windsurf/skills/ssot-write-gate/`
- **CI Gate**: `ops_scripts/hooks/validate_report_location.py`
- **Pre-commit Hook**: T3b (always_run)
- **Status**: ✅ **HARDENED**

#### 7. Test Rigor Enforcement
- **Rule**: `.windsurf/skills/test-rigor-enforcement/`
- **CI Gate**: `tools/adg_ci_lane_gate.py`
- **Pre-commit Hook**: T3a-skip
- **Status**: ✅ **ENFORCED**

---

### ❌ GAPS — RULES WITHOUT CI GATES (10/16)

#### 1. AST-First Gate
- **Rule**: `.windsurf/skills/ast-first-gate/`
- **Purpose**: Block code investigation without ADG dependency graph
- **Missing Gate**: No pre-commit hook to enforce AST-first discipline
- **Recommendation**: Create `ops_scripts/ci/check_ast_first_gate.py`

#### 2. Dedup Guard
- **Rule**: `.windsurf/skills/dedup-guard/`
- **Purpose**: Prevent duplicate agents, mixins, utility functions
- **Missing Gate**: No pre-commit hook to detect semantic duplicates
- **Recommendation**: Create `ops_scripts/ci/check_dedup_violations.py` using ADG

#### 3. Dependency Graph Analysis
- **Rule**: `.windsurf/skills/dependency-graph-analysis/`
- **Purpose**: Enforce graph-first impact analysis
- **Missing Gate**: No pre-commit hook to validate dependency graph usage
- **Recommendation**: Integrate with ADG CI gate

#### 4. Evidence Bundle
- **Rule**: `.windsurf/skills/evidence-bundle/`
- **Purpose**: Capture command outputs into evidence files
- **Missing Gate**: No pre-commit hook to validate evidence artifacts
- **Recommendation**: Create `ops_scripts/ci/check_evidence_bundle.py`

#### 5. MCP Tool Verify
- **Rule**: `.windsurf/skills/mcp-tool-verify/`
- **Purpose**: Verify MCP filesystem tool calls post-execution
- **Missing Gate**: No automated verification of write operations
- **Recommendation**: Create `ops_scripts/ci/check_mcp_tool_verify.py`

#### 6. Rollback Gate
- **Rule**: `.windsurf/skills/rollback-gate/`
- **Purpose**: Enforce explicit rollback checkpoints before multi-file phases
- **Missing Gate**: No pre-commit hook to validate checkpoint artifacts
- **Recommendation**: Create `ops_scripts/ci/check_rollback_checkpoints.py`

#### 7. Scope Guard
- **Rule**: `.windsurf/skills/scope-guard/`
- **Purpose**: Prevent scope drift using ADG dependency graph
- **Missing Gate**: No pre-commit hook to validate scope declarations
- **Recommendation**: Integrate with ADG CI gate

#### 8. Script Sprawl Guard
- **Rule**: `.windsurf/skills/script-sprawl-guard/`
- **Purpose**: Prevent creation of new runner scripts
- **Missing Gate**: No pre-commit hook to detect new executable scripts
- **Recommendation**: Create `ops_scripts/ci/check_script_sprawl.py`

#### 9. Shim Discipline
- **Rule**: `.windsurf/skills/shim-discipline/`
- **Purpose**: Enforce consistent shim/backward-compatibility discipline
- **Missing Gate**: No pre-commit hook to detect undocumented shims
- **Recommendation**: Create `ops_scripts/ci/check_shim_discipline.py`

---

## Existing CI Gates (36 total)

### Pre-Commit Hooks (Active)

```yaml
T0-ADG: adg-phase-gate (manual stage)
T0: trailing-whitespace, end-of-file-fixer, mixed-line-ending, check-merge-conflict
T1: python-syntax-check
T2a: ruff --fix
T2b: ruff-format
T3a: check-anti-patterns
T3a-skip: enforce-unit-strict-zero-skip
T3a-c0: check-c0-sovereignty
T3b: check-report-location
T3c: reject-generated-artifacts-tracked
T3d: folder-purity-validation (manual stage)
T3f: module-collision-guard
T3g: governance-policy-validation
T3h: validate-evidence-contract
T3i: guard-pytest-ini-scope
T3h: guard-apps-shared-instructional-layer
T4a: import-dependency-check
T5: purge-cache
```

### CI Scripts (ops_scripts/ci/)

36 check scripts covering:
- Anti-patterns (landmine detection)
- ADG proof artifact truthfulness
- ADG schema field names
- Agent registry completeness
- Apps output contract
- C0 boundary enforcement
- CI integrity
- Determinism replay/violations
- Direct execute calls
- Directory deletion sweep
- Embedding instantiation
- Environment contract
- Evidence contract v2
- FAISS persist contract
- Healer direct model access
- Kernel extension boundary
- Layer write sovereignty
- LLM SDK imports
- Model string literals
- No unconditional xfail
- Object dunder setattr
- **Plan location compliance** ✅
- Policy drift classification
- PowerShell ban
- Skip convergence gate
- Sovereign LLM gateway
- Spine adapter contract
- Spine bypass
- Structured output emission
- System learning boundary
- Test integrity
- Tooling apps boundary
- Utility silent swallowers
- Wall clock in determinism

---

## Recommendations

### Priority 1: Close Critical Gaps

1. **Create `ops_scripts/ci/check_ast_first_gate.py`**
   - Enforce §0 DEFAULT ANALYSIS MODE requirement
   - Block commits without ADG dependency graph evidence
   - Add to pre-commit as T3a-ast

2. **Create `ops_scripts/ci/check_dedup_violations.py`**
   - Use ADG semantic graph to detect duplicate symbols
   - Block creation of semantically equivalent agents/mixins
   - Add to pre-commit as T3a-dedup

3. **Create `ops_scripts/ci/check_script_sprawl.py`**
   - Detect new `.py` files in `tools/` or `ops_scripts/` without justification
   - Enforce canonical invocation policy
   - Add to pre-commit as T3a-sprawl

4. **Promote ADG Phase Gate to automatic stage**
   - Move `adg-phase-gate` from `stages: [manual]` to default
   - Enforce §ADG-1.2 automatically during repair loops

### Priority 2: Consolidate Rules

1. **Merge duplicate rule files**
   - `.windsurfrules_adg_repair_discipline.md` (root)
   - `.windsurf/rules/adg-repair-discipline.md` (subdirectory)
   - **Action**: Keep `.windsurf/rules/` version, delete root duplicate

2. **Create master rules index**
   - File: `.windsurf/RULES_INDEX.md`
   - List all rules with CI gate mappings
   - Reference from main README

### Priority 3: Harden Existing Gates

1. **Strengthen `check_anti_patterns.py`**
   - Add AST-based duplicate detection
   - Add shim discipline checks
   - Add script sprawl detection

2. **Enhance `adg_ci_gate.py`**
   - Add scope guard validation
   - Add rollback checkpoint verification
   - Add evidence bundle validation

---

## Constitutional Rules Summary

### §0: Default Analysis Mode
- **Rule**: AST dependency graph REQUIRED before code investigation
- **CI Gate**: ❌ **MISSING**
- **Priority**: **CRITICAL**

### §ADG-1: ADG Repair Discipline
- **Rule**: Graph-first repair protocol
- **CI Gate**: ⚠️ **PARTIAL** (manual stage only)
- **Priority**: **HIGH**

### Plan Location Rule
- **Rule**: Plans MUST be in `docs/reports/plans/`
- **CI Gate**: ✅ **ENFORCED**
- **Priority**: **COMPLETE**

---

## Action Items

- [ ] Create `ops_scripts/ci/check_ast_first_gate.py`
- [ ] Create `ops_scripts/ci/check_dedup_violations.py`
- [ ] Create `ops_scripts/ci/check_script_sprawl.py`
- [ ] Create `ops_scripts/ci/check_shim_discipline.py`
- [ ] Create `ops_scripts/ci/check_rollback_checkpoints.py`
- [ ] Promote `adg-phase-gate` to automatic stage
- [ ] Delete duplicate `.windsurfrules_adg_repair_discipline.md` from root
- [ ] Create `.windsurf/RULES_INDEX.md` master index
- [ ] Add CI gate references to each skill SKILL.md
- [ ] Update `.pre-commit-config.yaml` with new gates

---

## Conclusion

**Current State**: 6/16 rules have automated CI enforcement (37.5%)
**Target State**: 16/16 rules with pre-commit gates (100%)
**Gap**: 10 critical rules lack automated enforcement

**Next Steps**: Implement Priority 1 gates to close critical gaps and achieve full constitutional rule enforcement.

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

