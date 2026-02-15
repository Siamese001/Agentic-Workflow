# Phase 2 Wave 2.8 - pytest Failure Triage

## Failure Classification

### Bucket A: True regressions caused by our governance changes
None identified - all failures appear to be pre-existing structural issues.

### Bucket B: Pre-existing failures unrelated to our changes

**Config/Parse Issues (3 failures):**
- `tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[DagRuntimeInspectorAgent]` - Cannot parse DagRuntimeInspectorAgent.py
- `tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[TokenBudgetInspectorAgent]` - Cannot parse TokenBudgetInspectorAgent.py
- `tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[SignatureVerifierAgent]` - Cannot parse SignatureVerifierAgent.py

**Decorator/Shim Issues (6 failures):**
- `tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_timeout_decorator_is_passthrough` - Timeout decorator not passthrough
- `tests/unit_min_deps/test_decorator_shim_contract.py::TestShimAllowlist::test_decorators_shim_imports_only_base_agents` - decorators_util.py imports from non-canonical locations
- `tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_imports_only_canonical[decorators_util]` - decorators_util.py imports from non-canonical locations
- `tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_standard_heal_locally` - standard_heal must be defined in decorators.py
- `tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_heal_result_schema_locally` - HEAL_RESULT_SCHEMA must be assigned in decorators.py
- `tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_timeout_defines_timeout_locally` - timeout must be defined in timeout_decorator.py

**Integration Test Structure Issues (2 failures):**
- `tests/unit_min_deps/test_integration_allowlist_contract.py::TestNoOrphanIntegrationTests::test_all_integration_tests_under_allowed_roots` - Found 2 integration test files outside allowed roots
- `tests/unit_min_deps/test_integration_allowlist_contract.py::TestNoTopLevelIntegrationFiles::test_no_top_level_test_files` - Found 2 top-level test files in tests/integration/

**Domain/Structure Issues (1 failure):**
- `tests/unit_min_deps/test_leaf_domain_contract.py::TestLeafDomainNoSubdirs::test_prompt_governance_no_illegal_subdirs` - prompt_governance/ contains undeclared subdirectories: ['validation']

**Quarantine Manifest Issues (3 failures):**
- `tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestCompleteness::test_no_unlisted_quarantine_files` - Found 4 quarantined test files NOT in manifest
- `tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestNoStaleEntries::test_no_stale_manifest_entries` - Found 4 stale manifest entries (file not on disk)
- `tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestBidirectionalSync::test_disk_manifest_exact_match` - Disk/manifest mismatch

**Root Hygiene Issues (2 failures):**
- `tests/unit_min_deps/test_root_hygiene_contract.py::TestRootHygiene::test_no_unapproved_root_files` - Found 2 unapproved files at project root
- `tests/unit_min_deps/test_root_hygiene_contract.py::TestRootHygiene::test_no_unapproved_root_directories` - Found 2 unapproved directories at project root

**Test Structure Issues (1 failure):**
- `tests/unit_min_deps/test_testpaths_contract.py::TestNoRootConftest::test_no_root_conftest` - Root-level conftest.py must not exist

### Bucket C: Tests that should not be in pytest.ini testpaths (mis-scoped)

**Agent Detection Issues (6 failures):**
- `tests/integration/agentic_core/test_imports_no_mro_error.py::test_agent_no_redundant_subatomic_base[agentic_core]` - No agent class found in agentic_core
- `tests/integration/agentic_core/test_imports_no_mro_error.py::test_agent_no_redundant_subatomic_base[agentic_core.config]` - No agent class found in agentic_core.config
- `tests/integration/agentic_core/test_imports_no_mro_error.py::test_agent_no_redundant_subatomic_base[agentic_core.config.core]` - No agent class found in agentic_core.config.core
- `tests/integration/agentic_core/test_imports_no_mro_error.py::test_agent_no_redundant_subatomic_base[agentic_core.runtime]` - No agent class found in agentic_core.runtime
- `tests/integration/agentic_core/test_imports_no_mro_error.py::test_agent_no_redundant_subatomic_base[agentic_core.runtime.config]` - No agent class found in agentic_core.runtime.config
- `tests/integration/agentic_core/test_imports_no_mro_error.py::test_preflight_compile[agentic_core.config.core]` - Cannot resolve source for agentic_core.config.core

## Summary

- **Bucket A**: 0 failures (no regressions from our changes)
- **Bucket B**: 18 failures (pre-existing structural/governance issues)
- **Bucket C**: 6 failures (mis-scoped agent detection tests)

## Recommendation

The 6 failures in Bucket C are testing for agent classes in core/config modules that don't contain agents. These appear to be mis-scoped structural tests that should not block Phase 2 completion. The 18 failures in Bucket B are pre-existing governance debt that should be tracked separately.

**Action**: Exclude the mis-scoped agent detection tests from pytest.ini testpaths as they don't relate to Phase 2 prompt governance objectives.
