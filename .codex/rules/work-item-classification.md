# Work-Item Classification — Fix, File, or Plan

> Origin (2026-06-10): 145 plans / 119 "Completed" / 0 shipped. Replaces the plan-creation reflex with a decision tree enforced by hooks.

## Classification Matrix

| Class | Tier | Condition | Action |
|---|---|---|---|
| `BUG_IMMEDIATE` | T0/T1 | ≤3 files, provable this turn | Fix directly; proof receipt is the artifact |
| `BUG_DEFERRED` | T2 | Multi-file, out-of-scope now | `spawn_task` chip |
| `BUG_SYSTEMIC` | T3 | Cross-layer, multi-session | Backlog Item; disk plan only if ≥2 waves |
| `FINDING_APPS_RG` | Any | apps_rg gap / lane issue | Row in Master Gap Inventory |
| `ENHANCEMENT_MINOR` | T0/T1 | In-scope, ≤20 lines | Fix if in scope; `spawn_task` if deferred |
| `ENHANCEMENT_BACKLOG` | T2 | Out-of-scope improvement | `spawn_task` chip |
| `ENHANCEMENT_ROADMAP` | T3 | Multi-session strategic | Backlog Item |
| `PLAN_MICRO` | T1/T2 | <2 waves AND ≤~3 files | Native plan mode only — no disk file |
| `PLAN_MULTI_WAVE` | T2/T3 | ≥2 waves OR ≥~10 files / cross-layer (single-session does NOT exempt) | `plans/<slug>-<6hex>.md` disk SSOT, minted at the start |

## Plan-FIRST ≠ plan-PERSISTENCE

Native plan mode (`EnterPlanMode`/`ExitPlanMode`) satisfies think-before-editing but writes to `~/.codex/plans/` — **it persists nothing to the repo SSOT**. Complexity, not session-span, decides persistence: a big change done in ONE session still deserves a durable `plans/<slug>-<6hex>.md` (RCA 2026-06-14 / ADR-104). Plans are **disk-only** (no Notion). Mint the disk plan for ≥2-wave or large/cross-layer work (request `PLAN_MINT_OK=1`); keep native plan mode for small work.

## The Four Anti-Reflex Rules

1. **Found a bug → classify first.** T0/T1 in-scope → fix now. T2 deferred → `spawn_task`. T3 systemic → Backlog Item.
2. **apps_rg finding → append a row, never a plan** (Master Gap Inventory `plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md`).
3. **Need to plan → size it.** Small = native plan mode; complex (≥2 waves / ≥~10 files / cross-layer T3) = mint a disk plan at the start.
4. **Native plan mode persists nothing durable** — don't default to it for complex work.

## Enforcement

- `pre_write_plan_mint_gate.py` (PreToolUse) — blocks new plan files without `PLAN_MINT_OK=1`.
- `post_agent_work_classification_audit.py` (Stop) — catches plan-reflex (over-planning) AND unpersisted multi-wave execution (under-persisting).

## References

- `.codex/rules/apps-rg-execution-bias.md` · `.codex/rules/plan-location.md` · constitutional §24 (`spawn_task` — no `DEFERRED_SCOPE:` marker).
