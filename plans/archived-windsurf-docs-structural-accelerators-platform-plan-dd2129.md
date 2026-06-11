---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\structural-accelerators-platform-plan-dd2129.md'
original_relative_path: 'structural-accelerators-platform-plan-dd2129.md'
source_sha256: 1c8e93ea00a5925f99ea02b6337d86720045cc8e10d57a7a233fa6bacba21852
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-10'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Structural Accelerators Platform Build-Out

Single-pass implementation of nine governed accelerators wired into the Structure Blueprint SSOT, eliminating hardcoded artifact paths, establishing a central registry of derivation contracts, and integrating each accelerator with the existing AST dependency graph.

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


## Section 1 — Current State Inventory

### What Exists

| Artifact | Location | Status | SSOT-Registered? |
|---|---|---|---|
| AST dep graph builder | `tools/dep_graph_db.py` | **Complete** – in-memory + SQLite | No canonical path entry in SSOT |
| ADG JSON dump builder | `ops_scripts/ci/dump_adg_to_file.py` | **Complete** – writes `artifacts/adg/adg_full_*.json` | Path hardcoded (`ROOT/"artifacts"/"adg"`) |
| ADG artifact manifest | `artifacts/adg/artifact_manifest.json` | **Stub only** – `"artifacts": []` | No schema, no writer registered |
| ADG SQLite cache | `artifacts/dep_graph.sqlite` | **Active** – written by `dep_graph_db.py` | Path hardcoded in `tools/dep_graph_db.py:46` |
| Structure drift validator | `agentic_core/L5_safety/validators/structure_drift_validator.py` + `ops_scripts/ci/structure_drift_validator.py` | **Partial** – directory/file hash only, no graph edge diff | No SSOT path entry |
| ADG CI invariant scanner | `agentic_core/adg/ci/invariant_scanner.py` | **Complete** – LLM egress, embedding factory, layer boundary rules | Registered only in ADG schema, not SSOT accelerator registry |
| Runtime invariant checker | `agentic_core/L5_safety/invariants/runtime_invariant_checker.py` | **Complete** – 6 runtime rules | Domain-local, not machine-readable registry |
| Prompt governance invariant registry | `agentic_core/prompt_governance/core/invariant_registry.py` | **Partial** – prompt domain only | Domain-local |
| Coverage scoreboard | `ops_scripts/ci/coverage_scoreboard.py` | **Partial** – line/branch only, not symbol-level | No SSOT path |
| Guardian analysis script | `artifacts/_guardian_adg_analysis.py` | **Dead/ad hoc** – hardcoded Windows path, zero live references | **DELETE OUTRIGHT** |

### What Does NOT Exist
- **Canonical Definition Registry** — no cross-domain machine-readable registry of all SSOT surfaces
- **Config Consumption Graph** — no tracking of config symbol flow or duplicate-detection graph
- **Execution Path Graph** — no structured capture of `execute_ssot` → guardian → healer flow
- **Change Impact Engine** — no API over `tools/dep_graph_db.py::blast_radius` + test/validator join
- **Symbol Ownership Map** — no file mapping symbols to owning layer/territory/validator
- **Test Coverage by Symbol Map** — no symbol-level gap map (only line/branch coverage today)
- **Failure Mode Catalog** — no machine-readable failure taxonomy
- **Accelerator SSOT Registry** — no `ACCELERATOR_REGISTRY` block in `structure_blueprint`

### Critical Hardcoded Path Violations Found
- `tools/dep_graph_db.py:46` — `DB_PATH = ROOT / "artifacts" / "dep_graph.sqlite"` (not from SSOT)
- `ops_scripts/ci/dump_adg_to_file.py:40` — `OUT_DIR = ROOT / "artifacts" / "adg"` (not from SSOT)
- `agentic_core/L0_routing/scripts/execute_ssot.py:73,2938` — `AGENTIC_CORE_DIR = "agentic_core"` duplicated locally (SSOT constant already exists in `ssot.py`)

---

## Section 2 — SSOT Design

### New Module: `accelerator_registry.py`

A new module inside the `structure_blueprint` package:
```
agentic_core/L5_safety/config/structure_blueprint/accelerator_registry.py
```

