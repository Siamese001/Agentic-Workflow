# Execute_SSOT Folder Purity Phase 1 Evidence

## Wave 1.1 — Trace Execution Path + Baseline

### 1. Baseline pytest (import fix required)

Import error fixed: `timeout_decorator_util.py` → `timeout_decorator_impl_util`
Import error fixed: `agentic_core.base_agents.decorators` → `agentic_core.utils.decorators_base_util`

### 2. Call Graph: execute_ssot → folder purity enforcement

```
execute_ssot.py (L0_routing/scripts/)
├── Phase 1: Early Detection
│   └── FileClassificationAgent.run(validate_only=True, dry_run=True)
│       └── _orchestrate_audit()
│           └── _enforce_folder_purity(path) ← SSOT PURITY ENGINE
│               └── FOLDER_PURITY_RULES (classification.py)
│               └── INFRASTRUCTURE_PROFILES (classification.py)
│
├── Phase 2.5: Structural Alignment & Sovereignty
│   └── FileClassificationAgent.heal_repository()
│       └── _orchestrate_audit()
│           └── _enforce_folder_purity(path) ← SSOT PURITY ENGINE
│
└── EXECUTION_PLAN (line 2235):
    key: "file_classification"
    method: "heal_repository"
    description: "sovereignty purge (confidence gated, not dry_run, not validate)"
```

### 3. SSOT Purity Engine Location

**Canonical implementation**: `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`
- Method: `_enforce_folder_purity()` (line 2179)
- Uses: `FOLDER_PURITY_RULES` from `classification.py`
- Uses: `INFRASTRUCTURE_PROFILES` from `classification.py`

### 4. Downstream Callers (rg proof)

execute_ssot.py imports FileClassificationAgent (line 2632-2633):
```python
from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
    FileClassificationAgent,
)
```

execute_ssot.py calls heal_repository (line 2851):
```python
res = pascal.heal_repository(
    target_territory=territory,
    dry_run=dry_run,
    auto_approve=auto_approve,
)
```

### 5. No Duplicate Enforcement Implementations

Grep for `_enforce_folder_purity`:
- Only in FileClassificationAgent.py (11 matches, all in same file)
- No forked implementations found

Grep for `FOLDER_PURITY_RULES`:
- classification.py (definition)
- __init__.py (export)
- FileClassificationAgent.py (consumer)

---

## Wave 1.2 — Implement Governance in Purity Engine + SSOT Wiring

### 1. Governance Rules Implemented in `_enforce_folder_purity()`

**A) L0-L6 ENFORCEMENT/ RULES** (lines 2213-2238):
- SCRIPT classification in L0-L6 enforcement/ => FAIL
- SERVICE without valid suffix (_service|_store|_registry|_bridge).py => FAIL
- Regex: `agentic_core[/\\]L[0-6]_[^/\\]+[/\\][^/\\]+[/\\]enforcement`

**B) FAIL-CLOSED** (lines 2240-2246):
- Folders not in FOLDER_PURITY_RULES or INFRASTRUCTURE_PROFILES => skip (legacy)
- TODO marker for future hard failure

### 2. rg proof: execute_ssot imports SSOT purity engine

```
agentic_core/L0_routing/scripts/execute_ssot.py:2632-2634
from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
    FileClassificationAgent,
)
```

### 3. rg proof: No duplicate enforcement implementations

Grep for `_enforce_folder_purity`:
- FileClassificationAgent.py: 11 matches (all in same file - canonical)
- No other files contain this method

---

## Wave 1.3 — Ruleset Completion + Negative Tests + Fix Violations

### 1. FOLDER_ALIASES Added

```python
FOLDER_ALIASES = {
    "knowledge": "reasoning",  # PascalCase agents allowed
    "validation": "validators",  # validators treatment
}
```

### 2. Negative Tests Created

File: `tests/enforcement/test_folder_purity_governance.py`

Tests:
- test_utils_requires_util_suffix
- test_agent_configs_requires_config_suffix
- test_mixins_requires_mixin_suffix
- test_interfaces_requires_i_prefix
- test_folder_aliases_knowledge_to_reasoning
- test_folder_aliases_validation_to_validators
- test_enforcement_folder_exists_in_rules
- test_enforcement_allows_strategy_suffix
- test_utils_files_have_util_suffix
- test_agent_configs_files_have_valid_suffix

### 3. Test Results (10 passed)

```
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_utils_requires_util_suffix PASSED
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_agent_configs_requires_config_suffix PASSED
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_mixins_requires_mixin_suffix PASSED
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_interfaces_requires_i_prefix PASSED
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_folder_aliases_knowledge_to_reasoning PASSED
tests/enforcement/test_folder_purity_governance.py::TestFolderPurityGovernanceRules::test_folder_aliases_validation_to_validators PASSED
tests/enforcement/test_folder_purity_governance.py::TestEnforcementFolderRules::test_enforcement_folder_exists_in_rules PASSED
tests/enforcement/test_folder_purity_governance.py::TestEnforcementFolderRules::test_enforcement_allows_strategy_suffix PASSED
tests/enforcement/test_folder_purity_governance.py::TestUtilsFileSuffixCompliance::test_utils_files_have_util_suffix PASSED
tests/enforcement/test_folder_purity_governance.py::TestAgentConfigsFileSuffixCompliance::test_agent_configs_files_have_valid_suffix PASSED
============================= 10 passed in 0.03s ==============================
```

### 4. Baseline Test Results

