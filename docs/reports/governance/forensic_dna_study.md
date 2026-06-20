# Forensic DNA Study — Behavioral Pattern Analysis & Mitigation Recommendation

**Date:** 2026-06-15 · **Scope:** 341 merges (2025-11-11 → 2026-06-14, full history) +
2,000 most-recent non-merge commits (2026-04-21 → 2026-06-15) + 317 merged PR cards.
**Author:** Claude (high-signal enforcer mode). **Subject:** `Siamese001/Agentic-Workflow`.
**North star:** apps_rg E2E, 11/11 lanes X3_ALLOW, sliding-scale graph skills, assembled DOCX.

> Companion visual: [forensic_dna_study.png](forensic_dna_study.png). Prior ADHD-focused
> analysis: PR #379 (`PARKING_LOT.md`) + the attention-timeline artifact.

---

## 1. Method & provenance

- Local git history (unshallowed: 10,099 commits, 341 merges) → timing, churn, thrash, branch taxonomy.
- GitHub PR search API → review/merge/comment metadata (317 merged PRs).
- Each commit classified by subject keywords (north-star / governance-meta / plan / thrash).
- All figures are DIRECTLY OBSERVED from git/API unless marked DERIVED. Churn totals include
  generated artifacts (run bundles, ADG dumps) and so over-state human authoring — the *ratios*
  and *single-commit deletion events* are the reliable signal, not the absolute line counts.

---

## 2. Headline findings

| # | Finding | Value | Grade |
|---|---|---|---|
| F1 | Merged PRs reviewed by a second party | **0 of 317 (0%)** | DIRECTLY OBSERVED |
| F2 | North-star commits (2k window) | **18%** | DIRECTLY OBSERVED |
| F3 | Governance/meta commits | **20%** | DIRECTLY OBSERVED |
| F4 | Plan-authoring commits | **15%** | DIRECTLY OBSERVED |
| F5 | Thrash (revert/re-pin/re-baseline/retire/decommission) | **6%** | DIRECTLY OBSERVED |
| F6 | Commits < 10 min apart (burst-committing) | **69%** | DIRECTLY OBSERVED |
| F7 | Terminal merge binge | **W24 = 83 merges** (vs 1–10 typical) | DIRECTLY OBSERVED |
| F8 | Activity cadence | **7/7 days, all 24h; Sunday highest (382)** | DIRECTLY OBSERVED |
| F9 | Build-then-demolish | single commits of **−463k / −296k / −124k** lines | DIRECTLY OBSERVED |
| F10 | Self-merge latency | PR #378 created→merged in **~30 min**, 0 comments | DIRECTLY OBSERVED |

**The one-sentence read:** a uniquely capable solo operator, working round-the-clock with
**no external checkpoint**, spends ~4× more effort building/rearranging governance machinery
and plans than on the north star — and self-approves all of it within minutes.

---

## 3. The DNA — suboptimal patterns, separated by origin

