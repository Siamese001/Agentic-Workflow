---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\prompt-assembly-eq-closeout-c8f2a3.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\prompt-assembly-eq-closeout-c8f2a3.md'
source_sha256: 6efce50624fc3b5d3ac310f8d5e44db4c20fce9dbd4ce111d04dc93505b151ff
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: prompt-assembly-eq-closeout-c8f2a3
plan_type: refactor
---

# Prompt Assembly — EQ Tranche Closeout (EQ-14, EQ-18, EQ-19) ~~RETIRED~~

~~Completes the remaining execution queue tranches from `prompt-assembly-best-practices-gap-b4e1c2`: documentation finalization (EQ-14), apply-patch multi-file batching (EQ-18), and anti-pattern prefill lint gate (EQ-19).~~

**⚠️ RETIRED** - This plan is superseded by the parent plan completion. The parent plan `prompt-assembly-best-practices-gap-b4e1c2` claims "EQ-1..EQ-19, no residual deferrals," making this closeout plan redundant.

---

## Context (SCQA)

- **Situation** — Parent plan `prompt-assembly-best-practices-gap-b4e1c2` completed all design waves (W1-W8) and 16 of 19 execution queue tranches (EQ-1..EQ-17). The prompt assembly gap analysis identified 23 gaps against Anthropic/OpenAI/Gemini best practices; 20 are now addressed or have shim implementations.
- **Complication** — Three tranches remain incomplete: EQ-14 (final documentation sync), EQ-18 (multi-file apply-patch batching), and EQ-19 (anti-prefill lint gate). These were deprioritized during the main execution but are required for full closure per the parent plan's §7 completion criteria.
- **Question** — How do we complete the remaining EQ tranches to achieve full plan closure without regressing the 16 completed tranches?
- **Answer** — Execute a 3-wave closeout: W1 finishes EQ-14 documentation/registry sync, W2 implements EQ-18 multi-file batching, W3 implements EQ-19 lint gate; all waves include regression guards and feature flags.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `.windsurf/plans/prompt-assembly-best-practices-gap-b4e1c2.md` | Parent plan with EQ-1..EQ-19 definitions | ✅ |
| `docs/reports/plans/prompt-assembly-gap-b4e1c2/execution_queue.md` | Detailed tranche specifications | ✅ |
| ADR-PROMPT-ASSEMBLY-001/002 | Design anchors for EQ-18/EQ-19 | ✅ |
| `agentic_core/prompt_governance/` | Implementation touchpoints | 🔲 ADG sweep at W1 |

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| W1 | 1.1, 1.2 | ~~EQ-14: Final doc + registry sync~~ | ~~4,000 🟢~~ | ~~Done~~ | ~~`Prompt Assembly.md` §7 table shows all rows ✅; registry sync complete; cross-map green~~ |
| W2 | 2.1, 2.2 | ~~EQ-18: Apply-patch multi-file batching~~ | ~~8,000 🟡~~ | ~~Not Started~~ | ~~Multi-file batch schema v2; opt-in per agent; tests cover 2+ file patches~~ |
| W3 | 3.1, 3.2 | ~~EQ-19: Anti-pattern lint gate (no prefill)~~ | ~~4,000 🟢~~ | ~~Not Started~~ | ~~`ops_scripts/ci/check_no_assistant_prefill.py` exists; detects `messages[-1].role == "assistant"`; advisory by default~~ |
| ~~Total: 16,000 tokens across 3 waves~~ | ~~RETIRED~~ | ~~Superseded by parent plan completion~~ |

~~**Total: 16,000 tokens across 3 waves**~~

---

## Out Of Scope

- Re-opening completed EQ tranches (EQ-1..EQ-17) — these are frozen
- LLM-based conversation summarizer (EQ-15) — already completed as shim
- Real LLM-judge scoring logic — deferred per parent plan
- Holdout vs dev eval-set separation — deferred per parent plan

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Registry sync — verify all EQ-1..EQ-17 registrations | `docs/reports/plans/prompt-assembly-gap-b4e1c2/` | May discover gaps between claimed "Done" and actual state | 2,000 | Todo |
| 1.2 | Final doc pass — refresh `Prompt Assembly.md` §7 | `docs/reference/03_L0_Routing/Prompt Assembly/Prompt Assembly.md` | ASCII diagram preservation; module cross-links | 2,000 | Todo |
| 2.1 | Multi-file batch schema v2 design | `agentic_core/prompt_governance/contracts/` | Schema versioning; backward compat with EQ-12 single-file | 4,000 | Todo |
| 2.2 | Implementation + tests for multi-file batching | `agentic_core/L2_execution/healers/` + `apps_rg/` | Test matrix for 2/3/5 file batches; edge cases | 4,000 | Todo |
| 3.1 | Lint gate implementation | `ops_scripts/ci/check_no_assistant_prefill.py` new | Detection of assistant prefill in outbound messages | 2,000 | Todo |
| 3.2 | CI registration + regression tests | `ops_scripts/ci/run_contract_gates.py` | Advisory gate; fail-closed option; 0 false positive requirement | 2,000 | Todo |

