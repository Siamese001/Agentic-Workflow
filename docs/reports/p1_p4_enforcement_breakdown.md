# P1-P4 Severity Enforcement - Granular Breakout

**Date:** 2026-04-06  
**Purpose:** Comprehensive mapping of P1-P4 severity levels and where they are used and enforced throughout the repository

## Severity Level Definitions (SSOT: `agentic_core/L5_safety/config/severity.py`)

### P1 (CRITICAL)
- **Value:** `"critical"`
- **P-Level:** P0/P1 (Ruff) / P1 (ADG)
- **Ruff Category:** P0
- **ADG Category:** P1
- **Blocks Commit:** ✅ YES
- **Description:** System-breaking or security-critical - blocks commit
- **Examples:** Layer boundary violations, security vulnerabilities, PowerShell usage, missing critical dependencies, broken imports in production code

### P2 (HIGH)
- **Value:** `"high"`
- **P-Level:** P1/P2 (Ruff) / P2 (ADG)
- **Ruff Category:** P1
- **ADG Category:** P2
- **Blocks Commit:** ✅ YES
- **Description:** Bugs or architectural violations - should fix before commit
- **Examples:** Unused imports, global mutations, test coverage gaps, deprecated APIs, silent exception swallowers, circular dependencies

### P3 (MEDIUM)
- **Value:** `"medium"`
- **P-Level:** P2/P3 (Ruff) / P3 (ADG)
- **Ruff Category:** P2
- **ADG Category:** P3
- **Blocks Commit:** ❌ NO
- **Description:** Code quality issues - consider fixing
- **Examples:** Long functions, complex cyclomatic complexity, inconsistent naming, missing docstrings, TODO comments without owners

### P4 (LOW)
- **Value:** `"low"`
- **P-Level:** P3/P4 (Ruff) / P4 (ADG)
- **Ruff Category:** P3
- **ADG Category:** P4
- **Blocks Commit:** ❌ NO
- **Description:** Minor style issues - informational
- **Examples:** Line length violations, trailing whitespace, missing type hints in utility code, unused variables in tests, debug print statements, semantic enrichment warnings

## Enforcement Points by Category

### 1. ADG Violations (Database: `artifacts/adg/adg_indexed_*.sqlite`)

#### Current State (ADG Snapshot: 04062026_0751)
- **P1 (CRITICAL):** 0 violations
- **P2 (HIGH):** 0 violations
- **P3 (MEDIUM):** 307 violations (antipattern category)
- **P4 (LOW):** 4391 violations (antipattern category)
- **Layer Violations:** 0

#### Violation Schema (violations table)
- `id`: INTEGER (primary key)
- `node_id`: INTEGER (reference to nodes table)
- `category`: TEXT (e.g., "antipattern")
- `violation_type`: TEXT (e.g., "Exception", "ValueError")
- `file_path`: TEXT
- `line_number`: INTEGER
- `status`: TEXT (e.g., "untriaged")
- `severity`: TEXT (CRITICAL, HIGH, MEDIUM, LOW)
- `description`: TEXT
- `remediation`: TEXT

#### Enforcement Scripts

##### `ops_scripts/ci/adg_p1_defect_gate.py`
- **Severity:** P1 (CRITICAL)
- **Purpose:** Blocks commits if P1 defects exist in ADG
- **Enforcement:** Queries ADG for `SeverityLevel.CRITICAL` violations
- **Status:** Commented out in pre-commit (handled by T10.6)
- **Code Reference:** Line 58 - `(SeverityLevel.CRITICAL.value,)`

##### `ops_scripts/ci/adg_layer_violation_gate.py`
- **Severity:** P1 (CRITICAL)
- **Purpose:** Detects and reports layer boundary violations
- **Enforcement:** Queries ADG for layer violation edges
- **Status:** Commented out in pre-commit (handled by T10.6)
- **Code Reference:** Line 8 - "SEVERITY SSOT: Layer violations are classified as SeverityLevel.CRITICAL"

