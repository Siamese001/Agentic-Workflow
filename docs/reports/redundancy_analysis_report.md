# Redundancy Analysis: generate_full_adg.py vs .pre-commit-config.yaml

**Date:** 2026-04-06  
**Purpose:** Identify any redundancy between `generate_full_adg.py` and `.pre-commit-config.yaml`

## generate_full_adg.py Internal Checks

### Validation Functions
1. **_check_artifact_validity()** - Validates ADG artifact structure
2. **_check_sqlite_integrity()** - Checks SQLite database integrity
3. **_check_artifact_consistency()** - Validates consistency across artifacts
4. **_check_p1_defects()** - Checks for P1 critical defects (layer violations)
5. **_check_mcp_config_drift()** - Checks MCP config drift
6. **_perform_wal_checkpoint()** - Performs WAL checkpoint on SQLite
7. **_check_locked_files()** - Checks for locked SQLite files

### ADG Structural Checks
- **P1 Defects:** Critical layer violations and repair routes
- **P2-P4 Defects:** High/medium/low severity issues
- **Layer Violations:** Boundary violations in the ADG
- **Burndown Tracking:** Anti-pattern count ratchet
- **Semantic Warnings:** P4-level semantic issues
- **Closure Validation:** Gaps in closure validation

### Output Generation
- SQLite database (ADG indexed)
- JSON snapshot
- File graph
- Symbol graph
- Governance graph
- Zip archive
- Reports

## .pre-commit-config.yaml Hook Checks

### T0: Admission/Guards
- Agent deletion authorization
- Trailing whitespace
- End-of-file fixer
- Line endings (LF)
- Merge conflict markers

### T1: Syntax
- Python syntax validation

### T2: Linting
- Ruff CRITICAL (security)
- Ruff HIGH (bug patterns)
- Ruff MEDIUM (style)
- Ruff LOW (formatting/Python3)

### T3: Formatting
- Ruff format

### T4: Guardian Comments
- Guardian comment auto-fix

### T6: AST Semantics
- Hollow file gate (AST semantic verification)

### T7: SSOT Paths
- Report location SSOT check
- Plan location SSOT gate

### T7.7: Governance
- Windsurf governance health check

### T8: Artifacts
- Reject tracked generated artifacts

### T9: Boundary
- Tooling/apps boundary guard

### T10: Architectural
- Module collision guard

### T10.6: ADG Unified Gate
- File change detection (agentic_core/, tools/generate/, tools/adg/, config/)
- Conditional ADG generation (via generate_full_adg.py --strict)
- Python grep ban
- YAML grep ban
- Skip-file ratchet

### T11: Config
- MCP config sovereignty
- Pytest config SSOT

### T12: Governance
- Guardian exemption quality ratchet

### T21: Summary
- Pre-commit governance summary report

## Redundancy Analysis

### Potential Overlaps

#### 1. MCP Config Checks
- **generate_full_adg.py:** `_check_mcp_config_drift()` - Checks MCP config drift
- **.pre-commit-config.yaml:** T11 - MCP config sovereignty, T11.2 - MCP config drift detection (commented out)

**Analysis:** ⚠️ **POTENTIAL REDUNDANCY**
- `generate_full_adg.py` includes MCP config drift check
- `.pre-commit-config.yaml` has T11.2 commented out (script not implemented)
- **Recommendation:** Decide which should handle MCP config drift check
  - Option A: Keep in generate_full_adg.py (runs during ADG generation)
  - Option B: Implement in pre-commit (runs on every commit)
  - Option C: Both (pre-commit for fast feedback, ADG for comprehensive check)

#### 2. Artifact Validation
- **generate_full_adg.py:** `_check_artifact_validity()`, `_check_artifact_consistency()`
- **.pre-commit-config.yaml:** T8 - Reject tracked generated artifacts

**Analysis:** ✅ **NO REDUNDANCY**
- `generate_full_adg.py` validates ADG artifact structure and consistency
- T8 prevents tracking generated artifacts in git
- Different purposes: internal validation vs. git hygiene

#### 3. File Lock Checks
- **generate_full_adg.py:** `_check_locked_files()` - Checks for locked SQLite files
- **.pre-commit-config.yaml:** No equivalent

**Analysis:** ✅ **NO REDUNDANCY**
- This is an internal ADG generation check to prevent SQLite corruption
- No equivalent in pre-commit (not needed)

#### 4. P1 Defects
- **generate_full_adg.py:** `_check_p1_defects()` - Checks for P1 critical defects
- **.pre-commit-config.yaml:** T10.6 calls generate_full_adg.py --strict (includes P1 check)

**Analysis:** ✅ **NO REDUNDANCY**
- T10.6 delegates to generate_full_adg.py
- Clear delegation, not duplication

#### 5. Layer Violations
- **generate_full_adg.py:** Includes layer violation detection
- **.pre-commit-config.yaml:** T10.6 calls generate_full_adg.py --strict (includes layer violations)

**Analysis:** ✅ **NO REDUNDANCY**
- T10.6 delegates to generate_full_adg.py
- Clear delegation, not duplication

#### 6. Burndown Tracking
- **generate_full_adg.py:** Includes burndown tracking
- **.pre-commit-config.yaml:** T10.6 calls generate_full_adg.py --strict (includes burndown)

**Analysis:** ✅ **NO REDUNDANCY**
- T10.6 delegates to generate_full_adg.py
- Clear delegation, not duplication

## Summary

### Redundancy Score: ✅ MINIMAL REDUNDANCY

**Confirmed Redundancy:**
- ⚠️ **MCP Config Drift:** Both generate_full_adg.py and .pre-commit-config.yaml (T11.2 commented out) include MCP config drift checks

**No Redundancy:**
- ✅ Artifact validation (internal vs. git hygiene)
- ✅ File lock checks (internal ADG only)
- ✅ P1 defects (delegated via T10.6)
- ✅ Layer violations (delegated via T10.6)
- ✅ Burndown tracking (delegated via T10.6)
- ✅ All other checks (distinct purposes)

### Recommendations

1. **Resolve MCP Config Drift Redundancy:**
   - Decide where MCP config drift should be checked
   - Implement T11.2 script if moving to pre-commit
   - Remove from generate_full_adg.py if moving to pre-commit
   - Or keep both with clear documentation of purpose

2. **Document Delegation:**
   - Clearly document that T10.6 delegates to generate_full_adg.py
   - Ensure team understands this relationship

3. **Consider Separation:**
   - If MCP config drift is needed for every commit, implement in pre-commit
   - If MCP config drift is only needed for ADG generation, keep in generate_full_adg.py

## Conclusion

**Overall Assessment: ✅ MINIMAL REDUNDANCY**

The redundancy between `generate_full_adg.py` and `.pre-commit-config.yaml` is minimal. The only potential overlap is MCP config drift checking, which is currently commented out in the pre-commit config. All other checks are either:
1. Delegated from pre-commit to generate_full_adg.py (T10.6)
2. Distinct purposes (internal validation vs. git hygiene)
3. Unique to one system (no equivalent in the other)

The architecture is well-designed with clear separation of concerns.
