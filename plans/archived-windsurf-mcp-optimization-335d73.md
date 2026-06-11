---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\mcp-optimization-335d73.md'
original_relative_path: 'mcp-optimization-335d73.md'
source_sha256: 629ebf2e47d92bb79011de84c121e873462ba9bb56a950eca181b85c97755c3a
recovered_status: LOST_RECOVERED
last_commit: '20f413ffbf5'
last_commit_date: '2026-04-01 14:39:03 -0400'
created_date: '2026-03-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# MCP Optimization — Fix Broken Wiring + Expand Usage

Use the refreshed ADG (3,318 modules, 151,789 edges, 217 critical violations) to fix dead/stub MCP wiring and expand MCP usage across LLM routing, Redis, ADG persistence, sequential thinking, playwright, filesystem, and brave search.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## ADG Key Findings (2026-03-11T183233Z)

| Signal | Value |
|---|---|
| Modules | 3,318 |
| Edges | 151,789 |
| Critical violations | 217 |
| Repair routes | 705 |
| `mcp_authority` bare references (undefined) | 5 files |
| `redis_shield` bare references (undefined) | 5 files |
| `mcp_manager.py` | **Missing entirely** — imported by `sovereign_mcp_router.py` |
| `MCPConnectionManager` | Protocol stub only in `seams/contracts/mcp.py` — no concrete implementation |
| `load_mcp_config` | Missing — imported but no file exists |
| Sequential thinking MCP | Registered in `mcp_registry.py`, never called by any agent |
| Brave search MCP | Registered, referenced only in a dead/unreachable fallback branch |
| Playwright MCP | Registered, only used in L6 dashboard util via subprocess (not live MCP tools) |
| Filesystem MCP | `SovereignFilesystemMcp` exists but calls `redis_shield` / `mcp_authority` (both undefined) |
| Redis MCP | `REDIS_MCP_ENABLED` flag gates registry presence only, not runtime routing |
| ADG → Memory MCP | No persistence path exists |
| LLM Router | `ModelRouter` + `FallbackClient` — mock stubs only (`asyncio.sleep`) |

---

## Phases

### Phase 1 — Create `mcp_manager.py` + fix `mcp_authority` / `redis_shield` undefined references
**Files:**
- `agentic_core/L3_orchestration/reasoning/mcp_manager.py` *(create)*
- `agentic_core/L3_orchestration/engines/sovereign_mcp_router.py`
- `agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py`

**Work:**
- Create `mcp_manager.py` with concrete `MCPConnectionManager` (satisfies Protocol in `seams/contracts/mcp.py`) and `load_mcp_config` — routes `call_tool(tool, kwargs)` to live Windsurf MCP tools (`mcp8_*`, `mcp12_*`, `mcp1_*`, `mcp11_*`) via a dispatch table
- Replace all bare `mcp_authority.record_breach(...)` / `mcp_authority.is_authorized()` calls with `MCPSovereignAuthority` singleton from `mcp_sovereign_authority_enforcer.py`
- Replace all bare `redis_shield.execute(...)` calls with `get_hot_cache()` from `agentic_core.cache`

### Phase 2 — LLM Router: wire real providers + sequential thinking MCP tier
**Files:**
- `apps_shared/types/model_router_types.py`
- `apps_shared/utils/router_factory_util.py`

**Work:**
- Replace `OpenAIClient.generate` / `AnthropicClient.generate` mock stubs with real provider calls (env-var API keys, no hardcoding)
- Add `ModelTier.SEQUENTIAL` tier mapped to `sequential_thinking` MCP — invoked when `complexity_score >= 9` or `task_type == STRATEGIC_PLANNING`
- Add `_call_sequential_thinking(prompt, goal, max_steps)` on `FallbackClient` routing through `MCPConnectionManager.call_tool("sequential_thinking", {...})`
- Cache sequential thinking step templates in Redis via `get_hot_cache()` (30-day TTL)

### Phase 3 — Redis MCP: route `SovereignRedisOrchestrator` through MCP when flag enabled
**Files:**
- `agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py`
- `agentic_core/L2_execution/config/mcp_registry.py`

**Work:**
- When `sovereign_config.REDIS_MCP_ENABLED=True`, route `get`/`set`/`delete` through `MCPConnectionManager.call_tool("redis_get"/"redis_set"/"redis_delete", ...)` instead of direct `redis.Redis`
- Keep direct `redis.Redis` as fallback when flag is off (backwards compat)
- Currently flag only gates registry presence — extend to gate actual runtime dispatch

