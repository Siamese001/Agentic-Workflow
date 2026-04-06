# Pre-Commit Hook to P1-P4 Severity Mapping

**Date:** 2026-04-06  
**Purpose:** Map pre-commit hook checks to P1-P4 severity categories based on SeverityLevel SSOT

## Severity Level Definitions (from `agentic_core/L5_safety/config/severity.py`)

### P1 (CRITICAL)
- **IMPACT:** System-breaking, security breach, data loss, or constitutional violation
- **URGENCY:** Immediate - MUST block commit until fixed
- **EXAMPLES:** Layer boundary violations, security vulnerabilities, PowerShell usage, missing critical dependencies, broken imports in production code
- **Blocks Commit:** ✅ YES

### P2 (HIGH)
- **IMPACT:** Bugs that affect functionality, architectural violations, anti-patterns
- **URGENCY:** High - should fix before commit, degrades quality significantly
- **EXAMPLES:** Unused imports, global mutations, test coverage gaps, deprecated APIs, silent exception swallowers, circular dependencies
- **Blocks Commit:** ✅ YES

### P3 (MEDIUM)
- **IMPACT:** Code quality issues, maintainability concerns, style violations
- **URGENCY:** Medium - consider fixing, technical debt accumulation
- **EXAMPLES:** Long functions, complex cyclomatic complexity, inconsistent naming, missing docstrings, TODO comments without owners
- **Blocks Commit:** ❌ NO

### P4 (LOW)
- **IMPACT:** Minor style issues, formatting, informational
- **URGENCY:** Low - nice to have, can be deferred
- **EXAMPLES:** Line length violations, trailing whitespace, missing type hints in utility code, unused variables in tests, debug print statements, semantic enrichment warnings
- **Blocks Commit:** ❌ NO

## Pre-Commit Hook Mapping

### T0: Admission/Guards

#### T0-guard: Agent Deletion Authorization
- **Severity:** P1 (CRITICAL)
- **Rationale:** Deleting agents without authorization is a constitutional violation (Rule §1.6)
- **Impact:** Loss of critical system components
- **Blocks Commit:** ✅ YES

#### T0: Trailing Whitespace
- **Severity:** P4 (LOW)
- **Rationale:** Minor formatting issue, does not affect functionality
- **Impact:** Cosmetic only
- **Blocks Commit:** ❌ NO

#### T0: End-of-File Fixer
- **Severity:** P4 (LOW)
- **Rationale:** Minor formatting issue, ensures file ends with newline
- **Impact:** Cosmetic only
- **Blocks Commit:** ❌ NO

#### T0: Enforce LF Line Endings
- **Severity:** P4 (LOW)
- **Rationale:** Cross-platform consistency, minor formatting
- **Impact:** Cosmetic only, auto-fixable
- **Blocks Commit:** ❌ NO

#### T0: Check Merge Conflict Markers
- **Severity:** P1 (CRITICAL)
- **Rationale:** Merge conflicts indicate unresolved repository state
- **Impact:** System-breaking if committed
- **Blocks Commit:** ✅ YES

### T1: Syntax Validation

#### T1: Python Syntax Validation
- **Severity:** P1 (CRITICAL)
- **Rationale:** Broken syntax makes code unrunnable
- **Impact:** System-breaking
- **Blocks Commit:** ✅ YES

### T2: Ruff Linting

#### T2-P0: Ruff CRITICAL (Security/Safety/Runtime)
- **Severity:** P1 (CRITICAL)
- **Rationale:** Security vulnerabilities, safety violations, runtime errors
- **Impact:** Security breach or system-breaking
- **Blocks Commit:** ✅ YES
- **Examples:** S603 (subprocess with untrusted input), S607 (partial executable paths), S324 (insecure hash)

#### T2-P1: Ruff HIGH (Bug Patterns/Code Quality)
- **Severity:** P2 (HIGH)
- **Rationale:** Bug patterns and high-impact code quality issues
- **Impact:** Bugs that affect functionality
- **Blocks Commit:** ✅ YES
- **Examples:** B007 (unused loop variables), E402 (module level import not at top)