##### `ops_scripts/ci/adg_burndown_gate.py`
- **Severity:** P1/P2 (CRITICAL for new, HIGH for existing)
- **Purpose:** Enforces anti-pattern count ratchet
- **Enforcement:** 
  - New file+category pairs → SeverityLevel.CRITICAL
  - Existing count increases → SeverityLevel.HIGH
- **Status:** Commented out in pre-commit (handled by T10.6)
- **Code Reference:** Line 653 - `severity = SeverityLevel.CRITICAL if is_new else SeverityLevel.HIGH`

### 2. Source-Code Pattern Bans

##### `ops_scripts/ci/adg_python_ban_gate.py`
- **Severity:** P1 (CRITICAL)
- **Purpose:** Blocks grep/mypy/pytest usage as ADG substitutes
- **Enforcement:** Scans Python files for banned patterns
- **Status:** Commented out in pre-commit (handled by T10.6)
- **Code Reference:** Line 335 - `severity=SeverityLevel.CRITICAL`

##### `ops_scripts/ci/adg_yaml_grep_ban_gate.py`
- **Severity:** P1 (CRITICAL)
- **Purpose:** Blocks grep/rg in GitHub Actions workflows
- **Enforcement:** Scans YAML workflow files for banned patterns
- **Status:** Commented out in pre-commit (handled by T10.6)
- **Code Reference:** Line 221 - `severity=SeverityLevel.CRITICAL`

### 3. Structural/Architectural Checks

##### `ops_scripts/ci/hollow_file_gate.py`
- **Severity:** P2 (HIGH) or P3 (MEDIUM)
- **Purpose:** Detects files with no behavioral content
- **Enforcement:**
  - Files with zero FunctionDef/ClassDef → SeverityLevel.HIGH
  - Files with minimal content → SeverityLevel.MEDIUM
- **Status:** Active (T6 in pre-commit)
- **Code Reference:** Lines 259-261

##### `ops_scripts/ci/check_report_location.py` (T7)
- **Severity:** P2 (HIGH)
- **Purpose:** Enforces SSOT for report locations
- **Enforcement:** Reports violate SSOT → SeverityLevel.HIGH
- **Status:** Active (T7 in pre-commit)

##### `ops_scripts/ci/plan_location_gate.py` (T7.5)
- **Severity:** P2 (HIGH)
- **Purpose:** Enforces SSOT for plan locations
- **Enforcement:** Plans violate SSOT → SeverityLevel.HIGH
- **Status:** Active (T7.5 in pre-commit)

##### `ops_scripts/ci/check_tooling_apps_boundary.py` (T9)
- **Severity:** P1 (CRITICAL)
- **Purpose:** Enforces tooling/apps boundary (§8.3)
- **Enforcement:** Cross-boundary violations → SeverityLevel.CRITICAL
- **Status:** Active (T9 in pre-commit)

##### `ops_scripts/ci/module_collision_guard.py` (T10)
- **Severity:** P2 (HIGH)
- **Purpose:** Detects duplicate filenames across modules
- **Enforcement:** Filename collisions → SeverityLevel.HIGH
- **Status:** Active (T10 in pre-commit)

### 4. Config/Governance Checks

##### `ops_scripts/ci/check_windsurf_governance.py` (T7.7)
- **Severity:** P2 (HIGH)
- **Purpose:** Validates governance configuration health
- **Enforcement:** Governance violations → SeverityLevel.HIGH
- **Status:** Active (T7.7 in pre-commit)

