---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\severity-ssot-migration-a1b2c3.md'
original_relative_path: 'severity-ssot-migration-a1b2c3.md'
source_sha256: bfb706bb0f72d977a265fa660b4b705f1d43415ea7a5a9eb0fa00c0799ce06b2
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Severity SSOT Migration Plan

**Created:** 2026-04-06
**Status:** MIGRATION COMPLETE
**Impact:** HIGH - Affects ADG, pre-commit, validation, and test enforcement systems

## Problem Statement

Multiple incompatible severity systems exist across the codebase:

| System | Location | Case | Values |
|--------|----------|------|--------|
| ADG Query Contracts | `agentic_core/adg/contracts/query_contracts.py` | lowercase | info, low, medium, high, critical |
| Pre-Commit Schema | `ops_scripts/ci/pre_commit_issue_schema.py` | UPPERCASE | CRITICAL, HIGH, MEDIUM, LOW, INFO |
| Validation Config | `agentic_core/runtime/config/validation_severity_config.py` | lowercase | info, warning, error, critical |
| Test Enforcement | `tools/test_enforcement/` | UPPERCASE | HIGH, MEDIUM, LOW |
| Ruff Linting | `.pre-commit-config.yaml` | P0-P3 | P0 (critical), P1 (high), P2 (medium), P3 (low) |

## Solution

**SSOT Location:** `agentic_core/L5_safety/config/severity.py`

### Canonical Severity Definitions

| Level | P-Level | Impact | Urgency | Blocks Commit? | Examples |
|-------|---------|--------|---------|----------------|----------|
| CRITICAL | P0/P1 | System-breaking, security, constitutional violation | Immediate | YES | Layer violations, PowerShell usage, security bugs |
| HIGH | P1/P2 | Bugs, architectural violations, anti-patterns | High | YES | Unused imports, global mutations, test coverage gaps |
| MEDIUM | P2/P3 | Code quality, maintainability | Medium | NO | Long functions, complexity, missing docstrings |
| LOW | P3/P4 | Minor style, formatting | Low | NO | Line length, trailing whitespace, debug prints |
| INFO | N/A | No issue | N/A | NO | Hook passed, hook skipped |

### Semantic Criteria

**CRITICAL (P0/P1) - Blocks Commit**
- Constitutional violations (PowerShell usage, agent deletion without auth)
- Security vulnerabilities (SQL injection, path traversal, credential leaks)
- Layer boundary violations that break architectural invariants
- Broken imports in production code
- Missing critical dependencies
- Data loss or corruption risks

**HIGH (P1/P2) - Should Fix Before Commit**
- Bug patterns (unused imports, dead code, unreachable code)
- Architectural violations (wrong-layer imports, circular dependencies)
- Anti-patterns (global mutations, silent exception swallowers)
- Test coverage gaps in critical paths
- Deprecated API usage
- Performance anti-patterns

**MEDIUM (P2/P3) - Consider Fixing**
- Code quality issues (long functions, high cyclomatic complexity)
- Maintainability concerns (inconsistent naming, missing docstrings)
- Technical debt indicators (TODO comments without owners, FIXME comments)
- Minor architectural violations (non-critical boundary crossings)
- Inconsistent error handling patterns

**LOW (P3/P4) - Informational**
- Style violations (line length, trailing whitespace)
- Formatting issues (inconsistent spacing)
- Minor linter warnings (unused variables in tests)
- Debug statements (print statements in non-production code)
- Missing type hints in utility code

## Migration Strategy

### Phase 1: Update SSOT Consumers (Low Risk) ✅ COMPLETE

**1.1 Pre-Commit Schema** ✅
- File: `ops_scripts/ci/pre_commit_issue_schema.py`
- Change: Import from SSOT, use alias for backward compat
- Status: DONE - Imports work correctly

**1.2 ADG Query Contracts** ✅
- File: `agentic_core/adg/contracts/query_contracts.py`
- Change: Import from SSOT, alias as FindingSeverity
- Status: DONE - Imports work correctly

**1.3 Validation Config** ✅
- File: `agentic_core/runtime/config/validation_severity_config.py`
- Change: Import from SSOT, map legacy values via from_legacy_string()
- Status: DONE - Imports work correctly, legacy WARNING→MEDIUM, ERROR→HIGH mapping works

### Phase 2: Update Database Queries (Medium Risk) ✅ COMPLETE

**2.1 ADG P1 Defect Gate** ✅
- File: `ops_scripts/ci/adg_p1_defect_gate.py`
- Change: Use SSOT for severity comparison
- Status: DONE - Uses `SeverityLevel.CRITICAL.value` in SQL query

**2.2 ADG Layer Violation Gate** ✅
- File: `ops_scripts/ci/adg_layer_violation_gate.py`
- Change: Import SSOT for documentation
- Status: DONE - Imports SeverityLevel, documents as CRITICAL

**2.3 Test Enforcement Tools** ✅
- File: `tools/test_enforcement/validate_tests.py`
- Change: Use SSOT enum instead of string literals
- Status: DONE - Replaced 'HIGH'/'MEDIUM'/'LOW' with SeverityLevel enum values

- File: `tools/test_enforcement/identify_violations.py`
- Change: Use SSOT enum instead of string literals
- Status: DONE - Replaced all severity strings with SeverityLevel enum values

### Phase 3: Update Ruff Integration (Low Risk) ✅ COMPLETE

**3.1 Pre-Commit Config** ✅
- File: `.pre-commit-config.yaml`
- Change: Added comment mapping P0-P3 to SSOT
- Status: DONE - Added SEVERITY SSOT comments to all Ruff tiers and ADG gates

### Phase 4: Update Documentation (Low Risk) ✅ COMPLETE

**4.1 Constitutional Rules** ✅
- Status: NO CHANGES NEEDED - constitutional.md has no severity-specific terminology to update

**4.2 Pre-Commit Comments** ✅
- Status: COMPLETED IN PHASE 3 - SSOT comments already added to `.pre-commit-config.yaml`

## Testing Strategy

**Unit Tests**
- Test all conversion functions (`from_ruff_category`, `from_adg_category`, `from_legacy_string`)
- Test backward compatibility aliases
- Test case-insensitive legacy string conversion

**Integration Tests**
- Verify ADG P1 gate blocks on `SeverityLevel.CRITICAL`
- Verify pre-commit summary reports use SSOT enum values
- Verify validation config uses SSOT for severity assignment

**Regression Tests**
- Run full pre-commit hook suite
- Run ADG generation
- Run test enforcement tools

## Rollback Plan

If issues arise:
1. Revert individual file changes
2. Keep SSOT file in place but don't use it
3. Each phase can be rolled back independently

## Success Criteria

- [x] All severity enums import from SSOT (Phase 1 consumers)
- [x] No string literals for severity in production code (Phase 2 - ADG gates + test enforcement)
- [x] All conversion functions tested (Phase 1 - verified imports work)
- [x] Pre-commit hooks pass with SSOT (Phase 3 - comments added, ready for testing)
- [x] ADG generation succeeds with SSOT (Phase 2 - ADG gates updated)
- [x] Documentation updated to reference SSOT (Phase 4 - no changes needed)

## Open Questions

1. Should we enforce SSOT usage via lint rule?
   - Recommendation: ⭐ Yes, add linter to catch string literal severity values

2. Should we deprecate legacy severity values (WARNING, ERROR)?
   - Recommendation: ⭐ Yes, map to MEDIUM/HIGH and add deprecation warning
   - Recommendation: ⭐ Yes, use lowercase for database, uppercase for UI/display via `.display_name`
