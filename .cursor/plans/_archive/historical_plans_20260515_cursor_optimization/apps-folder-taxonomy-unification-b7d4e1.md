# Apps Folder Taxonomy Unification — Plan

> **Status**: Draft
> **Author**: Cascade (2026-05-01)
> **Tier**: T3 (cross-app, cross-layer, ~dozens of files per app, import rewrites)
> **Execution**: Plan-only this session. No code changes until waves are dispatched.
> **SSOT location**: `.windsurf/plans/apps-folder-taxonomy-unification-b7d4e1.md`
> **Related**: ADR (TBD — proposed `ADR-081-apps-folder-taxonomy.md`), `AGENTS.md` §Notion Workspace Map

---

## 1. Problem Statement

The nine `apps_*` folders (`apps_eval`, `apps_exec`, `apps_lic`, `apps_qna`, `apps_research`, `apps_rfp`, `apps_rg`, `apps_shared`, `apps_underwriting_ai`) have **divergent sub-folder taxonomies** and **inconsistent naming conventions**. This creates:

- **Cognitive load**: each app requires re-learning where engines, outputs, validators, and reasoning modules live.
- **Import drift**: cross-app consumers (`apps_shared`, `system_learning`, tests) reference heterogeneous paths; refactors cascade unpredictably.
- **SSOT violations** — new files land in legacy-only folders (e.g., `apps_rg/scripts/` has 76 items) when they belong elsewhere.
- **Documentation gaps** — `README.md`, `TECHNICAL_SPEC.md`, `TEST_STRATEGY.md` exist for some apps, absent from others.
- **Blocks constitutional §31** (SSOT folder routing) extension to the apps layer — currently only enforced on `ops_scripts/` / `.windsurf/scripts/` / `tools/`.

---

## 2. Evidence — Current Divergence Matrix

Observed 2026-05-01 via native directory listing.

| Sub-folder | eval | exec | lic | qna | research | rfp | rg | shared | underwriting_ai |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `config/`           | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `engines/`          | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| `integrations/`     | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `outputs/`          | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| `reasoning/`        | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `services/`         | ✓ | ✓ | 1-item | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ |
| `spine/`            | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| `scripts/`          | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ (76) | ✓ | ✗ |
| `tests/`            | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `tools/`            | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ |
| `types/`            | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `utils/`            | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ |
| `validators/`       | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |

**Idiosyncratic folders** (single-app):
- `apps_lic/`: `L1_cognition/`, `outreach_engine/`, `persistence/`, `policy/`, `observability/`
- `apps_qna/`: `builder/`, `router/`, `templates/`
- `apps_rfp/`: `_compat/`, `data/`
- `apps_rg/`: `enforcement/`, `runtime/`, `schemas/`, `bootstrap_runtime.py` (root-level)
- `apps_shared/`: `adapters/`, `data_adapters/`, `mixins/`, `orchestration/`, `prompts/`, `proof/`, `enforcement/`
- `apps_underwriting_ai/`: `ingestion/`, `parsers/`, `examples/`

**Doc-set divergence** at app root:
| Doc file | Present in |
|---|---|
| `README.md` | all EXCEPT `apps_lic` |
| `RUNBOOK.md` | all EXCEPT `apps_rg` |
| `SLO.md` | all EXCEPT `apps_rg` |
| `SVP_ENGINEERING_REVIEW.md` | all EXCEPT `apps_rg` |
| `TECHNICAL_SPEC.md` | eval, exec, qna, research, rfp only |
| `TEST_STRATEGY.md` | eval, exec, qna, research, rfp only |
| `THREAT_MODEL.md` | `apps_lic`, `apps_underwriting_ai` only |
| `spine_manifest.yaml` | ALL ✓ |

**Root-level Python stragglers** (should move into a sub-folder):
- `apps_eval/_telemetry.py`, `apps_research/_telemetry.py`
- `apps_exec/_optional_agentic_core.py`
- `apps_rg/bootstrap_runtime.py`

---

## 3. Proposed Canonical Taxonomy

