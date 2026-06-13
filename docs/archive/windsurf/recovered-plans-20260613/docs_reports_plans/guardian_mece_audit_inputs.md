# Guardian MECE Audit — Authoritative Inputs

> Generated deterministically from source files.
> Every claim below is evidenced by file path and line number.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## 1. Full Inventory of Guardian Tests

**Source**: `pytest --collect-only -q tests/guardian` → 503 tests collected.
**Raw artifact**: `docs/reports/plans/guardian_test_inventory_raw.txt`

### 1.1 Test Files (44 files)

| # | File | Test Classes / Functions | Test Count |
|---|------|------------------------|------------|
| 1 | `test_agent_autonomy.py` | `TestAgentAutonomy` (8), `test_required_methods` (1) | 9 |
| 2 | `test_agent_validation.py` | `TestAgentValidation` (8) | 8 |
| 3 | `test_aggregator_invariants.py` | `TestDeterministicOrdering` (2), `TestCorrelationIdPropagation` (3), `TestRollupPrecedence` (3), `TestPerGuardianMetadata` (3), `TestAggregateArtifactContract` (2), `TestArtifactIndex` (7), `TestDisabledGuardianExclusion` (4) | 24 |
| 4 | `test_ai_checking_ai_compliance.py` | `test_ai_checking_ai_compliance` (1) | 1 |
| 5 | `test_anti_patterns.py` | `TestSilentSwallowerDetector` (5), `TestTypeErasureDetector` (5), `TestPathFragilityDetector` (4), `TestMagicConfigDetector` (4), `TestGlobalMutationDetector` (4), `TestCompositeDetector` (2), `TestAntiPatternIntegration` (3) | 27 |
| 6 | `test_architecture_governance.py` | `TestArchitectureGovernance` (8) | 8 |
| 7 | `test_artifact_class_enum_ratchet.py` | 4 module-level functions | 4 |
| 8 | `test_behavioral_coverage_ratchet.py` | `TestCheckIdCoverage` (2 parametrized), `TestPassFailScenarios` (4 parametrized), `TestDisabledGuardianSmokeCoverage` (2 parametrized), `TestStatusPromotionCoverage` (2) | 10 |
| 9 | `test_code_quality_metrics.py` | `TestCodeQualityMetrics` (4) | 4 |
| 10 | `test_conftest_ignore_policy.py` | `TestIgnoreListGovernance` (4), `TestIgnoreListExpiration` (3) | 7 |
| 11 | `test_contract_compatibility.py` | `TestSchemaSnapshot` (5), `TestCheckKeySnapshot` (2), `TestArtifactKeySnapshot` (2), `TestCompatibilityGate` (4), `TestVersionBump` (3), `TestJsonSchemaValidation` (6), `TestEnumValueLocking` (4), `TestSyntheticBreakingChange` (3), `TestPathValidation` (3), `TestSchemaPolicyEnforcement` (4), `TestSchemaBoundsEnforcement` (6), `TestSchemaBoundsConstantsLocked` (4), `TestEvidenceDepthEnforcement` (4), `TestAggregateOnlyIndexEnforcement` (6) | 56 |
| 12 | `test_core_components.py` | `TestCoreComponents` (6), `test_critical_files_exist` (1) | 7 |
| 13 | `test_folder_purity_hardening.py` | `TestCompoundSuffixRegression` (6), `TestValidatorsFolderPurity` (1), `TestUtilsFolderPurity` (1), `TestTypesFolderPurity` (1), `TestEnforcementFolderPurity` (1), `TestDualTagConflictDetection` (7), `TestClassifyFileFolderContext` (3), `TestEnforcementRouting` (3), `TestRuntimeTypesPurity` (3), `TestFolderPurityConfig` (7) | 33 |
| 14 | `test_forensic_audit_unified.py` | `TestUnifiedForensicAudit` (5), `test_forensic_audit_comprehensive` (1) | 6 |
| 15 | `test_guardian_aggregation.py` | `TestCleanAggregation` (3), `TestDirtyAggregation` (3), `TestDeterministicOrdering` (2), `TestMetrics` (3), `TestSchemaCompliance` (3), `TestArtifactWriting` (1) | 15 |
| 16 | `test_guardian_contract.py` | `TestSchemaValidity` (4), `TestPathNormalization` (6), `TestStatusPromotion` (4), `TestSerializationRoundTrip` (6), `TestValidation` (6) | 26 |
| 17 | `test_guardian_contract_gate_scope.py` | 6 module-level, `TestNonVacuousContractGate` (5), `TestSyntheticRegistryFlip` (2), `TestSemanticCoverageEnforcement` (4) | 17 |
| 18 | `test_guardian_hygiene.py` | `TestCleanRepo` (3), `TestDirtyRepo` (5), `TestSchemaCompliance` (4), `TestArtifactWriting` (2), `TestDeterminism` (3), `TestScanFunctions` (4) | 21 |
| 19 | `test_guardian_manifest.py` | `TestMissingManifest` (3), `TestMissingLock` (3), `TestValidManifest` (3), `TestTamperedManifest` (3), `TestSchemaCompliance` (3), `TestDeterminism` (2) | 17 |
| 20 | `test_guardian_meta_coverage.py` | `TestGuardianMetaCoverage` (7) | 7 |
| 21 | `test_guardian_runtime_budget.py` | `TestCeilingConstants` (6), `TestGuardianRuntime` (3), `TestArtifactSize` (4) | 13 |
| 22 | `test_guardian_self_integrity.py` | `TestASTChecks` (8), `TestRealRepoIntegrity` (3), `TestSyntheticViolation` (1), `TestSchemaCompliance` (3) | 15 |
| 23 | `test_import_safety.py` | `TestImportSafety` (4), `TestNuclearImportSweep` (5), `TestGravityCompliance` (3) | 12 |
| 24 | `test_integration.py` | `TestGuardianIntegration` (9), `TestValidatorIntegration` (3) | 12 |
| 25 | `test_l6_signal_contract.py` | `TestL6Constants` (4), `TestArtifactPathContract` (2), `TestCorrelationId` (3), `TestContractDoc` (2), `TestArtifactClass` (7) | 18 |
| 26 | `test_manual_verification.py` | `TestManualVerification` (5) | 5 |
| 27 | `test_mece_naming_compliance.py` | `TestAcronymProtection` (5), `TestSuffixHygiene` (4), `TestTestNamingConventions` (3), `TestMECEComplianceArtifact` (1) | 13 |
| 28 | `test_mro_mixin_order.py` | `TestMROMixinOrder` (5) | 5 |
| 29 | `test_no_xfail_skip_in_contract_gate.py` | `test_no_bypass_constructs_in_guardian_tests` (1), `TestSyntheticBypassDetection` (14) | 15 |
| 30 | `test_obsolete_functionality_detection.py` | `TestObsoleteFunctionalityDetection` (1) | 1 |
| 31 | `test_orphan_agent_detection.py` | `TestOrphanAgentDetection` (3) | 3 |
| 32 | `test_pascal_edge_cases.py` | `TestPascalHardening` (4) | 4 |
| 33 | `test_performance_caps.py` | `TestScanBoundsEnforcement` (3), `TestPerformanceConstantsLocked` (4), `TestBudgetCapHandling` (4) | 11 |
| 34 | `test_registry_completeness.py` | `TestRegistryIsSSoT` (5), `TestGuardianIdPolicy` (1), `TestNoFilesystemFallback` (2), `TestFilesystemDiagnostic` (3) | 11 |
| 35 | `test_regression.py` | `TestDeduplicationRegression` (8), `TestPerformanceRegression` (3), `TestCoverageRegression` (3) | 14 |
| 36 | `test_scan_budget_integrity.py` | `TestScanCapImportDetection` (2), `TestGuardScanBudgetUsage` (2), `TestRuntimeErrorForCapsDetection` (3), `TestAnyExceptionForCapsDetection` (5), `TestEndToEndIntegrityPattern` (3) | 15 |
| 37 | `test_semantic_coverage_quality.py` | `TestAssertionQuality` (6), `TestBehavioralRatchetRequirements` (3) | 9 |
| 38 | `test_ssot_alignment.py` | `TestSSOTAlignment` (6) | 6 |
| 39 | `test_ssot_compliance.py` | `TestSSOTCompliance` (8) | 8 |
| 40 | `test_subatomic_compliance.py` | `TestSubatomicCompliance` (6) | 6 |