#### T2-P2: Ruff MEDIUM (Style/Organization)
- **Severity:** P3 (MEDIUM)
- **Rationale:** Style and organization issues
- **Impact:** Code quality and maintainability
- **Blocks Commit:** ❌ NO
- **Examples:** Import organization, unused variables, code complexity

#### T2-P3: Ruff LOW (Formatting/Python3)
- **Severity:** P4 (LOW)
- **Rationale:** Minor formatting and Python3 compatibility
- **Impact:** Cosmetic or minor compatibility
- **Blocks Commit:** ❌ NO
- **Examples:** Line length, minor formatting issues

### T3: Formatting

#### T3: Ruff Format
- **Severity:** P4 (LOW)
- **Rationale:** Code formatting normalization
- **Impact:** Cosmetic only, auto-fixable
- **Blocks Commit:** ❌ NO

### T4: Guardian Comments

#### T4: Guardian Comment Auto-Fix (Accelerator #1)
- **Severity:** P3 (MEDIUM)
- **Rationale:** Canonicalizes guardian comment format
- **Impact:** Maintainability and tool consistency
- **Blocks Commit:** ❌ NO

### T-1: Pre-Commit Summary

#### T-1: Pre-Commit Summary Initialization
- **Severity:** INFO
- **Rationale:** Infrastructure for reporting, not a validation check
- **Impact:** None
- **Blocks Commit:** ❌ NO

### T5: ADG CI Gates (Manual Only)

#### T5: ADG CI Gates (M1-M6)
- **Severity:** P1 (CRITICAL)
- **Rationale:** CI delta gates ensure ADG consistency across environments
- **Impact:** System-breaking if ADG is out of sync
- **Blocks Commit:** ✅ YES (manual stage only)

### T6: AST Semantics

#### T6: Hollow File Gate — AST Semantic Verification
- **Severity:** P2 (HIGH)
- **Rationale:** Detects files with no behavioral content (hollow files)
- **Impact:** Architectural violation, dead code
- **Blocks Commit:** ✅ YES

### T7: SSOT Paths

#### T7: Report Location SSOT Check
- **Severity:** P2 (HIGH)
- **Rationale:** Enforces SSOT for report locations
- **Impact:** Architectural violation, breaks tooling
- **Blocks Commit:** ✅ YES

#### T7.5: Plan Location SSOT Gate
- **Severity:** P2 (HIGH)
- **Rationale:** Enforces SSOT for plan locations
- **Impact:** Architectural violation, breaks tooling
- **Blocks Commit:** ✅ YES

### T7.7: Governance

#### T7.7-P1: Windsurf Governance Health Check
- **Severity:** P2 (HIGH)
- **Rationale:** Validates governance configuration health
- **Impact:** Architectural violation, breaks governance
- **Blocks Commit:** ✅ YES

### T8: Artifacts

#### T8: Reject Tracked Generated Artifacts
- **Severity:** P2 (HIGH)
- **Rationale:** Prevents tracking generated artifacts in git
- **Impact:** Repository bloat, breaks build reproducibility
- **Blocks Commit:** ✅ YES

### T9: Boundary

#### T9: Tooling/Apps Boundary Guard (§8.3)
- **Severity:** P1 (CRITICAL)
- **Rationale:** Enforces layer boundary between tooling and apps
- **Impact:** Architectural violation, layer boundary violation
- **Blocks Commit:** ✅ YES

### T10: Architectural

#### T10: Module Collision Guard
- **Severity:** P2 (HIGH)
- **Rationale:** Detects duplicate filenames across modules
- **Impact:** Architectural violation, breaks imports
- **Blocks Commit:** ✅ YES

#### T10.5: Eager Import Lint (Temporarily Disabled)
- **Severity:** P2 (HIGH)
- **Rationale:** Detects risky module-level imports in tests
- **Impact:** Test collection failures, breaks CI
- **Blocks Commit:** ✅ YES

#### T10.6: ADG Unified Gate — ADG generation + source-code checks
- **Severity:** P1 (CRITICAL)
- **Rationale:** Orchestrates ADG generation and source-code checks
- **Impact:** System-breaking if ADG is invalid
- **Blocks Commit:** ✅ YES
- **Sub-checks:**
  - P1 Defects (layer violations) → P1 (CRITICAL)
  - Python grep ban → P2 (HIGH)
  - YAML grep ban → P2 (HIGH)
  - Skip-file ratchet → P2 (HIGH)