### 3a. ADHD-core (covered in PR #379, restated for completeness)
- **Anxiety-driven avoidance** toward *unevaluable* meta-work (a gate can't fail you; a lane can).
- **Novelty/dopamine switching** — 23 north↔ortho pivots in 31h; friction on the goal triggers the pivot.
- **Capture-by-doing** — fear of losing an idea → build it now (the 3,053-plan fossil record).

### 3b. ADHD *variants* (newly surfaced here)
- **V1 · Hyperfocus binge / hypomanic cadence (F7, F8).** W24's 83 merges and 7-day, 24-hour
  activity with Sunday as the *peak* day is not sustainable focus — it's a binge with no
  recovery cycle. Productivity mania burns the same fuel as a crash.
- **V2 · Time-blindness (F6, F8).** 69% of commits land <10 min apart and work spans the full
  clock including local late-night. No time-boxing; the day has no edges.

### 3c. Patterns **outside ADHD** (the new contribution of this study)
These are organizational / cognitive-style patterns, not attention-regulation. They would
persist even if the ADHD were fully treated, and several *amplify* the ADHD ones.

- **P1 · No-checkpoint solo operation (F1, F10) — the master amplifier.** 0/317 PRs reviewed;
  PRs self-merged in minutes. P1 has **two dimensions, and they are now in different states**
  (see §6): (a) the **correctness** checkpoint — *restored*: CI was 100% failing and bypassed
  (red theater = no checkpoint), and the right-sizing refactor took it to lean **green-and-passing**;
  (b) the **judgment** checkpoint — *still open*: no "is this the north star?" gate that the
  operator cannot unilaterally wave through. CI passing proves the code is correct; it never asks
  whether the code *should exist*. The remaining hole is judgment, not correctness. This is a
  **process/structure** defect, not a neurological one.
- **P2 · Build-then-demolish / sunk-cost over-engineering (F9).** Notion enforcement, Fort Knox
  certification, dozens of "orphan" gates were built, then mass-deleted (−463k, −296k, −124k
  in single commits). Energy spent erecting machinery that was later torn out = pure waste,
  and the teardown itself becomes more "productive" meta-work.
- **P3 · Process-as-product / Parkinson's law of triviality (F3).** 282 CI gates, 62 governance
  scripts, 43 rules for a *solo* repo. Governance is engineered to enterprise-fleet standard
  while the actual product (one resume pipeline) is 18% of effort. The trivial-but-safe work
  crowds out the important-but-risky work.
- **P4 · Documentation-as-displacement (F4).** 15% of commits are plan-authoring; 3,053 plan
  files on disk. Plans substitute the *feeling* of progress for shipped output.
- **P5 · Thrash / same-day supersession (F5).** 6% of commits undo recent work (re-pin,
  re-baseline, restore-after-revert, mutual reverts — the RC3 collision class the repo's own
  rules already document). Decisions are remade, not made.
- **P6 · No WIP limit / branch sprawl.** Concurrent lanes across `claude/`, `feat/`, `codex/`,
  `chat/`, `integration/`, `wip/`, `w5/`. Parallel in-flight work guarantees merge conflicts,
  rebases, and the thrash in P5.
- **P7 · Tooling recursion.** The AskUserQuestion confidence meta-learning loop and calibration
  ledgers are *tools to govern the tools*. Each abstraction layer added is a new surface that
  needs maintenance — and a new place for displacement energy to hide.
- **P8 · Low-deliberation throughput (F6).** Burst-committing pairs with P1: nothing forces a
  pause to ask "should this exist?" The result is high motion, modest north-star displacement.
- **P9 · Parallelism-as-permission-to-never-choose (operator-surfaced 2026-06-15) — the alibi'd
  variant of the fear.** High AI-desktop capacity (multi-agent / multi-worktree) is recruited not
  to go *faster at the north star* but to *avoid choosing* between it and orthogonal ideas — "I'll
  run all of them on their own branch and merge/rebase later." It is P-core (fear of loss) with a
  *rational-sounding hardware alibi*, which makes it more insidious than ordinary procrastination.
  Measured cost (after-pivot window, 4.8 days) — **using merge/commit *activity*, not branch
  existence**: rebase/sync-merge tax **0.32→2.50/day (~8×)**; **19 distinct lanes merged**;
  **17 collision-class commits** (revert/restore/re-pin/reconcile/post-rebase) — the "later" in
  "merge later" *is* those 17.
  *Correction (operator-surfaced 2026-06-15):* an earlier draft cited "46 live branches" as a
  WIP-graveyard signal — **retracted**. Branch *existence* is a poor WIP proxy here: of 45 remote
  branches, **19 are merged-into-main but deliberately retained** (a benign hygiene habit, zero
  velocity cost), **~9 are automated bot branches** (`cursor/missing-test-coverage-*` spawned daily,
  not operator choice), and "unmerged" itself overcounts because **squash/rebase merges show as
  unmerged** (SHA not an ancestor of `main`). The P9 conclusion does **not** depend on branch count —
  the merge/commit-activity metrics above are unaffected by retention or bots and carry the finding.
  **Why it's a false economy for THIS goal:** 11/11 lanes is not embarrassingly-parallel — the plan's
  own "FEC grounding is the SYSTEMIC W2 blocker" is a *shared* dependency. By **Amdahl** you cannot
  parallelize past the serial bottleneck (parallel lanes in front of an unfixed root pile up as WIP
  or need redoing); by **Little's Law** a solo operator's per-lane cycle time *rises* with WIP — four
  lanes at once finish *later*, not sooner, plus the rebase/collision tax. One shipped lane > four
  70%-done lanes (inventory that decays and conflicts as `main` moves). Legitimate parallelism (per
  `agent-fanout-restraint`): independent subtasks / conclusion-only sweeps / adversarial verification
  — **after** the shared blocker is fixed, not before.

---

## 4. The core question: more enforcement, or another way?

### Recommendation: **NOT more enforcement. Subtract enforcement; add external constraint.**

The instinct — and this repo's reflex — is to write a rule against each pattern. **That instinct
is itself pattern P3.** I recommend against it, and defend that below.

### Why more enforcement will fail (defense)

1. **It already failed at scale.** There are 282 CI gates, 62 governance scripts, 43 rules, 18
   hooks. Under all of it, north-star effort is *18%* and falling (8% in the last 50 commits).
   The enforcement surface grew while the outcome did not. More of a thing that isn't working
   is not the fix.
2. **The enforcement is the addiction object.** 20% of commits *are* governance. Adding rules
   feeds the exact displacement behavior we're trying to stop. You cannot dig out of a hole
   with the shovel that's digging it.
3. **Self-enforcement is self-bypassable.** Every gate in this repo ships with a `*_BYPASS=1`
   escape, and the operator is solo. A rule a person can wave through at 1 a.m. with no reviewer
   (P1) is a suggestion, not a control. Internal rules cannot bind the person who writes them.
4. **Each rule is a liability.** Every new gate is more surface to maintain, more thrash (P5),
   more build-then-demolish risk (P2). Enforcement has *negative* marginal return here.

### What to do instead — constraints, not controls (ranked by leverage)

1. **Restore an external checkpoint (fixes P1 — highest leverage).** Re-introduce a review gate
   the operator *cannot* self-approve. Options, cheapest first: (a) an **AI reviewer that must
   PASS each PR against one question — "does this advance 11/11 lanes? if no, why is it merging?"**
   — and whose verdict is recorded; (b) a mandatory **24-hour cool-down** on any non-north-star
   PR (kills the 30-min self-merge and the burst); (c) a human reviewer if one is ever available.
   The point is friction the solo operator can't unilaterally remove.
2. **One scoreboard, not gates.** SessionStart shows exactly two numbers: lanes green (n/11) and
   7-day north-star %. No rule fires; the mirror does the work. You can't game a number you stare at.
3. **Meta-work freeze (fixes P3/P4/P7).** No new rules/hooks/skills/governance/plan files until
   11/11 green. Enforce by *removing* the ability, not adding a rule — flip `pre_write_plan_mint_gate`
   to default-deny, and block writes under `.codex/rules|hooks|governance` behind an explicit
   in-turn override.
4. **Subtraction quota (fixes P2).** Adopt the repo's own dormant rule: any change that adds
   machinery must remove at least as much. Better: a standing target to cut the 282 gates to <50.
5. **WIP = 1, enforced by reaping (fixes P5/P6).** One active branch. Auto-delete the rest. The
   worktree-reap machinery already exists — point it at *parallelism*, not just merged branches.
6. **Time edges (fixes V1/V2).** One recovery day/week with zero commits; a hard daily stop.
   Circadian regularity is a documented ADHD stabilizer and directly attacks the binge cadence.

### The meta-principle

> You cannot out-*rule* a self-governance problem. A solo operator's internal rules are all
> self-bypassable, and writing them is the very displacement behavior to be cured. The leverage
> is **external constraint** (a checkpoint you can't wave through), **radical subtraction** (shrink
> the surface that absorbs displacement energy), and **a single visible metric** (so progress is
> measured by output, not by process). Constraints bind; controls accumulate.

---

## 5. Operator context incorporated (2026-06-15 corrections)

Two operator corrections were received and verified against history; both are upheld.

### 6a. CI was right-sized, not just churned — and it now *works*

| Snapshot | Workflows | YAML lines |
|---|---|---|
| 2026-05-10 (peak) | 24 | 3,721 |
| 2026-06-13 (pre-trim) | 21 | 3,241 |
| **HEAD (now)** | **12** | **1,947** |

GitHub CI surface roughly **halved** (−43% workflows / −40% lines vs pre-trim; −50% / −48% vs
peak). The shift-left philosophy is sound for a solo dev: heavy, repeatedly-redundant checks
(R1B semantic-cache re-reads, repeat full-ADG re-runs) were moved out of per-push CI to local
**preemptive** runs. Corroborated by `485fddc5` (ADG-Delta → workflow_dispatch-only, "solo
workflow"), `fb13b27b` (right-size on-PR surface), `9afd1448` (rationalize Actions baseline).

### 6b. The prior CI was red theater; the refactor *restored* the checkpoint

History shows pre-refactor CI was **100% failing and routinely bypassed** (`6adee442`
"Unblock pre-existing CI failures", `50a0a4f4` "make contract-gates pass on PRs",
`eb5b209a` "fail closed summary routing"). A CI that always fails and is always bypassed is
**not** an external checkpoint — it is noise that trains the operator to ignore red. Taking it
to **lean green-and-passing** (verified on PRs #378, #379) is a genuine *restoration* of the
correctness brake, not a removal.

### 6c. What this changes in the analysis

- **Retracted:** the earlier claim that shift-left "deepens the P1 hole." It does the opposite
  for the *correctness* dimension — it replaced a non-functioning gate with a working one.
- **Reclassified:** the CI right-sizing commits are **legitimate debt paydown**, aligned with
  Recommendation #4 (subtraction), not displacement. The headline displacement % is modestly
  overstated by the keyword classifier for this reason.
- **Sharpened (unchanged in spirit):** the open hole is now precisely the **judgment**
  checkpoint (§3c P1a vs P1b). Do **not** re-add CI to fix it — CI already works and is rightly
  lean. The single missing brake is a cheap *"does this advance 11/11 lanes?"* gate the operator
  cannot self-approve (Recommendation #1). Keep heavy ADG shifted-left and local; keep CI lean and
  green; add exactly one judgment gate. Three different concerns — do not conflate them.

## 6. Definition of done for *this* recommendation

This report succeeds only if it results in **subtraction and one external checkpoint**, not a
44th rule. If the next action taken is "write a new gate to enforce the above," the analysis was
not absorbed — that outcome would itself be a data point confirming P3.

---

## 7. Before/After the pivot (`2f83d4bb` · 2026-06-10 17:10 UTC) — did it work?

Cohorts: **BEFORE** = 500 commits / 31.6 days (2026-05-09 → 06-10); **AFTER** = 284 commits /
4.8 days (06-10 → 06-15). Normalized per-day. Figure: [pivot_before_after.png](pivot_before_after.png).

| KPI | Before | After | Δ | Read |
|---|---|---|---|---|
| North-star **code** commits / day | 3.4 | **12.0** | **+253%** | ✅ real product output tripled |
| North-star code % of commits | 22% | **30%** | **+8pp** | ✅ composition improved |
| PRs merged / day | 0.28 | 4.58 | +1536% | ✅ discrete deliverable cadence |
| North-star % (subject) | 37% | 41% | +4pp | ✅ modest |
| Governance % of commits | 24% | 24% | **0pp** | ⚠️ meta-work did **not** shrink |
| Plan-touching commits / day | 2.2 | 10.0 | +355% | ⚠️ (partly bulk moves; still up) |
| Thrash/undo % | 10% | 11% | +1pp | ⚠️ flat |
| Commits / day | 15.8 | 39.5 | +150% | ⚠️ velocity binge (unsustainable) |

**Milestone:** the **first green generated lane** — ibm_bullets `X3_ALLOW` (`f678fb91`, 2026-06-14) —
landed **after** the pivot. Before the pivot there were zero green lanes; the realignment preceded
the first real product win.

**Verdict — DERIVED:** the pivot succeeded on its primary job (north-star *code* now ships, and a
lane went green), and composition moved the right way (+8pp). It did **not** shrink the meta-work —
governance held at 24% and plan/thrash were flat; they were *swamped* by a +150% velocity binge
rather than reduced. So the fear-driven orthogonal capture is **still present in absolute terms**;
it now runs *alongside* more real work instead of *instead of* it. Next gain = cut the flat 24%, not
add more output on top.

## 8. Beating the fear + the ADHD loop — the minimal enforcement set

> The request: "what hooks/rules help me get away from my irrational fears and ADHD?" The honest
> answer is **a small set of constraint/capture hooks, each paid for by deleting old gates** — net
> enforcement surface must **shrink**. Adding 44 more rules *is* the disease (P3). The fear is
> *loss of an orthogonal idea*; the cure is **trusted capture + guaranteed resurfacing**, not acting
> on the idea. These hooks make capture frictionless and resurfacing certain — that is what dissolves
> the fear.

| # | Hook / rule | Type | Attacks | Add or flip |
|---|---|---|---|---|
| H1 | **Parking-lot weekly-review nudge** (SessionStart): if `PARKING_LOT.md` has lines unreviewed >7 days, surface them | capture-support | **the fear directly** — makes "you WILL see this again" true; without it the lot is a black hole and the build-now reflex returns | ADD |
| H2 | **North-star scoreboard** (SessionStart banner): lanes `n/11` + 7-day north-star % | mirror | target visibility; replaces reading 43 rules at startup | ADD |
| H3 | **Judgment brake** (PreToolUse on Write to `.codex/rules\|hooks\|governance\|plans/`): one prompt — "not north-star code; 1-line: why now, or park it?" — answer logged | external friction (the one missing brake, §3c P1b) | the displacement *act*, at the moment it happens; the only gate that asks *should this exist* | ADD (replaces ~230 others) |
| H4 | **Plan-mint default-DENY** (`pre_write_plan_mint_gate.py`) | constraint | plan-as-displacement (P4); flip warn→block | FLIP |
| H5 | **Subtraction quota** (PreToolUse): an additive governance commit blocks unless it removes ≥ as much (the repo's dormant rule, wired) | constraint | build-then-demolish + sprawl (P2/P3) | WIRE |
| H6 | **Time-edge nudge** (Stop/SessionStart): flag round-the-clock / no-recovery-day cadence | gentle | the binge + time-blindness (V1/V2) | ADD (optional) |
| H7 | **WIP=1 gate for north-star lanes** (SessionStart/PreToolUse): block creating a new north-star worktree/branch while another north-star lane is unmerged; the worktree machinery already tracks lanes — flip it to enforce the *existing* `apps-rg-execution-bias` "WIP=1" rule. Pair with a **rebase-tax meter** that surfaces sync-merge + collision counts so the parallelism cost is visible | constraint (the hardware-can't-rationalize-it brake) | **P9** — parallelism-as-permission; the merge/rebase-later tax | WIRE (rule already exists) |

**The binding rule for all of the above:** *every hook added must be paid for by deleting old gates.*
Recommended net move: **+3–4 new constraint/capture hooks (H1, H2, H3, opt. H6), 3 flips/wires of
*existing* rules (H4, H5, H7 — no new surface), and −230 correctness gates** (282 → ~50). If the
surface grows, the recommendation has been inverted into the very pattern it diagnoses. Note H7 (WIP=1)
and H5 (subtraction quota) wire rules that **already exist and are simply unenforced** — the cheapest
wins, since the parallelism tax (P9) and build-then-demolish (P2) are both governed by doctrine the
repo already wrote and then rationalized away.

**Why this beats the fear specifically:** H1+H2 make it *safe* to park an orthogonal idea (it is
captured, it will resurface, and the target stays visible), so the brain no longer needs to build it
*now* to feel safe. H3+H4+H5 add friction to the *act* of building it now. Capture removes the
motive; friction removes the means. Neither alone works — together they let you stay on the lane
while *trusting* that nothing is lost.

## Appendix — reproduction

- `git log --merges -341 --pretty='%H|%ai|%s'` → merge cadence
- `git log --no-merges -2000 --pretty='C|%H|%ai|%s' --shortstat` → churn/timing/classification (`/tmp/dna.py`)
- `search_pull_requests: repo:… is:pr is:merged` (317) vs `… review:none` (317) → F1
- Figure generator: `/tmp/dnaviz.py` → [forensic_dna_study.png](forensic_dna_study.png)
- Pivot anchor: `git log --diff-filter=A -- apps-rg-execution-bias.md` → `2f83d4bb` @ 2026-06-10 17:10 UTC
- Before/after: `git log --no-merges -500 2f83d4bb~1` vs `git log --no-merges 2f83d4bb..HEAD` (`/tmp/ba.py`) → [pivot_before_after.png](pivot_before_after.png)
