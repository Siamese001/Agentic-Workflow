---
plan_id: notion-backlog-schema-refactor-7c3d9e
plan_type: infra
# infra: no code refactor of L0..L6 agentic_core; touches Notion schema + post-hook + AGENTS.md.
# §22 ADG graph-layer-evidence gate: SKIPPED per plan_type=infra.
---

# Notion Backlog Schema Refactor — Typed Fields + Projection Pattern

Replace the broken mixed-schema `Priority` field and prose-embedded impact scores with typed properties, a `Plans` relation DB, and a single `Backlog Snapshot` projection page that Cursor Agent reads with one API call instead of paginating 155+ rows.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `AGENTS.md` Notion Workspace Map | existing Wave/Phase Convergence IDs + writeback patterns | ✅ |
| `.cursor/rules/deferred-scope-capture.md` | marker contract + auto-post fields that must survive migration | ✅ |
| `.cursor/rules/memory-notion-writeback.md` | writeback discipline that consumers rely on | ✅ |
| `tools/priority/deferred_scope_scorer.py` | SSOT scorer that produces `band` + `impact_score` — both must land in typed fields | ✅ |
| `.cursor/scripts/post_cursor_agent_deferred_scope_capture.py` | current post-hook that writes rows; must be updated to typed fields + snapshot refresh | ✅ |
| Notion API docs (2.0 data_source split) | database_id vs data_source_id semantics for writes/reads | ✅ |
| 11-Coordinated-Notion-Agents postmortem (Reddit 2026) | projection-over-source pattern; consumer/schema decoupling | ✅ |

---

## Wave Structure

| Wave | Metric | Scope | Checkpoint | Tokens |
|------|--------|-------|------------|---------|
| W1 | Additive schema — new typed fields on existing DB | Add `P-Band`, `Impact Score`, `Layer`, `Surface`, `Fan-In`, `Coverage Gap %` properties; keep legacy `Priority` for back-compat | A — schema additive only, no row writes | 2,000 🟢 |
| W2 | Backfill — parse legacy rows into new typed fields | Python script reads all rows, parses `[Pn]` from title + impact from `Blocking Items`, writes typed fields | B — 155 rows backfilled, 0 data loss | 3,000 🟢 |
| W3 | `Plans` relation DB + migration from free-text | Create `Plans` DB; backfill one row per unique plan slug; convert `Plan File` rich_text to `relation` | C — every Backlog Item has `Plan` relation | 4,000 🟢 |
| W4 | `Backlog Snapshot` projection page + hook wiring | Create single page; wire `post_cursor_agent_deferred_scope_capture.py` to regenerate markdown snapshot on every write | D — `retrieve-a-page` returns full dashboard | 4,000 🟢 |
| W5 | Consumer switchover + AGENTS.md update | Update `AGENTS.md` Notion Workspace Map; update memory-notion-writeback skill templates; default Cursor Agent backlog query → `retrieve-a-page(Snapshot)` | E — `query notion backlog` answered in 1 call | 2,000 🟢 |
| W6 | Deprecate `Priority` number field + rename DB | After 1-week bake, archive legacy `Priority` property; rename `Wave/Phase Convergence` → `Backlog Items` | F — `Priority` removed, DB renamed | 2,000 🟢 |

**Total: 17,000 tokens across 6 waves, all GREEN.**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files / Notion ops) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------------------|-------------|-------------|--------|
| 1.1 | Add `P-Band` select property (`P0..P5, UNSCORED`) | Notion UI or `API-update-a-data-source` on `aa8d2507-101e-4384-81d9-60ea3fe33876` | PP-1 mixed-schema Priority | ~1k | 🔲 TODO |
| 1.2 | Add `Impact Score`, `Fan-In`, `Coverage Gap %` (number) + `Layer`, `Surface` (select) | Same DB | PP-2 scalar data in prose | ~1k | 🔲 TODO |
| 2.1 | Write `tools/migration/notion_backfill_typed_fields.py` — parse existing 155 rows | new script; reads from data_source, writes via `API-patch-page` | GAP-1 existing rows lack typed data | ~1.5k | 🔲 TODO |
| 2.2 | Execute backfill; verify 100% coverage (every row has `P-Band` set) | Run script; audit with `API-query-data-source` filter `P-Band is empty` | GAP-2 backfill idempotency | ~1.5k | 🔲 TODO |
| 3.1 | Create `Plans` Notion DB with `Slug` title + `Status` + `Summary` + rollups | `API-post-page` + `API-create-a-data-source` | PP-3 free-text plan slugs | ~1.5k | 🔲 TODO |
| 3.2 | Backfill one row per unique plan slug (20 unique plans from current data) | Migration script | GAP-3 orphan rows (NEW: prefix) | ~1k | 🔲 TODO |
| 3.3 | Add `Plan` relation property to Backlog Items; backfill relation | Schema update + migration | GAP-4 plan rename cascade | ~1.5k | 🔲 TODO |
| 4.1 | Create `Backlog Snapshot` standalone page | `API-post-page` under workspace root | PP-4 pagination cost | ~1k | 🔲 TODO |
| 4.2 | Extend `post_cursor_agent_deferred_scope_capture.py` → `regenerate_snapshot()` | `.cursor/scripts/post_cursor_agent_deferred_scope_capture.py` | GAP-5 hook must not slow down turns | ~1.5k | 🔲 TODO |
| 4.3 | Render top-25 markdown + counts + stale flags to snapshot page via `API-patch-block-children` | New helper `tools/notion/snapshot_renderer.py` | GAP-6 idempotent rendering | ~1.5k | 🔲 TODO |
| 5.1 | Update `AGENTS.md` Notion Workspace Map with new DB IDs + Snapshot page ID | `AGENTS.md` Notion block + sync check | PP-5 consumer routing docs | ~1k | 🔲 TODO |
| 5.2 | Update `.cursor/skills/writeback-discipline/` row templates to new typed fields | skill content | PP-6 template drift | ~1k | 🔲 TODO |
| 6.1 | Archive legacy `Priority` number property after 1-week bake | Notion schema update | — | ~1k | 🔲 TODO |
| 6.2 | Rename DB `Wave/Phase Convergence` → `Backlog Items` | Notion UI | — | ~1k | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: Existing rows lack typed data**
- 155 rows have impact scores only in prose `Blocking Items`, bands only in title `[Pn]` prefix.
- Mitigation: W2 parser script is deterministic; regex patterns already validated against live data (33/33 band match, 22/33 exact impact, 11/33 rounding-only).

