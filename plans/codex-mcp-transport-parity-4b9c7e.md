---
plan_id: codex-mcp-transport-parity-4b9c7e
plan_format: v2
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# Codex MCP Transport Parity with Claude SSOT

Make Codex mirror the Claude Code MCP setup exactly: root `.mcp.json` remains the live server SSOT, `.claude/mcp-notes.md` remains the dormant/re-add block SSOT, and Codex exposes each access pattern through either the same MCP, an explicitly named plugin substitute, or a documented degraded fallback.

> **plan_id discipline**: `plan_id` matches the filename stem `codex-mcp-transport-parity-4b9c7e`. Wave markers use `plan=codex-mcp-transport-parity-4b9c7e`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: IN_PROGRESS
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-06-10

> **COMPLETION REQUEST BLOCKED (2026-06-10).** User requested marking the plan
> completed and performing testing. Testing was performed, but the plan was not
> marked complete because the live closeout gate failed:
> `mcp__adg_sqlite__adg_health` returned `Transport closed`. Local gates passed:
> Codex backup verifier, plan format compliance, and focused pytest
> (`14 passed, 5 warnings`). The W4 audit helper also runs, but now reports
> duplicate live process families for `adg_sqlite`, `memory`, `vector_db`,
> `notion`, `context7`, and `playwright`. Completion requires MCP host cleanup /
> restart, reopened `adg_sqlite` transport, and a passing live ADG health check.
> Evidence:
> `docs/reports/codex/codex_mcp_completion_attempt_20260610.md` and
> `docs/reports/codex/codex_mcp_completion_attempt_20260610.json`.

> **W3 COMPLETE OUT-OF-ORDER (2026-06-10).** Executed by explicit user request
> while W2.3 remains blocked. Created the dormant server policy artifacts:
> `docs/reports/codex/codex_mcp_dormant_policy.md` and
> `docs/reports/codex/codex_mcp_dormant_policy.json`. Redis, Tavily,
> `pytest_mcp`, and `otel_mcp` now have explicit dormant/re-add, substitute,
> prerequisite, and "not live unless re-added" policies. W2.3 still blocks
> advancing the main wave cursor because live Codex ADG MCP is serving the
> primary checkout without the eval-harness Redis decode fix.

> **W4 COMPLETE OUT-OF-ORDER (2026-06-10).** Executed by explicit user request
> while W2.3 remains blocked. Added the read-only Codex MCP transport audit
> helper `scripts/governance/audit_codex_mcp_transports.py` and created the
> W4 artifacts: `docs/reports/codex/codex_mcp_transport_lifecycle_audit.md`
> and `docs/reports/codex/codex_mcp_transport_lifecycle_audit.json`. The audit
> captures ADG runtime PID/nonce baseline, command/script/TCP/env readiness,
> placeholder policy, and duplicate-process classification. Open W4 finding:
> `adg_sqlite` has two Python stdio server processes; live runtime PID is
> `12236`, so cleanup should use the owning MCP host restart path and verify
> PID/nonce change.

> **W5 COMPLETE OUT-OF-ORDER (2026-06-10).** Executed by explicit user request
> while W2.3 remains blocked. Updated Codex adapter docs/skills as thin pointers
> to `.mcp.json`, `.claude/mcp-notes.md`, and `mcp-integration` without copying
> Claude rule bodies. Created W5 closeout artifacts:
> `docs/reports/codex/codex_mcp_w5_verification.md` and
> `docs/reports/codex/codex_mcp_w5_verification.json`. Notion Plans row exists
> with `Status=In Progress`, `Exists On Disk=true`, and
> `Plan File Path=plans/codex-mcp-transport-parity-4b9c7e.md`. The original
> creation-time `Not Started` expectation is superseded by actual wave execution;
> do not mark the plan complete while W2.3 remains blocked.

> **W2 BLOCKED (2026-06-10).** Created the live route contract artifacts:
> `docs/reports/codex/codex_mcp_live_route_contract.md` and
> `docs/reports/codex/codex_mcp_live_route_contract.json`. W2.1 and W2.2 are complete:
> Memory, Vector DB, GitKraken, DeepWiki, Notion, Context7, and Playwright all have
> explicit Codex route contracts. W2.3 is blocked by `ADG-LIVE-CODE-MISMATCH`: live
> Codex ADG MCP serves `C:\Git\Agentic-Workflow-FRESH` code, while the Redis decode
> / Redis-3 compatibility fix exists in `C:\Git\eval-harness`. Evidence:
> `adg_health` is full/healthy, but `adg_node("1")` with `backend_used=redis`
> returns fields like `id="__json__:\"1\""`. Unblock by merging/applying the ADG
> Redis fixes into the primary checkout or relaunching Codex with
> `AGENTIC_REPO_ROOT=C:\Git\eval-harness`, then restart MCP and re-warm affected keys.

