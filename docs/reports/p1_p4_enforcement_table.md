# P1-P4 Enforcement Table - Comprehensive ADG Review

**Date:** 2026-04-06
**Purpose:** Detailed table of P1-P4 severity levels with enforcement locations throughout the repository

## Summary: P1-P4 Definitions & Enforcement

| Level | Name | Description | Blocks ADG Gen | Blocks Commit | Auto-Fix Timing | Pre-Commit Hooks | ADG Enforcement | Test Coverage | Current Count |
|-------|------|-------------|----------------|---------------|-----------------|------------------|-----------------|---------------|---------------|
| **P1** | CRITICAL | System-breaking or security-critical violations | ✅ YES (fail-fast) | ✅ YES | ✅ Fix scripts run before manual ADG re-run | 7 hooks: T0-guard, T0 (merge conflicts), T1 (syntax), T2-P0 (Ruff CRITICAL), T9 (boundary), T10.6 (ADG unified), T11 (MCP config) | 8 fail-fast checks: `_check_p1_defects()`, layer violations, artifact validity, SQLite integrity, artifact consistency, closure validation, locked files, critical edge coverage (<95%), critical path linkage (>5%) | `test_p1_defects_fail_in_strict_mode()`, `test_no_p1_defects_pass_in_strict_mode()`, `test_p1_defects_ignored_in_non_strict_mode()` | 0 |
| **P2** | HIGH | Bugs or architectural violations | ❌ NO (tracking only) | ✅ YES (via T21 summary reporter) | ✅ Fix scripts run after ADG completion | 11 hooks: T2-P1 (Ruff HIGH), T6 (hollow file), T7 (report SSOT), T7.5 (plan SSOT), T7.7 (governance), T8 (generated artifacts), T10 (module collision), T11.3 (pytest SSOT), T12 (guardian exemption) | `SilentSwallowerDetector`, `InvalidStubDetector` in `anti_pattern_scanner_validator.py` (tracking only — recorded in SQLite, do not block) | `test_severity.py` (SeverityLevel.HIGH tests), `test_pre_commit_summary_reporter.py` | 0 |
| **P3** | MEDIUM | Code quality issues | ❌ NO | ❌ NO | ❌ No auto-fix | 2 hooks (non-blocking): T2-P2 (Ruff MEDIUM), T4 (guardian comment auto-fix) | Code quality metrics in ADG, semantic warnings | `test_severity.py` (SeverityLevel.MEDIUM tests) | 307 ¹ |
| **P4** | LOW | Minor style issues | ❌ NO | ❌ NO | ❌ No auto-fix | 5 hooks (non-blocking): T0 (trailing whitespace, EOF, line endings), T2-P3 (Ruff LOW), T3 (Ruff format) | Semantic enrichment warnings in ADG | `test_severity.py` (SeverityLevel.LOW tests) | 4391 ¹ |

> ¹ Point-in-time counts from ADG snapshot `04062026_0751` — will drift over time.

### Key Enforcement Principles

1. **Only P1 blocks ADG generation** - Via `_check_p1_defects()` in `generate_full_adg.py` with `sys.exit(1)` in strict mode
2. **P2 tracks but does not block** - Violations recorded in ADG SQLite database, fix scripts run post-generation
3. **P2 auto-fix enforcement** - After ADG completes, fix scripts automatically run to rectify P2 violations
4. **Pre-commit blocking** - P1 and P2 block commits via pre-commit hooks; P3 and P4 are warnings only

### Enforcement Flow

```
Developer writes code
    ↓
Pre-commit hooks (fast checks, seconds)
    ├─ P1/P2 violations → BLOCK commit
    └─ P3/P4 violations → WARN, allow commit
    ↓
Commit succeeds
    ↓
ADG generation (comprehensive analysis, minutes)
    ├─ P1 violations → FAIL-FAST, sys.exit(1), run fix scripts
    ├─ P2 violations → TRACK in database, complete generation, run fix scripts
    └─ P3/P4 violations → TRACK for metrics, complete generation
    ↓
Fix scripts run automatically (P1 before retry, P2 after completion)
    ↓
ADG artifacts generated
```

## P1-P4 Enforcement Matrix

