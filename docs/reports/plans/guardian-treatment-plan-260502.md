# Guardian Test Treatment Plan - Individual File-by-File

This plan provides individual treatment recommendations for all 79 guardian test files based on static analysis, ADG similarity mapping, and behavioral content assessment.

---

## Executive Summary

| Action | Count | % of Total |
|--------|-------|------------|
| **DELETE** | 75 | 95% |
| **KEEP** | 4 | 5% |
| **TOTAL** | 79 | 100% |

**Key Evidence:**
- 10 placeholder tests with `assertTrue(True)` — zero behavioral value
- 55 template stubs (29-30 lines) importing nonexistent symbols — no production code coverage
- 4 substantive tests with real assertions, fixtures, and behavioral logic — genuine value

---

## Detailed Treatment Plan (by Category)

### Category 1: PLACEHOLDER — DELETE (10 files)

| # | File | Lines | Tests | Evidence | Treatment |
|---|------|-------|-------|----------|-----------|
| 1 | `test_activation_gate.py` | 33 | 3 | `PlaceholderTest` class, `assertTrue(True)`, `assertEqual(1+1, 2)` | **DELETE** |
| 2 | `test_adg_anomaly_fixes.py` | 33 | 3 | `PlaceholderTest` class, `assertTrue(True)`, `assertEqual(1+1, 2)` | **DELETE** |
| 3 | `test_adg_graph_coverage_guardian.py` | 33 | 3 | `PlaceholderTest` class, `assertTrue(True)`, `assertEqual(1+1, 2)` | **DELETE** |
| 4 | `test_agent_capability_limits.py` | 33 | 3 | `PlaceholderTest` class, `assertTrue(True)`, `assertEqual(1+1, 2)` | **DELETE** |
| 5 | `test_agent_registry_hardened.py` | 33 | 3 | `PlaceholderTest` class, `assertTrue(True)`, `assertEqual(1+1, 2)` | **DELETE** |
| 6 | `test_agent_validation.py` | 33 | 3 | `PlaceholderTest` class, `assertTrue(True)`, `assertEqual(1+1, 2)` | **DELETE** |
| 7 | `test_ai_checking_ai_compliance.py` | 33 | 3 | `PlaceholderTest` class, `assertTrue(True)`, `assertEqual(1+1, 2)` | **DELETE** |
| 8 | `test_all_active_agents_have_heal.py` | 33 | 3 | `PlaceholderTest` class, `assertTrue(True)`, `assertEqual(1+1, 2)` | **DELETE** |
| 9 | `test_anti_patterns.py` | 33 | 3 | `PlaceholderTest` class, `assertTrue(True)`, `assertEqual(1+1, 2)` | **DELETE** |
| 10 | `test_architecture_governance.py` | 33 | 3 | `PlaceholderTest` class, `assertTrue(True)`, `assertEqual(1+1, 2)` | **DELETE** |

**Evidence for DELETE:**
- Zero behavioral assertions (only tautological `True` and `1+1=2`)
- No imports from production code
- No coverage of production symbols (ADG: 0 edges)
- Similarity score to existing tests: <0.10 (name-only)

---

### Category 2: TEMPLATE_STUB — DELETE (55 files)

**Pattern:** All 29-30 line files with identical structure:
```python
from agentic_core import {symbol_name}  # NEVER EXISTED
assert {symbol_name} is not None
```

