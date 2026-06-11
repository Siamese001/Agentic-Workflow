---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\exec-summary-anthropic-surgical-regen-f3c8d2.md'
original_relative_path: 'exec-summary-anthropic-surgical-regen-f3c8d2.md'
source_sha256: 376354c6e2297664a945e7f45000fefb7159fb891661fc4d47ef225b896e347f
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: exec-summary-anthropic-surgical-regen-f3c8d2
plan_type: enhancement
touches_agentic_core: false
touches_governance_ci: false
parent_plan: exec-summary-judge-regen-prompt-loop-b9e4c3
---

# Executive Summary — Anthropic-Aligned Surgical Judge Regen

Align apps_rg judge-regen with Anthropic **prompt chaining** and **evaluator–optimizer** patterns: generate once on frozen compile, evaluate in separate judge calls, then apply a **minimal** same-authority delta turn — without truncating judge feedback or re-running the full scratch prompt.

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: —
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-05-26
NOTION_PAGE_ID: 36c27693-f55c-81bc-a4a3-de1022a6e532

PLAN_CREATED: slug=exec-summary-anthropic-surgical-regen-f3c8d2 path=.cursor/plans/exec-summary-anthropic-surgical-regen-f3c8d2.md status=Complete notion=36c27693-f55c-81bc-a4a3-de1022a6e532

---

## Context (SCQA)

- **Situation** — Executive-summary lane at **24k** context (`VLLM_MAX_MODEL_LEN=24576`). Judge regen uses frozen compile + `REGEN_DELTA` / prescriptive delta via `core.SameAuthorityRegenRunner` (ADR-085). Brown SVP run [`exec_summary_20260526_193949`](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_193949): scratch **DRAFT_READY**, X2 PASS, 3 regen cycles, all **G5** `delta_scope_violation`, published scratch (`regen_outcome: no_acceptable_candidate`).
- **Complication** — Legacy **delta token cap** dropped judge lines (e.g. 7/19). **G5** counts global sentence edits vs a class budget, not “only touch judge-cited sentences.” **`delta_class`** routing can mis-target repair (e.g. `executive_signal` when Gemini’s primary complaint is `resume_voice`). Regen must not become a disguised full rewrite.
- **Question** — How do we match Anthropic surgical-regen guidance while keeping spine law (frozen compile, same authority, X2/X3 gates, no mock PASS)?
- **Answer** — **Three explicit stages** (draft → evaluate → minimal refine), **full verbatim judge feedback** in delta, **allowlist-based G5**, and **cycle-bounded** retries — not env truncation or global sentence-count caps as the primary scope lever.

---

## Anthropic guidance → harness mapping

