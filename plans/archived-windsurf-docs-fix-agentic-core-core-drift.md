---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\fix-agentic-core-core-drift.md'
original_relative_path: 'fix-agentic-core-core-drift.md'
source_sha256: 83c2e4151043f9f1100437ca302fca5bc27bb05a1244e693e8d729db133f71c3
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Blueprint Authority Hardening: RCA + Structural Prevention (v3)

Comprehensive plan to fix 5 categories of blueprint drift and add 8 structural prevention layers via a modular enforcement engine that emits deterministic, machine-readable artifacts.

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


## ARCHITECTURE DECISIONS (Resolved Before Coding)

### AD-1: Enforcement Engine Ownership — Singular

**Decision**: `_verify.py` is the **sole CI enforcement engine**. `gravity_validator.py` is demoted to agent-facing consumer.

Current state:

- `_verify.py` (929 lines, 9 checks) — CI-enforced via `ssot_verify.yml`
- `gravity_validator.py` (511 lines, 4 checks) — consumed by `DynamicSealAgent`, `PreCommitSovereignAgent`, `ssot_cli`; NOT in CI

New structural rules go **only** into the enforcement sub-package (AD-2). `gravity_validator.py` may consume enforcement module outputs but must not duplicate rule logic.

**Invariant**: No structural rule implemented in two places.

---

### AD-2: Enforcement Sub-Package (Monolith Prevention)

`_verify.py` will NOT grow. Instead, create:

```text
structure_blueprint/
    enforcement/
        __init__.py
        territory_diff.py        # Layer 1 + 7
        leaf_node.py             # Layer 2
        volatile_rules.py        # Layer 3
        mixin_ast.py             # Layer 4
        import_verifier.py       # Layer 5
        blueprint_hash.py        # Layer 6
        cross_layer.py           # Layer 8
        import_graph.py          # Shared import graph builder (AD-5)
        types.py                 # Shared result types
```

Each module exposes a single function:

```python
def check(root: Path, territories: MappingProxyType) -> EnforcementResult:
    ...
```

`EnforcementResult` is a typed dict:

```python
class EnforcementResult(TypedDict):
    name: str               # e.g. "territory_diff"
    passed: bool
    violations: list[dict]  # machine-readable violation records
    stats: dict[str, int]   # counts for governance signals (§32)
```

`_verify.py` becomes a thin orchestrator:

1. Imports each enforcement module
2. Calls `check()` on each
3. Aggregates into `EnforcementReport`
4. Emits JSON artifact (AD-3)
5. Prints human-readable summary
6. Returns exit code

Existing 9 checks in `_verify.py` remain in place for now (extracting them is a separate refactor — do not scope-creep).

---

### AD-3: Deterministic Artifact Emission

Every enforcement module emits structured results. The orchestrator aggregates into:

```text
docs/reports/verification/enforcement_report.json
```

Schema:

```json
{
  "timestamp": "2026-02-08T22:12:00Z",
  "verifier_version": "4.5.0",
  "overall_passed": false,
  "checks": [
    {
      "name": "territory_diff",
      "passed": false,
      "violations": [
        {
          "territory": "prompt_governance",
          "type": "undeclared_subfolder",
          "path": "prompt_governance/optimization",
          "severity": "error"
        }
      ],
      "stats": {
        "territories_checked": 12,
        "undeclared_count": 1,
        "missing_required_count": 0
      }
    }
  ],
  "summary": {
    "total_checks": 7,
    "passed": 6,
    "failed": 1,
    "total_violations": 1
  }
}
```

CI can diff this artifact over time. Human report is derived from the JSON, not the other way around.

---

### AD-4: Blueprint Hash Protocol

**Hash computation**:

- Raw bytes (no whitespace normalization)
- Files sorted alphabetically by name
- Files included: all `.py` files in `structure_blueprint/` (excluding `__pycache__/`, `_verify.py`, `_simulate_verify.py`, `enforcement/`)
- Hash algorithm: SHA-256, full hex

**Storage**: `structure_blueprint/blueprint_integrity.sha256` (inside the package, version-controlled)

**Update protocol**:

