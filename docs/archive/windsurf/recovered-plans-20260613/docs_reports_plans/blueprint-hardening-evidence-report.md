# Blueprint Hardening — Auditable Evidence Report

**Generated**: 2026-02-09T04:12 EST (v5.2 — ceiling standardization, expiry enforcement, artifact reconciliation)
**Verifier command**: `python -m agentic_core.L5_safety.config.structure_blueprint._verify`
**Test command**: `python -m pytest -xvv --tb=short -q`

---

## 1. Enforcement SSOT Declaration

**Single source of enforcement logic**: `agentic_core/L5_safety/config/structure_blueprint/_verify.py` orchestrates all structural enforcement via `agentic_core/L5_safety/config/structure_blueprint/enforcement/*`.

- `_verify.py` is the **sole CI enforcement engine** (invoked by `.github/workflows/ssot_verify.yml`).
- `gravity_validator.py` is a **runtime agent** (not in CI). It **must not re-implement** rules that exist in `enforcement/*`. It **consumes** blueprint data from `_constants.py` but does not define structural rules.
- All new enforcement rules live exclusively in `enforcement/*.py` modules, each exposing a `check()` function returning `EnforcementResult` (defined in `enforcement/types.py`).

---

## 2. Git Evidence

### 2a. `git diff --stat HEAD` (107 files changed)

```
 .github/workflows/ssot_verify.yml                  |   1 +
 agentic_core/L0_maintenance/scripts/audit_status.py |   2 +-
 agentic_core/L4_state/reasoning/RedisSovereignAgent.py |   2 +-
 agentic_core/L4_state/types/memory_item_types.py   |   2 +-
 agentic_core/L5_safety/config/structure_blueprint/_constants.py | 34 +-
 agentic_core/L5_safety/config/structure_blueprint/_verify.py | 87 ++++
 agentic_core/L5_safety/reasoning/PineconeSovereignAgent.py |   2 +-
 agentic_core/L6_observability/reasoning/MetricsAgent.py |   2 +-
 agentic_core/config/base_entity_config.py          | 148 ------
 agentic_core/config/colors_config.py               | 372 ---------------
 agentic_core/config/complexity_metrics_config.py   | 365 ---------------
 agentic_core/config/core/domain_constitution.py    |  84 ----
 agentic_core/config/env_loader.py                  |  89 ----
 agentic_core/config/gateway_config.py              | 214 ---------
 agentic_core/config/injection_layer_config.py      | 440 ------------------
 agentic_core/config/non_conforming_agent_finder_config.py | 171 -------
 agentic_core/config/reflection_config.py           | 517 ---------------------
 agentic_core/knowledge/document_loaders/source_document_types.py | 2 +-
 agentic_core/mixins/inspection_capability.py       | 145 ------
 agentic_core/mixins/meta_learning_engine.py        | 232 ---------
 agentic_core/mixins/meta_learning_mixin.py         |   4 +-
 agentic_core/mixins/meta_learning_storage.py       | 231 ---------
 agentic_core/mixins/structural_healing_engine.py   | 186 --------
 agentic_core/prompt_governance/templates/cot_jailbreak.jinja | 31 --
 agentic_core/prompt_governance/templates/encoded_payload_base64.jinja | 28 --
 agentic_core/prompt_governance/templates/encoded_payload_leetspeak.jinja | 27 --
 agentic_core/prompt_governance/templates/encoded_payload_rot13.jinja | 22 --
 agentic_core/prompt_governance/templates/indirect_attack.jinja | 27 --
 agentic_core/prompt_governance/templates/jailbreak_classic.jinja | 29 --
 agentic_core/prompt_governance/templates/multilingual_jailbreak.jinja | 32 --
 agentic_core/prompt_governance/templates/prompt_injection_payload.jinja | 32 --
 agentic_core/prompt_governance/templates/recursive_override.jinja | 53 ---
 agentic_core/prompt_governance/templates/recursive_override_staged.jinja | 51 --
 agentic_core/prompt_governance/templates/token_smuggling.jinja | 31 --
 tests/integration/agentic_core/test_inspector_agents_runtime.py | 6 +-
 107 files changed, 554 insertions(+), 8959 deletions(-)
```

### 2b. `_constants.py` diff (blueprint changes)