It is a **leaf node** (no internal package deps beyond stdlib + `_constants`). It defines `ACCELERATOR_REGISTRY: dict[str, AcceleratorSpec]` where each entry is a `TypedDict` with exactly the required fields.

### `AcceleratorSpec` TypedDict Fields

```python
class AcceleratorSpec(TypedDict, total=False):
    artifact_key: str               # canonical short ID, snake_case
    canonical_path: str             # repo-relative path to generated artifact
    schema_version: str             # "1.0", "2.0" etc
    builder_module: str             # dotted Python module path of builder
    builder_entrypoint: str         # function name in builder_module
    source_inputs: list[str]        # artifact_keys or literal repo paths this depends on
    refresh_policy: str             # "on_commit" | "on_demand" | "ci_required" | "never"
    required_for_ci: bool
    required_for_execute_ssot: bool
    required_for_apps: bool
    allowed_readers: list[str]      # module path prefixes allowed to read
    allowed_writers: list[str]      # module paths allowed to write (exactly)
    derivation_only: bool           # True = never hand-edit
    hand_edit_forbidden: bool
    validation_function: str        # dotted path to checker function
    failure_behavior: str           # "raise" | "warn" | "skip"
    description: str
```

### Registry Keys (9 new + 2 existing wired)

| Key | Artifact Path | Builder Module |
|---|---|---|
| `adg_full_json` | `artifacts/adg/adg_full_latest.json` | `ops_scripts.ci.dump_adg_to_file` |
| `adg_sqlite` | `artifacts/dep_graph.sqlite` | `tools.dep_graph_db` |
| `canonical_definition_registry` | `artifacts/structural_intelligence/canonical_definition_registry.json` | `ops_scripts.ci.build_canonical_definition_registry` |
| `config_consumption_graph` | `artifacts/structural_intelligence/config_consumption_graph.json` | `ops_scripts.ci.build_config_consumption_graph` |
| `execution_path_graph` | `artifacts/structural_intelligence/execution_path_graph.json` | `ops_scripts.ci.build_execution_path_graph` |
| `change_impact_engine` | `artifacts/structural_intelligence/change_impact_cache.json` | `ops_scripts.ci.build_change_impact_engine` |
| `invariant_registry` | `artifacts/structural_intelligence/invariant_registry.json` | `ops_scripts.ci.build_invariant_registry` |
| `architecture_drift_diff` | `artifacts/structural_intelligence/architecture_drift_diff.json` | `ops_scripts.ci.build_architecture_drift_diff` |
| `symbol_ownership_map` | `artifacts/structural_intelligence/symbol_ownership_map.json` | `ops_scripts.ci.build_symbol_ownership_map` |
| `test_coverage_by_symbol` | `artifacts/structural_intelligence/test_coverage_by_symbol.json` | `ops_scripts.ci.build_test_coverage_by_symbol` |
| `failure_mode_catalog` | `artifacts/structural_intelligence/failure_mode_catalog.json` | `ops_scripts.ci.build_failure_mode_catalog` |

### SSOT Path Constants to Add to `ssot.py`

```python
STRUCTURAL_INTELLIGENCE_DIR: str = "artifacts/structural_intelligence"
ADG_ARTIFACTS_DIR: str = "artifacts/adg"
ADG_SQLITE_PATH: str = "artifacts/dep_graph.sqlite"
ACCELERATOR_REGISTRY_MODULE: str = (
    "agentic_core.L5_safety.config.structure_blueprint.accelerator_registry"
)
```

### Export Wiring

`accelerator_registry.py` is exported from `structure_blueprint/__init__.py` (cold/lazy path, same pattern as other cold modules) and re-exported from the shim `structure_blueprint_config.py`.

---

## Section 3 — Canonical File Location Plan

### Builders (new)
```
ops_scripts/ci/build_canonical_definition_registry.py
ops_scripts/ci/build_config_consumption_graph.py
ops_scripts/ci/build_execution_path_graph.py
ops_scripts/ci/build_change_impact_engine.py
ops_scripts/ci/build_invariant_registry.py
ops_scripts/ci/build_architecture_drift_diff.py
ops_scripts/ci/build_symbol_ownership_map.py
ops_scripts/ci/build_test_coverage_by_symbol.py
ops_scripts/ci/build_failure_mode_catalog.py
```

