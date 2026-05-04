---
trigger: model_decision
description: Use this rule when interacting with Notion Plans or Backlog Items databases — status field values, invariants for In Progress/Not Started/Completed/Retired/Archived, staleness rules, on-disk-presence checks, or when constructing a Backlog Snapshot read. Extracted from AGENTS.md 2026-05-02 per plan token-burn-followup-f8c2d1 deferred-scope item.
---

# Notion Plans + Backlog Items — Status Taxonomy and Snapshot Read Path

> Extracted from AGENTS.md 2026-05-02 to reduce always-loaded content. Invariants unchanged; only location moved.

## Plans DB Status Taxonomy (canonical)

> ⛔ **CANONICAL Status option strings — pass these EXACT plain-word values to the Notion API.** Emoji glyphs elsewhere in this rule are display mnemonics for human readers, NEVER literal API values.

| Canonical Name | API-literal | Meaning | Required Conditions |
|---|---|---|---|
| `In Progress` | `{"select": {"name": "In Progress"}}` | green — someone is working on this right now | File exists on disk · edited within last 14 days · has wave/phase work in progress |
| `Not Started` | `{"select": {"name": "Not Started"}}` | gray — written, not started | File exists on disk · no execution work yet |
| `Completed` | `{"select": {"name": "Completed"}}` | blue — work landed | All waves/phases done · audit trail kept |
| `Retired` | `{"select": {"name": "Retired"}}` | purple — no longer relevant | Replaced by another plan, OR stale-by-design, OR work obsolete, OR file gone from disk — specific reason in Summary field |
| `Archived` | `{"select": {"name": "Archived"}}` | gray — hidden from views | Reserved — not for routine use |

**Any other Status value is forbidden.** Notion Select fields silently auto-create unknown option names — writing an unknown value does NOT error, it pollutes the DB schema with a new duplicate option.

### Stale duplicate options (DO NOT USE)

Left over from migrations; live in the schema but must never be selected:

| Stale string | Stale id | Canonical replacement |
|---|---|---|
| `🟡Draft` (red) | `f5abd2a2-03bc-4951-9e38-ae9e1343909c` | `Not Started` |
| `🔵Completed` (pink) | `6da99522-3194-4aa3-aac4-44296b4048b7` | `Completed` |

Incident precedent (2026-05-03): four per-app FEC producer plans posted with `🟡Draft`; caught and patched to `Draft`. Enforcement now lives in plan `notion-plans-status-enforcement-7a1e2d` (helper + post-cascade audit + CI drift gate NP2).

### Display mnemonic (for humans only)

When discussing statuses in prose or dashboards, the 🟢In Progress / 🟡Not Started / 🔵Completed / 🟣Retired / ⚪Archived glyph notation is a **display mnemonic** — convenient for eyeballing at a glance. These glyphs MUST NOT appear in any `API-post-page` / `API-patch-page` payload targeting the Plans or Backlog Items `Status` field.

**Schema note (2026-05-02)**: brown-colored duplicate `Completed` option was deleted via `API-update-a-data-source`. Desktop UI rename pass completed for both Plans and Backlog Items DBs: `Active`→`Live`, `Proposed`→`Draft`, `Complete`→`Completed`, `Superseded`→`Retired`. Option IDs preserved across rename (Notion UI rename ≠ API rename — API does not support it).

**Plans DB Invariants**:
- A row with `Status = In Progress` MUST have `Exists On Disk = true`
- A row with `Status = In Progress` MUST have been edited within the last 14 days (otherwise flip to `Retired` with reason "stale since YYYY-MM-DD")
- A row whose plan file was deleted from disk MUST have `Exists On Disk = false` AND `Status ∈ {Retired, Completed, Archived}`
- A plan that explicitly supersedes another (via `Supersedes` table in plan body) flips the predecessor to `Retired` in the same response
- **Mandatory `AI Summary` (added 2026-05-03)**: every Plans row with `Status ∈ {In Progress, Not Started, Completed}` MUST have a non-empty `AI Summary` property. Content MUST be **one single sentence, ≤ 12 words, scope + why-it-matters** — NOT bullet-style, NOT a prose recap of the `Summary` field. The DB grid shows only the first line; density per pixel is the goal. Examples: `"Completes apps_* spine migration; soak period before strict ADG certification flip."` (12 words), `"Turns ADG audit into two-stage certification so silent skips can't hide failures."` (12 words). Rows in `Retired`/`Archived` are exempt. Empty `AI Summary` is a reviewability violation — a reader scanning the DB learns nothing from a row without one. Enforcement: `ops_scripts/ci/check_notion_plans_ai_summary.py` checks presence (always) and ≤ 15-word length (advisory soft-cap on top of the 12-word target). Fail-closed via `NOTION_PLANS_AI_SUMMARY_FAIL_CLOSED=1`.

**Canonical Status option strings (updated 2026-05-03)**:
Option names are `In Progress`/`Not Started`/`Waiting`/`Completed`/`Retired`/`Archived` (same option IDs as former `Live`/`Draft` — only display names changed). The 🟢/🟡/🔵/🟣/⚪ notation in this rule is DISPLAY MNEMONIC — not literal option strings. When calling `API-post-page` / `API-patch-page`, pass `{"Status": {"select": {"name": "Not Started"}}}` — NEVER `"🟡Draft"` or `"Draft"`. The emoji-prefixed variants (`🟡Draft` red / `🔵Completed` pink) are STALE DUPLICATES and MUST NOT be selected. The old plain-word forms `Live` and `Draft` are also stale after the 2026-05-03 rename.

**Shared taxonomy — Backlog Items DB**: the same status names apply (In Progress/Not Started/Completed/Retired/Archived) for cross-DB consistency. However, Plans-specific invariants do NOT transfer:
- Backlog Items have no `Exists On Disk` field → on-disk-presence invariant is Plans-only
- Backlog items can legitimately sit in `Not Started` for months waiting on dependencies → 14-day staleness clock is Plans-only
- The "descope → Retired" flip applies to both DBs ✅

**Migration history (2026-05-02)**:
- 50 plans flipped Live → Retired in one session (Plans DB had become a graveyard with `Live` as default-and-never-decay)
- Schema rename pass on both Plans DB and Backlog Items DB: `Active`→`Live`, `Proposed`→`Draft`, `Complete`→`Completed`, `Superseded`→`Retired`; brown-colored `Completed` duplicate deleted on Plans DB
- 2026-05-03: `Live`→`In Progress`, `Draft`→`Not Started` (same option IDs, display names changed in Notion UI)
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
