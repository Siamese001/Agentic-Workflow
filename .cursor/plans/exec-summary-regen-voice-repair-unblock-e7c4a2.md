---
plan_id: exec-summary-regen-voice-repair-unblock-e7c4a2
plan_type: enhancement
touches_agentic_core: false
touches_governance_ci: false
parent_plan: exec-summary-anthropic-surgical-regen-f3c8d2
---

# Executive Summary — Regen Loop Unblock (Voice Repair + Delta Routing)

Unblock judge regen for Brown SVP executive summary: stop deterministic post-processors from injecting the exact sentences judges fail, route `delta_class` to substantive dimensions, and give Qwen incremental per-cycle signal so regen can pass X2 and rescore.

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: In Progress
CURRENT_WAVE: W2
LAST_COMPLETED_WAVE: W1
LAST_UPDATED: 2026-05-26
NOTION_PAGE_ID: 36c27693-f55c-8192-b780-c470af1130c1

PLAN_CREATED: slug=exec-summary-regen-voice-repair-unblock-e7c4a2 path=.cursor/plans/exec-summary-regen-voice-repair-unblock-e7c4a2.md status=Not Started notion=36c27693-f55c-8192-b780-c470af1130c1

---

## Context (SCQA)

- **Situation** — V10 initial prompt now weaves `$22M` / `20%` / `40%` into scratch display ([`exec_summary_20260526_213359`](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_213359)). OpenAI passes (4.3). Surgical regen infra is live ([`exec-summary-anthropic-surgical-regen-f3c8d2.md`](exec-summary-anthropic-surgical-regen-f3c8d2.md): full judge feedback, G5v2 allowlist, `SameAuthorityRegenRunner`).
- **Complication** — Ten judge regen cycles all fail: **7× `post_regen_x2_failed`**, **2× `regen_not_accepted`** (hash-identical to anchor after voice repair), **0 accepted**. `scores_before` frozen at Gemini 3.0 / Anthropic 3.5 for every cycle. Root cause is **not** “Qwen ignores regen delta” alone — deterministic `voice_repair` replaces Qwen’s metric-bearing S5 with hardcoded abstract prose (`_S5_CREDENTIAL_REPLACEMENT` / `_S6_FORWARD_REPLACEMENT` in [`executive_summary_voice_repair.py`](../../apps_rg/runtime/sections/executive_summary_voice_repair.py)) that judges quote verbatim as failures. Regen delta asks Qwen to fix sentences that were never Qwen’s. `delta_class` locks to `resume_voice_humanize` while Anthropic majors are `executive_signal` + `synthesis_quality`. Anchor stays `LAST_APPROVED` (= scratch) every cycle — no incremental learning.
- **Question** — How do we make regen prompts sufficient for Qwen to produce a publish-eligible candidate that passes all model-backed judges without weakening X2?
- **Answer** — **Stop sabotaging scratch before judges see it** (voice repair), **route regen to the right repair class**, **anchor each cycle to prior attempt + narrowed delta**, **pin facts so S5/S6 can satisfy judge asks within X2**, and **persist per-cycle X2/judge receipts** for proof.

### Evidence anchor (run `exec_summary_20260526_213359`)

| Artifact | Finding |
|----------|---------|
| [`judge_remediation_cycles.json`](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_213359/judge_remediation_cycles.json) | `stopped_reason: regen_not_accepted`, `regen_outcome: no_acceptable_candidate`, 10 cycles, all `delta_class: resume_voice_humanize` |
| [`provider_response.json`](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_213359/provider_response.json) | Qwen raw S5: *"Quantitative rigor … stress-testing cycles by 40%"* |
| [`l2_output.json`](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_213359/l2_output.json) | Published S5: *"capital-markets rigor informs which platform investments clear governance gates fastest"* (= `_S5_CREDENTIAL_REPLACEMENT`) |
| [`provider_request_judge_regen_cycle01_...json`](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_213359/provider_request_judge_regen_cycle01_attempt00_judge_regen-01-00-05486d0d.json) | 17-line `REGEN_DELTA_v1`; judges ask to fix S5/S6/connectives — same pack all cycles |
| [`claim_ledger`](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_213359/l2_output.json) | Row [4] triggers `_S5_CREDENTIAL_DUMP_RE`; row [5] triggers `_S6_THIN_RECAP_RE` |

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W0 | W0.1 | Plan + Notion registration | ~8K | NOTION_TOKEN | ✅ DONE | Plan on disk + Plans DB row |
| W1 | W1.1–W1.3 | Voice repair: remove judge-failing hardcoded S5/S6 | ~25K | apps_rg only | ✅ DONE | 13 pytest; metric S5 preserved; no judge-fail substring |
| W2 | W2.1–W2.2 | `delta_class` composite routing | ~18K | judge schema stable | 🔲 TODO | Anthropic `executive_signal` routes when present; tests |
| W3 | W3.1–W3.3 | Per-cycle anchor + incremental delta | ~30K | no core schema change | 🔲 TODO | Cycle N+1 sees cycle N output; delta narrows |
| W4 | W4.1–W4.2 | Composition plan S5/S6 fact pinning | ~22K | C0 pool unchanged | 🔲 TODO | S5 can cite metric fact; S6 has forward anchor |
| W5 | W5.1–W5.2 | Per-cycle receipts + convergence exit | ~15K | artifact_dir writable | 🔲 TODO | `*_cycle_N.json` persisted; early exit on hash repeat |
| W6 | W6.1 | Brown REAL_LLM E2E proof | ~25K | Qwen + judges up | 🔲 TODO | ≥1 regen cycle X2-pass + judge rescore improves OR all-judges-pass |

