---
trigger: model_decision
description: Converted from Cursor rule scope-containment.md Demoted from always_on 2026-05-26 (governance-dedup-closeout-e8a4c2 W4). Cursor SSOT: .cursor/rules/scope-containment.mdc (alwaysApply: false).
---

# Scope Containment — No Gold-Plating, One Task At A Time

> ⛔ **Scope of the current response = (a) what the user asked for + (b) files in the active plan's `Files In Scope` + (c) files required to satisfy (a)+(b) transitively. Nothing else.**

Operationalizes constitutional §18 (no hidden scope expansion).

## The Four Hard Rules

1. **No gold-plating.** Don't improve code Cursor Agent "noticed needed improving" while doing something else. File a `NEXT_STEP:` marker; move on.
2. **No "while I'm here" edits.** Touching an unrelated file because it's open / nearby = scope expansion — forbidden without explicit user approval this turn.
3. **One active task at a time.** Asked for X → do X. Don't start Y because Y "also needs doing". Concurrent scopes require an explicit user turn naming both.
4. **Out-of-scope improvements → `NEXT_STEP:` marker, NOT an edit.** Per `next-step-capture.md`, emit marker same response; hook auto-captures; DO NOT implement.

## In-Scope vs Out-of-Scope

**In scope**: files the user named (path / `@` mention / quoted snippet); files in plan `Files In Scope`; files required for (a)+(b) to compile / type-check / pass tests; tests covering the above.

**Out of scope by default**: files only discovered via `grep_search` / `code_search` (read-only context, never edit); unrelated anti-pattern / lint / formatting touches; doc / README updates unless requested; new tests for code paths outside active scope.

## Retrieval Discipline

**Caps**: `grep_search`+`code_search` ≤3/response; file reads ≤10/response. **ADG > grep** for dependencies. See `scope-containment` skill for detailed procedure.

## Scope Markers

| Marker | When | Format |
|--------|------|--------|
| `SCOPE_RESET:` | Cross-turn topic shift | `SCOPE_RESET: from=<prior> to=<new> dropped=<files>` |
| `NEXT_STEP:` | Out-of-scope ideas (don't implement) | `NEXT_STEP:` + description |

Triggers: different top-level dir, layer (L0→L4), app (apps_qna→apps_rg), task type (refactor→debug→plan), explicit "switch to".

## Forbidden Patterns

- ❌ "I also noticed X could be improved, so I fixed it too" — gold-plating.
- ❌ Editing files across 3+ modules the user did not mention in one response.
- ❌ Starting a new plan/task/refactor mid-response because current work "reminded me".
- ❌ `grep_search` >3× without a matching `adg_*` or ADG-SQLite direct-read attempt first.
- ❌ Renaming / moving / deleting files outside active scope — even if the filename looks obviously wrong.

## Escape Hatches

- User approved expansion ("yes, also fix Y") — proceed
- Transitive requirement — state inline before editing
- Emergency rollback — constitutional §7
- Scripted batch — `SCOPE_CONTAINMENT_BYPASS=1`

## Enforcement

`post_cascade_grep_budget_audit.py` (text-search cap) · `post_cascade_read_budget_audit.py` (file-read cap) · `post_cascade_token_telemetry.py` (telemetry). `scope-containment` skill for detailed procedure. Constitutional §18, §28, §31. Siblings: `next-step-capture.md`, `deferred-scope-capture.md`, `global_rules.md`.
