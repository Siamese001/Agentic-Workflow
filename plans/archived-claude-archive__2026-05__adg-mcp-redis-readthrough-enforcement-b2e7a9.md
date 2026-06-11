---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\adg-mcp-redis-readthrough-enforcement-b2e7a9.md'
original_relative_path: '_archive\\2026-05\\adg-mcp-redis-readthrough-enforcement-b2e7a9.md'
source_sha256: 565af73a04e22488daaa3ad837531f8c4ed26862ad70559a8e34cf3093586a6c
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: adg-mcp-redis-readthrough-enforcement-b2e7a9
plan_type: governance
parent_plan_id: adg-hotspot-test-coverage-b8e4f2
prior_sibling_plan_id: l5-fanin-architecture-reduction-e7c4a2
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: true
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

# ADG MCP + Redis read-through enforcement (policy ↔ implementation alignment)

**Child plan** under **PARTIAL** parent `adg-hotspot-test-coverage-b8e4f2`, sibling-aware to `l5-fanin-architecture-reduction-e7c4a2` (fan-in work exposed the gap).

**Problem statement:** Repo rules state **SQLite = canonical truth**, **Redis = hot projection**, **MCP = read-only gateway**, with **Redis green-light before T2/T3** and `adg_sqlite` as the primary agent surface. In `tools/adg/core/service.py`, **several MCP-backed entrypoints still call `SQLiteBackend` directly** (always `backend_used=sqlite`), while fan-in / fan-out / node-by-file paths use **`_read_through_cache`** (Redis hit → SQLite miss/fill). Agents and CI scripts often skip straight to **`sqlite3` on disk**, which is **allowed as degraded fallback** but must be **provenance-stamped** and should not be the silent default for refactor/analysis.

**Outcome:** MCP consumers see **Redis when the cache is warm** for the **same operations** that today bypass Redis; **SQLite remains authoritative** on divergence; **ratchet/CI** may stay SQLite-embedded but must be **documented** as intentional; skills/rules updated so the ladder is one sentence everywhere.

---

## Parent and lineage

| Role | Plan / artifact |
|------|------------------|
| **Parent** | `.cursor/plans/adg-hotspot-test-coverage-b8e4f2.md` |
| **Prior sibling (context)** | `.cursor/plans/l5-fanin-architecture-reduction-e7c4a2.md` — fan-in / MCP vs sqlite RCA |
| **Primary code** | `tools/adg/core/service.py`, `tools/adg/core/sqlite_backend.py`, `tools/adg/cache/redis_cache.py`, `tools/adg/mv_reader.py` |

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1  
PLAN_STATUS: COMPLETE  
CURRENT_WAVE: COMPLETE  
LAST_COMPLETED_WAVE: W5  
LAST_UPDATED: 2026-05-16  

> **CLOSED.** W1 inventory SSOT: `docs/reports/adg/adg_mcp_redis_readthrough_inventory.md`. W3 MV key contract + W4 mock verification: `docs/reports/adg/adg_mcp_redis_mv_key_contract.md`.  
> **W5 doctrine:** Canonical ladder + verbatim doctrine in **`adg-sqlite`**, **`graph-analysis`**, **`mcp-integration` §2**, **`adg-canonical-invariants.mdc` §1**. No ADGService behavior change in W5; **`test_mv_mcp_handlers.py`** drift remains separate.

---

## Non-goals

- Replacing **canonical SQLite** snapshots or changing **ADG ingest** ownership.
- Weakening **CI gates** or **ratchet** baselines; no `DEFAULT_RATCHET` edits under this plan.
- Mandatory **agentic_core** edits (this plan targets **tools/adg** + docs/rules/tests).

---

## Wave structure

| Wave | Focus | Primary deliverable |
|------|--------|-------------------|
| **W1** | Inventory | Matrix: MCP tool → `ADGService` method → `_read_through_cache`? → `backend_used` today |
| **W2** | Implement read-through | Wire **high-value** SQLite-only paths to same cache pattern as fan-in (at minimum: `get_mv_hotspot_centrality`; candidates: `find_node`, `query_p_view`, `get_blast_radius` if sqlite-only) |
| **W3** | Redis / MV keys | **DONE (W3 wave):** hotspot key contract + ingest gap — **`docs/reports/adg/adg_mcp_redis_mv_key_contract.md`** |
| **W4** | Verification | **DONE:** mock-only tests for **`get_mv_hotspot_centrality` `backend_used`** (redis/sqlite/error/empty/divergence), **`response.data`** keys **`{hotspots,count}`**, MCP handler passthrough; **no graph regen**. Table: **`docs/reports/adg/adg_mcp_redis_mv_key_contract.md`** § W4 verification. |
| **W5** | Doctrine sync | **DONE:** canonical ladder Redis warm → MCP → SQLite direct + **`DEGRADED_FALLBACK`** unless CI parity — **`adg-sqlite`**, **`graph-analysis`**, **`mcp-integration` §2**, **`adg-canonical-invariants.mdc`** |