### 1.2 Support Files (non-test, in `tests/guardian/`)

| File | Role |
|------|------|
| `__init__.py` | Package marker (empty) |
| `_assertions.py` | `assert_check()`, `assert_guardian_status()`, coverage registry |
| `_contract_gate_ssot.py` | SSOT mappings: guardian_id → test modules, symbols, status assertions |
| `base.py` | `GuardianTestBase`, `AgentTestMixin`, `ValidationResult` |
| `conftest.py` | Marker auto-apply, `collect_ignore_glob`, session fixtures, JSON report hook |
| `guardian_report.py` | `GuardianReportBuilder`, `ViolationCode`, `FixAction` enums, `GuardianReport` |

### 1.3 Ignored Test Files (via `conftest.py` `collect_ignore_glob`)

```
collect_ignore_glob = [
    "test_comprehensive_structure.py",   # TODO(#GUARD-01) missing scripts.validate_structure
    "test_mro_integrity.py",             # TODO(#GUARD-02) missing core_integrity_util module
]
```

**Evidence**: `@tests/guardian/conftest.py:49-52`

---

## 2. Guardian Implementation Surface

### 2.1 Canonical Source Modules

| Module | Role | Imported By |
|--------|------|-------------|
| `agentic_core/L0_maintenance/types/guardian_contract.py` (784 LOC) | **SSOT schema**: `GuardianResult`, `GuardianCheck`, `GuardianArtifact`, enums, JSON Schema, validators, path normalization, scan budget | Nearly all test files |
| `agentic_core/L0_maintenance/types/guardian_registry.py` (149 LOC) | **SSOT registry**: `GuardianSpec`, `ALL_GUARDIANS`, helper functions | `test_aggregator_invariants`, `test_behavioral_coverage_ratchet`, `test_guardian_meta_coverage`, `test_registry_completeness`, `_contract_gate_ssot` |
| `agentic_core/L0_maintenance/scripts/run_guardian_hygiene.py` (347 LOC) | Guardian: hygiene enforcement | `test_guardian_hygiene`, `test_performance_caps` |
| `agentic_core/L0_maintenance/scripts/run_guardian_manifest.py` (227 LOC) | Guardian: manifest integrity | `test_guardian_manifest` |
| `agentic_core/L0_maintenance/scripts/run_guardian_contract_integrity.py` (353 LOC) | Meta-guardian: contract integrity checker | `test_guardian_self_integrity`, `test_scan_budget_integrity` |
| `agentic_core/L0_maintenance/scripts/run_all_guardians.py` (272 LOC) | Aggregator: runs all registered guardians | `test_guardian_aggregation`, `test_guardian_runtime_budget` |
| `agentic_core/L5_safety/config/structure_blueprint.py` | `ROOT_WHITELIST`, `get_validated_project_root()` | Multiple guardian scripts |
| `agentic_core/L5_safety/config/structure_blueprint_config.py` | `SOVEREIGN_TERRITORIES`, `CORE_SUBFOLDER_MAP`, `FORBIDDEN_ROOT_FOLDERS`, `COMPOUND_SUFFIX_CONFLICTS`, `FOLDER_PURITY_RULES` | `test_ssot_compliance`, `test_ssot_alignment`, `test_folder_purity_hardening` |
| `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | File classification logic | `test_pascal_edge_cases` |
| `agentic_core/core/classification_kernel.py` | `classify_file_standalone()` SSOT kernel | Referenced by classification tests |

### 2.2 Test-Internal Infrastructure

| Module | Role |
|--------|------|
| `tests/guardian/guardian_report.py` | `GuardianReportBuilder` (thread-safe singleton), `ViolationCode` (23 codes), `FixAction` (13 actions), `GuardianReport` dataclass |
| `tests/guardian/_assertions.py` | `assert_check()` with quality-gate coverage tracking, `assert_guardian_status()`, `clear_assertion_registry()` |
| `tests/guardian/_contract_gate_ssot.py` | `GUARDIAN_ID_TO_TEST_MODULES`, `GUARDIAN_ID_TO_REQUIRED_TEST_SYMBOLS`, `GUARDIAN_ID_TO_REQUIRED_STATUS_ASSERTIONS`, `CONTRACT_GATE_TEST_MODULES` |
| `tests/guardian/base.py` | `GuardianTestBase` (AST parsing, agent scanning, layer hierarchy), `AgentTestMixin`, `ValidationResult` |

---

## 3. Contracts and Schemas

### 3.1 `GuardianResult` Dataclass

**Source**: `@agentic_core/L0_maintenance/types/guardian_contract.py:604-724`

```
@dataclass
class GuardianResult:
    guardian_id: str
    version: int = CONTRACT_VERSION           # 1
    timestamp: str | None = None
    correlation_id: str | None = None
    status: str = GuardianStatus.PASS.value    # "PASS"
    summary: str = ""
    checks: list[GuardianCheck] = []
    artifacts: list[GuardianArtifact] = []
    metrics: dict[str, int | float] = {}
    remediation_hints: list[str] = []
    index: dict[str, Any] = {}                 # aggregate-only
    artifact_class: str = ArtifactClass.INDIVIDUAL.value  # "individual"
