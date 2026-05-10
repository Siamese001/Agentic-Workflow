# Apps Test Surface Taxonomy — Enforcement Rule

> ⛔ **All test files for `apps_<x>` packages MUST live in one of the 3 canonical surfaces below.**
> App-local `apps_<x>/tests/` directories are FORBIDDEN (consolidated 2026-05-09,
> plan `apps-test-surface-consolidation-11acd9-v2`).

## The 3 Canonical Test Surfaces

| Surface | Path | Content |
|---|---|---|
| **Unit** | `tests/unit/<app>/` | Isolated unit tests; mirrors `apps_<app>/` structure |
| **Integration** | `tests/<app>/` | Integration/E2E tests requiring real dependencies |
| **Contract** | `tests/_apps_contract/test_<app>_*.py` | Cross-app contract and governance tests |

`<app>` is the full package name, e.g. `apps_rg`, `apps_qna`.

## Forbidden Locations

| Location | Why forbidden |
|---|---|
| `apps_<x>/tests/` | App-local test directory — consolidated into 3-surface layout |
| `tests/integration/apps_<x>/` | Misplaced integration tests — use `tests/<app>/` instead |

## Invariants

1. **No `apps_<x>/tests/` directories** — CI gate `T7r` (`check_apps_folder_taxonomy.py`) flags these as violations.
2. **No `tests/integration/apps_<x>/` directories** — CI gate `TSP1` (`check_apps_test_surface_parity.py`) flags these as violations.
3. **Every `apps_<x>` package MUST have a `tests/<app>/` directory** with at least `__init__.py` + `conftest.py`.
4. **Every `apps_<x>` package MUST have a `tests/unit/<app>/` directory** with at least `__init__.py`.

## Enforcement

- `ops_scripts/ci/check_apps_folder_taxonomy.py` (T7r) — blocks `apps_<x>/tests/` subdirectories
- `ops_scripts/ci/check_apps_test_surface_parity.py` (TSP1) — verifies all 3 surfaces exist + no misplaced dirs

## Migration (when adding new apps_<x> package)

1. Create `tests/unit/<app>/__init__.py`
2. Create `tests/<app>/__init__.py` + `tests/<app>/conftest.py`
3. Add contract tests as `tests/_apps_contract/test_<app>_*.py`
4. Do NOT create `apps_<app>/tests/`

## References

- Plan: `apps-test-surface-consolidation-11acd9-v2`
- Sibling rule: `.windsurf/rules/apps-folder-taxonomy.md`
- Path constants: `agentic_core.L0_routing.config.path_constants` (`APPS_TEST_UNIT_DIR`, `APPS_TEST_INTEGRATION_DIR`, `APPS_CONTRACT_DIR`)
