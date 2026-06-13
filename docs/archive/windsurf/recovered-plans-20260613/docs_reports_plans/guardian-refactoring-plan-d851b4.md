# GUARDIAN FORENSIC HARDENING PROTOCOL (V4.7 COMPLIANCE)

This plan elevates the Guardian suite from "linting" to a **Cryptographically Signed Forensic Audit** as required by Prompt v4.7 Target State V10.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


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
- **AUTHORITY IS TOKENIZED:** All outputs must include SHA-256 signatures [Cap 7.2]
- **DISCOVERY IS ABSOLUTE:** `forensic_discovery_prep.py` JSON is the sole source of truth [Cap 0.1]
- **MUTATION IS SURGICAL:** All fixes must emit `SurgicalManifest` JSON, never raw IO [Cap 1.1]

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
- **Action**: Enforce **Fail-Closed Default** (P1) on `ROOT_ALLOWED_PATTERNS`
- **Action**: Add validation for `TESTS_ROOT_FILE_WHITELIST`
- **Action**: Verify constitutional principles are enforced
- **Action**: [CRITICAL] Validate **Policy Immutability** (Cap 4.2) by hashing `structure_blueprint_config.py` at init vs exit

**2. test_ssot_alignment.py** (16 SSOT references)
- Dynamically loads structure_blueprint.py
- **Action**: Add loading of new constitutional principles
- **Action**: Add validation for `STRUCTURAL_INVARIANT` (leaf node enforcement)
- **Action**: Update to check `PROJECT_ROOT_WHITELIST`
- **Action**: **Bind to Discovery JSON**: Verify Blueprint config matches the *actual* disk state found by Discovery (Cap 0.1)

**3. test_obsolete_functionality_detection.py** (2 SSOT references)
- Already references STRICT OBSOLESCENCE PROTOCOL and TEST LAYERING PRINCIPLE
- **Action**: Verify implementation matches constitutional principles
- **Action**: Add explicit test for STRUCTURAL INVARIANT violations
- **Action**: Ensure phase file detection doesn't violate "no filename pattern deletion" rule
- **Action**: **Ban "Cleaners":** Convert all deletion logic to emit `SurgicalManifest` (Cap 1.1) for external review

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
- **Action**: [CRITICAL] **Enforce Mixin Safety (Cap 8.3):** `Safety*` mixins MUST be index `<` `BaseAgent` in `__bases__`
- **Action**: [CRITICAL] **Ban Adapters (Cap 8.1):** Fail on any class name matching `*Adapter`
- **Action**: [CRITICAL] **Discovery Match (Cap 8.4):** Compare AST MRO signature against Discovery JSON. Mismatch = FAIL.

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
- **Action**: [MANDATORY] **Cryptographic Signing (Cap 7.2):**
  - Input: `timestamp + commit_hash + sorted(violation_vector)`
  - Output: `SHA-256` signature appended to report footer.
  - Rule: No signature = Invalid Report.

## Implementation Strategy

### Phase 0: Forensic Authority Link (Pre-Requisite)
1. Hard-link Guardian to `forensic_discovery_prep.py` output.
2. Fail immediately if Discovery JSON is missing or stale (>10m old).
3. Establish "Golden Hash" of `structure_blueprint_config.py`.

### Phase 1: Structural & Constitutional Hygiene
1. Update `test_ssot_compliance.py` with `PROJECT_ROOT_WHITELIST`.
2. Implement `STRUCTURAL_INVARIANT` (Leaf vs Branch) enforcement.
3. **Deploy MRO Iron Dome:** Update `test_mro_integrity.py` to enforce Cap 8.1 (No Adapters) and 8.3 (Safety Left).

### Phase 2: The "Zero-Loss" Remediation Engine
1. **Deprecate all file deletion/editing functions.**
2. Implement `RemediationManifestFactory` to output standard V10 `SurgicalManifest` JSONs [Cap 1].
3. Ensure `test_obsolete_functionality` produces Manifests, not side-effects.

### Phase 3: Signed Authority & Reporting
1. Upgrade `guardian_report.py` to sign artifacts (SHA-256).
2. Enforce "Artifact Presence" check (Cap 7.3) - Absence of signed artifact = CI Failure.

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

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

