---
trigger: always_on
---


> **Cascade always-on discipline:** Keep this file lean and invariant-focused. Put durable boundaries here; procedures and examples belong in skills or workflows.
>
> **Cascade enforcement split:** Advisory guidance lives here; deterministic detection lives in `post_cascade_grep_budget_audit.py` (text-search budget) and `post_cascade_scope_drift_detector.py` (future).

# Scope Containment — No Gold-Plating, One Task At A Time

> ⛔ **The scope of the current response is exactly: (a) what the user just asked for, plus (b) files named in the active plan's `Files In Scope`, plus (c) files required to satisfy (a) and (b) transitively. Nothing else.**

Sibling to constitutional §18 (no hidden scope expansion). That rule says "don't widen scope"; this one operationalizes it.

## The Four Hard Rules

1. **No gold-plating.** Do not improve code Cascade "noticed needed improving" while working on something else. File a `NEXT_STEP:` marker; move on.
2. **No "while I'm here" edits.** Touching an unrelated file because it happens to be open or in a nearby directory is scope expansion — forbidden without explicit user approval in the current turn.
3. **One active task at a time.** If the user asks for X, do X. Do not start Y because Y "also needs doing". Concurrent task scopes require an explicit user turn that lists both.
4. **Improvements outside scope → `NEXT_STEP:` marker, not an edit.** Per `.windsurf/rules/next-step-capture.md`, emit the marker in the same response; let the hook auto-capture it; DO NOT implement.

## What Counts As In Scope

In scope for the current response:

- Files the user named in their latest message (by path, `@` mention, or quoted snippet)
- Files listed in the active plan's `Files In Scope` / `## Phase-Level Summary · Scope (files)` column
- Files required to make (a) and (b) compile, type-check, or pass their existing tests
- Test files that cover the above (per testing-framework skill)

Out of scope by default:

- Files Cascade discovered via `grep_search` or `code_search` that are not in the above set — these can be *read* for context, never edited
- Unrelated anti-pattern cleanups, lint fixes, or formatting touches
- Documentation / README updates unless the user asked or the plan names them
- New tests for code paths outside the active scope

## Retrieval Discipline

- Prefer **reading named files** over searching. If the plan names the files, read them directly; do not grep "to be sure".
- **Cap text-search invocations per response at 3** (combined `grep_search` + `code_search`). Over the cap is logged by `post_cascade_grep_budget_audit.py`. If a task genuinely needs more than 3, use ADG MCP (`adg_sqlite`) — it answers dependency questions with one structured call instead of N text shots.
- **ADG for dependency questions** (constitutional §28): never grep for "who imports X", "what depends on Y", "where is Z used". Use `adg_edge_fanin` / `adg_edge_fanout` / direct SQLite. Same rule, restated here because it is the #1 cause of "reviewing entire codebase every run".

## Forbidden Patterns

- ❌ "I also noticed that X could be improved, so I fixed it too." — this is gold-plating.
- ❌ A single response that edits files across 3+ modules the user did not mention.
- ❌ Starting a new plan, task, or refactor mid-response because the current work "reminded me" of another issue.
- ❌ Running `grep_search` more than 3 times in one response without a matching `adg_*` or ADG-SQLite direct-read attempt first.
- ❌ Renaming, moving, or deleting files that are not in the active scope — even if the filename looks obviously wrong.

## Escape Hatches

- **User explicitly approved expansion** in the current turn (e.g., "yes, also fix the related bug in module Y") — the approval is the scope extension; proceed.
- **Transitive requirement** — an in-scope edit forces an out-of-scope file to change (e.g., updating an import signature). State the requirement inline before editing.
- **Emergency rollback** — constitutional §7 auto-closure path; operational bypass.
- **`SCOPE_CONTAINMENT_BYPASS=1`** env var — logs a bypass row; use only for scripted batch runs or acknowledged exploratory sessions.

## Enforcement

1. **This rule** (always_on — advisory) shapes composition every turn.
2. **`post_cascade_grep_budget_audit.py`** — post-response audit, ≤3 text-search calls per response; logs to `artifacts/windsurf/grep_budget_violations.jsonl`.
3. **`.codeiumignore`** — shrinks the indexing surface so `archives/`, `artifacts/`, `reports/`, `data/` don't show up in Fast Context results and pull the agent's attention out of scope.
4. **`NEXT_STEP:` marker** (sibling rule `next-step-capture.md`) — the relief valve for "I noticed something else" — captures it to backlog instead of widening the current scope.

## References

- Constitutional §18 (no hidden scope expansion), §28 (ADG over grep), §31 (SSOT folder routing)
- `next-step-capture.md` — where out-of-scope ideas go
- `deferred-scope-capture.md` — where descoped wave work goes
- `global_rules.md` ADG-First Retrieval-Tool Decision Tree
- Web research: Cursor agent best practices, Augment harness engineering, Anthropic skill authoring — all converge on "feed less, more precisely; reject out-of-task work"
