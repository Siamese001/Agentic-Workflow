
<!-- Converted from `.claude/rules/notion-plans-taxonomy.md`. Original Cursor trigger: `model_decision`. -->

# Notion Plans + Backlog Items — Status Taxonomy and Snapshot Read Path

> Extracted from AGENTS.md 2026-05-02 to reduce always-loaded content. Invariants unchanged; only location moved.

## Plans DB Status Taxonomy (canonical)

> 🔴 **SSOT (2026-06-08): the live Plans DB has exactly FIVE Status options —**
> `In Progress`, `Not Started`, `Completed`, `Retired`, `Archived`. **`Lower Priority` and `Waiting`
> were retired** (they were never created in the live data source; writing them would make Notion
> silently auto-create polluting options). They are now **stale-coerced → `In Progress` and
> forbidden** at the code SSOT `.claude/governance/scripts/_notion_plans_status_check.py`
> (`CANONICAL_STATUSES` / `ACTIVE_STATUSES` / `TERMINAL_STATUSES` / `STALE_EQUIVALENTS` /
> `FORBIDDEN_PLANS_STATUSES`), with `_notion_canonical.py` + `_plan_lifecycle.PlanStatus` deriving
> from it and `tests/unit/windsurf_scripts/test_notion_status_ssot_consistency.py` enforcing it.
> **Any content below that references `Lower Priority`/`Waiting` (the 7-row table, transition matrix,
> Waiting-For invariants DS-2/DS-3/NP10, time-rules T2/T5) is SUPERSEDED** — retained only as
> historical context pending a full doc rewrite.

> ⛔ **CANONICAL Status option strings — pass these EXACT plain-word values to the Notion API.** Emoji glyphs elsewhere in this rule are display mnemonics for human readers, NEVER literal API values.

| Canonical Name | API-literal | Meaning | Required Conditions |
|---|---|---|---|
| `In Progress` | `{"select": {"name": "In Progress"}}` | green — someone is working on this right now | File exists on disk · edited within last 14 days · has wave/phase work in progress |
| `Not Started` | `{"select": {"name": "Not Started"}}` | gray — written, not started | File exists on disk · no execution work yet |
| `Lower Priority` | `{"select": {"name": "Lower Priority"}}` | yellow — paused or lower priority | File exists on disk · work intentionally suspended · may resume later |
| `Waiting` | `{"select": {"name": "Waiting"}}` | orange — blocked on external dependency | File exists on disk · blocked on upstream (person, system, decision) |
| `Completed` | `{"select": {"name": "Completed"}}` | blue — work landed | All waves/phases done · audit trail kept |
| `Retired` | `{"select": {"name": "Retired"}}` | purple — no longer relevant | Replaced by another plan, OR stale-by-design, OR work obsolete, OR file gone from disk — specific reason in Summary field |
| `Archived` | `{"select": {"name": "Archived"}}` | gray — hidden from views | Reserved — not for routine use |

**Any other Status value is forbidden.** Notion Select fields silently auto-create unknown option names — writing an unknown value does NOT error, it pollutes the DB schema with a new duplicate option.

## Status Criteria and Transition Rules (Enforceable)

> Each status has **Entry Criteria** (when to enter), **Exit Criteria** (when to leave), **Required Fields**, and **Time-Based Rules**. Gates validate these automatically.

| Status | Color | Entry Criteria | Exit Criteria | Required Fields | Max Duration | Auto-Transition Trigger |
|--------|-------|----------------|---------------|-----------------|--------------|------------------------|
| **Not Started** | Gray | Plan file created on disk; no wave execution started | WAVE_START marker emitted OR manual status change to active work | `Slug`, `Plan File Path`, `Exists On Disk=true`, `AI Summary` | Indefinite (but 30d stale → review) | None (manual only) |
| **In Progress** | Green | WAVE_START marker emitted for any wave; OR explicit user start | WAVE_COMPLETE of final wave (→Completed) OR stall >14d (→Retired) OR explicit park (→Lower Priority/Waiting) | Same as Not Started + active wave logs | 14 days without edit | Auto-flip to `Retired` if file untouched >14d |
| **Lower Priority** | Yellow | Explicit decision to park active/pending work; work suspended intentionally | Resume work (→In Progress) OR obsolete (→Retired) | Same as Not Started + `Summary` must state resume condition | 30 days | Review at 30d; no auto-flip |
| **Waiting** | Orange | Blocked on external dependency (person, system, decision); OR waiting for time-bound trigger (date/event); OR waiting for other work to complete first (internal dependency) | Dependency resolved/time reached/work done (→In Progress) OR obsolete (→Retired) | Same as Not Started + `Waiting For` must name blocker or time/event | 14 days | Flag for review if `Waiting For` empty >7d |
| **Completed** | Blue | PLAN_COMPLETE marker emitted; all waves done; audit trail preserved | None (terminal state) | Same as Not Started + final wave log in Summary | N/A (terminal) | None |
| **Retired** | Purple | Long-term preservation of historical plans; not for routine use | None (terminal state) | `Exists On Disk` may be false; `Summary` must state preservation reason | N/A (terminal) | Manual only |
| **Archived** | Gray | Plan superseded by another; OR stale >14d with no activity; OR work obsolete; OR file deleted | None (terminal state) | Minimal; `Summary` may be empty | N/A (terminal) | Auto-flip from In Progress after 14d stale |

