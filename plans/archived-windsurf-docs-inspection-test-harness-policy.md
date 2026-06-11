---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\inspection-test-harness-policy.md'
original_relative_path: 'inspection-test-harness-policy.md'
source_sha256: 99e50617b314a28c7773a98b27395da72aca4e521517fc0a231f451aefcf12ee
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Inspection Test Harness — Policy Decision Record

**Date**: 2026-02-08
**Scope**: `DagRuntimeInspectorAgent`, `TokenBudgetInspectorAgent`, `SignatureVerifierAgent`
**Status**: Implemented

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Decision: AST Structural + Stub Behavioral Tests (No Runtime Agent Import)

### Context

The three inspector agents inherit from `InspectionCapability` (a lightweight
stdlib-only mixin) but also inherit from `SovereignBaseAgent`, which transitively
pulls in `pydantic`, `redis`, `requests`, and other optional dependencies not
present in the unit test environment.

Attempting to `import DagRuntimeInspectorAgent` at test time fails with:

```
ModuleNotFoundError: No module named 'pydantic'
```

This caused the original tests to **silently skip** (via `pytest.skip()` in
fixtures), producing a false-green test suite.

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **A. Install all deps in test env** | Tests real agents at runtime | Bloats unit env with redis/pydantic/requests; couples unit tests to infra |
| **B. Refactor agents for lazy imports** | Agents importable without heavy deps | Large refactor across 120+ agent files; breaks existing import contracts |
| **C. AST structural + stub behavioral** | Zero-dep, deterministic, fast | Tests shape not full runtime semantics; stub tests the mixin contract, not agent-specific logic |
| **D. Separate integration test job** | Full runtime coverage in CI | Requires CI infra changes; doesn't solve local dev story |

### Decision

**Option C (AST + stub) for unit tests**, with the following compensations:

1. **AST structural checks** verify agent shape without import:
   - Class exists at expected filesystem path
   - Inherits from `InspectionCapability` and `SubatomicTestingMixin`
   - Implements `perform_checks`, `diagnose`, `heal_repository`, `heal`
   - Sets `INSPECTION_LOG_PREFIX` as non-empty string constant
   - `diagnose()` delegates to `run_inspection()` (source grep)
   - Return type annotation is `InspectionResult` (AST node check)
   - No legacy `execute()` method present

2. **Stub behavioral tests** verify `InspectionCapability` contract:
   - Lightweight `InspectionCapability` subclass mimics agent's `perform_checks()` logic
   - `run_inspection()` returns `InspectionResult` with correct `.healthy`, `.issues`, `.metrics`
   - `make_heal_result()` returns canonical heal schema

3. **Post-cleanup invariants** guard against regression:
   - No `DiagnosticReport` class in `inspection_capability.py`
   - No `to_diagnostic_report()` method on `InspectionResult`
   - No agent imports `DiagnosticReport` from `inspection_capability`
   - All agents annotate `diagnose() -> InspectionResult`
   - No inspector agent defines `execute()`

### What These Tests Do NOT Cover

- **Runtime MRO correctness**: Conditional imports or metaclass conflicts at runtime
- **Side-effect-free import boundaries**: Requires actual import in deps-available env
- **Agent-specific business logic**: Stubs replicate `perform_checks()` shape, not full domain logic
- **Decorator behavior**: `@standard_heal` and `@timeout` wrapping behavior in context

### Recommended Future Compensations

1. **Integration test job in CI** (Option D) that installs full deps and runs
   `pytest tests/integration/` with actual agent imports. This would catch MRO
   and runtime-import failures.
2. **Import-time smoke test**: A lightweight test that attempts
   `importlib.import_module()` for each agent in a deps-available environment.
   Can be gated on an env var (`FULL_DEPS=1`) so it doesn't block local dev.

### Environment Constraints

- **Unit test env**: Python 3.12, pytest, stdlib only (no pydantic/redis/requests)
- **CI env**: TBD — should include full deps for integration tests
- **Local dev**: Developers may or may not have optional deps installed

### Test Classification

| Test Class | Type | What It Validates |
|------------|------|-------------------|
| `Test*StructuralContract` | Structural contract | Agent shape via AST |
| `TestInspectionCapabilityContractVia*Stub` | Behavioral contract | Mixin contract via stub |
| `TestNoLegacyAdapterTypes` | Regression invariant | No re-introduction of removed types |
| `TestDiagnoseReturnsInspectionResult` | Regression invariant | Return type + no legacy methods |
| `TestDecoratorsShimContract` | Import contract | Shim re-export correctness |

### Breaking Change: DiagnosticReport Removal

`DiagnosticReport` and `to_diagnostic_report()` were removed from
`inspection_capability.py` in commit `a108f9ff2`. This is a breaking change.

**Migration proof** (repo-wide):
- `grep -r "from agentic_core.mixins.inspection_capability import.*DiagnosticReport"` → 0 results
- `grep -r "to_diagnostic_report"` → 0 results
- Remaining `DiagnosticReport` references (6 files) all import from `shared.result_types` — an independent type in apps territory

No deprecation shim was needed because there were zero consumers.

### Breaking Change: execute() Removal

`SignatureVerifierAgent.execute()` was removed in the same commit. It was a
buggy legacy adapter (referenced undefined `OperationResult` type and undefined
`result` variable in the original code). No other inspector agent had `execute()`.

**Migration proof**:
- AST scan of all 3 inspector agents confirms no `execute()` method
- No test or production code called `SignatureVerifierAgent().execute()`

### Phantom Import Resolution (Issue #5)

During investigation, discovered that `agentic_core/base_agents/decorators.py`
and `agentic_core/base_agents/timeout_decorator.py` did not exist despite being
imported by 54 and 67 files respectively.

**Root cause**: Modules were relocated to canonical locations during a prior
refactor but import paths were never updated.

**Fix**: Created shim modules that re-export from canonical locations:
- `base_agents/decorators.py` → re-exports from `L5_safety/utils/decorators_util.py`
- `base_agents/timeout_decorator.py` → re-exports from `L0_maintenance/utils/timeout_decorator_util.py`

**Contract tests**: `test_decorator_shim_contract.py` (11 tests) verifies shim
correctness and identity with canonical implementations.

**Known architectural debt — layer inversion**:

The current shim direction creates layer inversion: `base_agents/decorators.py`
imports from `L5_safety/utils/decorators_util.py`, meaning the foundational
`base_agents` package depends on a higher layer (L5).

Per `SOVEREIGN_TERRITORIES`, decorators belong in `base_agents`:
```
"base_agents": {
    "purpose": "STRICT IDENTITY ONLY. Sovereign base classes, layer bases, and decorators.",
```

The implementation in `decorators_util.py` uses only stdlib (no L5-specific
dependencies), so it can be moved without breaking layer constraints.

**Remediation plan** (tracked, not blocking):
1. Move canonical implementation from `L5_safety/utils/decorators_util.py` to
   `base_agents/decorators.py`
2. Convert `L5_safety/utils/decorators_util.py` to a backward-compat shim
3. Update 53 direct importers of the L5 location to use `base_agents` path
4. Add layer-constraint enforcement to pre-commit hooks

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