### Phase Progress

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|-----------------|-------------|-------------|--------|
| W0.1 | Register plan (Notion + `PLAN_CREATED`) | `.cursor/plans/`, Notion | — | ~8K | ✅ DONE |
| W1.1 | Audit + document voice_repair trigger graph | `executive_summary_voice_repair.py` | Hardcoded fallbacks = judge quotes | ~8K | ✅ DONE |
| W1.2 | Replace `_S5_CREDENTIAL_REPLACEMENT` / `_S6_FORWARD_REPLACEMENT` with metric-grounded templates | `executive_summary_voice_repair.py`, tests | S5 loses 40% when repaired | ~12K | ✅ DONE |
| W1.3 | Gate synthesis_regen materialization vs voice_repair order | `executive_summary_voice_repair.py` (post-order safe) | Double-rewrite S5 | ~8K | ✅ DONE |
| W2.1 | `resolve_delta_class`: composite when multi-judge multi-dimension | `executive_summary_judge_remediation.py` (or resolver module) | Wrong class 10 cycles | ~10K | 🔲 TODO |
| W2.2 | Map composite class → regen delta sections + EDIT_BUDGET | `executive_summary_judge_remediation.py` | Voice-only instructions | ~8K | 🔲 TODO |
| W3.1 | Regen anchor = prior cycle output (not scratch) after cycle 1 | `executive_summary_judge_remediation.py`, bridge | No learning curve | ~12K | 🔲 TODO |
| W3.2 | Append `PRIOR_ATTEMPT` + `STILL_FAILING` lines to delta | `collect_judge_remediation_delta_lines` | Identical 17 lines | ~10K | 🔲 TODO |
| W3.3 | Unit tests: anchor hash advances per cycle | `tests/unit/apps_rg/` | — | ~8K | 🔲 TODO |
| W4.1 | S5 composition: allow `fact_quant_hpc_001` outcome in display when FSA cited | `executive_summary_synthesis_contract.py`, composition | S5 has no numeric facts | ~12K | 🔲 TODO |
| W4.2 | S6 forward synthesis: briefing/JD grounding line in I0 + arc | prompt template + contract | Generic S6 | ~10K | 🔲 TODO |
| W5.1 | Persist `judge_remediation_receipt_cycle_N.json`, `x2_gate_outputs_post_regen_cycle_N.json` | `executive_summary_lane.py` | Only last receipt survives | ~8K | 🔲 TODO |
| W5.2 | Convergence early-exit when `regen_output_hash` repeats | `executive_summary_lane.py` | 8 wasted cycles | ~7K | 🔲 TODO |
| W6.1 | Brown SVP re-run + closeout report | CLI, `docs/reports/apps_rg/` | — | ~25K | 🔲 TODO |

---

## Out Of Scope

- Changing `VLLM_MAX_MODEL_LEN` or first-pass token budget (see [executive_summary_24k_context_budget_rationalization_20260526.md](../../docs/reports/apps_rg/executive_summary_24k_context_budget_rationalization_20260526.md)).
- `agentic_core` `IncrementalRepairContract` schema changes (apps bridge only unless Author-Gate).
- Weakening X2 gates, judge rubrics, or fixtures to force PASS.
- Full-panel judge rescore every cycle (keep `soft_failed_only` default).
- Re-opening V10 metric-weave prompt work except S6 forward-grounding lines in W4.2.

