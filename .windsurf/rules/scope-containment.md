---
trigger: always_on
---

# Scope Containment — No Gold-Plating, One Task At A Time

> ⛔ **Scope of the current response = (a) what the user asked for + (b) files in the active plan's `Files In Scope` + (c) files required to satisfy (a)+(b) transitively. Nothing else.**

Operationalizes constitutional §18 (no hidden scope expansion).

## The Four Hard Rules

1. **No gold-plating.** Don't improve code Cascade "noticed needed improving" while doing something else. File a `NEXT_STEP:` marker; move on.
2. **No "while I'm here" edits.** Touching an unrelated file because it's open / nearby = scope expansion — forbidden without explicit user approval this turn.
3. **One active task at a time.** Asked for X → do X. Don't start Y because Y "also needs doing". Concurrent scopes require an explicit user turn naming both.
4. **Out-of-scope improvements → `NEXT_STEP:` marker, NOT an edit.** Per `next-step-capture.md`, emit marker same response; hook auto-captures; DO NOT implement.

## In-Scope vs Out-of-Scope

**In scope**: files the user named (path / `@` mention / quoted snippet); files in plan `Files In Scope`; files required for (a)+(b) to compile / type-check / pass tests; tests covering the above.

**Out of scope by default**: files only discovered via `grep_search` / `code_search` (read-only context, never edit); unrelated anti-pattern / lint / formatting touches; doc / README updates unless requested; new tests for code paths outside active scope.

## Retrieval Discipline

- **Read named files; don't grep "to be sure".** Plan names files → read directly.
- **Text-search cap: 3/response** (`grep_search` + `code_search` combined). Audit: `post_cascade_grep_budget_audit.py`. Need more → use ADG MCP (one structured call, not N text shots).
- **File-read cap: 10/response** (native `read_file` / `read_notebook` / `read_url_content` + MCP `read_text_file` / `read_file` / `read_multiple_files`). Audit: `post_cascade_read_budget_audit.py`. Bypass: `READ_BUDGET_BYPASS=1`.
- **ADG > grep for dependencies** (constitutional §28). Never grep "who imports X / what depends on Y". Use `adg_edge_fanin` / `adg_edge_fanout` / direct SQLite.

## Scope-Reset Marker (Cross-Turn Topic Transitions)

When the user shifts to a different module/layer/concern from the prior turn, Cascade MUST emit before any tool call:

```
SCOPE_RESET: from=<prior-scope> to=<new-scope> dropped=<files-or-topics>
```

Triggers (any one): user names files in a different top-level dir; different layer (`L0`→`L4`) or app (`apps_qna`→`apps_rg`); different task type (refactor→debug→plan) on different code; explicit "new task" / "switch to" / "different question".

Do NOT emit for natural continuations ("now W2", "verify that", "fix the typo"). The marker drops prior-turn files from active reasoning; if old context is genuinely needed, the user re-mentions it or the active plan lists it.

## Summarize-Before-Return (Discarding Search Chunks)

After any `code_search` or multi-file `grep_search`, Cascade MUST state retained paths and discard chunk contents before continuing:

```
[After code_search] Retained: <path1>, <path2>. Discarded: chunk contents (will read targeted files if needed).
```

Chunks served their purpose (locating files); paths are the durable artifact. Re-reasoning over chunk bulk across N more tool calls is the "ingest whole repo" failure mode this rule prevents. Behavioral — no hook enforcement.

## Forbidden Patterns

- ❌ "I also noticed X could be improved, so I fixed it too" — gold-plating.
- ❌ Editing files across 3+ modules the user did not mention in one response.
- ❌ Starting a new plan/task/refactor mid-response because current work "reminded me".
- ❌ `grep_search` >3× without a matching `adg_*` or ADG-SQLite direct-read attempt first.
- ❌ Renaming / moving / deleting files outside active scope — even if the filename looks obviously wrong.

## Escape Hatches

- **User approved expansion** this turn ("yes, also fix Y") — proceed.
- **Transitive requirement** — in-scope edit forces out-of-scope file change (e.g. import signature). State requirement inline before editing.
- **Emergency rollback** — constitutional §7 auto-closure path.
- **`SCOPE_CONTAINMENT_BYPASS=1`** — logs bypass row; scripted batch / acknowledged exploration only.

## Enforcement

| Layer | Component |
|---|---|
| Composition | This rule (always_on, advisory) |
| Text-search cap | `post_cascade_grep_budget_audit.py` → `artifacts/windsurf/grep_budget_violations.jsonl` |
| File-read cap | `post_cascade_read_budget_audit.py` → `artifacts/windsurf/read_budget_violations.jsonl` |
| Token telemetry | `post_cascade_token_telemetry.py` → `artifacts/windsurf/turn_budget.jsonl`; weekly: `ops_scripts/calibration/token_burn_weekly_report.py` |
| Indexing surface | `.codeiumignore` excludes `archives/`, `artifacts/`, `reports/`, `data/` |
| Out-of-scope ideas | `NEXT_STEP:` marker (`next-step-capture.md`) |
| Topic transitions | `SCOPE_RESET:` marker (this rule) |

## References

Constitutional §18 (no hidden scope expansion), §28 (ADG over grep), §31 (SSOT folder routing). Siblings: `next-step-capture.md`, `deferred-scope-capture.md`, `global_rules.md` (ADG-First Retrieval-Tool Decision Tree).