- Local-only flag: `--update-blueprint-hash`
- Forbidden in CI (add to `ssot_verify.yml` forbidden flags list per §22)
- CI behavior: compare stored hash against computed → FAIL on mismatch

**What triggers hash change**: Any edit to `_constants.py`, `ssot.py`, `derived.py`, `territories.py`, `artifacts.py`, `semantics.py`, `classification.py`, `governance.py`, or `__init__.py`.

---

### AD-5: Import Graph Caching

AST-based import analysis is needed by multiple enforcement modules (Layers 3, 5, 8). Re-parsing per rule is O(n*k) where k = number of rules.

**Solution**: `enforcement/import_graph.py` builds the graph once:

```python
class ImportGraph:
    """Cached adjacency map of all internal imports across SCAN_ROOTS."""

    def __init__(self, root: Path, scan_roots: tuple[str, ...]):
        self._adjacency: dict[str, set[str]] = {}  # file -> set of imported modules
        self._reverse: dict[str, set[str]] = {}     # module -> set of importing files
        self._build(root, scan_roots)

    def imports_from(self, file: str) -> set[str]: ...
    def imported_by(self, module: str) -> set[str]: ...
    def files_importing_territory(self, territory: str) -> set[str]: ...
    def resolve_module_path(self, module: str) -> Path | None: ...
```

**Consumers**:

- `volatile_rules.py` -> `graph.files_importing_territory("artifacts")`
- `import_verifier.py` -> `graph.resolve_module_path(module)` for phantom detection
- `cross_layer.py` -> `graph.imports_from(file)` for layer/purity checks

**Lifecycle**: Built once per `_verify.py` run. Passed to each enforcement module that needs it.

---

### AD-6: Territory Schema — Required vs Optional Subfolders

Current blueprint uses flat `"subfolders": {...}` with no distinction between required and optional.

**New schema**:

```python
"prompt_governance": {
    ...
    "strict_subfolder_enforcement": True,
    "required_subfolders": ["meta_prompts", "templates", "scripts", "security"],
    "optional_subfolders": ["core", "domain", "optimization", "registry", "utils"],
}
```

**Enforcement logic** (in `territory_diff.py`):

- Undeclared subfolder (not in required OR optional) -> **FAIL**
- Missing required subfolder -> **FAIL**
- Missing optional subfolder -> **WARN** (logged in artifact, does not fail)

---

### AD-7: Volatile Territory — Non-Exporting Enforcement

Block ALL import forms from volatile territories:

- `from artifacts.foo import bar` -> FAIL
- `import artifacts.foo` -> FAIL
- `from artifacts.foo import *` -> FAIL

Additionally, within volatile territory files:

- `__all__` declarations -> FAIL (volatile modules must not define export surface)

**Dynamic import detection**: AST-check for `__import__("artifacts...")` and `importlib.import_module("artifacts...")` calls referencing volatile territory paths.

---

### AD-8: Plan Invariants (Machine-Verifiable)

This plan is a constitutional document. It must be verifiable:

- **Section count**: 6 top-level parts (Architecture Decisions, Findings, Hardening Layers, Implementation Phases, Verification Criteria, Plan Invariants)
- **AD count**: 8 architecture decisions
- **Finding count**: 5 findings
- **Layer count**: 8 hardening layers
- **Phase count**: 9 phases (0-8)
- **Step count**: 35 steps

If the plan is edited, step count must be updated or version-bumped.

**Plan version**: v3 (this document).

---

## PART A — FORENSIC FINDINGS (Reactive Fixes)

### FINDING 1: `agentic_core/core/` — Undeclared Territory

**RCA**: `build_sovereign_territories()` in `_constants.py` builds `agentic_core_subfolders` with 15 entries. `core` is absent — directory created ad-hoc for the classification kernel without blueprint update.

**Fix**: Add `"core"` to `agentic_core_subfolders`: `flat: True`, stdlib-only, safe to import from any layer.

---

### FINDING 2: `agentic_core/config/` — Root-Level File Sprawl