### SSOT Module (new)
```
agentic_core/L5_safety/config/structure_blueprint/accelerator_registry.py
```

### Generated Artifact Outputs (new governed folder)
```
artifacts/structural_intelligence/
  canonical_definition_registry.json
  config_consumption_graph.json
  execution_path_graph.json
  change_impact_cache.json
  invariant_registry.json
  architecture_drift_diff.json
  symbol_ownership_map.json
  test_coverage_by_symbol.json
  failure_mode_catalog.json
```

### Snapshot / Diff Baselines
```
artifacts/structural_intelligence/snapshots/
  architecture_drift_baseline_<timestamp>.json   (retained per CI run, pruned > 30)
```

### Schema Files
Each artifact's schema lives as a `$schema_version` field inline (JSON) + a `schema` top-level key.  No separate JSON Schema files needed at this stage — the `AcceleratorSpec.schema_version` field tracks breaking changes.

### Validator / Checker (new)
```
ops_scripts/ci/validate_accelerator_registry.py   # checks all registered artifacts
```

### Tests (new)
```
tests/architecture/test_accelerator_registry_ssot.py
tests/architecture/test_accelerator_artifact_resolution.py
tests/architecture/test_accelerator_missing_artifact_behavior.py
tests/architecture/test_accelerator_consumer_path_canon.py
tests/architecture/test_architecture_drift_diff.py
```

---

## Section 4 — Implementation Plan (Ordered Slices)

### Slice 0 — Delete Dead Script + SSOT Path Constants
**Actions:**
1. **Delete** `artifacts/_guardian_adg_analysis.py` (zero live references confirmed via grep)
2. **Add** to `agentic_core/L5_safety/config/structure_blueprint/ssot.py`:
   - `STRUCTURAL_INTELLIGENCE_DIR`, `ADG_ARTIFACTS_DIR`, `ADG_SQLITE_PATH`
3. **Export** them from `__init__.py` and `structure_blueprint_config.py` shim

### Slice 1 — `AcceleratorSpec` TypedDict + `ACCELERATOR_REGISTRY` dict
**File:** `agentic_core/L5_safety/config/structure_blueprint/accelerator_registry.py`
- Define `AcceleratorSpec` TypedDict
- Define full `ACCELERATOR_REGISTRY` with all 11 entries
- `get_accelerator(key)` — returns spec or raises `KeyError` with clear message
- `resolve_canonical_path(key, repo_root)` — returns `Path`, raises `AcceleratorArtifactMissingError` if `required_for_ci=True` and file absent
- `validate_accelerator_registry()` — checks all required fields present, no duplicate keys

### Slice 2 — Wire SSOT exports
**Files:** `__init__.py` cold-path block + `structure_blueprint_config.py` shim
- Add `accelerator_registry` to the cold-path `__getattr__` block
- Re-export `ACCELERATOR_REGISTRY`, `AcceleratorSpec`, `get_accelerator`, `resolve_canonical_path` from shim

### Slice 3 — Fix hardcoded path violations + bootstrap constant documentation
**Files:** `tools/dep_graph_db.py`, `ops_scripts/ci/dump_adg_to_file.py`, `agentic_core/L0_routing/scripts/execute_ssot.py`

**A. `tools/dep_graph_db.py`**
- Replace `DB_PATH = ROOT / "artifacts" / "dep_graph.sqlite"` with import from SSOT `ADG_SQLITE_PATH`

**B. `ops_scripts/ci/dump_adg_to_file.py`**
- Replace `OUT_DIR = ROOT / "artifacts" / "adg"` with import from SSOT `ADG_ARTIFACTS_DIR`

**C. `agentic_core/L0_routing/scripts/execute_ssot.py`** (bootstrap exception handling)
- **Line 73** (early-boot copy before imports): Mark as **BOOTSTRAP EXCEPTION** with inline comment:
  ```python
  # BOOTSTRAP EXCEPTION:
  # Needed before repo-root resolution and canonical config import at line 997.
  # Must stay identical to SSOT AGENTIC_CORE_DIR.
  # TODO: Collapse once boot-sequencing allows canonical import before resolve_repo_root().
  AGENTIC_CORE_DIR = "agentic_core"
  ```
