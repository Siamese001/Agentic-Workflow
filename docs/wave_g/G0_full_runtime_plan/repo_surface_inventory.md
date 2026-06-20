# Wave G — Repo Surface Inventory

Concrete, repo-grounded list of every surface Wave G is accountable for. Each surface is tagged with:

- **Layer**: L0–L6, cross-cutting, app, infra, ops, config, docs, tests, control-plane, artefact
- **Primary G sub-wave**: which sub-wave owns the inventory pass for it
- **Notes**: anything special (seam, adapter, boundary, unknown)

Paths are repo-relative. `n=` prefix on a child count indicates counts observed at G0 scoping time and may drift by G execution; actual counts MUST be re-tallied at each sub-wave's start.

## 1. Agentic core (L0–L6 + cross-cutting)

### L0–L6 layer directories

| Path | Layer | Primary G wave | Notes |
|---|---|---|---|
| `agentic_core/L0_routing/` | L0 | G1 | Route authority; F03 embodiment |
| `agentic_core/L1_cognition/` | L1 | G1 | Plan authority; F02 embodiment; hosts `reasoning/context_assembler.py` (F04) |
| `agentic_core/L2_execution/` | L2 | G1 | Task execution; F06 + F07 healing embodiment |
| `agentic_core/L3_orchestration/` | L3 | G1 | Orchestration (F05); includes `core/orchestrator_state_retry.py` |
| `agentic_core/L4_state/` | L4 | G1, G4 | Durable state authority (F10); has `cache/`, `memory/`, `enforcement/` |
| `agentic_core/L5_safety/` | L5 | G1 | Policy/safety authority (F11); has `audit/`, `enforcement/`, `validators/` |
| `agentic_core/L6_observability/` | L6 | G1 | Observability (F12); has `execution/`, `enforcement/` |

### Cross-cutting subsystems inside `agentic_core/`

| Path | Classification | Primary G wave | Notes |
|---|---|---|---|
| `agentic_core/runtime/` | Cross-cutting runtime core | G1 | `config/`, `contracts/`, `engine/`, `exceptions/`, `types/`, `utils/` — the runtime scaffolding |
| `agentic_core/agents/` | Agent registry | G1 | Concrete agents |
| `agentic_core/base_agents/` | Agent base classes | G1 | Inheritance roots |
| `agentic_core/seams/` | Seam authority | G1, G2 | Cross-layer contracts |
| `agentic_core/interfaces/` | Interface surfaces | G1, G2 | Typed interfaces |
| `agentic_core/mixins/` | Shared mixins | G1 | Composition helpers |
| `agentic_core/L_CONTRACTS/` | Layer contracts | G1, G2 | Formal layer contracts |
| `agentic_core/evaluation/` | Eval subsystem | G1, G3b | Eval pipeline pieces |
| `agentic_core/prompt_governance/` | Prompt control | G1, G4b | Prompt authority & governance |
| `agentic_core/knowledge/` | Knowledge surface | G1, G4 | Knowledge bases and retrieval |
| `agentic_core/adg/` | ADG runtime | G1, G2, G5 | Runtime side of AST Dependency Graph |
| `agentic_core/cache/` | Cache | G4 | In-process cache |
| `agentic_core/case_memory/` | Case memory | G4, G6 | Special surface |
| `agentic_core/embeddings/` | Embeddings | G4, G2b | Vector support |
| `agentic_core/gateway/` | Gateway | G2b | External-facing surface |
| `agentic_core/tracing/` | Tracing | G3b, G5 | Runtime tracing |
| `agentic_core/cloud_native/` | Special | G6 | Unknown taxonomy — needs classification |
| `agentic_core/core/` | Special | G6 | Thin; classify |
| `agentic_core/visualization/` | Special | G6 | Thin; classify |
| `agentic_core/config/` | Config | G4b | Runtime knobs |
| `agentic_core/_compat/` | Compat shim | G6 | Shim discipline surface |
| `agentic_core/utils/` | Utils | G6 | Grab-bag; must be classified |

## 2. apps_* surfaces

All 8 apps follow a similar shape; G1b inventories each and records deviations.