### 3.1 Mandatory sub-folders (every app)

| Sub-folder | Purpose | Required? |
|---|---|---|
| `config/`          | Agent/app specs, policies, rubrics, YAML configs | ✅ mandatory |
| `engines/`         | Core agent engines / hop implementations | ✅ mandatory (hop/agent apps); optional for library-only apps (`apps_qna`, `apps_shared`) |
| `integrations/`    | Ingress runners, external adapters, governed-run entrypoints | ✅ mandatory |
| `outputs/`         | Renderers, output formatters | ✅ mandatory (producer apps); N/A for library-only |
| `reasoning/`       | Planners, scorers, cognition glue | ✅ mandatory |
| `types/`           | Pydantic models, dataclasses, type aliases | ✅ mandatory |
| `validators/`      | Contract / schema / policy validators | ✅ mandatory |
| `utils/`           | Pure helpers (no business logic) | ✅ mandatory |
| `tests/`           | App-local unit tests | ✅ mandatory |

### 3.2 Optional standardized sub-folders

| Sub-folder | Purpose | When to include |
|---|---|---|
| `services/`        | Long-lived in-process services (cache, session, telemetry sidecar) | When the app owns a service; otherwise omit |
| `spine/`           | Spine manifest wiring + spine-only helpers | When app declares multi-stage spine (eval/exec/research/rfp pattern) |
| `tools/`           | App-specific CLIs and dev utilities | When count >0; else omit entirely |
| `scripts/`         | Ops scripts local to the app (smoke, bootstrap) | Strict budget: **≤5 files**; otherwise move to `ops_scripts/<app>/` per constitutional §31 |
| `data/`            | Static fixtures, embedded datasets | Only for legitimate bundled data; no generated artifacts |

### 3.3 Forbidden / to-be-renamed folders

| Current folder | Where it should live | Reason |
|---|---|---|
| `apps_lic/L1_cognition/` | `apps_lic/reasoning/` | L-layer prefix belongs to `agentic_core/`, not apps |
| `apps_lic/outreach_engine/` | `apps_lic/engines/outreach/` | Single-engine dir belongs under `engines/` |
| `apps_lic/persistence/` | `apps_lic/services/persistence/` | Persistence is a service |
| `apps_lic/policy/` | `apps_lic/validators/policy/` OR `apps_lic/config/policy/` | Policy files split: code → validators, data → config |
| `apps_lic/observability/` | `apps_lic/services/observability/` | Observability is a service |
| `apps_qna/builder/` | `apps_qna/engines/builder/` | Builder is an engine |
| `apps_qna/router/` | `apps_qna/engines/router/` | Router is an engine |
| `apps_qna/templates/` | `apps_qna/data/templates/` | Static templates are bundled data |
| `apps_rfp/_compat/` | DELETE (empty) | Empty compat dir; no content |
| `apps_rg/enforcement/` | `apps_rg/validators/enforcement/` OR `apps_shared/enforcement/` | Evaluate per-file (single file currently) |
| `apps_rg/runtime/` | `apps_rg/services/runtime/` | Runtime services |
| `apps_rg/schemas/` | `apps_rg/config/schemas/` | Schemas are configuration |
| `apps_rg/bootstrap_runtime.py` | `apps_rg/services/runtime/bootstrap.py` | Root-level stragglers forbidden |
| `apps_shared/adapters/` | `apps_shared/integrations/adapters/` | Adapters are integrations |
| `apps_shared/data_adapters/` | `apps_shared/integrations/data_adapters/` | Same |
| `apps_shared/mixins/` | `apps_shared/utils/mixins/` | Mixins are utilities |
| `apps_shared/orchestration/` | `apps_shared/reasoning/orchestration/` | Orchestration is reasoning |
| `apps_shared/prompts/` | `apps_shared/data/prompts/` | Static prompt files |
| `apps_shared/proof/` | `apps_shared/validators/proof/` | Proof artifacts are validation |
| `apps_shared/enforcement/` | `apps_shared/validators/enforcement/` | Enforcement is validation |
| `apps_underwriting_ai/ingestion/` | `apps_underwriting_ai/engines/ingestion/` | Ingestion is an engine stage |
| `apps_underwriting_ai/parsers/` | `apps_underwriting_ai/engines/parsers/` | Parsers are engine stage |
| `apps_underwriting_ai/examples/` | `docs/examples/apps_underwriting_ai/` OR DELETE | Examples belong in docs |
| `apps_eval/_telemetry.py` | `apps_eval/services/telemetry.py` | Root-level strip |
| `apps_research/_telemetry.py` | `apps_research/services/telemetry.py` | Root-level strip |
| `apps_exec/_optional_agentic_core.py` | `apps_exec/utils/optional_agentic_core.py` | Root-level strip |