```

### 3.2 Status Enums

| Enum | Values | Source Line |
|------|--------|-------------|
| `GuardianStatus` | `PASS`, `FAIL`, `ERROR` | `guardian_contract.py:30-35` |
| `CheckStatus` | `PASS`, `FAIL`, `SKIP` | `guardian_contract.py:38-43` |
| `ArtifactType` | `diff`, `json`, `log`, `snapshot` | `guardian_contract.py:46-53` |
| `ArtifactClass` | `individual`, `aggregate` | `guardian_contract.py:204-208` |

Frozen enum value sets (version-locked):

```python
GUARDIAN_STATUS_VALUES  = frozenset({"PASS", "FAIL", "ERROR"})
CHECK_STATUS_VALUES     = frozenset({"PASS", "FAIL", "SKIP"})
ARTIFACT_TYPE_VALUES    = frozenset({"diff", "json", "log", "snapshot"})
```

### 3.3 `GuardianReportBuilder` Status Enum (Test-Side)

| Enum | Values | Note |
|------|--------|------|
| `GuardianStatus` (in `guardian_report.py`) | `PASS`, `BLOCKING` | Binary output for test report only — distinct from contract `GuardianStatus` |

### 3.4 `ScanBudgetExceeded` Sentinel

**Source**: `@agentic_core/L0_maintenance/types/guardian_contract.py:270-298`

Returned (not raised) by scan functions when budget caps are breached.

```
class ScanBudgetExceeded:
    cap_name: str
    limit: int
    scanned: int
    details: str       # property
    remediation_hints: list[str]  # property
