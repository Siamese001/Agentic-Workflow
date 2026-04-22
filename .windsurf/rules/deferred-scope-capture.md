---
trigger: always_on
---

# Deferred Scope Capture — Durable Cross-Session Persistence

> **Cascade always-on discipline:** Keep this file lean and invariant-focused. Full procedure lives in the `deferred-scope-capture` skill and the hook scripts; this rule states the invariants and the marker contract.
>
> **Cascade enforcement split:** Advisory guidance lives here; deterministic capture + auto-post runs in `.windsurf/scripts/post_cascade_deferred_scope_capture.py`.

# The Invariant

> ⛔ **Every deferred scope item MUST be captured to Notion with a computed priority within the same response that introduces it.** No exceptions. Self-reported "added to backlog" prose without a DEFERRED_SCOPE marker is a constitutional violation.

This rule exists because 2026-04-22 session surfaced 5 distinct failure modes:
1. Cascade mentioned deferred work in prose → nothing written to Notion
2. Notion rows posted without matching plan file on disk (orphan rows)
3. Memory entities created with wrong `entityType="general"` → auto-purged at 30 days
4. Duplicate rows posted by subsequent sessions (no dedup check)
5. Rows misrouted to sentinel plan-file names instead of real plans

## The DEFERRED_SCOPE Marker (contract)

When Cascade introduces a deferred scope item, it MUST emit a **plain-text marker line** in the response, in this format:

```
DEFERRED_SCOPE: plan=<plan-slug> wave=<wave_id> phase=<phase_id> layer=<L0..L6|L_*> fan_in=<N> surface=<Execution|Write|Security|State|Observability|None> coverage_gap_pct=<N.N> est_tokens=<N> reason=<short>
```

**Placement rules**:
- Plain text only (no backticks, no code fence)
- Own line
- MUST appear before any Notion `API-post-page` call for that scope
- One marker per deferred item (N items = N markers)

**Field requirements**:

| Field | Values | Example |
|---|---|---|
| `plan` | existing plan slug in `.windsurf/plans/` or `NEW:<slug>` if creating | `test-coverage-backlog-f8f5a7` |
| `wave` | Wave ID (existing pattern) | `D1b`, `F4`, `W2-P1` |
| `phase` | Phase ID (existing pattern) | `D1b.1`, `F4.2`, `P1` |
| `layer` | L0..L6 or L_APP, L_OPS, L_TOOLS, L_SHARED, etc. | `L5` |
| `fan_in` | integer from ADG `adg_edge_fanin` query | `12` |
| `surface` | one of 5 ADG surfaces or `None` | `Security` |
| `coverage_gap_pct` | % untested (0.0-100.0) | `85.4` |
| `est_tokens` | token estimate | `12000` |
| `reason` | 5-10 word summary | `L5 enforcement gates coverage` |

## The Priority Formula (auto-computed — no human argument)

The post-hook computes priority band P1..P5 deterministically:

```
impact = coverage_gap_pct × layer_multiplier × (1 + log10(1 + fan_in)) × surface_boost

layer_multiplier:  L0=2.0, L5=2.0, L3=1.75, L4=1.75, L1=1.0, L2=1.0, L6=0.75, others=1.0
surface_boost:     Security=1.5, Write=1.4, Execution=1.3, State=1.2, Observability=1.1, None=1.0
```

Bands:
| Band | Impact range |
|---|---|
| **P1** | impact ≥ 300 |
| **P2** | impact ≥ 150 |
| **P3** | impact ≥ 75 |
| **P4** | impact ≥ 30 |
| **P5** | impact < 30 |

SSOT: `tools/priority/deferred_scope_scorer.py`. Do NOT hand-assign priority bands; let the scorer decide.

## Auto-Capture Flow (what the hook does)

`.windsurf/scripts/post_cascade_deferred_scope_capture.py` runs on every Cascade response:

1. **Parse** all `DEFERRED_SCOPE:` markers in the response
2. **Validate** each marker has all required fields (malformed → log violation, skip)
3. **Score** using `deferred_scope_scorer.py` → P-band
4. **Check** whether a matching Notion `API-post-page` occurred in same response (via `WRITEBACK:` receipt)
5. **If missing**: auto-POST to Wave/Phase Convergence DB (`aa8d2507-101e-4384-81d9-60ea3fe33876`) with computed priority prefix `[Pn]` in Phase Title and all 9 enriched fields
6. **Log**: every marker + action to `artifacts/windsurf/deferred_scope_capture.jsonl`

## Required Writeback Fields (auto-populated by hook)

When auto-posting, the hook fills ALL 9 Wave/Phase Convergence enriched fields:

```
Phase Title       = "[P{band}] {wave} {phase} — {reason}"
Phase ID          = {phase}
Wave ID           = {wave}
Sub-Wave          = "{wave}-{band}-AUTO" (AUTO suffix marks hook-posted rows)
Dependencies      = "Auto-captured from DEFERRED_SCOPE marker. Review before execution."
Success Criteria  = "See Blocking Items for scope; Cascade to fill on execution start."
Files In Scope    = "TBD — Cascade to fill on execution start."
Parent Plan Summary = "{plan}: deferred scope auto-captured {UTC_DATE}."
Plan File         = "{plan}.md" (resolved to 6hex if NEW:)
Status            = "Todo"
Est Tokens        = {est_tokens}
Blocking Items    = "{reason}. Layer={layer}, fan_in={fan_in}, surface={surface}, coverage_gap_pct={coverage_gap_pct}. Priority impact score: {impact_score}."
```

## Forbidden Patterns

- ❌ Prose-only deferred scope mentions ("this could be a future task", "deferred to next session") without a DEFERRED_SCOPE marker
- ❌ Hand-assigned priority (`[P2]` chosen by Cascade rather than scorer)
- ❌ Writing to a sentinel plan-file name like `(infrastructure — no dedicated plan file...)` instead of a real or `NEW:` plan slug
- ❌ Creating memory entity without `entityType=ProceduralPattern` (or other protected type) — auto-purge trap
- ❌ Silent duplicate posts — hook dedupes by (plan, wave, phase) tuple before posting

## Escape Hatch

`DEFERRED_SCOPE_CAPTURE_BYPASS=1` environment variable — logs a bypass row and skips auto-post. Use only for scripted batch runs or acknowledged exploratory sessions.

## Enforcement Layers

1. **This rule** (always_on — advisory) tells Cascade the invariant
2. **`.windsurf/scripts/post_cascade_deferred_scope_capture.py`** (post_cascade_response hook — deterministic)
3. **`tools/priority/deferred_scope_scorer.py`** (priority SSOT)
4. **`tools/reports/audit_notion_backlog_coverage.py`** (session-start reconciliation)
5. **Memory entity `ProceduralPattern:DeferredScopeCaptureProtocol`** (cross-session recall)

## References

- Format precedent: `DECISION_CAPTURED:` in `author-gate-enforcement.md`
- Writeback discipline: `memory-notion-writeback.md`
- ADG layer multipliers: `adg-canonical-invariants.md` §6
- Notion schema: AGENTS.md §Notion Workspace Map
