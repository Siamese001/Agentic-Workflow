---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\exec-summary-judge-regen-loop-closure-d8f3a1.md'
original_relative_path: '_archive\\2026-05\\exec-summary-judge-regen-loop-closure-d8f3a1.md'
source_sha256: 1ba60af2c09311f343e75864640ccd3e39ba41a5b573f6465db0b1cec968cc73
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: exec-summary-judge-regen-loop-closure-d8f3a1
plan_type: product
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: docs/reports/cursor/exec_summary_judge_regen_loop_w0_receipt.md
dod_exempt: false
---

# Executive Summary — Judge Regen Loop Closure (W4 + Deferred)

**North star:** Close the **product loop** left open by [core-same-authority-incremental-regen-e7a4b1.md](core-same-authority-incremental-regen-e7a4b1.md): after a real judge/gate trigger, same-authority regen must yield a **lane-accepted** draft — **X2 green after regen, before judge rescore** — not only chassis receipts with post-regen revert.

**Parent (COMPLETED):** Chassis proved (`SameAuthorityRegenRunner`, `messages[]`, Brown `exec_summary_20260525_122058`). Parent W4 unblock criterion **#4 failed** (`post_regen_x2_failed_after_x2_repair`).

**Anti-pattern:** Re-open parent plan; weaken X2 gates; add narrative X2 proxies for judges; move rubric/X3 policy into core.

> **plan_id discipline:** `exec-summary-judge-regen-loop-closure-d8f3a1`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: Completed
PLAN_HARDENING: applied_2026-05-25 deferred_followup_v1
CURRENT_WAVE: DONE
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-25
EXECUTION_APPROVED: true
PLAN_COMPLETE: plan=exec-summary-judge-regen-loop-closure-d8f3a1 waves=W0-W5 receipt=docs/reports/cursor/exec_summary_judge_regen_loop_closeout_20260525.md brown=exec_summary_20260525_124637
WAVE_COMPLETE: plan=exec-summary-judge-regen-loop-closure-d8f3a1 wave=0 note="ADR-086 apps orchestrator PD-1 + w0 receipt"
WAVE_COMPLETE: plan=exec-summary-judge-regen-loop-closure-d8f3a1 wave=1 note="lane unify + env defaults + assistant-only thread"
WAVE_COMPLETE: plan=exec-summary-judge-regen-loop-closure-d8f3a1 wave=2 note="prepare + source_sensitive strip + shape-only x2 repair gate"
WAVE_COMPLETE: plan=exec-summary-judge-regen-loop-closure-d8f3a1 wave=3 note="judge_directed_regen.py core contract + tests"
WAVE_COMPLETE: plan=exec-summary-judge-regen-loop-closure-d8f3a1 wave=4 note="x2 pre/post regen snapshots on live path"
WAVE_COMPLETE: plan=exec-summary-judge-regen-loop-closure-d8f3a1 wave=5 note="Brown 124637 cycle accepted post-regen X2 green before rescore"
PARENT_PLAN: core-same-authority-incremental-regen-e7a4b1
PARENT_STATUS: Completed (W0–W3)
DEFERRED_FROM_PARENT: W4 JudgeDirectedRegenOrchestrator, lane dual-path, post-regen X2 acceptance, Brown loop-close re-proof

NOTION_PAGE_ID: 36b27693-f55c-8186-8829-c504c6ba97ad
NOTION_PLAN_URL: https://www.notion.so/exec-summary-judge-regen-loop-closure-d8f3a1-36b27693f55c81868829c504c6ba97ad
PLAN_CREATED: slug=exec-summary-judge-regen-loop-closure-d8f3a1 path=.cursor/plans/exec-summary-judge-regen-loop-closure-d8f3a1.md status=Not Started notion_page=36b27693-f55c-8186-8829-c504c6ba97ad

---

## Context (SCQA)