```

### 3.5 JSON Schema

**Source**: `@agentic_core/L0_maintenance/types/guardian_contract.py:88-179`

`CONTRACT_JSON_SCHEMA` is a JSON Schema 2020-12 definition with:
- `additionalProperties: false` at all levels (top, check, artifact)
- `required`: `guardian_id`, `version`, `status`, `summary`, `checks`, `artifacts`, `metrics`, `remediation_hints`
- Optional: `timestamp`, `correlation_id`, `index`, `artifact_class`
- Check items: `check_id`, `status`, `details`, `evidence` (maxProperties: 30)
- Artifact items: `type`, `path` (no backslashes, no leading `/`), `description`
- Metrics: maxProperties 50
- Index: aggregate-only, entries require `status` + `artifacts`

### 3.6 Schema Bounds Constants

| Constant | Value | Source |
|----------|-------|--------|
| `MAX_METRICS_PROPERTIES` | 50 | `guardian_contract.py:243` |
| `MAX_EVIDENCE_PROPERTIES` | 30 | `guardian_contract.py:244` |
| `MAX_EVIDENCE_DEPTH` | 3 | `guardian_contract.py:245` |
| `MAX_PAYLOAD_BYTES` | 524,288 (512 KB) | `guardian_contract.py:246` |
| `MAX_STRING_VALUE_LENGTH` | 500 | `guardian_contract.py:247` |

### 3.7 Performance Ceiling Constants

| Constant | Value | Source |
|----------|-------|--------|
| `MAX_GUARDIAN_RUNTIME_MS` | 30,000 | `guardian_contract.py:250` |
| `MAX_ARTIFACT_SIZE_KB` | 512 | `guardian_contract.py:251` |
| `MAX_SCAN_DEPTH` | 10 | `guardian_contract.py:252` |
| `MAX_FILES_PER_SCAN` | 10,000 | `guardian_contract.py:255` |
| `MAX_FOLDER_DEPTH` | 10 | `guardian_contract.py:256` |
| `IGNORE_PATTERNS` | `frozenset({".git", "__pycache__", ".pytest_cache", ".nox", "node_modules", ".venv", "venv"})` | `guardian_contract.py:257-267` |

### 3.8 Artifact Filename Patterns

| Pattern | Constant | Use |
|---------|----------|-----|
| `guardian_{guardian_id}_{correlation_id}.json` | `INDIVIDUAL_ARTIFACT_PATTERN` | Per-guardian with correlation |
| `guardian_{guardian_id}_result.json` | `INDIVIDUAL_ARTIFACT_PATTERN_NO_CORR` | Per-guardian without correlation |
| `combined_guardian_{correlation_id}.json` | `AGGREGATE_ARTIFACT_PATTERN` | Aggregate with correlation |
| `combined_guardian_result.json` | `AGGREGATE_ARTIFACT_PATTERN_NO_CORR` | Aggregate without correlation |
| `guardian_{guardian_id}.json` | `GUARDIAN_ARTIFACT_PATTERN` | **Deprecated** |

### 3.9 L6 Contract Constants

| Constant | Value |
|----------|-------|
| `GUARDIAN_ARTIFACT_DIR` | `docs/reports/verification/guardian` |
| `AGGREGATE_GUARDIAN_ID` | `combined` |
| `CONTRACT_VERSION` | `1` |

### 3.10 Contract Schema Snapshot (Frozen Keys)

```python
CONTRACT_SCHEMA_SNAPSHOT = {
    "guardian_id": "str",
    "version": "int",
    "status": "str",
    "summary": "str",
    "checks": "list[dict]",
    "artifacts": "list[dict]",
    "metrics": "dict",
    "remediation_hints": "list[str]",
    "timestamp": "str|None",
    "correlation_id": "str|None",
    "index": "dict",
    "artifact_class": "str",
}
CHECK_SCHEMA_KEYS  = frozenset({"check_id", "status", "details", "evidence"})
ARTIFACT_SCHEMA_KEYS = frozenset({"type", "path", "description"})
```

---

## 4. Guardian Registry / Discovery Artifacts

### 4.1 SSOT Registry

**Source**: `@agentic_core/L0_maintenance/types/guardian_registry.py:53-96`

```
ALL_GUARDIANS: tuple[GuardianSpec, ...] = (sorted by guardian_id)
```

| guardian_id | entrypoint_module | entrypoint_fn | check_ids | tier | enabled_by_default |
|-------------|-------------------|---------------|-----------|------|--------------------|
| `contract_integrity` | `agentic_core.L0_maintenance.scripts.run_guardian_contract_integrity` | `run_contract_integrity_guardian` | `scripts_found`, `imports_contract`, `imports_normalize`, `returns_result` | fast | **False** (meta-guardian) |
| `hygiene` | `agentic_core.L0_maintenance.scripts.run_guardian_hygiene` | `run_hygiene_guardian` | `temp_artifacts`, `empty_folders`, `init_only_folders` | fast | **True** |
| `manifest_integrity` | `agentic_core.L0_maintenance.scripts.run_guardian_manifest` | `run_manifest_guardian` | `manifest_exists`, `lock_exists`, `checksum_match` | fast | **True** |

### 4.2 Enabled vs Disabled

- **Enabled** (run by default aggregator): `hygiene`, `manifest_integrity`
- **Disabled** (run explicitly): `contract_integrity`

### 4.3 Contract Gate Scope

**Source**: `@tests/guardian/_contract_gate_ssot.py:19-106`

**GUARDIAN_ID_TO_TEST_MODULES**:

| guardian_id | Test module(s) |
|-------------|---------------|
| `contract_integrity` | `test_guardian_self_integrity` |
| `hygiene` | `test_guardian_hygiene` |
| `manifest_integrity` | `test_guardian_manifest` |

**CONTRACT_GATE_TEST_MODULES** (9 modules):
`test_artifact_class_enum_ratchet`, `test_behavioral_coverage_ratchet`, `test_core_components`, `test_guardian_contract_gate_scope`, `test_guardian_hygiene`, `test_guardian_manifest`, `test_guardian_self_integrity`, `test_no_xfail_skip_in_contract_gate`, `test_scan_budget_integrity`

### 4.4 `GuardianSpec` Dataclass

```python
@dataclass(frozen=True)
class GuardianSpec:
    guardian_id: str
    entrypoint_module: str
    entrypoint_fn: str
    check_ids: tuple[str, ...]
    tier: Literal["fast", "slow"] = "fast"
    enabled_by_default: bool = True