---

## Architectural defects → wave mapping

| # | Defect | Wave |
|---|--------|------|
| 1 | `voice_repair` injects judge-failing S5/S6 | W1 |
| 2 | `delta_class` → `resume_voice_humanize` only | W2 |
| 3 | Anchor = scratch every cycle | W3 |
| 4 | S5 facts lack numeric outcomes | W4 |
| 5 | S6 forward synthesis ungrounded | W4 |
| 6 | Identical 17-line delta all cycles | W3 |
| 7 | Per-cycle X2 receipt overwritten | W5 |
| 8 | No convergence early-exit | W5 |

---

## Wave 0 — Plan registration

WAVE_ID: W0
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Delivered (2026-05-26)**

| Item | Value |
|------|-------|
| Notion page | `36c27693-f55c-8192-b780-c470af1130c1` |
| Status | Not Started |
| Sync script | [`tools/notion/plan_notion_sync_exec_summary_regen_voice_repair_unblock.py`](../../tools/notion/plan_notion_sync_exec_summary_regen_voice_repair_unblock.py) |

**Acceptance**

- [x] [`.cursor/plans/exec-summary-regen-voice-repair-unblock-e7c4a2.md`](exec-summary-regen-voice-repair-unblock-e7c4a2.md) exists with wave table at top.
- [x] Notion Plans row: `Status=Not Started`, `Exists On Disk=true`, `Plan File Path=.cursor/plans/exec-summary-regen-voice-repair-unblock-e7c4a2.md`.
- [x] `PLAN_CREATED` marker updated with `NOTION_PAGE_ID`.

---

## Wave 1 — Voice repair must not inject judge failures

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES

**Delivered (2026-05-26)**

| Item | Path |
|------|------|
| Voice repair implementation | [`executive_summary_voice_repair.py`](../../apps_rg/runtime/sections/executive_summary_voice_repair.py) |
| Regen-unblock tests | [`test_executive_summary_voice_repair_regen_unblock.py`](../../tests/unit/apps_rg/test_executive_summary_voice_repair_regen_unblock.py) |
| W1 receipt | [`exec_summary_regen_voice_repair_w1_receipt.md`](../../docs/reports/apps_rg/exec_summary_regen_voice_repair_w1_receipt.md) |

**Problem (proven)**

Qwen raw S5 contains `40%` stress-testing outcome. After `finalize_executive_summary_coherence` / `_repair_synthesis_quality_sentences`, published S5 matches:

```text
On that commercial base, capital-markets rigor informs which platform investments clear
governance gates fastest in regulated programs.
```

Anthropic and Gemini regen deltas quote this exact string as the failure.

**Phases**

- **W1.1** — Trace trigger chain: `claim_ledger` row [4] → materialization → `_S5_CREDENTIAL_DUMP_RE` → `_S5_CREDENTIAL_REPLACEMENT`. Document in wave receipt.
- **W1.2** — Replace hardcoded replacements with **fact-grounded** rewrites:
  - Prefer keeping Qwen display when it already has allowed metrics and passes `x2_exec_summary_no_credential_dump`.
  - If rewrite required: surface `FSA` + one allowed outcome from `fact_quant_hpc_001` or `fact_governance_003` (no derivatives inventory list).
  - Remove or narrow `_S5_CREDENTIAL_DUMP_RE` so metric-bearing S5 is not classified as dump.
- **W1.3** — Order: run voice repair **before** synthesis materialization forces claim_text into display, OR skip voice_repair when display already passes relevant X2 gates.

**Files**

| File | Change |
|------|--------|
| [`apps_rg/runtime/sections/executive_summary_voice_repair.py`](../../apps_rg/runtime/sections/executive_summary_voice_repair.py) | Remove/replace `_S5_CREDENTIAL_REPLACEMENT`, `_S6_FORWARD_REPLACEMENT`; tighten patterns |
| [`apps_rg/runtime/sections/executive_summary_lane.py`](../../apps_rg/runtime/sections/executive_summary_lane.py) | Call order / skip guard |
| `tests/unit/apps_rg/test_executive_summary_voice_repair_regen_unblock.py` | New: scratch path preserves metric S5; no hardcoded judge-fail string |

**Acceptance**