- **Situation** — Core regen chassis is live: `apps_rg` delegates to `SameAuthorityRegenRunner`; Brown run emits `same_authority_regen_receipt.json`, `provider_request_regen.json`, prescriptive `REGEN_DELTA_v1` user turn.
- **Complication** — Brown `122058`: core heal **PASS**, lane **reverts** draft (`x2_exec_summary_meta_filler_zero`, `x2_source_sensitive_phrases_supported`); X3 stays `X3_REVIEW_JUDGE_SOFT_FAIL`. Lane may still use legacy message paths on multi-cycle follow-ons. Parent W4 orchestrator blocked.
- **Question** — How do we make judge-directed regen **change shippable output** without breaking spine law?
- **Answer** — **Apps-owned loop policy** (trigger, X2 re-check, rescore, disposition) + **optional thin core orchestrator** only if boundary-safe; unify lane on core bridge; fix post-regen X2 acceptance; re-prove on Brown.

---

## Deferred Scope Register (from parent)

| ID | Deferred item | Owner | This plan wave |
|----|---------------|-------|----------------|
| DS-1 | `judge_directed_regen.py` / `JudgeDirectedRegenOrchestrator` | Core (protocol) + apps (policy) | W3 |
| DS-2 | Lane multi-cycle: legacy `build_judge_remediation_user_message` vs core bridge | apps_rg | W1 |
| DS-3 | Post-regen X2 green before judge rescore (parent unblock #4) | apps_rg | W2, W5 |
| DS-4 | Separate `x2_gate_outputs` before/after regen snapshots | apps_rg | W4 |
| DS-5 | `judge_remediation_cycles.json` **accepted** (not `post_regen_x2_failed_*`) | apps_rg | W5 |
| DS-6 | Semantic ceiling > 1 (`max_semantic_regen_attempts`) | apps policy | Out of scope until W5 PASS |
| DS-7 | Dual env flags (`JUDGE_REGEN` + `CORE_SAME_AUTHORITY_REGEN`) → product default | apps_rg | W1 |
| DS-8 | Link operator ship ([exec-summary-operator-ship-a3f7c2.md](exec-summary-operator-ship-a3f7c2.md)) for DRAFT_READY vs CERTIFIED | apps_rg | W2 (coordination only) |

**Stays out of scope (parent + this plan):**

- X3 policy / 2-of-3 judge quorum in core
- Rubric / X2 gate **definitions** in core (apps validators SSOT)
- L5 executing repair or emitting disposition
- Claude-as-author (Qwen/vLLM profile unchanged)
- Re-teaching frozen compile / provider substitution

---

## Product Decisions (lock W0 — Author-Gate if architecture fork)

| ID | Decision | Default |
|----|----------|---------|
| PD-1 | **Orchestrator placement** | Prefer **apps lane orchestration** calling existing `SameAuthorityRegenRunner`; add core `JudgeDirectedRegenOrchestrator` only if it stays policy-free (no rubric/X2 IDs). |
| PD-2 | **Single regen path** | All judge remediation cycles use `executive_summary_same_authority_regen_bridge` when core runner enabled; no legacy PROMPT_LOCK in user turns. |
| PD-3 | **Loop success** | `judge_remediation_cycles.cycles[].accepted=true` AND no `reverted=post_regen_x2_failed*` on success path. |
| PD-4 | **Ordering** | Emit `x2_gate_outputs_pre_regen.json` + `x2_gate_outputs_post_regen.json` (or equivalent) before judge rescore. |
| PD-5 | **Default flags** | Product path: `APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1` and `APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN=1` without operator env (align [exec-summary-operator-ship-a3f7c2.md](exec-summary-operator-ship-a3f7c2.md)). |
| PD-6 | **No gate weakening** | Fix regen output / repair policy / floors — not X2 PASS by deleting gates. |

---

## Architecture Invariants

| ID | Invariant |
|----|-----------|
| INV-1 | `SameAuthorityRegenRunner` remains E4 Heal subtype; no parallel regen side channel. |
| INV-2 | Core regen modules stay app-agnostic (`check_same_authority_regen_boundary.py` PASS). |
| INV-3 | Frozen compile + same provider preserved on every regen attempt. |
| INV-4 | `semantic_regen_attempt_index` ≠ `transport_retry_count`. |
| INV-5 | App owns trigger, floors, X2 re-check, judge rescore, X3/Exit. |
| INV-6 | Parent plan stays **Completed**; this plan owns loop closure only. |
| INV-7 | Live Brown re-proof required for plan PASS (not unit tests alone). |

---

## Parent W4 Unblock Criteria (traceability)

| # | Parent criterion | Status at parent close | This plan |
|---|------------------|------------------------|-----------|
| 1 | W1 NC tests green | ✅ Met | Maintain (regression) |
| 2 | W2 receipt + semantic/transport separation | ✅ Met | Maintain (regression) |
| 3 | W3 delegation; no duplicate apps PROMPT_LOCK | ✅ Met | W1 harden |
| 4 | Brown: X2 green after regen before rescore | ❌ **Failed** | **W2 + W5** |

---

## Execution Waves

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.0–W0.2 | Charter, DS register, Author-Gate (PD-1 placement) | ~40K | Parent chassis on `main` | ✅ DONE | AG receipt + PD-1 locked |
| W1 | W1.0–W1.2 | Lane dual-path → core bridge only; env defaults | ~70K | No lane rewrite beyond exec summary | ✅ DONE | Core bridge + defaults on |
| W2 | W2.0–W2.2 | Post-regen X2 acceptance (meta_filler, source_sensitive) | ~80K | Brown failure IDs known | ✅ DONE | prepare + shape-only repair gate |
| W3 | W3.0–W3.1 | Optional `JudgeDirectedRegenOrchestrator` or ADR “apps-only” | ~60K | W0 PD-1 | ✅ DONE | ADR-086 + `judge_directed_regen.py` |
| W4 | W4.0 | Before/after X2 artifact snapshots + timeline receipt | ~35K | W1 wired | ✅ DONE | pre/post snapshots Brown 124637 |
| W5 | W5.0–W5.1 | Live Brown re-proof + closeout receipt | ~90K | vLLM + judges available | ✅ DONE | Cycle accepted; post-regen X2 0 failed |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.0 | Deferred scope register on disk | This plan + parent cross-link | Traceability | ~10K | 🔲 TODO |
| W0.1 | Author-Gate PD-1 orchestrator placement | AG packet | Core vs apps boundary | ~15K | 🔲 TODO |
| W0.2 | Migration / scope receipt | `artifacts/governance/` | Parent W4 handoff | ~15K | 🔲 TODO |
| W1.0 | `executive_summary_lane.py` cycle unification | Lane + remediation | Dual path | ~35K | 🔲 TODO |
| W1.1 | Default env / repair policy | `executive_summary_repair_policy.py` | Operator flags | ~20K | 🔲 TODO |
| W1.2 | Delegation regression tests | `test_*regen*` | Bridge coverage | ~15K | 🔲 TODO |
| W2.0 | Post-regen X2 repair acceptance policy | `judge_remediation`, X2 validators usage | Brown revert | ~40K | 🔲 TODO |
| W2.1 | Monotonicity + floors alignment | remediation + repair policy | Word/ledger floors | ~25K | 🔲 TODO |
| W2.2 | X2 repair pytest (fixture + policy) | tests/apps_rg | No live LLM | ~15K | 🔲 TODO |
| W3.0 | Orchestrator module or ADR | `regen/judge_directed_regen.py` OR apps-only ADR | PD-1 outcome | ~40K | 🔲 TODO |
| W3.1 | Orchestrator unit tests | tests/regen or apps | Boundary | ~20K | 🔲 TODO |
| W4.0 | Pre/post X2 snapshot emit | lane artifact writers | Hostile verifier | ~35K | 🔲 TODO |
| W5.0 | Brown live run | `python -m apps_rg --section executive_summary …` | Real providers | ~60K | 🔲 TODO |
| W5.1 | Closeout receipt + Notion complete | `docs/reports/apps_rg/` | DoD-5 loop | ~30K | 🔲 TODO |

---

## Definition of Done

| ID | Criterion | Proof |
|----|-----------|-------|
| DoD-0 | `author_gate_receipt_ref` populated (W0 PD-1) | Non-empty path in YAML |
| DoD-1 | Parent chassis regression: regen pytest + boundary CI exit 0 | Command output in receipt |
| DoD-2 | No dual regen user-message path on product default | Grep/CI assertion |
| DoD-3 | Post-regen X2 policy tests PASS (meta_filler, source_sensitive) | pytest path listed in receipt |
| DoD-4 | Pre/post regen X2 snapshots emitted on live path | Artifact paths in run_dir |
| DoD-5 | **Brown live:** `judge_remediation_cycles` cycle **accepted** without `post_regen_x2_failed_after_x2_repair` | `docs/reports/apps_rg/exec_summary_judge_regen_loop_brown_*_receipt.md` |
| DoD-6 | X2 pass **after** regen evidenced **before** judge rescore in timeline | Receipt §ordering |
| DoD-7 | Orchestrator delivered (module) or explicitly waived (ADR apps-only) | File path + test |
| DoD-8 | Notion Completed only after DoD-0–7 | `PLAN_COMPLETE` marker |
| DoD-9 | Smoke: `python -m apps_rg --section executive_summary` (Brown args) exits per operator tier | Exit code + stdout matrix doc |

### Verification vs Deferral

| Item | In scope | Deferred |
|------|----------|----------|
| Loop acceptance on Brown | ✅ W5 | — |
| `max_semantic_regen_attempts` > 1 | — | After W5 PASS |
| CERTIFIED 3/3 judges | — | [exec-summary-operator-ship-a3f7c2.md](exec-summary-operator-ship-a3f7c2.md) |
| Core X3 / quorum | — | Parent out of scope |

---

## Live Brown Proof Shape (W5 — mandatory)

Same CLI as parent (no `--proof-mode`):

```bash
set APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1
set APPS_RG_EXEC_SUMMARY_CORE_SAME_AUTHORITY_REGEN=1
python -m apps_rg --section executive_summary --target-company "Brown & Brown" --target-role "SVP IT Strategy & Innovation" --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt --provider qwen_vllm --allow-non-allow-exit-zero --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

| Artifact | Required |
|----------|----------|
| `same_authority_regen_receipt.json` | Core heal PASS |
| `provider_request_regen.json` | `messages[]` thread proof |
| `judge_remediation_cycles.json` | `accepted: true`, no post-regen X2 revert |
| `x2_gate_outputs_pre_regen.json` | Snapshot (W4) |
| `x2_gate_outputs_post_regen.json` | All targeted gates PASS |
| `x1d_llm_judge_outputs.json` | Rescore after post-regen X2 |
| `x3_disposition.json` | Honest status (REVIEW acceptable if documented) |

**PASS for this plan:** DoD-5 + DoD-6 satisfied. **Not required:** X3_ALLOW / 3/3 judges (operator ship).

---

## Wave Closeout Commands (record exit codes)

```bash
python -m compileall agentic_core apps_rg -q
pytest tests/unit/agentic_core/L2_execution/regen/ -q
pytest tests/unit/apps_rg/test_executive_summary_judge_remediation.py tests/unit/apps_rg/test_same_authority_regen_delegation.py -q
python ops_scripts/ci/check_same_authority_regen_boundary.py
# W5 live Brown — command above
```

---

## Merge Acceptance Gate

- [ ] W0 Author-Gate receipt for orchestrator placement (PD-1)
- [ ] W1 single regen path on product default
- [ ] W2 post-regen X2 acceptance tests PASS
- [ ] W3 orchestrator module or apps-only ADR
- [ ] W4 pre/post X2 snapshots on live path
- [ ] W5 Brown receipt: loop **accepted**, ordering proof
- [ ] Parent regression suite still exit 0

---

## Related Plans

| Plan | Relationship |
|------|----------------|
| [core-same-authority-incremental-regen-e7a4b1.md](core-same-authority-incremental-regen-e7a4b1.md) | Parent — chassis COMPLETED |
| [exec-summary-operator-ship-a3f7c2.md](exec-summary-operator-ship-a3f7c2.md) | Exit / DRAFT_READY vs CERTIFIED |
| [exec-summary-l2-x1d-input-parity-c4f8e1.md](exec-summary-l2-x1d-input-parity-c4f8e1.md) | Judge packet parity |

---

## Reference

Parent Brown failure excerpt (`exec_summary_20260525_122058`):

```text
judge_remediation_cycles.stopped_reason: post_regen_x2_failed_after_x2_repair
failed_gate_ids: x2_exec_summary_meta_filler_zero, x2_source_sensitive_phrases_supported
core_same_authority_regen: accepted=true, heal_outcome=PASS
```

Chassis docs: [ADR-085](../docs/adr/ADR-085-same-authority-incremental-regen.md), [envelope spec v1](../docs/reference/L2_execution/same_authority_regen_envelope_spec_v1.md).