| Anthropic principle | Source | Current harness | Target |
|---------------------|--------|-----------------|--------|
| **Prompt chaining** — separate calls per stage; each step has one job | [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) | Scratch + judges + regen in one lane; regen appends user turn | **Freeze** stage-1 compile; stage-2 = X1D only; stage-3 = `REGEN_DELTA` only |
| **Evaluator–optimizer** — generate → score vs rubric → minimal fix | Same + [Claude prompting](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-prompting-best-practices) | X1D soft-fail triggers regen; G5 post-hoc | Evaluator output = **structured** findings + **cited sentence indexes**; optimizer = delta allowlist + prescriptive lines |
| **Smallest high-signal context** — don’t flood refine turn | [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Was truncating delta via env caps | **Removed** `APPS_RG_EXEC_SUMMARY_REGEN_DELTA_TOKEN_CAP` / `REGEN_MAX_DELTA_TOKENS`; scope via allowlist + class instruction |
| **Positive, motivated instructions** | [anthropic_best_practices_2026.md](../../docs/reference/_primers/prompting/anthropic_best_practices_2026.md) | `EDIT_BUDGET`, `REGEN_DELTA_v1` | Keep “revise ONLY cited sentences + ledger” as **do** instructions |
| **Regression harness** — verify fix didn’t break pass | Evaluator–optimizer loop | X2 + soft-failed judge rescore | Per-cycle: X2 snapshot, G5 allowlist, rescore **soft_failed_only** (default) |

### Non-goals (Anthropic anti-patterns we reject)

- Re-running full scratch / re-compiling on judge fail (breaks frozen compile).
- Truncating judge remediation text to fit a token budget (drops signal).
- Using global sentence-edit count as the **only** scope guard (blocks legitimate multi-sentence voice fixes).
- Shipping regen candidate when X2 regresses (Brown lesson — keep scratch).

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1 | Plan + Notion registration | ~8K | NOTION_TOKEN set | ✅ DONE | Plan on disk + Plans DB row |
| W1 | W1.1 | Remove delta token env truncation | ~12K | 24k headroom | ✅ DONE | Full judge feedback in delta; 12 unit tests pass |
| W2 | W2.1–W2.2 | Document 3-stage contract in operator guide + delta pack order | ~15K | W1 merged | ✅ DONE | Operator guide + 7 pack-order unit tests pass |
| W3 | W3.1–W3.3 | G5v2: judge `cited_sentence_indexes` + allowlist gate | ~35K | Judge schema extension | ✅ DONE | `evaluate_g5_delta_scope_v2`; 19 policy tests pass |
| W4 | W4.1–W4.2 | `delta_class` routing + prescriptive delta quality | ~25K | W3 or parallel | ✅ DONE | Voice prose routes over exec-signal; allowlist EDIT_BUDGET |
| W5 | W5.1 | Brown REAL_LLM proof + receipt | ~20K | Qwen + judges up | ✅ DONE (PARTIAL) | Infra PASS; cycle1 G5v2 pass; scratch published |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W0.1 | Register plan (Notion + `PLAN_CREATED`) | ✅ DONE |
| W1.1 | Delete regen delta token env knobs | ✅ DONE |
| W2.1 | Operator guide “3-stage regen” section | ✅ DONE |
| W2.2 | `REGEN_DELTA` pack order: dimension → verbatim feedback → floors → guards | ✅ DONE |
| W3.1 | X1D judges emit `cited_sentence_indexes` per finding (0-based, 6-sentence model) | ✅ DONE |
| W3.2 | `evaluate_g5_delta_scope_v2` allowlist + freeze non-cited sentences | ✅ DONE |
| W3.3 | Receipt: `g5_delta_scope_cycle_*.json` records allowlist + violations | ✅ DONE |
| W4.1 | `resolve_delta_class`: voice before executive_signal when both fail | ✅ DONE |
| W4.2 | Prescriptive delta: tie each instruction to cited indexes | ✅ DONE |
| W5.1 | Brown SVP re-run + verifier script | ✅ DONE |

---

## Out Of Scope

- Changing `VLLM_MAX_MODEL_LEN` or first-pass 92% gate (see [executive_summary_24k_context_budget_rationalization_20260526.md](../../docs/reports/apps_rg/executive_summary_24k_context_budget_rationalization_20260526.md)).
- `agentic_core` contract schema changes (apps bridge only unless Author-Gate core migration).
- Full-panel judge rescore every cycle (keep `soft_failed_only` default).
- Exploratory full-paragraph regen (`APPS_RG_EXEC_SUMMARY_EXPLORATORY_REGEN`) unless explicit operator opt-in.

---

## Wave 0 — Plan registration

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Acceptance**

- [`.cursor/plans/exec-summary-anthropic-surgical-regen-f3c8d2.md`](exec-summary-anthropic-surgical-regen-f3c8d2.md) exists with wave table at top.
- Notion Plans row: `Status=Not Started`, `Exists On Disk=true`, `Plan File Path` set.

---

## Wave 1 — Delta feedback never truncated (complete)

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Delivered (2026-05-26)**

| Change | File(s) |
|--------|---------|
| Removed `APPS_RG_EXEC_SUMMARY_REGEN_DELTA_TOKEN_CAP` / `REGEN_MAX_DELTA_TOKENS` | [`executive_summary_repair_policy.py`](../../apps_rg/runtime/sections/executive_summary_repair_policy.py) |
| Always `_flatten_delta_sections` (no `_pack_delta_lines_to_token_budget`) | [`executive_summary_judge_remediation.py`](../../apps_rg/runtime/sections/executive_summary_judge_remediation.py) |
| Observability: `judge_feedback_lines_dropped: 0` | [`executive_summary_regen_observability.py`](../../apps_rg/runtime/sections/executive_summary_regen_observability.py) |
| Operator guide env rows removed | [`executive_summary_operator_guide.md`](../../docs/apps_rg/executive_summary_operator_guide.md) |

**Proof**

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/test_executive_summary_regen_max_delta_tokens.py \
  tests/unit/apps_rg/test_executive_summary_judge_delta_token_pack.py \
  tests/unit/apps_rg/test_prompt_judge_x2_alignment_w4.py \
  -q -p pytest_timeout
```

---

## Wave 2 — Three-stage regen contract (documentation + pack discipline)

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Delivered (2026-05-26)**

| ID | Change | File(s) |
|----|--------|---------|
| W2.1 | “Three-stage judge regen” section (mermaid, stages table, must-not-do, artifacts) | [`executive_summary_operator_guide.md`](../../docs/apps_rg/executive_summary_operator_guide.md) |
| W2.2 | `REGEN_DELTA_SECTION_ORDER` constant + docstring on `format_regen_delta_user_turn` | [`executive_summary_judge_remediation.py`](../../apps_rg/runtime/sections/executive_summary_judge_remediation.py), [`prompt_lock.py`](../../agentic_core/L2_execution/regen/prompt_lock.py) |
| W2.2 | Pack order + zero-drop + no-anchor-in-delta tests | [`test_executive_summary_judge_delta_token_pack.py`](../../tests/unit/apps_rg/test_executive_summary_judge_delta_token_pack.py) |

**Proof**

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/test_executive_summary_judge_delta_token_pack.py \
  -q -p pytest_timeout
```

WAVE_COMPLETE: plan=exec-summary-anthropic-surgical-regen-f3c8d2 wave=2 note="operator guide 3-stage section, REGEN_DELTA_SECTION_ORDER, 7 tests pass"

---

## Wave 3 — G5v2 allowlist (evaluator output → optimizer bounds)

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Delivered (2026-05-26)**

| ID | Change | File(s) |
|----|--------|---------|
| W3.1 | Judge rubric: require 1-based `cited_sentence_indexes` (S1=1 … S6=6) | [`executive_summary_x1d_dimension_verdicts.py`](../../apps_rg/runtime/judges/executive_summary_x1d_dimension_verdicts.py), [`executive_summary_x1d.py`](../../apps_rg/runtime/judges/executive_summary_x1d.py) |
| W3.2 | `build_regen_sentence_allowlist`, `evaluate_g5_delta_scope_v2`; lane wired | [`executive_summary_regen_delta_policy.py`](../../apps_rg/runtime/sections/executive_summary_regen_delta_policy.py), [`executive_summary_lane.py`](../../apps_rg/runtime/sections/executive_summary_lane.py) |
| W3.3 | Receipt schema v2: `allowlist`, `out_of_allowlist_indices`, `g5_legacy_budget_advisory` | same + operator guide |

**Proof**

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/test_executive_summary_regen_delta_policy.py \
  -q -p pytest_timeout
```

WAVE_COMPLETE: plan=exec-summary-anthropic-surgical-regen-f3c8d2 wave=3 note="G5v2 allowlist primary gate, legacy budget advisory, 19 tests"

---

## Wave 4 — Delta class routing + prescriptive delta

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Delivered (2026-05-26)**

| ID | Change | File(s) |
|----|--------|---------|
| W4.1 | `_resume_voice_prose_signal` routes `resume_voice_humanize` when exec-signal fails but prose cites mechanical/repetition | [`executive_summary_regen_delta_policy.py`](../../apps_rg/runtime/sections/executive_summary_regen_delta_policy.py) |
| W4.2 | `format_edit_budget_line` + allowlist-scoped `format_delta_class_regen_instruction`; wired in delta collector | [`executive_summary_judge_remediation.py`](../../apps_rg/runtime/sections/executive_summary_judge_remediation.py) |

**Proof**

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/unit/apps_rg/test_executive_summary_regen_delta_policy.py \
  tests/unit/apps_rg/test_executive_summary_judge_delta_token_pack.py \
  -q -p pytest_timeout
```

WAVE_COMPLETE: plan=exec-summary-anthropic-surgical-regen-f3c8d2 wave=4 note="voice prose routing, allowlist EDIT_BUDGET, Brown fixture delta test, 30 tests"

---

## Wave 5 — Brown REAL_LLM proof

WAVE_ID: W5
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Run:** [exec_summary_20260526_202438](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_202438) · receipt: [executive_summary_anthropic_surgical_regen_w5_brown_20260526.md](../../docs/reports/apps_rg/executive_summary_anthropic_surgical_regen_w5_brown_20260526.md)

**Proof**

```bash
python tools/cursor/verify_exec_summary_anthropic_surgical_regen.py \
  artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_202438
```

WAVE_COMPLETE: plan=exec-summary-anthropic-surgical-regen-f3c8d2 wave=5 note="Brown REAL_LLM ~313s DRAFT_READY; G5v2 cycle1 pass; verifier w5_infrastructure_ok PASS"

---

## Gap Register

**GAP-1: G5 global sentence budget vs surgical allowlist**

- G5 blocks multi-sentence voice fixes that judges explicitly request.
- W3 closes with allowlist-primary gate.

**GAP-2: Judge schema lacks cited indexes today**

- Findings are prose-only; model must be prompted + schema-validated.
- W3.1 adds fields; fallback = infer indexes from regex on “S2–S5” only when indexes absent (degraded mode, logged).

**GAP-3: Core runner `delta_token_budget_exceeded` with huge sentinel**

- `JUDGE_REGEN_CORE_DELTA_TOKEN_CEILING` prevents spurious core refusal; monitor regen dispatch size in W5.

---

## Definition of Done

DoD-1: W1 merged — no env-based truncation of judge feedback

- Evidence: grep shows no `REGEN_DELTA_TOKEN_CAP`; `collect_judge_remediation_delta_lines` uses `_flatten_delta_sections` only.
- Status: ✅ DONE

DoD-2: G5v2 allowlist enforced on regen publish path

- Evidence: `pytest tests/unit/apps_rg/test_executive_summary_regen_delta_policy.py -q` includes allowlist cases; `g5_delta_scope_cycle_1.json` shows `allowlist` key.
- Status: DONE (19+ policy tests; G5v2 on live path)

DoD-3: Brown REAL_LLM regen smoke

- Evidence: [executive_summary_anthropic_surgical_regen_w5_brown_20260526.md](../../docs/reports/apps_rg/executive_summary_anthropic_surgical_regen_w5_brown_20260526.md); run [exec_summary_20260526_202438](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_202438); verifier `tools/cursor/verify_exec_summary_anthropic_surgical_regen.py` PASS.
- Status: PARTIAL (exit 0 DRAFT_READY; infra proven; no accepted regen cycle)

DoD-4: Zero regressions on regen unit suite

- Evidence: 123 pytest (contract + regen modules); 30 regen-focused unit tests PASS (2026-05-26).
- Status: DONE

DoD-5: Operator guide + Notion plan row current

- Evidence: [executive_summary_operator_guide.md](../../docs/apps_rg/executive_summary_operator_guide.md); Notion Plans `exec-summary-anthropic-surgical-regen-f3c8d2` Completed.
- Status: DONE

---

## Verification vs deferral

| Item | Verify in-plan | Defer |
|------|----------------|-------|
| Delta token env removal | W1 ✅ | — |
| G5 allowlist | W3 | — |
| Core schema migration | — | Separate core plan if `IncrementalRepairContract` needs `allowlist` field |
| Multi-lane (headline/competencies) regen | — | apps_rg exec summary only |

---

## Related work

- Parent: [exec-summary-judge-regen-prompt-loop-b9e4c3](exec-summary-judge-regen-prompt-loop-b9e4c3.md)
- Brown debug run: [exec_summary_20260526_193949](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_193949)
- 24k budget: [executive_summary_24k_context_budget_rationalization_20260526.md](../../docs/reports/apps_rg/executive_summary_24k_context_budget_rationalization_20260526.md)
- Core spec: [same_authority_regen_envelope_spec_v1.md](../../docs/reference/L2_execution/same_authority_regen_envelope_spec_v1.md)

---

PLAN_COMPLETE: plan=exec-summary-anthropic-surgical-regen-f3c8d2 note="W0-W5 done; G5v2 allowlist + full judge delta; Brown W5 exec_summary_20260526_202438 infra PASS; 123 pytest; receipt executive_summary_anthropic_surgical_regen_w5_brown_20260526.md; product regen acceptance PARTIAL (no_acceptable_candidate)"
