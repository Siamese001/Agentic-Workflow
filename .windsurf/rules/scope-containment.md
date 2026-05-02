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
- **Cap file-read invocations per response at 10** (combined native `read_file`, `read_notebook`, `read_url_content`, and MCP `read_text_file` / `read_file` / `read_multiple_files`). Over the cap is logged by `post_cascade_read_budget_audit.py`. Bypass: `READ_BUDGET_BYPASS=1`.
- **ADG for dependency questions** (constitutional §28): never grep for "who imports X", "what depends on Y", "where is Z used". Use `adg_edge_fanin` / `adg_edge_fanout` / direct SQLite. Same rule, restated here because it is the #1 cause of "reviewing entire codebase every run".

## Scope-Reset Marker (Cross-Turn Topic Transitions)

When the user's new message clearly shifts to a different module/layer/concern than the prior turn, Cascade MUST emit a `SCOPE_RESET:` marker before any tool call in the response.

Marker shape:
```
SCOPE_RESET: from=<prior-scope-summary> to=<new-scope-summary> dropped=<comma-separated-files-or-topics>
```

Heuristics that trigger the marker (any one is sufficient):

- The user names files under a different top-level directory (e.g., `apps_eval/` → `agentic_core/L0_routing/`)
- The user names a different layer (`L0` → `L4`) or different app (`apps_qna` → `apps_rg`)
- The user opens a new task type (refactoring → debugging → planning) on different code
- The user explicitly says "new task", "switch to", "different question"

Do NOT emit `SCOPE_RESET:` for natural continuations of the same task (e.g., "now W2", "verify that", "fix the typo") — those inherit prior scope.

Effect: the marker is the explicit hand-off. Files / context referenced in the previous turn but not named in the new turn are dropped from active reasoning. If the new task genuinely needs old context, the user will re-mention it or the active plan will list it.

Example:
```
SCOPE_RESET: from=W3-trim-always-on-rules to=apps_qna-pack-builder-bug dropped=.windsurf/rules/*.md, ops_scripts/ci/check_always_on_token_budget.py
```

## Summarize-Before-Return (Discarding Search Chunks)

After any `code_search` or multi-file `grep_search` returns results, Cascade MUST state which paths it retains for active reasoning and explicitly discard the chunk contents before continuing.

Required composition pattern:
```
[After code_search] Retained: <path1>, <path2>. Discarded: chunk contents (will read targeted files if needed).
```

Why: `code_search` returns scored chunks of file contents. Holding all chunk text in active reasoning across N more tool calls is exactly the "ingest whole repo" failure mode this rule exists to prevent. The chunks served their purpose (locating relevant files); the file paths are the durable artifact.

This is a behavioral rule with no hook enforcement — relies on Cascade composition discipline. The `code_search` return is in tool-result history regardless; the discipline is to NOT re-reason over its bulk contents in subsequent steps.

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
2. **`post_cascade_grep_budget_audit.py`** — ≤3 text-search calls per response; logs to `artifacts/windsurf/grep_budget_violations.jsonl`.
3. **`post_cascade_read_budget_audit.py`** — ≤10 file-read calls per response; logs to `artifacts/windsurf/read_budget_violations.jsonl`.
4. **`post_cascade_token_telemetry.py`** — per-turn approximate token-burn telemetry; logs to `artifacts/windsurf/turn_budget.jsonl`; weekly rollup via `ops_scripts/calibration/token_burn_weekly_report.py`.
5. **`.codeiumignore`** — shrinks the indexing surface so `archives/`, `artifacts/`, `reports/`, `data/` don't show up in Fast Context results and pull the agent's attention out of scope.
6. **`NEXT_STEP:` marker** (sibling rule `next-step-capture.md`) — the relief valve for "I noticed something else" — captures it to backlog instead of widening the current scope.
7. **`SCOPE_RESET:` marker** (this rule, §Scope-Reset Marker) — explicit topic-transition hand-off; drops prior-turn context that the new task does not need.

## References

- Constitutional §18 (no hidden scope expansion), §28 (ADG over grep), §31 (SSOT folder routing)
- `next-step-capture.md` — where out-of-scope ideas go
- `deferred-scope-capture.md` — where descoped wave work goes
- `global_rules.md` ADG-First Retrieval-Tool Decision Tree
- Web research: Cursor agent best practices, Augment harness engineering, Anthropic skill authoring — all converge on "feed less, more precisely; reject out-of-task work"