### 3.4 Naming conventions (all apps)

| Convention | Rule |
|---|---|
| Folder names | `snake_case`, singular-or-plural-consistent (plural preferred for containers: `engines`, `validators`, `types`, `services`) |
| Folder names reserved | No `L0_`..`L6_` prefixes in `apps_*` (those are `agentic_core/` only) |
| Python modules | `snake_case.py`; no `CamelCase.py` except legacy `Hardened*Strategy.py` in `apps_rg/enforcement/` + `apps_shared/enforcement/` (grandfathered via `__init__.py` re-exports) |
| Root-level `_*.py` | Forbidden (move to sub-folder); `_compat/` sub-folders allowed only during active migration windows |
| `__init__.py` | Required in every sub-folder |
| `__main__.py` | At app root only (entrypoint) |

### 3.5 Documentation doc-set (app root — mandatory)

Every app MUST have all seven at app root:
1. `README.md` — purpose, quickstart, links to other docs
2. `RUNBOOK.md` — operational runbook (start, stop, healthchecks)
3. `SLO.md` — service-level objectives
4. `SVP_ENGINEERING_REVIEW.md` — engineering review snapshot
5. `TECHNICAL_SPEC.md` — architecture spec
6. `TEST_STRATEGY.md` — test pyramid + coverage targets
7. `spine_manifest.yaml` — spine wiring

Conditionally required:
- `THREAT_MODEL.md` — required for any app with external/untrusted input (`apps_lic`, `apps_underwriting_ai`, `apps_rg`, `apps_research`)
- `PATHOLOGY_TAXONOMY.md` — required for interview-pack apps (`apps_qna`)

---

## 4. ADG_GRAPH_LAYER_EVIDENCE

> Constitutional §22 — T3 refactoring plans MUST cite graph-layer primitives as primary drivers.

### 4.1 Materialized views consulted (to be queried during Wave execution)

| MV | Use in this refactor |
|---|---|
| `mv_graph_reverse_dependency_hotspots` | Identify high-fan-in modules in apps_* whose move requires the most import rewrites |
| `mv_graph_chokepoint_bridges` | Detect single-file chokepoints (e.g., `apps_rg/bootstrap_runtime.py`) whose move risks breaking cross-app wiring |
| `mv_graph_critical_path_blast_radius` | Compute blast radius for each renamed folder before commit |
| `mv_hotspot_centrality` | Rank modules by degree centrality — high-centrality modules move in earlier, smaller waves |
| `mv_dependency_cone_risk` | Quantify reverse-cone size for each folder rename |
| `mv_exemptions_near_critical_paths` | Surface guardian exemptions that may need updating after rename |

### 4.2 Semantic edges used

| Edge | Use |
|---|---|
| `imports` | Primary: every import statement referencing a moved path must be rewritten |
| `resolves_callsite` | Detect dynamic imports / string-based lookups that grep/ADG static edges miss |
| `reads_from`, `writes_to` | Validate `data/` / `config/` moves don't break IO paths |

### 4.3 Pre-built P-views cross-referenced