> **W1 COMPLETE (2026-06-10).** Created the Codex MCP capability matrix artifacts:
> `docs/reports/codex/codex_mcp_capability_matrix.md` and
> `docs/reports/codex/codex_mcp_capability_matrix.json`. The matrix covers every
> live `.mcp.json` server plus dormant/re-add blocks from `.claude/mcp-notes.md`.
> Fresh Codex discovery confirmed Memory, Vector DB, GitKraken, and DeepWiki remain
> unavailable as Codex-callable MCP tools; `adg_sqlite` is green; Notion, Playwright,
> and Tavily have plugin/substitute surfaces; Redis and Tavily are intentionally
> dormant in `.mcp.json` and stored as re-add blocks in `.claude/mcp-notes.md`.

---

## Context (SCQA)

- **Situation** - The ADG SQLite MCP is now open in Codex with `mode=full`, `sqlite=healthy`, and `redis=healthy`. The root `.mcp.json` lists Claude Code live servers: `GitKraken`, `adg_sqlite`, `deepwiki`, `memory`, `vector_db`, `notion`, `context7`, and `playwright`. `CLAUDE.md` and `.claude/mcp-notes.md` explicitly say `pytest_mcp`, `redis`, `otel_mcp`, and `tavily` are not in `.mcp.json`; they use native substitutes unless re-added from `.claude/mcp-notes.md`.
- **Complication** - Codex currently exposes only a subset of those stable MCP IDs. `memory`, `vector_db`, `GitKraken`, `deepwiki`, raw `context7`, raw `playwright`, and standalone `redis` are not directly callable through Codex tool discovery. Codex has plugin substitutes for some surfaces, but they do not preserve the Claude tool names, health gates, or access patterns. Process inspection also shows duplicate MCP subprocesses for several Node/Python servers.
- **Question** - How do we make Codex replicate the Claude MCP setup exactly while preserving the repo's access ladder, dormant-server policy, health gates, and fallback semantics?
- **Answer** - Build a Codex MCP parity layer that reads Claude SSOT configuration, records a capability matrix, restores or maps each server's exact access pattern, and adds transport health/process hygiene checks so Codex can prove parity without creating a second registry.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2, W1.3 | Claude SSOT inventory and Codex capability matrix | ~6K | `.mcp.json`, `CLAUDE.md`, `.claude/mcp-notes.md`, and `mcp-integration` remain authoritative | DONE | Machine-readable matrix lists every live, dormant, plugin, and fallback access pattern with evidence |
| W2 | W2.1, W2.2, W2.3 | Live server parity for configured `.mcp.json` servers | ~10K | Codex can expose deferred MCP tools or route to local validated fallbacks | BLOCKED | W2.1/W2.2 route contracts complete; W2.3 blocked by live ADG primary-checkout Redis decode mismatch |
| W3 | W3.1, W3.2, W3.3 | Dormant Redis/Tavily/pytest/OTel policy replication | ~8K | Dormant means not re-added unless explicitly selected; substitutes still must be exact | DONE | Redis and Tavily answer "where stored now" and implement exact current substitute/re-add paths |
| W4 | W4.1, W4.2, W4.3 | Transport lifecycle and duplicate-process hygiene | ~8K | Existing MCP bootstrap guards can be reused or extended | DONE | Health probes detect closed transports, duplicate MCP processes, stale env placeholders, and recoverable restart paths |
| W5 | W5.1, W5.2, W5.3 | Documentation, Notion registration, and verification gates | ~6K | Plan registration uses Plans DB; Codex adapter docs remain thin pointers to Claude SSOT | DONE | Docs, tests, and governance checks prove Codex is an adapter, not a second MCP SSOT |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Inventory Claude live MCP servers from root `.mcp.json` | DONE |
| W1.2 | Inventory dormant/re-add MCP blocks from `.claude/mcp-notes.md` | DONE |
| W1.3 | Generate Codex capability matrix and gap taxonomy | DONE |
| W2.1 | Restore or map Memory, Vector, GitKraken, and DeepWiki access | DONE |
| W2.2 | Normalize Notion, Context7, and Playwright Codex plugin/raw MCP routes | DONE |
| W2.3 | Prove ADG SQLite/Redis parity and protect the fixed Redis cache path | BLOCKED |
| W3.1 | Replicate Redis current storage, substitute, and re-add semantics | DONE |
| W3.2 | Replicate Tavily current storage, substitute, and re-add semantics | DONE |
| W3.3 | Capture pytest_mcp and otel_mcp dormant policy with exact fallbacks | DONE |
| W4.1 | Add transport health probes for Codex-visible and local MCP surfaces | DONE |
| W4.2 | Add duplicate-process detection and cleanup guidance | DONE |
| W4.3 | Add env placeholder and credential preflight checks | DONE |
| W5.1 | Update Codex backup adapter docs/skills as thin SSOT pointers | DONE |
| W5.2 | Register and sync the plan in Notion Plans DB | DONE |
| W5.3 | Run governance, MCP parity, and focused transport tests | DONE |

