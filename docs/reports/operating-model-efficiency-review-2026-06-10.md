# Operating-Model Efficiency Review — "145 Plans, 0 Shipped"

> **Date:** 2026-06-10  
> **Scope:** apps_rg delivery cadence over the preceding ~3 weeks  
> **Status:** Findings consolidated from existing governance artifacts (commit `2f83d4bb` / PR #282, `.claude/rules/apps-rg-execution-bias.md`, `CLAUDE.md`, plan `b8c3d1`). No new measurement performed — this report copies and organizes findings already recorded in the repo.

---

## 1. The headline finding

In the ~3 weeks preceding 2026-06-10, the operating model produced:

| Metric | Value |
|---|---|
| Plan files created | **145** |
| Plans marked `Completed` | **119** |
| Product shipped (AIG resume, 11/11 lanes X3_ALLOW, assembled DOCX) | **0** |

The system was 82% "complete" by its own bookkeeping and 0% delivered by the only
metric that matters. Plan completion had silently become the success proxy in place
of a shipped artifact.

_Source: commit `2f83d4bb` ("Adopted after the operating-model review: 145 plans /
119 completed / 0 product shipped in 3 weeks"), echoed in `apps-rg-execution-bias.md`._

## 2. Root cause — a mode-faithful amplifier stuck in PLAN mode

The agent system is a **mode-faithful amplifier**: it executes whatever mode it is
defaulted into, at scale. Its default mode was effectively PLANNING, so it amplified
planning — not delivery. The dominant reflex was:

> "I found a gap → write a plan."

Each discovery spawned a *new plan document* rather than a *backlog row against an
existing plan* or an *executed increment*. Discovery was unbounded and front-loaded
instead of post-increment, so the plan count compounded while the product did not move.

## 3. Secondary failure modes observed

| # | Failure mode | Evidence |
|---|---|---|
| F1 | **Plan-as-progress accounting** | 119 "Completed" plans, 0 shipped product. Completing a plan was treated as an outcome. |
| F2 | **The factory reflex** | Findings/ideas became new plan files instead of rows in a single backlog. |
| F3 | **RC3 collision class** | Parallel sessions doing write-work on the same app produced *same-day supersessions* and *mutual reverts* (both observed 2026-06-10). No WIP limit was enforced. |
| F4 | **Unbounded, pre-increment discovery** | New analysis lenses opened before the active wave shipped, multiplying scope. |
| F5 | **Addition without subtraction** | Gates/receipts/machinery accumulated without consolidating equivalent existing machinery. |
| F6 | **Proposals over receipts** | Status was reported as what *could* be planned, not what *ran* and what the receipts showed. |

## 4. Scope-debt this produced

The deferred-but-undelivered work was later consolidated into a single master
inventory (plan `apps-rg-lane-aggregation-gap-closure-b8c3d1`): a **42-gap inventory
across seven recurring families** (Qwen-era over-compensation, numeric/config drift,
uncovered stochastic-content failures, judge fragility, all-or-nothing aggregation,
C0.3 value-spine gaps, base-resume containment). That backlog is the proof of how much
real work had been *enumerated in plans* but never *executed into product*.

> Note: the rule cites a "43-gap Master Inventory"; the plan body enumerates 42 gaps
> (G1–G42). The one-row discrepancy is in the source artifacts, not introduced here.

## 5. The corrective standing orders (adopted 2026-06-10)

The review's response is codified in `apps-rg-execution-bias.md` and `CLAUDE.md`.
Default mode flipped from PLAN to **EXECUTE**:

1. **Execute, don't plan.** New plan files are blocked by
   `.claude/hooks/pre_write_plan_mint_gate.py`; minting requires explicit same-turn
   user authorization (`PLAN_MINT_OK=1`).
2. **Findings become rows, not plans** — appended to the single master backlog (`b8c3d1`).
3. **WIP limit = 1 active plan, one owner session** (directly targets the RC3 collisions).
4. **Discovery budget ~20%, post-increment only.**
5. **Subtraction before addition.**
6. **Receipts over proposals** — the weekly heartbeat E2E lane matrix is the only status artifact.

**North star (only success metric until met):** AIG resume, 11/11 lanes X3_ALLOW,
assembled DOCX in hand.

## 6. One-line summary

> A mode-faithful agent stuck in plan mode turned three weeks of effort into 145 plans
> and 119 "completions" with zero shipped product; the fix is a mechanically-enforced
> execute-first operating model with a hard WIP limit and a single backlog.

---

### Source artifacts

- [apps-rg-execution-bias.md](../../.claude/rules/apps-rg-execution-bias.md) — standing orders + rationale
- [CLAUDE.md](../../CLAUDE.md) § "apps_rg Operating Model — Standing Orders (2026-06-10)"
- [pre_write_plan_mint_gate.py](../../.claude/hooks/pre_write_plan_mint_gate.py) — enforcement
- [apps-rg-lane-aggregation-gap-closure-b8c3d1.md](../../plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md) — single backlog (42-gap inventory)
- Commit `2f83d4bb` (PR #282) — review adoption record
