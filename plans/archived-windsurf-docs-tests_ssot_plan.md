---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\tests_ssot_plan.md'
original_relative_path: 'tests_ssot_plan.md'
source_sha256: 38772135087b8c3b924d191fb73060a4d757379126440a4763780aa20fe8e987
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-02'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Single SSOT for `tests/` Subfolder Structure

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Problem Statement

The `tests/` directory has **no authoritative SSOT**. Four separate definitions exist,
all diverged from each other and from the actual disk state. The healing pipeline
(`LocationHealerAgent`, `TestGeneratorAgent`) invents test locations because there is
nothing canonical to consult.

## Current Fragmentation (Audit)

| Definition | File | Contents | Problem |
|---|---|---|---|
| Territory declaration | `_constants.py` `tests` | 15 subfolders | Missing 15 actual disk folders |
| Subfolder map | `derived.py` `TESTS_L2_SUBFOLDER_MAP` | `{unit,integration,e2e,guardian,apps_lic}` | Stale, wrong shape |
| Local map | `align_tests_structure_util.py` | `{unit:[test_agents,…]}` | Completely invented, diverged |
| Path constants | `ssot.py` `TESTS_AUTOGEN_DIR` etc. | 4 constants | `autogen` not in blueprint territory |

### Subfolders on disk NOT in blueprint (15)
`agentic_core`, `apps_lic`, `apps_rg`, `apps_shared`, `architecture`, `contracts`,
`enforcement`, `governance`, `integration_e2e`, `integration_full_deps`, `scripts`,
`sovereign_hardening`, `ssot_equivalence`, `support`, `system_learning`

### Healing pipeline gaps
- `LocationHealerAgent`: no routing rules for test file placement
- `TestGeneratorAgent`: hardcodes `tests/autogen` (not in blueprint)
- Neither consults any SSOT to decide where a test file goes

---

## Design: One SSOT, All Consumers Read From It

### Canonical SSOT location
`agentic_core/L5_safety/config/structure_blueprint/_constants.py` → `tests` territory

This is already the authoritative source for `is_path_allowed()`. Everything else
**imports from it**; nothing else defines its own map.

### Required additions to `_constants.py` `tests` territory

Add all missing subfolders with canonical categorization:

```
tests/
  unit/              ← mirror of agentic_core/ + apps_*/  (already: exclude_from_depth_rules)
  unit_min_deps/     ← minimal-dep unit tests (no mirror contract)
  integration/       ← inter-component tests (already: exclude_from_depth_rules)
  integration_e2e/   ← full-pipeline integration (→ merge into integration/ long-term)
  integration_full_deps/ ← heavy-dep integration (→ merge into integration/ long-term)
  e2e/               ← full user-flow simulations
  guardian/          ← architectural compliance (AST-based)
  architecture/      ← structural invariant tests (→ alias for guardian/)
  governance/        ← governance policy tests
  contracts/         ← contract/interface tests
  enforcement/       ← enforcement rule tests
  behavioral/        ← behavioral acceptance tests
  performance/       ← benchmarks
  stress/            ← load tests
  support/           ← shared test infrastructure (helpers, fixtures, base classes)
  system_learning/   ← system_learning module tests (mirrors system_learning/)
  sovereign_hardening/ ← sovereign integrity tests
  ssot_equivalence/  ← SSOT equivalence/drift tests
  scripts/           ← script-level tests
  core/              ← core framework tests
  fixtures/          ← shared pytest fixtures
  goldens/           ← golden data
  snapshots/         ← snapshot data
  helpers/           ← test helper modules
  misc/              ← miscellaneous
  _quarantine/       ← tests pending triage
  _config/           ← test configuration
```

Add `test_routing_rules` to the `unit` entry:
```python
"test_routing_rules": {
    "agentic_core/**": "tests/unit/agentic_core/",
    "apps_lic/**":     "tests/unit/apps_lic/",
    "apps_rg/**":      "tests/unit/apps_rg/",
    "apps_shared/**":  "tests/unit/apps_shared/",
    "system_learning/**": "tests/unit_min_deps/system_learning/",
}
```