---

## Current Tavily And Redis Storage

**Tavily**
- **Current live `.mcp.json` status**: not present.
- **Current storage/SSOT**: `CLAUDE.md` "Not in `.mcp.json`" line and `.claude/mcp-notes.md` dropped-server block.
- **Current credential**: Windows OS env var `TAVILY_API_KEY`.
- **Current Claude substitute**: native WebSearch/WebFetch, while `mcp-integration` §8 remains dormant reference.
- **Current Codex substitute**: Codex Tavily plugin tools when exposed (`_tavily_search`, `_tavily_extract`, `_tavily_crawl`, `_tavily_research`), otherwise web tooling with explicit degraded note.
- **Exact re-add block**: `.claude/mcp-notes.md` contains `"tavily": {"command": "cmd", "args": ["/c", "npx", "-y", "tavily-mcp"], "env": {"TAVILY_API_KEY": "${TAVILY_API_KEY}"}}`.

**Redis**
- **Current live `.mcp.json` status**: no standalone `redis` server. `ADG_REDIS_URL` is still used by `adg_sqlite` and `memory`.
- **Current storage/SSOT**: `CLAUDE.md` "Not in `.mcp.json`" line, `.claude/mcp-notes.md` dropped-server block, `mcp-integration` §2, and the ADG Redis hot-cache code path.
- **Current credential/config**: Windows OS env var `ADG_REDIS_URL`; local Redis service at the configured URL.
- **Current Claude substitute**: `redis-cli` via Bash for standalone cache inspection; ADG access goes through `adg_sqlite` MCP first, then SQLite direct only with `DEGRADED_FALLBACK`.
- **Current Codex substitute**: ADG MCP `adg_health`/`adg_node`/`backend_used=redis` for ADG hot projection; local Python/Redis CLI fallback only with an explicit degraded note for standalone key inspection.
- **Exact re-add block**: `.claude/mcp-notes.md` contains `"redis": {"command": "python", "args": ["-u", "${AGENTIC_REPO_ROOT}/tools/mcp/redis_mcp_server.py"], "env": {"REDIS_DB": "0", "REDIS_HOST": "localhost", "REDIS_PORT": "6379", "REDIS_TIMEOUT": "5", "PYTHONPATH": "${AGENTIC_REPO_ROOT}", "PYTHONUNBUFFERED": "1"}}`.

---

## Out Of Scope

- Migrating plan SSOT back into `.claude/plans`.
- Rewriting Claude MCP skills or duplicating their rule bodies in Codex.
- Making Redis authoritative over SQLite ADG data.
- Re-adding dormant MCP servers to `.mcp.json` without an explicit decision.
- Replacing Codex plugins when they already provide a faithful substitute with documented deltas.

---

## Wave 1 - Claude SSOT Inventory And Codex Matrix

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED - Read-only audit and generated parity artifact.

**Phases**:
- **W1.1** - Inventory Claude live MCP servers from root `.mcp.json` | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** - Inventory dormant/re-add MCP blocks from `.claude/mcp-notes.md` | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.3** - Generate Codex capability matrix and gap taxonomy | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Matrix contains columns: `server_id`, `claude_status`, `claude_tool_names`, `codex_surface`, `fallback`, `env`, `health_probe`, `mutation_policy`, `gap_status`.
- Matrix distinguishes live `.mcp.json`, dormant/re-add, plugin substitute, local fallback, and unsupported.
- Tavily and Redis rows exactly match `CLAUDE.md` and `.claude/mcp-notes.md`.

