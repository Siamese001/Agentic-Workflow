# Brown & Brown SVP — Full Resume Run RCA & Remediation Plan

**Generated:** 2026-05-27 (UTC)  
**Targeting:** Brown & Brown · SVP IT Strategy & Innovation  
**Related plan:** [skills-graph-hardening-gap-closure-53576c.md](../../.cursor/plans/skills-graph-hardening-gap-closure-53576c.md)

---

## Executive summary

Two live `python -m apps_rg` runs were executed after graph-skills hardening (18 Brown promotions + `skill_svp_it_strategy_innovation` mint). **Neither run produced an authorized full resume.**

| Run | Briefing | Artifact | Primary failure |
|-----|----------|----------|-----------------|
| A | Full (`brown_brown_svp_it_strategy_innovation_briefing.md`) | [full_resume_a7c31b6fe534](../../artifacts/apps_rg/runtime_proofs/full_resume_a7c31b6fe534) | **I1** Token budget pre-dispatch (96.17% > 95% cap) |
| B | Exec digest (`brown_brown_svp_it_strategy_innovation_briefing_exec.md`) | [full_resume_d8312b748dbe](../../artifacts/apps_rg/runtime_proofs/full_resume_d8312b748dbe) | **I2–I4** Exec summary REAL_LLM + X2 PASS, but X3 judge soft-fail → phase-1 abort → 6 lanes blocked |

Root causes are **independent but sequenced**: I1 blocks before generation; I2–I4 block after exec-summary generation when `product_fail_closed` treats judge soft-fail as lane hard-fail.

---

## Issue inventory

### I1 — First-pass token budget exceeded (full briefing)

| Field | Value |
|-------|--------|
| **Symptom** | `TOKEN BUDGET BLOCKED — shorten briefing and/or JD` |
| **Fail-closed** | `TOKEN_BUDGET_EXCEEDED_FIRST_PASS_95PCT` |
| **Receipt** | [token_budget_receipt.json](../../artifacts/apps_rg/runtime_proofs/full_resume_a7c31b6fe534/lanes/executive_summary/token_budget_receipt.json) |
| **Utilization** | 21,172 est. input tokens / 20,915 cap (**96.17%**) |
| **Overage** | ~257 est. tokens |

**Root cause (5 Whys)**

1. **Why blocked?** Compiled exec-summary prompt exceeds `first_pass_input_utilization_max` (0.95 × 22,016 available input tokens).
2. **Why so large?** Targeting + evidence capsule grew: full briefing ~15,210 chars (~5,678 est. targeting tokens after safety); graph/fact context larger post–skill promotions.
3. **Why did 0.95 not suffice?** Policy was raised from 0.92 → 0.95 to absorb prior marginal overages; this run still sits **1.17 pp above** the new cap.
4. **Why no auto-trim?** `targeting_context_frozen_author_judge_parity` — targeting prose is not auto-truncated; optional trim did not apply (`trim_applied: false`).
5. **Why operator used full briefing?** Full file is a **research dossier** (tables, ASCII diagrams, citations), not sized for 24k Qwen first-pass input.

**Contributing factors**

- `CHARS_PER_TOKEN_ESTIMATE=3` + `ESTIMATE_SAFETY_MULTIPLIER=1.12` is conservative (intentional fail-closed).
- JD alone ~4,335 chars (~1,618 est. tokens) — acceptable; **briefing dominates** delta vs exec variant.

**Evidence**

| Asset | Chars | Est. tokens (÷3 × 1.12) |
|-------|------:|------------------------:|
| Full briefing | 15,210 | ~5,678 |
| Exec briefing | 2,426 | ~905 |
| JD | 4,335 | ~1,618 |

Run B with exec briefing: utilization **79.14%** → dispatch allowed ([receipt](../../artifacts/apps_rg/runtime_proofs/full_resume_d8312b748dbe/lanes/executive_summary/token_budget_receipt.json)).

---

### I2 — X3 `REVIEW_JUDGE_SOFT_FAIL` (Anthropic below floor)

| Field | Value |
|-------|--------|
| **Symptom** | `X3_REVIEW_JUDGE_SOFT_FAIL`; `outcome_authorized=False` |
| **Blocking judge** | `anthropic_claude` (claude-opus-4-6) |
| **Score** | **3.4 / 5.0** (threshold **4.0**, normalized 0.68 < 0.80) |
| **Passing judges** | gemini_pro 5.0, openai_chatgpt 4.3 |
| **Receipt** | [x1d_llm_judge_outputs.json](../../artifacts/apps_rg/runtime_proofs/full_resume_d8312b748dbe/lanes/executive_summary/x1d_llm_judge_outputs.json) |
| **Code path** | [executive_summary_x3.py](../../apps_rg/runtime/exit/executive_summary_x3.py) — `judge_required_for_allow` + soft_fail → `allowed=False` |

**Root cause**

Scratch exec summary reads as **achievement inventory** vs **SVP IT strategy narrative** for brokerage context:

