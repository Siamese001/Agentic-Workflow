
<!-- Converted from `.claude/rules/notion-plan-wave-deferral.md`. Original Cursor trigger: `always_on`. -->

> See `plan-lifecycle-procedures.md` for full wave deferral and execution protocol.

# Notion Plan-Wave Deferral — Core Invariant

## The Rule

> ⛔ **While executing a multi-wave plan, Cursor Agent MUST NOT call any Notion MCP tool. ALL Notion writes are deferred until after the final wave completes.**

## Core Requirements (Always-On)

| Phase | Action |
|-------|--------|
| Wave 1 start | `wave_execution_state.py start` (direct HTTP) |
| During execution | **NO MCP calls** — blocked by `pre_mcp_gate` |
| Final wave | `wave_execution_state.py complete` (direct HTTP) |
| Post-completion | MCP writes allowed one-per-block |

## Required Markers

```
WAVE_COMPLETE: plan=<slug-6hex> wave=<N> note="<summary>"
PHASE_COMPLETE: plan=<slug-6hex> phase=<id> note="<one-liner>"
PLAN_COMPLETE: plan=<slug-6hex> note="<final outcome>"
```

## Full Protocol

| Topic | Location |
|-------|----------|
| Sanctioned non-MCP path | `plan-lifecycle-procedures.md` §3 |
| Retrospective plan protocol | `plan-lifecycle-procedures.md` §3 |
| Wave lifecycle details | `plan-lifecycle-procedures.md` §3 |
| High-signal Summary appends | `plan-lifecycle-procedures.md` §3 |

## Bypass

- `NOTION_WAVE_DEFERRAL_BYPASS=1` — bypass MCP-call deferral (logged)
- `WAVE_LIFECYCLE_NOTION_BYPASS=1` — skip direct-HTTP writer
- `PLAN_COMPLETE_AUDIT_BYPASS=1` — suppress advisory warning

---

**Core invariant preserved.** Full protocol moved to `plan-lifecycle-procedures.md` (W3.P3 2026-05-12).
