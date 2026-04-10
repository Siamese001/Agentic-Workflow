# Archive: structure_blueprint v1 enforcement modules

**Archived:** 2026-04-10
**Reason:** SSOT Structure Enforcement Revamp — Method A (YAML-only enforcement)

## What was archived

These modules implemented runtime Python-based structure validation that has been
replaced by a simplified YAML policy + single-file CI gate:

| Module | Lines | Purpose |
|--------|-------|---------|
| `_verify.py` | ~983 | Runtime structure verification against SSOT |
| `_simulate_verify.py` | ~410 | Dry-run structure simulation |
| `sovereign_kernel.py` | ~250 | Kernel extension boundary checking |
| `governance.py` | ~158 | Healing/mission/gravity/MCP config |
| `enforcement/import_graph.py` | ~354 | Import graph analysis for structure |
| `enforcement/types.py` | ~243 | Type definitions for enforcement |
| `enforcement/known_debt_baseline.json` | — | Known debt baseline data |
| `enforcement/missing_optional_baseline.json` | — | Missing optional baseline data |

**Total archived: ~2,400 lines of Python**

## Replacement

- **Policy YAML:** `config/structure_blueprint/structure_policy.yaml` (~100 lines)
- **CI gate:** `ops_scripts/ci/check_structure_policy.py` (~150 lines)

## ADG evidence

- ADG snapshot: `04102026_1052`
- Fan-in on all archived modules: **0 external production consumers**
- `_verify.py`: only consumer of `enforcement/` subdirectory
- `sovereign_kernel.py`: 1 consumer in `ops_scripts/archives/orphaned/` (already archived)
- `governance.py`: 0 consumers
- `_simulate_verify.py`: 0 consumers

## Wave 2 Archive (2026-04-11): YAML configs

| File | Purpose |
|------|---------|
| `territories.yaml` | Territory structure definitions (depth, purpose, subfolders) |
| `layers.yaml` | Layer definitions |

These YAMLs are superseded by `config/structure_blueprint/structure_policy.yaml`.
Runtime constants that consumed these have been hardcoded as empty frozensets
(`ALLOW_ROOT_PY_TERRITORIES`, `LAYER_PREFIX_EXEMPT_TERRITORIES`) in L0 `path_constants.py`.

## Safe to delete permanently after

90-day archive period (per constitutional §3). Target: 2026-07-10.