- S1 thesis generic (“decentralized regulated enterprises”) — weak Brown/insurance brokerage hook.
- S2 near-verbatim fact echo (Basel III/CCAR) vs synthesis.
- S5/S6 redundant legacy-modernization theme; S6 not forward-looking (judge: `synthesis_quality`, `executive_signal`).

This is a **content/rubric alignment** failure on one panel member, not X2 correctness (X2 **PASS** on published scratch).

**Product certification**

[product_certification_receipt.json](../../artifacts/apps_rg/runtime_proofs/full_resume_d8312b748dbe/lanes/executive_summary/product_certification_receipt.json): `NOT_CLAIMED`, `blocking_judges=anthropic_claude`.

---

### I3 — Judge regen stuck: post-regen X2 failures (sentence count / ledger)

| Field | Value |
|-------|--------|
| **Symptom** | Regen cycles 1–2 `accepted: false`, `reverted: post_regen_x2_failed` |
| **Stopped** | `x2_stuck_same_failure` after cycle 2 |
| **Receipt** | [judge_remediation_cycles.json](../../artifacts/apps_rg/runtime_proofs/full_resume_d8312b748dbe/lanes/executive_summary/judge_remediation_cycles.json) |

**Root cause**

Regen aimed at Anthropic narrative feedback but **broke deterministic X2 invariants**:

- Cycle 1: 6 → **5** sentences → fails `x2_exec_summary_sentence_count_6`.
- Repeated failures on claim-ledger consistency, sentence coverage, synthesis_quality gates (rows 1, 5, 6).
- **No post-regen judge refresh** on an X2-passing candidate; final publish baseline = **scratch** (`only_scratch_publish_eligible`), which still carries I2 soft-fail.

**Gap:** Remediation loop optimizes judge voice without a hard constraint that regen must preserve 6-sentence SRFS + ledger parity before acceptance.

---

### I4 — Phase-1 lane cascade (downstream sections never ran)

| Field | Value |
|-------|--------|
| **Symptom** | headline, competencies, ibm_*, unify_* → `UNKNOWN` / `dispatch_error:lane_exit_error` |
| **Receipt** | [phase1_lane_inventory.json](../../artifacts/apps_rg/runtime_proofs/full_resume_d8312b748dbe/modular_r4/phase1_lane_inventory.json) |

**Root cause (mechanism)**

1. `product_fail_closed_runtime()` is **true** for full resume product path.
2. Executive-summary lane returns `exit_status=error` when X3 is not `X3_ALLOW` (soft-fail counts as hard fail for integrated dispatch).
3. [modular_resume_generation.py](../../apps_rg/l2_recipe/modular_resume_generation.py) sets `phase1_aborted` on exec-summary hard fail → subsequent lanes get `dispatch_error:lane_exit_error|missing_pointer`.

**By design** for fail-closed product runs; **operator impact** is conflated: token block (I1) and judge soft-fail (I2) both present as full-run `error` with no partial merge artifact.

---

## Out of scope for this RCA (separate verification)

| Topic | Status | Note |
|-------|--------|------|
| Graph skills in live selection | Not exercised in Run A; Run B stopped at exec summary | Re-run after I1–I4 cleared; gap detector post-promotion: `draft_overlap=37` |
| `jd_inferred_skill_svp_it_strategy` pseudo | Still rejected by design | Real skill: `skill_svp_it_strategy_innovation` (ACTIVE_CONFIRMED) |
| W4.2 utilization scorer gate | Plan-deferred | [skills-graph-hardening plan](../../.cursor/plans/skills-graph-hardening-gap-closure-53576c.md) |

---

## Remediation plan

### R0 — Operator unblock (no code, &lt;1 day)

| ID | Action | Owner | Proof |
|----|--------|-------|-------|
| R0.1 | Re-run with `--manual-brief ..._briefing_exec.md` (proven 79% utilization) | Operator | `token_budget_receipt.json` → `dispatch_allowed: true` |
| R0.2 | For full briefing runs, trim ≥300 chars targeting-only prose OR split: exec variant in CLI, full doc for human research only | Operator | Utilization ≤ 95% |
| R0.3 | Document in targeting README: **default CLI brief = `*_briefing_exec.md`**; full brief = research | Docs | File exists + linked from Brown config |

### R1 — Token budget policy (apps_rg, 1–2 days)

| ID | Action | Rationale |
|----|--------|-----------|
| R1.1 | Add `apps_rg` CLI hint when `TOKEN_BUDGET_EXCEEDED`: print sibling `*_briefing_exec.md` if present | Reduces repeat failures |
| R1.2 | Optional: auto-select exec brief when full brief exceeds cap (behind `APPS_RG_AUTO_EXEC_BRIEF=1`, default off) | Fail-closed default preserved |
| R1.3 | **Do not** raise 0.95 → 0.97 without Author-Gate — marginal 257-token overage is briefing bloat, not policy bug | Avoid masking dossier misuse |

### R2 — Exec summary narrative + judge loop (apps_rg, 3–5 days)