### Exported constants from `ssot.py`

Add:
```python
TEST_MIRROR_ROOTS: frozenset[str] = frozenset({"agentic_core", "apps_lic", "apps_rg", "apps_shared"})
TEST_MIRROR_BASE: str = "tests/unit"
TEST_CANONICAL_LOCATION_MAP: dict[str, str] = {
    "agentic_core": "tests/unit/agentic_core",
    "apps_lic":     "tests/unit/apps_lic",
    "apps_rg":      "tests/unit/apps_rg",
    "apps_shared":  "tests/unit/apps_shared",
    "system_learning": "tests/unit_min_deps/system_learning",
}
```

Remove: `TESTS_AUTOGEN_DIR` (autogen not in blueprint — route to `tests/unit_min_deps/` instead)

### Delete / replace impostor maps

| File | Action |
|---|---|
| `derived.py` `TESTS_L2_SUBFOLDER_MAP` | Replace body with import-and-derive from `_constants.py` territory |
| `align_tests_structure_util.py` local map | Replace with `from agentic_core.L5_safety.config.structure_blueprint import TESTS_SUBFOLDER_MAP` |
| `TestGeneratorAgent.py` hardcoded `tests/autogen` | Replace with `TESTS_AUTOGEN_DIR` → then point to `tests/unit_min_deps/` or source-mirrored path |

### Wire `LocationHealerAgent`

Import `TEST_CANONICAL_LOCATION_MAP` from SSOT. When the healer encounters a
`test_*.py` file that needs placement:

```python
from agentic_core.L5_safety.config.structure_blueprint import TEST_CANONICAL_LOCATION_MAP

def canonical_test_path(source_path: Path, repo_root: Path) -> Path:
    rel = source_path.relative_to(repo_root)
    root = rel.parts[0]
    if root in TEST_CANONICAL_LOCATION_MAP:
        mirror_base = Path(TEST_CANONICAL_LOCATION_MAP[root])
        sub = Path(*rel.parts[1:])  # strip the root
        return repo_root / mirror_base / sub.parent / f"test_{source_path.stem}.py"
    return repo_root / "tests/unit_min_deps" / f"test_{source_path.stem}.py"
```

---

## Implementation Phases

### Phase A — SSOT declaration (this session)
1. Add all 15 missing subfolders to `_constants.py` `tests` territory
2. Add `TEST_CANONICAL_LOCATION_MAP`, `TEST_MIRROR_ROOTS`, `TEST_MIRROR_BASE` to `ssot.py`
3. Export the new constants from `__init__.py`

### Phase B — Delete impostors
4. Replace `derived.py` `TESTS_L2_SUBFOLDER_MAP` with derivation from territory
5. Replace `align_tests_structure_util.py` local map with SSOT import
6. Replace `TestGeneratorAgent` hardcoded path with SSOT constant

### Phase C — Wire healers
7. Wire `LocationHealerAgent` to use `TEST_CANONICAL_LOCATION_MAP`
8. Wire `TestGeneratorAgent.tests_dir` default to use SSOT constant

### Phase D — Migrate existing misplaced tests
9. Move `tests/agentic_core/` → `tests/unit/agentic_core/`
10. Move `tests/apps_lic/`, `tests/apps_rg/`, `tests/apps_shared/` → `tests/unit/`
11. Update `conftest.py` / `pytest.ini` testpaths

---

## Invariant Test (guard against regression)

Add `tests/architecture/test_tests_ssot_invariant.py`:
- Assert every folder under `tests/` is declared in `_constants.py` territory
- Assert `TESTS_L2_SUBFOLDER_MAP` in `derived.py` equals keys from territory
- Assert `align_tests_structure_util.TESTS_L2_SUBFOLDER_MAP` imports from SSOT
- Assert no file in `LocationHealerAgent.py` hardcodes a `tests/` path

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