| P-view | Relevance |
|---|---|
| `v_p0_apps_direct_infra`    | Apps importing infrastructure directly — MUST remain untouched by this refactor (structural, not taxonomic) |
| `v_p1_mis_layered_infra`    | Candidates already flagged — reconcile with proposed rename targets to avoid worsening |
| `v_p1_zero_caller_infra`    | Dead code — identify during Wave 2 audit so it gets deleted rather than moved |
| `v_p2_duplicated_adapters`  | `apps_shared/adapters/` + `apps_shared/data_adapters/` + per-app adapter dirs may already be flagged; consolidate on move |

**Note**: every migration wave below produces a `## ADG_HOTSPOT_REPORT` table (see §5 template) populated by the above MVs before any file moves.

---

## 5. ADG_HOTSPOT_REPORT (populated per-wave during execution)

Template each wave uses:

| Rank | Archetype | Layer | File/Folder | Fan-in | Fan-out | Impact Score | Surface(s) | Notes |
|---|---|---|---|---:|---:|---:|---|---|
| 1 | … | L_APP | … | … | … | … | Execution/Write/Security/State/Observability | … |

Archetypes per constitutional §23(c): `CENTRAL_DEPENDENCY`, `ORCHESTRATOR`, `STATE_NODE`, `SAFETY_GATEKEEPER`.

Layer multipliers (§23(d)): L0/L5 ×2.0, L3/L4 ×1.75, L1/L2 ×1.0, L6 ×0.75 — applied post-discovery when ranking.

**Pre-seed ranking hypothesis** (to verify in Wave 2):
| Rank | Candidate | Archetype | Why |
|---|---|---|---|
| 1 | `apps_shared/enforcement/` | SAFETY_GATEKEEPER | 18 files; every app imports it; highest blast radius |
| 2 | `apps_shared/reasoning/` | CENTRAL_DEPENDENCY | 15 files; shared cognition glue |
| 3 | `apps_shared/types/` | CENTRAL_DEPENDENCY | 59 files; highest fan-in of any single folder in the repo |
| 4 | `apps_shared/proof/` | SAFETY_GATEKEEPER | 24 files; proof/validator consolidation |
| 5 | `apps_rg/bootstrap_runtime.py` | ORCHESTRATOR | single-file chokepoint at apps_rg root |
| 6 | `apps_lic/L1_cognition/` | CENTRAL_DEPENDENCY | reserved-prefix collision with agentic_core |

---

## 6. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| **W1 — Charter** | P1.1, P1.2 | ADR + canonical spec document | 6k | §3 taxonomy accepted | Todo | ADR merged; `docs/architecture/apps-folder-taxonomy.md` exists |
| **W2 — Audit** | P2.1..P2.9 | One gap-analysis phase per app against canonical | 12k | ADG snapshot current | Todo | Per-app delta table + file-move matrix committed to plan |
| **W3 — Low-risk renames** | P3.1..P3.3 | Root-level stragglers + empty dirs (`_compat/`, `_telemetry.py`, `_optional_agentic_core.py`, `bootstrap_runtime.py`) | 8k | Low fan-in | Todo | 4 root-level files moved; `_compat/` deleted; tests green |
| **W4 — Apps without doc set** | P4.1..P4.4 | Author missing `README/TECHNICAL_SPEC/TEST_STRATEGY` for `apps_lic`, `apps_rg`, `apps_shared`, `apps_underwriting_ai` | 14k | No blockers | Todo | All 9 apps have 7-doc set (+ conditional THREAT_MODEL / PATHOLOGY_TAXONOMY) |
| **W5 — apps_qna normalization** | P5.1..P5.3 | `builder/` → `engines/builder/`, `router/` → `engines/router/`, `templates/` → `data/templates/` | 10k | qna has test coverage for router + builder | Todo | 3 folders renamed; all pack builds pass |
| **W6 — apps_lic normalization** | P6.1..P6.5 | `L1_cognition/` → `reasoning/`, `outreach_engine/` → `engines/outreach/`, `persistence/` → `services/persistence/`, `policy/` split, `observability/` → `services/observability/` | 18k | apps_lic suite passes today | Todo | 5 folders renamed/split; imports rewritten; suite green |
| **W7 — apps_underwriting_ai normalization** | P7.1..P7.3 | `ingestion/` + `parsers/` → `engines/*`, `examples/` → `docs/examples/` or delete | 8k | app still pre-production | Todo | 3 folders moved; tests green |
| **W8 — apps_rg normalization** | P8.1..P8.4 | `enforcement/` reloc, `runtime/` → `services/runtime/`, `schemas/` → `config/schemas/`, `scripts/` budget audit (76 items) | 22k | High blast radius expected | Todo | All moves applied; apps_rg `scripts/` trimmed to ≤5 files or migrated to `ops_scripts/apps_rg/` |
| **W9 — apps_shared consolidation** | P9.1..P9.6 | `adapters/`+`data_adapters/`→`integrations/`, `mixins/`→`utils/mixins/`, `orchestration/`→`reasoning/orchestration/`, `prompts/`→`data/prompts/`, `proof/`→`validators/proof/`, `enforcement/`→`validators/enforcement/` | 28k | Highest blast radius — ALL apps consume shared | Todo | 6 folders moved; all 9 apps still import cleanly; full pytest green |
| **W10 — Enforcement** | P10.1, P10.2 | CI gate `check_apps_folder_taxonomy.py` + `.windsurf/rules/apps-folder-taxonomy.md` + constitutional §32 entry | 10k | All prior waves done | Todo | Gate blocks forbidden folders on new PRs; rule loaded always-on |