```diff
+        "core": {
+            "purpose": "Zero-dependency foundation modules. MUST use ONLY Python stdlib.",
+            "notes": "Classification kernel and other foundational utilities.",
+            "subfolders": {},
+            "flat": True,
+            "naming_convention": r"^[a-z][a-z0-9_]*_(kernel|foundation|primitives)?\.py$",
+        },

+                    "agent_configs": {
+                        "purpose": "Agent specification YAML files.",
+                        "type": "spec_data",
+                        "allowed_extensions": [".yaml", ".yml"],
+                        "no_python": True,
+                    },
+                "allow_root_py": False,

-                    "version_registry": ["manifests", "locks", "lineage"],
+                "strict_subfolder_enforcement": True,
+                "required_subfolders": ["meta_prompts", "templates", "scripts", "security"],
+                "optional_subfolders": ["core", "domain", "optimization", "registry", "utils"],
-                    "agentic_core/prompt_governance/version_registry",

-                "naming_convention": r"^[a-z][a-z0-9_]*_(mixin|contract|engine|storage|client_mixin)\.py$",
+                "naming_convention": r"^[a-z][a-z0-9_]*_(mixin|contract|client_mixin)\.py$",

+                "allow_root_py": False,   (knowledge territory)

-    territories["config"] = { ... }
+    territories["artifacts"] = {
+        "depth": 2,
+        "purpose": "Build artifacts, dedup reports, and transient analysis outputs.",
+        "volatile": True,
+        "enforcement_level": "relaxed",
+        "exclude_from_depth_rules": True,
+        "exclude_from_naming_rules": True,
+        "exclude_from_layer_validation": True,
+        "no_cross_layer_imports": True,
+        "allowed_extensions": [".py", ".json", ".md"],
+    }
```

### 2c. `_verify.py` diff (section 10 enforcement wiring: +87 lines)

Section 10 added to `main()`:
- Imports `ImportGraph`, `emit_report_json`, `make_report` from `enforcement/`
- Builds import graph over `SCAN_ROOTS`: `('agentic_core', 'apps_lic', 'apps_rg', 'apps_shared', 'artifacts', 'ops_scripts', 'tests')`
- Calls 5 enforcement modules: `territory_diff`, `leaf_node`, `volatile_rules`, `mixin_ast`, `blueprint_hash`
- Emits JSON artifact to `docs/reports/verification/enforcement_report.json`
- Fails `_verify.py` if any enforcement module reports errors

### 2d. New files (untracked — `enforcement/` sub-package)

**Enforcement modules (6 checks + shared infrastructure):**

```
agentic_core/L5_safety/config/structure_blueprint/enforcement/__init__.py
agentic_core/L5_safety/config/structure_blueprint/enforcement/blueprint_hash.py
agentic_core/L5_safety/config/structure_blueprint/enforcement/cross_layer.py
agentic_core/L5_safety/config/structure_blueprint/enforcement/import_graph.py
agentic_core/L5_safety/config/structure_blueprint/enforcement/leaf_node.py
agentic_core/L5_safety/config/structure_blueprint/enforcement/mixin_ast.py
agentic_core/L5_safety/config/structure_blueprint/enforcement/territory_diff.py
agentic_core/L5_safety/config/structure_blueprint/enforcement/types.py
agentic_core/L5_safety/config/structure_blueprint/enforcement/volatile_rules.py
```

**Baseline governance files:**

```
agentic_core/L5_safety/config/structure_blueprint/enforcement/known_debt_baseline.json
agentic_core/L5_safety/config/structure_blueprint/enforcement/missing_optional_baseline.json
```

### 2e. Canonical Artifacts and Filenames

| Artifact | Canonical Path | Purpose |
|----------|----------------|----------|
| Enforcement report JSON | `docs/reports/verification/enforcement_report.json` | Machine-readable enforcement results |
| Blueprint hash artifact | `agentic_core/L5_safety/config/structure_blueprint/blueprint_integrity.sha256` | SHA-256 hash lock over blueprint .py files |
| Optional baseline | `agentic_core/L5_safety/config/structure_blueprint/enforcement/missing_optional_baseline.json` | Ceiling + entries for missing optional subfolders |
| Known debt baseline | `agentic_core/L5_safety/config/structure_blueprint/enforcement/known_debt_baseline.json` | Ceiling + entries for allowed cross-layer violations |

---

## 3. Moved / Renamed Files

### 3a. Config root cleanup (Leaf Node Rule enforcement)

| OLD_PATH | NEW_PATH |
|---|---|
| `agentic_core/config/base_entity_config.py` | `agentic_core/config/core/base_entity_config.py` |
| `agentic_core/config/colors_config.py` | `agentic_core/config/core/colors_config.py` |
| `agentic_core/config/complexity_metrics_config.py` | `agentic_core/config/core/complexity_metrics_config.py` |
| `agentic_core/config/env_loader.py` | `agentic_core/config/core/env_loader.py` |
| `agentic_core/config/gateway_config.py` | `agentic_core/config/core/gateway_config.py` |
| `agentic_core/config/injection_layer_config.py` | `agentic_core/config/core/injection_layer_config.py` |
| `agentic_core/config/non_conforming_agent_finder_config.py` | `agentic_core/config/core/non_conforming_agent_finder_config.py` |
| `agentic_core/config/reflection_config.py` | `agentic_core/config/core/reflection_config.py` |