### Status Quick Reference (Condensed)

| Status | When to Use | Key Trigger | Required Field | Terminal? |
|--------|-------------|-------------|----------------|-----------|
| **Not Started** | Plan created, work not begun | PLAN_CREATED marker | `AI Summary` | No |
| **In Progress** | Active wave execution | WAVE_START marker | Wave logs | No |
| **Lower Priority** | Intentionally parked work | Explicit decision | Resume condition in `Summary` | No |
| **Waiting** | Blocked on external/internal dependency or time-bound | Blocker/time identified | `Waiting For` | No |
| **Completed** | All waves done, work landed | PLAN_COMPLETE marker | Final wave log | **Yes** |
| **Retired** | Long-term preservation | Manual curation | Preservation reason | **Yes** |
| **Archived** | Obsolete/superseded/stale | 14d stale auto-flip | Minimal fields | **Yes** |

### Transition Matrix (Valid Status Flows)

```
                    ┌─────────────┐
    ┌───────────────┤  Archived   │◄────────────────────────────┐
    │               │  (terminal) │                             │
    │               └─────────────┘                             │
    │                                                         │
    │   ┌─────────────┐    ┌─────────────┐   ┌─────────────┐   │
    └──►│  Not Started │───►│ In Progress │◄──┤  Waiting    │   │
        │             │    │             │   │  (blocked)  │   │
        │  (initial)  │◄───┤  (active)   │──►└─────────────┘   │
        └─────────────┘    │             │                      │
              │            └──────┬──────┘                      │
              │                   │                             │
              │     ┌─────────────┼─────────────┐               │
              │     ▼             ▼             ▼               │
              │ ┌─────────┐  ┌─────────┐   ┌──────────┐          │
              └►│Lower    │  │Completed│   │ Retired  │◄─────────┘
                │Priority │  │(terminal)    │(terminal)│
                │(parked)  │  └─────────┘   └──────────┘
                └────┬────┘
                     │
                     └──────────────────────► (resume → In Progress)
```

**Forbidden Transitions** (enforced by gates):
- `Completed` → anything (terminal)
- `Retired` → anything except `Archived` (terminal with one escape)
- `Archived` → anything (terminal)
- `Not Started` ← `Completed/Retired/Archived` (no regression from terminal)
- `In Progress` ← `Completed` (no regression)

### Field Requirements by Status (Gate-Enforced)

| Status | `Exists On Disk` | `AI Summary` | `Summary` non-empty | `Waiting For` | Max Word Count (AI Summary) |
|--------|------------------|--------------|---------------------|---------------|------------------------------|
| Not Started | `true` mandatory | mandatory | advisory | N/A | 15 (soft), 12 (target) |
| In Progress | `true` mandatory | mandatory | advisory | N/A | 15 (soft), 12 (target) |
| Lower Priority | `true` mandatory | mandatory | mandatory (resume condition) | N/A | 15 (soft), 12 (target) |
| Waiting | `true` mandatory | mandatory | advisory | mandatory | 15 (soft), 12 (target) |
| Completed | `true` advisory | advisory | advisory (wave logs auto-populated) | N/A | N/A |
| Retired | `true` or `false` | exempt | mandatory (reason for retirement) | N/A | N/A |
| Archived | `true` or `false` | exempt | exempt | N/A | N/A |

### Time-Based Enforcement Rules