- **2a**: 7 `.py` files in root of `config/` violate Leaf Node Rule -> move to `config/core/`
- **2b**: `agent_configs/` subfolder (12 YAML files) undeclared -> legitimize with `"type": "spec_data"`, `"allowed_extensions": [".yaml"]`, `"no_python": True`
- **2c**: `domain_constitution.py` has no valid suffix -> rename to `domain_constitution_config.py`
- **2d**: 5 phantom imports referencing non-existent modules -> fix or remove

---

### FINDING 3: `artifacts/` — Scanned but Undeclared Territory

**RCA**: In `SCAN_ROOTS` but no `territories["artifacts"]` entry. Also: phantom `territories["config"]` (line 920) declares a root-level `config/` that doesn't exist on disk.

**Fix**: Legitimize as volatile territory with explicit safeguards (AD-7). Remove phantom `territories["config"]`.

---

### FINDING 4: `mixins/` Naming Violations & Engine Misplacement

- **4a**: `structural_healing_engine.py` + `meta_learning_engine.py` + `meta_learning_storage.py` — pure stateless logic, zero classes, NOT mixins -> move to `agentic_core/utils/`
- **4b**: `inspection_capability.py` — suffix `_capability` not in allowed set -> rename to `inspection_capability_mixin.py`
- **4c**: After moves, tighten regex to `r"^[a-z][a-z0-9_]*_(mixin|contract|client_mixin)\.py$"`

---

### FINDING 5: `prompt_governance/` — Taxonomy & Subfolder Drift

**`meta_prompts/` vs `templates/`**: Distinction is valid — different abstraction levels (meta-orchestration vs task execution). **Keep separate.**

Issues:

- 10+ adversarial payload `.jinja` files in `templates/` are red-team test fixtures -> move to `security/adversarial/`
- 6 undeclared subfolders on disk (`core`, `domain`, `optimization`, `registry`, `security`, `utils`)
- 1 phantom subfolder in blueprint (`version_registry`) doesn't exist on disk

---

## PART B — STRUCTURAL PREVENTION (8 Hardening Layers)

The root problem is not folder drift — it's **blueprint authority drift**. These 8 layers, implemented as isolated enforcement modules (AD-2), eliminate the trust surface.

### Enforcement gap table

| # | Layer | Existing | Gap |
| --- | --- | --- | --- |
| 1 | Territory auto-diff | `gravity_validator` (agentic_core only, not CI) | Not bidirectional. No required/optional semantics. No artifact. |
| 2 | Root `.py` prohibition | Leaf Node Rule in docs only | No `allow_root_py` flag. Not enforced. |
| 3 | Volatile safeguards | None | No import-FROM blocking. No `__all__` prohibition. No dynamic import check. |
| 4 | AST mixin validation | Regex only | No structural class check. |
| 5 | Import path verifier | `_verify.py` section 5 (structure_blueprint scope only) | Not general-purpose. |
| 6 | Blueprint hash | Allowlist hash exists | No whole-blueprint integrity hash. |
| 7 | Strict subfolder enforcement | agentic_core only | No prompt_governance, config, knowledge coverage. |
| 8 | Cross-layer import law | Upward layer check only | No volatile isolation, utils purity, config independence. |

---

### LAYER 1 + 7: `enforcement/territory_diff.py`

Handles both territory auto-diff (L1) and strict subfolder enforcement (L7) since they share logic.

**Input**: `SOVEREIGN_TERRITORIES`, filesystem

**Logic**:

```python
for territory_name, config in territories.items():
    if not (root / territory_name).is_dir(): continue

    declared_required = set(config.get("required_subfolders", []))
    declared_optional = set(config.get("optional_subfolders", []))
    declared_all = declared_required | declared_optional
    actual = {d.name for d in (root / territory_name).iterdir() if d.is_dir()} - EXCLUDED

    undeclared = actual - declared_all
    missing_required = declared_required - actual

    if config.get("strict_subfolder_enforcement"):
        # Also check nested subfolders for territories with "subfolders" dict
        ...
```

**Artifact**: `territory_diff` section in `enforcement_report.json` with per-territory breakdown.

---

### LAYER 2: `enforcement/leaf_node.py`

**Input**: Territories with `"allow_root_py": False`

