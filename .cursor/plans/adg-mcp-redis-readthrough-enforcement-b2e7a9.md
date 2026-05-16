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
PLAN_STATUS: IN_PROGRESS  
CURRENT_WAVE: W1  
LAST_COMPLETED_WAVE: (none)  
LAST_UPDATED: 2026-05-16  

> W1 artifact: `artifacts/test_inventory/adg_mcp_redis_readthrough_inventory.md` (pending human review before marking W1 complete / DoD-4).

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
| **W3** | Redis / MV keys | Ensure `adg_redis_ingest.py` / `RedisCache` / `MvReader` expose data **needed** by W2 (add keys or document gap) |
| **W4** | Verification | Unit/integration tests for `backend_used` / hit-miss; MCP handler tests if present; **no** graph regeneration requirement for merge |
| **W5** | Doctrine sync | Update `.cursor/skills/adg-sqlite.md`, `graph-analysis`, `mcp-integration` §2: explicit ladder **Redis (warm) → MCP → SQLite direct + `DEGRADED_FALLBACK` reason** |

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

- Tests prove at least one **redis hit** path (mock or embedded Redis) and **sqlite fallback**.
- `python -m pytest` on touched tests **green** (narrow scope).

---

## W5 acceptance

- Rules/skills cite **one** canonical ladder; agent guidance: raw `sqlite3` in plans requires **`DEGRADED_FALLBACK`** unless matching named CI script.

---

## Definition of Done

| # | Criterion | Status |
|---|-----------|--------|
| DoD-1 | Plan file on disk | DONE (this file) |
| DoD-2 | Parent linked | DONE |
| DoD-3 | Notion Plans row | DONE (`36227693-f55c-815d-8eda-dcd9e3aa0031`) |
| DoD-4 | W1 inventory artifact | 🔲 (file created; awaits review per W1 gates) |
| DoD-5 | Code + tests + docs | 🔲 |

---

## Related artifacts

- `.cursor/rules/adg-canonical-invariants.mdc`
- `.cursor/skills/adg-sqlite/SKILL.md`
- `.cursor/skills/mcp-integration/SKILL.md` §2
- `tools/adg/core/service.py`
- `ops_scripts/ci/check_l5_hotspot_fanin_ratchet.py` (SQLite-canonical note)

PLAN_CREATED: slug=adg-mcp-redis-readthrough-enforcement-b2e7a9 path=.cursor/plans/adg-mcp-redis-readthrough-enforcement-b2e7a9.md status=Not Started  
NOTION_PLAN_PAGE_ID: 36227693-f55c-815d-8eda-dcd9e3aa0031