| # | File | Lines | Import Symbol | Exists? | Treatment |
|---|------|-------|---------------|---------|-----------|
| 11 | `test_artifact_class_enum_ratchet.py` | 30 | `artifact_class_enum_ratchet` | ❌ No | **DELETE** |
| 12 | `test_behavioral_coverage_ratchet.py` | 30 | `behavioral_coverage_ratchet` | ❌ No | **DELETE** |
| 13 | `test_certification_evidence_hygiene.py` | 30 | `certification_evidence_hygiene` | ❌ No | **DELETE** |
| 14 | `test_circuit_breaker_gate.py` | 30 | `circuit_breaker_gate` | ❌ No | **DELETE** |
| 15 | `test_classification_kernel_hardened.py` | 30 | `classification_kernel_hardened` | ❌ No | **DELETE** |
| 16 | `test_code_quality_metrics.py` | 30 | `code_quality_metrics` | ❌ No | **DELETE** |
| 17 | `test_comprehensive_structure.py` | 30 | `comprehensive_structure` | ❌ No | **DELETE** |
| 18 | `test_conftest_ignore_policy.py` | 30 | `conftest_ignore_policy` | ❌ No | **DELETE** |
| 19 | `test_contract_compatibility.py` | 30 | `contract_compatibility` | ❌ No | **DELETE** |
| 20 | `test_crypto_trust_signing_contracts.py` | 30 | `crypto_trust_signing_contracts` | ❌ No | **DELETE** |
| 21 | `test_determinism_replayability_contracts.py` | 30 | `determinism_replayability_contracts` | ❌ No | **DELETE** |
| 22 | `test_deterministic_loop_detector.py` | 30 | `deterministic_loop_detector` | ❌ No | **DELETE** |
| 23 | `test_discovery_sovereign_classification.py` | 30 | `discovery_sovereign_classification` | ❌ No | **DELETE** |
| 24 | `test_enforcement_mode_transition_matrix.py` | 30 | `enforcement_mode_transition_matrix` | ❌ No | **DELETE** |
| 25 | `test_execution_gateway_bugfixes.py` | 30 | `execution_gateway_bugfixes` | ❌ No | **DELETE** |
| 26 | `test_forensic_audit_unified.py` | 30 | `forensic_audit_unified` | ❌ No | **DELETE** |
| 27 | `test_governance_escalation_contracts.py` | 30 | `governance_escalation_contracts` | ❌ No | **DELETE** |
| 28 | `test_gravity_validator_hardened.py` | 30 | `gravity_validator_hardened` | ❌ No | **DELETE** |
| 29 | `test_guardian_aggregation.py` | 30 | `guardian_aggregation` | ❌ No | **DELETE** |
| 30 | `test_guardian_architecture_governance.py` | 30 | `guardian_architecture_governance` | ❌ No | **DELETE** |
| 31 | `test_guardian_c0_sovereignty.py` | 30 | `guardian_c0_sovereignty` | ❌ No | **DELETE** |
| 32 | `test_guardian_change_package_activation.py` | 30 | `guardian_change_package_activation` | ❌ No | **DELETE** |
| 33 | `test_guardian_classification_compliance.py` | 30 | `guardian_classification_compliance` | ❌ No | **DELETE** |
| 34 | `test_guardian_config_with_logic.py` | 30 | `guardian_config_with_logic` | ❌ No | **DELETE** |
| 35 | `test_guardian_contract.py` | 30 | `guardian_contract` | ❌ No | **DELETE** |
| 36 | `test_guardian_cross_layer_mutation.py` | 30 | `guardian_cross_layer_mutation` | ❌ No | **DELETE** |
| 37 | `test_guardian_duplicate_ssot.py` | 30 | `guardian_duplicate_ssot` | ❌ No | **DELETE** |
| 38 | `test_guardian_escalation_determinism.py` | 30 | `guardian_escalation_determinism` | ❌ No | **DELETE** |
| 39 | `test_guardian_gateway_bypass.py` | 30 | `guardian_gateway_bypass` | ❌ No | **DELETE** |
| 40 | `test_guardian_hygiene.py` | 30 | `guardian_hygiene` | ❌ No | **DELETE** |
| 41 | `test_guardian_manifest.py` | 30 | `guardian_manifest` | ❌ No | **DELETE** |
| 42 | `test_guardian_prompt_assembly_exclusivity.py` | 30 | `guardian_prompt_assembly_exclusivity` | ❌ No | **DELETE** |
| 43 | `test_guardian_self_integrity.py` | 30 | `guardian_self_integrity` | ❌ No | **DELETE** |
| 44 | `test_incident_bundle_generator.py` | 30 | `incident_bundle_generator` | ❌ No | **DELETE** |
| 45 | `test_injection_regression_gate.py` | 30 | `injection_regression_gate` | ❌ No | **DELETE** |
| 46 | `test_l1_runtime_bypass_simple.py` | 30 | `l1_runtime_bypass_simple` | ❌ No | **DELETE** |
| 47 | `test_llm_validator_no_new_gaps.py` | 30 | `llm_validator_no_new_gaps` | ❌ No | **DELETE** |
| 48 | `test_manifest_verify_hash_enforced.py` | 30 | `manifest_verify_hash_enforced` | ❌ No | **DELETE** |
| 49 | `test_manual_verification.py` | 30 | `manual_verification` | ❌ No | **DELETE** |
| 50 | `test_mece_naming_compliance.py` | 30 | `mece_naming_compliance` | ❌ No | **DELETE** |
| 51 | `test_meta_invariant_governance.py` | 30 | `meta_invariant_governance` | ❌ No | **DELETE** |
| 52 | `test_mission_runner_wiring.py` | 30 | `mission_runner_wiring` | ❌ No | **DELETE** |
| 53 | `test_pascal_edge_cases.py` | 30 | `pascal_edge_cases` | ❌ No | **DELETE** |
| 54 | `test_policy_pack_validator.py` | 30 | `policy_pack_validator` | ❌ No | **DELETE** |
| 55 | `test_registry_completeness.py` | 30 | `registry_completeness` | ❌ No | **DELETE** |
| 56 | `test_retry_mixin_wiring.py` | 30 | `retry_mixin_wiring` | ❌ No | **DELETE** |
| 57 | `test_review_summary_generator.py` | 30 | `review_summary_generator` | ❌ No | **DELETE** |
| 58 | `test_runtime_entrypoint_inventory.py` | 30 | `runtime_entrypoint_inventory` | ❌ No | **DELETE** |
| 59 | `test_scanner_governance.py` | 30 | `scanner_governance` | ❌ No | **DELETE** |
| 60 | `test_semantic_coverage_quality.py` | 30 | `semantic_coverage_quality` | ❌ No | **DELETE** |
| 61 | `test_signed_guardian_result_emission.py` | 30 | `signed_guardian_result_emission` | ❌ No | **DELETE** |
| 62 | `test_silent_degradation_detector.py` | 30 | `silent_degradation_detector` | ❌ No | **DELETE** |
| 63 | `test_sovereign_llm_gateway_hardened.py` | 30 | `sovereign_llm_gateway_hardened` | ❌ No | **DELETE** |
| 64 | `test_sovereignty_runtime_contract.py` | 30 | `sovereignty_runtime_contract` | ❌ No | **DELETE** |
| 65 | `test_ssot_alignment.py` | 30 | `ssot_alignment` | ❌ No | **DELETE** |