| Severity | Description | Impact | Blocks Commit | ADG Category | Pre-Commit Hooks | ADG Enforcement | Test Coverage | Current Count |
|----------|-------------|--------|---------------|--------------|------------------|-----------------|---------------|---------------|
| **P1 (CRITICAL)** | System-breaking or security-critical | Layer violations, security vulnerabilities, PowerShell usage, broken imports | ✅ YES | P1 | T0-guard, T0 (merge conflicts), T1 (syntax), T2-P0 (Ruff CRITICAL), T9 (boundary), T10.6 (ADG unified), T11 (MCP config) | `_check_p1_defects()` in `generate_full_adg.py`, layer violation detection, artifact validity, SQLite integrity, artifact consistency, closure validation, locked files, critical edge coverage (<95%), critical path linkage (>5%) | `test_p1_defects_fail_in_strict_mode()` in `test_generate_full_adg_failfast.py` | 0 |
| **P2 (HIGH)** | Bugs or architectural violations | Unused imports, global mutations, test coverage gaps, deprecated APIs, circular dependencies, silent swallowers, invalid stubs | ✅ YES | P2 | T2-P1 (Ruff HIGH), T6 (hollow file), T7 (report SSOT), T7.5 (plan SSOT), T7.7 (governance), T8 (generated artifacts), T10 (module collision), T11.3 (pytest SSOT), T12 (guardian exemption) | Architectural issue detection in ADG, module collision detection, silent swallower detection (P2 in ADG - tracking only), invalid stub detection (P2 in ADG - tracking only) | `test_severity.py` (SeverityLevel.HIGH tests), `test_pre_commit_summary_reporter.py` | 0 |
| **P3 (MEDIUM)** | Code quality issues | Long functions, complex cyclomatic complexity, inconsistent naming, missing docstrings, TODO comments | ❌ NO | P3 | T2-P2 (Ruff MEDIUM), T4 (guardian comment auto-fix) | Code quality metrics in ADG, semantic warnings | `test_severity.py` (SeverityLevel.MEDIUM tests) | 307 (antipattern) |
| **P4 (LOW)** | Minor style issues | Line length violations, trailing whitespace, missing type hints, unused variables in tests, debug prints | ❌ NO | P4 | T0 (trailing whitespace, EOF, line endings), T2-P3 (Ruff LOW), T3 (Ruff format) | Semantic enrichment warnings in ADG | `test_severity.py` (SeverityLevel.LOW tests) | 4391 (antipattern) |

## Detailed Enforcement Breakdown

### P1 (CRITICAL) - Detailed Breakdown

| Aspect | Details |
|--------|---------|
| **Impact** | Layer violations, security vulnerabilities, PowerShell usage, broken imports |
| **Blocking Behavior** | Blocks ADG generation from starting via `sys.exit(1)` in strict mode |
| **Pre-Commit Hooks** | T0-guard (agent deletion), T0 (merge conflicts), T1 (syntax), T2-P0 (Ruff CRITICAL), T9 (boundary), T10.6 (ADG unified), T11 (MCP config) |
| **ADG Fail-Fast Checks** | `_check_p1_defects()`, artifact validity, SQLite integrity, artifact consistency, closure validation, locked files, critical edge coverage (<95%), critical path linkage (>5%) |
| **Fix Script Timing** | Before ADG generation retry (after fix scripts run) |
| **Example Violations** | Layer gravity violations (L0→L2), security issues (S603, S607, S324), PowerShell in subprocess, missing imports |

### P2 (HIGH) - Detailed Breakdown

| Aspect | Details |
|--------|---------|
| **Impact** | Unused imports, global mutations, test coverage gaps, deprecated APIs, circular dependencies, silent swallowers, invalid stubs |
| **Blocking Behavior** | Does NOT block ADG generation - tracks violations in SQLite database |
| **Pre-Commit Hooks** | T2-P1 (Ruff HIGH), T6 (hollow file), T7 (report SSOT), T7.5 (plan SSOT), T7.7 (governance), T8 (generated artifacts), T10 (module collision), T11.3 (pytest SSOT), T12 (guardian exemption) |
| **ADG Enforcement** | `SilentSwallowerDetector`, `InvalidStubDetector` in `anti_pattern_scanner_validator.py` — tracking only, recorded in SQLite, do not block generation |
| **Fix Script Timing** | After ADG generation completes (automatic rectification) |
| **Fix Scripts** | `tools/fix/fix_silent_swallowers.py`, `tools/fix/fix_high_severity_silent_swallowers.py`, `tools/fix/fix_invalid_stubs.py` (scripts exist on disk; wiring into ADG post-run pipeline is pending) |
| **Exemption Mechanism** | `# guardian: allow-silent-swallow` (silent swallowers), `# guardian: allow-invalid-stub` (invalid stubs) — placed on line immediately before the violation |
| **Example Violations** | Silent swallowers (`except Exception: pass`), invalid test stubs (success-only returns), unused imports, circular dependencies |