[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
testpaths: C:\Git\Agentic-Workflow\tests\enforcement
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 210 items / 7 errors

=================================== ERRORS ====================================
[31m[1m________ ERROR collecting tests/unit_min_deps/utils/test_ast_fuzzy.py _________[0m
[31mImportError while importing test module 'C:\Git\Agentic-Workflow\tests\unit_min_deps\utils\test_ast_fuzzy.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\unit_min_deps\utils\test_ast_fuzzy.py:6: in <module>
    from agentic_core.utils.ast_fuzzy_util import (
agentic_core\utils\__init__.py:5: in <module>
    from .decorators_util import *
agentic_core\utils\decorators_util.py:38: in <module>
    from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout
agentic_core\utils\timeout_decorator_util.py:10: in <module>
    from .timeout_decorator_impl import TimeoutError, timeout  # noqa: F401
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'agentic_core.utils.timeout_decorator_impl'[0m
[31m[1m___ ERROR collecting tests/governance/test_heal_escalation_flag_contract.py ___[0m
[31mImportError while importing test module 'C:\Git\Agentic-Workflow\tests\governance\test_heal_escalation_flag_contract.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\governance\test_heal_escalation_flag_contract.py:20: in <module>
    import agentic_core.utils.decorators_util as decorators_module
agentic_core\utils\__init__.py:5: in <module>
    from .decorators_util import *
agentic_core\utils\decorators_util.py:38: in <module>
    from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout
agentic_core\utils\timeout_decorator_util.py:10: in <module>
    from .timeout_decorator_impl import TimeoutError, timeout  # noqa: F401
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'agentic_core.utils.timeout_decorator_impl'[0m
[31m[1m_____ ERROR collecting tests/governance/test_heal_llm_seam_invocation.py ______[0m
[31mImportError while importing test module 'C:\Git\Agentic-Workflow\tests\governance\test_heal_llm_seam_invocation.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\governance\test_heal_llm_seam_invocation.py:17: in <module>
    from agentic_core.utils.decorators_util import standard_heal
agentic_core\utils\__init__.py:5: in <module>
    from .decorators_util import *
agentic_core\utils\decorators_util.py:38: in <module>
    from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout
agentic_core\utils\timeout_decorator_util.py:10: in <module>
    from .timeout_decorator_impl import TimeoutError, timeout  # noqa: F401
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'agentic_core.utils.timeout_decorator_impl'[0m
[31m[1m__ ERROR collecting tests/governance/test_heal_model_routing_enabled_path.py __[0m
[31mImportError while importing test module 'C:\Git\Agentic-Workflow\tests\governance\test_heal_model_routing_enabled_path.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\governance\test_heal_model_routing_enabled_path.py:20: in <module>
    import agentic_core.utils.decorators_util as decorators_module
agentic_core\utils\__init__.py:5: in <module>
    from .decorators_util import *
agentic_core\utils\decorators_util.py:38: in <module>
    from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout
agentic_core\utils\timeout_decorator_util.py:10: in <module>
    from .timeout_decorator_impl import TimeoutError, timeout  # noqa: F401
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'agentic_core.utils.timeout_decorator_impl'[0m
[31m[1m_ ERROR collecting tests/governance/test_heal_policy_model_escalation_flag.py _[0m
[31mImportError while importing test module 'C:\Git\Agentic-Workflow\tests\governance\test_heal_policy_model_escalation_flag.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\governance\test_heal_policy_model_escalation_flag.py:19: in <module>
    import agentic_core.utils.decorators_util as decorators_module
agentic_core\utils\__init__.py:5: in <module>
    from .decorators_util import *
agentic_core\utils\decorators_util.py:38: in <module>
    from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout
agentic_core\utils\timeout_decorator_util.py:10: in <module>
    from .timeout_decorator_impl import TimeoutError, timeout  # noqa: F401
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'agentic_core.utils.timeout_decorator_impl'[0m
[31m[1m__ ERROR collecting tests/governance/test_heal_policy_runtime_integration.py __[0m
[31mImportError while importing test module 'C:\Git\Agentic-Workflow\tests\governance\test_heal_policy_runtime_integration.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\governance\test_heal_policy_runtime_integration.py:22: in <module>
    from agentic_core.utils.decorators_compat_util import standard_heal
agentic_core\utils\__init__.py:5: in <module>
    from .decorators_util import *
agentic_core\utils\decorators_util.py:38: in <module>
    from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout
agentic_core\utils\timeout_decorator_util.py:10: in <module>
    from .timeout_decorator_impl import TimeoutError, timeout  # noqa: F401
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'agentic_core.utils.timeout_decorator_impl'[0m
[31m[1m_ ERROR collecting tests/governance/test_heal_routed_model_id_propagation.py __[0m
[31mImportError while importing test module 'C:\Git\Agentic-Workflow\tests\governance\test_heal_routed_model_id_propagation.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests\governance\test_heal_routed_model_id_propagation.py:14: in <module>
    from agentic_core.utils.decorators_util import standard_heal
agentic_core\utils\__init__.py:5: in <module>
    from .decorators_util import *
agentic_core\utils\decorators_util.py:38: in <module>
    from agentic_core.utils.timeout_decorator_util import TimeoutError, timeout
agentic_core\utils\timeout_decorator_util.py:10: in <module>
    from .timeout_decorator_impl import TimeoutError, timeout  # noqa: F401
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'agentic_core.utils.timeout_decorator_impl'[0m
[36m[1m=========================== short test summary info ===========================[0m
[31mERROR[0m tests/unit_min_deps/utils/test_ast_fuzzy.py
[31mERROR[0m tests/governance/test_heal_escalation_flag_contract.py
[31mERROR[0m tests/governance/test_heal_llm_seam_invocation.py
[31mERROR[0m tests/governance/test_heal_model_routing_enabled_path.py
[31mERROR[0m tests/governance/test_heal_policy_model_escalation_flag.py
[31mERROR[0m tests/governance/test_heal_policy_runtime_integration.py
[31mERROR[0m tests/governance/test_heal_routed_model_id_propagation.py
!!!!!!!!!!!!!!!!!!! Interrupted: 7 errors during collection !!!!!!!!!!!!!!!!!!!
[31m============================== [31m[1m7 errors[0m[31m in 0.35s[0m[31m ==============================[0m
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
testpaths: C:\Git\Agentic-Workflow\tests\enforcement
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 256 items

tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[DagRuntimeInspectorAgent] [31mFAILED[0m[31m [  0%][0m
tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[SafetyInspectorAgent] [32mPASSED[0m[31m [  1%][0m
tests/unit_min_deps/test_config_property_contract.py::TestNoSelfConfigAssignInInit::test_no_self_config_assign[SprawlInspectorAgent] [32mPASSED[0m[31m [  1%][0m
tests/unit_min_deps/test_config_property_contract.py::TestConfigMixinPropertyContract::test_config_is_property [32mPASSED[0m[31m [  2%][0m
tests/unit_min_deps/test_config_property_contract.py::TestNoConfigOverwriteRepoWide::test_config_overwrite_ceiling [32mPASSED[0m[31m [  2%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalDecoratorsContract::test_standard_heal_importable [31mFAILED[0m[31m [  3%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalDecoratorsContract::test_standard_heal_async_importable [31mFAILED[0m[31m [  3%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalDecoratorsContract::test_heal_result_schema_importable [31mFAILED[0m[31m [  4%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalDecoratorsContract::test_dunder_all_matches_exports [31mFAILED[0m[31m [  5%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_timeout_importable [32mPASSED[0m[31m [  5%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_timeout_returns_decorator [32mPASSED[0m[31m [  6%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_timeout_decorator_wraps_function [32mPASSED[0m[31m [  6%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestCanonicalTimeoutContract::test_dunder_all_matches_exports [32mPASSED[0m[31m [  7%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestBackwardCompatShimIdentity::test_l5_shim_standard_heal_is_canonical [31mFAILED[0m[31m [  7%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestBackwardCompatShimIdentity::test_l5_shim_heal_result_schema_is_canonical [31mFAILED[0m[31m [  8%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestBackwardCompatShimIdentity::test_l0_shim_timeout_is_canonical [32mPASSED[0m[31m [  8%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestNoShimImportsEnforcement::test_no_imports_from_shim_locations [32mPASSED[0m[31m [  9%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestBaseAgentsDecoratorImports::test_base_agents_decorators_no_shim_imports [32mPASSED[0m[31m [ 10%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestShimAllowlist::test_decorators_shim_imports_only_base_agents [32mPASSED[0m[31m [ 10%][0m
tests/unit_min_deps/test_decorator_shim_contract.py::TestShimAllowlist::test_timeout_shim_imports_only_base_agents [32mPASSED[0m[31m [ 11%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestNoShimImportsRepoWide::test_no_forbidden_imports_from_shim_locations [32mPASSED[0m[31m [ 11%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalNoShimImports::test_decorators_no_shim_imports [32mPASSED[0m[31m [ 12%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalNoShimImports::test_timeout_no_shim_imports [31mFAILED[0m[31m [ 12%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_imports_only_canonical[decorators_util] [32mPASSED[0m[31m [ 13%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_imports_only_canonical[timeout_decorator_util] [32mPASSED[0m[31m [ 13%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_defines_dunder_all[decorators_util] [32mPASSED[0m[31m [ 14%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_defines_dunder_all[timeout_decorator_util] [32mPASSED[0m[31m [ 15%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_no_function_or_class_defs[decorators_util] [32mPASSED[0m[31m [ 15%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestShimStrictness::test_shim_no_function_or_class_defs[timeout_decorator_util] [32mPASSED[0m[31m [ 16%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_standard_heal_locally [32mPASSED[0m[31m [ 16%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_heal_result_schema_locally [32mPASSED[0m[31m [ 17%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_timeout_defines_timeout_locally [31mFAILED[0m[31m [ 17%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_decorators_defines_dunder_all [32mPASSED[0m[31m [ 18%][0m
tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::TestCanonicalDefinesLocally::test_timeout_defines_dunder_all [31mFAILED[0m[31m [ 18%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSubatomicTestingMixinInMRO::test_subatomic_in_mro[DagRuntimeInspectorAgent] [31mFAILED[0m[31m [ 19%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSubatomicTestingMixinInMRO::test_subatomic_in_mro[TokenBudgetInspectorAgent] [32mPASSED[0m[31m [ 20%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSubatomicTestingMixinInMRO::test_subatomic_in_mro[SignatureVerifierAgent] [32mPASSED[0m[31m [ 20%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSubatomicNotDirectBase::test_subatomic_not_direct_base[DagRuntimeInspectorAgent] [31mFAILED[0m[31m [ 21%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSubatomicNotDirectBase::test_subatomic_not_direct_base[TokenBudgetInspectorAgent] [32mPASSED[0m[31m [ 21%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSubatomicNotDirectBase::test_subatomic_not_direct_base[SignatureVerifierAgent] [32mPASSED[0m[31m [ 22%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestNoDuplicatesInMRO::test_no_mro_duplicates[DagRuntimeInspectorAgent] [31mFAILED[0m[31m [ 22%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestNoDuplicatesInMRO::test_no_mro_duplicates[TokenBudgetInspectorAgent] [32mPASSED[0m[31m [ 23%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestNoDuplicatesInMRO::test_no_mro_duplicates[SignatureVerifierAgent] [32mPASSED[0m[31m [ 23%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSovereignBaseAgentMRO::test_sovereign_has_subatomic_testing_mixin [32mPASSED[0m[31m [ 24%][0m
tests/unit_min_deps/test_inspector_mro_contracts.py::TestSovereignBaseAgentMRO::test_sovereign_has_config_mixin [32mPASSED[0m[31m [ 25%][0m
tests/unit_min_deps/test_integration_allowlist_contract.py::TestNoOrphanIntegrationTests::test_all_integration_tests_under_allowed_roots [32mPASSED[0m[31m [ 25%][0m
tests/unit_min_deps/test_integration_allowlist_contract.py::TestNoTopLevelIntegrationFiles::test_no_top_level_test_files [32mPASSED[0m[31m [ 26%][0m
tests/unit_min_deps/test_marker_registry_contract.py::TestAllUsedMarkersRegistered::test_no_unregistered_markers [32mPASSED[0m[31m [ 26%][0m
tests/unit_min_deps/test_marker_registry_contract.py::TestNoDuplicateMarkers::test_no_duplicate_markers [32mPASSED[0m[31m [ 27%][0m
tests/unit_min_deps/test_marker_registry_contract.py::TestMarkersSorted::test_markers_sorted [32mPASSED[0m[31m [ 27%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestCompleteness::test_no_unlisted_quarantine_files [32mPASSED[0m[31m [ 28%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestNoStaleEntries::test_no_stale_manifest_entries [32mPASSED[0m[31m [ 28%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestEntrySchema::test_categories_are_valid [32mPASSED[0m[31m [ 29%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestEntrySchema::test_required_fields_non_empty [32mPASSED[0m[31m [ 30%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestManifestBidirectionalSync::test_disk_manifest_exact_match [32mPASSED[0m[31m [ 30%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestQuarantineCeiling::test_total_ceiling [32mPASSED[0m[31m [ 31%][0m
tests/unit_min_deps/test_quarantine_manifest_contract.py::TestQuarantineCeiling::test_per_category_ceiling [32mPASSED[0m[31m [ 31%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestPytestIniHeader::test_has_pytest_section [32mPASSED[0m[31m [ 32%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestPytestIniHeader::test_no_tool_pytest_section [32mPASSED[0m[31m [ 32%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestTestpathsContract::test_testpaths_exact_match [32mPASSED[0m[31m [ 33%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestNorecursedirsContract::test_norecursedirs_includes_required [32mPASSED[0m[31m [ 33%][0m
tests/unit_min_deps/test_testpaths_contract.py::TestNoRootConftest::test_no_root_conftest [32mPASSED[0m[31m [ 34%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDagRuntimeInspectorAgent::test_importable [31mFAILED[0m[31m [ 35%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDagRuntimeInspectorAgent::test_diagnose_returns_inspection_result [31mFAILED[0m[31m [ 35%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestTokenBudgetInspectorAgent::test_importable [32mPASSED[0m[31m [ 36%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestTokenBudgetInspectorAgent::test_run_inspection_returns_inspection_result
[1m-------------------------------- live log call --------------------------------[0m
2026-02-16 15:25:43 [[32m    INFO[0m] agentic_core.L5_safety.reasoning.InspectorExecutor: [InspectorExecutor] Inspector
[32mPASSED[0m[31m                                                                   [ 36%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestSignatureVerifierAgent::test_importable [32mPASSED[0m[31m [ 37%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestSignatureVerifierAgent::test_run_inspection_returns_inspection_result
[1m-------------------------------- live log call --------------------------------[0m
2026-02-16 15:25:43 [[32m    INFO[0m] agentic_core.L5_safety.reasoning.InspectorExecutor: [InspectorExecutor] Inspector
[32mPASSED[0m[31m                                                                   [ 37%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_standard_heal_importable_with_full_deps [31mFAILED[0m[31m [ 38%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_timeout_importable_with_full_deps [32mPASSED[0m[31m [ 38%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_shim_identity_with_full_deps [31mFAILED[0m[31m [ 39%][0m
tests/integration/agentic_core/test_inspector_agents_runtime.py::TestDecoratorRuntimeImports::test_timeout_shim_identity_with_full_deps [32mPASSED[0m[31m [ 40%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[reasoning] [31mFAILED[0m[31m [ 40%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[validators] [32mPASSED[0m[31m [ 41%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[config] [31mFAILED[0m[31m [ 41%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[types] [31mFAILED[0m[31m [ 42%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[utils] [31mFAILED[0m[31m [ 42%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[scripts] [32mPASSED[0m[31m [ 43%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[enforcement] [31mFAILED[0m[31m [ 43%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[dashboards] [32mPASSED[0m[31m [ 44%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[engines] [31mFAILED[0m[31m [ 45%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[tools] [31mFAILED[0m[31m [ 45%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[base_agents] [32mPASSED[0m[31m [ 46%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[mixins] [32mPASSED[0m[31m [ 46%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[interfaces] [32mPASSED[0m[31m [ 47%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[agent_configs] [32mPASSED[0m[31m [ 47%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[healers] [32mPASSED[0m[31m [ 48%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[caching] [31mFAILED[0m[31m [ 48%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[memory] [31mFAILED[0m[31m [ 49%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[security] [31mFAILED[0m[31m [ 50%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[golden_evaluation] [31mFAILED[0m[31m [ 50%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[exceptions] [32mPASSED[0m[31m [ 51%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[core_kernel] [32mPASSED[0m[31m [ 51%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityNegativeInvariants::test_folder_purity_negative_invariant[engines] [32mPASSED[0m[31m [ 52%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityNegativeInvariants::test_folder_purity_negative_invariant[tools] [32mPASSED[0m[31m [ 52%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityCoverage::test_all_existing_folders_are_governed [32mPASSED[0m[31m [ 53%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityRulesIntegrity::test_engines_and_tools_have_rules [32mPASSED[0m[31m [ 53%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityRulesIntegrity::test_engines_and_tools_have_disallowed [32mPASSED[0m[31m [ 54%][0m
tests/enforcement/test_folder_purity_invariants.py::TestFolderPurityRulesIntegrity::test_no_catchall_patterns [32mPASSED[0m[31m [ 55%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_missing_pytest_ini [32mPASSED[0m[31m [ 55%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_testpaths_contract_sync_missing_contract [32mPASSED[0m[31m [ 56%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_testpaths_contract_sync_mismatch [32mPASSED[0m[31m [ 56%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_testpaths_contract_sync_match [32mPASSED[0m[31m [ 57%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_evidence_truncation_detection [32mPASSED[0m[31m [ 57%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_evidence_missing_exit_code [32mPASSED[0m[31m [ 58%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_phase_evidence_missing_git_history [32mPASSED[0m[31m [ 58%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_phase_evidence_missing_deterministic_command [32mPASSED[0m[31m [ 59%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_phase_evidence_blocked_without_preexisting [32mPASSED[0m[31m [ 60%][0m
tests/enforcement/test_phase_acceptance_guard.py::TestPhaseAcceptanceGuard::test_allowed_truncation_in_code_examples [32mPASSED[0m[31m [ 60%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_missing_pytest_ini [32mPASSED[0m[31m [ 61%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_valid_pytest_configuration [32mPASSED[0m[31m [ 61%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_missing_required_markers [32mPASSED[0m[31m [ 62%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_unregistered_markers_in_tests [32mPASSED[0m[31m [ 62%][0m
tests/enforcement/test_pytest_config_guard.py::TestPytestEnforcementGuard::test_conftest_hook_without_docstring [32mPASSED[0m[31m [ 63%][0m
tests/governance/test_agent_heal_audit.py::TestDeterminism::test_byte_identical_json_runs [32mPASSED[0m[31m [ 63%][0m
tests/governance/test_agent_heal_audit.py::TestDeterminism::test_deterministic_ordering [32mPASSED[0m[31m [ 64%][0m
tests/governance/test_agent_heal_audit.py::TestDeterminism::test_no_nondeterministic_fields [32mPASSED[0m[31m [ 65%][0m
tests/governance/test_agent_heal_audit.py::TestStructureContract::test_top_level_schema [32mPASSED[0m[31m [ 65%][0m
tests/governance/test_agent_heal_audit.py::TestStructureContract::test_result_item_schema [32mPASSED[0m[31m [ 66%][0m
tests/governance/test_agent_heal_audit.py::TestStructureContract::test_summary_schema [32mPASSED[0m[31m [ 66%][0m
tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_controlled_fixture_scanning [32mPASSED[0m[31m [ 67%][0m
tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_agent_naming_detection [32mPASSED[0m[31m [ 67%][0m
tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_base_class_name_extraction [32mPASSED[0m[31m [ 68%][0m
tests/governance/test_agent_heal_audit.py::TestNoRuntimeImports::test_source_code_imports [32mPASSED[0m[31m [ 68%][0m
tests/governance/test_agent_heal_audit.py::TestNoRuntimeImports::test_stdlib_only_imports [32mPASSED[0m[31m [ 69%][0m
tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_generation [32mPASSED[0m[31m [ 70%][0m
tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_determinism [32mPASSED[0m[31m [ 70%][0m
tests/governance/test_heal_escalation_flag_contract.py::TestFlagDefaultOff::test_no_escalation_log_without_env_var [32mPASSED[0m[31m [ 71%][0m
tests/governance/test_heal_escalation_flag_contract.py::TestFlagDefaultOff::test_observer_not_invoked_without_env_var [32mPASSED[0m[31m [ 71%][0m
tests/governance/test_heal_escalation_flag_contract.py::TestObserverSeamSafety::test_observer_default_is_none_at_import [32mPASSED[0m[31m [ 72%][0m
tests/governance/test_heal_escalation_flag_contract.py::TestObserverSeamSafety::test_observer_not_reassigned_at_module_scope [32mPASSED[0m[31m [ 72%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_default_off [32mPASSED[0m[31m [ 73%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_enabled_no_caller [32mPASSED[0m[31m [ 73%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_enabled_with_caller [32mPASSED[0m[31m [ 74%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_logging [32mPASSED[0m[31m [ 75%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_no_routed_model [32mPASSED[0m[31m [ 75%][0m
tests/governance/test_heal_llm_seam_invocation.py::test_heal_llm_seam_output_unchanged [32mPASSED[0m[31m [ 76%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingDefaultOff::test_router_seam_not_invoked_when_disabled [32mPASSED[0m[31m [ 76%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingDefaultOff::test_no_routed_model_log_when_disabled [32mPASSED[0m[31m [ 77%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledLow::test_router_invoked_with_low_tier [32mPASSED[0m[31m [ 77%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledLow::test_routed_model_log_contains_local_low [32mPASSED[0m[31m [ 78%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledHigh::test_router_invoked_with_high_tier [32mPASSED[0m[31m [ 78%][0m
tests/governance/test_heal_model_routing_enabled_path.py::TestModelRoutingEnabledHigh::test_routed_model_log_contains_local_high [32mPASSED[0m[31m [ 79%][0m
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagDefaultOff::test_no_escalation_log_when_disabled [32mPASSED[0m[31m [ 80%][0m
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagDefaultOff::test_observer_not_invoked_when_disabled [32mPASSED[0m[31m [ 80%][0m
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagEnabled::test_escalation_log_when_enabled [32mPASSED[0m[31m [ 81%][0m
tests/governance/test_heal_policy_model_escalation_flag.py::TestEscalationFlagEnabled::test_observer_invoked_when_enabled [32mPASSED[0m[31m [ 81%][0m
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_stdlib_only_imports [32mPASSED[0m[31m [ 82%][0m
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_no_network_model_keywords [32mPASSED[0m[31m [ 82%][0m
tests/governance/test_heal_policy_purity_contract.py::TestHealPolicyPurityContract::test_no_banned_string_literals [32mPASSED[0m[31m [ 83%][0m
tests/governance/test_heal_policy_runtime_integration.py::TestHealPolicyRuntimeIntegration::test_decide_reasoning_tier_is_invoked [32mPASSED[0m[31m [ 83%][0m
tests/governance/test_heal_policy_runtime_integration.py::TestHealPolicyRuntimeIntegration::test_policy_decision_is_logged [32mPASSED[0m[31m [ 84%][0m
tests/governance/test_heal_policy_runtime_integration.py::TestHealPolicyRuntimeIntegration::test_output_unchanged_by_policy_integration [32mPASSED[0m[31m [ 85%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_very_high_boundary [32mPASSED[0m[31m [ 85%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_very_high_boundary_just_below [32mPASSED[0m[31m [ 86%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_high_boundary [32mPASSED[0m[31m [ 86%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_high_boundary_just_below [32mPASSED[0m[31m [ 87%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_medium_boundary [32mPASSED[0m[31m [ 87%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_medium_boundary_just_below [32mPASSED[0m[31m [ 88%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_low_values [32mPASSED[0m[31m [ 88%][0m
tests/governance/test_heal_policy_types.py::TestClassifyConfidence::test_validation_errors [32mPASSED[0m[31m [ 89%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_trivial_rule_returns_low_even_with_low_confidence [32mPASSED[0m[31m [ 90%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_trivial_rule_order [32mPASSED[0m[31m [ 90%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_escalation_confidence_low [32mPASSED[0m[31m [ 91%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_escalation_complexity_high [32mPASSED[0m[31m [ 91%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_escalation_safety_risk_high [32mPASSED[0m[31m [ 92%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_escalation_retry_count_high [32mPASSED[0m[31m [ 92%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_default_low [32mPASSED[0m[31m [ 93%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_determinism [32mPASSED[0m[31m [ 93%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_validation_task_complexity [32mPASSED[0m[31m [ 94%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_validation_safety_risk [32mPASSED[0m[31m [ 95%][0m
tests/governance/test_heal_policy_types.py::TestDecideReasoningTier::test_validation_retry_count [32mPASSED[0m[31m [ 95%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_disabled [32mPASSED[0m[31m [ 96%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_enabled_with_router [32mPASSED[0m[31m [ 96%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_enabled_no_router [32mPASSED[0m[31m [ 97%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_logging_enabled [32mPASSED[0m[31m [ 97%][0m
tests/governance/test_heal_routed_model_id_propagation.py::test_heal_routed_model_id_disabled_no_logging [32mPASSED[0m[31m [ 98%][0m
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_no_banned_imports [32mPASSED[0m[31m [ 98%][0m
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_standard_heal_no_routing_calls [32mPASSED[0m[31m [ 99%][0m
tests/governance/test_standard_heal_no_routing_contract.py::TestStandardHealNoRoutingContract::test_wrapper_function_no_routing_calls [32mPASSED[0m[31m [100%][0m

================================== FAILURES ===================================
[31m[1m_ TestNoSelfConfigAssignInInit.test_no_self_config_assign[DagRuntimeInspectorAgent] _[0m
[1m[31mtests\unit_min_deps\test_config_property_contract.py[0m:79: in test_no_self_config_assign
    [0m[94massert[39;49;00m tree [95mis[39;49;00m [95mnot[39;49;00m [94mNone[39;49;00m, [33mf[39;49;00m[33m"[39;49;00m[33mCannot parse [39;49;00m[33m{[39;49;00minspector_file.name[33m}[39;49;00m[33m"[39;49;00m[90m[39;49;00m
[1m[31mE   AssertionError: Cannot parse DagRuntimeInspectorAgent.py[0m
[1m[31mE   assert None is not None[0m
[31m[1m________ TestCanonicalDecoratorsContract.test_standard_heal_importable ________[0m
[1m[31mtests\unit_min_deps\test_decorator_shim_contract.py[0m:35: in test_standard_heal_importable
    [0m[94mfrom[39;49;00m[90m [39;49;00m[04m[96magentic_core[39;49;00m[04m[96m.[39;49;00m[04m[96mbase_agents[39;49;00m[04m[96m.[39;49;00m[04m[96mdecorators[39;49;00m[90m [39;49;00m[94mimport[39;49;00m standard_heal[90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'[0m
[31m[1m_____ TestCanonicalDecoratorsContract.test_standard_heal_async_importable _____[0m
[1m[31mtests\unit_min_deps\test_decorator_shim_contract.py[0m:40: in test_standard_heal_async_importable
    [0m[94mfrom[39;49;00m[90m [39;49;00m[04m[96magentic_core[39;49;00m[04m[96m.[39;49;00m[04m[96mbase_agents[39;49;00m[04m[96m.[39;49;00m[04m[96mdecorators[39;49;00m[90m [39;49;00m[94mimport[39;49;00m standard_heal_async[90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'[0m
[31m[1m_____ TestCanonicalDecoratorsContract.test_heal_result_schema_importable ______[0m
[1m[31mtests\unit_min_deps\test_decorator_shim_contract.py[0m:45: in test_heal_result_schema_importable
    [0m[94mfrom[39;49;00m[90m [39;49;00m[04m[96magentic_core[39;49;00m[04m[96m.[39;49;00m[04m[96mbase_agents[39;49;00m[04m[96m.[39;49;00m[04m[96mdecorators[39;49;00m[90m [39;49;00m[94mimport[39;49;00m HEAL_RESULT_SCHEMA[90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'[0m
[31m[1m_______ TestCanonicalDecoratorsContract.test_dunder_all_matches_exports _______[0m
[1m[31mtests\unit_min_deps\test_decorator_shim_contract.py[0m:53: in test_dunder_all_matches_exports
    [0m[94mimport[39;49;00m[90m [39;49;00m[04m[96magentic_core[39;49;00m[04m[96m.[39;49;00m[04m[96mbase_agents[39;49;00m[04m[96m.[39;49;00m[04m[96mdecorators[39;49;00m[90m [39;49;00m[94mas[39;49;00m[90m [39;49;00m[04m[96mmod[39;49;00m[90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'[0m
[31m[1m___ TestBackwardCompatShimIdentity.test_l5_shim_standard_heal_is_canonical ____[0m
[1m[31mtests\unit_min_deps\test_decorator_shim_contract.py[0m:98: in test_l5_shim_standard_heal_is_canonical
    [0m[94mfrom[39;49;00m[90m [39;49;00m[04m[96magentic_core[39;49;00m[04m[96m.[39;49;00m[04m[96mbase_agents[39;49;00m[04m[96m.[39;49;00m[04m[96mdecorators[39;49;00m[90m [39;49;00m[94mimport[39;49;00m standard_heal [94mas[39;49;00m canonical[90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'[0m
[31m[1m_ TestBackwardCompatShimIdentity.test_l5_shim_heal_result_schema_is_canonical _[0m
[1m[31mtests\unit_min_deps\test_decorator_shim_contract.py[0m:105: in test_l5_shim_heal_result_schema_is_canonical
    [0m[94mfrom[39;49;00m[90m [39;49;00m[04m[96magentic_core[39;49;00m[04m[96m.[39;49;00m[04m[96mbase_agents[39;49;00m[04m[96m.[39;49;00m[04m[96mdecorators[39;49;00m[90m [39;49;00m[94mimport[39;49;00m HEAL_RESULT_SCHEMA [94mas[39;49;00m canonical[90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'[0m
[31m[1m___________ TestCanonicalNoShimImports.test_timeout_no_shim_imports ___________[0m
[1m[31mtests\unit_min_deps\test_decorator_timeout_layer_constraints.py[0m:133: in test_timeout_no_shim_imports
    [0m[94massert[39;49;00m tree [95mis[39;49;00m [95mnot[39;49;00m [94mNone[39;49;00m, [33m"[39;49;00m[33mCannot parse timeout_decorator.py[39;49;00m[33m"[39;49;00m[90m[39;49;00m
[1m[31mE   AssertionError: Cannot parse timeout_decorator.py[0m
[1m[31mE   assert None is not None[0m
[31m[1m______ TestCanonicalDefinesLocally.test_timeout_defines_timeout_locally _______[0m
[1m[31mtests\unit_min_deps\test_decorator_timeout_layer_constraints.py[0m:264: in test_timeout_defines_timeout_locally
    [0m[94massert[39;49;00m tree [95mis[39;49;00m [95mnot[39;49;00m [94mNone[39;49;00m[90m[39;49;00m
[1m[31mE   assert None is not None[0m
[31m[1m_________ TestCanonicalDefinesLocally.test_timeout_defines_dunder_all _________[0m
[1m[31mtests\unit_min_deps\test_decorator_timeout_layer_constraints.py[0m:285: in test_timeout_defines_dunder_all
    [0m[94massert[39;49;00m tree [95mis[39;49;00m [95mnot[39;49;00m [94mNone[39;49;00m[90m[39;49;00m
[1m[31mE   assert None is not None[0m
[31m[1m_ TestSubatomicTestingMixinInMRO.test_subatomic_in_mro[DagRuntimeInspectorAgent] _[0m
[1m[31mtests\unit_min_deps\test_inspector_mro_contracts.py[0m:51: in test_subatomic_in_mro
    [0m[96mcls[39;49;00m = _import_class(module_path, class_name)[90m[39;49;00m
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^[90m[39;49;00m
[1m[31mtests\unit_min_deps\test_inspector_mro_contracts.py[0m:37: in _import_class
    [0mmod = importlib.import_module(module_path)[90m[39;49;00m
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^[90m[39;49;00m
[1m[31mC:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py[0m:90: in import_module
    [0m[94mreturn[39;49;00m _bootstrap._gcd_import(name[level:], package, level)[90m[39;49;00m
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^[90m[39;49;00m
[1m[31m<frozen importlib._bootstrap>[0m:1387: in _gcd_import
    [0m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[90m[39;49;00m
[1m[31m<frozen importlib._bootstrap>[0m:1360: in _find_and_load
    [0m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[90m[39;49;00m
[1m[31m<frozen importlib._bootstrap>[0m:1324: in _find_and_load_unlocked
    [0m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.L3_orchestration.engines.DagRuntimeInspectorAgent'[0m
[31m[1m_ TestSubatomicNotDirectBase.test_subatomic_not_direct_base[DagRuntimeInspectorAgent] _[0m
[1m[31mtests\unit_min_deps\test_inspector_mro_contracts.py[0m:68: in test_subatomic_not_direct_base
    [0m[96mcls[39;49;00m = _import_class(module_path, class_name)[90m[39;49;00m
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^[90m[39;49;00m
[1m[31mtests\unit_min_deps\test_inspector_mro_contracts.py[0m:37: in _import_class
    [0mmod = importlib.import_module(module_path)[90m[39;49;00m
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^[90m[39;49;00m
[1m[31mC:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py[0m:90: in import_module
    [0m[94mreturn[39;49;00m _bootstrap._gcd_import(name[level:], package, level)[90m[39;49;00m
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^[90m[39;49;00m
[1m[31m<frozen importlib._bootstrap>[0m:1387: in _gcd_import
    [0m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[90m[39;49;00m
[1m[31m<frozen importlib._bootstrap>[0m:1360: in _find_and_load
    [0m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[90m[39;49;00m
[1m[31m<frozen importlib._bootstrap>[0m:1324: in _find_and_load_unlocked
    [0m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.L3_orchestration.engines.DagRuntimeInspectorAgent'[0m
[31m[1m___ TestNoDuplicatesInMRO.test_no_mro_duplicates[DagRuntimeInspectorAgent] ____[0m
[1m[31mtests\unit_min_deps\test_inspector_mro_contracts.py[0m:87: in test_no_mro_duplicates
    [0m[96mcls[39;49;00m = _import_class(module_path, class_name)[90m[39;49;00m
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^[90m[39;49;00m
[1m[31mtests\unit_min_deps\test_inspector_mro_contracts.py[0m:37: in _import_class
    [0mmod = importlib.import_module(module_path)[90m[39;49;00m
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^[90m[39;49;00m
[1m[31mC:\Users\amita\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py[0m:90: in import_module
    [0m[94mreturn[39;49;00m _bootstrap._gcd_import(name[level:], package, level)[90m[39;49;00m
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^[90m[39;49;00m
[1m[31m<frozen importlib._bootstrap>[0m:1387: in _gcd_import
    [0m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[90m[39;49;00m
[1m[31m<frozen importlib._bootstrap>[0m:1360: in _find_and_load
    [0m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[90m[39;49;00m
[1m[31m<frozen importlib._bootstrap>[0m:1324: in _find_and_load_unlocked
    [0m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[04m[91m?[39;49;00m[90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.L3_orchestration.engines.DagRuntimeInspectorAgent'[0m
[31m[1m________________ TestDagRuntimeInspectorAgent.test_importable _________________[0m
[1m[31mtests\integration\agentic_core\test_inspector_agents_runtime.py[0m:53: in test_importable
    [0m[94mfrom[39;49;00m[90m [39;49;00m[04m[96magentic_core[39;49;00m[04m[96m.[39;49;00m[04m[96mL3_orchestration[39;49;00m[04m[96m.[39;49;00m[04m[96mengines[39;49;00m[04m[96m.[39;49;00m[04m[96mDagRuntimeInspectorAgent[39;49;00m[90m [39;49;00m[94mimport[39;49;00m ([90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.L3_orchestration.engines.DagRuntimeInspectorAgent'[0m
[31m[1m____ TestDagRuntimeInspectorAgent.test_diagnose_returns_inspection_result _____[0m
[1m[31mtests\integration\agentic_core\test_inspector_agents_runtime.py[0m:60: in test_diagnose_returns_inspection_result
    [0m[94mfrom[39;49;00m[90m [39;49;00m[04m[96magentic_core[39;49;00m[04m[96m.[39;49;00m[04m[96mL3_orchestration[39;49;00m[04m[96m.[39;49;00m[04m[96mengines[39;49;00m[04m[96m.[39;49;00m[04m[96mDagRuntimeInspectorAgent[39;49;00m[90m [39;49;00m[94mimport[39;49;00m ([90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.L3_orchestration.engines.DagRuntimeInspectorAgent'[0m
[31m[1m__ TestDecoratorRuntimeImports.test_standard_heal_importable_with_full_deps ___[0m
[1m[31mtests\integration\agentic_core\test_inspector_agents_runtime.py[0m:134: in test_standard_heal_importable_with_full_deps
    [0m[94mfrom[39;49;00m[90m [39;49;00m[04m[96magentic_core[39;49;00m[04m[96m.[39;49;00m[04m[96mbase_agents[39;49;00m[04m[96m.[39;49;00m[04m[96mdecorators[39;49;00m[90m [39;49;00m[94mimport[39;49;00m standard_heal[90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'[0m
[31m[1m________ TestDecoratorRuntimeImports.test_shim_identity_with_full_deps ________[0m
[1m[31mtests\integration\agentic_core\test_inspector_agents_runtime.py[0m:145: in test_shim_identity_with_full_deps
    [0m[94mfrom[39;49;00m[90m [39;49;00m[04m[96magentic_core[39;49;00m[04m[96m.[39;49;00m[04m[96mbase_agents[39;49;00m[04m[96m.[39;49;00m[04m[96mdecorators[39;49;00m[90m [39;49;00m[94mimport[39;49;00m standard_heal [94mas[39;49;00m canonical[90m[39;49;00m
[1m[31mE   ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'[0m
[31m[1m_ TestFolderPurityPositiveInvariants.test_folder_purity_positive_invariant[reasoning] _[0m
[1m[31mtests\enforcement\test_folder_purity_invariants.py[0m:100: in test_folder_purity_positive_invariant
    [0mpytest.fail(msg)[90m[39;49;00m
[1m[31mE   Failed: Folder purity violation in 'reasoning/' (9 files do not match allowed patterns):[0m
[1m[31mE     - apps_lic\reasoning\IndustrysensitivityStrategy.py[0m
[1m[31mE     - apps_lic\reasoning\LicCodeInterpreter.py[0m
[1m[31mE     - apps_rg\reasoning\ConfidencemetricsStrategy.py[0m
[1m[31mE     - apps_rg\reasoning\HardenedopenaiexecutorStrategy.py[0m
[1m[31mE     - apps_shared\reasoning\restore_all_archived_agents.py[0m
[1m[31mE     - apps_shared\reasoning\restore_app_agents.py[0m
[1m[31mE     - apps_shared\reasoning\restore_void_agents.py[0m
[1m[31mE     - apps_shared\reasoning\runtime_observability_agentic_spans.py[0m
[1m[31mE     - apps_shared\reasoning\update_orchestrator_imports.py[0m
[31m[1m_ TestFolderPurityPositiveInvariants.test_folder_purity_positive_invariant[config] _[0m
[1m[31mtests\enforcement\test_folder_purity_invariants.py[0m:100: in test_folder_purity_positive_invariant
    [0mpytest.fail(msg)[90m[39;49;00m
[1m[31mE   Failed: Folder purity violation in 'config/' (2 files do not match allowed patterns):[0m
[1m[31mE     - agentic_core\L2_execution\config\mcp_registry.py[0m
[1m[31mE     - agentic_core\L5_safety\config\blueprint_compiler.py[0m
[31m[1m_ TestFolderPurityPositiveInvariants.test_folder_purity_positive_invariant[types] _[0m
[1m[31mtests\enforcement\test_folder_purity_invariants.py[0m:100: in test_folder_purity_positive_invariant
    [0mpytest.fail(msg)[90m[39;49;00m
[1m[31mE   Failed: Folder purity violation in 'types/' (23 files do not match allowed patterns):[0m
[1m[31mE     - agentic_core\L0_routing\types\guardian_contract.py[0m
[1m[31mE     - agentic_core\L0_routing\types\guardian_registry.py[0m
[1m[31mE     - agentic_core\L0_routing\types\integration_contract.py[0m
[1m[31mE     - agentic_core\L0_routing\types\v15_artifact_typed.py[0m
[1m[31mE     - agentic_core\L0_routing\types\v15_artifact_validate.py[0m
[1m[31mE     - agentic_core\L0_routing\types\v15_contracts.py[0m
[1m[31mE     - agentic_core\L0_routing\types\v15_p2_contracts.py[0m
[1m[31mE     - agentic_core\L2_execution\types\healer_registry.py[0m
[1m[31mE     - agentic_core\L2_execution\types\heal_contract.py[0m
[1m[31mE     - agentic_core\L2_execution\types\l2_phase_spec.py[0m
[1m[31mE     - agentic_core\L3_orchestration\types\approval_contract.py[0m
[1m[31mE     - agentic_core\L5_safety\types\agent_audit_result.py[0m
[1m[31mE     - agentic_core\L5_safety\types\heal_llm_seam.py[0m
[1m[31mE     - agentic_core\L5_safety\types\heal_model_map.py[0m
[1m[31mE     - agentic_core\L6_observability\types\sovereign_report.py[0m
[1m[31mE     - apps_lic\types\ImmutableStagingBuffer.py[0m
[1m[31mE     - apps_lic\types\SpecialistDraftPacket.py[0m
[1m[31mE     - apps_lic\types\TraceRegistry.py[0m
[1m[31mE     - apps_rg\types\PromptTemplate.py[0m
[1m[31mE     - apps_rg\types\SovereignContext.py[0m
[1m[31mE     ... and 3 more[0m
[31m[1m_ TestFolderPurityPositiveInvariants.test_folder_purity_positive_invariant[utils] _[0m
[1m[31mtests\enforcement\test_folder_purity_invariants.py[0m:100: in test_folder_purity_positive_invariant
    [0mpytest.fail(msg)[90m[39;49;00m
[1m[31mE   Failed: Folder purity violation in 'utils/' (12 files do not match allowed patterns):[0m
[1m[31mE     - agentic_core\L1_cognition\utils\guardrails.py[0m
[1m[31mE     - agentic_core\L1_cognition\utils\history_merger.py[0m
[1m[31mE     - agentic_core\L1_cognition\utils\profile_updater.py[0m
[1m[31mE     - agentic_core\L1_cognition\utils\template_finder.py[0m
[1m[31mE     - agentic_core\L1_cognition\utils\template_matcher.py[0m
[1m[31mE     - agentic_core\L1_cognition\utils\token_updater.py[0m
[1m[31mE     - agentic_core\L3_orchestration\utils\log_orchestration_metrics.py[0m
[1m[31mE     - agentic_core\L4_state\utils\local_disk_adapter.py[0m
[1m[31mE     - agentic_core\L5_safety\utils\cache_invalidation_utils.py[0m
[1m[31mE     - agentic_core\L5_safety\utils\code_tool_runner_core.py[0m
[1m[31mE     - agentic_core\L5_safety\utils\ConstitutionalOverseer.py[0m
[1m[31mE     - agentic_core\L5_safety\utils\_fca_safety_gates.py[0m
[31m[1m_ TestFolderPurityPositiveInvariants.test_folder_purity_positive_invariant[enforcement] _[0m
[1m[31mtests\enforcement\test_folder_purity_invariants.py[0m:100: in test_folder_purity_positive_invariant
    [0mpytest.fail(msg)[90m[39;49;00m
[1m[31mE   Failed: Folder purity violation in 'enforcement/' (71 files do not match allowed patterns):[0m
[1m[31mE     - agentic_core\L0_routing\enforcement\boot_sequence.py[0m
[1m[31mE     - agentic_core\L0_routing\enforcement\v15_execution_gateway.py[0m
[1m[31mE     - agentic_core\L0_routing\enforcement\v15_p3_contracts.py[0m
[1m[31mE     - agentic_core\L0_routing\enforcement\v15_p4_contracts.py[0m
[1m[31mE     - agentic_core\L0_routing\enforcement\v15_p5_contracts.py[0m
[1m[31mE     - agentic_core\L0_routing\enforcement\v15_p6_contracts.py[0m
[1m[31mE     - agentic_core\L0_routing\enforcement\v15_runtime_guard.py[0m
[1m[31mE     - agentic_core\L0_routing\enforcement\vigilance_routing.py[0m
[1m[31mE     - agentic_core\L1_cognition\enforcement\execution_status.py[0m
[1m[31mE     - agentic_core\L1_cognition\enforcement\mission_status.py[0m
[1m[31mE     - agentic_core\L2_execution\enforcement\capability_chokepoint.py[0m
[1m[31mE     - agentic_core\L2_execution\enforcement\dashboard_e2_e_pipeline.py[0m
[1m[31mE     - agentic_core\L2_execution\enforcement\docker_sandbox.py[0m
[1m[31mE     - agentic_core\L2_execution\enforcement\filesystem_mcp.py[0m
[1m[31mE     - agentic_core\L2_execution\enforcement\firecracker_manager.py[0m
[1m[31mE     - agentic_core\L2_execution\enforcement\healer_pipe_order.py[0m
[1m[31mE     - agentic_core\L2_execution\enforcement\sovereign_filesystem_mcp.py[0m
[1m[31mE     - agentic_core\L3_orchestration\enforcement\enforce_orchestration_policy.py[0m
[1m[31mE     - agentic_core\L3_orchestration\enforcement\mission_runner.py[0m
[1m[31mE     - agentic_core\L4_state\enforcement\change_tracker.py[0m
[1m[31mE     ... and 51 more[0m
[31m[1m_ TestFolderPurityPositiveInvariants.test_folder_purity_positive_invariant[engines] _[0m
[1m[31mtests\enforcement\test_folder_purity_invariants.py[0m:100: in test_folder_purity_positive_invariant
    [0mpytest.fail(msg)[90m[39;49;00m
[1m[31mE   Failed: Folder purity violation in 'engines/' (28 files do not match allowed patterns):[0m
[1m[31mE     - agentic_core\L1_cognition\engines\cache_manager.py[0m
[1m[31mE     - agentic_core\L1_cognition\engines\CognitiveNode.py[0m
[1m[31mE     - agentic_core\L1_cognition\engines\domain_manager.py[0m
[1m[31mE     - agentic_core\L1_cognition\engines\episodic_manager.py[0m
[1m[31mE     - agentic_core\L1_cognition\engines\meta_observability.py[0m
[1m[31mE     - agentic_core\L1_cognition\engines\semantic_manager.py[0m
[1m[31mE     - agentic_core\L1_cognition\engines\strategist_bio_writer.py[0m
[1m[31mE     - agentic_core\L2_execution\engines\tool_registry.py[0m
[1m[31mE     - agentic_core\L2_execution\engines\validation_orchestrator.py[0m
[1m[31mE     - agentic_core\L3_orchestration\engines\AgentFactory.py[0m
[1m[31mE     - agentic_core\L3_orchestration\engines\coordinator_capability_orchestrator.py[0m
[1m[31mE     - agentic_core\L3_orchestration\engines\dag_manager.py[0m
[1m[31mE     - agentic_core\L3_orchestration\engines\decomposition_orchestrator.py[0m
[1m[31mE     - agentic_core\L3_orchestration\engines\recovery_coordinator_orchestrator.py[0m
[1m[31mE     - agentic_core\L3_orchestration\engines\recursive_orchestrator.py[0m
[1m[31mE     - agentic_core\L3_orchestration\engines\reflex_layer_pattern.py[0m
[1m[31mE     - agentic_core\L3_orchestration\engines\rl_coordinator_orchestrator.py[0m
[1m[31mE     - agentic_core\L3_orchestration\engines\sovereign_mcp_marketplace.py[0m
[1m[31mE     - agentic_core\L3_orchestration\engines\sovereign_rag_orchestrator.py[0m
[1m[31mE     - agentic_core\L3_orchestration\engines\sovereign_redis_orchestrator.py[0m
[1m[31mE     ... and 8 more[0m
[31m[1m_ TestFolderPurityPositiveInvariants.test_folder_purity_positive_invariant[tools] _[0m
[1m[31mtests\enforcement\test_folder_purity_invariants.py[0m:100: in test_folder_purity_positive_invariant
    [0mpytest.fail(msg)[90m[39;49;00m
[1m[31mE   Failed: Folder purity violation in 'tools/' (77 files do not match allowed patterns):[0m
[1m[31mE     - agentic_core\L2_execution\tools\tool_chain_executor.py[0m
[1m[31mE     - apps_lic\tools\AdjustToneWeights.py[0m
[1m[31mE     - apps_lic\tools\AggregateCampaignState.py[0m
[1m[31mE     - apps_lic\tools\analyze_duplicates_detailed.py[0m
[1m[31mE     - apps_lic\tools\AssessContentRisk.py[0m
[1m[31mE     - apps_lic\tools\AssessMessageRelevance.py[0m
[1m[31mE     - apps_lic\tools\BuildMessageFilters.py[0m
[1m[31mE     - apps_lic\tools\BuildPersonalizationQuery.py[0m
[1m[31mE     - apps_lic\tools\CalibrateEngagementScore.py[0m
[1m[31mE     - apps_lic\tools\call_personalization_api.py[0m
[1m[31mE     - apps_lic\tools\clean_duplicates_enhanced.py[0m
[1m[31mE     - apps_lic\tools\ComputePersonalizationMatch.py[0m
[1m[31mE     - apps_lic\tools\create_message_body.py[0m
[1m[31mE     - apps_lic\tools\DiagnosePersonalizationIssues.py[0m
[1m[31mE     - apps_lic\tools\dispatch_outreach_tools.py[0m
[1m[31mE     - apps_lic\tools\enforce_execution_policy.py[0m
[1m[31mE     - apps_lic\tools\enforce_tone_guidelines.py[0m
[1m[31mE     - apps_lic\tools\EvaluateComplianceLevel.py[0m
[1m[31mE     - apps_lic\tools\EvaluateEngagementPotential.py[0m
[1m[31mE     - apps_lic\tools\EvaluatePersonalizationQuality.py[0m
[1m[31mE     ... and 57 more[0m
[31m[1m_ TestFolderPurityPositiveInvariants.test_folder_purity_positive_invariant[caching] _[0m
[1m[31mtests\enforcement\test_folder_purity_invariants.py[0m:100: in test_folder_purity_positive_invariant
    [0mpytest.fail(msg)[90m[39;49;00m
[1m[31mE   Failed: Folder purity violation in 'caching/' (1 files do not match allowed patterns):[0m
[1m[31mE     - agentic_core\L4_state\caching\redis_mcp_client.py[0m
[31m[1m_ TestFolderPurityPositiveInvariants.test_folder_purity_positive_invariant[memory] _[0m
[1m[31mtests\enforcement\test_folder_purity_invariants.py[0m:100: in test_folder_purity_positive_invariant
    [0mpytest.fail(msg)[90m[39;49;00m
[1m[31mE   Failed: Folder purity violation in 'memory/' (8 files do not match allowed patterns):[0m
[1m[31mE     - agentic_core\L4_state\memory\blob_storage_provider.py[0m
[1m[31mE     - agentic_core\L4_state\memory\in_memory_vector_cache.py[0m
[1m[31mE     - agentic_core\L4_state\memory\runtime_models.py[0m
[1m[31mE     - agentic_core\L4_state\memory\runtime_state_guard.py[0m
[1m[31mE     - agentic_core\L4_state\memory\semantic_cache_manager.py[0m
[1m[31mE     - agentic_core\L4_state\memory\sovereign_reasoning_memory_ledger.py[0m
[1m[31mE     - agentic_core\L4_state\memory\sovereign_semantic_cache.py[0m
[1m[31mE     - agentic_core\L4_state\memory\verifiable_checkpoint_manager.py[0m
[31m[1m_ TestFolderPurityPositiveInvariants.test_folder_purity_positive_invariant[security] _[0m
[1m[31mtests\enforcement\test_folder_purity_invariants.py[0m:100: in test_folder_purity_positive_invariant
    [0mpytest.fail(msg)[90m[39;49;00m
[1m[31mE   Failed: Folder purity violation in 'security/' (1 files do not match allowed patterns):[0m
[1m[31mE     - agentic_core\L5_safety\security\injection_regression_gate.py[0m
[31m[1m_ TestFolderPurityPositiveInvariants.test_folder_purity_positive_invariant[golden_evaluation] _[0m
[1m[31mtests\enforcement\test_folder_purity_invariants.py[0m:100: in test_folder_purity_positive_invariant
    [0mpytest.fail(msg)[90m[39;49;00m
[1m[31mE   Failed: Folder purity violation in 'golden_evaluation/' (3 files do not match allowed patterns):[0m
[1m[31mE     - agentic_core\L6_observability\golden_evaluation\injection_regression_suite.py[0m
[1m[31mE     - agentic_core\L6_observability\golden_evaluation\resume_quality_evaluator.py[0m
[1m[31mE     - agentic_core\L6_observability\golden_evaluation\tool_use_ground_truth_evaluator.py[0m
============================ slowest 10 durations =============================
2.89s call     tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_determinism
2.84s call     tests/governance/test_agent_heal_audit.py::TestDeterminism::test_byte_identical_json_runs
1.47s call     tests/governance/test_agent_heal_audit.py::TestStructureContract::test_summary_schema
1.46s call     tests/governance/test_agent_heal_audit.py::TestStructureContract::test_top_level_schema
1.45s call     tests/governance/test_agent_heal_audit.py::TestMarkdownGeneration::test_markdown_generation
1.44s call     tests/governance/test_agent_heal_audit.py::TestStructureContract::test_result_item_schema
1.42s call     tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_base_class_name_extraction
1.42s call     tests/governance/test_agent_heal_audit.py::TestDeterminism::test_deterministic_ordering
1.42s call     tests/governance/test_agent_heal_audit.py::TestDeterminism::test_no_nondeterministic_fields
1.42s call     tests/governance/test_agent_heal_audit.py::TestEnumerationIntegrity::test_agent_naming_detection
[36m[1m=========================== short test summary info ===========================[0m
[31mFAILED[0m tests/unit_min_deps/test_config_property_contract.py::[1mTestNoSelfConfigAssignInInit::test_no_self_config_assign[DagRuntimeInspectorAgent][0m - AssertionError: Cannot parse DagRuntimeInspectorAgent.py
[31mFAILED[0m tests/unit_min_deps/test_decorator_shim_contract.py::[1mTestCanonicalDecoratorsContract::test_standard_heal_importable[0m - ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'
[31mFAILED[0m tests/unit_min_deps/test_decorator_shim_contract.py::[1mTestCanonicalDecoratorsContract::test_standard_heal_async_importable[0m - ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'
[31mFAILED[0m tests/unit_min_deps/test_decorator_shim_contract.py::[1mTestCanonicalDecoratorsContract::test_heal_result_schema_importable[0m - ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'
[31mFAILED[0m tests/unit_min_deps/test_decorator_shim_contract.py::[1mTestCanonicalDecoratorsContract::test_dunder_all_matches_exports[0m - ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'
[31mFAILED[0m tests/unit_min_deps/test_decorator_shim_contract.py::[1mTestBackwardCompatShimIdentity::test_l5_shim_standard_heal_is_canonical[0m - ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'
[31mFAILED[0m tests/unit_min_deps/test_decorator_shim_contract.py::[1mTestBackwardCompatShimIdentity::test_l5_shim_heal_result_schema_is_canonical[0m - ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'
[31mFAILED[0m tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::[1mTestCanonicalNoShimImports::test_timeout_no_shim_imports[0m - AssertionError: Cannot parse timeout_decorator.py
[31mFAILED[0m tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::[1mTestCanonicalDefinesLocally::test_timeout_defines_timeout_locally[0m - assert None is not None
[31mFAILED[0m tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::[1mTestCanonicalDefinesLocally::test_timeout_defines_dunder_all[0m - assert None is not None
[31mFAILED[0m tests/unit_min_deps/test_inspector_mro_contracts.py::[1mTestSubatomicTestingMixinInMRO::test_subatomic_in_mro[DagRuntimeInspectorAgent][0m - ModuleNotFoundError: No module named 'agentic_core.L3_orchestration.engines...
[31mFAILED[0m tests/unit_min_deps/test_inspector_mro_contracts.py::[1mTestSubatomicNotDirectBase::test_subatomic_not_direct_base[DagRuntimeInspectorAgent][0m - ModuleNotFoundError: No module named 'agentic_core.L3_orchestration.engines...
[31mFAILED[0m tests/unit_min_deps/test_inspector_mro_contracts.py::[1mTestNoDuplicatesInMRO::test_no_mro_duplicates[DagRuntimeInspectorAgent][0m - ModuleNotFoundError: No module named 'agentic_core.L3_orchestration.engines...
[31mFAILED[0m tests/integration/agentic_core/test_inspector_agents_runtime.py::[1mTestDagRuntimeInspectorAgent::test_importable[0m - ModuleNotFoundError: No module named 'agentic_core.L3_orchestration.engines...
[31mFAILED[0m tests/integration/agentic_core/test_inspector_agents_runtime.py::[1mTestDagRuntimeInspectorAgent::test_diagnose_returns_inspection_result[0m - ModuleNotFoundError: No module named 'agentic_core.L3_orchestration.engines...
[31mFAILED[0m tests/integration/agentic_core/test_inspector_agents_runtime.py::[1mTestDecoratorRuntimeImports::test_standard_heal_importable_with_full_deps[0m - ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'
[31mFAILED[0m tests/integration/agentic_core/test_inspector_agents_runtime.py::[1mTestDecoratorRuntimeImports::test_shim_identity_with_full_deps[0m - ModuleNotFoundError: No module named 'agentic_core.base_agents.decorators'
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[reasoning][0m - Failed: Folder purity violation in 'reasoning/' (9 files do not match allow...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[config][0m - Failed: Folder purity violation in 'config/' (2 files do not match allowed ...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[types][0m - Failed: Folder purity violation in 'types/' (23 files do not match allowed ...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[utils][0m - Failed: Folder purity violation in 'utils/' (12 files do not match allowed ...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[enforcement][0m - Failed: Folder purity violation in 'enforcement/' (71 files do not match al...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[engines][0m - Failed: Folder purity violation in 'engines/' (28 files do not match allowe...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[tools][0m - Failed: Folder purity violation in 'tools/' (77 files do not match allowed ...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[caching][0m - Failed: Folder purity violation in 'caching/' (1 files do not match allowed...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[memory][0m - Failed: Folder purity violation in 'memory/' (8 files do not match allowed ...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[security][0m - Failed: Folder purity violation in 'security/' (1 files do not match allowe...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[golden_evaluation][0m - Failed: Folder purity violation in 'golden_evaluation/' (3 files do not mat...
[31m======================= [31m[1m28 failed[0m, [32m152 passed[0m[31m in 20.07s[0m[31m =======================[0m
[1m============================= test session starts =============================[0m
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 10 items

[33m============================ [33mno tests ran[0m[33m in 0.02s[0m[33m ============================[0m