| Rule ID | Condition | Action | Enforced By |
|---------|-----------|--------|-------------|
| T1 | `In Progress` + no file edit >14d | Auto-flip to `Retired` with reason "stale since YYYY-MM-DD" | `check_notion_plans_status_canonical.py --query-notion` |
| T2 | `Waiting` + empty `Waiting For` (immediate) | ERROR: populate blocker description before or with the status write | `check_notion_plans_waiting_for.py` (NP10) + `post_agent_notion_plans_status_audit.py` |
| T3 | `Lower Priority` >30d without resume | INFO: review for retirement | Advisory only (manual decision) |
| T4 | `Not Started` >30d without start | INFO: review for retirement | Advisory only |
| T5 | `In Progress` + deferred scope items >7d old + empty `Waiting For` | Recommend flip to `Waiting` | `check_notion_plans_status_canonical.py --query-notion` |

### Bypass / Emergency Override

All time-based flips can be suppressed with explicit marker in `Summary`:
- `[[bypass:T1]]` — blocks auto-retire for this plan
- `[[bypass:T2]]` — blocks Waiting-for-empty warning
- `[[bypass:T3]]` — blocks 30d Lower Priority review

Bypass expires after 14 days; must be renewed.

### Stale duplicate options (DO NOT USE)

Left over from migrations; live in the schema but must never be selected:

| Stale string | Stale id | Canonical replacement |
|---|---|---|
| `🟡Draft` (red) | `f5abd2a2-03bc-4951-9e38-ae9e1343909c` | `Not Started` |
| `🔵Completed` (pink) | `6da99522-3194-4aa3-aac4-44296b4048b7` | `Completed` |
| `Draft` (red, id `79d24503-da3e-4d22-a0fb-13a0c6d36d11`) | stale schema option | `Not Started` |
| `Live` (any) | stale schema option | `In Progress` |

> ⛔ **For NEW plans, ALWAYS use `Not Started`.** `Draft` is a stale red option that still exists in the Notion schema — Notion will silently accept it without error. It MUST NOT be used.

Incident precedent (2026-05-03): four per-app FEC producer plans posted with `🟡Draft`; patched to `Not Started`. Incident (2026-05-05): deferred E5 plan posted with `Draft`; patched to `Not Started`. Enforcement: plan `notion-plans-status-enforcement-7a1e2d` (helper `_notion_plans_status_check.py` + post-cursor_agent audit + CI drift gate NP2).

### Display mnemonic (for humans only)

When discussing statuses in prose or dashboards, the 🟢In Progress / ⚪Not Started / 🟡Lower Priority / 🟠Waiting / 🔵Completed / 🟣Retired / ⚪Archived glyph notation is a **display mnemonic** — convenient for eyeballing at a glance. These glyphs MUST NOT appear in any `API-post-page` / `API-patch-page` payload targeting the Plans or Backlog Items `Status` field.

**Schema note (2026-05-02)**: brown-colored duplicate `Completed` option was deleted via `API-update-a-data-source`. Desktop UI rename pass completed for both Plans and Backlog Items DBs: `Active`→`Live`, `Proposed`→`Draft`, `Complete`→`Completed`, `Superseded`→`Retired`. Option IDs preserved across rename (Notion UI rename ≠ API rename — API does not support it).

**Plans DB Invariants**:
- A row with `Status = In Progress` MUST have `Exists On Disk = true`
- A row with `Status = In Progress` MUST have been edited within the last 14 days (otherwise flip to `Retired` with reason "stale since YYYY-MM-DD")
- A row whose plan file was deleted from disk MUST have `Exists On Disk = false` AND `Status ∈ {Retired, Completed, Archived}`
- A plan that explicitly supersedes another **MUST** declare it via a `## Supersedes` table in the plan body (and/or a `supersedes: [<slug>, ...]` frontmatter list) — the canonical machine-readable trigger. Grammar:
  ```markdown
  ## Supersedes
  | Predecessor slug | Reason |
  |---|---|
  | <predecessor-slug> | <why this plan replaces it> |
  ```
  Declared predecessors are flipped to `Retired` automatically — with a dated `Summary` note **and** a posted Notion comment linking the successor — by the post-agent hook `post_agent_plan_supersession_retire.py`. The CI sweep gate `check_plan_supersession_consistency.py` (PLAN-SUPERSEDE) backstops cross-session/cross-worktree/Notion-only misses the live hook cannot observe. A net-new plan declares an empty section (`_None — net-new plan._`). Bypass: `PLAN_SUPERSESSION_RETIRE_BYPASS=1` (hook) / `PLAN_SUPERSESSION_GATE_BYPASS=1` (gate); enforce in CI via `PLAN_SUPERSESSION_GATE_FAIL_CLOSED=1`.