**Additional TEMPLATE_STUB files (66-75):**
- `test_ssot_bootstrap_wiring.py`
- `test_ssot_heal_runner_preflight.py`
- `test_ssot_utf8_output.py`
- `test_structure_blueprint_hardened.py`
- `test_structure_drift.py`
- `test_structure_healers.py`
- `test_test_quality_detector.py`
- `test_tool_contract_validation.py`
- `test_traceability_provenance_contracts.py`
- `test_zero_ssot_hardcoding.py`

**Evidence for DELETE:**
- **195 import failures** across all template stubs (verified via `exec()` import test)
- **Zero behavioral assertions** — only `assert X is not None` smoke tests
- **ADG coverage: 0** — no `covers` or `tests_execution_of` edges to production code
- **Similarity to existing tests:** 0.75-0.80 composite score with 1 shared import, but existing tests have 10x more coverage
- **Template generation date:** All files created in same batch (git log shows same timestamp range)
- **No implementation trail:** Symbols never existed in production codebase (git log search confirms)

---

### Category 3: BEHAVIORAL — KEEP (4 files)

| # | File | Lines | Tests | Key Assertions | Fixtures | Treatment |
|---|------|-------|-------|----------------|----------|-----------|
| 76 | `test_test_silent_skip_detector.py` | 580 | 29 | `assert result.has_violations`, `assert "BROAD_EXCEPT_AVAILABILITY_FLAG" in _sub_patterns(result)`, `assert v.metadata["flag"] == "_AVAILABLE"` | ✅ `tmp_path`, `test_py` fixture, `prod_py` fixture | **KEEP** |
| 77 | `test_exemption_recognition.py` | 252 | 12 | `assert len(violations) == 0`, `assert violations[0].category.value == "silent_degradation"`, proximity-based exemption tests | ✅ `tmp_path` | **KEEP** |
| 78 | `test_agent_autonomy.py` | 242 | 9 | `assert result["compliant"]`, `assert "missing heal_repository" in v`, `assert "No agent classes found" in result["error"]` | ✅ `validator` fixture, temp file handling | **KEEP** |
| 79 | `test_core_components.py` | 170 | 7 | `assert result["compliant"]`, `assert "nonexistent_file.py" in result["missing"]`, performance assertions | ✅ CoreComponentsValidator, `tmp_path` | **KEEP** |

**Evidence for KEEP:**

#### test_test_silent_skip_detector.py (580 lines)
- **Behavioral coverage:** 29 test methods across 5 test classes
- **Production code tested:** `TestSilentSkipDetector` validator from `agentic_core.L5_safety.validators`
- **Edge cases covered:**
  - `BROAD_EXCEPT_AVAILABILITY_FLAG` detection (positive cases)
  - Safe `except ImportError` pattern (negative / no false-positive)
  - Bare `except`, `except BaseException` (positive)
  - Tuple `except (E1, E2)` variants
  - Non-test files skipped entirely
  - Guardian exemption comment suppression
  - Severity/category verification
- **Unique value:** Only behavioral tests for this validator — ADG stubs exist but don't test logic
- **Imports:** All resolve (`agentic_core.L5_safety.validators.test_skip_detector_validator`)

