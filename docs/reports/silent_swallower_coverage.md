# Silent Swallower Coverage - Enforcement and Testing

**Date:** 2026-04-06  
**Purpose:** Document all locations where silent swallowers are detected, enforced, and tested

## Enforcement Separation of Concerns

**Architectural Preference: ADG-First Enforcement**

**Pre-Commit (Removed for Silent Swallowers):** Too heavy
- Silent swallower detection requires AST analysis
- AST analysis is too slow for pre-commit (minutes vs seconds)
- Removed T4 (guardian) for silent swallowers

**ADG (Primary Enforcement):** P2 (HIGH) - Architectural tracking
- Silent swallowers recorded as P2 (HIGH) in ADG
- Does NOT block ADG generation (only P1 blocks via `_check_p1_defects()`)
- AST analysis is acceptable during ADG generation
- Purpose: Architectural integrity, compliance tracking
- **Primary Enforcement:** ADG is the authoritative source for tracking, not ad-hoc scripts
- **Blocking:** P2 does NOT block, only P1 blocks ADG generation

**Guardian Fix Scripts:** Auto-run enforcement
- Automatically run after ADG generation completes when P2 violations detected
- Fix silent swallowers automatically without manual intervention
- ADG generation handles ongoing enforcement automatically

**Rationale:**
- Pre-commit stays fast (seconds) for basic hygiene
- ADG handles heavy architectural analysis (minutes)
- No reliance on ad-hoc guardian scripts
- ADG is comprehensive and catches violations early in development cycle

## Policy Document

**Location:** `docs/reference/_primers/Python/Error & Exception Handling.md`

**Definition:** Column 3 (BROAD SWALLOW/SILENT SWALLOWER) - Exception handling that catches errors but hides the truth, preventing proper error reporting and recovery.

**Severity:** P2 (HIGH) - Tracked in ADG, does NOT block ADG generation (only P1 blocks)

## Guardian Validators (L5 Safety)

**Note:** These validators run during ADG generation, NOT pre-commit

### 1. Silent Swallower Validator
**Location:** `agentic_core/L5_safety/validators/silent_swallower_validator.py`

**Purpose:** Detect silent swallower patterns in AST across all Python files

**Detection Patterns:**
- `except Exception:` with `pass` (broad swallow)
- `except:` with `pass` (bare except)
- `except Exception:` with only logging (no action)
- Missing exception handling in critical paths

**Whitelist:** `# guardian: allow-silent-swallow` comment (3-5 lines above violation)

**Category:** `AntiPatternCategory.SILENT_SWALLOWER`

**Severity:** P2 (HIGH) - Tracked in ADG, does NOT block ADG generation (only P1 blocks)

---

### 2. Silent Degradation Validator
**Location:** `agentic_core/L5_safety/validators/silent_degradation_validator.py`

**Purpose:** Detect availability guard skips and silent degradation patterns

**Detection Patterns:**
- `EXCEPT_IMPORT_PASS` - `except ImportError: pass` (ImportError-specific silent swallow)
- Availability guard skips without proper handling
- Silent degradation of system capabilities

**Whitelist:** `# guardian: allow-silent-swallow` comment

**Category:** `AntiPatternCategory.SILENT_DEGRADATION`

**Severity:** P2 (HIGH) - Tracked in ADG, does NOT block ADG generation (only P1 blocks)

---

### 3. Utility Silent Swallower Validator
**Location:** `agentic_core/L5_safety/validators/utility_silent_swallower_validator.py`

**Purpose:** Enhanced silent swallower detection for utility/ops scripts with context-aware analysis

**Detection Patterns:**
- Context-aware silent swallower detection in utility scripts
- Distinguishes between legitimate error handling and silent swallows
- Enhanced for ops/scripts directory patterns

**Whitelist:** `# guardian: allow-silent-swallow` comment

**Category:** `AntiPatternCategory.SILENT_SWALLOWER`

**Severity:** P2 (HIGH) - Tracked in ADG, does NOT block ADG generation (only P1 blocks)

---

## Pre-Commit Enforcement

### Guardian Hook (T4) - REMOVED for Silent Swallowers
**Status:** REMOVED for silent swallowers

**Reason:** AST-based silent swallower detection is too heavy for pre-commit (minutes vs seconds)

**Architectural Decision:** Move heavy architectural checks to ADG, keep pre-commit light and fast

**What Remains in Pre-Commit:**
- Syntax validation (T1)
- Basic linting (T2 - Ruff)
- Formatting (T3)
- Whitespace checks (T0)
- Other lightweight checks

---

## Test Coverage

### 1. Guardian Test - Silent Skip Detector
**Location:** `tests/guardian/test_test_silent_skip_detector.py`

