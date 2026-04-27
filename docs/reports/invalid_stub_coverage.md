# Invalid Stub Detection - Enforcement and Testing

**Date:** 2026-04-06  
**Purpose:** Document all locations where invalid stubs are detected and enforced

## Enforcement Separation of Concerns

**Architectural Preference: ADG-First Enforcement**

**Pre-Commit:** Not applicable (test file analysis too heavy for pre-commit)

**ADG (Primary Enforcement):** P2 (HIGH) - Architectural tracking
- Invalid stubs recorded as P2 (HIGH) in ADG
- Does NOT block ADG generation (only P1 blocks via `_check_p1_defects()`)
- AST analysis of test files during ADG generation
- Purpose: Test quality assurance, architectural insights
- **Primary Enforcement:** ADG is the authoritative source for tracking
- **Blocking:** P2 does NOT block, only P1 blocks ADG generation

**Guardian Fix Scripts:** Historical cleanup only
- Used for one-time cleanup of legacy invalid stubs
- Not for regular enforcement
- ADG generation handles ongoing enforcement automatically

**Rationale:**
- Pre-commit stays fast (seconds) for basic hygiene
- ADG handles heavy architectural analysis (minutes)
- No reliance on ad-hoc guardian scripts
- ADG is comprehensive and catches violations early in development cycle

## Policy Document

**Location:** `docs/reference/_primers/Python/STUB vs SHIM.md`

**Definition:** Invalid stubs are test doubles that only return success paths and don't simulate failures (low fidelity)

**Critical Rule:** A stub must mirror the *Contract*, not just the *Success Path*. If a stub cannot simulate failure, the code depending on it cannot prove resilience.

**Severity:** P2 (HIGH) - Tracked in ADG, does NOT block ADG generation (only P1 blocks)

## Valid vs Invalid Stubs

### Valid Stub ✅ (High Fidelity)
- **Trait:** Mirrors the Contract, handles edge cases
- **Example:**
  - `find("Valid_Book")` → `{ status: 200, data: [...] }`
  - `find("Missing_Book")` → `{ status: 404, error: "None" }`
- **Outcome:** Logic is forced to handle null/errors. System is "Hardened."

### Invalid Stub ❌ (Low Fidelity)
- **Trait:** Masks weakness, only success path
- **Example:**
  - `find("Valid_Book")` → `{ status: 200, data: [...] }`
  - `find("Missing_Book")` → `{ status: 200, data: [...] }` (always success!)
- **Outcome:** Logic assumes data is always present. System crashes in Production.

## Detection Strategy (AST Analysis)

**Target:** Test files (`tests/**/*.py`)

**Detection Patterns:**
1. **Always-Success Returns:** Functions that always return success status codes (e.g., always 200, never 404)
2. **Missing Error Paths:** Mock/stub functions without exception raising or error return branches
3. **Hardcoded Success:** Stub methods that only return successful responses regardless of input
4. **No Timeout Simulation:** Network stubs that don't simulate timeout failures
5. **No Null Simulation:** Database stubs that don't simulate null/empty results

**Heuristics:**
- Mock objects with only `return_value` set (no `side_effect` for errors)
- Stub functions with single return statement (no conditional error paths)
- Test doubles that don't test failure scenarios
- Missing test cases for error conditions in test suite

## ADG Integration

### Anti-Pattern Detection (Tracking Only)
**Location:** ADG generation via AST analysis of test files

**Category:** `antipattern` in ADG violations table

**Severity Mapping:**
- Invalid stub violations → P2 (HIGH) in ADG - tracked only, does NOT block
- **Note:** ADG tracks invalid stubs for test quality insights, but does NOT block generation (only P1 blocks via `_check_p1_defects()`)

**Purpose:** Test quality assurance, architectural insights, trend analysis

**Current State:** To be determined (first implementation)

**Enforcement Flow:**
1. Developer writes test code
2. Pre-commit runs fast checks (syntax, linting, formatting) - seconds
3. Code committed to repository
4. ADG generation runs heavy analysis (AST, architectural checks) - minutes
5. ADG analyzes test files for invalid stub patterns
6. ADG detects violations → Invalid stubs recorded as P2 (HIGH) for tracking
7. ADG continues generation (P2 does NOT block)
8. ADG completes successfully with violation tracking
9. Developer can review violations and fix if needed

## Test Coverage

### Stub Validator Tests
**Location:** To be implemented in `tests/guardian/` or `tests/unit/agentic_core/L5_safety/validators/`

**Test Coverage Needed:**
- Test detection of always-success stubs
- Test detection of missing error paths
- Test detection of hardcoded success returns
- Test detection of missing timeout simulation
- Test detection of missing null simulation
- Test exemption recognition (if whitelist comments are added)

## Fix Scripts (Auto-Run Enforcement)

**Note:** These scripts run automatically after ADG generation completes when P2 violations are detected, not historical cleanup. ADG handles ongoing enforcement automatically.

### Invalid Stub Fixer
**Location:** To be implemented in `tools/fix/fix_invalid_stubs.py`

**Purpose:** Fix invalid stubs by adding error simulation paths (auto-run after ADG generation)

**Detection:**
- Scans test files for invalid stub patterns
- Identifies stubs that only return success
- Reports to `tools/invalid_stub_report.json`

**Fix Actions:**
- Add error return branches to stub functions
- Add exception raising scenarios
- Add timeout simulation for network stubs
- Add null simulation for database stubs
- Add guardian exemptions for legitimate cases (if needed)

**Report:** `tools/invalid_stub_report.json`

**Usage:** Automatically run by ADG generation when P2 violations detected

## Summary Matrix