---

## W1 acceptance

- Table in `artifacts/test_inventory/adg_mcp_redis_readthrough_inventory.md` listing every `adg_*` tool in `tools/adg/mcp/` → service method → cache strategy.
- Explicit callout of **`check_l5_hotspot_fanin_ratchet.py`** (and peers): **SQLite-by-design** with provenance note “CI parity.”

---

## W2–W3 acceptance

- `get_mv_hotspot_centrality` (and any other in-scope method) uses shared **`_read_through_cache`** (or `MvReader`) where Redis has row material; **`backend_used`** reflects `redis` vs `sqlite` per `ADGResponse`.
- **Cold Redis:** behavior = current SQLite path (no new failure mode).
- **Divergence:** SQLite fill path remains source of truth.

---

## W4 acceptance

- **DONE (2026-05-16):** Narrow pytest proves hotspot path **`backend_used`** for **redis vs sqlite** (warm rank + hydrated rows; cold `MVRedisReader`; `None`/`[]`; reader exception); **SQLite fallback** preserves canonical ordering on divergence (`hydrate_mv_hotspot_centrality_ordered` → `None`).
- **`ADGResponse.data`** retains exactly **`hotspots`** + **`count`** (validated in read-through + **P33** tests); **`tools/adg/mcp/tool_handlers.adg_mv_hotspot_centrality`** echoes **`status`/`data`/`backend_used`** with same inner `data` shape.
- **No** standalone `redis-server` required for proofs (MagicMock **`_mv_reader`** / stub services).

---

## W5 acceptance

- **DONE (2026-05-16):** Skills **`adg-sqlite`**, **`graph-analysis`**, **`mcp-integration` §2**, and rule **`adg-canonical-invariants.mdc` §1** cite the **same** canonical ladder and **verbatim doctrine** (Redis warm projection → MCP → SQLite direct only with **`DEGRADED_FALLBACK`** unless named CI parity script). Reports **`adg_mcp_redis_mv_key_contract.md`** § W5 + inventory header updated.

---

## Definition of Done

| # | Criterion | Status |
|---|-----------|--------|
| DoD-1 | Plan file on disk | DONE (this file) |
| DoD-2 | Parent linked | DONE |
| DoD-3 | Notion Plans row | DONE (`36227693-f55c-815d-8eda-dcd9e3aa0031`) |
| DoD-4 | W1 inventory artifact | DONE — `docs/reports/adg/adg_mcp_redis_readthrough_inventory.md` (+ optional artifacts mirror `artifacts/test_inventory/...`) |
| DoD-W3 | W3 `mv_hotspot_centrality` Redis key proof | DONE — `docs/reports/adg/adg_mcp_redis_mv_key_contract.md` + `tests/unit/tools/adg/test_mv_hotspot_redis_key_contract.py` |
| DoD-W4 | W4 hotspot `backend_used` + payload verification (mock-only) | DONE — `docs/reports/adg/adg_mcp_redis_mv_key_contract.md` § W4 + `test_get_mv_hotspot_centrality_readthrough.py` + **`test_p33_graph_layer_tools.py`** (W4 nodes) |
| DoD-5 | W5 doctrine sync (skills/rules ladder) | DONE — `.cursor/skills/adg-sqlite/SKILL.md`, `graph-analysis/SKILL.md`, `mcp-integration/SKILL.md` §2, `.cursor/rules/adg-canonical-invariants.mdc`; evidence **`docs/reports/adg/adg_mcp_redis_mv_key_contract.md`** § W5 |

---

## Related artifacts

- `.cursor/rules/adg-canonical-invariants.mdc`
- `.cursor/skills/adg-sqlite/SKILL.md`
- `.cursor/skills/graph-analysis/SKILL.md`
- `.cursor/skills/mcp-integration/SKILL.md` §2
- `tools/adg/core/service.py`
- `ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py` (SQLite-canonical note)

PLAN_CREATED: slug=adg-mcp-redis-readthrough-enforcement-b2e7a9 path=.cursor/plans/adg-mcp-redis-readthrough-enforcement-b2e7a9.md status=COMPLETE  
NOTION_PLAN_PAGE_ID: 36227693-f55c-815d-8eda-dcd9e3aa0031