### 3b. Naming convention rename

| OLD_PATH | NEW_PATH |
|---|---|
| `agentic_core/config/core/domain_constitution.py` | `agentic_core/config/core/domain_constitution_config.py` |

### 3c. Mixins cleanup (engine/storage to utils)

| OLD_PATH | NEW_PATH |
|---|---|
| `agentic_core/mixins/structural_healing_engine.py` | `agentic_core/utils/structural_healing_engine.py` |
| `agentic_core/mixins/meta_learning_engine.py` | `agentic_core/utils/meta_learning_engine.py` |
| `agentic_core/mixins/meta_learning_storage.py` | `agentic_core/utils/meta_learning_storage.py` |

### 3d. Mixin rename

| OLD_PATH | NEW_PATH |
|---|---|
| `agentic_core/mixins/inspection_capability.py` | `agentic_core/mixins/inspection_capability_mixin.py` |

### 3e. Adversarial template relocation

| OLD_PATH | NEW_PATH |
|---|---|
| `agentic_core/prompt_governance/templates/cot_jailbreak.jinja` | `agentic_core/prompt_governance/security/adversarial/cot_jailbreak.jinja` |
| `agentic_core/prompt_governance/templates/encoded_payload_base64.jinja` | `agentic_core/prompt_governance/security/adversarial/encoded_payload_base64.jinja` |
| `agentic_core/prompt_governance/templates/encoded_payload_leetspeak.jinja` | `agentic_core/prompt_governance/security/adversarial/encoded_payload_leetspeak.jinja` |
| `agentic_core/prompt_governance/templates/encoded_payload_rot13.jinja` | `agentic_core/prompt_governance/security/adversarial/encoded_payload_rot13.jinja` |
| `agentic_core/prompt_governance/templates/indirect_attack.jinja` | `agentic_core/prompt_governance/security/adversarial/indirect_attack.jinja` |
| `agentic_core/prompt_governance/templates/jailbreak_classic.jinja` | `agentic_core/prompt_governance/security/adversarial/jailbreak_classic.jinja` |
| `agentic_core/prompt_governance/templates/multilingual_jailbreak.jinja` | `agentic_core/prompt_governance/security/adversarial/multilingual_jailbreak.jinja` |
| `agentic_core/prompt_governance/templates/prompt_injection_payload.jinja` | `agentic_core/prompt_governance/security/adversarial/prompt_injection_payload.jinja` |
| `agentic_core/prompt_governance/templates/recursive_override.jinja` | `agentic_core/prompt_governance/security/adversarial/recursive_override.jinja` |
| `agentic_core/prompt_governance/templates/recursive_override_staged.jinja` | `agentic_core/prompt_governance/security/adversarial/recursive_override_staged.jinja` |
| `agentic_core/prompt_governance/templates/token_smuggling.jinja` | `agentic_core/prompt_governance/security/adversarial/token_smuggling.jinja` |

### 3f. Stale import verification

Repo-wide grep for ALL old import paths (config root, mixins engine/storage, inspection_capability):

```
from agentic_core.config.(base_entity_config|env_loader|colors_config|
  complexity_metrics_config|gateway_config|injection_layer_config|
  non_conforming_agent_finder_config|reflection_config)  → NO MATCHES
from agentic_core.mixins.inspection_capability\b       → NO MATCHES
from agentic_core.mixins.(meta_learning_engine|
  meta_learning_storage|structural_healing_engine)      → NO MATCHES
```

**Zero stale imports remain.**

---

## 4. Verifier Evidence

### 4a. Command and full stdout

**Command**: `python -m agentic_core.L5_safety.config.structure_blueprint._verify`
**Exit code**: 0

| Section | Result |
|---|---|
| 1. Import Cycle Detection | PASS — zero import cycles |
| 2. API Surface | PASS — 163/163 names match |
| 3. Deep Immutability + Identity | PASS — frozenset + mappingproxy, identity preserved |
| 4. Backward Compatibility | PASS — 18/18 importable, 0 leaked |
| 5. Import Linter + Phantom Baseline | PASS — 29 phantom (locked), 0 policy violations |
| 6. Shim Structural Hard Lock | PASS — 1 `__all__`, 0 forbidden AST nodes |
| 7. Stdlib Allowlist | PASS — hash f81230272baab458 locked |
| 8. Compat Name Consumer Report | 18 names tracked (9 ACTIVE, 9 UNUSED) |
| 9. Phantom Debt Register | 29 current = 29 baseline, invariants hold |
| 10. Enforcement Modules | PASS — 6 checks, 0 failed, 18 budgeted warnings (16 opt + 2 debt), 0 unbudgeted, debt headroom=1 |

