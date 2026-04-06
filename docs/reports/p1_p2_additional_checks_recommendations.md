# Additional P1-P2 ADG Checks - Best Practices Recommendations

**Date:** 2026-04-06  
**Purpose:** Identify additional P1-P2 severity areas in ADG that should be checked beyond the documented table

**Status:** ✅ AGREED - Stricter thresholds applied

## Executive Summary

Based on analysis of `tools/generate/generate_full_adg.py`, several critical ADG validation checks exist beyond the documented P1-P2 table. This document categorizes these checks by severity and provides best practice recommendations for enforcement.

## Current ADG Fail-Fast Checks

### P1 (CRITICAL) - Currently Blocking (8 checks)

| Check | Function | What It Validates | Current Behavior | Recommendation |
|-------|----------|-------------------|------------------|----------------|
| **Artifact Validity** | `_check_artifact_validity()` | Missing, zero-byte, or invalid artifacts (snapshot, SQLite) | ✅ Blocks ADG generation | ✅ Correct - keep as P1 |
| **SQLite Integrity** | `_check_sqlite_integrity()` | Database integrity, required tables (nodes, edges, violations, meta) | ✅ Blocks ADG generation | ✅ Correct - keep as P1 |
| **Artifact Consistency** | `_check_artifact_consistency()` | Count mismatch between JSON graphs and SQLite | ✅ Blocks ADG generation | ✅ Correct - keep as P1 |
| **P1 Defects** | `_check_p1_defects()` | Critical layer violations in routing summary | ✅ Blocks in strict mode | ✅ Correct - keep as P1 |
| **Closure Validation** | Closure validation (strict mode) | Runtime enforcement gaps (Gaps 1-5) | ✅ Blocks in strict mode (except allowlisted) | ✅ Correct - keep as P1 |
| **Locked Files** | `_check_locked_files()` | SQLite files locked by MCP server | ✅ Blocks ADG generation | ✅ Correct - keep as P1 |
| **Zip Creation** | Zip creation failure | ADG archival compression | ✅ Blocks ADG generation | ✅ Correct - keep as P1 |
| **Syntax Errors** | Python syntax validation | Syntax errors in Python files | ✅ Blocks ADG generation | ✅ Correct - keep as P1 |

### P2 (HIGH) - Currently Non-Blocking (4 checks)

| Check | Function | What It Validates | Current Behavior | Recommendation |
|-------|----------|-------------------|------------------|----------------|
| **MCP Config Drift** | `_check_mcp_config_drift()` | Drift between YAML SSOT and global MCP config | ⚠️ WARNING only, does not block | ⚠️ Should be P1 in pre-commit (see recommendation) |
| **Critical Edge Coverage** | Edge report generation | Coverage of critical edge types | 📊 Monitoring only | ⚠️ Should have P2 threshold enforcement |
| **Critical Path Linkage** | Boundary report generation | Unresolved import paths | 📊 Monitoring only | ⚠️ Should have P2 threshold enforcement |
| **High Criticality Ownership** | E8 ownership tracking | Modules with high criticality ownership | 📊 Monitoring only | ℹ️ Keep as informational (P3) |

## Detailed Analysis

### 1. Artifact Validity Check (P1) ✅

**Location:** `generate_full_adg.py:165-214`

**Validates:**
- Required artifacts exist (snapshot.json, adg_indexed.sqlite)
- Artifacts are not zero-byte
- SQLite database is queryable
- JSON files are valid JSON

**Current Severity:** P1 (CRITICAL) - Blocks ADG generation

**Best Practice Assessment:** ✅ CORRECT
- Missing or corrupted artifacts indicate partial/failed generation
- Must block to prevent downstream tools from using invalid ADG
- Aligns with CI/CD best practices for artifact validation

**No changes recommended.**

---

### 2. SQLite Integrity Check (P1) ✅

**Location:** `generate_full_adg.py:217-249`

