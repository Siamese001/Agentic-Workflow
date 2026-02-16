# Execute SSOT Folder Purity Phase 14 Evidence

## Wave 14.1 — Repro + Root Cause Triage (No Code Changes)

### 1. pytest -q output

20 failed, 175 passed in 19.30s

### 2. Root Cause Analysis

**Import Errors (fixed during triage):**
- `agentic_core.prompt_governance.security.__init__.py` had stale imports to moved files
- `agentic_core.prompt_governance.security.detectors.__init__.py` had wrong export name
- `agentic_core.prompt_governance.security.validators.__init__.py` had wrong export name
- `agentic_core.prompt_governance.security.utils.__init__.py` had circular import

**Remaining Issues:**
1. `DagRuntimeInspectorAgent` - module doesn't exist (5 test failures) - FIXED (wrong path in tests)
2. `timeout_decorator.py` - parsing issues (3 test failures) - FIXED (wrong path in tests)
3. Folder purity invariants - 11 folders with violations (11 test failures) - PRE-EXISTING
4. `test_no_self_config_assign[DagRuntimeInspectorAgent]` - file doesn't exist (1 test failure) - FIXED

---

## Wave 14.2 — Restore Import Contracts

### 1. Import Fixes Applied

- `agentic_core/prompt_governance/security/__init__.py` - Updated to import from detectors/
- `agentic_core/prompt_governance/security/detectors/__init__.py` - Fixed export (PIIScrubber not scrub_pii)
- `agentic_core/prompt_governance/security/validators/__init__.py` - Fixed export (validate_against_schema not OutputSchemaValidator)
- `agentic_core/prompt_governance/security/utils/__init__.py` - Removed circular imports

### 2. Test Path Fixes

- `tests/unit_min_deps/test_inspector_mro_contracts.py` - Fixed DagRuntimeInspectorAgent path (engines -> reasoning)
- `tests/integration/agentic_core/test_inspector_agents_runtime.py` - Fixed DagRuntimeInspectorAgent path
- `tests/unit_min_deps/test_config_property_contract.py` - Fixed DagRuntimeInspectorAgent path
- `tests/unit_min_deps/test_decorator_timeout_layer_constraints.py` - Fixed timeout_decorator path

### 3. Test Results After Import Fixes

11 failed, 184 passed - All failures are folder purity invariant violations (pre-existing)

