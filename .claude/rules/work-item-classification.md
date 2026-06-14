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
| `PLAN_MICRO` | T1/T2 | ≤1 session, <2 waves, **and** ≤~3 files | Native plan mode only. No disk file. | No |
| `PLAN_MULTI_WAVE` | T2/T3 | ≥2 waves **OR** large/cross-layer (≥~10 files) — **single-session does NOT exempt** | `plans/<slug>-<6hex>.md` (disk-only SSOT), **minted at the start** | No |

## The Plan-Correction (most common mistake)

> **Plan-FIRST ≠ plan-PERSISTENCE.** Native plan mode (`EnterPlanMode`/`ExitPlanMode`) satisfies
> *think-before-editing*, but it writes to `~/.claude/plans/` — **it persists nothing to the repo SSOT.**
> Complexity, not session-span, decides persistence: a big change done in ONE session still deserves a
> durable `plans/<slug>-<6hex>.md` record. (RCA 2026-06-14: a 7-wave / ~230-file T3 change ran entirely
> in native plan mode and left no SSOT plan — see ADR-104.)
>
> **Plans are disk-only.** The windsurf/cursor-era Notion plan-registration / status / wave-lifecycle
> enforcement was removed (it never functioned). No plan goes to Notion. (Notion remains an *optional
> manual* durable backlog for Backlog Items per constitutional §24 — never enforced, never for plan status.)

| Planning type | Disk file? |
|---|---|
| Native plan mode (single session, <2 waves, ≤~3 files) | No |
| Micro-plan (in-session decomposition, <2 waves, T1/T2, small) | No |
| **Multi-wave (≥2 waves) OR large/cross-layer (≥~10 files) — even single-session** | **Yes — `plans/<slug>-<6hex>.md`, minted at the start** |

The wrong default was: every plan → `plans/*.md` (→ Notion). The over-correction was: *every* plan →
native plan mode → never persist. The correct default: native plan mode for small work; **mint a disk
SSOT plan for genuinely complex work (≥2 waves or large), regardless of whether it spans sessions.**

## The Four Anti-Reflex Rules

1. **Found a bug → classify first.** T0/T1 → fix immediately, no planning. T2 deferred → `spawn_task`. T3 systemic → Backlog Item.
2. **Found an apps_rg finding → append a row, never a plan.** The Master Gap Inventory (`plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md`) is the only output.
3. **Need to plan → size it, don't just ask about sessions.** Small (≤~3 files, <2 waves) = native plan mode only. **Complex (≥2 waves OR ≥~10 files OR cross-layer T3) = mint a disk `plans/<slug>-<6hex>.md` at the start** (request `PLAN_MINT_OK=1`), then execute — even if it all happens in one session.
4. **Native plan mode persists nothing durable.** Do not let it be the default for complex work just because it is friction-free: it leaves no SSOT record. Mint the disk plan for ≥2-wave / large changes; keep native plan mode for small work. (Notion plan registration was removed — SSOT is disk-only.)

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
| T2/T3, fits one focused session, <2 waves, ≤~3 files | `PLAN_MICRO` |
| ≥2 waves **OR** ≥~10 files **OR** cross-layer T3 — even if single-session | `PLAN_MULTI_WAVE` |

## Enforcement

| Mechanism | Event | What it catches |
|---|---|---|
| `pre_write_plan_mint_gate.py` (PreToolUse) | Write/Edit | New plan file creation without authorization |
| `post_agent_work_classification_audit.py` (Stop) | After response | Plan-reflex (over-planning) **and** unpersisted multi-wave execution (under-persisting — multi-wave work with no minted `plans/*.md`) |
| This rule (model_decision) | On demand | Shapes classification decisions |

## Decision Flow (condensed)

```
New finding?
  ├── apps_rg related? → row in Master Gap Inventory. DONE.
  ├── T0/T1 bug, in scope? → fix directly. DONE.
  ├── T0/T1 bug, out of scope? → spawn_task. DONE.
  ├── T2 bug? → spawn_task (user decides if Backlog Item). DONE.
  ├── T3 systemic bug? → Backlog Item (optional manual Notion backlog, §24). If ≥2 waves: also disk plan file.
  └── Enhancement? → same ladder (minor→fix, backlog→spawn_task, roadmap→Backlog Item).

Plan needed?
  ├── Small (<2 waves, ≤~3 files)? → native plan mode only. No file. DONE.
  └── ≥2 waves OR ≥~10 files OR cross-layer T3 (even single-session)? → mint plans/<slug>-<6hex>.md
      at the START (request PLAN_MINT_OK=1) → execute. SSOT disk-only, no Notion.
```

## References

- Operating model: `.claude/rules/apps-rg-execution-bias.md`
- Master Gap Inventory: `plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md`
- Plan location: `.claude/rules/plan-location.md` (constitutional §36 retired — plans are disk-only)
- Deferred scope: constitutional §24 (`spawn_task` — no `DEFERRED_SCOPE:` marker)
- Classification auditor: `.claude/governance/scripts/post_agent_work_classification_audit.py`
- Plan mint gate: `.claude/hooks/pre_write_plan_mint_gate.py`