---

## Wave 2 - Live `.mcp.json` Server Parity

WAVE_ID: W2
WAVE_STATUS: BLOCKED
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** - Restore or map Memory, Vector, GitKraken, and DeepWiki access | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** - Normalize Notion, Context7, and Playwright Codex plugin/raw MCP routes | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.3** - Prove ADG SQLite/Redis parity and protect the fixed Redis cache path | ~3K tokens | PHASE_STATUS: BLOCKED | PHASE_COMPLETE: NO

**Acceptance**:
- `memory`: `mem_recall_session_start`, entity creation, and writeback have either a callable Codex route or a documented blocked status that preempts false compliance.
- `vector_db`: semantic search/list/stats access has a callable Codex route or a local script fallback marked `DEGRADED_FALLBACK`.
- `GitKraken`: Codex route either exposes `gk mcp` tools or documents native `git` plus GitHub plugin fallback where it differs.
- `deepwiki`: external GitHub repo Q&A has a callable route or clearly blocked status.
- `notion`: Codex Notion plugin properties are mapped to Claude Plans DB access patterns.
- `context7`: raw MCP versus Codex substitute is explicit, including optional `CONTEXT7_API_KEY`.
- `playwright`: raw MCP versus `node_repl`/browser plugin substitute is explicit.

---

## Wave 3 - Dormant Server Policy Replication

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** - Replicate Redis current storage, substitute, and re-add semantics | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** - Replicate Tavily current storage, substitute, and re-add semantics | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.3** - Capture pytest_mcp and otel_mcp dormant policy with exact fallbacks | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Redis row states: standalone server absent from `.mcp.json`; re-add block in `.claude/mcp-notes.md`; current substitute `redis-cli`; ADG path through `adg_sqlite`; mutation via `tools/adg/adg_redis_ingest.py`.
- Tavily row states: server absent from `.mcp.json`; re-add block in `.claude/mcp-notes.md`; current substitute native web tools in Claude and Tavily plugin/web fallback in Codex; `TAVILY_API_KEY` required for re-add/plugin.
- `pytest_mcp` row states: dormant; current substitute `python -m pytest` with repo pytest policy.
- `otel_mcp` row states: dormant/on-demand; collector/runtime ADG prerequisites are explicit.
- No dormant server is silently treated as live.

**Result**:
- W3 artifacts:
  - `docs/reports/codex/codex_mcp_dormant_policy.md`
  - `docs/reports/codex/codex_mcp_dormant_policy.json`
- Redis storage answer: standalone Redis MCP is absent from `.mcp.json`; the
  exact re-add block is in `.claude/mcp-notes.md`; current local access is
  `redis-cli`; ADG access goes through `adg_sqlite`; Redis projection mutation
  goes through `tools/adg/adg_redis_ingest.py`.
- Tavily storage answer: Tavily MCP is absent from `.mcp.json`; the exact re-add
  block is in `.claude/mcp-notes.md`; `TAVILY_API_KEY` is present in the current
  environment and `C:\Users\amita\env\.env`; Codex uses Tavily plugin/web
  substitute surfaces unless raw MCP is explicitly re-added.
- `pytest_mcp` remains dormant with `python -m pytest` as the direct substitute
  under repo pytest policy.
- `otel_mcp` remains dormant/on-demand, with collector/runtime ADG prerequisites
  required before `otel_server_info` can be considered live.

---

## Wave 4 - Transport Lifecycle And Process Hygiene

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W4.1** - Add transport health probes for Codex-visible and local MCP surfaces | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.2** - Add duplicate-process detection and cleanup guidance | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.3** - Add env placeholder and credential preflight checks | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `adg_runtime_info` PID/nonce changes prove host restarts where available.
- Local probes verify command existence, script compile, TCP dependency health, and credential presence without leaving orphaned background servers.
- Duplicate Notion/Context7/Playwright/ADG/Memory/Vector subprocesses are classified and remediated with non-destructive cleanup guidance.
- Env placeholders like `${ADG_REDIS_URL}` and `${AGENTIC_REPO_ROOT}` are rejected or normalized consistently across Codex-started paths.