#### test_exemption_recognition.py (252 lines)
- **Behavioral coverage:** 12 test methods covering all 6 silent-degradation sub-patterns
- **Production code tested:** `SilentDegradationDetector` from `agentic_core.L5_safety.validators`
- **Edge cases covered:**
  - Exemption proximity requirements (3-line vs 6-line distance)
  - Malformed exemption comments
  - All 6 sub-patterns: `EXCEPT_IMPORT_PASS`, `AVAILABILITY_GUARD_SKIP`, `LOG_AND_RETURN_MOCK`, `SKIP_STRING_RETURN`, `PHANTOM_MODULE_IMPORT`, `SILENT_SUCCESS_ON_NOOP`
- **Unique value:** Only tests for exemption proximity logic
- **Imports:** All resolve (`SilentDegradationDetector`, `EnforcementLevel`)

#### test_agent_autonomy.py (242 lines)
- **Behavioral coverage:** 9 test methods including validator class
- **Production code tested:** `AgentAutonomyValidator` (self-contained in test file)
- **Edge cases covered:**
  - `heal_repository` method presence via AST analysis
  - Syntax error handling
  - Multiple agent classes in single file
  - Partial compliance scenarios
  - Non-Python file handling
- **Unique value:** Self-contained AST-based validator with comprehensive edge cases
- **Imports:** `ast`, `tempfile` (stdlib only — no production dependencies)

#### test_core_components.py (170 lines)
- **Behavioral coverage:** 7 test methods
- **Production code tested:** File existence checking for critical infrastructure
- **Edge cases covered:**
  - Critical file existence validation
  - Missing file detection
  - Empty file list handling
  - Partial file existence
  - Directory vs file handling
  - Performance with 1000-file lists
- **Unique value:** Only file-existence validation tests for critical infrastructure
- **Imports:** `pathlib`, `pytest` — minimal dependencies

---

## Support Files Treatment

| File | Lines | Purpose | Treatment |
|------|-------|---------|-----------|
| `conftest.py` | 501 | Pytest fixtures, guardian marker auto-application, JSON report generation | **EVALUATE** — Check if `logs/guardian_report.json` consumed downstream |
| `base.py` | 200 | `GuardianTestBase` with AST parsing utilities | **DELETE** — Functionality exists in ADG scanner |
| `_assertions.py` | 147 | Semantic coverage assertion helpers (`assert_check`, `assert_guardian_status`) | **EVALUATE** — Keep if downstream uses `GuardianResult` assertions |
| `_contract_gate_ssot.py` | 375 | SSOT mapping of guardian IDs to test modules | **DELETE** — References modules that are themselves being deleted |
| `guardian_report.py` | 316 | JSON report builder with violation codes | **EVALUATE** — Keep if downstream consumes reports |

---

## Appendix: Verification Test Suite

Created in `tests/_verification/`:

| Test | Purpose | Evidence Generated |
|------|---------|-------------------|
| `test_guardian_importability.py` | Verify which tests fail at import | `guardian_importability_report.json` |
| `test_guardian_runtime.py` | Execute tests, record pass/fail | `guardian_runtime_report.json` |
| `test_guardian_downstream_usage.py` | Find consumers of guardian_report.json | `guardian_consumer_report.json` |
| `test_guardian_coverage_delta.py` | Compare coverage vs similar existing tests | `guardian_coverage_orphans.json` |
| `test_guardian_behavioral_uniqueness.py` | Score tests by behavioral content | `guardian_behavioral_scores.json` |
| `run_guardian_verification.py` | One-shot runner for all + final verdict | `guardian_final_verdict.json` |

**Run all verification:**
```bash
python run_guardian_verification.py
```

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Accidentally delete valuable test | 4 behavioral tests identified by >100 lines, >5 test methods, real assertions, fixtures |
| Downstream consumer breakage | Verify `guardian_report.json` consumers before deleting conftest/guardian_report.py |
| Loss of documentation | Template stubs have no semantic documentation — loss is minimal |
| CI/test count reduction | Expected — tests/guardian counts will drop from 79 to 4 (+ verification tests) |

---

## Implementation Order (if approved)

1. **Run verification tests** → Confirm evidence (should show ~75 broken, 4 working)
2. **Delete PLACEHOLDER files** (10 files) — lowest risk
3. **Delete TEMPLATE_STUB files** (55 files) — bulk deletion
4. **EVALUATE support files** — check downstream consumers
5. **Relocate KEEP files** (optional) — move to appropriate test directories
6. **Remove tests/guardian directory** (if empty after deletions)

---

*Plan generated: 2026-03-31*  
*Evidence sources: ADG SQLite analysis, import resolution tests, AST parsing, git history search*