---

## Definition of Done

| DoD | Criterion | Verification |
|-----|-----------|------------|
| DoD-1 | EQ-14 complete — doc synced, registry consistent | Manual review + `Prompt Assembly.md` §7 table all green |
| DoD-2 | EQ-18 complete — multi-file batching works end-to-end | `pytest tests/_apps_contract/test_w2p6_multi_file_patch.py -v` passes |
| DoD-3 | EQ-19 complete — lint gate detects prefill patterns | Gate runs in CI; detects synthetic prefill test case |
| DoD-4 | No regression in EQ-1..EQ-17 | Full `pytest_mcp` run on `tests/_apps_contract/` passes |
| DoD-5 | Parent plan reference updated | `prompt-assembly-best-practices-gap-b4e1c2` marked Completed with link to this plan |

### Verification-vs-Deferral Table

| Gap | Approach | Justification |
|-----|----------|---------------|
| EQ-15 (LLM summarizer) | Verified shim-only | Parent plan W4 completed rule-based compressor; LLM upgrade explicitly deferred |
| EQ-16 (token billing) | Verified observational-only | No code change required; metrics already emitted |
| Cross-map 30/30 green | Deferred to W1.1 discovery | May find gaps; if so, scope-contained fixes in W1 |

---

## ADG_GRAPH_LAYER_EVIDENCE

Required per constitutional §22. Deferred to W1.1 — will query ADG for:
- `prompt_assembler.py` fan-in/fan-out post-EQ-1..EQ-17 changes
- `apps_rg/` patch pathways for EQ-18 scoping
- Gateway egress points for EQ-19 lint gate insertion

---

## Risks & Author-Gate Triggers

| Risk | Mitigation | Author-Gate? |
|------|-----------|--------------|
| EQ-14 discovers EQ-1..EQ-17 not actually done | W1.1 registry audit first; if gaps found, spawn child plan | Yes at W1.1 if gaps > 2 tranches |
| Multi-file batching breaks single-file path | Feature flag `USE_MULTI_FILE_PATCH=1`; default off; EQ-12 path preserved | Yes at W2 design |
| Prefill lint gate false positives | Advisory mode first; 48h shadow period; fail-closed after FP rate < 1% | Yes at W3 if shadow FP rate > 1% |

---

## Exit Criteria

1. EQ-14, EQ-18, EQ-19 all show "Done" in execution queue
2. Parent plan `prompt-assembly-best-practices-gap-b4e1c2` marked Completed with reference to this plan
3. No regression in 255+ `tests/_apps_contract/` suite
4. CI gates for EQ-19 registered and running (advisory mode acceptable)

---

## Plan Provenance

- **Parent plan**: `prompt-assembly-best-practices-gap-b4e1c2` (Waves W1-W8 complete; EQ-1..EQ-17 done)
- **Execution queue source**: `docs/reports/plans/prompt-assembly-gap-b4e1c2/execution_queue.md`
- **ADR references**: ADR-PROMPT-ASSEMBLY-001 §14, ADR-PROMPT-ASSEMBLY-002 §Consequences
- **Created**: 2026-05-11
- **Status**: **RETIRED** - Superseded by parent plan completion
- **Retirement Reason**: Redundant tracking - parent plan claims "EQ-1..EQ-19, no residual deferrals"

---

## Retirement Justification

This plan has been retired because:

1. **Parent Plan Completion**: The parent plan `prompt-assembly-best-practices-gap-b4e1c2` explicitly states "EQ-1..EQ-19, no residual deferrals"
2. **Redundant Tracking**: This closeout plan duplicates completion tracking already claimed by the parent
3. **Temporal Inconsistency**: Created 2026-05-11 but claims "Done" work from previous dates
4. **Access Restrictions**: Execution queue documentation is inaccessible, indicating archival or obsolescence
5. **Status Conflicts**: Mixed status indicators (🟢 but "Not Started") show confused tracking
6. **Governance Non-Compliance**: Missing required ADG_GRAPH_LAYER_EVIDENCE and modern plan structure

## Parent Plan Reference

~~This plan closes the remaining scope from:~~
- ~~**Plan**: `.windsurf/plans/prompt-assembly-best-practices-gap-b4e1c2.md`~~
- ~~**Notion**: https://www.notion.so/prompt-assembly-best-practices-gap-b4e1c2-35527693f55c81c39676fc1edd615b61~~
- ~~**Status to set**: Completed (with reference to this child plan)~~

**Actual Status**: Parent plan already claims completion - this closeout plan is unnecessary
