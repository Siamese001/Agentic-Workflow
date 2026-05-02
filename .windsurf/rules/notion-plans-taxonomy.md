---
trigger: model_decision
description: Use this rule when interacting with Notion Plans or Backlog Items databases — status field values, invariants for Live/Draft/Completed/Retired/Archived, staleness rules, on-disk-presence checks, or when constructing a Backlog Snapshot read. Extracted from AGENTS.md 2026-05-02 per plan token-burn-followup-f8c2d1 deferred-scope item.
---

# Notion Plans + Backlog Items — Status Taxonomy and Snapshot Read Path

> Extracted from AGENTS.md 2026-05-02 to reduce always-loaded content. Invariants unchanged; only location moved.

## Plans DB Status Taxonomy (canonical)

The `Plans` data source uses the following 5-status taxonomy. Any other status value is forbidden.

| Status | Color | Meaning | Required Conditions |
|---|---|---|---|
| 🟢 **Live** | green | Someone is working on this right now | File exists on disk · edited within last 14 days · has wave/phase work in progress |
| 🟡 **Draft** | yellow | Written, not started | File exists on disk · no execution work yet |
| 🔵 **Completed** | blue | Work landed | All waves/phases done · audit trail kept |
| 🟣 **Retired** | purple | No longer relevant | Replaced by another plan, OR stale-by-design, OR work obsolete, OR file gone from disk — specific reason in Summary field |
| ⚪ **Archived** | gray | Hidden from views | Reserved — not for routine use |

**Schema note (2026-05-02)**: brown-colored duplicate `Completed` option was deleted via `API-update-a-data-source`. Desktop UI rename pass completed for both Plans and Backlog Items DBs: `Active`→`Live`, `Proposed`→`Draft`, `Complete`→`Completed`, `Superseded`→`Retired`. Option IDs preserved across rename (Notion UI rename ≠ API rename — API does not support it).

**Plans DB Invariants**:
- A row with `Status = Live` MUST have `Exists On Disk = true`
- A row with `Status = Live` MUST have been edited within the last 14 days (otherwise flip to `Retired` with reason "stale since YYYY-MM-DD")
- A row whose plan file was deleted from disk MUST have `Exists On Disk = false` AND `Status ∈ {Retired, Completed, Archived}`
- A plan that explicitly supersedes another (via `Supersedes` table in plan body) flips the predecessor to `Retired` in the same response

**Shared taxonomy — Backlog Items DB**: the same 5 status names apply (Live/Draft/Completed/Retired/Archived) for cross-DB consistency. However, Plans-specific invariants do NOT transfer:
- Backlog Items have no `Exists On Disk` field → on-disk-presence invariant is Plans-only
- Backlog items can legitimately sit in `Draft` for months waiting on dependencies → 14-day staleness clock is Plans-only
- The "descope → Retired" flip applies to both DBs ✅

**Migration history (2026-05-02)**:
- 50 plans flipped Live → Retired in one session (Plans DB had become a graveyard with `Live` as default-and-never-decay)
- Schema rename pass on both Plans DB and Backlog Items DB: `Active`→`Live`, `Proposed`→`Draft`, `Complete`→`Completed`, `Superseded`→`Retired`; brown-colored `Completed` duplicate deleted on Plans DB
- Higher-signal vocabulary chosen for outcome-orientation (`Completed` > `Complete`, `Retired` > `Superseded`)
- 14-day staleness clock + on-disk-presence invariant exists specifically to prevent the graveyard pattern recurring (Plans only)

## Backlog Snapshot — preferred read path (added 2026-04-23)

For any **dashboard / top-N / "what's the current state of the backlog"** question, prefer **one** `API-get-block-children` call on the Backlog Snapshot page over paginating Wave/Phase Convergence:

- **Page ID**: `34b27693-f55c-81b4-93ba-efec5755a20e`
- **Content**: top-25 open P1+P2 by Impact Score, band distribution, stale flags — pre-rendered markdown
- **Size**: ~5 KB vs. ~170 KB for full paginated query
- **Regenerate**: `python tools/notion/snapshot_renderer.py --regenerate` (~4 s, uses only the typed fields backfilled in W1/W2)

Use `API-query-data-source` on Wave/Phase Convergence only when you need a specific filter/sort not in the snapshot (e.g., all rows linked to a specific `Plan` relation).

## References

- AGENTS.md Notion Workspace Map (auto-gen MCP/Notion registry table)
- `.windsurf/rules/plan-location.md` (Plans file system SSOT)
- `.windsurf/skills/notion/SKILL.md` (procedural Notion guidance)
- Plan `token-burn-followup-f8c2d1` §12.1 (this extraction)
