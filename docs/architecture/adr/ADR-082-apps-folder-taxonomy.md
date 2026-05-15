# ADR-082 — Apps Folder Taxonomy Unification

- **Status**: Accepted
- **Date**: 2026-05-03 (re-execution; original 2026-05-02 rolled back)
- **Deciders**: Cursor Agent (authored), user (approved re-execution via Author-Gate option 1)
- **Context tier**: T3 (cross-app, cross-layer)
- **SSOT plan**: `.windsurf/plans/apps-folder-taxonomy-unification-b7d4e1.md`
- **Sunset window**: Compat shims sunset 2026-05-17 (2-week window from re-execution).
- **Slot provenance**: ADR-081 already occupies `docs/adr/ADR-081-apps-e2e-spine-cert-wireup.md`. Slot re-assigned to 082.

## 1. Context

Nine `apps_*` folders (`apps_eval`, `apps_exec`, `apps_lic`, `apps_qna`, `apps_research`, `apps_rfp`, `apps_rg`, `apps_shared`, `apps_underwriting_ai`) have divergent sub-folder taxonomies and inconsistent naming. See plan §2 for the audited divergence matrix. Outcomes:

- New files land in idiosyncratic per-app folders (e.g., `apps_lic/L1_cognition/`, `apps_rg/bootstrap_runtime.py`, `apps_qna/builder/`, `apps_shared/proof/`), creating cognitive drag and import churn.
- Constitutional §31 (SSOT folder routing) can only be extended to the apps layer once taxonomy is canonical.
- Documentation doc-set is uneven (4 of 9 apps missing `README.md` + `TECHNICAL_SPEC.md` + `TEST_STRATEGY.md`).

## 2. Decision

Canonicalize every `apps_*` tree to a fixed sub-folder grammar and enforce it with CI (gate `ops_scripts/ci/check_apps_folder_taxonomy.py`) + an always-on-trigger Cursor Agent rule (`.windsurf/rules/apps-folder-taxonomy.md`).

### 2.1 Mandatory sub-folders (all apps)

`config/`, `engines/` (exempt for library-only apps `apps_qna`, `apps_shared`), `integrations/`, `outputs/` (exempt for library-only apps), `reasoning/`, `types/`, `validators/`, `utils/`, `tests/`.

### 2.2 Optional standardized sub-folders

`services/`, `spine/`, `tools/`, `scripts/` (budget: ≤5 files; else move to `ops_scripts/<app>/`), `data/`.

### 2.3 Forbidden folders → canonical mapping

Full mapping in plan §3.3. Highlights:
- `apps_lic/L1_cognition/` → `apps_lic/reasoning/` (L-layer prefix reserved for `agentic_core/`)
- `apps_lic/outreach_engine/` → `apps_lic/engines/outreach/`
- `apps_lic/persistence/` + `apps_lic/observability/` → `apps_lic/services/{persistence,observability}/`
- `apps_lic/policy/` → `apps_lic/validators/policy/` (wholesale; per-file code/data split deferred)
- `apps_qna/{builder,router}/` → `apps_qna/engines/{builder,router}/`
- `apps_qna/templates/` → `apps_qna/data/templates/`
- `apps_rg/enforcement/` → `apps_rg/validators/enforcement/`
- `apps_rg/schemas/` → `apps_rg/config/schemas/`
- `apps_rg/scripts/` (77 items) → `ops_scripts/apps_rg/` wholesale (per-script triage deferred)
- `apps_rg/bootstrap_runtime.py` → `apps_rg/services/runtime/bootstrap.py`
- `apps_shared/adapters/` + `apps_shared/data_adapters/` → `apps_shared/integrations/{adapters,data_adapters}/`
- `apps_shared/mixins/` → `apps_shared/utils/mixins/`
- `apps_shared/orchestration/` → `apps_shared/reasoning/orchestration/`
- `apps_shared/prompts/` → `apps_shared/data/prompts/`
- `apps_shared/proof/` → `apps_shared/validators/proof/`
- `apps_shared/enforcement/` → `apps_shared/validators/enforcement/`
- `apps_shared/templates/` → `apps_shared/data/templates/`
- `apps_underwriting_ai/parsers/` → `apps_underwriting_ai/engines/parsers/`
- `apps_underwriting_ai/policy/` → `apps_underwriting_ai/validators/policy/`
- `apps_eval/_telemetry.py` → `apps_eval/services/telemetry.py`
- `apps_research/_telemetry.py` → `apps_research/services/telemetry.py`
- `apps_exec/_optional_agentic_core.py` → `apps_exec/utils/optional_agentic_core.py`
- `apps_shared/_apps_e2e_dry_run.py` → `apps_shared/utils/apps_e2e_dry_run.py`
- `apps_rfp/_compat/` → DELETE (empty)

