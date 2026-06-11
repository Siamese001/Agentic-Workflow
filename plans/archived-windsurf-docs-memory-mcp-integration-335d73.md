---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\memory-mcp-integration-335d73.md'
original_relative_path: 'memory-mcp-integration-335d73.md'
source_sha256: 59087bfb98e2d6c2d56ae105e00bcec997edeb0b4288223e195b4f8f8be6fa89
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Memory MCP Full Agent Integration

Integrate the live Memory MCP (`mcp11_*` tools) as the persistent knowledge graph across all agent layers — `agentic_core`, `apps_rg`, `apps_lic`, and `apps_shared`.

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


## Current State (from ADG + code review)

| Component | Status | Gap |
|---|---|---|
| `GraphMemoryBridge` (L4) | Exists, stubs out `mcp11_*` calls via injected `Callable` | Never wired to live MCP — no-ops in production |
| `SovereignMemoryMcp` (L4) | References Redis shield + missing constants | Dead code — `MAX_ENTITY_NAME_LENGTH` undefined |
| `ADGMCPClient` | Pure in-memory fallback, `use_mcp=False` always | ADG graph never persists to Memory MCP |
| `KnowledgeGraphHealingStrategy` | `_extract_entities_relations` returns empty dict | Stub — extraction + persistence not implemented |
| `BaseDispatchAgent` / `RgReflectionAgent` | No memory writes | Agents learn nothing across sessions |
| MCP registry | `memory` entry correct (`@modelcontextprotocol/server-memory`) | Tools available as `mcp11_*` in Windsurf |

---

## Phase Plan

### Phase 1 — Wire GraphMemoryBridge to live `mcp11_*` tools
**Files:** `agentic_core/L4_state/enforcement/graph_memory_bridge.py`

- Replace the injected `Callable` pattern with direct `mcp11_create_entities`, `mcp11_create_relations`, `mcp11_add_observations`, `mcp11_search_nodes` calls
- Remove the stub `_init_mcp` that assumes availability but never connects
- Keep resilient mode: log + skip if MCP unavailable, never crash

### Phase 2 — Fix SovereignMemoryMcp dead code
**Files:** `agentic_core/L4_state/memory/sovereign_memory_store.py`

- Fix `MAX_ENTITY_NAME_LENGTH` undefined constant (use `max_entity_name_length` already declared)
- Remove Redis shield dependency (not available in CI) — route through `GraphMemoryBridge` instead
- `create_entities`, `add_observations`, `search_nodes` delegate to `GraphMemoryBridge`

### Phase 3 — BaseDispatchAgent: register + write on task completion
**Files:** `apps_shared/reasoning/BaseDispatchAgent.py`

- On agent init: call `bridge.create_agent_entity(self.__class__.__name__)`
- On task success (score >= 0.8): call `bridge.create_mastered_task_relation(...)`
- On task failure: call `bridge.create_relation(..., RELATION_FAILED_TASK)`
- Observation: record task type, timestamp, outcome

### Phase 4 — RgReflectionAgent: persist reflection insights
**Files:** `apps_rg/reasoning/RgReflectionAgent.py`

- After each reflection cycle: `bridge.add_observation(agent_name, reflection_summary)`
- Create `REFLECTS_ON` relation: agent -> document/section entity
- Query prior reflections via `bridge.search_entities(query)` to avoid redundant analysis

### Phase 5 — BaseHealingOrchestrator: record healing outcomes
**Files:** `apps_shared/reasoning/BaseHealingOrchestrator.py`

- Create `HealingRun` entity per cycle with observations: files_fixed, violations_resolved
- Relation: `HealingOrchestrator -HEALED-> FileEntity`
- Enables cross-session healing deduplication (don't re-heal already-fixed files)

### Phase 6 — KnowledgeGraphHealingStrategy: implement extraction
**Files:** `agentic_core/L3_orchestration/enforcement/knowledge_graph_healing_strategy.py`

- `_extract_entities_relations`: parse file content -> extract class/function names as entities, import relations
- `_persist_kg_data`: route through `GraphMemoryBridge` (not the current empty `return True` stub)
- Confidence threshold: only persist if >= `KG_MIN_CONFIDENCE_FOR_HEALING`

### Phase 7 — apps_lic agents: campaign/deliverability memory
**Files:** `apps_lic/reasoning/OutreachLearningAgent.py`

- Register agent entities on init
- Persist campaign outcomes as observations on `CampaignEntity` nodes
- Persist success/failure patterns via MASTERED_TASK / FAILED_TASK relations

---

## Key Design Decisions

- **No new files** for the bridge — harden `GraphMemoryBridge` in-place; it is already the SSOT
- **Mixin approach**: `GraphMemoryBridge.get_instance()` singleton — agents call it directly, no new base class
- **Resilient by default**: all Memory MCP calls wrapped in try/except; agents must not fail if MCP is down
- **Idempotency**: entity names are class names (stable); `create_agent_entity` already guards duplicates
- **Test strategy**: inject mock functions via `bridge.set_mcp_functions(...)` (already supported)

---

## Files Touched

| File | Change Type | Status |
|---|---|---|
| `agentic_core/L4_state/enforcement/graph_memory_bridge.py` | Harden — wire live `mcp11_*` | DONE |
| `agentic_core/L4_state/memory/sovereign_memory_store.py` | Fix dead code + delegate to bridge | DONE |
| `agentic_core/L3_orchestration/enforcement/knowledge_graph_healing_strategy.py` | Implement stubs | DONE |
| `apps_shared/reasoning/BaseDispatchAgent.py` | Add bridge calls | DONE |
| `apps_shared/reasoning/BaseHealingOrchestrator.py` | Add healing outcome persistence | DONE |
| `apps_rg/reasoning/RgReflectionAgent.py` | Add reflection persistence | DONE |
| `apps_lic/reasoning/OutreachLearningAgent.py` | Add entity registration + outcome storage | DONE |

---

## Out of Scope (this plan)
- ADG -> Memory MCP persistence (separate concern)
- Redis MCP migration (Phase 16A already tracked)
- LLM Router MCP (Phase 16B)

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