**Result**:
- Added read-only audit helper:
  - `scripts/governance/audit_codex_mcp_transports.py`
- W4 artifacts:
  - `docs/reports/codex/codex_mcp_transport_lifecycle_audit.md`
  - `docs/reports/codex/codex_mcp_transport_lifecycle_audit.json`
- `adg_health` is green; `adg_runtime_info` baseline is PID `12236`, startup
  nonce `17aa233dcc0d`. A future restart is proven only if PID or nonce changes.
- Redis TCP dependency is open on `localhost:6379`; command/script probes pass.
- Current runtime env values have no unresolved `${...}` placeholders; source
  placeholders in `.mcp.json` remain expected registry form.
- Duplicate-process classification:
  - `adg_sqlite`: `duplicate` with PIDs `11052` and `12236`.
  - `memory`: `single`.
  - `vector_db`: `single`.
  - `notion`, `context7`, `playwright`: `single_launch_tree`.
  - Dormant `redis`, `pytest_mcp`, `otel_mcp`, `tavily`: no live standalone
    process.
- Focused tests passed:
  `python -m pytest -p pytest_timeout tests/unit/adg/test_path_resolver_sentinel_rejection.py tests/unit/tools/adg/test_adg_mcp_fixes.py::TestRedisUrlEnvOverride -q`
  returned `14 passed, 5 warnings`.

---

## Wave 5 - Documentation, Registration, And Verification

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** - Update Codex backup adapter docs/skills as thin SSOT pointers | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W5.2** - Register and sync the plan in Notion Plans DB | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W5.3** - Run governance, MCP parity, and focused transport tests | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Codex docs do not copy Claude rule bodies; they point to `.mcp.json`, `.claude/mcp-notes.md`, and `mcp-integration` sections.
- Plans DB row exists with `Status=Not Started`, `Exists On Disk=true`, and the correct `Plan File Path`.
- `python scripts/governance/verify_codex_backup.py` passes after any Codex adapter doc/skill edits.
- `python ops_scripts/ci/check_plan_format_compliance.py --strict --paths plans/codex-mcp-transport-parity-4b9c7e.md` passes.

**Result**:
- Updated thin adapter pointers:
  - `docs/codex-backup-adapter.md`
  - `C:\Users\amita\.codex\skills\agentic-workflow-governance\SKILL.md`
  - `C:\Users\amita\.codex\skills\agentic-workflow-verification\SKILL.md`
- W5 artifacts:
  - `docs/reports/codex/codex_mcp_w5_verification.md`
  - `docs/reports/codex/codex_mcp_w5_verification.json`
- Notion Plans row:
  - URL: `https://app.notion.com/p/37b27693f55c8195864af01d07b7181a`
  - Status: `In Progress`
  - Exists On Disk: `__YES__`
  - Plan File Path: `plans/codex-mcp-transport-parity-4b9c7e.md`
- The original `Status=Not Started` acceptance was creation-time guidance. It is
  now intentionally `In Progress` because waves have executed and W2.3 remains
  blocked.
- Verification passed:
  - `python scripts/governance/verify_codex_backup.py`
  - `python scripts/governance/audit_codex_mcp_transports.py --json`
  - `python -m py_compile scripts/governance/audit_codex_mcp_transports.py scripts/governance/verify_codex_backup.py`
  - focused pytest slice: `14 passed, 5 warnings`

---

## Execution Details

### W1.1 - Inventory Live MCP Registry
**Scope**: Read root `.mcp.json`, `AGENTS.md` MCP Quick Reference, and `CLAUDE.md` live/dormant sections.

**Commands**:
```bash
python -c "import json, pathlib; print(json.dumps(json.loads(pathlib.Path('.mcp.json').read_text())['mcpServers'], indent=2))"
rg -n "MCP Quick Reference|Not in `.mcp.json`|redis|tavily" AGENTS.md CLAUDE.md .claude/mcp-notes.md
```

### W1.2 - Inventory Dormant/Re-add Blocks
**Scope**: Parse `.claude/mcp-notes.md` JSONC blocks for `pytest_mcp`, `redis`, `otel_mcp`, and `tavily`.

**Commands**:
```bash
python -c "from pathlib import Path; print(Path('.claude/mcp-notes.md').read_text(encoding='utf-8'))"
```