- **Line 2938** (second redefinition): **DELETE** — this one is after canonical imports are available (line 997-1007), so it's a pure duplicate with no bootstrap justification
- **After line 1007** (after canonical imports load): Add runtime assertion:
  ```python
  # Validate bootstrap constant matches SSOT
  assert AGENTIC_CORE_DIR == "agentic_core", (
      f"Bootstrap AGENTIC_CORE_DIR mismatch: {AGENTIC_CORE_DIR!r} != 'agentic_core'"
  )
  ```

### Slice 4 — Builders (minimal derivation-only implementations)
Each builder follows the same contract:
1. Imports `ACCELERATOR_REGISTRY` to resolve its own output path
2. Reads its declared `source_inputs` from the registry
3. Writes `{"schema_version": "1.0", "built_at": "...", "data": {...}, "_derived": true, "_hand_edit_forbidden": true}`
4. Fails loudly if a required input is missing

**Builders to implement (each ~80-150 lines):**

**A. `build_canonical_definition_registry.py`**
- Walk `structure_blueprint/__init__.py` public API + `SOVEREIGN_TERRITORIES` keys
- Emit: `{symbol: {module, type, consumers_hint, deprecated}}`

**B. `build_config_consumption_graph.py`**
- Use the ADG SQLite graph (`tools.dep_graph_db.build()`)
- Walk all nodes that import from `structure_blueprint` modules
- Detect local redefinitions of path constants (scan for string literals matching known SSOT values)
- Emit edges: `{consumer_module → [config_symbol, …], is_canonical_import: bool, local_shadow_detected: bool}`

**C. `build_execution_path_graph.py`**
- Static trace from `execute_ssot_entrypoint.py` entry through known call graph
- Use ADG `blast_radius` + manual seed list of guardian/healer entry symbols
- Emit ordered nodes: `{step_id, module, function, enforcement_gate: bool, mutation_point: bool}`

**D. `build_change_impact_engine.py`**
- Thin wrapper: given `--changed-file` CLI arg, call `dep_graph_db.blast_radius(module)`
- Join with symbol ownership map and test coverage map
- Emit: `{changed_module, direct_consumers, transitive_consumers, affected_tests, blast_radius_class}`

**E. `build_invariant_registry.py`**
- Aggregate invariant records from:
  - `agentic_core/adg/ci/invariant_scanner.py` (3 ADG rules)
  - `agentic_core/L5_safety/invariants/runtime_invariant_checker.py` (6 runtime rules)
  - Hand-authored additions for structural rules (no-silent-fallback, no-local-SSOT-dup, etc.)
- Emit: `{id, description, severity, enforcing_checker, failure_mode, linked_artifact}`

**F. `build_architecture_drift_diff.py`**
- Load latest two ADG JSON dumps from `artifacts/adg/` sorted by timestamp
- Diff: new edges, removed edges, new cycles, fan-out spikes (>10 new importers), new layer violations
- Emit: `{prior_artifact, current_artifact, diff: {new_edges, removed_edges, new_cycles, ...}}`

**G. `build_symbol_ownership_map.py`**
- Walk Python files via AST, collect `ClassDef`/`FunctionDef` top-level symbols
- Map each to `{owning_file, owning_territory, owning_layer, is_canonical, related_tests}`
- Use `TEST_CANONICAL_LOCATION_MAP` from SSOT for test cross-reference

**H. `build_test_coverage_by_symbol.py`**
- Cross-reference symbol ownership map with test files (AST scan of test function names)
- Flag symbols with `in_degree > 3` (high centrality) and no direct test
- Emit: `{symbol, test_count, direct_tests, centrality, coverage_verdict}`

**I. `build_failure_mode_catalog.py`**
- Emit hand-authored static catalog (data-driven, no AST scan required)
- 10 canonical failure modes: import_mismatch, swallowed_exception, schema_drift, duplicate_threshold, local_config_hardcoding, fake_healthy_test, orphan_validator, mutation_before_path_validation, fallback_masking, sync_async_mismatch
- Each: `{failure_mode_id, description, symptom_pattern, detection_logic, known_examples, remediation, regression_test_type}`

