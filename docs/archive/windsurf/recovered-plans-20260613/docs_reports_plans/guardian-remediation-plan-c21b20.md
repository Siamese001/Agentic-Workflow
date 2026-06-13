# Guardian Violations Remediation Plan

Phased implementation plan to remediate 6 failing guardians identified in the dry run, addressing 228 import violations, 30 empty folders, 4 misplaced files, and structural compliance issues.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Violation Summary

| Guardian | Status | Violations |
|----------|--------|------------|
| architecture_governance | FAIL | 228 upward import violations |
| classification_compliance | FAIL | 73 misclassified files |
| drift_detection | FAIL | 1 forbidden root folder (`logs`) |
| hierarchy_compliance | FAIL | 13 non-approved subfolders, 1 missing directory |
| hygiene | FAIL | 30 empty folders, scan budget exceeded |
| location_alignment | FAIL | 4 misplaced files, 2 missing sovereign roots |
| manifest_integrity | PASS | Skipped (no manifest.json) |

---

## Phase 1: Quick Wins (Low Risk, High Impact)

**Scope**: Remove/relocate trivial violations that don't require code changes.

### 1.1 Remove Empty Folders (30 folders)
- Delete empty directories in `agentic_core/L0_maintenance/`
- Delete empty cache directories in `apps_shared/types/cache/`
- Delete empty test scaffold directories
- **Estimated files**: 0 code changes, 30 directory deletions

### 1.2 Remove Misplaced Backup Files (4 files)
- Move `.backup/test_illegal_root_file.py.bak` → `archives/`
- Move `.backup/test_shallow.py.bak` → `archives/`
- Move `agentic_core/prompt_governance/registry/backups/registry.v1.backup` → `archives/`
- Evaluate `tests/conftest.py` placement (may be intentional)

### 1.3 Remove Forbidden Root Folder
- Delete or relocate `logs/` folder at repository root

### 1.4 Create Missing Sovereign Roots
- Create `.gravity_state/` directory with `.gitkeep`
- Create `dev_tools/` directory with `.gitkeep`

**Phase 1 Deliverables**:
- 30 empty folders removed
- 3-4 backup files relocated
- 2 missing directories created
- 1 forbidden folder removed

---

## Phase 2: Hierarchy Compliance (Medium Risk)

**Scope**: Address non-approved subfolders and missing structure.

### 2.1 Evaluate Non-Approved Subfolders (13 folders)
Review and decide disposition for each:

| Folder | Layer | Action |
|--------|-------|--------|
| `engines/` | L0_routing | Rename to `reasoning/` or add to allowlist |
| `meta_control/` | L0_routing | Rename to approved folder or add to allowlist |
| `policy/` | L0_routing | Rename to `config/` or add to allowlist |
| `engines/` | L1_cognition | Rename to `reasoning/` or add to allowlist |
| `engines/` | L2_execution | Rename to `reasoning/` or add to allowlist |
| `healers/` | L2_execution | Add to allowlist (domain-specific) |
| `scripts/` | L2_execution | Move contents to L0_routing/scripts |
| `engines/` | L3_orchestration | Rename to `reasoning/` or add to allowlist |
| `caching/` | L4_state | Rename to `utils/` or add to allowlist |
| `security/` | L5_safety | Rename to `enforcement/` or add to allowlist |
| `engines/` | L6_observability | Rename to `reasoning/` or add to allowlist |
| `golden_evaluation/` | L6_observability | Add to allowlist (domain-specific) |
| `enforcement/` | L7_meta_learning | Already approved (verify) |

### 2.2 Fix Missing Directory
- Create `agentic_core/L0_routing/logs/` or update blueprint to remove requirement

**Phase 2 Deliverables**:
- 13 subfolder dispositions resolved
- Blueprint config updated if adding allowlist entries
- Import paths updated if renaming folders

---

## Phase 3: Classification Compliance (Medium-High Risk)

**Scope**: Relocate 73 misclassified files to correct LCD folders.

### 3.1 L5_safety/enforcement Misclassifications (20+ files)
Files currently in `enforcement/` that should be elsewhere:

| File | Current | Target | Type |
|------|---------|--------|------|
| `airlock_trimmer.py` | enforcement | scripts | SCRIPT |
| `archival_gatekeeper.py` | enforcement | utils | SERVICE |
| `artifact_emission_prohibition.py` | enforcement | utils | UTILITY |
| `circular_import_fixer.py` | enforcement | scripts | SCRIPT |
| `context_session_manager.py` | enforcement | utils | SERVICE |
| `fast_dashboard_e2_e_pipeline.py` | enforcement | reasoning | ORCHESTRATOR |
| `final_airlock_trimmer.py` | enforcement | scripts | SCRIPT |
| `hardcoded_path_refactorer.py` | enforcement | scripts | SCRIPT |
| `input_validation_guardrail.py` | enforcement | reasoning | AGENT |
| `mission_utils.py` | enforcement | utils | UTILITY |
| `module_collision_guard.py` | enforcement | scripts | SCRIPT |
| `mutation_prohibition.py` | enforcement | utils | UTILITY |
| `namespace_medic.py` | enforcement | scripts | SCRIPT |
| `process_guard.py` | enforcement | utils | SERVICE |
| `pytest_config_guard.py` | enforcement | config | CONFIG |
| `rg_execution_safety_enforcer.py` | enforcement | utils | UTILITY |
| `safe_subprocess_handler.py` | enforcement | utils | UTILITY |
| `ssot_import_enforcer.py` | enforcement | scripts | SCRIPT |
| `toxic_dependency_auditor.py` | enforcement | reasoning | AGENT |
| `verification_gate.py` | enforcement | reasoning | AGENT |

### 3.2 L5_safety/utils Misclassifications (14 files)
Scripts incorrectly in `utils/`:
- Move `*_util.py` scripts to `scripts/` folder
- Move `subprocess_security_util.py` to `types/` (EXCEPTION type)

### 3.3 Other Layer Misclassifications
- L6_observability/enforcement → utils (2 files)
- L5_safety/validators → utils/scripts (2 files)
- L5_safety/types → utils (1 file)

**Phase 3 Deliverables**:
- 73 files relocated to correct LCD folders
- All import statements updated
- Tests verified passing

---

## Phase 4: Import Compliance (High Risk, High Effort)

**Scope**: Fix 228 upward import violations (lower layers importing from higher layers).

### 4.1 Analyze Import Patterns
Most violations are L0 → L5 imports:
- `mutation_prohibition` (most common)
- `structure_blueprint_config`
- Various L5 agents/validators

### 4.2 Strategy Options

**Option A: Move Shared Code Down**
- Move `mutation_prohibition.py` to L0 (if it has no L5+ dependencies)
- Move `structure_blueprint_config.py` to L0 (if possible)
- Pros: Fixes violations at source
- Cons: May create new violations, large refactor

**Option B: Create L0 Interfaces**
- Define interfaces/protocols in L0
- Implement in higher layers
- Use dependency injection
- Pros: Clean architecture
- Cons: Significant refactor

**Option C: Allowlist Known Violations**
- Document architectural exceptions
- Add to guardian allowlist
- Pros: Quick fix
- Cons: Technical debt, doesn't fix root cause

**Option D: Hybrid Approach (Recommended)**
1. Move truly shared utilities to L0 (mutation_prohibition, etc.)
2. Create interfaces for agent dependencies
3. Allowlist remaining justified violations with documentation

### 4.3 Priority Files for Refactoring
Top 10 files with most violations:
1. `execute_ssot.py` - 15+ violations
2. `colors.py` - 8+ violations
3. `SSOTFolderCleanupAgent.py` - 5+ violations
4. `forward_rolling_facade.py` - 5+ violations
5. `agent_validation_util.py` - 3+ violations

**Phase 4 Deliverables**:
- Import violation count reduced by 80%+
- Shared utilities relocated to appropriate layers
- Remaining violations documented and allowlisted

---

## Phase 5: Validation & Hardening

### 5.1 Run Full Guardian Suite
```powershell
$env:V15_TEST_SIGNING="1"
python -m agentic_core.L0_routing.scripts.run_all_guardians --format json
```

### 5.2 Run Full Test Suite
```powershell
python -m pytest tests/ -v --tb=short
```

### 5.3 Update Baselines
- Refresh drift detection baseline
- Update classification compliance baseline
- Document any remaining allowlisted violations

### 5.4 Add CI Enforcement
- Ensure guardian checks run in CI pipeline
- Set up ratchet mechanism to prevent regression

**Phase 5 Deliverables**:
- All 7 guardians passing
- Full test suite green
- CI enforcement active

---

## Phase 6: Test Structure Mirroring (New Guardian)

