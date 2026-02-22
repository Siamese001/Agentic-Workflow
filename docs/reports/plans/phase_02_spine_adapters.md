# Phase 2: LIC + RG Spine Adapters (Deterministic CID) + Proof

## Scope
- Implement LIC and RG spine adapters with deterministic CID derivation
- Add unit_min_deps tests for both adapters verifying CID determinism and call order
- Ensure adapters route through ExecutionOrchestrator with proper CID registration
- No PowerShell usage, no baseline expansions

## Evidence

### LIC Unit Tests
```
Command: python -m pytest -q tests/unit_min_deps/test_apps_lic_spine_adapter.py
Exit code: 0
Output:
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: c:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_adapter_returns_cid PASSED [ 14%]
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_has_lic_prefix PASSED [ 28%]
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_is_deterministic PASSED [ 42%]
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_different_inputs_produce_different_cids PASSED [ 57%]
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_registered_before_orchestrator_execute PASSED [ 71%]
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_cid_passed_to_orchestrator PASSED [ 85%]
tests/unit_min_deps/test_apps_lic_spine_adapter.py::test_adapter_state_success_on_clean_input PASSED [100%]

============================== 7 passed in 0.08s ==============================
```

### RG Unit Tests
```
Command: python -m pytest -q tests/unit_min_deps/test_apps_rg_spine_adapter.py
Exit code: 0
Output:
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0
rootdir: c:\Git\Agentic-Workflow
configfile: pytest.ini (WARNING: ignoring pytest config in pyproject.toml!)
plugins: anyio-4.12.1, asyncio-1.3.0, cov-7.0.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 7 items

tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_adapter_returns_cid PASSED [ 14%]
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_has_rg_prefix PASSED [ 28%]
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_is_deterministic PASSED [ 42%]
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_different_inputs_produce_different_cids PASSED [ 57%]
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_registered_before_orchestrator_execute PASSED [ 71%]
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_cid_passed_to_orchestrator PASSED [ 85%]
tests/unit_min_deps/test_apps_rg_spine_adapter.py::test_adapter_state_success_on_clean_input PASSED [100%]

============================== 7 passed in 0.07s ==============================
```

### Full Test Suite
```
Command: python -m pytest -q
Exit code: 0
Output: 1145 passed, 4 warnings in 61.27s (0:01:01)
```

### Spine Bypass Check
```
Command: python ops_scripts/ci/check_spine_bypass.py
Exit code: 0
Output: [OK] Spine bypass + randomness guard: 0 new violations (1185 files scanned, 286 baselined)
```

## Files Changed

### New Files
- `apps_rg/engines/rg_spine_adapter.py` - RG spine adapter with deterministic CID
- `tests/unit_min_deps/test_apps_rg_spine_adapter.py` - Unit tests for RG adapter
- `tools/evidence/phase02_spine_adapters_evidence_runner.py` - Evidence runner script

### Modified Files
- `apps_lic/engines/lic_spine_adapter.py` - Updated to use deterministic CID utilities
- `tests/unit_min_deps/test_apps_lic_spine_adapter.py` - Updated tests with proper mocking
- `apps_rg/engines/__init__.py` - Removed non-existent imports

## Implementation Details

### LIC Adapter
- Uses `strip_nondeterministic` and `canonical_hash` from `apps_shared.utils.determinism_util`
- Derives CID as "lic-" + 16-char hash prefix
- Registers CID with `CIDRegistry.new_cycle` before orchestrator execution
- Passes enriched intent_input with `_cid` and `_cycle_attempt` to orchestrator

### RG Adapter
- Mirrors LIC adapter implementation with "rg-" prefix
- Same deterministic CID derivation workflow
- Includes null-object stubs for unwired components
- Full assembler adapter with manifest hash generation

### Tests
- Verify CID presence and correct prefixes
- Prove CID determinism with identical inputs
- Ensure different inputs produce different CIDs
- Validate call order: CIDRegistry.new_cycle before ExecutionOrchestrator.execute
- Confirm enriched intent_input contains CID fields

## Final Commit Hash
ec94d3e8af85e3f577cb7c70828786d091531986

## Compliance
- ✅ No PowerShell usage
- ✅ No baseline expansions
- ✅ All tests pass
- ✅ Spine bypass check passes
- ✅ Deterministic CID implementation
- ✅ Proper unit test coverage