### T11: Config

#### T11: MCP Config Sovereignty — filesystem allowedDirectories locked to repo root (Rule #0)
- **Severity:** P1 (CRITICAL)
- **Rationale:** Enforces constitutional Rule #0 for MCP config
- **Impact:** Constitutional violation, security risk
- **Blocks Commit:** ✅ YES

#### T11.2: MCP Config Drift Detection (Temporarily Disabled)
- **Severity:** P2 (HIGH)
- **Rationale:** Prevents drift between workspace and global MCP config
- **Impact:** Architectural violation, breaks tooling
- **Blocks Commit:** ✅ YES

#### T11.3: Pytest Config SSOT — pytest.ini vs pyproject.toml consistency
- **Severity:** P2 (HIGH)
- **Rationale:** Ensures pytest config consistency
- **Impact:** Architectural violation, breaks testing
- **Blocks Commit:** ✅ YES

### T12: Governance

#### T12: Guardian Exemption Quality Ratchet
- **Severity:** P2 (HIGH)
- **Rationale:** Enforces guardian exemption count ceiling
- **Impact:** Architectural violation, allows anti-pattern accumulation
- **Blocks Commit:** ✅ YES

### T13: ADG Anti-Pattern (Commented Out - Handled by T10.6)

#### T13: ADG Anti-Pattern Burndown Ratchet
- **Severity:** P2 (HIGH)
- **Rationale:** Enforces anti-pattern count ratchet
- **Impact:** Architectural violation, allows anti-pattern accumulation
- **Blocks Commit:** ✅ YES
- **Status:** Commented out - now handled by T10.6 (generate_full_adg.py)

#### T13.5: ADG Layer Violation Gate
- **Severity:** P1 (CRITICAL)
- **Rationale:** Detects layer boundary violations
- **Impact:** Architectural violation, layer boundary violation
- **Blocks Commit:** ✅ YES
- **Status:** Commented out - now handled by T10.6 (generate_full_adg.py)

#### T13.6: ADG P1 Defect Gate — BLOCKING
- **Severity:** P1 (CRITICAL)
- **Rationale:** Blocks commits if P1 defects exist
- **Impact:** System-breaking, layer violations
- **Blocks Commit:** ✅ YES
- **Status:** Commented out - now handled by T10.6 (generate_full_adg.py)

### T14: ADG Python Ban (Commented Out - Handled by T10.6)

#### T14: ADG Python Ban Gate — no grep/mypy/pytest as ADG substitutes
- **Severity:** P2 (HIGH)
- **Rationale:** Prevents using grep/mypy/pytest as ADG substitutes
- **Impact:** Architectural violation, breaks ADG acceleration
- **Blocks Commit:** ✅ YES
- **Status:** Commented out - now handled by T10.6

### T15: ADG YAML Grep-Ban (Commented Out - Handled by T10.6)

#### T15: ADG YAML Grep-Ban Gate — no grep/rg in GitHub Actions run: steps
- **Severity:** P2 (HIGH)
- **Rationale:** Prevents grep/rg in GitHub Actions workflows
- **Impact:** Architectural violation, breaks ADG acceleration
- **Blocks Commit:** ✅ YES
- **Status:** Commented out - now handled by T10.6

### T16: Skip-File Ratchet (Commented Out - Handled by T10.6)

#### T16: ADG Skip-File Ratchet — enforce skip-file directive count ceiling
- **Severity:** P2 (HIGH)
- **Rationale:** Enforces skip-file directive count ceiling
- **Impact:** Architectural violation, allows anti-pattern accumulation
- **Blocks Commit:** ✅ YES
- **Status:** Commented out - now handled by T10.6

### T20: Cleanup (Temporarily Disabled)

#### T20: Pycache Purge (Final Cleanup)
- **Severity:** P4 (LOW)
- **Rationale:** Cleans up __pycache__ directories
- **Impact:** Repository cleanliness, cosmetic
- **Blocks Commit:** ❌ NO
- **Status:** Temporarily disabled due to file corruption issue on Windows

### T21: Summary Report