##### `ops_scripts/ci/check_mcp_config_sovereignty.py` (T11)
- **Severity:** P1 (CRITICAL)
- **Purpose:** Enforces MCP config sovereignty (Rule #0)
- **Enforcement:** Non-sovereign config → SeverityLevel.CRITICAL
- **Status:** Active (T11 in pre-commit)

##### `ops_scripts/ci/guardian_exemption_gate.py` (T12)
- **Severity:** P2 (HIGH)
- **Purpose:** Enforces guardian exemption quality ratchet
- **Enforcement:** Exemption ceiling exceeded → SeverityLevel.HIGH
- **Status:** Active (T12 in pre-commit)
- **Code Reference:** Lines 748, 761

### 5. Pre-Commit Summary Reporting

##### `ops_scripts/ci/pre_commit_summary_reporter.py` (T21)
- **Purpose:** Aggregates and displays hook results
- **Severity Usage:**
  - Line 106: Default severity = SeverityLevel.MEDIUM
  - Lines 220-223: Severity ordering for display
  - Lines 251-260: Color-coded severity display
  - Line 314: Blocks commit if CRITICAL + HIGH > 0
  - Line 323: Warns if MEDIUM + LOW > 0
- **Status:** Active (T21 in pre-commit)

##### `ops_scripts/ci/pre_commit_issue_schema.py`
- **Purpose:** Schema for pre-commit issues
- **Severity Usage:**
  - Lines 158-161: Color codes by severity
  - Lines 166-169: Icons by severity
- **Status:** Infrastructure (not a hook)

### 6. Ruff Linting (T2)

##### `.pre-commit-config.yaml` (T2 Hooks)
- **T2-P0: Ruff CRITICAL (Security/Safety/Runtime)**
  - Severity: P1 (CRITICAL)
  - Ruff Categories: S603, S607, S324
  - Maps to: SeverityLevel.CRITICAL
  - Status: Active (T2-P0 in pre-commit)
  
- **T2-P1: Ruff HIGH (Bug Patterns/Code Quality)**
  - Severity: P2 (HIGH)
  - Ruff Categories: B007, E402, etc.
  - Maps to: SeverityLevel.HIGH
  - Status: Active (T2-P1 in pre-commit)

- **T2-P2: Ruff MEDIUM (Style/Organization)**
  - Severity: P3 (MEDIUM)
  - Ruff Categories: Import organization, unused variables
  - Maps to: SeverityLevel.MEDIUM
  - Status: Active (T2-P2 in pre-commit)

- **T2-P3: Ruff LOW (Formatting/Python3)**
  - Severity: P4 (LOW)
  - Ruff Categories: Line length, minor formatting
  - Maps to: SeverityLevel.LOW
  - Status: Active (T2-P3 in pre-commit)

### 7. Test Enforcement

##### `tests/unit/agentic_core/L5_safety/config/test_severity.py`
- **Purpose:** Unit tests for SeverityLevel enum
- **Coverage:**
  - P-level mapping (lines 29-32)
  - Ruff category mapping (lines 37-40)
  - ADG category mapping (lines 44-47)
  - Conversion functions (lines 54-91)
  - Legacy string conversion (lines 102-117)
  - Blocks commit property (line 91)
- **Status:** Active test suite

##### `tests/ops_scripts/ci/test_pre_commit_summary_reporter.py`
- **Purpose:** Tests for pre-commit summary reporter
- **Coverage:**
  - Severity colorization (lines 196-202)
  - Severity icons (lines 207-210)
  - Severity ordering (lines 124-273)
- **Status:** Active test suite

##### `tests/ops_scripts/ci/test_pre_commit_issue_schema.py`
- **Purpose:** Tests for pre-commit issue schema
- **Coverage:**
  - Severity enum values (lines 24-27)
  - Severity assignment (lines 39-178)
  - Severity display (lines 196-210)
- **Status:** Active test suite

## Pre-Commit Hook Severity Mapping

### P1 (CRITICAL) - Blocks Commit (7 Active Hooks)
- T0-guard: Agent Deletion Authorization → `ops_scripts/hooks/guard_agent_deletion.py` (N/A)
- T0: Check Merge Conflict Markers → Built-in pre-commit hook (N/A)
- T1: Python Syntax Validation → Built-in pre-commit hook (N/A)
- T2-P0: Ruff CRITICAL → Built-in ruff hook (`.pre-commit-config.yaml:174`)
- T9: Tooling/Apps Boundary Guard → `ops_scripts/ci/check_tooling_apps_boundary.py` (N/A)
- T10.6: ADG Unified Gate → `ops_scripts/hooks/adg_unified_gate.py` (`.pre-commit-config.yaml:374`)
- T11: MCP Config Sovereignty → `ops_scripts/ci/check_mcp_config_sovereignty.py` (`.pre-commit-config.yaml:387`)

### P2 (HIGH) - Blocks Commit (11 Active Hooks)
- T2-P1: Ruff HIGH → Built-in ruff hook (`.pre-commit-config.yaml:185`)
- T6: Hollow File Gate → `ops_scripts/ci/hollow_file_gate.py` (`.pre-commit-config.yaml:275`)
- T7: Report Location SSOT Check → `ops_scripts/ci/check_report_location.py` (`.pre-commit-config.yaml:284`)
- T7.5: Plan Location SSOT Gate → `ops_scripts/ci/plan_location_gate.py` (`.pre-commit-config.yaml:294`)
- T7.7-P1: Windsurf Governance Health Check → `ops_scripts/ci/check_windsurf_governance.py` (`.pre-commit-config.yaml:307`)
- T8: Reject Tracked Generated Artifacts → `ops_scripts/ci/reject_generated_artifacts_tracked.py` (`.pre-commit-config.yaml:320`)
- T10: Module Collision Guard → `ops_scripts/ci/module_collision_guard.py` (`.pre-commit-config.yaml:331`)
- T11.3: Pytest Config SSOT → `ops_scripts/ci/pytest_config_ssot.py` (`.pre-commit-config.yaml:410`)
- T12: Guardian Exemption Quality Ratchet → `ops_scripts/ci/guardian_exemption_gate.py` (`.pre-commit-config.yaml:429`)

### P3 (MEDIUM) - Does Not Block (2 Active Hooks)
- T2-P2: Ruff MEDIUM → Built-in ruff hook (`.pre-commit-config.yaml:196`)
- T4: Guardian Comment Auto-Fix → Built-in guardian hook (`.pre-commit-config.yaml:232`)

### P4 (LOW) - Does Not Block (5 Active Hooks)
- T0: Trailing Whitespace → Built-in pre-commit hook (N/A)
- T0: End-of-File Fixer → Built-in pre-commit hook (N/A)
- T0: Enforce LF Line Endings → Built-in pre-commit hook (N/A)
- T2-P3: Ruff LOW → Built-in ruff hook (`.pre-commit-config.yaml:207`)
- T3: Ruff Format → Built-in ruff hook (`.pre-commit-config.yaml:218`)

## ADG Violation Categories by Severity

### Current ADG Violation Distribution (Snapshot: 04062026_0751)
- **P3 (MEDIUM):** 307 violations (all antipattern category)
  - Examples: Exception types, ValueError, ImportError, custom exceptions
  - Files: `agentic_core/L0_routing/enforcement/*.py`
  
- **P4 (LOW):** 4391 violations (all antipattern category)
  - Examples: Custom exception types, error handling patterns
  - Files: Distributed across enforcement modules

### ADG Violation Types by Category
- LOW: antipattern (4391) - Exception, ValueError, ImportError, PipeOrderViolation, PolicyMutationIncident, etc.
- MEDIUM: antipattern (307) - Various exception types in enforcement code
- HIGH: antipattern (0) - N/A
- CRITICAL: antipattern (0) - N/A

## Severity Conversion Functions

### Ruff to SeverityLevel (`from_ruff_category`)
- **P0** → SeverityLevel.CRITICAL
- **P1** → SeverityLevel.HIGH
- **P2** → SeverityLevel.MEDIUM
- **P3** → SeverityLevel.LOW

### ADG to SeverityLevel (`from_adg_category`)
- **P1** → SeverityLevel.CRITICAL
- **P2** → SeverityLevel.HIGH
- **P3** → SeverityLevel.MEDIUM
- **P4** → SeverityLevel.LOW

### Legacy String to SeverityLevel (`from_legacy_string`)
- **CRITICAL, critical, P1, P0** → SeverityLevel.CRITICAL
- **HIGH, high, P2** → SeverityLevel.HIGH
- **MEDIUM, medium, P3, WARNING** → SeverityLevel.MEDIUM
- **LOW, low, P4** → SeverityLevel.LOW
- **INFO, passed, skipped** → SeverityLevel.INFO
- **ERROR** → SeverityLevel.HIGH

## Blocking Behavior

### Blocks Commit (CRITICAL + HIGH)
- **Property:** `SeverityLevel.blocks_commit` returns `True` for CRITICAL and HIGH
- **Implementation:** `return self in (SeverityLevel.CRITICAL, SeverityLevel.HIGH)`
- **Pre-Commit Enforcement:** T21 summary reporter blocks if `critical_high_count > 0`
- **Code Reference:** `ops_scripts/ci/pre_commit_summary_reporter.py:314`

### Does Not Block (MEDIUM + LOW)
- **Property:** `SeverityLevel.blocks_commit` returns `False` for MEDIUM and LOW
- **Pre-Commit Enforcement:** T21 summary reporter warns if `medium + low > 0` but does not block
- **Code Reference:** `ops_scripts/ci/pre_commit_summary_reporter.py:323`

## Color and Icon Mapping

### Color Codes (Terminal)
- **CRITICAL:** `\033[91m` (Bright red)
- **HIGH:** `\033[93m` (Bright yellow)
- **MEDIUM:** `\033[94m` (Bright blue)
- **LOW:** `\033[97m` (Bright white)

### Icons (ASCII - Windows Compatible)
- **CRITICAL:** `[!]` or `⛔` (original emoji, replaced for Windows)
- **HIGH:** `[!]` or `⚠️` (original emoji, replaced for Windows)
- **MEDIUM:** `[*]` or `🔹` (original emoji, replaced for Windows)
- **LOW:** `[i]` or `ℹ️` (original emoji, replaced for Windows)
- **INFO:** `[OK]` or `✓` (original emoji, replaced for Windows)

## Key Files Reference

### SSOT Definitions
- **Severity Enum:** `agentic_core/L5_safety/config/severity.py`
- **Pre-Commit Config:** `.pre-commit-config.yaml`
- **ADG Database:** `artifacts/adg/adg_indexed_*.sqlite`

### Enforcement Scripts
- **ADG Gates:** `ops_scripts/ci/adg_*.py`
- **Structural Gates:** `ops_scripts/ci/*_gate.py`
- **Config Checks:** `ops_scripts/ci/check_*.py`
- **Summary Reporter:** `ops_scripts/ci/pre_commit_summary_reporter.py`

### Test Files
- **Severity Tests:** `tests/unit/agentic_core/L5_safety/config/test_severity.py`
- **Summary Reporter Tests:** `tests/ops_scripts/ci/test_pre_commit_summary_reporter.py`
- **Issue Schema Tests:** `tests/ops_scripts/ci/test_pre_commit_issue_schema.py`

## Summary

### Enforcement Coverage
- **P1 (CRITICAL):** 7 active hooks + ADG generation
- **P2 (HIGH):** 11 active hooks + ADG generation
- **P3 (MEDIUM):** 2 active hooks (non-blocking)
- **P4 (LOW):** 5 active hooks (non-blocking)

### Current ADG State
- **P1 Violations:** 0
- **P2 Violations:** 0
- **P3 Violations:** 307 (antipattern)
- **P4 Violations:** 4391 (antipattern)
- **Layer Violations:** 0

### Key Observations
1. **Unified Gate Consolidation:** T10.6 consolidates 7 ADG-related hooks into a single orchestrator
2. **Severity Consistency:** All enforcement points use the canonical SeverityLevel enum
3. **Blocking Behavior:** CRITICAL and HIGH block commits; MEDIUM and LOW do not
4. **ADG Integration:** ADG generation (T10.6) is the primary source of P1-P4 violation data
5. **Test Coverage:** Comprehensive test coverage for severity enum and pre-commit schema