**GAP-2: Backfill idempotency**
- Script must be re-runnable without double-writes or clobbering manual edits.
- Mitigation: skip rows where `P-Band` already set; emit audit log.

**GAP-3: Orphan rows with `NEW:` plan prefix**
- 9 rows reference plans that don't exist on disk (`NEW:adg-mcp-reopen-hardening`).
- Mitigation: create stub `Plans` row for each unique `NEW:` slug; flag as `Status=Proposed`.

**GAP-4: Plan rename cascade**
- Once `Plan` is a relation, renaming a plan file on disk must update the Notion `Plans` row, not re-point every Backlog Item.
- Mitigation: `Plans.Slug` is the title; document update flow in writeback-discipline skill.

**GAP-5: Hook latency**
- Snapshot regeneration on every post-hook turn could exceed the 5s progress-bar threshold.
- Mitigation: throttle to once per 30s (unless forced); use single `API-patch-block-children` replace, not per-row updates.

**GAP-6: Idempotent snapshot rendering**
- Rendering must clear old children before appending new ones to avoid infinite growth.
- Mitigation: snapshot page has exactly one top-level `synced_block` or known marker; replace its children wholesale.

---

## Execution Plan

### Phase W1 — Additive Schema (no data writes)

**Scope**: Add typed properties to existing `aa8d2507-101e-4384-81d9-60ea3fe33876` database. Keep legacy `Priority` column for back-compat.

**Commands** (via Cursor Agent Notion MCP):
```
# W1.1 — W1.2: add properties via API-update-a-data-source
# (or manually via Notion UI — either works; API gives provenance)
```

**Acceptance**: New properties visible in DB schema; existing rows show empty values; no consumer breakage.

### Phase W2 — Backfill

**Scope**: Parse `[Pn]` and `Priority impact score: N.NN` from existing rows into typed fields.

**Commands**:
```bash
python tools/migration/notion_backfill_typed_fields.py --dry-run
python tools/migration/notion_backfill_typed_fields.py --execute
```

**Acceptance**: `API-query-data-source` with `filter: {P-Band: is_empty}` returns 0 rows.

### Phase W3 — Plans Relation DB

**Scope**: Create `Plans` DB; backfill ~20 unique plan slugs; add `Plan` relation on Backlog Items.

**Commands**:
```bash
python tools/migration/notion_create_plans_db.py
python tools/migration/notion_backfill_plan_relations.py --execute
```

**Acceptance**: Every Backlog Item has a non-null `Plan` relation; `Plans.Open Items` rollup > 0 for top plans.

### Phase W4 — Projection Page

**Scope**: Create `Backlog Snapshot` page; wire post-hook to regenerate on every marker-bearing response.

**Commands**:
```bash
python tools/notion/snapshot_renderer.py --create-page
# Then update .cursor/scripts/post_cursor_agent_deferred_scope_capture.py to call regenerate_snapshot()
```

**Acceptance**: `API-retrieve-a-page(snapshot_id)` returns top-25 + counts + band breakdown in <2KB.

### Phase W5 — Consumer Switchover

**Scope**: Update AGENTS.md + skill templates; make `retrieve-a-page(Snapshot)` the default backlog query.

**Commands**:
```bash
# Edit AGENTS.md Notion Workspace Map block
# Edit .cursor/skills/writeback-discipline/SKILL.md templates
python .cursor/scripts/sync_mcp_config.py  # regenerates Quick Reference if needed
```