| ID | Action | Rationale |
|----|--------|-----------|
| R2.1 | Prompt/SRFS: require S1 Brown brokerage + IT strategy hook; S6 forward synthesis (mirror Anthropic findings) | Addresses I2 root content |
| R2.2 | Regen acceptance gate: **reject** regen candidate unless `x2_exec_summary_sentence_count_6` + claim_ledger gates pass **before** publish | Fixes I3 |
| R2.3 | After accepted regen, **re-run X1D panel** on published text; X3 from fresh scores | Closes judge/regen desync |
| R2.4 | Consider `executive_signal` weighting: 2/3 judges pass + no decisive fail → `X3_ALLOW` with `REVIEW_ONLY` flag (Author-Gate) | Product policy choice |

### R3 — Full-run orchestration UX (apps_rg, 2–3 days)

| ID | Action | Rationale |
|----|--------|-----------|
| R3.1 | When exec summary is `DRAFT_READY` but not `X3_ALLOW`, emit **partial resume bundle** (exec + deterministic sections) with explicit `outcome_authorized=False` | Operators get value during judge iteration |
| R3.2 | Separate exit codes: `token_budget_blocked` vs `judge_review_blocked` vs `lane_hard_fail` | Clearer RCA in CI/logs |
| R3.3 | `FULL_RUN_SECTION_STATUS.md` must show pre-run block reason per lane (not only UNKNOWN) | Already partially in `integrated_lane_pre_run_failure.json` — surface in summary |

### R4 — Graph skills verification run (after R0–R2)

| ID | Action | Proof |
|----|--------|-------|
| R4.1 | Full resume pass with exec brief + R2 prompt fixes | All lanes REAL_LLM; merge artifact |
| R4.2 | Run `detect_graph_skill_gaps.py` on artifact dir | `skill_svp_it_strategy_innovation` admitted; Brown partner/GTM skills in selection rationale |
| R4.3 | Update [skills-graph-hardening plan](../../.cursor/plans/skills-graph-hardening-gap-closure-53576c.md) wave table | W3/W4 closeout markers |

---

## Implementation status (2026-05-27)

| Wave | Status | Deliverable |
|------|--------|-------------|
| R0 | **Done** | [targeting/README.md](../../apps_rg/config/targeting/README.md) |
| R1 | **Done** | [briefing_exec_resolution.py](../../apps_rg/runtime/briefing_exec_resolution.py), token-budget sibling hint, `APPS_RG_AUTO_EXEC_BRIEF` in [__main__.py](../../apps_rg/__main__.py) |
| R2.2 | **Done** | G5v2 `sentence_count_invariant` when regen caps disabled |
| R2.1 / R2.3 / R2.4 | Open | Prompt/judge policy (E0 already has S1/S6 contract; post-regen panel refresh deferred) |
| R3.2 | **Done** | [cli_exit_codes.py](../../apps_rg/runtime/cli_exit_codes.py) — exit 3 token, 4 judge review |
| R3.3 | **Done** | [full_run_section_status.py](../../apps_rg/runtime/full_run_section_status.py) PRE_RUN rows |
| R4 | Open | Full resume proof run after operator unblock |

---

## Acceptance criteria (remediation complete)

- [ ] Full briefing run either passes token gate (trimmed dossier) or CLI defaults to exec brief with documented policy.
- [ ] Exec-summary run achieves `X3_ALLOW` or explicit operator-accepted `DRAFT_READY` with 2/3 judges pass documented.
- [ ] Regen cannot publish text failing `x2_exec_summary_sentence_count_6`.
- [ ] Full resume: ≥6 lanes with `REAL_LLM` + merged `review_bundle.zip` under `outcome_authorized=True` OR documented partial bundle path.
- [ ] RCA receipt + Notion Plans row linked; backlog item for R2.4 if policy change needed.

---

## Artifact index

| Run | Folder | Token receipt | Exec output |
|-----|--------|---------------|-------------|
| A (full brief) | [full_resume_a7c31b6fe534](../../artifacts/apps_rg/runtime_proofs/full_resume_a7c31b6fe534) | [blocked](../../artifacts/apps_rg/runtime_proofs/full_resume_a7c31b6fe534/lanes/executive_summary/token_budget_receipt.json) | — |
| B (exec brief) | [full_resume_d8312b748dbe](../../artifacts/apps_rg/runtime_proofs/full_resume_d8312b748dbe) | [pass](../../artifacts/apps_rg/runtime_proofs/full_resume_d8312b748dbe/lanes/executive_summary/token_budget_receipt.json) | [resume_display_text.txt](../../artifacts/apps_rg/runtime_proofs/full_resume_d8312b748dbe/lanes/executive_summary/resume_display_text.txt) |

---

## Markers

```
RCA_COMPLETE: brown_svp_full_resume path=docs/reports/apps_rg/brown_svp_full_resume_rca_remediation_20260527.md runs=a7c31b6fe534,d8312b748dbe issues=I1,I2,I3,I4
REMEDIATION_PLAN: waves=R0(operator),R1(token),R2(judge/regen),R3(orchestration),R4(graph_verify)
```