```

### 4.5 Helper Functions

| Function | Returns |
|----------|---------|
| `get_guardian_specs(enabled_only, tier)` | Filtered tuple of `GuardianSpec` |
| `get_guardian_by_id(guardian_id)` | `GuardianSpec | None` |
| `get_all_check_ids()` | `dict[str, tuple[str, ...]]` |
| `get_guardian_entrypoints()` | `dict[str, tuple[str, str]]` |

---

## 5. Test-to-Check Linkage Evidence

### 5.1 Registry-Derived check_ids per Guardian

#### Guardian: `hygiene`
| check_id | Emitted When | Test Coverage |
|----------|-------------|---------------|
| `temp_artifacts` | `.pyc`/`.pyo`/`.tmp`/`.bak`/`.swp` found | `test_guardian_hygiene.py::TestCleanRepo`, `TestDirtyRepo::test_temp_artifacts_detected` |
| `empty_folders` | Truly empty folders found | `test_guardian_hygiene.py::TestDirtyRepo::test_empty_folders_detected` |
| `init_only_folders` | Folders with only `__init__.py` | `test_guardian_hygiene.py::TestDirtyRepo::test_init_only_folders_detected` |
| `scan_budget_exceeded` | `ScanBudgetExceeded` sentinel returned | `test_performance_caps.py::TestBudgetCapHandling` |

#### Guardian: `manifest_integrity`
| check_id | Emitted When | Test Coverage |
|----------|-------------|---------------|
| `manifest_exists` | `manifest.json` present or absent | `test_guardian_manifest.py::TestMissingManifest`, `TestValidManifest` |
| `lock_exists` | `.manifest.lock` present or absent | `test_guardian_manifest.py::TestMissingLock` |
| `checksum_match` | SHA-256 match/mismatch | `test_guardian_manifest.py::TestValidManifest`, `TestTamperedManifest` |

#### Guardian: `contract_integrity` (disabled)
| check_id | Emitted When | Test Coverage |
|----------|-------------|---------------|
| `scripts_found` | Registry has guardians to check | `test_guardian_self_integrity.py::TestRealRepoIntegrity` |
| `imports_contract_{gid}` | Per-guardian canonical import check | `test_guardian_self_integrity.py::TestASTChecks::test_compliant_imports_contract` |
| `imports_normalize_{gid}` | Per-guardian `normalize_repo_path` import check | `test_guardian_self_integrity.py::TestASTChecks::test_compliant_imports_normalize` |
| `returns_result_{gid}` | Per-guardian return type annotation check | `test_guardian_self_integrity.py::TestASTChecks::test_compliant_returns_guardian_result` |
| `scan_budget_pattern_{gid}` | Scanning guardian uses `guard_scan_budget` correctly | `test_scan_budget_integrity.py` |

### 5.2 Non-Registry Tests (Architectural Invariants)

These tests do not invoke registered guardians but enforce structural invariants:

| Test File | Invariant Category | Key Assertion Target |
|-----------|--------------------|---------------------|
| `test_aggregator_invariants` | Aggregator determinism | Registry order, correlation ID propagation, rollup precedence, index completeness |
| `test_contract_compatibility` | Schema stability | Frozen key snapshots, JSON Schema validation, enum value locking, bounds enforcement |
| `test_guardian_contract` | Result schema validity | Required fields, path normalization, status promotion, serialization round-trip |
| `test_l6_signal_contract` | L6 observability | Constant values, artifact patterns, correlation ID, contract doc existence |
| `test_behavioral_coverage_ratchet` | Coverage completeness | All `check_id`s referenced, PASS+FAIL scenarios per guardian |
| `test_semantic_coverage_quality` | Assertion quality | Only "status + semantic" assertions count toward coverage |
| `test_artifact_class_enum_ratchet` | Enum usage | No `.value` in construction, only in serialization |
| `test_no_xfail_skip_in_contract_gate` | No bypass | AST-scans for forbidden `xfail`/`skip` constructs |
| `test_conftest_ignore_policy` | Ignore governance | Locked allowlist, ticket references, owner tags, expiry dates |
| `test_registry_completeness` | Registry integrity | Importable callables, unique IDs, no filesystem globs |
| `test_guardian_meta_coverage` | Meta coverage | Every registered guardian has test coverage |
| `test_guardian_runtime_budget` | Performance | Runtime < 30s, artifact < 512KB |
| `test_guardian_contract_gate_scope` | Gate scope lock | All SSOT modules present, not ignored, semantic coverage |
| `test_scan_budget_integrity` | Scan budget pattern | AST-detects correct budget enforcement patterns |
| `test_performance_caps` | In-code enforcement | `MAX_FILES_PER_SCAN`, `MAX_FOLDER_DEPTH`, `IGNORE_PATTERNS` |
| `test_ssot_alignment` | Blueprint reality | Paths exist, naming conventions, orphan detection, depth limits |
| `test_ssot_compliance` | SSOT compliance (hardened) | Territory validation, subfolder compliance, layer hierarchy, monolith check |
| `test_subatomic_compliance` | Subatomic rules | ≤2 mixins, ≤2 public methods, naming, layer zoning, file size |
| `test_import_safety` | Import integrity | Syntax validation, circular deps, forbidden imports, `__init__` completeness |
| `test_architecture_governance` | Architecture | Gravity violations, naming conventions |
| `test_mro_mixin_order` | MRO safety | Safety mixins precede base agents |
| `test_anti_patterns` | Code smell detection | Silent swallowing, type erasure, path fragility, magic config, global mutation |
| `test_agent_autonomy` | Agent compliance | `heal_repository` method presence |
| `test_agent_validation` | Agent structure | `__init__`, `run`, `heal`, `test_` methods |
| `test_ai_checking_ai_compliance` | Constitutional | No AI agents validating other AI agents |
| `test_forensic_audit_unified` | Forensic | LLM validation, structural validation, dynamic introspection detection |
| `test_code_quality_metrics` | Quality metrics | File size, complexity, documentation, imports |
| `test_mece_naming_compliance` | Naming | Acronym protection, suffix hygiene, test naming |
| `test_core_components` | Critical files | Existence of critical system files |
| `test_manual_verification` | Detector validation | Synthetic violations detected by subprocess runs |
| `test_orphan_agent_detection` | Agent lifecycle | Unused agent identification, disposition recommendations |
| `test_obsolete_functionality_detection` | Obsolete code | Broken imports, missing functions, phase file consolidation |
| `test_regression` | Dedup regression | Merged files exist, old files removed, functionality preserved |
| `test_integration` | Component integration | Base classes, scanning, AST parsing, validators |
| `test_pascal_edge_cases` | Classification edge cases | Script protection, types immunity, agent suffix enforcement |
| `test_folder_purity_hardening` | Classification hardening | Compound suffixes, folder purity rules, dual-tag conflicts |
| `test_guardian_self_integrity` | Meta-guardian | Real guardians pass integrity checks, synthetic violations caught |

---

## 6. Execution Semantics

### 6.1 Status Lattice

```
ERROR > FAIL > PASS
```

**Promotion rules** (in `GuardianResult.add_check()`):

```python
# @guardian_contract.py:654-656
if status_val == CheckStatus.FAIL.value and self.status != GuardianStatus.ERROR.value:
    self.status = GuardianStatus.FAIL.value