**Acceptance**: "query notion backlog" in a fresh chat completes with 1 MCP call, ≤2KB response.

### Phase W6 — Legacy Cleanup

**Scope**: Archive `Priority` number property (not delete — preserves history); rename DB.

**Acceptance**: DB named `Backlog Items`; `Priority` no longer visible in default view.

---

## Rules

- No deletion of existing Notion data at any wave; additive and copy-forward only until W6.
- Each wave commits atomically; rollback is revert-last-commit + revert-schema via Notion history.
- Hook changes must preserve `DEFERRED_SCOPE:` marker contract (constitutional §24).
- Snapshot regeneration is best-effort; hook failures must fail-open (exit 0) and log to `artifacts/cursor/notion_snapshot_errors.jsonl`.
- No `pytest.mark.skip` on any new migration or snapshot tests.
- All subprocess calls in migration scripts: `subprocess.run(argv, shell=False, timeout=30)`.

---

## Success Criteria

- [ ] Typed fields (`P-Band`, `Impact Score`, `Layer`, `Surface`) populated on 100% of rows
- [ ] `Plans` DB exists with ≥ 20 plan rows and `Open Items` rollup working
- [ ] `Backlog Snapshot` page is Cursor Agent's new default for "query backlog"
- [ ] `query notion backlog` request resolves in 1 MCP call (down from 2 + client aggregation)
- [ ] Response payload for dashboard query ≤ 5KB (down from ~170KB)
- [ ] AGENTS.md Notion Workspace Map reflects new DB IDs and Snapshot page ID
- [ ] `post_cursor_agent_deferred_scope_capture.py` updated tests pass (`pytest tests/unit/ops_scripts/hooks/windsurf/test_post_cursor_agent_deferred_scope_capture.py`)
- [ ] No regression in DEFERRED_SCOPE marker contract (existing regression tests pass)
- [ ] Legacy `Priority` number field archived (not deleted) after 1-week bake
- [ ] DB renamed to `Backlog Items` in Notion UI

---

## Implementation Commands

```bash
# W1 — Schema additive (manual Notion UI or API-update-a-data-source)
# W2 — Backfill
python tools/migration/notion_backfill_typed_fields.py --dry-run
python tools/migration/notion_backfill_typed_fields.py --execute

# W3 — Plans DB
python tools/migration/notion_create_plans_db.py
python tools/migration/notion_backfill_plan_relations.py --execute

# W4 — Snapshot
python tools/notion/snapshot_renderer.py --create-page
python tools/notion/snapshot_renderer.py --regenerate  # test manually once

# W5 — Consumer switchover (file edits, no runtime commands)

# W6 — After 1-week bake: archive Priority, rename DB (manual Notion UI)
```

---

## Rollback Strategy

**Per-wave rollback (applies to any wave):**
1. Revert the commit for that wave (`git revert <sha>`).
2. For schema additions: new properties are additive — simply leave them unused, or delete via Notion UI (does not affect existing Priority/prose data).
3. For backfill writes: the legacy `Priority` number field and prose `Blocking Items` are never modified, so consumers fall back automatically.
4. For W5 consumer switchover: revert `AGENTS.md` block; Cursor Agent reverts to paginated query.
5. For W6 rename: rename back via Notion UI; unarchive `Priority` from archived-properties.

**Nuclear rollback (worst case):**
- All typed data is a projection of data still present in `[Pn]` title prefix + `Blocking Items` prose.
- Deleting the new typed properties, the `Plans` DB, and the `Snapshot` page returns the system to exact current state.
- Zero data loss possible at any point.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Rows with typed `P-Band` | 100% (155/155) | `API-query-data-source` filter `P-Band: is_empty` → 0 results |
| Rows with typed `Impact Score` (auto-captured rows only) | 100% of 33 scored rows | filter `Impact Score: is_empty AND Plan contains DEFERRED_SCOPE` → 0 |
| Unique `Plans` rows | ≥ 20 | `API-query-data-source(Plans)` count |
| Snapshot page payload size | ≤ 5 KB | `retrieve-a-page` response byte count |
| Default backlog query API call count | 1 | manual Cursor Agent trace in fresh session |
| Existing DEFERRED_SCOPE tests | all pass | `pytest tests/unit/ops_scripts/hooks/windsurf/ -v -k deferred_scope` |
| Hook-added regression test for snapshot | pass | new `test_snapshot_renderer.py` |

## Cursor Agent Alignment Checks

- Keep always-on rules lean; this plan's operational detail lives in the plan file, not in rules.
- Retrieve local scoped evidence (existing row sample) before building backfill parsers.
- Prefer exact structural matches (regex for `[Pn]` + impact) before fuzzy approaches.
- For migration writes, extract and log every original value before overwrite.
- Deterministic enforcement (backfill idempotency, snapshot throttle) lives in scripts, not template prose.