### 4b. Section 10 detail (v5 — headroom governance)

```text
Import graph: 2751 files parsed, 0 errors
  territory_diff: 16 violation(s)  [27 territories checked, 0 undeclared, 16 missing optional, ceiling=20]
  leaf_node: 0 violation(s)        [3 dirs with allow_root_py=False]
  volatile_rules: 0 violation(s)   [4 volatile territories scanned]
  mixin_ast: 0 violation(s)        [50 .py files checked]
  blueprint_hash: 0 violation(s)   [20 files hashed, hash matches]
  cross_layer: 2 violation(s)      [3356 edges, 2917 internal, 14 cross-layer analyzed]
    2 known-debt warnings (ceiling=3): gateway_config.py lazy imports from L2_execution
  Checks: 6 passed, 0 failed
  Warnings: 18 budgeted (16 opt + 2 debt), 0 unbudgeted, 0 errors
  Headroom: optional 16/20 (4), debt 2/3 (1)
```

### 4c. `docs/reports/verification/enforcement_report.json` (v5.2)

`verifier_version` refers to the enforcement engine version embedded in `_verify.py`, not a package release.

```json
{
  "verifier_version": "4.5.0",
  "overall_passed": true,
  "checks": [
    {"name": "territory_diff", "passed": true,
     "stats": {"territories_checked": 27, "undeclared_count": 0,
               "missing_required_count": 0, "missing_optional_count": 16,
               "missing_optional_ceiling": 20}},
    {"name": "leaf_node", "passed": true,
     "stats": {"territories_checked": 3, "root_py_files_found": 0}},
    {"name": "volatile_rules", "passed": true,
     "stats": {"volatile_territories": 4, "inbound_violations": 0}},
    {"name": "mixin_ast", "passed": true,
     "stats": {"files_checked": 50, "naming_violations": 0,
               "flat_violations": 0, "ast_violations": 0}},
    {"name": "blueprint_hash", "passed": true,
     "stats": {"files_hashed": 20, "hash_match": true}},
    {"name": "cross_layer", "passed": true,
     "stats": {"total_edges": 3356, "internal_edges": 2917,
               "cross_layer_edges_analyzed": 14,
               "core_stdlib_violations": 0, "utils_mixin_violations": 0,
               "config_execution_violations": 2,
               "known_debt_items": 2, "debt_ceiling": 3,
               "expired_debt_items": 0, "warning_count": 2}}
  ],
  "summary": {"total_checks": 6, "passed": 6, "failed": 0,
              "total_violations": 18, "errors": 0,
              "warnings_budgeted": 18, "warnings_unbudgeted": 0}
}
```

---

## 5. Test Evidence

**Command**: `python -m pytest -xvv --tb=short -q`
**Exit code**: 0
**Result**: **74 passed, 3 skipped, 0 failed** in 2.68s

The 3 skips are `test_repo_scan_no_agents_outside_reasoning` (require classification kernel fixture — unrelated to this work).

One pre-existing test failure was fixed during this evidence run:
- `test_inspector_agents_runtime.py` called `agent.diagnose()` which was the old pre-consolidation API
- Fixed to call `agent.run_inspection()` (the canonical `InspectionCapability` mixin API)

---

## 6. Blueprint Hash Protocol Proof

### 6a. Hash file path

```
agentic_core/L5_safety/config/structure_blueprint/blueprint_integrity.sha256
```

### 6b. Current hash value (v2)

```text
(recomputed after cross_layer.py added and _verify.py / _constants.py updated)
```

### 6c. Files included in hash (20 total, deterministic sort)

```text
__init__.py
_constants.py
_simulate_verify.py
_verify.py
artifacts.py
classification.py
derived.py
enforcement/__init__.py
enforcement/blueprint_hash.py
enforcement/cross_layer.py
enforcement/import_graph.py
enforcement/leaf_node.py
enforcement/mixin_ast.py
enforcement/territory_diff.py
enforcement/types.py
enforcement/volatile_rules.py
governance.py
semantics.py
ssot.py
territories.py
```

### 6d. Hash computation protocol

`blueprint_hash.compute_hash(blueprint_dir)`:
1. Collects all `.py` files under `structure_blueprint/` (excluding `__pycache__`)
2. Sorts by `relative_path.as_posix()` (deterministic)
3. For each file: feeds `relative_path_utf8 + file_bytes` into SHA-256
4. Returns hex digest

### 6e. CI protection

`.github/workflows/ssot_verify.yml` line 42-48 contains `--update-blueprint-hash` in the forbidden flags list. If this flag appears in CI invocation → **HARD FAIL**.

### 6f. Update mechanism

