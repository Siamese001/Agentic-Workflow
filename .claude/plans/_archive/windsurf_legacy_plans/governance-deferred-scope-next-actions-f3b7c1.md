---
plan_id: governance-deferred-scope-next-actions-f3b7c1
plan_type: tracker
touches_agentic_core: false
touches_governance_ci: false
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: true
---

# Governance Deferred Scope — Next Actions Tracker

Captures the three deferred next-actions from the W2/B6B reconciliation closeout. No execution in this plan — each action requires its own plan or Author-Gate before any work begins.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DEFERRED
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-12

---

## Context (SCQA)

- **Situation** — W2 Hook Consolidation completed under `windsurf-governance-consolidation-a7c3e9` on 2026-05-12 via W1C R4 waiver + C1-C6 phase-local controls. Deferred plan `windsurf-governance-w2-deferred-b6b-unblock-a8d4e2` retired as stale-premise.
- **Complication** — Three actionable follow-on items were identified during reconciliation closeout but are out-of-scope for any active plan. They need a home to prevent loss.
- **Question** — Where do the three deferred next-actions live so future sessions can pick them up with full context?
- **Answer** — This tracker plan records each action's status, prerequisites, and constraints. No execution occurs here.

---

## Deferred Actions

### DS-1 — `post_setup_worktree.py` Hook Issue

| Field | Value |
|---|---|
| **Type** | Bug / behavior defect candidate |
| **Source** | Observed during W2 consolidation review |
| **Status** | `DEFERRED — Needs scoped Author-Gate plan` |
| **Prerequisites** | New plan required. Author-Gate for `error_handling` or `refactor_scope` decision type before any edits. |
| **Constraints** | No changes to hook behavior without: (1) confirmed RCA of root cause, (2) Author-Gate approval, (3) zero-regression test sweep covering hook manifest. |
| **Risk** | `post_setup_worktree.py` is a governance hook. Incorrect fix could silently disable worktree setup enforcement. |
| **Next step** | Open a new plan scoped to: (a) reproduce the defect, (b) RCA, (c) Author-Gate decision on fix strategy, (d) apply fix with regression tests. |

---

### DS-2 — B6B Post-W2 Shadow Monitoring

| Field | Value |
|---|---|
| **Type** | Observational — no code changes |
| **Source** | B6B shadow runner `artifacts/b6b/b6b_shadow_runner.py` built during W1C as post-W2 monitoring tool |
| **Status** | `DEFERRED — Ready to run; observational only` |
| **Prerequisites** | Real sessions to observe. No plan or Author-Gate required for observation. |
| **Constraints** | ⛔ Read-only. `b6b_shadow_runner.py` must NOT be modified during monitoring. Results go to `artifacts/b6b/shadow_results/`. No enforcement changes permitted based on shadow data alone — requires separate Author-Gate. |
| **Activation** | `python artifacts/b6b/b6b_shadow_runner.py` against real session artifacts. |
| **Expected output** | Hook invocation counts, bypass rates, replacement_for[] chain coverage. Feeds future B6B promotion decision. |
| **Next step** | Run after ≥3 real sessions accumulate under W2 survivor hooks. Review results and open separate plan if promotion criteria warrant action. |

---

### DS-3 — 59→20 Future Hook Consolidation

| Field | Value |
|---|---|
| **Type** | Governance reduction — scope expansion of W2 |
| **Source** | W2 completed 59→(7 survivors + 22 replacement_for entries). Original target was 59→20. Gap of ~32 additional hook consolidations not executed. |
| **Status** | `DEFERRED — Requires new plan + Author-Gate + risk review` |
| **Prerequisites** | (1) ≥14 days of B6B shadow data post-W2 (DS-2 above). (2) Author-Gate `refactor_scope` decision. (3) New standalone plan with wave structure and DoD. (4) Risk review: each additional consolidation risks enforcement gap if replacement_for[] chains break. |
| **Constraints** | ⛔ Zero work on this item without the three prerequisites met. No ad-hoc hook deletions or moves. Any work that changes `hooks.json` in ways not covered by DS-2 monitoring data requires explicit new plan activation. |
| **Hook count baseline** | 59 total as of 2026-05-12; 7 survivors with 22 replacement_for[] entries. |
| **Next step** | After DS-2 shadow data ≥14 days, open new plan. Baseline: `artifacts/governance-baseline/hooks_manifest_pre_w2.json`. |

---

## Dependencies Between Actions

```
DS-2 (shadow monitoring) → gates → DS-3 (future consolidation)
DS-1 (hook bug) → independent → can proceed in parallel
```

DS-1 is independent. DS-2 must produce ≥14 days of data before DS-3 planning begins.

---

## Out Of Scope

- Any actual hook consolidation work (→ DS-3 plan)
- Any fix to `post_setup_worktree.py` (→ DS-1 plan)
- Any changes to `b6b_shadow_runner.py` (→ read-only during DS-2)
- Any enforcement rule changes based on shadow data alone

---

## Definition of Done

DoD-1: All three deferred actions documented with prerequisites, constraints, and next steps.
- Evidence: This file on disk at `.windsurf/plans/governance-deferred-scope-next-actions-f3b7c1.md`
- Status: DONE

DoD-2: Plan registered in Notion Plans DB with Status=Deferred.
- Evidence: Notion page exists for slug `governance-deferred-scope-next-actions-f3b7c1`
- Status: DONE

---

## Footer

```
PLAN: governance-deferred-scope-next-actions-f3b7c1
STATUS: DEFERRED (tracker only — no execution waves)
PARENT_PLAN: windsurf-governance-consolidation-a7c3e9
RETIRED_PLAN: windsurf-governance-w2-deferred-b6b-unblock-a8d4e2
CREATED: 2026-05-12
AUTHOR: Cascade
DS_1_STATUS: DEFERRED — needs scoped Author-Gate plan
DS_2_STATUS: DEFERRED — ready to run; observational only
DS_3_STATUS: DEFERRED — gated on DS-2 ≥14 days + new plan + Author-Gate
```