**Logic**: For each such territory, scan root directory for `.py` files (excluding `__init__.py`). Any found -> violation.

**Artifact**: `leaf_node` section with file paths.

---

### LAYER 3: `enforcement/volatile_rules.py`

**Input**: Import graph (AD-5), territories with `"volatile": True`

**Logic**:

1. Any `Import` or `ImportFrom` targeting volatile territory path from outside -> violation
2. `from volatile_territory import *` -> violation
3. `__import__("volatile_territory...")` or `importlib.import_module("volatile_territory...")` -> violation
4. Files inside volatile territory with `__all__` -> violation (non-exporting rule, AD-7)

**Artifact**: `volatile_rules` section with importing file, import line, target.

---

### LAYER 4: `enforcement/mixin_ast.py`

**Input**: Files in `agentic_core/mixins/`

**Logic**: AST-parse each `.py` file (skip `__init__.py`). Must contain at least one `ClassDef` with name ending in `Mixin` or `Contract`.

**Companion**: Check that files relocated to `utils/` do not import from `mixins/` (uses import graph).

**Artifact**: `mixin_ast` section with violating files.

---

### LAYER 5: `enforcement/import_verifier.py`

**Input**: Import graph (AD-5)

**Logic**: For every internal `ImportFrom` (module starts with `agentic_core`, `apps_lic`, `apps_rg`, `apps_shared`):

1. Resolve module path to filesystem -> if missing, phantom module
2. For each imported name, check `hasattr` on loaded module -> if missing, phantom name

**Baseline lock**: Extends existing phantom baseline pattern. Uses non-growing debt (§29).

**Artifact**: `import_verifier` section with phantom list and counts.

---

### LAYER 6: `enforcement/blueprint_hash.py`

**Input**: Blueprint source files (per AD-4)

**Logic**:

1. Enumerate `.py` files in `structure_blueprint/` (exclude `__pycache__/`, `_verify.py`, `_simulate_verify.py`, `enforcement/`)
2. Sort by filename alphabetically
3. Concatenate raw bytes
4. SHA-256 full hex
5. Compare against stored hash in `structure_blueprint/blueprint_integrity.sha256`

**Update flag**: `--update-blueprint-hash` (local only, forbidden in CI)

**Artifact**: `blueprint_hash` section with computed vs stored hash.

---

### LAYER 8: `enforcement/cross_layer.py`

**Input**: Import graph (AD-5)

**Rules**:

1. **Volatile isolation**: No file outside volatile territory may import FROM volatile territory
2. **Utils purity**: `agentic_core/utils/` must not import from `agentic_core/mixins/`
3. **Config independence**: `agentic_core/config/` must not import from `L2_execution` or higher
4. **Core zero-dep**: `agentic_core/core/` must import ONLY stdlib

**Artifact**: `cross_layer` section with per-rule violation list.

---

## PART C — IMPLEMENTATION PHASES

### Phase 0: Enforcement Infrastructure (Before Reactive Fixes)

1. Create `structure_blueprint/enforcement/` sub-package with `__init__.py`
2. Create `enforcement/types.py` with `EnforcementResult` TypedDict
3. Create `enforcement/import_graph.py` with `ImportGraph` class
4. Wire `_verify.py` orchestrator to call enforcement modules (empty stubs initially)
5. Create `docs/reports/verification/` directory
6. Add `--update-blueprint-hash` to forbidden flags in `ssot_verify.yml`

### Phase 1: Blueprint legitimization (Findings 1 + 3)

7. Add `"core"` to `agentic_core_subfolders` in `_constants.py`
8. Add `territories["artifacts"]` with volatile schema (AD-7)
9. Remove phantom `territories["config"]` (line 920)

### Phase 2: Config root cleanup (Finding 2)

10. Move 7 root `.py` files to `config/core/`
11. Rename `env_loader.py` to `env_loader_config.py`
12. Update all importers (10 or fewer files)
13. Legitimize `agent_configs` with `"type": "spec_data"`, `"no_python": True`
14. Rename `domain_constitution.py` to `domain_constitution_config.py`
15. Fix 5 broken import paths

