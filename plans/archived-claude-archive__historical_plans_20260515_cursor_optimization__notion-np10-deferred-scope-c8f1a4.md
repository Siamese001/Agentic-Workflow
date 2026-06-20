---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\notion-np10-deferred-scope-c8f1a4.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\notion-np10-deferred-scope-c8f1a4.md'
source_sha256: 032f411bb398e9a2a53ed0d4e69827c83021bbee4a67ad6fca7bf8d9fb2afbbe
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
slug: notion-np10-deferred-scope-c8f1a4
status: Not Started
dod_exempt: true
---

# NP10 Deferred Scope — Waiting-For Completeness Follow-On

## Context

Parent plan: `notion-np10-waiting-for-enforcement-b3d7c2` (Completed 2026-05-10).

This plan collects all items explicitly deferred from the parent plan's
Verification-vs-Deferral table, plus natural follow-on improvements identified
during implementation.

**Do not implement — planning artifact only.**

---

## Deferred Scope Items

### DS-1 — Auto-patch for blank Waiting For

**What**: When `post_cascade_notion_plans_status_audit.py` detects
`WAITING_EMPTY_WAITING_FOR` in a Cascade response, attempt an auto-PATCH to
prompt Cascade to re-issue the write with a populated value, similar to the
existing stale-status auto-patch logic (`_auto_patch_violation`).

**Why deferred**: Auto-patching `Waiting For` requires knowing *what* the
blocker actually is — unlike stale-status where the canonical replacement is
deterministic. Requires a second Cascade response or an interactive prompt.
The audit logging + advisory error is sufficient for the first version.

**Effort**: ~1k tokens. Complexity: low.

---

### DS-2 — TBD / "unknown" heuristic (weak Waiting For values)

**What**: Extend `decide_waiting_for()` (or add a sibling
`decide_waiting_for_quality()`) to flag known placeholder strings as
effectively-blank: `"TBD"`, `"tbd"`, `"unknown"`, `"Unknown"`, `"N/A"`,
`"n/a"`, `"?"`, `"pending"`.

**Why**: Rule prose lists these as unacceptable but the pure-logic helper
currently passes any non-empty string. A one-line check would close this gap.

**Effort**: ~300 tokens. Complexity: trivial.

**Suggested implementation**:
```python
_WEAK_WAITING_FOR: frozenset[str] = frozenset({
    "tbd", "unknown", "n/a", "?", "pending", "todo", "none",
})

def decide_waiting_for_quality(db_id, status_value, waiting_for_value):
    if decide_waiting_for(db_id, status_value, waiting_for_value) is not None:
        return None  # already caught as blank
    wf = (waiting_for_value or "").strip().lower()
    if wf in _WEAK_WAITING_FOR:
        return WaitingForViolation(...)
    return None
```

---

### DS-3 — Backlog Items DB parity

**What**: Apply the same `Waiting → non-blank Waiting For` rule to the
**Backlog Items DB** (`aa8d2507-101e-4384-81d9-60ea3fe33876` / data_source
`fc7f6bf4-6a73-43cd-a4e8-1ef23267dbe7`).

**Why deferred**: The Backlog Items DB shares the same Status taxonomy. Backlog
rows can also be set to `Waiting`. Currently only Plans DB is enforced.

**Effort**: ~1k tokens. Complexity: low — extend `_is_plans_surface` or add
a parallel `_is_backlog_surface` check; add a second `decide_waiting_for` call
in the audit; add a new CI gate `check_notion_backlog_waiting_for.py`.

---

### DS-4 — NP2 `--query-notion` deferred-age threshold for Waiting-without-Waiting-For

**What**: The existing T2 rule in `check_notion_plans_status_canonical.py`
previously flagged WARN after 7 days. It was updated to point at NP10.
However, the NP2 `--query-notion` live-DB check for `IN_PROGRESS_EMPTY_WAITING_FOR`
(plans that *should* flip to Waiting) still uses the 7-day threshold.

Consider adding a corresponding check: plans that *are* in Waiting with
empty Waiting For that were created/updated >N days ago should escalate
from ERROR to CRITICAL to force resolution.

**Effort**: ~500 tokens. Complexity: trivial (add age-based escalation in
`_check_waiting_for_completeness`).

---

### DS-5 — Notion UI reminder block on Waiting pages

**What**: When Cascade creates a new Plans DB row with `Status=Waiting`, append
a reminder block to the Notion page body:

> ⚠️ **This plan is Waiting.** Please populate the `Waiting For` property above
> with the specific blocker before leaving this page.

**Why**: Belt-and-braces for human editors working directly in Notion (not via
Cascade). The enforcement hooks only fire on Cascade writes.

**Effort**: ~600 tokens. Complexity: low — add `API-patch-block-children` call
in `_plan_registration.py` or `wave_execution_state.py` when status is Waiting.

---

### DS-6 — Tests for post-cascade audit Waiting-For detection

**What**: `post_cascade_notion_plans_status_audit.py` now has a
`WAITING_EMPTY_WAITING_FOR` code path in `detect_violations()` but there are
**no unit tests** for this specific path. Add test cases to
`tests/unit/windsurf_scripts/` (or extend the existing audit test file if one
exists) covering:

1. Invoke with `Status=Waiting` + absent `Waiting For` → violation
2. Invoke with `Status=Waiting` + populated `Waiting For` → no violation
3. Invoke with `Status=In Progress` + absent `Waiting For` → no violation (not applicable)
4. Invoke targeting non-Plans DB with `Status=Waiting` → no violation

**Effort**: ~600 tokens. Complexity: low.

---

### DS-7 — `check_notion_plans_waiting_for.py` pagination support

**What**: The current NP10 gate fetches `page_size=100` Waiting rows. If the
Plans DB ever has >100 Waiting rows simultaneously, results are silently
truncated.

Add cursor-based pagination loop using `has_more` + `next_cursor` from the
Notion query response.

**Effort**: ~400 tokens. Complexity: trivial.

---

## Wave Structure (placeholder — do not execute)

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | DS-2, DS-6 | Trivial quality + test gaps | ~1k | Not Started |
| W2 | DS-3, DS-7 | Backlog parity + pagination | ~1.5k | Not Started |
| W3 | DS-1, DS-4, DS-5 | Auto-patch, escalation, UI hint | ~2k | Not Started |

## Definition of Done (when this plan executes)

| # | Criterion |
|---|-----------|
| DoD-1 | All DS items listed above addressed or explicitly re-deferred with reason |
| DoD-2 | Tests for `post_cascade_notion_plans_status_audit.py` Waiting-For path green |
| DoD-3 | Backlog Items Waiting-For parity gate exits 0 against live DB |
| DoD-4 | `check_notion_plans_waiting_for.py` pagination handles >100 Waiting rows |
