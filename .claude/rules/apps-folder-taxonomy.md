
<!-- Converted from `.claude/rules/apps-folder-taxonomy.md`. Original Cursor trigger: `model_decision`. -->

# Apps Folder Taxonomy (ADR-082)

> ⛔ Every `apps_*/` tree MUST follow the canonical taxonomy. CI gate `T7r` (`ops_scripts/ci/check_apps_folder_taxonomy.py`) enforces at pre-commit + CI time.

## Hard rules

1. **Forbidden root folders under any `apps_*/`**: `L0_*`..`L6_*`, `L1_cognition`, `outreach_engine`, `persistence`, `observability`, `runtime`, `builder`, `router`, `templates`, `ingestion`, `parsers`, `examples`, `adapters`, `data_adapters`, `mixins`, `orchestration`, `prompts`, `proof`, `enforcement`, `policy` (as top-level), `_compat`.
2. **Canonical target for each forbidden folder** — see `docs/architecture/apps-folder-taxonomy.md` §3.
3. **No root-level `_*.py`** in `apps_*/` (e.g., `apps_X/_telemetry.py`, `apps_X/_optional_foo.py`, `apps_X/bootstrap_runtime.py`). Canonical: `services/`, `utils/`, or appropriate sub-folder.
4. **Mandatory doc-set** at every app root: `README.md`, `RUNBOOK.md`, `SLO.md`, `SVP_ENGINEERING_REVIEW.md`, `TECHNICAL_SPEC.md`, `TEST_STRATEGY.md`, `spine_manifest.yaml`.
5. **Conditional docs**: `THREAT_MODEL.md` for `apps_lic`/`apps_rg`/`apps_research`/`apps_underwriting_ai`; `PATHOLOGY_TAXONOMY.md` for `apps_qna`.
6. **Scripts budget**: `apps_*/scripts/` ≤ 5 files. Rest → `ops_scripts/<app>/` (constitutional §31).
7. **No `L0_`..`L6_` prefix in `apps_*/`** — reserved for `agentic_core/`.
8. **`CamelCase.py`** files only for grandfathered `Hardened*Strategy.py` (re-exported via `__init__.py`). New files: `snake_case.py`.

## Canonical sub-folder grammar

| Folder | Purpose |
|---|---|
| `config/` | Agent specs, YAML policies, rubrics, routing tables |
| `engines/` | Core agent engines / hop implementations (exempt for library-only apps) |
| `integrations/` | Ingress runners, adapters, governed-run entrypoints |
| `outputs/` | Renderers, formatters (exempt for library-only apps) |
| `reasoning/` | Planners, scorers, cognition glue, orchestration |
| `services/` | Long-lived in-process services |
| `types/` | Pydantic models, dataclasses |
| `utils/` | Pure helpers (no business logic) |
| `validators/` | Contract/schema/policy validators |
| `data/` | Static fixtures, bundled datasets, prompts, templates |
| `spine/` | Spine manifest wiring (when app declares multi-stage spine) |

Library-only apps (`apps_qna`, `apps_shared`) may omit `engines/` and `outputs/`.

> ⛔ **`apps_<x>/tests/` is FORBIDDEN.** App-local test directories were consolidated into the 3-surface canonical test layout (plan `apps-test-surface-consolidation-11acd9-v2`). CI gate `T7r` (`check_apps_folder_taxonomy.py`) flags any `tests/` sub-folder at an app root as a violation.

## Canonical test surfaces

| Surface | Path | Content |
|---|---|---|
| Unit | `tests/unit/<app>/` | Isolated unit tests; mirrors `apps_<app>/` structure |
| Integration | `tests/<app>/` | Integration/E2E tests requiring real dependencies |
| Contract | `tests/_apps_contract/test_<app>_*.py` | Cross-app contract and governance tests |

No test files belong inside `apps_<x>/`. Use `git mv` + `tests/<app>/` or `tests/unit/<app>/`.

## Migration discipline

When moving files under `apps_*/`:

1. Create canonical target + `__init__.py` chain.
2. `Move-Item` / `git mv` the files.
3. Write a **compat shim at the OLD path**:
   - **Package `__init__.py`**: `sys.modules`-redirect pattern + `DeprecationWarning`
   - **File-level `.py`**: self-contained content copy + `DeprecationWarning` + `ADR-082` marker (avoids circular imports when parent package has eager submodule imports)
4. Rewrite intra-package imports (`from apps_X.OLD.` → `from apps_X.NEW.`) across the moved folder.
5. Run targeted pytest scoped to the affected app + ADG fan-in.
6. **Sunset date**: 2 weeks from move. Delete compat shims; rewrite remaining consumers; regen ADG.

## Enforcement layers

1. **This rule** (trigger=model_decision) — loads when Cursor Agent edits `apps_*/` content.
2. **CI gate `T7r`** — `ops_scripts/ci/check_apps_folder_taxonomy.py` runs pre-commit + CI.
3. **Compat-shim exemption** — during the 2-week sunset window, files containing `ADR-082` + (`sys.modules[__name__]` | `DeprecationWarning` | `Compat shim`) are exempt.

## Bypass

`APPS_TAXONOMY_BYPASS=1` env var — emits WARNING and exits 0. Use only for scripted migrations or acknowledged exploratory runs.

## References

- ADR: `docs/architecture/adr/ADR-082-apps-folder-taxonomy.md`
- Canonical spec: `docs/architecture/apps-folder-taxonomy.md`
- Plan: `.claude/plans/apps-folder-taxonomy-unification-b7d4e1.md`
- Constitutional §31 (SSOT folder routing) — the pattern this rule extends to `apps_*/`.