**Total est.**: ~136k tokens across 10 waves, 39 phases.

---

## 7. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---:|---:|---|
| P1.1 | Draft ADR-081 apps folder taxonomy | 1 (new) | Getting §3 accepted | 3k | Todo |
| P1.2 | Publish `docs/architecture/apps-folder-taxonomy.md` (canonical spec) | 1 (new) | None | 3k | Todo |
| P2.1 | Audit `apps_eval` vs canonical | 0 (analysis) | None | 1k | Todo |
| P2.2 | Audit `apps_exec` | 0 | None | 1k | Todo |
| P2.3 | Audit `apps_lic` | 0 | 5 idiosyncratic folders | 2k | Todo |
| P2.4 | Audit `apps_qna` | 0 | 3 idiosyncratic folders | 1k | Todo |
| P2.5 | Audit `apps_research` | 0 | None | 1k | Todo |
| P2.6 | Audit `apps_rfp` | 0 | `_compat/` empty | 1k | Todo |
| P2.7 | Audit `apps_rg` | 0 | `scripts/` has 76 items; root `bootstrap_runtime.py` | 3k | Todo |
| P2.8 | Audit `apps_shared` | 0 | 6 idiosyncratic folders; highest blast radius | 3k | Todo |
| P2.9 | Audit `apps_underwriting_ai` | 0 | Missing doc set; `examples/` | 1k | Todo |
| P3.1 | Move root-level `_telemetry.py` (eval + research) → `services/telemetry.py` | 2 moves + ADG import rewrite | Cross-package import updates | 3k | Todo |
| P3.2 | Move `apps_exec/_optional_agentic_core.py` → `utils/optional_agentic_core.py` | 1 move | None | 2k | Todo |
| P3.3 | Delete `apps_rfp/_compat/` (empty) + move `apps_rg/bootstrap_runtime.py` → `services/runtime/bootstrap.py` | 1 delete + 1 move | bootstrap is a chokepoint | 3k | Todo |
| P4.1 | Author missing docs for `apps_lic` (README, TECHNICAL_SPEC, TEST_STRATEGY) | 3 new | None | 4k | Todo |
| P4.2 | Author missing docs for `apps_rg` (README, RUNBOOK, SLO, SVP, TECHNICAL_SPEC, TEST_STRATEGY) | 6 new | Largest doc gap | 5k | Todo |
| P4.3 | Author missing docs for `apps_shared` (README, TECHNICAL_SPEC, TEST_STRATEGY) | 3 new | None | 3k | Todo |
| P4.4 | Author missing docs for `apps_underwriting_ai` (TECHNICAL_SPEC, TEST_STRATEGY) | 2 new | None | 2k | Todo |
| P5.1 | `apps_qna/builder/` → `apps_qna/engines/builder/` | 2 files + ADG rewrite | builder has fan-in from tests | 3k | Todo |
| P5.2 | `apps_qna/router/` → `apps_qna/engines/router/` | 7 files + ADG rewrite | paste_bandit + pack_loader are hot | 4k | Todo |
| P5.3 | `apps_qna/templates/` → `apps_qna/data/templates/` | 24 files | File-reference paths in code | 3k | Todo |
| P6.1 | `apps_lic/L1_cognition/` → `apps_lic/reasoning/` (merge) | 2 files | reasoning/ already exists (22 items) — merge carefully | 4k | Todo |
| P6.2 | `apps_lic/outreach_engine/` → `apps_lic/engines/outreach/` | 1 file | None | 2k | Todo |
| P6.3 | `apps_lic/persistence/` → `apps_lic/services/persistence/` | 3 files | services/ currently 1-item | 3k | Todo |
| P6.4 | `apps_lic/policy/` split: code → `validators/policy/`, data → `config/policy/` | 11 files | Split discipline needed | 5k | Todo |
| P6.5 | `apps_lic/observability/` → `apps_lic/services/observability/` | 3 files | None | 4k | Todo |
| P7.1 | `apps_underwriting_ai/ingestion/` → `engines/ingestion/` | 8 files | None | 3k | Todo |
| P7.2 | `apps_underwriting_ai/parsers/` → `engines/parsers/` | 7 files | None | 3k | Todo |
| P7.3 | `apps_underwriting_ai/examples/` → `docs/examples/apps_underwriting_ai/` (or delete) | 2 files | Decide delete vs. move | 2k | Todo |
| P8.1 | `apps_rg/enforcement/` file-by-file audit | 1 file | Single-file dir | 3k | Todo |
| P8.2 | `apps_rg/runtime/` → `apps_rg/services/runtime/` | 4 files | None | 4k | Todo |
| P8.3 | `apps_rg/schemas/` → `apps_rg/config/schemas/` | 1 file | None | 2k | Todo |
| P8.4 | `apps_rg/scripts/` budget audit (76 → ≤5; rest to `ops_scripts/apps_rg/`) | 76 files | Largest single migration; requires per-script triage | 13k | Todo |
| P9.1 | `apps_shared/adapters/` + `data_adapters/` → `apps_shared/integrations/adapters/` | 6 files | All apps consume | 5k | Todo |
| P9.2 | `apps_shared/mixins/` → `apps_shared/utils/mixins/` | 1 file | None | 2k | Todo |
| P9.3 | `apps_shared/orchestration/` → `apps_shared/reasoning/orchestration/` | 2 files | reasoning/ already 15 items | 3k | Todo |
| P9.4 | `apps_shared/prompts/` → `apps_shared/data/prompts/` | 1 file | None | 2k | Todo |
| P9.5 | `apps_shared/proof/` → `apps_shared/validators/proof/` | 24 files | Validator path already used | 8k | Todo |
| P9.6 | `apps_shared/enforcement/` → `apps_shared/validators/enforcement/` | 18 files | Highest fan-in; SAFETY_GATEKEEPER | 8k | Todo |
| P10.1 | Author `ops_scripts/ci/check_apps_folder_taxonomy.py` + pre-commit hook `T7r` | 1 new | Extends constitutional §31 helper pattern | 6k | Todo |
| P10.2 | Author `.windsurf/rules/apps-folder-taxonomy.md` (always_on) + constitutional §32 | 2 new | Loaded-at-start enforcement | 4k | Todo |

