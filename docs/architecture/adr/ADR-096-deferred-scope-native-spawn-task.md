# ADR-096 — Deferred-scope / next-step markers superseded by native spawn_task

- **Status:** Accepted
- **Date:** 2026-06-07
- **Plan:** [claude-native-supersession-9d3f7a](../../../plans/claude-native-supersession-9d3f7a.md) (Wave W4)

## Context

Out-of-scope work was captured with `DEFERRED_SCOPE:` (constitutional §24) and `NEXT_STEP:` markers,
each backed by a capture hook, a deterministic P1–P5 scorer, a miss-detector, a session-start recovery
hook, a Notion-posting path, and CI/pre-commit gates (`check_deferred_scope_markers.py`, T6e1, T7i,
T7j). This emulated a "spin out a follow-up task" mechanism Claude Code now provides natively as
**`spawn_task`** — a background-task chip the user can promote to its own session/worktree or dismiss.

## Decision

- **Invariant kept:** out-of-scope work must be *captured*, not silently dropped.
- **Retired:** the marker→hook→scorer→Notion pipeline.
  - `run_contract_gates.py`: DEFER deferred-scope gate removed.
  - `.pre-commit-config.yaml`: T6e1 `deferred-scope-marker`, T7i `deferred-scope-markers`, T7j
    `notion-schema-mece` removed.
  - Constitutional **§24** reworded to native `spawn_task`; slot kept for stable numbering.
  - `deferred-scope-capture.md` + `next-step-capture.md` reduced to spawn_task stubs.
- **Kept:** a durable Notion backlog row remains available via **explicit user action**; scoped
  wave-deferral inside an active plan is noted in the plan body.
- **Left dormant (swept W5):** `post_cursor_agent_deferred_scope_capture.py`,
  `post_cursor_agent_next_step_capture.py`, `post_cursor_agent_next_step_miss_detector.py`,
  `pre_user_prompt_deferred_scope_recovery.py`, `tools/priority/deferred_scope_scorer.py`. The ADG
  burndown `adg-gates-markers` manual hook still emits `DEFERRED_SCOPE:` lines; they are now operator
  signals rather than auto-posted rows.

## Consequences

- Out-of-scope items become real, actionable chips instead of prose markers that could vanish.
- Fewer gates and no scorer to maintain.
- Reversible from git history.