### P3 (MEDIUM) - Detailed Breakdown

| Aspect | Details |
|--------|---------|
| **Impact** | Long functions, complex cyclomatic complexity, inconsistent naming, missing docstrings, TODO comments |
| **Blocking Behavior** | Does NOT block ADG generation - tracked for code quality metrics |
| **Pre-Commit Hooks** | T2-P2 (Ruff MEDIUM), T4 (guardian comment auto-fix) - both non-blocking |
| **ADG Enforcement** | Code quality metrics in ADG, semantic warnings |
| **Fix Script Timing** | None (no auto-fix) |
| **Example Violations** | Functions > 50 lines, cyclomatic complexity > 10, missing docstrings on public functions |
| **Current Count** | 307 antipattern violations |

### P4 (LOW) - Detailed Breakdown

| Aspect | Details |
|--------|---------|
| **Impact** | Line length violations, trailing whitespace, missing type hints, unused variables in tests, debug prints |
| **Blocking Behavior** | Does NOT block ADG generation - tracked for style warnings |
| **Pre-Commit Hooks** | T0 (trailing whitespace, EOF, line endings), T2-P3 (Ruff LOW), T3 (Ruff format) - all non-blocking |
| **ADG Enforcement** | Semantic enrichment warnings in ADG |
| **Fix Script Timing** | None (no auto-fix) |
| **Example Violations** | Lines > 100 characters, trailing whitespace, missing type hints, print() statements |
| **Current Count** | 4391 antipattern violations |

## Layer Gravity Violations

### What Are Layer Gravity Violations?
- **Definition:** Lower layers (e.g., L0) cannot import upward (e.g., from L2)
- **Rule:** LN can only import from L0..LN
- **Severity:** P1 (CRITICAL) - Constitutional layer boundary violation

### Enforcement Points
- **ADG Detection:** `agentic_core/L5_safety/utils/gravity_visitor_util.py` - `check_layer_gravity()`
- **Pre-Commit:** T9 - Tooling/Apps Boundary Guard
- **ADG Unified Gate (T10.6):** Layer violation detection via `generate_full_adg.py`
- **Test Coverage:** `tests/e2e/agentic_core/test_layer_sovereignty_e2e.py` - `TestLayerGravity` class

### Key Files
- **SSOT:** `agentic_core/L4_state/utils/layer_gravity_util.py` (LAYER_ORDER, GRAVITY_RULES)
- **Validator:** `agentic_core/L5_safety/validators/gravity_validator.py`
- **Visitor:** `agentic_core/L5_safety/utils/gravity_visitor_util.py`
- **E2E Test:** `tests/e2e/agentic_core/test_layer_sovereignty_e2e.py` (lines 29-137)

### Current State
- **Gravity Violations:** 0 (per ADG snapshot 04062026_0751)
- **Layer Violations:** 0 (per ADG snapshot 04062026_0751)

## Guardian Tests Coverage (tests/guardian)

### Test Files
| Test File | Purpose | Severity Coverage |
|-----------|---------|-------------------|
| `test_agent_autonomy.py` | Agent method compliance (heal_repository, etc.) | P1 (BLOCKING) |
| `test_exemption_recognition.py` | Guardian exemption suppression (line distance) | P1/P2 |
| `test_test_silent_skip_detector.py` | Silent skip detection (severity: error) | P2 (HIGH) |
| `test_guardian_prioritizer.py` | Violation prioritization | P1-P4 |
| `test_core_components.py` | Core component validation | P1-P4 |

### Violation Codes (guardian_report.py)
| Code | Category | Severity |
|------|----------|----------|
| `MRO_DIAMOND` | MRO Violations | BLOCKING (P1) |
| `IMPORT_LAYER_VIOLATION` | Import Violations | BLOCKING (P1) |
| `SSOT_VIOLATION` | SSOT Violations | BLOCKING (P1) |
| `CAPABILITY_VIOLATION` | Capability Violations | BLOCKING (P1) |
| `MUTATION_VIOLATION` | Mutation Violations | BLOCKING (P1) |
| `CONSTITUTIONAL_VIOLATION` | Constitutional Violations | BLOCKING (P1) |

## Severity Conversion Functions

### Ruff to SeverityLevel
| Ruff Category | SeverityLevel | P-Level |
|---------------|---------------|---------|
| P0 | CRITICAL | P0/P1 |
| P1 | HIGH | P1/P2 |
| P2 | MEDIUM | P2/P3 |
| P3 | LOW | P3/P4 |