---

## 8. Migration Mechanics (per-phase template)

Every move-phase follows this fixed sequence:

1. **Blast-radius query** — ADG MCP `adg_edge_fanin(relation_type="imports")` on every module in the source folder; capture import paths to rewrite.
2. **Pre-move MV snapshot** — save `mv_hotspot_centrality` row for the target module.
3. **Move** — `git mv` (preserves history) to target path; create target parent `__init__.py` if missing.
4. **Import rewrite** — `sed`/AST-safe rewrite of importers flagged in step 1. Prefer `libcst`-based rewrite for any import touching >10 callers.
5. **Compatibility shim** — at OLD path, emit `__init__.py` that re-exports from NEW path with `DeprecationWarning`. **Sunset window: 2 weeks**.
6. **Run targeted tests** — pytest_mcp scoped to `tests/` under the affected app + any cross-app tests flagged by ADG fanin.
7. **Regenerate ADG** — `python tools/generate_full_adg.py` so downstream waves see new topology.
8. **Commit** — single commit per phase, message format `refactor(apps-taxonomy): <phase-id> <short>`.
9. **Notion writeback** — `API-patch-page` on this plan row + `API-post-page` per wave completion in Wave/Phase Convergence.

---

## 9. Import-Rewrite Strategy

| Pattern | Rewrite tool | Validation |
|---|---|---|
| Simple `from apps_X.OLD import foo` → `from apps_X.NEW import foo` | `libcst` codemod | ADG regen + pytest |
| Dynamic `importlib.import_module("apps_X.OLD")` | manual + grep audit | `resolves_callsite` ADG edges |
| String-based `"apps_X.OLD"` in config/YAML | search + replace in `config/` files | YAML validation |
| Typing references `"apps_X.OLD.Foo"` (forward refs) | `libcst` | mypy/pyright |