### Phase 4 — ADG → Memory MCP persistence
**Files:**
- `tools/generate_full_adg.py`
- `agentic_core/L4_state/enforcement/graph_memory_bridge.py`

**Work:**
- After ADG generation, call `GraphMemoryBridge.get_instance()` to persist:
  - Layer summary entities (e.g. `ADG_L4: 90 modules`) with violation-count observations
  - Top-10 fan-out hotspot module entities
  - All 217 critical violation entities with `VIOLATES` relations and severity/file observations
  - ADG snapshot digest entity for drift tracking (`+23 edges, +2 violations` delta)
- Enables agents to `search_nodes("L4 violations")` cross-session without re-running ADG

### Phase 5 — Brave Search: fix dead branch + wire into reflection agents
**Files:**
- `agentic_core/L3_orchestration/engines/sovereign_mcp_router.py`
- `apps_rg/reasoning/RgReflectionAgent.py`

**Work:**
- In `SovereignMcpRouter.resolve_violation`, the `brave_search` fallback is unreachable (guarded by `raise` before it) — fix control flow so live `mcp1_brave_web_search` is actually called
- In `RgReflectionAgent._post_reflect`, add `_search_external_best_practices(topic)` that calls `mcp1_brave_web_search` when quality score < 0.6

### Phase 6 — Playwright: replace subprocess calls with live `mcp12_*` tools
**Files:**
- `agentic_core/L6_observability/dashboards/verify_dashboard_e2e_playwright_util.py`
- `ops_scripts/dev_tools/l0_scripts/playwright_verify_total_row_util.py`

**Work:**
- Replace existing Playwright subprocess/CLI calls with `mcp12_playwright_navigate`, `mcp12_playwright_screenshot`, `mcp12_playwright_get_visible_text`
- Wire into `BaseHealingOrchestrator._persist_healing_cycle` to trigger dashboard verification after each healing cycle

### Phase 7 — Filesystem MCP: harden `SovereignFilesystemMcp` with `mcp8_*` tools
**Files:**
- `agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py`

**Work:**
- Replace `await self.manager.call_tool("read_file", ...)` with `mcp8_read_text_file`
- Replace `await self.manager.call_tool("write_file", ...)` with `mcp8_write_file`
- Replace `redis_shield.execute(...)` ledger writes with `get_hot_cache().set(...)` (Phase 1 prerequisite)

---

## Dependency Order

```
Phase 1 (create mcp_manager + fix undefined refs)
  ├─► Phase 2 (LLM router + sequential thinking)
  ├─► Phase 3 (Redis MCP routing)
  └─► Phase 7 (filesystem MCP hardening)

Phase 4 (ADG → Memory MCP)  — independent
Phase 5 (Brave search fix)  — independent
Phase 6 (Playwright)        — independent
```

---

## Files Touched

| File | Phase | Change |
|---|---|---|
| `agentic_core/L3_orchestration/reasoning/mcp_manager.py` | 1 | **Create** concrete `MCPConnectionManager` + `load_mcp_config` |
| `agentic_core/L3_orchestration/engines/sovereign_mcp_router.py` | 1, 5 | Fix undefined refs; fix brave search unreachable branch |
| `agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py` | 1, 7 | Fix undefined refs; wire `mcp8_*` |
| `apps_shared/types/model_router_types.py` | 2 | Wire real providers + sequential MCP tier |
| `apps_shared/utils/router_factory_util.py` | 2 | Factory wiring |
| `agentic_core/L3_orchestration/engines/sovereign_redis_orchestrator.py` | 3 | Redis MCP flag routing |
| `tools/generate_full_adg.py` | 4 | ADG → Memory MCP persistence hook |
| `agentic_core/L4_state/enforcement/graph_memory_bridge.py` | 4 | ADG entity/relation schemas |
| `apps_rg/reasoning/RgReflectionAgent.py` | 5 | Brave search quality-gate fallback |
| `agentic_core/L6_observability/dashboards/verify_dashboard_e2e_playwright_util.py` | 6 | Wire `mcp12_*` |
| `ops_scripts/dev_tools/l0_scripts/playwright_verify_total_row_util.py` | 6 | Wire `mcp12_*` |

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

