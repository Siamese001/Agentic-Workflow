# Test Contract

Single-page reference for the governed test topology.

## Default `pytest` Behavior

```bash
pytest -q
```

Collects **only** from the explicit `testpaths` in `pytest.ini`:

| Testpath | Description |
|---|---|
| `tests/unit_min_deps` | Contract/structural tests — stdlib + pytest only, zero optional deps |
| `tests/integration/agentic_core` | Integration tests for agentic_core agents — may require pydantic |

No other directories are collected by default. `--strict-markers` is enforced.

## Nox Sessions

| Session | Command | Scope |
|---|---|---|
| `unit_min_deps` | `nox -s unit_min_deps` | `tests/unit_min_deps/` |
| `integration` | `nox -s integration` | `tests/integration/agentic_core/` (installs pydantic) |
| `decorators` | `nox -s decorators` | Decorator/timeout AST enforcement subset |
| `legacy_unit` | `nox -s legacy_unit` | `tests/unit/` — legacy, NOT default |

## Running Legacy Suites

Legacy test directories exist but are **not** collected by default:

```bash
# Legacy unit tests (may have optional-dep failures)
pytest tests/unit/ -q

# E2E tests
pytest tests/e2e/ -q

# Guardian tests
pytest tests/guardian/ -q
```

These must be invoked explicitly by path.

## Quarantine Policy

Broken tests live in `tests/_quarantine/`. This directory is in `norecursedirs` and is **never** collected.

### Adding a test to quarantine

1. Move the file to `tests/_quarantine/` (preserve relative path structure).
2. Add an entry to `tests/_quarantine/QUARANTINE_MANIFEST.json` with:
   - `path` — relative to repo root, forward slashes
   - `category` — one of: `missing_dep`, `missing_module`, `assertion_rot`, `infra_required`, `runtime_error`
   - `primary_dep` — the blocking dependency or module
   - `re_enable` — one-phrase criteria to un-quarantine
3. The contract test `tests/unit_min_deps/test_quarantine_manifest_contract.py` enforces bidirectional sync.

### Re-enabling a quarantined test

1. Fix the root cause (install dep, restore module, update assertions).
2. Move the file back to `tests/integration/agentic_core/` (or appropriate testpath).
3. Remove the entry from `QUARANTINE_MANIFEST.json`.
4. Run `pytest -q` to verify clean collection.

## Governance Contract Tests

| Contract | File | Enforces |
|---|---|---|
| MRO guard | `test_inspector_mro_contracts.py` | Inspector agent MRO invariants |
| Config property | `test_config_property_contract.py` | No `self.config` overwrite in `__init__` |
| Topology | `test_testpaths_contract.py` | pytest.ini header, testpaths, norecursedirs |
| Quarantine manifest | `test_quarantine_manifest_contract.py` | Bidirectional disk↔manifest sync |
| Marker registry | `test_marker_registry_contract.py` | All used markers registered, sorted, no duplicates |
| Decorator shim | `test_decorator_shim_contract.py` | Canonical decorator imports, shim identity |
| Decorator layers | `test_decorator_timeout_layer_constraints.py` | No shim imports repo-wide |