- Unit: given Qwen-like parsed output with S5 `40%`, `apply_voice_repair_to_parsed` does **not** emit `capital-markets rigor informs which platform investments`.
- Unit: `_S5_CREDENTIAL_DUMP_RE` does not fire on single-FSA + one-metric sentences.
- No edits to `agentic_core`.

---

## Wave 2 — Delta class routing

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

**Problem**

All 10 cycles used `delta_class=resume_voice_humanize` while Anthropic `major_failed_dimensions` were `executive_signal`, `synthesis_quality`.

**Phases**

- **W2.1** — Extend `resolve_delta_class` (or equivalent) to emit composite when:
  - ≥2 providers fail, and
  - failed dimensions include both `resume_voice` and (`executive_signal` | `synthesis_quality`).
  - Example: `executive_signal_and_voice_v1`.
- **W2.2** — Map composite class to `REGEN_DELTA` sections: metric weave for S3–S5, connective variety, S6 forward grounding — not voice-only humanize bullets.

**Files**

| File | Change |
|------|--------|
| [`apps_rg/runtime/sections/executive_summary_judge_remediation.py`](../../apps_rg/runtime/sections/executive_summary_judge_remediation.py) | `resolve_delta_class`, `collect_judge_remediation_delta_lines` |
| `tests/unit/apps_rg/test_executive_summary_delta_class_routing.py` | New routing matrix tests |

**Acceptance**

- Fixture: Gemini `resume_voice` + Anthropic `executive_signal` → composite class, delta contains metric/S5/S6 lines.
- Fixture: voice-only failure → `resume_voice_humanize` unchanged.

---

## Wave 3 — Incremental regen anchor and delta

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

**Problem**

`anchor_classification=LAST_APPROVED` always points at scratch. Cycles 3–9 produced hash-stable Qwen text but lane reverted to scratch on X2, so Qwen never refined from its own attempt.

**Phases**

- **W3.1** — After cycle 1, set `anchor_output_text` to **last regen candidate display** (post-parse, pre-revert snapshot) when `draft_parse_ok` and `output_changed`, even if X2 failed — for next cycle's assistant turn only; publish baseline still scratch until accepted.
- **W3.2** — Add delta lines:
  - `PRIOR_ATTEMPT_SUMMARY: <one line per changed sentence>`
  - `STILL_FAILING_AFTER_PRIOR_ATTEMPT: <judge lines that persisted>`
  - Drop remediations already satisfied (e.g. connective fixed → remove that bullet).
- **W3.3** — Tests: mock two-cycle loop; cycle 2 request includes cycle 1 assistant content.

**Files**

| File | Change |
|------|--------|
| [`apps_rg/runtime/sections/executive_summary_judge_remediation.py`](../../apps_rg/runtime/sections/executive_summary_judge_remediation.py) | Anchor selection, delta packing |
| [`apps_rg/runtime/sections/executive_summary_same_authority_regen_bridge.py`](../../apps_rg/runtime/sections/executive_summary_same_authority_regen_bridge.py) | Pass dynamic anchor |
| [`apps_rg/runtime/sections/executive_summary_judge_regen_loop.py`](../../apps_rg/runtime/sections/executive_summary_judge_regen_loop.py) | Thread extension |

**Acceptance**

- Cycle 2 `provider_request` assistant message contains cycle 1 `resume_display_text` (not scratch formulaic S2–S5).
- Delta line count decreases or changes when prior attempt fixed a cited issue.

---

## Wave 4 — Composition plan: ground S5/S6 for judges

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

**Problem**

Judges ask for S5 metric/outcome and S6 grounded forward synthesis, but composition plan binds S5 to credential facts without numerics; S6 only has retrospective facts.

**Phases**

- **W4.1** — `SENTENCE_ARC_SVP_STRATEGY` S5: allow citing `fact_quant_hpc_001` **display metric** when row also references FSA credential fact; forbid derivatives employer inventory.
- **W4.2** — S6: add briefing-derived forward anchor (Brown decentralized units / innovation mandate) as **targeting-only** prose allowed in display per existing `jd_alignment.targeting_only` pattern.

**Files**

| File | Change |
|------|--------|
| [`apps_rg/runtime/sections/executive_summary_synthesis_contract.py`](../../apps_rg/runtime/sections/executive_summary_synthesis_contract.py) | Arc guidance |
| [`apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml`](../../apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml) | I0 S6 forward line (minor) |
| `tests/unit/apps_rg/test_executive_summary_initial_generation_metric_weave_v10.py` | Extend S5/S6 assertions |

