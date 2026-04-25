---
trigger: always_on
---

# Next-Step Capture — Suggested Follow-Ups Become Durable Backlog

> ⛔ **When Cascade suggests a next step, it MUST emit a `NEXT_STEP:` marker
> in the same response.** Prose-only "could do later" language is a
> constitutional violation (§24-bis), because such suggestions historically
> vanish between sessions.

## Why this exists

Sibling rule to `deferred-scope-capture.md`. That rule handles **scoped
deferrals from refactoring waves** (carries ADG impact measurement). This
rule handles **voluntary follow-up suggestions** — optional polish, nice-to-
have hardening, "consider X" recommendations — that Cascade surfaces at the
end of a response.

The two differ in intent:

| Concern | `DEFERRED_SCOPE` | `NEXT_STEP` |
|---|---|---|
| Origin | Wave/phase execution descoped something | Cascade suggests polish / followup |
| Measurement | Full ADG impact (layer, fan_in, surface, coverage_gap_pct) | Self-reported priority (P2..P5) |
| P-band source | `deferred_scope_scorer.py` (computed) | Author-declared (`priority=P4` etc.) |
| Default target | Wave/Phase Convergence — `[Pn]` prefix | Wave/Phase Convergence — `[NEXT·Pn]` prefix |
| Failure mode | Scope loss across sessions | Follow-up amnesia |

Both are auto-posted to Notion and optionally auto-scaffold a plan file.

## The NEXT_STEP Marker (contract)

When Cascade suggests a follow-up action, it MUST emit a plain-text marker
line in the same response, in this format:

```
NEXT_STEP: plan=<plan-slug-or-NEW:slug> title=<short> priority=<P2..P5> est_tokens=<N> reason=<why>
```

**Placement rules** (identical to DEFERRED_SCOPE):
- Plain text only (no backticks, no code fence)
- Own line
- Can appear anywhere in the response — before or after a Notion call
- One marker per follow-up item

**Field requirements**:

| Field | Values | Required | Example |
|---|---|:---:|---|
| `plan` | existing plan slug, or `NEW:<slug>` if creating | ✅ | `NEW:ci-workflow-hardening` |
| `title` | short descriptor (≤60 chars, no commas) | ✅ | `Add GH Actions nightly run` |
| `priority` | `P2`, `P3`, `P4`, or `P5` | ✅ | `P3` |
| `est_tokens` | integer sizing estimate | ✅ | `8000` |
| `reason` | one-line rationale (may contain spaces) | ✅ | `Nightly catches orphans earlier than weekly` |
| `wave` | Wave ID (default: `W-NEXT`) | ⬜ | `W-NEXT` |
| `phase` | Phase ID (default: `NEXT-<sha8>`) | ⬜ | `NEXT-a1b2c3d4` |
| `depends_on` | comma-free ID list (`other-slug; other-slug2`) | ⬜ | `system-learning-waves-7b3c91` |

`priority` is the author-declared P-band. It does NOT pass through the
DEFERRED_SCOPE scorer — next steps are self-sized.

## Auto-Capture Flow (what the hook does)

`.windsurf/scripts/post_cascade_next_step_capture.py` runs on every Cascade
response:

1. **Parse** all `NEXT_STEP:` markers in the response
2. **Validate** required fields (malformed → log violation, skip)
3. **Scaffold plan file** when the marker uses `plan=NEW:<slug>` via the
   shared `_deferred_scope_plan_scaffold.scaffold_plan_if_needed()`
4. **Dedupe** against local log (7-day window) and Notion (authoritative)
5. **Auto-POST** to Wave/Phase Convergence DB with `[NEXT·P{n}]` Phase Title
   prefix, Sub-Wave suffix `-NEXT-AUTO`, and the 9 enriched fields
6. **Log** every marker + action to
   `artifacts/windsurf/next_step_capture.jsonl`

## Required Writeback Fields (auto-populated)

```
Phase Title       = "[NEXT·{priority}] {title}"
Phase ID          = {phase or "NEXT-<sha8>"}
Wave ID           = {wave or "W-NEXT"}
Sub-Wave          = "{wave}-{priority}-NEXT-AUTO"
Dependencies      = "{depends_on or 'none declared'}"
Success Criteria  = "TBD — Cascade suggested follow-up."
Files In Scope    = "TBD — Cascade to fill on execution start."
Parent Plan Summary = "{plan_file}: NEXT_STEP auto-captured {UTC_DATE} via post_cascade hook."
Plan File         = "{plan_file}" (resolved to 6hex if NEW:)
Status            = "Todo"
Est Tokens        = {est_tokens}
Blocking Items    = "{reason}. Priority={priority}. Auto-captured from NEXT_STEP marker."
P-Band            = {priority}
Impact Score      = 0.0 (next-step markers do not pass through the scorer)
```

## Forbidden Patterns

- ❌ Prose "optional follow-up" mentions without a `NEXT_STEP:` marker
- ❌ `priority=P1` — P1 is reserved for scored DEFERRED_SCOPE items
- ❌ `priority=P1|critical|blocker` — values outside `{P2, P3, P4, P5}`
- ❌ Writing "TBD" in the `title` field — each NEXT_STEP must have a concrete title
- ❌ Sentinel plan names like `(no plan)` or `TBD` — use `NEW:<slug>` if creating

## When NOT to emit a NEXT_STEP

- Work in the CURRENT scope of the current plan — that's current work, not a follow-up
- Work formally DEFERRED during a wave — use `DEFERRED_SCOPE:` instead
- Hypothetical musings ("one could imagine a system that...") — those are not backlog items
- Documentation-only cleanup with no clear downstream value

## Escape Hatch

`NEXT_STEP_CAPTURE_BYPASS=1` environment variable — logs a bypass row and
skips auto-post. Use only for scripted batch runs or acknowledged
exploratory sessions where Cascade is brainstorming at scale.

## Enforcement Layers

1. **This rule** (always_on — advisory) tells Cascade the invariant
2. **`.windsurf/scripts/post_cascade_next_step_capture.py`** (post_cascade_response hook — deterministic)
3. **`.windsurf/scripts/_deferred_scope_plan_scaffold.py`** (shared with DEFERRED_SCOPE — auto-creates plan file on `NEW:<slug>`)
4. **`ops_scripts/ci/check_notion_plan_file_drift.py`** (manual-stage CI gate — catches orphan Notion rows from either marker class)

## References

- Sibling: `deferred-scope-capture.md` (scored deferrals)
- Plan SSOT location: `.windsurf/rules/plan-location.md`
- Writeback discipline: `memory-notion-writeback.md`
- Notion schema: AGENTS.md §Notion Workspace Map