#### T21: Pre-Commit Governance Summary Report
- **Severity:** INFO
- **Rationale:** Displays summary of hook results, not a validation check
- **Impact:** None
- **Blocks Commit:** ❌ NO

## Summary by Severity Category

### P1 (CRITICAL) - Blocks Commit
- T0-guard: Agent Deletion Authorization
- T0: Check Merge Conflict Markers
- T1: Python Syntax Validation
- T2-P0: Ruff CRITICAL (Security/Safety/Runtime)
- T9: Tooling/Apps Boundary Guard
- T10.6: ADG Unified Gate
- T11: MCP Config Sovereignty

### P2 (HIGH) - Blocks Commit
- T2-P1: Ruff HIGH (Bug Patterns/Code Quality)
- T6: Hollow File Gate
- T7: Report Location SSOT Check
- T7.5: Plan Location SSOT Gate
- T7.7-P1: Windsurf Governance Health Check
- T8: Reject Tracked Generated Artifacts
- T10: Module Collision Guard
- T10.5: Eager Import Lint (disabled)
- T11.2: MCP Config Drift Detection (disabled)
- T11.3: Pytest Config SSOT
- T12: Guardian Exemption Quality Ratchet

### P3 (MEDIUM) - Does Not Block
- T2-P2: Ruff MEDIUM (Style/Organization)
- T4: Guardian Comment Auto-Fix

### P4 (LOW) - Does Not Block
- T0: Trailing Whitespace
- T0: End-of-File Fixer
- T0: Enforce LF Line Endings
- T2-P3: Ruff LOW (Formatting/Python3)
- T3: Ruff Format
- T20: Pycache Purge (disabled)

### INFO - Not a Validation Check
- T-1: Pre-Commit Summary Initialization
- T21: Pre-Commit Governance Summary Report

## Anti-Pattern Mapping

### Anti-Patterns Checked by Pre-Commit

#### Security Anti-Patterns (P1)
- **PowerShell Usage:** T2-P0 (S607) - Blocks commits with PowerShell
- **Subprocess with Untrusted Input:** T2-P0 (S603) - Blocks unsafe subprocess calls
- **Insecure Hash Functions:** T2-P0 (S324) - Blocks MD5 usage (unless exempted)
- **MCP Config Violations:** T11 - Blocks non-sovereign MCP config

#### Architectural Anti-Patterns (P2)
- **Layer Boundary Violations:** T9, T10.6 (via ADG) - Blocks cross-layer violations
- **Module Collisions:** T10 - Blocks duplicate filenames
- **SSOT Violations:** T7, T7.5 - Blocks misplaced reports/plans
- **Generated Artifacts in Git:** T8 - Blocks tracking generated files
- **Hollow Files:** T6 - Blocks files with no behavioral content
- **Grep as ADG Substitute:** T10.6 - Blocks grep/mypy/pytest usage
- **Skip-File Proliferation:** T10.6, T12 - Blocks uncontrolled skip-file directives

#### Code Quality Anti-Patterns (P2-P3)
- **Unused Variables:** T2-P1 (B007) - Blocks unused loop variables
- **Module-Level Imports Not at Top:** T2-P1 (E402) - Blocks E402 violations
- **Guardian Comment Format:** T4 - Auto-fixes non-canonical guardian comments
- **Import Organization:** T2-P2 - Auto-fixes import order

#### Style Anti-Patterns (P4)
- **Trailing Whitespace:** T0 - Auto-fixes trailing whitespace
- **Missing Newline at EOF:** T0 - Auto-fixes EOF
- **Line Endings:** T0 - Auto-fixes line endings
- **Code Formatting:** T3 - Auto-fixes formatting

## Conclusion

The pre-commit configuration maps well to the P1-P4 severity taxonomy:

- **P1 (CRITICAL):** 7 active hooks that block commits for system-breaking issues
- **P2 (HIGH):** 11 active hooks that block commits for architectural violations and bugs
- **P3 (MEDIUM):** 2 active hooks for code quality (auto-fixable, don't block)
- **P4 (LOW):** 5 active hooks for style/formatting (auto-fixable, don't block)

The unified ADG gate (T10.6) consolidates 7 previously separate hooks, all of which map to P1 or P2 severity, maintaining the same blocking behavior while eliminating redundancy.