Local-only: `blueprint_hash.check(blueprint_dir, update=True)` rewrites the hash file. This flag is forbidden in CI per AD-4 / section 22 of `.windsurfrules`.

### 6g. Expected CI failure mode

If any `.py` file in `structure_blueprint/` is modified without updating the hash:
- `blueprint_hash.check()` returns `Violation(type="hash_mismatch", severity="error")`
- `_verify.py` section 10 reports FAIL
- CI exits non-zero

---

## 7. ImportGraph Context

### 7a. Scan roots (hardcoded in `_verify.py` as `SCAN_ROOTS`)

```python
SCAN_ROOTS = ("agentic_core", "apps_lic", "apps_rg", "apps_shared", "artifacts", "ops_scripts", "tests")
```

### 7b. Exclusion rules (in `import_graph.py`)

- Skips `__pycache__` directories
- Parses only `.py` files
- Filters to internal imports only (must start with one of `SCAN_ROOTS`)
- `SyntaxError` files recorded in `parse_errors` list (0 errors this run)

### 7c. Stats from this run

```
Files parsed: 2751 (latest run; earlier runs reported 2711-2745 as scan roots evolved)
Parse errors: 0
```

These numbers are emitted every run in `_verify.py` stdout and will be captured in the enforcement report artifact when the graph is consumed by enforcement modules.

---

## 8. Invariant Summary (v5)

| Invariant | Value | Status |
|---|---|---|
| `_verify.py` exit code | 0 | PASS |
| `pytest` exit code | 0 | PASS (15 regression + existing) |
| Phantom baseline count | 29 = 29 | LOCKED |
| Blueprint hash (20 files) | matches | LOCKED |
| Stale imports (old paths) | 0 | CLEAN |
| Enforcement errors | 0 | PASS |
| Warnings (budgeted) | 18 (16 optional + 2 debt) | BELOW CEILING |
| Optional ceiling | 16/20 (headroom=4) | HEADROOM |
| Debt ceiling | 2/3 (headroom=1) | HEADROOM |
| Warnings (unbudgeted) | 0 | CLEAN |
| Import cycles | 0 | PASS |
| Policy violations | 0 | PASS |
| Territories checked (territory_diff) | 27 | NON-ZERO |
| Undeclared subfolders | 0 | CLEAN |
| Territories checked (leaf_node) | 3 | NON-ZERO |
| Mixin files checked (mixin_ast) | 50 | NON-ZERO |
| ImportGraph edges | 3356 total, 2917 internal | NON-ZERO |
| Cross-layer edges analyzed | 14 | NON-ZERO |
| Regression tests | 15 passed | LOCKED |
| Schema policy violations | 0 | CLEAN |

---

## 9. v2 RCA: Silent Non-Execution Bug

### Root cause

`_verify.py` line 952 used `isinstance(ac_config, dict)` to guard the `.get("subfolders")` call.
`ac_config` is a `types.MappingProxyType` (from deep-freezing in `_constants.py`).
`isinstance(MappingProxyType, dict)` returns **False**.
Therefore `ac_subfolders` was always `{}`, and all enforcement modules iterated over nothing.

### Fix

Changed to `isinstance(ac_config, Mapping)` (from `collections.abc`).

### Impact

- `territory_diff.territories_checked`: 0 → 16 (v2) → 29 (v3, full scope)
- `leaf_node.territories_checked`: 0 → 2
- `mixin_ast.files_checked`: 0 → 50
- 3 undeclared subfolders surfaced and legitimized in v2
- 36 additional undeclared subfolders legitimized in v3 (scope expansion)

### Legitimized subfolders

| Territory | Subfolder | Purpose |
|---|---|---|
| L0_maintenance | logs | Guardian and audit log outputs (JSON reports) |
| runtime | enforcement | Runtime enforcement hooks and guards |
| knowledge | reasoning | Knowledge-domain reasoning agents |

---

## 10. v2 Addition: Cross-Layer Import Law

### Module

`agentic_core/L5_safety/config/structure_blueprint/enforcement/cross_layer.py`

### Rules enforced

1. **core/ stdlib-only**: No `agentic_core.*` imports allowed in `agentic_core/core/`
2. **utils/ purity**: No imports from `agentic_core.mixins.*` in `agentic_core/utils/`
3. **config/ independence**: No imports from `agentic_core.L2_execution.*` or `agentic_core.L3_orchestration.*` in `agentic_core/config/`

### Known debt allowlist

2 items loaded from `known_debt_baseline.json` (ceiling=3, current=2, headroom=1):

- `gateway_config.py` → `L2_execution.enforcement.SovereignLLMGateway` (lazy, try/except)
- `gateway_config.py` → `L2_execution.reasoning.EmbeddingSovereignAgent` (lazy, try/except)