| Component | Location | Purpose | Severity | Blocking | Status |
|-----------|----------|---------|----------|----------|--------|
| **Policy Doc** | `docs/reference/_primers/Python/STUB vs SHIM.md` | Policy definition | N/A | N/A | ✅ Active |
| **Validator** | `agentic_core/L5_safety/validators/invalid_stub_validator.py` | AST detection of invalid stubs | P2 (HIGH) | ❌ No (tracking only) | ✅ Implemented |
| **ADG Integration** | `agentic_core/L5_safety/validators/anti_pattern_scanner_validator.py` | Unified scanner integration | P2 (HIGH) | ❌ No (tracking only) | ✅ Integrated |
| **Fix Script** | `tools/fix/fix_invalid_stubs.py` | Auto-fix invalid stubs | P2 (HIGH) | N/A (auto-run) | ✅ Implemented |
| **Test Coverage** | `tests/guardian/test_invalid_stub_detector.py` | Test stub validator | N/A | N/A | ✅ Implemented |

## Current Violation State

**Status:** All phases complete - validator fully implemented, integrated, tested, and fix script ready

**Test Results:** All 10 tests passing

**Implementation Status:**
- ✅ Phase 1: Validator Implementation
- ✅ Phase 2: ADG Integration
- ✅ Phase 3: Test Coverage
- ✅ Phase 4: Fix Scripts

## Enforcement Flow

1. **Developer writes test code** → New test added
2. **Pre-commit runs** → Fast checks only (syntax, linting, formatting) - seconds
3. **Commit succeeds** → Code committed to repository
4. **ADG generation runs** → Heavy analysis (AST, architectural checks, test file analysis) - minutes
5. **ADG analyzes test files** → Detects invalid stub patterns
6. **ADG detects violations** → Invalid stubs recorded as P2 (HIGH) for tracking
7. **ADG continues** → ADG generation completes successfully (P2 does NOT block)
8. **Auto-fix scripts run** → Automatically calls `tools/fix/fix_invalid_stubs.py`
9. **Fixes applied** → Invalid stubs automatically fixed with error simulation paths
10. **Developer reviews** → Can review fixes in git diff
11. **Historical cleanup** → Additional fix scripts used for legacy cleanup if needed

**Note:** Only P1 (CRITICAL) blocks ADG generation via `sys.exit(1)` - immediate failure, no partial outputs. P2/P3/P4 are tracked but do NOT block, and P2 automatically triggers fix scripts.

**Key Point:** ADG tracks test quality violations for architectural insights, P2 automatically triggers fix scripts, only P1 blocks generation

## Implementation Recommendations

### Phase 1: Validator Implementation ✅ COMPLETE
1. Create `agentic_core/L5_safety/validators/invalid_stub_validator.py` ✅
2. Implement AST analysis to detect invalid stub patterns ✅
3. Add P2 (HIGH) severity classification ✅
4. Support guardian exemption comments (if needed): `# guardian: allow-invalid-stub` ✅

### Phase 2: ADG Integration ✅ COMPLETE
1. Integrate validator into ADG generation pipeline ✅
2. Add to `anti_pattern_scanner_validator.py` composite detector ✅
3. Ensure violations are recorded in ADG SQLite database ✅
4. Add to routing summary for P2 tracking ✅

### Phase 3: Test Coverage ✅ COMPLETE
1. Create comprehensive test suite for validator ✅
2. Test valid stub patterns (should not trigger) ✅
3. Test invalid stub patterns (should trigger) ✅
4. Test exemption recognition ✅

**Test Coverage:**
- `test_category` - Validates category assignment
- `test_detects_invalid_stub_single_return` - Detects single return invalid stubs
- `test_detects_invalid_stub_multiple_unconditional_returns` - Detects multiple unconditional returns
- `test_valid_stub_with_error_return` - Validates stubs with error returns
- `test_valid_stub_with_raise` - Validates stubs that raise exceptions
- `test_whitelist_comment` - Tests guardian exemption comments
- `test_non_stub_function_ignored` - Ignores non-stub functions
- `test_scan_file_only_tests` - Tests file filtering (test_ prefix)
- `test_scan_file_in_tests_directory` - Tests file filtering (tests/ directory)
- `test_suggested_fix_generation` - Validates fix suggestion generation

**Result:** All 10 tests passing

### Phase 4: Fix Scripts ✅ COMPLETE
1. Implement `tools/fix/fix_invalid_stubs.py` ✅
2. Add automated fix suggestions ✅
3. Support manual review and approval (dry-run mode) ✅
4. Track cleanup progress (summary output) ✅

**Fix Script Features:**
- Scans test files for invalid stubs using the validator
- Dry-run mode to preview changes without applying them
- Apply mode to automatically add error simulation to invalid stubs
- Syntax validation before applying fixes
- Respects guardian exemption comments
- Progress tracking with summary output

**Usage:**
```bash
# Preview changes (dry-run)
python tools/fix/fix_invalid_stubs.py --dry-run --directory tests/guardian

# Apply fixes
python tools/fix/fix_invalid_stubs.py --apply --directory tests/guardian

# Scan all test files
python tools/fix/fix_invalid_stubs.py --dry-run
```

## Key Files Reference

### Policy
- `docs/reference/_primers/Python/STUB vs SHIM.md`

### Validators
- `agentic_core/L5_safety/validators/invalid_stub_validator.py` ✅
- `agentic_core/L5_safety/validators/anti_pattern_scanner_validator.py` ✅

### Tests
- `tests/guardian/test_invalid_stub_detector.py` ✅

### Fix Scripts
- `tools/fix/fix_invalid_stubs.py` ✅

### Reports (To be implemented)
- `tools/invalid_stub_report.json` ⚠️