### W1.3 - Generate Capability Matrix
**Scope**: Emit `docs/reports/codex/codex_mcp_capability_matrix.md` and optional JSON artifact from the inventory.

**Commands**:
```bash
python scripts/governance/verify_codex_backup.py
```

### W2.1 - Restore Critical Missing Live MCP Routes
**Scope**: Prioritize `memory`, `vector_db`, `GitKraken`, and `deepwiki` because repo governance names them as active Claude surfaces.

**Commands**:
```bash
python -m py_compile tools/memory/adg_memory_server.py tools/mcp/vector_db_server.py
```

### W2.2 - Normalize Plugin Substitutes
**Scope**: Map Codex Notion/GitHub/Tavily/Browser/node_repl/plugin tools to Claude tool names and note deltas.

**Commands**:
```bash
python scripts/governance/verify_codex_backup.py
```

### W2.3 - Protect ADG Redis Read-through
**Scope**: Keep the fixed Redis 3 hash-write compatibility and placeholder normalization covered.

**Commands**:
```bash
python -m pytest -p pytest_timeout tests/unit/tools/adg/test_adg_cache_service.py tests/unit/tools/adg/test_adg_mcp_fixes.py::TestRedisUrlEnvOverride tests/unit/tools/adg/test_adg_mcp_fixes.py::TestRedisAvailabilityRefresh -q
```

### W3.1 - Redis Dormant Policy
**Scope**: Replicate Claude's current Redis state exactly: absent standalone MCP, `redis-cli` substitute, `ADG_REDIS_URL` for ADG/memory, `adg_sqlite` as preferred ADG gateway.

**Commands**:
```bash
redis-cli ping
python tools/adg/adg_redis_ingest.py --check
```

### W3.2 - Tavily Dormant Policy
**Scope**: Replicate Claude's current Tavily state exactly: absent from `.mcp.json`, re-add block in `.claude/mcp-notes.md`, `TAVILY_API_KEY` prerequisite, native/plugin substitute.

**Commands**:
```bash
python -c "import os; raise SystemExit(0 if os.getenv('TAVILY_API_KEY') else 1)"
```

### W3.3 - pytest_mcp And OTel Dormant Policy
**Scope**: Keep dormant status explicit; do not imply raw MCP availability in Codex until re-added.

**Commands**:
```bash
python -m pytest --version
```

### W4.1 - Transport Health Probes
**Scope**: Add an audit script or documented procedure that checks visible Codex tools plus local command-start viability.

**Commands**:
```bash
python scripts/governance/verify_codex_backup.py
```

### W4.2 - Duplicate Process Hygiene
**Scope**: Detect multiple MCP subprocesses by command marker and report safe cleanup instructions.

**Commands**:
```bash
python -c "import psutil; print([p.info for p in psutil.process_iter(['pid','name','cmdline']) if p.info.get('cmdline')])"
```

### W4.3 - Env Placeholder Preflight
**Scope**: Prove `${VAR}` placeholders do not leak into runtime URLs/paths in Codex-started server processes.

**Commands**:
```bash
python -m pytest -p pytest_timeout tests/unit/adg/test_path_resolver_sentinel_rejection.py tests/unit/tools/adg/test_adg_mcp_fixes.py::TestRedisUrlEnvOverride -q
```

### W5.1 - Codex Adapter Docs
**Scope**: Update only Codex adapter docs/skills and point to Claude SSOTs.

**Commands**:
```bash
python scripts/governance/verify_codex_backup.py
```

### W5.2 - Plans DB Registration
**Scope**: Create/update Plans DB row after the plan file exists.

**Commands**:
```bash
python ops_scripts/ci/check_plan_registration_freshness.py --help
```

### W5.3 - Final Verification
**Scope**: Run format, adapter, and transport checks.

**Commands**:
```bash
python ops_scripts/ci/check_plan_format_compliance.py --strict --paths plans/codex-mcp-transport-parity-4b9c7e.md
python scripts/governance/verify_codex_backup.py
```

---

## Gap Register

**GAP-1: Memory MCP unavailable in Codex**
- Claude requires session-start memory recall; Codex has no `mem_recall_session_start` tool exposed.
- Impact: Codex cannot honestly satisfy the Memory first-call invariant without a documented blocked/degraded path.

**GAP-2: Vector DB MCP unavailable in Codex**
- `vector_db` is configured and local script startup is viable, but Codex exposes no semantic search tools.
- Impact: Codex falls back to lexical search when Claude would use vector search.

