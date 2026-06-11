---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\rca-h7-apps-eval-routing-discipline.md'
original_relative_path: 'rca-h7-apps-eval-routing-discipline.md'
source_sha256: e5fb1d431ad466906ab69fac0158aa285e308f28b3aa99a4c951169547d9713a
recovered_status: LOST_RECOVERED
last_commit: 'e614a8e476f'
last_commit_date: '2026-04-21 15:34:22 -0400'
created_date: '2026-04-21'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA — H7: `apps_eval` Routing-Discipline Opt-Out

**Plan reference:** `.windsurf/plans/routing-followups-7a2c91.md` (Phase F3.5)
**Parent gap:** `.windsurf/plans/routing-unification-qwen-abe735.md` §6 H7
**Status:** RCA + topology doc update required
**Date:** 2026-04-21

---

## 1. Observed State

Directory: `@c:\Git\Agentic-Workflow\apps_eval\`

Structure:

```
apps_eval/
  __main__.py
  _telemetry.py
  config/           (5 items)
  engines/          (7 items)
  integrations/     (4 items)
  reasoning/        (8 items)
  scripts/          (2 items)
  services/         (10 items)
  spine/            (2 items)
  types/            (2 items)
  utils/            (2 items)
  validators/       (5 items)
  README.md
  SVP_ENGINEERING_REVIEW.md
  TECHNICAL_SPEC.md
  TEST_STRATEGY.md
```

This is a full-weight application (~50+ Python modules) with its own engines, services, and spine. Unlike `apps_exec`, `apps_lic`, `apps_research`, `apps_rfp`, and `apps_rg` — which **all** consume `vllm_routing_predicates.Provider` (verified in H3 RCA consumer map) — `apps_eval` has **zero** imports of `Provider` per grep.

## 2. What This Means

`apps_eval` is either:

- **(a) Intentionally opt-out** — its use-case does not require the 4-tier routing scheme (e.g. it evaluates models but does not heal)
- **(b) Unintentional drift** — it predates or ignores the routing-SSOT work and should be wired up

The parent plan notes this as **H7 — unannounced opt-out**. "Unannounced" is the key word — no ADR explains why, and no topology doc captures it.

## 3. Why This Matters

An undocumented opt-out is a governance gap:

- Future routing changes may silently fail to cover `apps_eval`
- Consumers of `apps_eval`'s outputs cannot tell whether its model selection is governed by the routing SSOT
- Anti-pattern auditors (per constitutional §22) cannot score `apps_eval` correctly without knowing its intent

## 4. Recommended Fix (lightweight — no code change required)

A 2-step approach:

### Step 1: Verify opt-out is intentional (1k tokens)

Read `apps_eval/TECHNICAL_SPEC.md` + `apps_eval/SVP_ENGINEERING_REVIEW.md` to determine intent. Grep any `model_registry` imports inside `apps_eval/` to check if routing is done through an alternate path.

### Step 2: Write topology ADR (2k tokens)

Create `docs/architecture/adr/ADR-NNN-apps-eval-routing-opt-out.md` that either:

- **Documents the intentional opt-out** — explain why `apps_eval` does not need routing SSOT; mark as opt-out officially
- **Wires apps_eval into routing SSOT** — same as other apps, if the opt-out was unintentional

No code migration is proposed in the ADR itself. If wiring is chosen, a separate plan follows.

## 5. Decision Tree

```
Does apps_eval use any LLM for its core function?
├── NO → intentional opt-out; ADR documents rationale and closes the gap
└── YES → how does it pick the LLM?
    ├── Hardcoded model → ROUTING SSOT VIOLATION; wire through HealingRouter
    ├── Via an alt path (e.g. direct gateway) → document the alt path in ADR
    └── Via HealingRouter already (we missed the import) → no change, update consumer map
```

## 6. Blast Radius

None from this RCA — it produces documentation only. The eventual wire-up plan (if needed) would touch 1–3 files inside `apps_eval/reasoning/` and add routing imports. Low risk.

## 7. Next Action

Schedule Step 1 as a 15-minute read-only investigation. Based on finding, either:

- Write the opt-out ADR (most likely — `apps_eval` appears to be an evaluation harness, not a user-facing healer)
- Or open `.windsurf/plans/apps-eval-routing-wireup-<hash>.md` for a small migration

## 8. Provenance

ADG Provenance: backend=sqlite (consumer map from H3 RCA; directory listing from filesystem MCP)
Constitutional compliance: §22 — no dependency-graph questions asked; enumeration is a directory walk, not a dependency trace.