- **Mandatory `AI Summary` (added 2026-05-03)**: every Plans row with `Status ∈ {In Progress, Not Started, Lower Priority, Waiting, Completed}` MUST have a non-empty `AI Summary` property. Content MUST be **one single sentence, ≤ 12 words, scope + why-it-matters** — NOT bullet-style, NOT a prose recap of the `Summary` field. The DB grid shows only the first line; density per pixel is the goal. Examples: `"Completes apps_* spine migration; soak period before strict ADG certification flip."` (12 words), `"Turns ADG audit into two-stage certification so silent skips can't hide failures."` (12 words). Rows in `Retired`/`Archived` are exempt. Empty `AI Summary` is a reviewability violation — a reader scanning the DB learns nothing from a row without one. Enforcement: `ops_scripts/ci/check_notion_plans_ai_summary.py` checks presence (always) and ≤ 15-word length (advisory soft-cap on top of the 12-word target). Fail-closed via `NOTION_PLANS_AI_SUMMARY_FAIL_CLOSED=1`.

**Canonical Status option strings (updated 2026-05-10)**:
Option names are `In Progress`/`Not Started`/`Lower Priority`/`Waiting`/`Completed`/`Retired`/`Archived` (same option IDs as former `Live`/`Draft` — only display names changed). `Lower Priority` (formerly `Deprioritized` → `Deferred`, renamed 2026-05-10) is for paused/lower-priority work. The 🟢/🟡/🔵/🟣/⚪ notation in this rule is DISPLAY MNEMONIC — not literal option strings. When calling `API-post-page` / `API-patch-page`, pass `{"Status": {"select": {"name": "Not Started"}}}` — NEVER `"🟡Draft"` or `"Draft"`. The emoji-prefixed variants (`🟡Draft` red / `🔵Completed` pink) are STALE DUPLICATES and MUST NOT be selected. The old plain-word forms `Live` and `Draft` are also stale after the 2026-05-03 rename.

**Shared taxonomy — Backlog Items DB**: the same status names apply (In Progress/Not Started/Lower Priority/Waiting/Completed/Retired/Archived) for cross-DB consistency. However, Plans-specific invariants do NOT transfer:
- Backlog Items have no `Exists On Disk` field → on-disk-presence invariant is Plans-only
- Backlog items can legitimately sit in `Not Started` for months waiting on dependencies → 14-day staleness clock is Plans-only
- The "descope → Retired" flip applies to both DBs ✅

**Migration history (2026-05-02)**:
- 50 plans flipped Live → Retired in one session (Plans DB had become a graveyard with `Live` as default-and-never-decay)
- Schema rename pass on both Plans DB and Backlog Items DB: `Active`→`Live`, `Proposed`→`Draft`, `Complete`→`Completed`, `Superseded`→`Retired`; brown-colored `Completed` duplicate deleted on Plans DB
- 2026-05-03: `Live`→`In Progress`, `Draft`→`Not Started` (same option IDs, display names changed in Notion UI)
- 2026-05-05: `Deprioritized` added (later renamed)
- 2026-05-10: `Deprioritized` → `Deferred` → `Lower Priority` (UI rename, same option ID)
- **Forbidden legacy writes:** `Active`, `Deprioritized` — use `In Progress` / `Lower Priority`; `_notion_plans_status_check.py` blocks and maps via `STALE_EQUIVALENTS`
- 2026-05-10: `Deferred` → `Lower Priority` (UI rename, same option ID; legacy `Deferred` writes auto-mapped to `Lower Priority`)
- Higher-signal vocabulary chosen for outcome-orientation (`Completed` > `Complete`, `Retired` > `Superseded`)
- 14-day staleness clock + on-disk-presence invariant exists specifically to prevent the graveyard pattern recurring (Plans only)

## Backlog Snapshot — preferred read path (added 2026-04-23)

For any **dashboard / top-N / "what's the current state of the backlog"** question, prefer **one** `API-get-block-children` call on the Backlog Snapshot page over paginating Wave/Phase Convergence:

- **Page ID**: `34b27693-f55c-81b4-93ba-efec5755a20e`
- **Content**: top-25 open P1+P2 by Impact Score, band distribution, stale flags — pre-rendered markdown
- **Size**: ~5 KB vs. ~170 KB for full paginated query
- **Regenerate**: `python tools/notion/snapshot_renderer.py --regenerate` (~4 s, uses only the typed fields backfilled in W1/W2)

Use `API-query-data-source` on Wave/Phase Convergence only when you need a specific filter/sort not in the snapshot (e.g., all rows linked to a specific `Plan` relation).

## Status Canonical Enforcement (NP2)

