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
  PRs self-merged in minutes. There is no friction, no second opinion, no "is this the north
  star?" gate that the operator cannot unilaterally wave through. Every other pattern below
  runs unchecked *because* this one removes the brake. This is a **process/structure** defect,
  not a neurological one.
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
   to default-deny, and block writes under `.claude/rules|hooks|governance` behind an explicit
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

## 5. Definition of done for *this* recommendation

This report succeeds only if it results in **subtraction and one external checkpoint**, not a
44th rule. If the next action taken is "write a new gate to enforce the above," the analysis was
not absorbed — that outcome would itself be a data point confirming P3.

---

## Appendix — reproduction

- `git log --merges -341 --pretty='%H|%ai|%s'` → merge cadence
- `git log --no-merges -2000 --pretty='C|%H|%ai|%s' --shortstat` → churn/timing/classification (`/tmp/dna.py`)
- `search_pull_requests: repo:… is:pr is:merged` (317) vs `… review:none` (317) → F1
- Figure generator: `/tmp/dnaviz.py` → [forensic_dna_study.png](forensic_dna_study.png)