### Slice 5 — Validator / Registry Completeness Checker
**File:** `ops_scripts/ci/validate_accelerator_registry.py`
- Checks: every key has a `builder_module` that resolves to a real module
- Checks: every `required_for_ci=True` artifact exists on disk
- Checks: no consumer in guardian/execute_ssot reads a non-canonical path
- Checks: no duplicate `canonical_path` values across registry
- Exit code 0 = clean, 1 = violations (printed to stdout)

---

## Section 5 — Consumer Integration

### `tools/dep_graph_db.py`
- Replace `DB_PATH` literal with `get_accelerator("adg_sqlite").canonical_path` resolved via SSOT
- Keep `SSOT_DIRS` as-is (already matches `CODE_TERRITORIES`)

### `ops_scripts/ci/dump_adg_to_file.py`
- Replace `OUT_DIR` literal with SSOT `ADG_ARTIFACTS_DIR`
- Write a symlink or copy to `artifacts/adg/adg_full_latest.json` after each dump (allows canonical single-path reference by consumers)

### `agentic_core/L0_routing/scripts/execute_ssot.py`
- **Line 73**: Keep as documented bootstrap exception (see Slice 3C)
- **Line 2938**: Delete (pure duplicate, no bootstrap justification)
- Add runtime assertion after canonical imports to validate bootstrap constant matches SSOT
- Add import of `resolve_canonical_path` from `structure_blueprint.accelerator_registry` for any accelerator artifact reads

### Guardian scripts (`agentic_core/L0_routing/scripts/run_guardian_*.py`)
- No immediate changes required — they do not currently read accelerator artifacts
- Future wiring: `run_guardian_drift_detection.py` should call `build_architecture_drift_diff` builder before running

### CI checks (`ops_scripts/ci/validate_accelerator_registry.py`)
- Wire into `.github/workflows/` as a pre-merge check (new workflow step in existing `adg-invariant-scan.yml`)

---

## Section 6 — Validation and Invariants

### Checks implemented by `validate_accelerator_registry.py`:
1. All registry entries have all required `AcceleratorSpec` fields
2. No two entries share a `canonical_path`
3. Every `builder_module` resolves via `importlib`
4. Every `required_for_ci=True` artifact exists on disk OR builder can be invoked to produce it
5. No consumer in scanned files reads a path that matches any `canonical_path` value without going through `resolve_canonical_path()`
6. The existing ADG artifact is registered (`adg_full_json` key present)
7. `derivation_only=True` artifacts contain `"_hand_edit_forbidden": true` in their JSON

### Runtime enforcement (added to builders):
- All builders check schema version on load and raise `AcceleratorSchemaError` on mismatch
- Missing required input artifact → `AcceleratorArtifactMissingError(artifact_key, path)` — never silent

---

## Section 7 — Tests

| Test File | Covers |
|---|---|
| `tests/architecture/test_accelerator_registry_ssot.py` | All 11 registry keys present; no duplicate paths; all required fields populated |
| `tests/architecture/test_accelerator_artifact_resolution.py` | `resolve_canonical_path` returns correct `Path`; raises on unknown key |
| `tests/architecture/test_accelerator_missing_artifact_behavior.py` | `required_for_ci=True` + absent file → `AcceleratorArtifactMissingError` |
| `tests/architecture/test_accelerator_consumer_path_canon.py` | Scan `tools/dep_graph_db.py`, `dump_adg_to_file.py` — no hardcoded path literals matching SSOT values |
| `tests/architecture/test_architecture_drift_diff.py` | Controlled fixture: inject fake prior/current ADG JSONs; verify diff detects new edge, removed edge, new cycle |
| `tests/architecture/test_invariant_registry_schema.py` | Load `invariant_registry.json`; all entries have required fields; all `severity` values in allowed enum |
| `tests/architecture/test_symbol_ownership_map_schema.py` | Load `symbol_ownership_map.json`; validate schema; spot-check known symbol |
| `tests/architecture/test_test_coverage_by_symbol_schema.py` | Load `test_coverage_by_symbol.json`; validate schema; known untested symbol produces expected verdict |
| `tests/architecture/test_failure_mode_catalog_schema.py` | Load `failure_mode_catalog.json`; all 10 canonical modes present; required fields populated |
| `tests/architecture/test_change_impact_engine.py` | Controlled input: known module → expected blast radius using real ADG graph; output matches expected |
| `tests/architecture/test_config_consumption_graph.py` | Known config consumer → appears in graph; known shadow constant detected |

