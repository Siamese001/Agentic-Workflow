# Wave G — Runtime Scope Map

The runtime-topology map produced by Waves G1–G7 MUST cover every dimension below. Each dimension has a mandatory scope (must be in a G artefact) and explicit exclusions (must *not* drift into the G artefacts).

## Dimensions in scope

### 1. Agentic runtime (L0–L6 + C0-related logic)

**In scope**
- `agentic_core/L0_routing/` through `agentic_core/L6_observability/` — every Python module, its entry point type (agent, orchestrator, gate, evaluator, etc.), and its direct imports.
- Cross-cutting subsystems that host multi-layer runtime: `agentic_core/runtime/`, `agentic_core/agents/`, `agentic_core/base_agents/`, `agentic_core/seams/`, `agentic_core/interfaces/`, `agentic_core/mixins/`, `agentic_core/evaluation/`, `agentic_core/prompt_governance/`, `agentic_core/knowledge/`, `agentic_core/adg/`.
- C0-related logic: F04 context-assembly implementation in `agentic_core/L1_cognition/reasoning/context_assembler.py` and callers (cited via SRC-ADR-007). Records the L1-homed status per OOS-003 SUPERSEDED.
- Runtime embodiment of F07 healing / F08 exit / F09 UWG / F10 L4 / F11 L5 / F12 L6.

**Out of scope**
- Re-asserting the L0–L6 authority claims — those live in v1.3 atoms F02.01, F03.01, F05.01, F06.01, F07.x, F08.x, F09.x, F10.x, F11.x, F12.x.
- Archival code under `archives/` (import-forbidden per constitutional §12).

### 2. apps_* runtime and adapter inventory

**In scope (7 surfaces)**: `apps_eval/`, `apps_exec/`, `apps_lic/`, `apps_research/`, `apps_rfp/`, `apps_rg/`, `apps_shared/`, `apps_underwriting_ai/`.

For each:
- Entry points (`__main__.py`, `bootstrap_runtime.py`-style shims, CLI scripts under `scripts/`)
- Core sub-surfaces: `engines/`, `reasoning/`, `integrations/`, `services/`, `spine/`, `config/`, `outputs/`, `validators/`, `types/`, `tools/`
- How each app binds into `agentic_core` (direct imports, seams, shared mixins, adapter boundaries)
- App-specific prompts, configs, data, and outputs paths

**Out of scope**
- App-internal business logic that does not touch runtime wiring.
- Per-app unit test content (covered only at test-surface inventory depth in G5).

### 3. Service-to-service wiring and connectivity

**In scope**
- Import-graph edges across L0–L6 and across app/core boundaries (via ADG MCP).
- Seam/interface modules (`agentic_core/seams/`, `agentic_core/interfaces/`, `agentic_core/L_CONTRACTS/`).
- Method-level call-chain for the canonical request lifecycle (admit → plan → route → orchestrate → execute → heal → exit → write).
- Shared transports: subprocess, HTTP (local MCP loopback), Redis client, SQLite connections.

**Out of scope**
- External SaaS wiring that lives only as config (captured in §4 instead).

### 4. Provider / gateway / egress / auth boundaries

**In scope**
- `agentic_core/gateway/`, `infrastructure/sdks_mcps/` — all external provider SDK wrappers (OpenAI/Anthropic/etc.), gateway client code, egress points.
- Auth surfaces: env-var consumption (`.env`, `os.environ`), key-loading patterns, token rotation hooks.
- Rate-limiting, retry, circuit-breaker semantics at the egress edge.
- MCP servers as egress *and* ingress (loopback) surfaces.

**Out of scope**
- Secrets contents. Inventory cites key NAMES and consumer modules only.

### 5. Pipelines and state transitions

**In scope**
- Named pipelines: ADG generation (`tools/generate_full_adg.py`, `tools/adg/`), evaluation pipeline (`agentic_core/evaluation/`, `apps_eval/spine/`), replay pipeline (F08 exit spine → F09 UWG → F10 L4), memory lifecycle pipeline (F12 L6 → L4 → future-run F02 L1).
- State machines: orchestrator state (`agentic_core/L3_orchestration/core/orchestrator_state_retry.py` and peers), healing state (SRC-ADR-002 RetryConfig), exit-control gate states (SRC-ADR-003).
- Pipeline triggers: CLI, test harness, hooks, CI, operator.

**Out of scope**
- Per-step prompt content (covered as control-plane artefact in §8).

### 6. Replay / exit / evaluation / recovery traceability