| Path | Entry points | G wave | Notes |
|---|---|---|---|
| `apps_eval/` | `scripts/`, `spine/`, `services/` | G1b, G3b | Has `spine/` (eval spine) |
| `apps_exec/` | `scripts/`, `spine/` | G1b | Has `_optional_agentic_core.py` (adapter) |
| `apps_lic/` | `scripts/`, `services/` | G1b | No top-level docs |
| `apps_research/` | `scripts/`, `spine/` | G1b | Has `spine/` |
| `apps_rfp/` | `scripts/`, `spine/` | G1b | Has `spine/` + `_compat/` |
| `apps_rg/` | `__main__.py`, `bootstrap_runtime.py`, `scripts/` | G1b | Has explicit `bootstrap_runtime.py` — model for others |
| `apps_shared/` | `services/`, `spine/`, `data_adapters/` | G1b | Shared primitives; not an app proper |
| `apps_underwriting_ai/` | `scripts/`, `parsers/`, `ingestion/` | G1b | Ingestion-heavy |

Each app's `config/`, `engines/`, `reasoning/`, `integrations/`, `services/`, `outputs/`, `validators/`, `types/`, `tools/` sub-surfaces are inventoried by G1b.

## 3. Tools, MCP, and infrastructure

| Path | Classification | G wave | Notes |
|---|---|---|---|
| `tools/mcp/` | MCP servers | G5 | `enhanced_http_server.py`, `pytest_server.py`, `redis_mcp_server.py`, `vector_db_server.py`, `mcp_bootstrap.py`, `mcp_deferred_loader.py`, `mcp_subprocess.py`, subdirs `http_mcp/`, `pytest_support/`, `redis_mcp/` |
| `tools/adg/` | ADG tooling | G1, G5 | Canonical ADG generator + MCP server |
| `tools/retrieval/` | Retrieval service | G2b, G4 | Vector-DB facade |
| `tools/memory/` | Memory tools | G4b | Memory graph tooling |
| `tools/otel/` | OpenTelemetry | G3b, G5 | Observability export |
| `tools/guardian/` | Guardian | G4b, G5 | Exemption gate tooling |
| `tools/heal_classifier/` | Healing heuristics | G3b | Healer classification |
| `tools/graphdb/` | Graph DB | G4 | Storage surface |
| `tools/generate/` | Codegen helpers | G5 | Build-time tools |
| `tools/diag/` | Diagnostics | G5 | Operator tools |
| `tools/eval/` | Eval helpers | G3b | Shared eval helpers |
| `tools/validate/` | Validators | G5 | Validation helpers |
| `tools/debug/` | Debug helpers | G6 | Special |
| `tools/progress_display.py` | Shared UI | G4b | Mandated per constitutional §16 |
| `tools/generate_full_adg.py` | ADG pipeline entry | G1, G3, G5 | Canonical regeneration entry |
| `infrastructure/` | Infra layer | G2b, G4 | `sdks_mcps/` (SDK wrappers), `reasoning/`, `utils/`, `types/`, `config/` |
| `infrastructure/sdks_mcps/` | External SDK wrappers | G2b | `client_wrappers.py`, `mcp_catalog/` |

## 4. Ops, CI, governance

| Path | Classification | G wave | Notes |
|---|---|---|---|
| `ops_scripts/ci/` | CI gates | G5 | Contract gates, guardian, progress-bar, terminal cleanup, etc. |
| `ops_scripts/dev_tools/` | Dev ergonomics | G5 | Many; inventoried as a group |
| `ops_scripts/governance/` | Governance scripts | G5 | HITL, SVP reviews |
| `ops_scripts/maintenance/` | Maintenance | G5 | ADG refresh, cleanup |
| `ops_scripts/root_scripts/` | Entry points | G5 | Top-level operator entries |
| `ops_scripts/verification/` | Verification | G5 | Post-change checks |
| `ops_scripts/enforcement/`, `environment/`, `review/`, `security/`, `setup/`, `tools/` | Sparse sub-areas | G5 | Small |
| `.github/` | GitHub Actions | G5 | Workflows, actions, issue/PR templates |
| `.codex/rules/` | Rule SSOT | G4b, G5 | Constitutional + global + conditional |
| `.codex/hooks.json` | Hook registry | G5 | Memory-first gate, pre/post MCP, pre-run |
| `.mcp.json` | MCP registry | G5 | Stable server IDs + transports + env |
| `.codex/skills/` | Skills | G4b | Auto-invoked doctrine |
| `docs/archive/windsurf/legacy-tree/workflows/` | Workflows | G5 | Slash-commands |
| `.codex/governance/scripts/` | legacy editor helpers | G5 | Post-write sync scripts, etc. |
| `.codex/plans/` | Plans SSOT | G0 reuses, not owned | Not re-inventoried by G |

