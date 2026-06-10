# Operating-Model Efficiency Review — "~1,200 Plans, 0 Shipped"

> **Date:** 2026-06-10  
> **Scope:** Full plan-creation cadence over the last ~3 months (the data goes back to **April 2026** — the earliest dated archive bucket; that is "as far back as I can go").  
> **Status:** Findings reconstructed from the on-disk plan corpus + archive structure + in-file date stamps. The original ~3-week apps_rg slice (§1) is preserved as the triggering subset; §1b extends it to the full 3-month window.

> **Methodology / caveat (read first).** The intended source — the **Notion Plans DB** — is **not reachable from this execution environment** (no Notion MCP server is whitelisted in `.mcp.json`, and none is connected). Per `.claude/rules/plan-location.md`, Notion is a **file-driven mirror**: every Plans row is created *from* a `plans/<slug>-<6hex>.md` file with a content digest. So the on-disk plan corpus is the SSOT the Notion DB is built from, and is used here as the authoritative substitute. Git author-dates are **not** usable (the repo was bulk-committed in one June import, flattening all timestamps), so dates come from **archive bucket names** and **date stamps inside the plan files**. Counts are DIRECTLY OBSERVED from disk; monthly attribution is DERIVED and approximate.

---

<!-- ============================================================
     PICKUP NOTE FOR A NEW (Notion-enabled) SESSION
     The on-disk reconstruction below is the verified interim answer.
     To replace the DERIVED monthly attribution in §1b with authoritative
     Notion data, run this in a session where Notion is reachable
     (MCP connector enabled, OR api.notion.com allowlisted + NOTION_TOKEN set):

       1. Query Plans DB data source: ac53d31b-3068-4039-9ebe-856c12caab32
       2. Paginate all rows; for each pull: created_time, Status, Slug, Exists On Disk
       3. Bucket by created_time month (2026-03..2026-06) and by Status
       4. Replace the §1b "Monthly distribution" + completion figures with the
          Notion numbers; keep the on-disk figures as a labeled cross-check column
       5. Expected: Notion total < 1,197 on-disk (pre-registration + pre-2026-05-15
          sweep plans were never registered / are Retired|Archived). Not a discrepancy.
       6. Commit + push.
     ============================================================ -->

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

## 1b. The 3-month view (April → June 2026)

The ~3-week apps_rg slice above was not an anomaly — it was the visible tip of a
quarter-long pattern. Extending the window to the full plan corpus:

| Metric | Value | Grade |
|---|---|---|
| Total plan files on disk (`plans/` + `.claude/plans/` + archive) | **1,197** | OBSERVED |
| Distinct plan paths ever recorded in git (incl. moves/renames) | 2,181 | OBSERVED |
| Plans bearing a completion marker (`PLAN_STATUS: COMPLETE` / `PLAN_COMPLETE:` / `status: completed`) | 121 / 134 / 172 | OBSERVED |
| **Certified North-star deliverables (AIG resume, 11/11 lanes X3_ALLOW, assembled DOCX)** | **0** | DERIVED |
| Raw resume `.docx` generation outputs (uncertified, latest 2026-04-28) | 8 | OBSERVED |

### Monthly distribution (by archive bucket + in-file date stamps)

| Month | Archive bucket(s) | In-file date stamps | Notes |
|---|---|---|---|
| **2026-04** | `_archive/2026-04/` = 10 | 34 | Earliest data available ("as far back as I can go") |
| **2026-05** | `_archive/2026-05/` = 633 **+** `_archive/historical_plans_20260515_cursor_optimization/` = 451 → **~1,084** | 259 | The glut. A `2026-05-15` "cursor_optimization" sweep archived **451 plans in one pass** — the system recognized the plan-glut and tried to clean it, but the factory kept minting (633 more in the May bucket). |
| **2026-06** | `plans/` = 31 + `.claude/plans/` = 59 → **~90** | 62 | Current/active; the 145-plan apps_rg slice (§1) sits inside this tail. |

### What the 3-month view adds to the 3-week finding

1. **Scale:** the ~145-plan / 3-week figure generalizes to **~1,200 plan files over the quarter** — roughly **two-thirds concentrated in May 2026** alone.
2. **The self-aware-but-ineffective cleanup:** the `2026-05-15` archival of 451 plans proves the glut was *seen*, but archiving plans is not shipping product — the factory was not switched off until the 2026-06-10 standing orders.
3. **Shipping stayed flat at zero (North-star metric):** despite ~1,200 plans and 120–170 "completions," **no certified AIG deliverable** exists. The 8 `.docx` files are pre-certification generation outputs from late April, not 11/11-lane assembled product.
4. **"Completed" is decoupled from "delivered" all quarter** — not just in the 3-week window. The completion-marker count (121–172) tracks plan bookkeeping, not product.

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

> A mode-faithful agent stuck in plan mode turned **a quarter** of effort into **~1,200 plan
> files** (≈two-thirds minted in May 2026) and 120–170 "completions" with **zero certified
> product shipped** — even a mid-May sweep that archived 451 plans didn't stop the factory.
> The 145-plan / 3-week apps_rg slice was the tip, not the whole. The fix is a mechanically-
> enforced execute-first operating model with a hard WIP limit and a single backlog.

---

### Source artifacts

- [apps-rg-execution-bias.md](../../.claude/rules/apps-rg-execution-bias.md) — standing orders + rationale
- [CLAUDE.md](../../CLAUDE.md) § "apps_rg Operating Model — Standing Orders (2026-06-10)"
- [pre_write_plan_mint_gate.py](../../.claude/hooks/pre_write_plan_mint_gate.py) — enforcement
- [apps-rg-lane-aggregation-gap-closure-b8c3d1.md](../../plans/apps-rg-lane-aggregation-gap-closure-b8c3d1.md) — single backlog (42-gap inventory)
- Commit `2f83d4bb` (PR #282) — review adoption record