**Purpose:** Test silent swallower detection in test files

**Test Coverage:**
- `test_error_severity()` - Verifies all violations have "error" severity (lines 299-307)
- `test_flag_false_under_except()` - Detects `flag = False` under except (lines 271-283)
- `test_availability_guard_skip()` - Detects availability guard skips (lines 241-254)
- Multiple negative tests for proper handling patterns

**Severity Validation:** All violations must have `severity == "error"` (line 308)

---

### 2. Guardian Test - Exemption Recognition
**Location:** `tests/guardian/test_exemption_recognition.py`

**Purpose:** Test guardian exemption suppression for silent swallowers

**Test Coverage:**
- `test_exemption_within_3_lines()` - Exemptions within 3-5 lines suppress violations (lines 15-33)
- `test_exemption_at_5_lines()` - Exemptions at exactly 5 lines suppress violations (lines 35-49)
- `test_exemption_too_far_4_lines()` - Exemptions too far (4+) do not suppress (lines 147-166)
- `test_exemption_too_far_6_lines()` - Exemptions too far (6+) do not suppress (lines 168-190)
- `test_malformed_exemption()` - Malformed exemptions do not suppress (lines 192-210)

**Category:** `silent_degradation` (line 166)

---

### 3. Guardian Test - Agent Autonomy
**Location:** `tests/guardian/test_agent_autonomy.py`

**Purpose:** Test agent method compliance related to error handling

**Test Coverage:**
- Agent method validation (heal_repository, etc.)
- Missing method detection

**Severity:** P1 (BLOCKING) for missing critical methods

---

## Fix Scripts (Auto-Run Enforcement)

**Note:** These scripts run automatically after ADG generation completes when P2 violations are detected, not historical cleanup. ADG handles ongoing enforcement automatically.

### 1. Silent Swallower Fixer
**Location:** `tools/fix/fix_silent_swallowers.py`

**Purpose:** Fix silent swallowers that violate the Error & Exception Handling policy (auto-run after ADG generation)

**Detection:**
- Scans all Python files for silent swallower patterns
- Identifies improper exception handling
- Reports to `tools/silent_swallower_report.json`

**Fix Actions:**
- Adds proper error handling
- Adds logging where appropriate
- Adds guardian exemptions for legitimate cases

**Report:** `tools/silent_swallower_report.json`

**Usage:** Automatically run by ADG generation when P2 violations detected

---

### 2. High Severity Silent Swallower Fixer
**Location:** `tools/fix/fix_high_severity_silent_swallowers.py`

**Purpose:** Fix HIGH severity silent swallower violations

**Severity:** P2 (HIGH) - Prioritized fixes

**Report:** Reads from `tools/silent_swallower_report.json`

---

### 3. Medium Severity Swallower Fixer
**Location:** `tools/fix/fix_medium_severity_swallowers.py`

**Purpose:** Fix MEDIUM severity silent swallower violations

**Severity:** P3 (MEDIUM) - Lower priority fixes

**Report:** Reads from `tools/silent_swallower_report.json`

---

### 4. Low Severity Swallower Fixer
**Location:** `tools/fix/fix_low_severity_swallowers.py`

**Purpose:** Fix LOW severity silent swallower violations

**Severity:** P4 (LOW) - Informational fixes

**Report:** Reads from `tools/silent_swallower_report.json`

---

### 5. AST-Based Silent Swallower Fixer
**Location:** `tools/fix/ast_silent_swallower_fixer.py`

**Purpose:** AST-based silent swallower detection and fixing

**Method:** Uses AST analysis for more precise detection

---

### 6. Phase 1 Silent Swallowers Script
**Location:** `tools/scripts/_phase1_silent_swallowers.py`

**Purpose:** Phase 1: Fix Silent Swallower anti-patterns

**Function:** `fix_file_silent_swallowers()` - Fixes violations in single file

---

### 7. Bulk Guardian Exemptions
**Location:** `tools/fix/bulk_guardian_exemptions.py`

**Purpose:** Apply bulk guardian exemptions for silent swallowers

**Exemptions Applied:** 
- 30+ files with `silent_swallower` exemptions
- Files across all layers (L0-L6)
- Ops scripts and utility files

---

## ADG Integration

### Anti-Pattern Detection (Tracking Only)
**Location:** ADG generation via guardian validators

**Category:** `antipattern` in ADG violations table

**Severity Mapping:**
- Silent swallower violations → P2 (HIGH) in ADG - tracked only, does NOT block
- Silent degradation violations → P2 (HIGH) in ADG - tracked only, does NOT block
- **Note:** ADG tracks silent swallowers for architectural insights, but does NOT block generation (only P1 blocks via `_check_p1_defects()`)