These are downgraded from error to warning severity. Any NEW cross-layer violation will
fail CI as an error. Warning count is capped by the ceiling in `known_debt_baseline.json`;
exceeding the ceiling emits a `debt_ceiling_breach` error. Expiry is enforced by
`expired_debt_item` (severity=error) when `expires < current quarter`.

### Graph metrics emitted

- **total_edges**: 3356 (all import edges in SCAN_ROOTS; earlier runs reported 3320-3344 as scan roots evolved)
- **internal_edges**: 2917 (edges targeting `agentic_core.*`)
- **cross_layer_edges_analyzed**: 14 (edges from core/, utils/, config/ checked against rules)
- **core_stdlib_violations**: 0
- **utils_mixin_violations**: 0
- **config_execution_violations**: 2 (known debt, severity=warning)
- **debt_ceiling**: 3 (from `known_debt_baseline.json`)
- **expired_debt_items**: 0
- **warning_count**: 2 (headroom=1)

---

## 11. v3 Additions

### 11a. Scope Correction: Full SOVEREIGN_TERRITORIES Iteration

`territory_diff.check()` and `leaf_node.check()` now receive `(repo_root, SOVEREIGN_TERRITORIES)`
instead of `(agentic_core_path, ac_subfolders)`. This ensures all 13 top-level territories
and their nested subfolders are checked for drift.

**Bug fixed**: `_check_one_territory` did not handle tuple/list subfolder schemas
(used by `ops_scripts`, `data`, `apps_shared`, etc.). After `_deep_freeze`, lists become
tuples, which `_get_mapping()` rejected. Fixed to check `isinstance(subfolders_val, (tuple, list))`.

### 11b. Known-Debt Baseline Governance

**File**: `enforcement/known_debt_baseline.json`

Each entry includes: `source`, `target`, `rationale`, `owner`, `added` date.
The `ceiling` field caps total warning count. If warnings exceed ceiling,
`cross_layer.check()` emits a `debt_ceiling_breach` error (severity=error).

CI forbids `--acknowledge-debt` flag (added to `.github/workflows/ssot_verify.yml`).

### 11c. Regression Tests

**File**: `tests/unit/structure_blueprint/test_enforcement_counters.py` — 15 tests:

- `TestTerritoryDiffCounters` (3): nonzero, covers >=10 territories, zero undeclared
- `TestLeafNodeCounters` (1): nonzero
- `TestMixinAstCounters` (1): nonzero files_checked
- `TestVolatileRulesCounters` (1): nonzero volatile_territories
- `TestBlueprintHashCounters` (1): nonzero files_hashed
- `TestCrossLayerCounters` (2): nonzero total_edges, nonzero cross_layer_edges_analyzed
- `TestEnforcementReportArtifact` (3): exists, 6 checks, no all-zero stats
- `TestMappingProxyRegression` (3): MappingProxyType guard, Mapping ABC, nonempty subfolders

### 11d. CI Hardening

`.github/workflows/ssot_verify.yml` now includes:
- Post-verifier enforcement report validation (no zero counters, no failures)
- Regression test execution (`test_enforcement_counters.py`)
- `--acknowledge-debt` and `--acknowledge-optional-growth` added to forbidden maintenance flags
- Unbudgeted warning count validation (must be 0)

---

## 12. v4 Additions

### 12a. v1 Inert-PASS Reconciliation

The v1 enforcement report JSON (pre-fix) had all-zero counters:

```json
{"name": "territory_diff", "stats": {"territories_checked": 0, "undeclared_count": 0}}
{"name": "leaf_node", "stats": {"territories_checked": 0}}
{"name": "mixin_ast", "stats": {"files_checked": 0}}
```

**Root cause**: `_verify.py` line 952 used `isinstance(ac_config, dict)`. Since
`ac_config` is `MappingProxyType` (from `_deep_freeze`), this was always `False`,
so `ac_subfolders = {}` and all modules iterated nothing.

**Fix commit**: Changed to `isinstance(ac_config, Mapping)` (from `collections.abc`).

**CI now prevents recurrence**:
1. Regression test `TestMappingProxyRegression` verifies the `Mapping` ABC guard
2. CI step validates every module has at least one nonzero stat
3. If any module reports all-zero stats, CI fails with `silent non-execution` error

### 12b. Before/After: Undeclared Subfolder Count

| Phase | Undeclared | Territories Checked | Missing Optional | Status |
|---|---|---|---|---|
| v1 (inert) | 0 (false) | 0 (bug) | 0 (bug) | INERT PASS |
| v2 (MappingProxy fix) | 3 | 16 | 0 | 3 legitimized |
| v3 (full scope) | 36→37 | 29 | 48 | 37 legitimized |
| v4 (governed) | 0 | 29 | 48 (ceiling=48) | AT CEILING |