**Scope**: Create a new guardian to ensure `tests/unit` mirrors the repository structure for proper test coverage.

### 6.1 Current State Analysis
`tests/unit` currently has:
- `agentic_core/` (401 items) ✓ Mirrors source
- `apps_lic/` (122 items) ✓ Mirrors source
- `apps_rg/` (131 items) ✓ Mirrors source
- `apps_shared/` (128 items) ✓ Mirrors source
- Missing: `ops_scripts/` tests
- Extra: `consolidation/`, `dedup/`, `docs/`, `file_classification_agent/`, `structure_blueprint/` (test-specific)

### 6.2 Create New Guardian: `test_structure_mirroring`

**File**: `tests/guardian/test_test_structure_mirroring.py`

**Checks to implement**:
1. **source_mirroring**: Ensure each source directory has corresponding test directory
2. **orphan_tests**: Flag test directories without corresponding source
3. **coverage_completeness**: Warn about source directories without tests

**Source directories to check**:
```
agentic_core/     → tests/unit/agentic_core/ ✓
apps_lic/         → tests/unit/apps_lic/ ✓
apps_rg/          → tests/unit/apps_rg/ ✓
apps_shared/      → tests/unit/apps_shared/ ✓
ops_scripts/      → tests/unit/ops_scripts/ ❌ Missing
data/             → N/A (data files, no code)
docs/             → N/A (documentation)
archives/         → N/A (archived files)
artifacts/        → N/A (build artifacts)
system_learning/  → tests/unit/system_learning/ ❌ Missing
```

### 6.3 Guardian Implementation Structure

```python
class TestStructureMirroring:
    """Ensures tests/unit mirrors repository structure for comprehensive coverage."""

    def test_source_directories_have_tests(self):
        """Check each source directory has corresponding test directory."""

    def test_no_orphan_test_directories(self):
        """Flag test directories without corresponding source (except allowlisted)."""

    def test_coverage_completeness_report(self):
        """Generate report of source directories missing test coverage."""
```

### 6.4 Allowlisted Test-Only Directories
These test directories don't need source mirrors:
- `consolidation/` - Test consolidation utilities
- `dedup/` - Deduplication test utilities
- `docs/` - Documentation tests
- `file_classification_agent/` - Specific agent tests
- `structure_blueprint/` - Blueprint validation tests
- `core/` - Core test utilities
- `utils/` - General test utilities

### 6.5 Add to Guardian Registry
Update `guardian_registry.py` to include:
```python
GuardianSpec(
    guardian_id="test_structure_mirroring",
    entrypoint_module="tests.guardian.test_test_structure_mirroring",
    entrypoint_fn="TestStructureMirroring",
    check_ids=["source_mirroring", "orphan_tests", "coverage_completeness"],
    tier="structural",
    enabled_by_default=True,
)
```

**Phase 6 Deliverables**:
- New guardian test file created
- Guardian registry updated
- Initial run identifies missing `ops_scripts/` and `system_learning/` test directories
- Coverage report generated

---

## Risk Assessment

| Phase | Risk | Mitigation |
|-------|------|------------|
| Phase 1 | Low | No code changes, easily reversible |
| Phase 2 | Medium | May require import updates |
| Phase 3 | Medium-High | Many file moves, import updates |
| Phase 4 | High | Core architecture changes |
| Phase 5 | Low | Validation only |
| Phase 6 | Low | New guardian, no breaking changes |

## Estimated Effort

| Phase | Files | Effort |
|-------|-------|--------|
| Phase 1 | ~35 | 1- |
| Phase 2 | ~15 | 2- |
| Phase 3 | ~75 | 4- |
| Phase 4 | ~100+ | 8- |
| Phase 5 | 0 | 1- |
| Phase 6 | 2-3 | 2- |

**Total**: 18- of focused work

## Recommended Approach

1. **Start with Phase 1** - Quick wins, immediate impact
2. **Phase 2 & 3 together** - Related structural changes
3. **Phase 4 incrementally** - Break into sub-phases by layer
4. **Phase 5 after each phase** - Validate continuously
5. **Phase 6 anytime** - New guardian can be added independently

---

## Questions for User

1. **Phase 2**: Should non-approved subfolders be renamed or added to allowlist?
2. **Phase 4**: Preferred strategy for import violations (A, B, C, or D)?
3. **Scope**: Should all phases be implemented, or prioritize specific ones?
4. **Timeline**: Any deadline constraints?

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