```

- **PASS** → default. Stays PASS only if all checks are PASS or SKIP.
- **FAIL** → promoted when any check is FAIL (unless already ERROR).
- **ERROR** → set explicitly via `set_error()`. Once ERROR, never demoted.
- **SKIP** → does NOT promote top-level status. Used for non-applicable checks.

### 6.2 Aggregator Rollup

**Source**: `@agentic_core/L0_maintenance/scripts/run_all_guardians.py:132-139`

```python
if result.status == GuardianStatus.ERROR.value:
    combined.status = GuardianStatus.ERROR.value
elif result.status == GuardianStatus.FAIL.value:
    if combined.status != GuardianStatus.ERROR.value:
        combined.status = GuardianStatus.FAIL.value
```

Precedence: `ERROR > FAIL > PASS` (locked by `test_aggregator_invariants.py::TestRollupPrecedence`)

### 6.3 Scan Budget Handling

Scanning guardians return `ScanBudgetExceeded` sentinel (not raise exception) → guardian emits **FAIL** (not ERROR) with `check_id="scan_budget_exceeded"` and remediation hints.

### 6.4 Test-Side Status Model (Binary)

`guardian_report.py::GuardianStatus`: `PASS` | `BLOCKING`

- Any `pytest.fail()` → `BLOCKING`
- Used for test report JSON only, not for the guardian contract result.

### 6.5 ViolationCode Enum (23 codes)

Organized by category:
- **MRO**: `MRO_DIAMOND`, `MRO_ORDER`, `MRO_DUPLICATE_MIXIN`
- **Import**: `IMPORT_SYNTAX_ERROR`, `IMPORT_CIRCULAR`, `IMPORT_GHOST`, `IMPORT_LAYER_VIOLATION`
- **SSOT**: `SSOT_TERRITORY`, `SSOT_BASE_AGENT_LOCATION`, `SSOT_INDEPENDENCE`, `SSOT_TEST_PLACEMENT`, `SSOT_LAYER_HIERARCHY`, `SSOT_VOID_COMPLIANCE`, `SSOT_GHOST_FILE`
- **Subatomic**: `SUBATOMIC_MONOLITH`, `SUBATOMIC_MIXIN_LIMIT`, `SUBATOMIC_METHOD_LIMIT`, `SUBATOMIC_NAMING`, `SUBATOMIC_LAYER_ZONING`
- **Forensic**: `FORENSIC_LLM_VALIDATION`, `FORENSIC_STRUCTURAL`, `FORENSIC_INTROSPECTION`
- **Constitutional**: `CONSTITUTIONAL_BASE_AGENT`

---

## 7. Environment Assumptions

### 7.1 conftest.py Policies

**Source**: `@tests/guardian/conftest.py:1-250`

1. **Auto-marker**: All tests in `tests/guardian/` get `pytest.mark.guardian` applied automatically via `pytest_collection_modifyitems`.
2. **Collection ignores**: `collect_ignore_glob` excludes 2 files (`test_comprehensive_structure.py`, `test_mro_integrity.py`) with `TODO` tickets, owner tags, and `review_by` dates.
3. **Report hook**: `pytest_terminal_summary` writes `guardian_report.json` to `agentic_core/L0_maintenance/logs/` using `GuardianReportBuilder` singleton.
4. **Builder reset**: `GuardianReportBuilder.reset()` called after each run for idempotency.
5. **Path injection**: `PROJECT_ROOT` inserted into `sys.path` at import time.

### 7.2 Session-Scoped Fixtures

| Fixture | Scope | Returns |
|---------|-------|---------|
| `agent_registry` | session | Dict of agent files → {file_path, agent_classes, layer} |
| `layer_hierarchy` | session | `{"L0_maintenance": 0, ..., "L6_observability": 6}` |
| `guardian_performance_baseline` | session | `{max_test_time_seconds: 30, max_memory_mb: 100, max_agents_to_scan: 300}` |
| `critical_files` | session | List of 6 critical file paths |
| `territories` | session | `["agentic_core", "apps_lic", "apps_rg", "apps_shared"]` |
| `guardian_session_marker` | session (autouse) | No-op placeholder |

### 7.3 Determinism Rules

1. **No timestamps by default**: `GuardianResult.timestamp` defaults to `None`. Injectable for tests.
2. **Sorted execution**: Aggregator iterates `get_guardian_specs()` which returns `sorted(..., key=lambda s: s.guardian_id)`.
3. **Sorted scan results**: All `scan_*` functions return `sorted(hits)`.
4. **No filesystem globs in aggregator/integrity checker**: Registry-only enumeration (enforced by `test_registry_completeness.py::TestNoFilesystemFallback`).
5. **AST-only analysis**: All structural tests use `ast.parse()` — no runtime code execution of tested modules.

### 7.4 Subprocess Execution

`test_manual_verification.py` is the only test that runs guardian checks as subprocesses via `pytest` invocations. It creates temporary violation files, runs targeted `pytest` commands, and asserts non-zero exit codes.

### 7.5 Quality Assertion Gate

**Source**: `@tests/guardian/_assertions.py:99-103`

Coverage is recorded ONLY when:
1. `status` is asserted (not None), AND
2. At least one semantic property is verified (`details_contains` or `evidence_predicate`)

Empty or status-only assertions do NOT count. Enforced by `test_semantic_coverage_quality.py`.

### 7.6 Contract Gate No-Bypass Rule

**Source**: `test_no_xfail_skip_in_contract_gate.py`

AST-scans all `CONTRACT_GATE_TEST_MODULES` for forbidden constructs:
- `@pytest.mark.xfail`, `@pytest.mark.skip`, `@pytest.mark.skipif`
- `pytest.xfail()`, `pytest.skip()`, `pytest.importorskip()`
- `@unittest.skip`, `@unittest.skipIf`, `@unittest.skipUnless`

---

## Appendix A: File Cross-Reference Index

### Implementation Files → Test Files

| Implementation | Primary Test(s) |
|---------------|-----------------|
| `guardian_contract.py` | `test_guardian_contract`, `test_contract_compatibility`, `test_l6_signal_contract` |
| `guardian_registry.py` | `test_registry_completeness`, `test_guardian_meta_coverage`, `test_behavioral_coverage_ratchet` |
| `run_guardian_hygiene.py` | `test_guardian_hygiene`, `test_performance_caps` |
| `run_guardian_manifest.py` | `test_guardian_manifest` |
| `run_guardian_contract_integrity.py` | `test_guardian_self_integrity`, `test_scan_budget_integrity` |
| `run_all_guardians.py` | `test_guardian_aggregation`, `test_aggregator_invariants`, `test_guardian_runtime_budget` |
| `structure_blueprint_config.py` | `test_ssot_alignment`, `test_ssot_compliance`, `test_folder_purity_hardening` |
| `FileClassificationAgent.py` | `test_pascal_edge_cases` |

### ViolationCode → Test File

| ViolationCode | Asserted In |
|---------------|-------------|
| `MRO_DIAMOND`, `MRO_ORDER`, `MRO_DUPLICATE_MIXIN` | `test_mro_integrity` (ignored), `test_mro_mixin_order` |
| `IMPORT_SYNTAX_ERROR`, `IMPORT_CIRCULAR`, `IMPORT_GHOST`, `IMPORT_LAYER_VIOLATION` | `test_import_safety`, `test_subatomic_compliance` |
| `SSOT_TERRITORY`, `SSOT_INDEPENDENCE`, `SSOT_TEST_PLACEMENT`, `SSOT_LAYER_HIERARCHY`, `SSOT_VOID_COMPLIANCE`, `SSOT_GHOST_FILE` | `test_ssot_compliance` |
| `SSOT_BASE_AGENT_LOCATION` | `test_ssot_alignment` |
| `SUBATOMIC_MONOLITH`, `SUBATOMIC_MIXIN_LIMIT`, `SUBATOMIC_METHOD_LIMIT`, `SUBATOMIC_NAMING`, `SUBATOMIC_LAYER_ZONING` | `test_subatomic_compliance`, `test_ssot_compliance` |
| `FORENSIC_LLM_VALIDATION`, `FORENSIC_STRUCTURAL`, `FORENSIC_INTROSPECTION` | `test_forensic_audit_unified` |
| `CONSTITUTIONAL_BASE_AGENT` | `test_ssot_compliance` |

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