### 2.4 Naming conventions

Folders `snake_case`, plural for containers. No `L0_`..`L6_` prefixes in `apps_*` (reserved for `agentic_core/`). No root-level `_*.py`. `CamelCase.py` only for grandfathered `Hardened*Strategy.py` classes.

### 2.5 Doc-set (mandatory at app root)

All 7 required: `README.md`, `RUNBOOK.md`, `SLO.md`, `SVP_ENGINEERING_REVIEW.md`, `TECHNICAL_SPEC.md`, `TEST_STRATEGY.md`, `spine_manifest.yaml`.

Conditionally required:
- `THREAT_MODEL.md` — apps processing external/untrusted input: `apps_lic`, `apps_underwriting_ai`, `apps_rg`, `apps_research`.
- `PATHOLOGY_TAXONOMY.md` — interview-pack apps: `apps_qna`.

## 3. Migration mechanics

Every move phase follows the sequence documented in plan §8. Summary:

1. **Move** via filesystem (pwsh `Move-Item` / `git mv` post-hoc). Destination parent `__init__.py` created if missing.
2. **Compat shim at OLD path**:
   - **Packages** (OLD `__init__.py`): `sys.modules`-redirect pattern — `_target = importlib.import_module("<NEW>")` + `sys.modules[__name__] = _target`. This preserves sub-module imports.
   - **File-level** (OLD `*.py`): self-contained re-export pattern — `from <NEW> import *` plus `DeprecationWarning` at module load.
   - **Root-level hot files with circular-import risk** (e.g., `apps_eval/_telemetry.py`): self-contained COPY of canonical logic (not delegating) to avoid circular initialization when the destination package's `__init__.py` eagerly imports back.
3. **Intra-package import rewrites**: files inside a moved package that reference `apps_X.OLD.*` (their own package) MUST be rewritten to `apps_X.NEW.*` — otherwise the NEW package fails to load because its own `__init__.py` goes through the OLD compat shim, which is a sys.modules alias to the still-loading NEW package.
4. **Targeted tests** via `pytest_mcp` scoped to the affected app + cross-app ADG fan-in.
5. **Compat-shim sunset**: 2 weeks (2026-05-17). On sunset date:
   - Delete every OLD-path `__init__.py` compat shim
   - Delete every OLD-path file-level compat shim
   - Rewrite every remaining consumer import `apps_X.OLD.*` → `apps_X.NEW.*`
   - Regen ADG; confirm zero `DeprecationWarning` sources in full pytest

## 4. Consequences

### Positive

- Uniform taxonomy across 9 apps ⇒ reduced cognitive load for new developers and Cursor Agent itself.
- Constitutional §31 (SSOT folder routing) extensible to `apps_*/` via new gate `T7r` (`check_apps_folder_taxonomy.py`).
- Documentation parity ⇒ every app has the same discoverability contract.
- Enables deferred work: apps-e2e certification re-run over canonical layout, Fort Knox arm rerun, constitutional §32 entry.

### Negative

- Short-term churn: ~16 compat shims + 38 intra-package file rewrites + 5 `__init__.py` root-level updates.
- 2-week sunset window requires active consumer-rewrite monitoring.
- Governance xfail tests and certification tooling (`tools/certification/apps_e2e/*`, `tools/certification/apps_rg_e2e/emit_proof_bundle.py`) reference old paths; the compat shim preserves them during the window.

### Rollback

Every phase is a single commit (or pwsh `Move-Item` batch that's reversible via `git restore`). If ADG regen flags new P0 violations post-wave, `git revert` the wave. The 2026-05-02 → 2026-05-02-revert cycle is the proof-of-concept: the full migration was reverted in hours.

## 5. Related

- Plan: `.windsurf/plans/apps-folder-taxonomy-unification-b7d4e1.md`
- Canonical spec: `docs/architecture/apps-folder-taxonomy.md`
- Enforcement rule: `.windsurf/rules/apps-folder-taxonomy.md`
- CI gate: `ops_scripts/ci/check_apps_folder_taxonomy.py`
- Constitutional §31 (SSOT folder routing) — source discipline this ADR extends to `apps_*/`.
- Constitutional §32 — reserved for apps-taxonomy-always-on entry (deferred; see plan §16 item 4).