**GAP-3: GitKraken MCP unavailable in Codex**
- `GITKRAKEN_GK_PATH` exists and `gk mcp --help` works, but Codex exposes no GitKraken tools.
- Impact: Codex uses native git/GitHub plugin patterns that may not match repo SSOT expectations.

**GAP-4: DeepWiki MCP unavailable in Codex**
- Claude SSOT routes external GitHub repo Q&A to DeepWiki; Codex exposes no DeepWiki tools.
- Impact: Codex may use generic web search or GitHub plugin instead of DeepWiki.

**GAP-5: Context7 and Playwright are running but not exposed as raw Claude MCPs**
- Local `npx` packages resolve and processes exist, but Codex surfaces substitutes (`node_repl`, plugin docs) instead of the Claude tool names.
- Impact: tool routing advice can drift from actual callable tools.

**GAP-6: Redis standalone MCP is intentionally dormant, but Codex needs exact semantics**
- Current state is not "missing accidentally"; Redis server block is stored in `.claude/mcp-notes.md` and substituted by `redis-cli`/ADG.
- Impact: Codex must not add a standalone Redis MCP without explicit re-add decision.

**GAP-7: Tavily standalone MCP is intentionally dormant, but Codex needs exact semantics**
- Current state is not "missing accidentally"; Tavily server block is stored in `.claude/mcp-notes.md` and substituted by native web tools or Codex Tavily plugin.
- Impact: Codex must not claim raw `tavily-search` unless the MCP or plugin tool is actually exposed.

**GAP-8: Duplicate MCP subprocesses**
- Process inspection showed multiple Node/Python MCP subprocesses for Notion, Context7, Playwright, ADG, and Memory.
- Impact: stale processes can hold resources, confuse health checks, and create false transport confidence.

---

## Definition of Done

DoD-1: Capability matrix exists and covers all Claude live and dormant MCPs.
- Evidence: `docs/reports/codex/codex_mcp_capability_matrix.md` lists every server in `.mcp.json`, every dropped block in `.claude/mcp-notes.md`, Codex callable surface, fallback, and gap status.
- Status: TODO

DoD-2: Live critical transport smoke checks pass.
- Evidence: `adg_health` returns full mode; Notion self fetch works; Memory/Vector/GitKraken/DeepWiki routes are either callable or explicitly blocked with fallback.
- Status: TODO

DoD-3: Redis and Tavily semantics exactly match Claude current setup.
- Evidence: plan/doc matrix states Redis and Tavily are absent from `.mcp.json`, stored as re-add blocks in `.claude/mcp-notes.md`, and routed through current substitutes.
- Status: TODO

DoD-4: Transport hygiene script/procedure detects duplicate MCP processes and stale env placeholders.
- Evidence: audit output classifies duplicate processes and placeholder leakage without killing user-owned processes by default.
- Status: TODO

DoD-5: Codex adapter verification remains green.
- Evidence: `python scripts/governance/verify_codex_backup.py` exits 0 after any Codex docs/skills edits.
- Status: TODO

DoD-6: Plan format and registration are valid.
- Evidence: `python ops_scripts/ci/check_plan_format_compliance.py --strict --paths plans/codex-mcp-transport-parity-4b9c7e.md` exits 0 and Plans DB row has `Status=Not Started`, `Exists On Disk=true`, and `Plan File Path=plans/codex-mcp-transport-parity-4b9c7e.md`.
- Status: TODO

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=codex-mcp-transport-parity-4b9c7e wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=codex-mcp-transport-parity-4b9c7e decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=codex-mcp-transport-parity-4b9c7e reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

> **Documentation is not authorization.** Retroactive plan updates are not governance.

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| _None_ | Net-new Codex MCP parity plan. |

_None - net-new plan._

---

## Marker Quick Reference

Wave lifecycle markers:
```
PLAN_CREATED: slug=codex-mcp-transport-parity-4b9c7e path=plans/codex-mcp-transport-parity-4b9c7e.md status=Not Started
WAVE_START: plan=codex-mcp-transport-parity-4b9c7e wave=<N>
WAVE_COMPLETE: plan=codex-mcp-transport-parity-4b9c7e wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=codex-mcp-transport-parity-4b9c7e phase=<W1.1>
PLAN_COMPLETE: plan=codex-mcp-transport-parity-4b9c7e note="<final outcome>"
```
