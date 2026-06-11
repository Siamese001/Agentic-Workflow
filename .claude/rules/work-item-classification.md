# Work-Item Classification — Fix, File, or Plan

> Operating-model origin (2026-06-10): 145 plans / 119 "Completed" / 0 product shipped.
> Root cause: a plan-creation reflex that converts every finding into a document.
> This rule replaces that reflex with a decision tree enforced by hooks and memory.

## Classification Matrix

| Class | Tier | Condition | Action | Notion write? |
|---|---|---|---|---|
| `BUG_IMMEDIATE` | T0/T1 | ≤3 files, provable this turn | Fix directly; proof receipt is the artifact | No |
| `BUG_DEFERRED` | T2 | Multi-file, out-of-scope now | `spawn_task` chip | User decides |
| `BUG_SYSTEMIC` | T3 | Cross-layer, multi-session fix | Backlog Item; Plan only if ≥2 waves | Yes — Backlog Item |
| `FINDING_APPS_RG` | Any | apps_rg gap / lane issue | Row in Master Gap Inventory | No |
| `ENHANCEMENT_MINOR` | T0/T1 | In-scope, ≤20 lines | Fix if in scope; `spawn_task` if deferred | No |
| `ENHANCEMENT_BACKLOG` | T2 | Out-of-scope improvement | `spawn_task` chip | No |
| `ENHANCEMENT_ROADMAP` | T3 | Multi-session strategic | Backlog Item | Yes — Backlog Item |
| `PLAN_MICRO` | T1/T2 | ≤1 session, <2 waves | Native plan mode only. No disk file. No Notion. | No |
| `PLAN_MULTI_WAVE` | T2/T3 | ≥2 waves, spans sessions | `plans/<slug>-<6hex>.md` + Notion Plans DB (§36) | Yes — Plans DB |

## The Plan-Correction (most common mistake)

> **NOT all plans go to Notion.** Only multi-wave, multi-session plans need §36 registration.

| Planning type | Disk file? | Notion? |
|---|---|---|
| Native plan mode (`EnterPlanMode`/`ExitPlanMode`, single session) | No | No |
| Micro-plan (in-session decomposition, <2 waves, T1/T2) | No | No |
| Multi-wave plan (≥2 waves, expected to span sessions) | Yes — `plans/<slug>.md` | Yes — Plans DB |

The wrong default was: every plan → `plans/*.md` → Notion. The correct default is: every plan → native plan mode → only *escalate* to disk + Notion when the plan will span sessions and carry wave state.

## The Four Anti-Reflex Rules

1. **Found a bug → classify first.** T0/T1 → fix immediately, no planning. T2 deferred → `spawn_task`. T3 systemic → Backlog Item.
2. **Found an apps_rg finding → append a row, never a plan.** The Master Gap Inventory (`plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md`) is the only output.
3. **Need to plan → ask if it spans sessions.** Single session = native plan mode only. Multi-session = disk file + Notion.
4. **Writing to Notion Plans DB → verify it is multi-wave.** Micro-plans do not belong in Notion; they inflate the "Completed" count with zero delivery.

## Auto-Classification Signals

| Signal | Class |
|---|---|
| "X fails", "test fails", "gate blocks", single file fix visible | `BUG_IMMEDIATE` |
| "X is broken", multi-file, not blocking north star, can defer | `BUG_DEFERRED` |
| "X is architecturally wrong", cross-layer, needs refactor plan | `BUG_SYSTEMIC` |
| apps_rg lane failure, E2E block, section gap | `FINDING_APPS_RG` |
| "improve X", in-scope, ≤20 lines | `ENHANCEMENT_MINOR` |
| "add feature Y", out-of-scope or deferred | `ENHANCEMENT_BACKLOG` |
| "strategic initiative", multi-session, multi-team | `ENHANCEMENT_ROADMAP` |
| T2/T3 decomposition fits one focused session | `PLAN_MICRO` |
| T2/T3 decomposition needs state tracked across sessions | `PLAN_MULTI_WAVE` |

## Enforcement

| Mechanism | Event | What it catches |
|---|---|---|
| `pre_write_plan_mint_gate.py` (PreToolUse) | Write/Edit | New plan file creation without authorization |
| `post_agent_work_classification_audit.py` (Stop) | After response | Plan-reflex patterns in response text |
| This rule (model_decision) | On demand | Shapes classification decisions |

## Decision Flow (condensed)

```
New finding?
  ├── apps_rg related? → row in Master Gap Inventory. DONE.
  ├── T0/T1 bug, in scope? → fix directly. DONE.
  ├── T0/T1 bug, out of scope? → spawn_task. DONE.
  ├── T2 bug? → spawn_task (user decides if Backlog Item). DONE.
  ├── T3 systemic bug? → Backlog Item in Notion. If ≥2 waves: also plan file + Notion Plans.
  └── Enhancement? → same ladder (minor→fix, backlog→spawn_task, roadmap→Backlog Item).

Plan needed?
  ├── Single session, <2 waves? → native plan mode only. No file. No Notion. DONE.
  └── Multi-session, ≥2 waves? → plans/<slug>.md + Notion §36 + explicit user auth.
```

## References

- Operating model: `.claude/rules/apps-rg-execution-bias.md`
- Master Gap Inventory: `plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md`
- Plan registration: constitutional §36, `.claude/rules/plan-location.md`
- Deferred scope: constitutional §24 (`spawn_task` — no `DEFERRED_SCOPE:` marker)
- Classification auditor: `.claude/governance/scripts/post_agent_work_classification_audit.py`
- Plan mint gate: `.claude/hooks/pre_write_plan_mint_gate.py`