**Purpose:** Architectural validation, compliance metrics, trend analysis

**Current State (Snapshot 04062026_0751):**
- P2 (HIGH): 0 violations (current snapshot shows no silent swallower violations)
- Historical tracking: 30+ files with guardian exemptions

**Enforcement Flow:**
1. Developer writes code
2. Pre-commit runs fast checks (syntax, linting, formatting) - seconds
3. Code committed to repository
4. ADG generation runs heavy analysis (AST, architectural checks) - minutes
5. ADG detects violations → Silent swallowers recorded as P2 (HIGH) for tracking
6. ADG continues generation (P2 does NOT block)
7. ADG completes successfully with violation tracking
8. Developer can review violations and fix if needed

---

## Evidence Scripts

### 1. Scan Silent Swallower
**Location:** `tools/evidence/_scan_silent_swallower.py`

**Purpose:** Scan execute_ssot.py for silent_swallower antipatterns using the gate's scanner

**Method:** Uses guardian scanner for detection

---

### 2. Gate Scan All
**Location:** `tools/evidence/_gate_scan_all.py`

**Purpose:** Comprehensive gate scanning including silent swallower

**Includes:** `_scan_silent_swallower.py` in scan list

---

## Compliance Reporting

### Final Compliance Report
**Location:** `tools/generate/generate_final_compliance_report.py`

**Silent Swallower Metrics:**
- HIGH severity: 8,468 total
- MEDIUM severity: 2,379 total
- LOW severity: 1,715 total
- HIGH fixed: Track via `tools/high_severity_fixes_report.json`
- MEDIUM fixed: Track via `tools/medium_severity_fixes_report.json`

**Status:** Tracked in overall compliance metrics

---

## Guardian Sweep

### Guardian Sweep Script
**Location:** `tools/guardian/guardian_sweep.py`

**Purpose:** Annotate all remaining silent swallower violations with guardian comments

**Behavior:** Adds guardian exemptions to remaining violations

---

## Bulk Exemptions List

**Location:** `tools/fix/bulk_guardian_exemptions.py` (lines 11-30)

**Files with Silent Swallower Exemptions:**
- `adg_static_validation.py`
- `agentic_core/L0_routing/scripts/_ssot_phases.py`
- `agentic_core/L0_routing/scripts/_ssot_validation_artifacts.py`
- `agentic_core/L0_routing/scripts/collision_resolver.py`
- `agentic_core/L0_routing/scripts/forensic_discovery_prep.py`
- `agentic_core/L0_routing/utils/complexity_visitor_util.py`
- `agentic_core/L0_routing/utils/find_misnamed_agents_util.py`
- `agentic_core/L1_cognition/config/react_config.py`
- `agentic_core/L1_cognition/engines/meta_client.py`
- `agentic_core/L1_cognition/engines/query_planner.py`
- `agentic_core/L1_cognition/memory/healing_memory_retriever.py`
- `agentic_core/L2_execution/tools/file_io_impl.py`
- `agentic_core/L2_execution/tools/read_gateway.py`
- `agentic_core/L2_execution/types/ephemeral_vm_types.py`
- `agentic_core/L3_orchestration/engines/agent_gym_engine.py`
- `agentic_core/L3_orchestration/engines/orchestrator_engine.py`
- `agentic_core/L3_orchestration/reasoning/CoverageAgent.py`
- And 10+ more files across all layers

**Total:** 30+ files with silent swallower exemptions

---

## Summary Matrix