### Phase 3: Mixins cleanup (Finding 4)

16. Move `structural_healing_engine.py`, `meta_learning_engine.py`, `meta_learning_storage.py` to `agentic_core/utils/`
17. Update 4 importers
18. Rename `inspection_capability.py` to `inspection_capability_mixin.py`, update 11 importers
19. Tighten regex: remove `engine`/`storage` from allowed suffixes

### Phase 4: Prompt governance cleanup (Finding 5)

20. Move 10+ adversarial `.jinja` files to `security/adversarial/`
21. Reconcile blueprint subfolders: add required/optional sets (AD-6), remove phantom `version_registry`

### Phase 5: Layers 1+2+7 (Territory diff + Leaf Node + Strict subfolders)

22. Add `allow_root_py: False` to `config`, `knowledge` territories
23. Add `required_subfolders` / `optional_subfolders` to all governed territories (AD-6)
24. Implement `enforcement/territory_diff.py` (bidirectional, all territories, required vs optional)
25. Implement `enforcement/leaf_node.py`

### Phase 6: Layers 3+4 (Volatile + Mixin AST)

26. Implement `enforcement/volatile_rules.py` (import-FROM block, `__all__` block, dynamic import check)
27. Implement `enforcement/mixin_ast.py` (class structural check + utils->mixins prohibition)

### Phase 7: Layers 5+6 (Import verifier + Blueprint hash)

28. Implement `enforcement/import_verifier.py` (general phantom detection with baseline lock)
29. Implement `enforcement/blueprint_hash.py` (raw bytes, sorted, stored at `structure_blueprint/blueprint_integrity.sha256`)
30. Initialize `blueprint_integrity.sha256` with current hash

### Phase 8: Layer 8 + Final Verification

31. Implement `enforcement/cross_layer.py` (volatile isolation, utils purity, config independence, core zero-dep)
32. Wire all enforcement modules into `_verify.py` orchestrator
33. Emit `docs/reports/verification/enforcement_report.json`
34. Run `python -m agentic_core.L5_safety.config.structure_blueprint._verify` — all PASS
35. Run `pytest -xvv` — full green

---

## PART D — VERIFICATION CRITERIA

All criteria must pass. Each maps to a measurable artifact.

| # | Criterion | Artifact Location | Pass Condition |
| --- | --- | --- | --- |
| 1 | Territory auto-diff | `enforcement_report.json` -> `territory_diff` | 0 undeclared, 0 missing-required |
| 2 | Leaf node enforcement | `enforcement_report.json` -> `leaf_node` | 0 root `.py` in governed territories |
| 3 | Volatile import isolation | `enforcement_report.json` -> `volatile_rules` | 0 imports FROM volatile, 0 `__all__` in volatile |
| 4 | Mixin AST structural | `enforcement_report.json` -> `mixin_ast` | All files contain Mixin/Contract class |
| 5 | Import path verification | `enforcement_report.json` -> `import_verifier` | phantom_count <= baseline ceiling |
| 6 | Blueprint hash integrity | `enforcement_report.json` -> `blueprint_hash` | computed == stored |
| 7 | Strict subfolder enforcement | `enforcement_report.json` -> `territory_diff` | 0 violations in strict territories |
| 8 | Cross-layer import law | `enforcement_report.json` -> `cross_layer` | 0 violations across all 4 rules |
| 9 | Existing _verify.py checks | stdout + exit code | All 9 sections PASS |
| 10 | Test suite | `pytest -xvv` | Full green |

---

## PART E — PLAN INVARIANTS

| Invariant | Value |
| --- | --- |
| Plan version | v3 |
| Architecture decisions | 8 |
| Forensic findings | 5 |
| Hardening layers | 8 |
| Implementation phases | 9 (0-8) |
| Implementation steps | 35 |
| Enforcement modules | 7 (territory_diff, leaf_node, volatile_rules, mixin_ast, import_verifier, blueprint_hash, cross_layer) |
| Shared infrastructure | 2 (import_graph, types) |
| Artifact files | 2 (`enforcement_report.json`, `blueprint_integrity.sha256`) |

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

