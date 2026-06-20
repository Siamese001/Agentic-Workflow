# Apps Folder Taxonomy — Canonical Spec

> **Status**: Canonical (enforced by CI gate `T7r` + rule `.codex/rules/apps-folder-taxonomy.md`)
> **ADR**: `docs/architecture/adr/ADR-082-apps-folder-taxonomy.md`
> **SSOT Plan**: `.codex/plans/apps-folder-taxonomy-unification-b7d4e1.md`

This document is the canonical spec for the nine `apps_*` folders. CI gate T7r scans repo-root `apps_*` trees against these rules; the always-on rule loads this spec on any `apps_*` edit.

---

## 1. Mandatory sub-folders (every app unless explicitly library-only)

| Folder | Purpose | Required for |
|---|---|---|
| `config/`          | Agent/app specs, YAML policies, rubrics, routing tables | ALL |
| `engines/`         | Core agent engines / hop implementations | ALL except `apps_qna`, `apps_shared` (library-only) |
| `integrations/`    | Ingress runners, execution adapters, governed-run entrypoints | ALL |
| `outputs/`         | Renderers, formatters, output contracts | ALL except `apps_qna`, `apps_shared` |
| `reasoning/`       | Planners, scorers, cognition glue, orchestration | ALL |
| `types/`           | Pydantic models, dataclasses, type aliases | ALL |
| `validators/`      | Contract/schema/policy validators | ALL |
| `utils/`           | Pure helpers (no business logic) | ALL |
| `tests/`           | App-local unit tests | ALL |

## 2. Optional standardized sub-folders

| Folder | Purpose | When to include |
|---|---|---|
| `services/` | Long-lived in-process services (cache, session, telemetry sidecar) | When the app owns a service |
| `spine/`    | Spine manifest wiring + spine-only helpers | When app declares multi-stage spine |
| `tools/`    | App-specific CLIs and dev utilities | When count >0 |
| `scripts/`  | Ops scripts local to the app (smoke, bootstrap) | Strict budget: **≤5 files**. Rest → `ops_scripts/<app>/` per constitutional §31 |
| `data/`     | Static fixtures, bundled datasets, templates, prompts | Only for legitimate bundled data |

## 3. Forbidden folder names (CI gate rejects new instances)

| Forbidden | Canonical target |
|---|---|
| `L0_*`..`L6_*` under `apps_*/` | `reasoning/` (or equivalent sub-folder) — L-layer prefix is reserved for `agentic_core/` |
| `outreach_engine/`, `ingestion/`, `parsers/`, `builder/`, `router/` as top-level | `engines/<name>/` |
| `persistence/`, `observability/`, `runtime/`, `bootstrap_runtime.py` | `services/<name>/` |
| `enforcement/`, `proof/`, `policy/` (as code) | `validators/<name>/` |
| `adapters/`, `data_adapters/` | `integrations/<name>/` |
| `mixins/` | `utils/mixins/` |
| `orchestration/` | `reasoning/orchestration/` |
| `prompts/`, `templates/` | `data/<name>/` |
| `_compat/` | DELETE if empty; else time-bounded only |
| root-level `_*.py` | Relocate to a canonical sub-folder |
| `CamelCase.py` | Rename to `snake_case.py`, EXCEPT grandfathered `Hardened*Strategy.py` (re-exported via `__init__.py`) |

## 4. Documentation doc-set (mandatory at app root)

All seven required for every app:

1. `README.md` — purpose, quickstart, links
2. `RUNBOOK.md` — operational runbook
3. `SLO.md` — service-level objectives
4. `SVP_ENGINEERING_REVIEW.md` — engineering review snapshot
5. `TECHNICAL_SPEC.md` — architecture spec
6. `TEST_STRATEGY.md` — test pyramid + coverage targets
7. `spine_manifest.yaml` — spine wiring

Conditionally required:
- `THREAT_MODEL.md` — any app processing external/untrusted input (`apps_lic`, `apps_underwriting_ai`, `apps_rg`, `apps_research`).
- `PATHOLOGY_TAXONOMY.md` — interview-pack apps (`apps_qna`).

## 5. Enforcement

1. **Always-on rule** `.codex/rules/apps-folder-taxonomy.md` (trigger=model_decision) loads on any `apps_*` edit.
2. **CI gate** `ops_scripts/ci/check_apps_folder_taxonomy.py` — pre-commit + CI contract gate `T7r`:
   - `FORBIDDEN_ROOT_FOLDERS` check (scans every `apps_*/` for §3 violations)
   - Mandatory doc-set check (§4)
   - Root-level `_*.py` check
   - ADR-082 compat-shim exemption: files with marker `ADR-082` + `sys.modules[__name__]` | `DeprecationWarning` | `Compat shim` are allowed during the 2-week sunset window.
3. **Rule + gate bypass**: env var `APPS_TAXONOMY_BYPASS=1` with justification in commit message.

## 6. Migration mechanics

See ADR-082 §3. Every move: canonical-path creation + compat shim at OLD path + intra-package rewrite + targeted tests. 2-week compat sunset (2026-05-17 from re-execution 2026-05-03).

## 7. Deviations and exceptions

- Library-only apps (`apps_qna`, `apps_shared`) may omit `engines/` and `outputs/` — library-only is marked explicitly in the app's `README.md`.
- `apps_shared/contracts/` and `apps_shared/spine_emission/` are pre-existing canonical folders at the top of `apps_shared` — they do not require relocation; this spec acknowledges them as canonical peers to `integrations/`, `validators/`, etc. (see plan §16 item 10).

## 8. Changelog

| Date | Change |
|---|---|
| 2026-05-02 | Initial authoring (original execution; rolled back) |
| 2026-05-03 | Re-execution after user-directed rollback; sunset re-dated 2026-05-17 |