| Component | Location | Purpose | Severity | Blocking | Status |
|-----------|----------|---------|----------|----------|--------|
| **Policy Doc** | `docs/reference/_primers/Python/Error & Exception Handling.md` | Policy definition | N/A | N/A | ✅ Active |
| **Validator 1** | `agentic_core/L5_safety/validators/silent_swallower_validator.py` | AST detection | P2 (HIGH) | ❌ No (tracking only) | ✅ Active |
| **Validator 2** | `agentic_core/L5_safety/validators/silent_degradation_validator.py` | Degradation detection | P2 (HIGH) | ❌ No (tracking only) | ✅ Active |
| **Validator 3** | `agentic_core/L5_safety/validators/utility_silent_swallower_validator.py` | Utility script detection | P2 (HIGH) | ❌ No (tracking only) | ✅ Active |
| **Pre-Commit** | `.pre-commit-config.yaml` (T4) | Guardian hook | N/A | ❌ Removed (too heavy) | ❌ Removed |
| **ADG** | ADG generation | Anti-pattern detection | P2 (HIGH) | ❌ No (tracking only) | ✅ Active (tracking) |
| **Test 1** | `tests/guardian/test_test_silent_skip_detector.py` | Test detection | N/A | N/A | ✅ Active |
| **Test 2** | `tests/guardian/test_exemption_recognition.py` | Test exemptions | N/A | N/A | ✅ Active |
| **Test 3** | `tests/guardian/test_agent_autonomy.py` | Agent compliance | P1 (CRITICAL) | ✅ Yes | ✅ Active |
| **Fix Script 1** | `tools/fix/fix_silent_swallowers.py` | Auto-fix enforcement | P2-P4 | N/A (auto-run) | ✅ Available |
| **Fix Script 2** | `tools/fix/fix_high_severity_silent_swallowers.py` | Auto-fix enforcement | P2 (HIGH) | N/A (auto-run) | ✅ Available |
| **Fix Script 3** | `tools/fix/fix_medium_severity_swallowers.py` | Auto-fix enforcement | P3 (MEDIUM) | N/A (auto-run) | ✅ Available |
| **Fix Script 4** | `tools/fix/fix_low_severity_swallowers.py` | Auto-fix enforcement | P4 (LOW) | N/A (auto-run) | ✅ Available |
| **Fix Script 5** | `tools/fix/ast_silent_swallower_fixer.py` | Auto-fix enforcement | P2-P4 | N/A (auto-run) | ✅ Available |
| **Bulk Exemptions** | `tools/fix/bulk_guardian_exemptions.py` | Auto-fix enforcement | N/A | N/A (auto-run) | ✅ Available |
| **Evidence Scan** | `tools/evidence/_scan_silent_swallower.py` | Evidence collection | N/A | N/A | ✅ Available |
| **Compliance** | `tools/generate/generate_final_compliance_report.py` | Metrics tracking | N/A | N/A | ✅ Active |

---

## Current Violation State

**ADG Snapshot (04062026_0751):**
- **P2 (HIGH):** 0 violations (silent swallowers - well-controlled via ADG P2 enforcement)
- **P3 (MEDIUM):** 307 violations (code quality issues - long functions, complexity, etc.)
- **P4 (LOW):** 4391 violations (style issues - line length, trailing whitespace, etc.)

**Compliance Report Metrics (Historical):**
- HIGH severity: 8,468 total (historical cleanup completed)
- MEDIUM severity: 2,379 total (historical cleanup completed)
- LOW severity: 1,715 total (historical cleanup completed)

---

## Enforcement Flow

1. **Developer writes code** → New code added
2. **Pre-commit runs** → Fast checks only (syntax, linting, formatting) - seconds
3. **Commit succeeds** → Code committed to repository
4. **ADG generation runs** → Heavy architectural analysis (AST, silent swallower detection) - minutes
5. **ADG detects violations** → Silent swallowers recorded as P2 (HIGH) for tracking
6. **ADG continues** → ADG generation completes successfully (P2 does NOT block)
7. **Auto-fix scripts run** → Automatically calls `tools/fix/fix_silent_swallowers.py` and `tools/fix/fix_high_severity_silent_swallowers.py`
8. **Fixes applied** → Silent swallowers automatically fixed or guardian exemptions added
9. **Developer reviews** → Can review fixes in git diff
10. **Historical cleanup** → Additional guardian fix scripts used for legacy cleanup if needed

**Note:** Only P1 (CRITICAL) blocks ADG generation via `sys.exit(1)` - immediate failure, no partial outputs. P2/P3/P4 are tracked but do NOT block, and P2 automatically triggers fix scripts.

**Key Point:** ADG tracks violations for architectural insights, P2 automatically triggers fix scripts, only P1 blocks generation

---

## Key Files Reference

### Validators
- `agentic_core/L5_safety/validators/silent_swallower_validator.py`
- `agentic_core/L5_safety/validators/silent_degradation_validator.py`
- `agentic_core/L5_safety/validators/utility_silent_swallower_validator.py`

### Tests
- `tests/guardian/test_test_silent_skip_detector.py`
- `tests/guardian/test_exemption_recognition.py`
- `tests/guardian/test_agent_autonomy.py`

### Fix Scripts
- `tools/fix/fix_silent_swallowers.py`
- `tools/fix/fix_high_severity_silent_swallowers.py`
- `tools/fix/fix_medium_severity_swallowers.py`
- `tools/fix/fix_low_severity_swallowers.py`
- `tools/fix/ast_silent_swallower_fixer.py`

### Reports
- `tools/silent_swallower_report.json`
- `tools/high_severity_fixes_report.json`
- `tools/medium_severity_fixes_report.json`

### Documentation
- `docs/reference/_primers/Python/Error & Exception Handling.md`