### ADG to SeverityLevel
| ADG Category | SeverityLevel | P-Level |
|--------------|---------------|---------|
| P1 | CRITICAL | P1 |
| P2 | HIGH | P2 |
| P3 | MEDIUM | P3 |
| P4 | LOW | P4 |

### Legacy String to SeverityLevel
| Legacy String | SeverityLevel | P-Level |
|---------------|---------------|---------|
| CRITICAL, critical, P1, P0 | CRITICAL | P0/P1 |
| HIGH, high, P2, ERROR | HIGH | P1/P2 |
| MEDIUM, medium, P3, WARNING | MEDIUM | P2/P3 |
| LOW, low, P4 | LOW | P3/P4 |
| INFO, passed, skipped | INFO | N/A |

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

## Summary Statistics

### Enforcement Coverage
- **P1 (CRITICAL):** 7 active hooks + 8 ADG fail-fast checks + 6 guardian violation codes
- **P2 (HIGH):** 10 active hooks + ADG architectural detection + ADG silent swallower detection (P2 - tracking only) + ADG invalid stub detection (P2 - tracking only)
- **P3 (MEDIUM):** 2 active hooks (non-blocking) + ADG code quality metrics
- **P4 (LOW):** 5 active hooks (non-blocking) + ADG semantic warnings

### Current ADG State (Snapshot: 04062026_0751)
- **P1 Violations:** 0
- **P2 Violations:** 0
- **P3 Violations:** 307 (antipattern) - Code quality issues (long functions, complexity, etc.)
- **P4 Violations:** 4391 (antipattern) - Style issues (line length, trailing whitespace, etc.)
- **Layer Violations:** 0
- **Gravity Violations:** 0
- **Silent Swallower State:** 30+ files with guardian exemptions, tracked in compliance report (HIGH: 8,468, MEDIUM: 2,379, LOW: 1,715)

### Test Coverage Status
- ✅ SeverityLevel enum: Comprehensive unit tests
- ✅ P1 defects: ADG fail-fast tests
- ✅ Guardian violations: Agent autonomy, exemption recognition, silent skip
- ✅ Layer gravity: E2E tests
- ✅ Pre-commit schema: Issue schema tests
- ⚠️ Threshold enforcement: Recommended for critical edge coverage (<95%) and critical path linkage (>5%)

---

## Enforcement Separation of Concerns

### Architectural Preference: ADG-First Enforcement

**Pre-Commit Hooks:** Lightweight, fast checks (seconds)
- Focus on syntax, formatting, basic linting
- Run on every commit - must be fast
- Examples: T1 (syntax), T2 (Ruff), T3 (formatting), T0 (whitespace)
- **Goal:** Fast feedback loop for developers

**ADG:** Primary enforcement mechanism (minutes)
- Focus on architectural violations, layer boundaries, silent swallowers
- Runs on-demand or in CI - comprehensive and detailed
- **Blocks ADG generation in strict mode for P1 only** (via `_check_p1_defects()`)
- P2/P3/P4 are tracked but do NOT block ADG generation
- Examples: Layer violations (P1), silent swallowers (P2 - tracking only), architectural issues (P2)
- **Goal:** Deep architectural validation and compliance - P1 blocking, P2+ tracking

**Silent Swallower Example:**
- **Pre-Commit:** Removed T4 (guardian) - too heavy
- **ADG:** P2 (HIGH) - tracked in ADG for architectural insights, but does NOT block generation
- **Guardian Fix Scripts:** Historical cleanup only, not regular enforcement
- **Rationale:** ADG is comprehensive and fast enough to catch violations early for tracking

**Why ADG-First Architecture:**
1. **Comprehensive Coverage:** ADG already analyzes entire codebase, leverage it for enforcement
2. **Early Detection:** ADG runs during development cycle, catches violations before they accumulate
3. **No Ad-Hoc Scripts:** Eliminate need to run guardian fix scripts manually
4. **Single Source of Truth:** ADG is the authoritative architectural validation
5. **CI Integration:** ADG in CI provides consistent enforcement across team

**Blocking Behavior:**
- **P1 (CRITICAL):** Blocks ADG generation from even starting via fail-fast checks (artifact validity, SQLite integrity, etc.) + calls fix scripts automatically
- **P2 (HIGH):** Does NOT block ADG generation - completes generation + calls fix scripts to rectify issues
- **P3 (MEDIUM):** Does NOT block ADG generation - tracked for code quality metrics
- **P4 (LOW):** Does NOT block ADG generation - tracked for style warnings