**In scope**
- ExecutionTrace / mutation_hash paths (SRC-ADR-005).
- ExitControlGate.evaluate_sealed() and evaluate_and_emit() (SRC-ADR-003).
- GovernedHandoffAgent as sole durable-write seam.
- Heal/retry path binding: `agentic_core/L2_execution/` healer modules + SRC-ADR-002 retry config.
- Eval pipeline acceptance data flow (`apps_eval/`, `agentic_core/evaluation/`, `docs/architecture/eval_pipeline_acceptance.md`).

**Out of scope**
- Eval metric formulas — G references them, doesn't re-derive them.

### 7. Storage and infrastructure topology

**In scope**
- SQLite artefacts: `artifacts/adg/adg_indexed_*.sqlite` (canonical), plus any scoped SQLite stores referenced from `agentic_core/adg/` or per-app services.
- Redis namespaces: ADG hot cache, coordination fabric, (prefixes per `redis_namespace_stats`).
- Vector stores: `tools/mcp/vector_db_server.py` + `tools/retrieval/` adapters.
- Disk artefacts: `artifacts/`, `data/`, `logs/`, `test_artifacts/`, `system_learning/` outputs.
- Infrastructure layer: `infrastructure/` (SDK wrappers, reasoning scaffolds, utils).

**Out of scope**
- Cloud provisioning IaC (none exists in-repo at G0; if that changes, G4 re-scopes).

### 8. Config / prompts / rules / env / feature-flag control plane

**In scope**
- `config/` (token_budget, excluded_paths, schemas, structure_blueprint).
- `agentic_core/config/` and `agentic_core/runtime/config/` — runtime knob surfaces.
- Per-app `config/` directories.
- `.env` key inventory (names, consumers, defaults if declared).
- `.codex/rules/`, `AGENTS.md`, `.codex/skills/`, `docs/archive/windsurf/legacy-tree/workflows/` — governance/control surfaces read at agent startup.
- Prompt surfaces: `agentic_core/prompt_governance/`, `apps_shared/prompts/`, per-app prompt directories.
- Feature flags / runtime toggles wherever they live.

**Out of scope**
- Secret values.

### 9. Deployment / MCP / hooks / ops-scripts / CI topology

**In scope**
- MCP server inventory: `tools/mcp/` (enhanced_http, pytest, redis, vector_db), `tools/adg/mcp/` (adg_sqlite), plus all entries in `.mcp.json` (stable server IDs mapped to live transports).
- `.codex/hooks.json` — pre/post MCP gates, command gates, memory-first gate.
- `ops_scripts/` — CI gates (`ops_scripts/ci/`), dev tools, governance, maintenance, verification.
- `.github/` — CI workflows, actions, issue templates.
- Startup/shutdown paths: MCP server launch, Redis/vector-DB lifecycle, process boundaries.
- Operator workflows: `docs/archive/windsurf/legacy-tree/workflows/*.md`.

**Out of scope**
- External CI provider internals (GitHub Actions engine itself).

### 10. Unknown-taxonomy / special-surface normalization

**In scope**
- Directories that don't fit cleanly into L0–L6 / apps / tools / ops / config: e.g., `agentic_core/cloud_native/`, `agentic_core/case_memory/`, `agentic_core/embeddings/`, `agentic_core/visualization/`, `agentic_core/utils/`, `agentic_core/_compat/`, top-level `__pycache__` / `.windsurf/state/` / `.hypothesis/`, `templates/`, `.backup/`.
- Duplicated responsibilities across `agentic_core/` vs `infrastructure/` vs `tools/` (e.g., Redis clients, MCP subprocess helpers, retrieval adapters).
- `system_learning/` and its relationship to F12 / SRC-INT-004 memory lifecycle.

**Out of scope**
- Deleting or consolidating surfaces. G only inventories and classifies; consolidation is a later wave if warranted.

### 11. End-to-end operational flow

**In scope**
- The single walkable path from operator trigger → request admit → plan → route → orchestrate → execute → heal → evaluate → exit → UWG write → L4 persist → L6 observe → memory write-back.
- Overlay of wires identified in §3, pipelines in §5, stores in §7, configs in §8, deployment in §9.

**Out of scope**
- Marketing narrative.

## Explicit exclusions from Wave G

- No new Wave E/F artefacts, no edits to v1.3 canonical, no new atoms/edges/sources.
- No cloud IaC authoring.
- No prompt rewrites.
- No refactors — G is a map, not a change request.
- No B7 closure — G records B7 candidates only.

## B7 handling rule

If any G sub-wave surfaces a runtime fact that implies an interaction not currently represented in v1.3 (e.g., a cross-layer call never first-classed as an edge), G records the fact with a pointer: `B7_candidate: <short description>, surfaces: [paths], observed_in: <G-sub-wave-id>`. G never upgrades the v1.3 graph. The parked B7 wave is the only lane that can do that.