**Gate**: `ops_scripts/ci/check_notion_plans_status_canonical.py`  
**Hook**: `pre_mcp_gate.py` validates `API-post-page`/`API-patch-page` payloads  
**Audit**: `post_agent_notion_status_audit.py` logs violations to `artifacts/governance/notion_status_violations.jsonl`

### Pre-MCP Validation

Before any Notion write, validate `Status.select.name` is in canonical set:

```python
CANONICAL_STATUSES = {
    "In Progress", "Not Started", "Lower Priority", "Waiting",
    "Completed", "Retired", "Archived"
}

if payload.get("Status", {}).get("select", {}).get("name") not in CANONICAL_STATUSES:
    raise ValueError(f"Status must be canonical. Got: {status}")
```

### Fail-Closed Mode

`NOTION_PLANS_STATUS_FAIL_CLOSED=1` → exit 1 on any stale status detection

### Incident History

- 2026-05-03: Four per-app FEC plans posted with `🟡Draft` → patched to `Not Started`
- 2026-05-05: Deferred E5 plan posted with `Draft` → patched to `Not Started`  
- 2026-05-06: repo-dedup-deferred-followup plan posted with `Draft` → patched to `Not Started`
- 2026-05-10: notion-plan-identity-deferred-scope plan created with `Deferred` → RCA, marker corrected, patched to `Not Started`

## New-Plan Status Enforcement (NP9)

**Rule**: New plans MUST use "Not Started", not "Lower Priority" or "Waiting".  
**Gate**: `ops_scripts/ci/check_notion_plans_new_status.py`  
**Detection**: Plans created within 24h with status != "Not Started"  

NP2 allows "Lower Priority" as canonical (for intentionally parked work), but NP9 enforces the semantic rule that **newly-created plans** must start at "Not Started". The 24h window allows intentional "Lower Priority" transitions on older plans while catching PLAN_CREATED marker errors.

### Bypass / Fail-Closed

- `NOTION_PLANS_NEW_STATUS_BYPASS=1` → skip check
- `NOTION_PLANS_NEW_STATUS_FAIL_CLOSED=1` → exit 1 on violations

## Waiting-For Completeness Enforcement (NP10)

**Rule**: Every Plans DB row with `Status = "Waiting"` MUST have a non-blank `Waiting For` property naming the specific blocker, person, system, decision, or time-bound trigger.

> ⛔ **Blank `Waiting For` on a `Waiting` plan is an ERROR.** A plan in Waiting state with no description of what it is waiting for is unactionable — no one can unblock it.

**Gate**: `ops_scripts/ci/check_notion_plans_waiting_for.py`  
**Audit (write-time)**: `post_agent_notion_plans_status_audit.py` — fires when a `Status=Waiting` write is detected in the Claude Code response without a corresponding `Waiting For` value in the same invoke body.

**Enforcement layers**:
1. **Write-time** — `post_agent_notion_plans_status_audit.py` logs `WAITING_EMPTY_WAITING_FOR` to `artifacts/governance/notion_plans_status_violations.jsonl` when Claude Code writes `Status=Waiting` without `Waiting For` in the same API call.
2. **Live-DB** — `check_notion_plans_waiting_for.py` queries Notion for all current `Waiting` rows and reports ERROR for any with blank `Waiting For`. Runs on `--query-notion` or standalone.
3. **CI gate NP10** — registered in `run_contract_gates.py` as advisory; flip fail-closed via `NOTION_PLANS_WAITING_FOR_FAIL_CLOSED=1`.

**Acceptable `Waiting For` values** (examples):
- `"ADR-085 approval from Amit"`
- `"Qwen 32B AWQ model reload after Docker restart"`
- `"apps_lic C0 FEC producer plan to complete first"`
- `"2026-06-01 — scheduled review date"`

**Unacceptable** (triggers violation):
- *(blank)*
- `"TBD"`
- `"unknown"`

### Bypass / Fail-Closed

- `NOTION_PLANS_WAITING_FOR_BYPASS=1` → skip NP10 gate entirely
- `NOTION_PLANS_WAITING_FOR_FAIL_CLOSED=1` → exit 1 on any ERROR

## References

- AGENTS.md Notion Workspace Map (auto-gen MCP/Notion registry table)
- `.claude/rules/plan-location.md` (Plans file system SSOT)
- `.claude/skills/notion/SKILL.md` (procedural Notion guidance)
- Plan `token-burn-followup-f8c2d1` §12.1 (this extraction)
- Gate: `ops_scripts/ci/check_notion_plans_status_canonical.py`