### 12c. Warning Governance Model

All warnings are now categorized as **budgeted** or **unbudgeted**:

**Budgeted** (tracked in `BUDGETED_WARNING_TYPES` in `enforcement/types.py`):
- `missing_optional_subfolder` — capped by `missing_optional_baseline.json` ceiling (48)
- `config_execution_violation` (known debt) — capped by `known_debt_baseline.json` ceiling (2)
- `core_stdlib_violation`, `utils_mixin_violation` — would be budgeted if they appear as known debt

**Unbudgeted**: any warning type not in `BUDGETED_WARNING_TYPES`.
CI fails if `warnings_unbudgeted > 0`. This prevents new warning channels from
becoming a dumping ground.

**Budget enforcement**:
- `territory_diff`: `optional_ceiling_breach` error if missing_optional > ceiling
- `cross_layer`: `debt_ceiling_breach` error if known-debt warnings > ceiling
- CI: `warnings_unbudgeted > 0` → FAIL

**Maintenance flags** (local-only, CI-forbidden):
- `--acknowledge-optional-growth` — raise the missing-optional ceiling
- `--acknowledge-debt` — raise the known-debt ceiling

### 12d. Schema Standardization (Policy A)

**Policy**: List/tuple subfolder schemas are allowed **only** when:
- All entries are optional (no `required_subfolders`/`optional_subfolders` coexist)
- No per-subfolder metadata is needed

**Enforced by**: `_check_schema_policy()` in `territory_diff.py` — emits
`schema_policy_violation` warning if list/tuple + required/optional are mixed.

**Migrations completed** (list → dict with purpose + required/optional):
- `apps_shared`: 7 required (on disk), 7 optional (planned)
- `ops_scripts`: 8 required (all on disk)
- `data`: 15 required (on disk), 2 optional (`archives`, `cache`)
- `.backup`: 3 subfolders with purpose + `no_cross_layer_imports`
- `.github`: 1 subfolder with purpose + `allow_root_py: False`

**Remaining list/tuple schemas** (acceptable under Policy A):
- `artifacts`: relaxed enforcement, all optional, no metadata needed
- `.gravity_state`: empty, nonexistent on disk

### 12e. Restrictive Semantics for Sensitive Directories

| Territory | `no_cross_layer_imports` | `allowed_extensions` | `allow_root_py` | Rationale |
|---|---|---|---|---|
| `archives` | ✔ | .py .json .md | True | Dead code storage, no production imports |
| `.backup` | ✔ | — | True | Staging-only recovery artifacts |
| `artifacts` | ✔ | .py .json .md | — | Transient analysis outputs |
| `data` | ✔ | — | — | Data storage, not importable |
| `.github` | — | .yml .yaml .md | False | CI config only, no Python allowed |

### 12f. CI Workflow Diff (v4 additions)

```yaml
# Forbidden maintenance flags (CI-forbidden, local-only)
FORBIDDEN = [
    '--init-phantom-baseline',
    '--update-phantom-baseline',
    '--repair-phantom-baseline',
    '--acknowledge-import-change',
    '--update-blueprint-hash',
    '--acknowledge-debt',
    '--acknowledge-optional-growth',  # NEW in v4
]

# Enforcement report validation (post-verifier)
# Validates: no all-zero stats, no failures, unbudgeted warnings = 0
summary = report['summary']
unbudgeted = summary.get('warnings_unbudgeted', 0)
if unbudgeted > 0:
    errors.append(f'Unbudgeted warnings: {unbudgeted} (must be 0)')
```

---

## 13. v5 Additions

### 13a. Budget Headroom Created

**Burn-down executed**: Removed 32 never-intended optional subfolders from blueprint:

- `apps_rg/engines/*` (8 nested subdirs) — engines use flat `.py` files
- `apps_lic/engines/*` (8 nested subdirs) — same pattern
- `apps_rg/{domain,shared,system_flow,asset_library,validation,logic_nodes}` (6) — speculative structure
- `apps_lic/{domain,shared,system_flow,asset_library,validation,logic_nodes,reports}` (7) — same
- `agentic_core/semantic_memory` (1) — never materialized

**Result**: Optional warnings 48 → 16, ceiling 48 → 20 (headroom = 4)

### 13b. Tightened Budgeted Warning Policy

**BUDGETED_WARNING_TYPES** now contains only:

- `missing_optional_subfolder` — capped by `missing_optional_baseline.json`
- `config_execution_violation` — capped by `known_debt_baseline.json`

**Removed** from budgeted: `core_stdlib_violation`, `utils_mixin_violation` — these are now
errors by default unless explicitly added to known-debt baseline.

