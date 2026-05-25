# ADR-086: Judge-Directed Regen Loop — Apps Orchestrator SSOT

**Status:** Accepted (W0)  
**Date:** 2026-05-25  
**Plan:** `exec-summary-judge-regen-loop-closure-d8f3a1`  
**Parent:** ADR-085 / `core-same-authority-incremental-regen-e7a4b1` (COMPLETED)

## Context

ADR-085 delivered `SameAuthorityRegenRunner` and Brown proof of same-authority `messages[]` regen. Product loop still reverted drafts when post-regen X2 failed (`meta_filler`, `source_sensitive`).

## Decision

| Layer | Responsibility |
|-------|----------------|
| **Core** | `judge_directed_regen.py` — step enum + `JudgeDirectedRegenPlan` only (policy-free) |
| **apps_rg** | `executive_summary_judge_regen_loop.py` — prepare, X2 snapshots, thread extension |
| **apps_rg lane** | Trigger, X2 re-check, judge rescore, disposition, revert policy |

**PD-1:** No core rubric/X2 orchestration. Apps call `SameAuthorityRegenRunner` via existing bridge.

## Loop order (locked)

1. Evaluate trigger  
2. Same-authority regen (core)  
3. Prepare candidate (voice + source-sensitive strip + finalize)  
4. X2 pre snapshot  
5. X2 post-regen  
6. Optional X2 repair (eligible gates only)  
7. Judge rescore (after post-regen X2 pass)  
8. Emit receipts  

## Consequences

- Parent W4 deferred scope absorbed without reopening chassis plan.
- Default `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1` on product path.
- Multi-cycle threads append **assistant only**; next cycle uses core prescriptive delta.

## Non-goals

- X3 quorum / operator policy in core  
- Semantic regen ceiling > 1 (until loop closes on Brown)