**Validates:**
- SQLite PRAGMA integrity_check passes
- Required tables exist: nodes, edges, violations, meta

**Current Severity:** P1 (CRITICAL) - Blocks ADG generation

**Best Practice Assessment:** ✅ CORRECT
- Database corruption indicates filesystem or process failure
- Missing tables indicate schema migration failure
- Must block to prevent query failures in downstream tools

**No changes recommended.**

---

### 3. Artifact Consistency Check (P1) ✅

**Location:** `generate_full_adg.py:252-290`

**Validates:**
- JSON graph entity count matches SQLite node count
- JSON graph relation count matches SQLite edge count

**Current Severity:** P1 (CRITICAL) - Blocks ADG generation

**Best Practice Assessment:** ✅ CORRECT
- Count mismatch indicates serialization/deserialization failure
- Indicates data loss or corruption during generation
- Must block to ensure ADG query consistency

**No changes recommended.**

---

### 4. Closure Validation Gaps (P1) ✅

**Location:** `generate_full_adg.py:641-666`

**Validates:**
- Gap 1: UWG mutation chokepoint (UniversalWriteGateway.py)
- Gap 2: Determinism/replay interception (replay_guard.py)
- Gap 3: Policy hash validation (policy_hash_enforcer.py)
- Gap 4: HITL/DPO lineage (hitl_dpo_pair_generator.py)
- Gap 5: Meta-learning commit gating (meta_apply.py)

**Current Severity:** P1 (CRITICAL) - Blocks in strict mode
- Allowlist: EDGE SEMANTIC PRECISION, DETERMINISM (ARTIFACT LEVEL)
- Other gaps block ADG generation in strict mode

**Best Practice Assessment:** ✅ CORRECT
- Runtime enforcement gaps are constitutional violations
- These gaps bypass critical safety mechanisms
- Allowlist is justified for known technical debt

**Recommendation:** ✅ Keep as P1 with current allowlist
- Consider reducing allowlist as technical debt is resolved
- Document why each allowlisted gap is acceptable

---

### 5. Locked Files Detection (P1) ✅

**Location:** `generate_full_adg.py:2418-2442`

**Validates:**
- SQLite files locked by MCP server process
- Prevents archive cleanup failures

**Current Severity:** P1 (CRITICAL) - Blocks ADG generation

**Best Practice Assessment:** ✅ CORRECT
- Locked files indicate MCP server connection leak
- Prevents proper ADG archival and cleanup
- User must restart Windsurf to release locks

**No changes recommended.**

---

### 6. MCP Config Drift Check (P2 → P1) ⚠️

**Location:** `generate_full_adg.py:2363-2393`

**Validates:**
- Enabled server count in `config/mcp_servers.yaml` matches global MCP config
- Detects drift between SSOT and actual configuration

**Current Severity:** WARNING only - Does not block