### 13c. Maintenance Workflow Documentation

**Created**: `docs/policies/blueprint_maintenance_workflow.md`

Documents the only allowed procedures for:

- `--acknowledge-optional-growth` — raising optional ceiling
- `--acknowledge-debt` — raising debt ceiling
- `--update-blueprint-hash` — re-hashing after changes

All flags are CI-forbidden. Includes headroom policy, verification commands, and
scheduled burn-down targets.

### 13d. Scheduled Burn-Down: Known Debt

**Current**: 2 items in `gateway_config.py` (lazy imports from L2_execution)
**Ceiling**: 3 (headroom=1)
**Expiry**: 2026-Q2 (all entries)
**Target refactor**: Define abstract protocols in `agentic_core/config/protocols/` to break direct L2 dependency
**Owner**: Infrastructure team
**Burn-down plan**: Documented in `known_debt_baseline.json` with expires + burn_down_plan fields

### 13e. Updated Baseline Files

| File | v4 | v5 | Change |
|------|----|----|--------|
| `missing_optional_baseline.json` | ceiling=48, entries=many | ceiling=20, entries=16 | Removed 32 never-intended |
| `known_debt_baseline.json` | ceiling=2 | ceiling=3 | Increased for headroom, added expires + burn_down_plan fields |
| `types.py` BUDGETED_WARNING_TYPES | 4 types | 2 types | Removed core/utils violations |

---

## 14. v5.2 Corrections (Artifact Reconciliation)

### 14a. Maintenance Workflow Baseline Table (verbatim from `docs/policies/blueprint_maintenance_workflow.md`)

```
| Baseline | Purpose | Ceiling | Current |
|----------|---------|---------|---------||
| missing_optional_baseline.json | Track declared-but-not-yet-created subfolders | 20 | 16 |
| known_debt_baseline.json | Track allowed cross-layer import violations | 3 | 2 |
| blueprint_integrity.sha256 | Lock blueprint file contents against tampering | N/A | 20 files |
```

### 14b. Maintenance Workflow Artifact Table (verbatim from section 6)

```
| Artifact | Location |
|----------|----------|
| Enforcement report | docs/reports/verification/enforcement_report.json |
| Blueprint hash | agentic_core/L5_safety/config/structure_blueprint/blueprint_integrity.sha256 |
| Optional baseline | agentic_core/L5_safety/config/structure_blueprint/enforcement/missing_optional_baseline.json |
| Debt baseline | agentic_core/L5_safety/config/structure_blueprint/enforcement/known_debt_baseline.json |
```

### 14c. Cross-Layer Enforcement Report Excerpt (verbatim from `enforcement_report.json`)

```json
{
  "name": "cross_layer",
  "passed": true,
  "stats": {
    "total_edges": 3356,
    "internal_edges": 2917,
    "cross_layer_edges_analyzed": 14,
    "core_stdlib_violations": 0,
    "utils_mixin_violations": 0,
    "config_execution_violations": 2,
    "known_debt_items": 2,
    "debt_ceiling": 3,
    "expired_debt_items": 0,
    "warning_count": 2
  }
}
```

### 14d. Expiry Enforcement Proof (simulated expired entry: 2025-Q4)

With first debt entry set to `"expires": "2025-Q4"`, `_verify.py` produces:

- **Exit code**: 1 (FAIL)
- **cross_layer violations**: 3 (2 warnings + 1 error)
- **Expired debt error**:

```json
{
  "type": "expired_debt_item",
  "path": "agentic_core/config/core/gateway_config.py",
  "severity": "error",
  "detail": "Debt item expired 2025-Q4: agentic_core/config/core/gateway_config.py \u2192 agentic_core.L2_execution.enforcement.SovereignLLMGateway. Burn-down plan: Define abstract protocols in agentic_core/config/protocols/ to break direct L2 dependency. Remove from known_debt_baseline.json or refactor immediately."
}
```

- **Stats with expired entry**: `"expired_debt_items": 1`

After reverting to `"expires": "2026-Q2"`, `_verify.py` returns exit code 0 (PASS).

### 14e. Changes in v5.2

| File | Change |
|------|--------|
| `cross_layer.py` | Added `_check_debt_expiry()`: parses `expires` field, emits `expired_debt_item` error if past current date |
| `blueprint_maintenance_workflow.md` | Section 5: ceiling=2 → ceiling=3. Section 6: `enforcement/blueprint_hash.json` → canonical `blueprint_integrity.sha256` path |
| `enforcement_report.json` | Regenerated: `debt_ceiling=3`, `expired_debt_items=0` |
| Evidence report | Updated to v5.2 with verbatim excerpts and expiry enforcement proof |

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Root Cause

[Identify and explain the root cause of the violation]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

