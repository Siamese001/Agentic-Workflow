# Prompt Governance Security Purity Phase 1 Evidence

## Wave 1.1 — Inventory + Baseline (No Changes)

### 1. Inventory: prompt_governance/security folder

Root files found:
- `__init__.py`
- `injection_detector.py`
- `injection_scan_util.py`
- `normalization_util.py`
- `output_schema_validator.py`
- `pii_scrubber.py`

Subfolders:
- `adversarial/`
- `__pycache__/`

Files to move (utils):
- `injection_scan_util.py`
- `normalization_util.py`

### 2. Baseline pytest

[31mFAILED[0m tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::[1mTestCanonicalNoShimImports::test_timeout_no_shim_imports[0m - AssertionError: Cannot parse timeout_decorator.py
[31mFAILED[0m tests/unit_min_deps/test_decorator_timeout_layer_constraints.py::[1mTestCanonicalDefinesLocally::test_timeout_defines_timeout_locally[0m - assert None is not None
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[caching][0m - Failed: Folder purity violation in 'caching/' (1 files do not match allowed...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[memory][0m - Failed: Folder purity violation in 'memory/' (8 files do not match allowed ...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[security][0m - Failed: Folder purity violation in 'security/' (1 files do not match allowe...
[31mFAILED[0m tests/enforcement/test_folder_purity_invariants.py::[1mTestFolderPurityPositiveInvariants::test_folder_purity_positive_invariant[golden_evaluation][0m - Failed: Folder purity violation in 'golden_evaluation/' (3 files do not mat...
[31m======================= [31m[1m20 failed[0m, [32m170 passed[0m[31m in 20.68s[0m[31m =======================

---

## Wave 1.2 — Governance Rule: No Root Files for prompt_governance/security

### 1. Rules Added to classification.py

```python
NO_ROOT_FILES_FOLDERS: Final[frozenset[str]] = frozenset({
    "security",  # prompt_governance/security - utils must be in security/utils/
})

APPROVED_SUBFOLDERS: Final[Mapping[str, frozenset[str]]] = {
    "security": frozenset({"utils", "detectors", "schemas", "validators", "adversarial"}),
}
```

### 2. Enforcement Added to FileClassificationAgent._enforce_folder_purity()

Lines 2216-2227: Files directly under NO_ROOT_FILES_FOLDERS => FAIL with NO_ROOT_FILES_VIOLATION

### 3. Tests Added (3 new tests)

- test_security_in_no_root_files_folders
- test_security_has_approved_subfolders
- test_no_root_files_violation_detected

### 4. Test Results (13 passed)

```
tests/enforcement/test_folder_purity_governance.py - 13 passed in 0.19s
```

---

## Wave 1.3 — File Moves: security/*.py -> security/utils/*.py + Import Updates

### 1. Files Moved

```bash
git mv agentic_core/prompt_governance/security/injection_scan_util.py -> agentic_core/prompt_governance/security/utils/injection_scan_util.py
git mv agentic_core/prompt_governance/security/normalization_util.py -> agentic_core/prompt_governance/security/utils/normalization_util.py
```

### 2. Created __init__.py

`agentic_core/prompt_governance/security/utils/__init__.py`

### 3. Imports Updated (7 files)

- agentic_core/L3_orchestration/engines/sub_atomic_engine_impl.py
- agentic_core/L5_safety/enforcement/canary_token_defense_strategy.py
- agentic_core/mixins/instructional_injection_mixin.py
- agentic_core/prompt_governance/security/injection_detector.py
- tests/unit/agentic_core/L2_execution/enforcement/test_gateway_output_injection_scan.py
- tests/unit/agentic_core/prompt_governance/security/test_injection_wiring_non_fenced_joinpoints.py
- tests/unit/agentic_core/prompt_governance/security/test_injection_normalization_util.py

### 4. rg proof: No remaining old import paths

```bash
grep "prompt_governance\.security\.injection_scan_util|prompt_governance\.security\.normalization_util" -> No results found
```

### 5. Test Results (13 passed)

```
tests/enforcement/test_folder_purity_governance.py - 13 passed in 0.14s