## 5. Config / prompts / control plane

| Path | Classification | G wave | Notes |
|---|---|---|---|
| `config/` | Global config | G4b | `token_budget.yaml`, `excluded_paths.yaml`, `schemas/`, `structure_blueprint/` |
| `agentic_core/config/` | Core config | G4b | Runtime knobs |
| `agentic_core/runtime/config/` | Runtime config | G4b | Engine-level config |
| `apps_*/config/` | App config | G1b, G4b | Per app |
| `agentic_core/prompt_governance/` | Prompt authority | G4b | Governance over prompts |
| `apps_shared/prompts/` | Shared prompts | G4b | Shared templates |
| `.env` (root) | Env keys | G2b, G4b | NAMES only, never values |
| `AGENTS.md` | Top-level agent guidance | G4b | Always-on instruction |

## 6. Storage / artefact surfaces

| Path | Classification | G wave | Notes |
|---|---|---|---|
| `artifacts/` | Canonical artefact store | G4 | ADG SQLite, reports |
| `artifacts/adg/adg_indexed_*.sqlite` | Canonical ADG | G1, G4 | Primary dependency-graph source |
| `data/` | Data fixtures / seed | G4 | Inventoried by use |
| `logs/` | Runtime logs | G4 | Volatile |
| `test_artifacts/` | Test outputs | G4, G5 | Transient |
| `system_learning/` | Learning / memory | G4, G4b | Links to SRC-INT-004 memory lifecycle (F12.05/.07/.08) |
| `.backup/` | Backups | G6 | Special |
| `templates/` | Templates | G6 | Currently empty at G0 |

## 7. Docs / specs / contracts (reference-only for G)

| Path | G wave | Role |
|---|---|---|
| `docs/wave_e/99_integration_v13/` | reuse | v1.3 canonical — primary authority for cross-referencing |
| `docs/wave_e/F4_edge_exclusion_cleanup/` | reuse | F4 cleanup outputs |
| `docs/architecture/` | reuse | ADRs (including SRC-ADR-001..009) |
| `docs/specs/hardening/` | reuse | Named specs (HEALER_RETRY, L0_DECOMPOSITION, REPLAY_DETERMINISM, AUTHORITY_HIERARCHY) |
| `docs/contracts/` | reuse | Formal contracts (Guardian→L6) |
| `docs/reference/` | reuse | Narrow reference material |
| `docs/runbooks/`, `docs/operations/`, `docs/monitoring/` | reuse | Operator docs |
| `docs/reports/` | reuse | Prior wave outputs; never authoritative for G |
| `docs/wave_g/G0_full_runtime_plan/` | authored | THIS wave's outputs |

## 8. Tests

| Path | G wave | Role |
|---|---|---|
| `tests/` | G5 inventory only | Test surfaces as operator-invocable verification; not executed by G planning |
| `conftest.py`, `pytest.ini`, `pyproject.toml` pytest sections | G5 | Test config |

## 9. Tooling config / build

| Path | G wave | Role |
|---|---|---|
| `pyproject.toml` | G5 | Package, build, lint config |
| `.pre-commit-config.yaml` | G5 | Commit-time gates |
| `.gitignore`, `.gitattributes`, `.codeiumignore` | G5 | Boundaries |
| `.pylintrc`, `pyrightconfig.json` | G5 | Type / lint |

---

Anything not enumerated above and discovered during sub-wave execution MUST be added to this inventory via a G6 patch (unknown-taxonomy cleanup) and classified before the sub-wave that found it can complete.
