---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\rca-h3-provider-enum-audit.md'
original_relative_path: 'rca-h3-provider-enum-audit.md'
source_sha256: 788c5211fa747747e9b49ca9170b5cd7afb0ce7bbca4ca781cbf8961579ed686
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RCA — H3: `Provider` Enum Consumer Audit (Post-P5.4)

**Plan reference:** `.windsurf/plans/routing-followups-7a2c91.md` (Phase F3.2)
**Parent gap:** `.windsurf/plans/routing-unification-qwen-abe735.md` §6 H3
**Status:** RCA — completed audit; remaining actions queued
**Date:** 2026-04-21

---

## 1. Observed State (Post-P5.4)

Wave 5 P5.4 extended `Provider` enum (`@c:\Git\Agentic-Workflow\agentic_core\L4_state\config\vllm_routing_predicates.py`) from 2 values (`OPUS`, `LOCAL_VLLM`) to 4 (`OPUS`, `LOCAL_VLLM`, `GEMINI_FLASH`, `GEMINI_PRO`).

Consumer map (grep + visual verification):

| File | Role | Uses | Post-P5.4 semantics |
|---|---|---|---|
| `@c:\Git\Agentic-Workflow\apps_exec\reasoning\ExecOrchestrator.py` | Orchestrator | `Provider.OPUS`, `Provider.LOCAL_VLLM` | ✅ compat preserved |
| `@c:\Git\Agentic-Workflow\apps_lic\reasoning\GovernanceShieldAgent.py` | Orchestrator | `Provider.LOCAL_VLLM` | ✅ compat preserved |
| `@c:\Git\Agentic-Workflow\apps_research\reasoning\ResearchOrchestrator.py` | Orchestrator | `Provider` enum | ✅ compat preserved |
| `@c:\Git\Agentic-Workflow\apps_rfp\reasoning\RfpOrchestrator.py` | Orchestrator | `Provider` enum | ✅ compat preserved |
| `@c:\Git\Agentic-Workflow\apps_rg\bootstrap_runtime.py` | Runtime init | `Provider` enum | ✅ compat preserved |
| `@c:\Git\Agentic-Workflow\apps_rg\reasoning\RgResumeOrchestrator.py` | Orchestrator | `Provider` enum | ✅ compat preserved |

Plus 5 test suites in `tests/unit/apps_*/` confirming behavior.

**Correction to parent plan § P5.4 comment:** the plan noted "12 consumers"; actual count is **6 production + 5 test suites = 11 total code sites**. Close to the estimate but worth recording.

## 2. The Remaining Audit Question

P5.4 added the Flash/Pro values but did **not** audit whether existing callers should migrate from `Provider.OPUS` (a historical Claude-era alias) to the new Gemini-specific values. `Provider.OPUS` is kept for backward-compat but semantically means "high-reasoning cloud model" — which is now `GEMINI_PRO`.

Specifically: when an orchestrator sets `Provider.OPUS`, should the `HealingRouter` still dispatch to a Claude endpoint, or has that intent drifted to mean "use the best cloud model available" (now `GEMINI_PRO`)?

## 3. Decision Criterion

For each of the 6 production consumers, the correct value is determined by:

1. **Is the caller wired to a real Claude endpoint?** — If yes, keep `Provider.OPUS`.
2. **Is the caller using OPUS as a generic "high-tier cloud" sentinel?** — If yes, migrate to `Provider.GEMINI_PRO`.
3. **Is the caller using LOCAL_VLLM and never needs cloud?** — Keep `Provider.LOCAL_VLLM`, unaffected.

The determination requires reading each orchestrator's provider-dispatch logic (not covered in this RCA).

## 4. Recommended Fix (separate plan, NOT executed here)

A 3-phase audit plan:

1. **Read each of the 6 orchestrator `Provider.OPUS` call sites** and classify per §3
2. **Migrate sentinels** — update call sites where OPUS is a generic high-tier sentinel
3. **Deprecate `Provider.OPUS`** if no real Claude consumers remain; add `DeprecationWarning` on enum access; plan deletion for Wave 7

Estimated size: 4k tokens. Safe to execute independently of F1/F2.

## 5. Next Action

Open `.windsurf/plans/provider-enum-opus-audit-<hash>.md` and execute the 3-phase plan above. This RCA satisfies the §4 deferred-audit requirement from parent plan §6 H3.

## 6. Provenance

ADG Provenance: backend=sqlite (grep used only for string-literal matches per constitutional §3.2 exception), consumer map verified
Constitutional compliance: §22 — no dependency-graph questions asked, only literal string matches; grep usage is within policy.