**Acceptance**

- Composition plan output for Brown JD includes explicit S5 metric source_fact_id.
- X2 still PASS on unsupported-claims (no invented metrics).

---

## Wave 5 — Observability and convergence guard

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

**Phases**

- **W5.1** — Write per-cycle artifacts (do not overwrite singleton):
  - `judge_remediation_receipt_cycle_{n}.json`
  - `x2_gate_outputs_post_regen_cycle_{n}.json`
  - Include `post_regen_x2_failed_gate_ids` in cycles receipt.
- **W5.2** — If `regen_output_hash == prior_cycle_regen_output_hash`, set `stopped_reason: regen_converged` and break before `max_cycles`.

**Acceptance**

- Re-run one cycle in test harness → artifacts for cycle 1 and 2 both exist.
- Simulated identical hash → loop stops at cycle 2.

---

## Wave 6 — Brown E2E proof

WAVE_ID: W6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO

**Command**

```bash
python -m apps_rg --section executive_summary \
  --target-company "Brown & Brown" \
  --target-role "SVP IT Strategy & Innovation" \
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt \
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md \
  --provider qwen_vllm \
  --allow-non-allow-exit-zero
```

**PASS criteria (any one)**

1. `regen_outcome: accepted` and `all_model_backed_judges_pass` in [`judge_remediation_cycles.json`](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/<run_id>/judge_remediation_cycles.json), **or**
2. Published candidate is regen (not scratch) with X2 PASS and min model-backed score ≥ operator floor, **or**
3. **PARTIAL** documented: scratch passes X2 + OpenAI; regen improves Anthropic/Gemini scores vs `exec_summary_20260526_213359` baseline with receipt.

**Deliverable**

- [`docs/reports/apps_rg/exec_summary_regen_voice_repair_unblock_e2e_20260526.md`](../../docs/reports/apps_rg/exec_summary_regen_voice_repair_unblock_e2e_20260526.md) with linked artifacts.

---

## Definition of Done

| ID | Criterion | Verification |
|----|-----------|--------------|
| D1 | Voice repair no longer emits judge-failing S5/S6 strings on metric-bearing Qwen output | `pytest tests/unit/apps_rg/test_executive_summary_voice_repair_regen_unblock.py -o addopts=` |
| D2 | Composite `delta_class` when Anthropic exec_signal + Gemini voice fail | `pytest tests/unit/apps_rg/test_executive_summary_delta_class_routing.py -o addopts=` |
| D3 | Per-cycle regen receipts persisted | Inspect artifact dir after unit/integration test |
| D4 | Brown REAL_LLM run completes (exit 0) | CLI command in W6 |
| D5 | Closeout report with PASS/PARTIAL/FAIL and artifact links | `docs/reports/apps_rg/exec_summary_regen_voice_repair_unblock_e2e_20260526.md` |

### Verification vs deferral

| Item | In plan | Deferred |
|------|---------|----------|
| W1 voice repair | W1 | — |
| W2 delta class | W2 | — |
| W3 incremental anchor | W3 | — |
| W4 composition S5/S6 | W4 | — |
| W5 observability | W5 | — |
| W6 E2E | W6 | — |
| Notion registration | W0 | Until NOTION_TOKEN / user requests sync |
| Core `AnchorClassification` enum extension | — | Only if W3 cannot be done in apps bridge |

---

## Risk register

| Risk | Mitigation |
|------|------------|
| Removing voice_repair regressions X2 credential-dump gate | Keep strip path for true 3+ marker dumps; add tests with fixtures |
| Incremental anchor publishes bad regen | Publish baseline remains scratch until `publish_eligible` + G3 + X2 pass |
| S5 metric duplicates S4 | Arc: S5 cites commercial/governance outcome, S4 HPC — composition plan enforces distinct facts |
| Qwen still converges on abstract S5 | W4 fact pinning + W1 remove fallback |

---

## Related plans and reports

- Parent: [`exec-summary-anthropic-surgical-regen-f3c8d2.md`](exec-summary-anthropic-surgical-regen-f3c8d2.md) (COMPLETE)
- Prompt V10 metric weave: prior session edits to [`executive_summary.generate_scratch_v1.yaml`](../../apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml)
- Debug transcript: agent chat `9c9db833-505c-4d6a-8b97-82a24ae5956e`
- Baseline failed run: [`exec_summary_20260526_213359`](../../artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260526_213359)