**Best Practice Assessment:** ⚠️ SHOULD BE P1
- MCP config drift is a constitutional violation (Rule #0)
- Pre-commit hook T11 already checks this as P1
- ADG check should align with pre-commit severity

**Recommendation:** ⚠️ Upgrade to P1 in ADG generation
- Change from WARNING to ERROR in strict mode
- Align with pre-commit T11 (MCP Config Sovereignty)
- Blocks ADG generation if drift detected

**Implementation:**
```python
def _check_mcp_config_drift(strict_mode: bool = False) -> None:
    # ... existing code ...
    if yaml_count != global_count:
        print("[ERROR] MCP config drift detected!")
        print(f"[ERROR]   YAML enabled servers: {yaml_count}")
        print(f"[ERROR]   Global enabled servers: {global_count}")
        if strict_mode:
            print("[ERROR] MCP config drift is a constitutional violation (Rule #0)")
            print("[ERROR] Run: python tools/adg/sync_yaml_to_global.py")
            print("[ERROR] ADG generation failed - fix MCP config drift")
            sys.exit(1)
        else:
            print("[WARNING] Proceeding with ADG generation...")
```

---

### 7. Critical Edge Coverage (P2) ⚠️

**Location:** `generate_full_adg.py:1811-1828`

**Validates:**
- Coverage of critical edge types in ADG
- Critical edges: controls_flow, flows_to, emits_side_effect, reads_from, writes_to

**Current Severity:** Monitoring only - No blocking

**Best Practice Assessment:** ⚠️ SHOULD HAVE P2 THRESHOLDS
- Critical edges represent core system interactions
- Zero coverage indicates incomplete ADG extraction
- Should warn if coverage drops below threshold

**Recommendation:** ⚠️ Add P1/P2 threshold enforcement
- Set minimum threshold (e.g., 95% coverage required)
- Block as P1 if below 95% in strict mode
- Warn if below 95% in non-strict mode

**Implementation:**
```python
def _check_critical_edge_coverage(edge_report: dict, strict_mode: bool = False) -> None:
    critical_coverage = edge_report["critical_edge_coverage"]
    total_critical_edges = len(critical_coverage)
    covered_edges = sum(1 for count in critical_coverage.values() if count > 0)
    coverage_ratio = covered_edges / total_critical_edges if total_critical_edges > 0 else 0
    
    MIN_COVERAGE_THRESHOLD = 0.95  # 95%
    
    if coverage_ratio < MIN_COVERAGE_THRESHOLD:
        print(f"[WARNING] Critical edge coverage: {coverage_ratio:.1%} (threshold: {MIN_COVERAGE_THRESHOLD:.1%})")
        if strict_mode:
            print("[ERROR] Critical edge coverage below threshold - P1 DEFECT")
            print("[ERROR] ADG generation failed - incomplete critical edge extraction")
            sys.exit(1)
```

---

### 8. Critical Path Linkage (P2) ⚠️

**Location:** `generate_full_adg.py:1971-2024`

**Validates:**
- Unresolved import paths in ADG
- Critical path completeness

**Current Severity:** Monitoring only - No blocking

**Best Practice Assessment:** ⚠️ SHOULD HAVE P1/P2 THRESHOLDS
- Unresolved paths indicate incomplete dependency tracking
- High unresolved count affects ADG query accuracy
- Should warn if unresolved count exceeds 5%
- Should block as P1 if unresolved count exceeds 5%

**Recommendation:** ⚠️ Add P1/P2 threshold enforcement
- Set maximum threshold (e.g., 5% unresolved acceptable)
- Block as P1 if above 5% in strict mode
- Warn if above 5% in non-strict mode

**Implementation:**
```python
def _check_critical_path_linkage(boundary_report: dict, strict_mode: bool = False) -> None:
    critical_path_unresolved = boundary_report.get("critical_path_unresolved", 0)
    total_entities = boundary_report.get("total_entities", 1)
    unresolved_ratio = critical_path_unresolved / total_entities
    
    MAX_UNRESOLVED_THRESHOLD = 0.05  # 5%
    
    if unresolved_ratio > MAX_UNRESOLVED_THRESHOLD:
        print(f"[WARNING] Unresolved path ratio: {unresolved_ratio:.1%} (threshold: {MAX_UNRESOLVED_THRESHOLD:.1%})")
        if strict_mode:
            print("[ERROR] Unresolved path count above threshold - P1 DEFECT")
            print("[ERROR] ADG generation failed - incomplete dependency tracking")
            sys.exit(1)
```

---

### 9. High Criticality Ownership (P3) ℹ️

**Location:** `generate_full_adg.py:569-575`

**Validates:**
- Modules with high criticality ownership (E8)
- Ownership tracking for architectural governance

**Current Severity:** Monitoring only

**Best Practice Assessment:** ℹ️ KEEP AS INFORMATIONAL (P3)
- Ownership tracking is for architectural governance
- Does not indicate immediate system failure
- Should be informational for review

**No changes recommended.**

---

## Summary of Recommendations

### Immediate Actions (P1)

1. ✅ **No changes needed** for existing P1 checks (artifact validity, SQLite integrity, artifact consistency, P1 defects, closure validation, locked files, zip creation, syntax errors)
2. ⚠️ **Upgrade MCP config drift to P1** in ADG generation to align with pre-commit T11

### Medium Priority (P1/P2)

3. ⚠️ **Add threshold enforcement for critical edge coverage** - < 95% block as P1, >= 95% warn
4. ⚠️ **Add threshold enforcement for critical path linkage** - > 5% block as P1, <= 5% warn

### Low Priority (P3)

5. ℹ️ **Keep high criticality ownership as informational** - No blocking needed

## Best Practices Rationale

### Why MCP Config Drift Should Be P1

- **Constitutional Violation:** Rule #0 requires MCP config sovereignty
- **Precedent:** Pre-commit T11 already enforces this as P1
- **Impact:** Drift causes tooling misalignment and potential security risks
- **Industry Standard:** Configuration drift is a critical CI/CD failure mode

### Why Critical Edge Coverage Needs Thresholds

- **System Completeness:** Critical edges represent core system interactions
- **Query Accuracy:** Missing edges affect all downstream ADG queries
- **Regression Detection:** Thresholds detect extraction failures early
- **Industry Standard:** Code coverage thresholds are standard practice

### Why Critical Path Linkage Needs Thresholds

- **Dependency Accuracy:** Unresolved paths indicate incomplete tracking
- **Impact Analysis:** Affects blast radius calculations
- **Tooling Reliability:** High unresolved count reduces ADG utility
- **Industry Standard:** Import analysis tools enforce completeness thresholds

## Updated P1-P2 Enforcement Matrix

### P1 (CRITICAL) - Additional Checks

| Check | Function | Pre-Commit Equivalent | Current State | Recommended State |
|-------|----------|----------------------|---------------|-------------------|
| Artifact Validity | `_check_artifact_validity()` | N/A (ADG-internal) | ✅ P1 | ✅ P1 (no change) |
| SQLite Integrity | `_check_sqlite_integrity()` | N/A (ADG-internal) | ✅ P1 | ✅ P1 (no change) |
| Artifact Consistency | `_check_artifact_consistency()` | N/A (ADG-internal) | ✅ P1 | ✅ P1 (no change) |
| MCP Config Drift | `_check_mcp_config_drift()` | T11 (P1) | ⚠️ WARNING | ⚠️ Upgrade to P1 |
| Locked Files | `_check_locked_files()` | N/A (ADG-internal) | ✅ P1 | ✅ P1 (no change) |

### P2 (HIGH) → P1 - Additional Checks with Stricter Thresholds

| Check | Function | Current State | Recommended State | Threshold |
|-------|----------|---------------|-------------------|-----------|
| Critical Edge Coverage | Edge report generation | 📊 Monitoring | ⚠️ < 95% block as P1, >= 95% warn | 95% coverage threshold |
| Critical Path Linkage | Boundary report generation | 📊 Monitoring | ⚠️ > 5% block as P1, <= 5% warn | 5% unresolved threshold |

## Implementation Priority

1. **High Priority:** Upgrade MCP config drift to P1 (aligns with existing pre-commit)
2. **High Priority:** Add critical edge coverage thresholds - < 95% block as P1 (improves ADG quality)
3. **High Priority:** Add critical path linkage thresholds - > 5% block as P1 (improves ADG accuracy)

---

## User Agreement Summary

The following recommendations were agreed by the user:

1. ✅ **Agreed** - Upgrade MCP config drift to P1 in ADG generation
2. ✅ **Agreed with stricter threshold** - Critical edge coverage: < 95% block as P1, >= 95% warn
3. ✅ **Agreed with stricter threshold** - Critical path linkage: > 5% block as P1, <= 5% warn
4. ✅ **Agreed** - Keep high criticality ownership as P3 (informational)