**Rollback**: every phase is a single commit. If ADG regen detects new P0 violations post-move, `git revert <phase-commit>` and re-plan.

---

## 10. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|:---:|:---:|---|
| Import-graph churn breaks cross-app tests | High | High | Compat shim (step 5); single-commit-per-phase rollback |
| `apps_shared/enforcement/` move (P9.6) cascades to every app | High | High | Dedicate full wave; 2-week shim window; paired code review |
| `apps_rg/scripts/` triage (P8.4) uncovers orphaned scripts | Medium | Medium | Emit `NEXT_STEP:` markers per orphan; do not block wave on deletion decisions |
| Re-exports in compat shim miss dynamic imports | Medium | High | Grep audit in step 4; explicit `resolves_callsite` ADG query |
| Doc-authoring waves (W4) stall on content gaps | Medium | Low | Use existing apps as templates; accept TBD placeholders |
| Guardian exemptions reference old paths | Low | Medium | `mv_exemptions_near_critical_paths` query in W2 audit |

---

## 11. Out of Scope (explicitly deferred)

- Renaming the `apps_*` prefix itself (e.g., `apps_rg` → `app_resume_generator`) — separate ADR if ever pursued.
- Consolidating `agentic_core/` layers — that is the `L0..L6` taxonomy, unaffected here.
- Moving app entrypoints out of `apps_*` roots — `__main__.py` stays at root (constitutional convention).
- Renaming CamelCase legacy files (`Hardened*Strategy.py`) — grandfathered with __init__ re-export.

---

## 12. Success Criteria (overall plan)

- ✅ ADR-081 merged; canonical spec in `docs/architecture/`
- ✅ All 9 apps conform to §3.1 + §3.2 + §3.4 + §3.5
- ✅ No root-level `_*.py` files in any `apps_*` folder
- ✅ `apps_rg/scripts/` ≤5 files; remainder in `ops_scripts/apps_rg/`
- ✅ CI gate `check_apps_folder_taxonomy.py` green
- ✅ `.windsurf/rules/apps-folder-taxonomy.md` loaded always-on
- ✅ Full pytest suite green (pytest_mcp scoped to `tests/`)
- ✅ ADG regen produces zero NEW P0 violations
- ✅ All compat shims removed after 2-week window

---

## 13. Next Action

After user approval of this plan:
1. Dispatch W1 (ADR + canonical spec) — small, independent wave.
2. W2 audits run in parallel (one phase per app).
3. Low-risk W3 before any high-radius wave.
4. W9 (apps_shared) gates on W3–W8 completion due to blast radius.