---

## Section 8 — Gap Report

### What will be Created
- `accelerator_registry.py` — full SSOT module with all 11 entries
- 9 new builder scripts in `ops_scripts/ci/`
- `artifacts/structural_intelligence/` folder + 9 generated artifacts
- `ops_scripts/ci/validate_accelerator_registry.py` — completeness checker
- 11 test files in `tests/architecture/`
- SSOT path constants `STRUCTURAL_INTELLIGENCE_DIR`, `ADG_ARTIFACTS_DIR`, `ADG_SQLITE_PATH` in `ssot.py`

### What Will Be Deleted
- `artifacts/_guardian_adg_analysis.py` — dead/ad hoc script with hardcoded absolute path, zero live references

### What Will Be Only Partially Wired (Phase 1)
- **Config Consumption Graph** — detects hardcoded string literals matching SSOT path constants but cannot detect semantic duplication across non-string forms (e.g. `Path("agentic") / "core"`)
- **Execution Path Graph** — covers the `execute_ssot` → guardian → healer main trunk; does not yet trace all `apps_*` domain-specific flows
- **Test Coverage by Symbol** — cross-references symbol names to test function names lexically; does not parse runtime call graphs or pytest fixture wiring
- **`execute_ssot.py` early-boot path constants** — line 73 bootstrap copy (`AGENTIC_CORE_DIR`, `OPS_SCRIPTS_DIR`) cannot be removed without verifying `resolve_repo_root()` call ordering; marked as documented bootstrap exception with runtime assertion

### What Needs Follow-on Work
- Guardian scripts (`run_guardian_drift_detection.py`) should auto-invoke the drift diff builder before running
- `artifact_manifest.json` in `artifacts/adg/` (currently a stub) should be populated by the dump builder post-run
- A `MISSION_CONFIG`-level directive should add `validate_accelerator_registry` to the standard pre-run checklist in `execute_ssot`
- The `coverage_scoreboard.py` upgrade to symbol-level (depends on the test coverage by symbol map being stable for one sprint)
- CI workflow YAML update to invoke `validate_accelerator_registry.py` as a required step
- Boot-sequencing refactor to allow canonical SSOT imports before `resolve_repo_root()`, eliminating the bootstrap exception

### Temporary Compatibility Layers
- **`execute_ssot.py` line 73 bootstrap constant** — retained as a narrowly documented temporary exception with runtime assertion; scheduled for removal after boot-sequencing cleanup
- `ADG_SQLITE_PATH` added to SSOT; `tools/dep_graph_db.py` updated to import it; a one-line shim `DB_PATH = ADG_SQLITE_PATH` retained inside `dep_graph_db.py` for any external callers referencing `dep_graph_db.DB_PATH` directly

### Remaining Risks
- **Schema evolution**: `AcceleratorSpec` is a `TypedDict` — adding required fields in the future is a breaking change for all consumers that unpack specs; plan from day 1 to use `total=False` and validate at runtime rather than at type-check time
- **ADG staleness**: `adg_full_latest.json` symlink/copy is only as fresh as the last CI run; consumers that need real-time blast radius must call `dep_graph_db.build()` directly
- **Builder idempotency**: builders write to `artifacts/structural_intelligence/`; if two CI runs overlap they could corrupt the output; builders should write to a `.tmp` file and atomically rename
- **`execute_ssot.py` size**: at ~8800 lines the file has multiple local path constants; a full audit pass beyond the two identified duplicates is deferred to a follow-on cleanup phase

---

## Implementation Order Summary

| Phase | Steps | Risk |
|---|---|---|
| 1 | Slice 0: delete dead script + add SSOT path constants | Low |
| 2 | Slice 1-2: `accelerator_registry.py` + exports | Low |
| 3 | Slice 3: fix hardcoded path violations + bootstrap exception docs | Medium (dep_graph_db is used by many consumers) |
| 4 | Slice 4A-I: 9 builders (A → I order) | Medium (each isolated, fails loud) |
| 5 | Slice 5: `validate_accelerator_registry.py` | Low |
| 6 | Section 5: consumer wiring | Medium |
| 7 | Section 7: tests | Low |

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

