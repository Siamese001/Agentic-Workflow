# Guardian Test Refactoring Plan for SSOT Updates

The guardian tests need refactoring to align with the new constitutional principles and structural definitions added to `structure_blueprint_config.py`.

## Key SSOT Updates to Address

### 1. Constitutional Design Principles (Lines 11-42)
Three new constitutional principles were added:

**STRICT OBSOLESCENCE PROTOCOL (2026-02-04)**
- No file deletion based on naming conventions
- Requires AST-based zero-reference verification
- Fuzzy matching for renamed/moved modules
- Manual verification before deletion

**TEST LAYERING PRINCIPLE (2026-02-04)**
- Guardian tests = Architectural compliance validation only
- Unit/E2E/Integration tests = Functional correctness
- Guardian tests are COMPLEMENTARY, not replacements
- Do NOT fulfill 100% coverage requirements

**STRUCTURAL INVARIANT (2026-02-05)**
- Files allowed ONLY in leaf nodes (directories with no subfolders)
- Branch nodes must contain ONLY subdirectories
- Exceptions: `__init__.py`, `README.md`, `.gitignore`, `pyproject.toml`, `py.typed`

### 2. Guardian Constitutional Rules (Lines 296-304)
New `constitutional_rules` array in tests/guardian territory definition:
- Guardian tests are COMPLEMENTARY to unit/e2e tests, NOT replacements
- Guardian validates architectural compliance, NOT functional correctness
- Guardian tests do NOT fulfill 100% coverage requirements
- Guardian tests use AST-based analysis, NEVER string regex
- Guardian tests NEVER delete files based on filename patterns

### 3. New SSOT Constants
- `PROJECT_ROOT_WHITELIST` (Line 1539): Replaces old `ROOT_WHITELIST`
- `ROOT_ALLOWED_PATTERNS` (Line 1560): Regex patterns for allowed root files
- `FORBIDDEN_ROOT_FOLDERS` (Line 1616): Explicitly forbidden folders
- `TESTS_ROOT_FILE_WHITELIST` (Line 1619): Allowed test files at root
- `GLOBAL_EXCLUDED_DIRS` (Line 1813): Production lens exclusions

## Guardian Tests Requiring Refactoring

### High Priority - Direct SSOT Dependencies

**1. test_ssot_compliance.py** (20 SSOT references)
- Currently imports: `FORBIDDEN_ROOT_FOLDERS`, `ROOT_WHITELIST`, `SOVEREIGN_TERRITORIES`
- **Action**: Update to use `PROJECT_ROOT_WHITELIST` instead of `ROOT_WHITELIST`
- **Action**: Add validation for `ROOT_ALLOWED_PATTERNS`
- **Action**: Add validation for `TESTS_ROOT_FILE_WHITELIST`
- **Action**: Verify constitutional principles are enforced

**2. test_ssot_alignment.py** (16 SSOT references)
- Dynamically loads structure_blueprint.py
- **Action**: Add loading of new constitutional principles
- **Action**: Add validation for `STRUCTURAL_INVARIANT` (leaf node enforcement)
- **Action**: Update to check `PROJECT_ROOT_WHITELIST`
- **Action**: Add test for `ROOT_ALLOWED_PATTERNS` compliance

**3. test_obsolete_functionality_detection.py** (2 SSOT references)
- Already references STRICT OBSOLESCENCE PROTOCOL and TEST LAYERING PRINCIPLE
- **Action**: Verify implementation matches constitutional principles
- **Action**: Add explicit test for STRUCTURAL INVARIANT violations
- **Action**: Ensure phase file detection doesn't violate "no filename pattern deletion" rule

### Medium Priority - Indirect SSOT Dependencies

**4. test_comprehensive_structure.py** (9 SSOT references)
- Uses `VALID_TERRITORIES`, `FORBIDDEN_PATTERNS`
- **Action**: Update to validate STRUCTURAL INVARIANT (branch vs leaf nodes)
- **Action**: Add check for files in branch nodes (should only be exceptions)
- **Action**: Verify against `PROJECT_ROOT_WHITELIST`

**5. test_architecture_governance.py**
- Validates layer boundaries and naming conventions
- **Action**: Add validation that guardian tests don't check functional correctness
- **Action**: Ensure gravity violation checks respect constitutional principles
- **Action**: Add STRUCTURAL INVARIANT enforcement

**6. test_mro_integrity.py** (6 SSOT references)
- MRO and inheritance validation
- **Action**: Verify base agents respect STRUCTURAL INVARIANT
- **Action**: Ensure validation is architectural, not functional

### Low Priority - Alignment Checks

**7. test_import_safety.py** (4 SSOT references)
- Import validation and safety checks
- **Action**: Align with STRICT OBSOLESCENCE PROTOCOL
- **Action**: Ensure AST-based analysis only

**8. test_manual_verification.py** (3 SSOT references)
- Manual verification workflows
- **Action**: Update to reference constitutional principles
- **Action**: Add STRUCTURAL INVARIANT checks

**9. test_orphan_agent_detection.py** (1 SSOT reference)
- Orphan file detection
- **Action**: Ensure follows STRICT OBSOLESCENCE PROTOCOL
- **Action**: No deletion based on filename patterns

**10. guardian_report.py** (8 SSOT references)
- Report generation infrastructure
- **Action**: Add violation codes for constitutional principle violations
- **Action**: Add STRUCTURAL_INVARIANT violation type
- **Action**: Add PROJECT_ROOT_WHITELIST violation type

## Implementation Strategy

### Phase 1: Update Core SSOT Validators (High Priority)
1. Update `test_ssot_compliance.py` to use new constants
2. Update `test_ssot_alignment.py` to load and validate new principles
3. Verify `test_obsolete_functionality_detection.py` compliance

### Phase 2: Add STRUCTURAL INVARIANT Enforcement (Medium Priority)
1. Create new validator for branch vs leaf node enforcement
2. Add to `test_comprehensive_structure.py`
3. Add to `test_architecture_governance.py`

### Phase 3: Align Remaining Tests (Low Priority)
1. Update import safety and manual verification tests
2. Update orphan detection to follow STRICT OBSOLESCENCE PROTOCOL
3. Update guardian report infrastructure

### Phase 4: Add Constitutional Compliance Tests
1. Create new test: `test_constitutional_compliance.py`
2. Validate all three constitutional principles
3. Ensure guardian tests don't violate their own rules

## Expected Outcomes

After refactoring:
- ✅ All guardian tests reference `PROJECT_ROOT_WHITELIST` instead of deprecated `ROOT_WHITELIST`
- ✅ STRUCTURAL INVARIANT enforced (files only in leaf nodes)
- ✅ STRICT OBSOLESCENCE PROTOCOL validated (no filename-based deletion)
- ✅ TEST LAYERING PRINCIPLE enforced (guardian = architectural, not functional)
- ✅ Constitutional rules from SSOT are programmatically validated
- ✅ Guardian tests emit signed artifacts for all constitutional violations
- ✅ No guardian test performs functional correctness validation

## Risk Mitigation

**Breaking Changes:**
- `ROOT_WHITELIST` → `PROJECT_ROOT_WHITELIST` (name change)
- New validation rules may flag existing files as violations

**Mitigation:**
- Run full guardian test suite after each phase
- Document all violations found
- Provide remediation scripts for violations
- Ensure backward compatibility where possible
