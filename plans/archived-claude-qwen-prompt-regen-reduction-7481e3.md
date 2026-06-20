---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\qwen-prompt-regen-reduction-7481e3.md'
original_relative_path: 'qwen-prompt-regen-reduction-7481e3.md'
source_sha256: 00da3182325c8d5d9f6d673e6665e469f84e4e93f20e26e226b22f7aea3abbd3
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan: Qwen Prompt Regen Reduction — Executive Summary Section
<!-- slug: qwen-prompt-regen-reduction-7481e3 -->
<!-- last_updated: 2026-05-27 -->

## Context (SCQA)

**Situation:** The `apps_rg` executive summary section generates output exclusively via a local Qwen vLLM model. Post-X2 judge regen cycles default to up to 10 attempts per run (`JUDGE_REGEN_MAX_ATTEMPTS = 10`). After the W1–W6 fix session (plan `competencies-graph-proof-pool-p2-w1`), X2 gates are now clean, but the SVP-lane disposition remained `X3_REVIEW_JUDGE_SOFT_FAIL` — indicating Qwen produces structurally valid but synthesis-quality-weak output on first pass.

**Complication:** A full prompt audit identified eight root causes for excessive regen cycles, concentrated in four areas:
1. The single positive E0 example (`exec_summary_pos_svp_it_strategy_001`) uses the exact same metric values that appear in C0 facts → Qwen copies example structure rather than synthesising from facts → judges rate synthesis quality low → judge regen triggers.
2. "Max two stock bridges" constraint is stated three times across I0, creating an anxiety signal that causes over-correction and judge-graded prose degradation.
3. The S4 opener directive (non-stock opener on SVP ≥3 brushstrokes) lives in U0 (lowest authority slot) and is partially ignored on Qwen's first pass → synthesis regen.
4. `self_check` has 12 required fields, 7 of which are fully covered by X2 gates → wasted output tokens on every Qwen call.

**Question:** Can we restructure the prompt (E0 examples, I0 consolidation, authority slot placement, self_check, regen cap) to reduce average regen cycles from ~5–7 to ≤2 without weakening X2 gate coverage?

**Answer:** Yes — eight bounded changes across prompt template, E0 examples file, PA assembly, and repair policy cover all root causes with no gate weakening.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Files | Notes |
|------|-------|--------|-------|-------|
| W1 | Domain-transpose E0 positive + restore 2nd diverse positive | Not Started | `executive_summary_examples.yaml`, `e0_examples.py` | P0 — breaks template-following trap |
| W2 | Delete dead `SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR` + consolidate stock-bridge rule in I0 | Not Started | `executive_summary_pa.py`, `dispatch/executive_summary_pa.py`, `executive_summary.generate_scratch_v1.yaml` | P1 — removes maintenance hazard + deduplicates noise |
| W3 | Promote S4 opener directive from U0/composition to I0 | Not Started | `executive_summary.generate_scratch_v1.yaml`, `executive_summary_composition.py` | P1 — higher authority = first-pass compliance |
| W4 | Reduce self_check to 5 fields + set JUDGE_REGEN_MAX_ATTEMPTS=3 | Not Started | `executive_summary.generate_scratch_v1.yaml`, `executive_summary_pa.py`, `executive_summary_repair_policy.py` | P2 — token savings + caps runaway cost |
| W5 | Convert retired gold example to negative + proof re-run | Not Started | `executive_summary_examples.yaml` | P3 — regression guard + proof |

---

## Immutable Constraints

- No gate weakening: X2 gate set, rubric, and fixture files must not be softened.
- No non-Qwen generation path created — all changes target the shared compiled prompt that Qwen receives.
- `exec_summary_pos_svp_it_strategy_001` arc structure (6-sentence, S1 thesis / S2 platform / S3 commercial / S4 governance / S5 quant / S6 capstone) must be preserved — only metric values change.
- Proof law (`pa_proof_binding_v1`) and C0 fact reference contract remain unchanged.
- The S4 opener directive logic (introduced in `executive_summary_composition.py`) must stay as the runtime discriminant; W3 adds a static I0 advisory only — composition plan still drives per-run prescription.

---

## Wave 1 — Domain-Transpose E0 Positive + Restore 2nd Diverse Positive

**Problem:** `exec_summary_pos_svp_it_strategy_001` uses the exact dollar/percent metrics that appear in the real C0 facts for this candidate. Qwen pattern-matches on metric identity and produces near-verbatim example output. When judges detect low synthesis originality, they soft-fail → regen fires.

**Fix:**
1. Replace all real candidate metrics in `exec_summary_pos_svp_it_strategy_001` with transposed values from a different-domain persona (e.g. supply chain / manufacturing IT), so Qwen cannot echo the example by metric value. Arc, voice, and S1–S6 structure remain instructive; numbers change.
2. In `e0_examples.py → build_executive_summary_e0()`: restore `exec_summary_pos_credibility_implied_001` as a second positive on the strategy-executive lane (currently excluded when `strategy_executive=True`). This gives Qwen two structurally different arcs to draw from.

**Definition of Done:**
- `exec_summary_pos_svp_it_strategy_001.after` contains no `$22M`, `20%`, `8 to 28`, `40%` metric literals.
- `build_executive_summary_e0(strategy_executive=True)` emits two `<positive_example>` blocks.
- New unit test: `test_e0_svp_lane_no_real_metric_anchors` — asserts that both positives for SVP lane do not contain the string literals `"$22M"`, `"8 to 28"`, `"40%"` (metrics that appear verbatim in C0 facts for this target).
- New unit test: `test_e0_svp_lane_emits_two_positives` — asserts two positives on `strategy_executive=True`.

---

## Wave 2 — Delete Dead Constant + Consolidate Stock-Bridge Rule in I0

**Problem A:** `SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR` in `executive_summary_pa.py` (lines 310–321) and re-exported in `dispatch/executive_summary_pa.py` is never injected into any prompt path — confirmed by tracing all call sites of `format_srfs_style_only_quality_oneshot_block()`. It diverged from the YAML example (different S5 wording) and is a maintenance hazard.

**Problem B:** "Max two stock bridges" appears three times in I0:
- `six_sentence_period_contract` — "max two stock bridges"
- `approved_non_stock_openers` — "At most **two** stock bridges among..."
- `judge_alignment_contract → Connectives` — "At most two stock openers"

Repetition creates an anxiety signal; the model over-focuses on bridge avoidance and produces tonally degraded prose that judges soft-fail on `synthesis_quality`.

**Fix:**
1. Delete `SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR` constant and its `__all__` entries from both files. Add a grep-sentinel comment: `# SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR removed 2026-05-27 — was never injected; use E0 YAML`.
2. In `executive_summary.generate_scratch_v1.yaml`:
   - Remove "max two stock bridges" from `six_sentence_period_contract` (keep the 6-sentence count rule there).
   - Remove the stock bridge count from `approved_non_stock_openers` (keep the list of allowed openers).
   - Retain a single authoritative statement only in `judge_alignment_contract → Connectives`.

**Definition of Done:**
- `SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR` does not appear in any `.py` file (grep sentinel).
- "max two stock bridges" / "At most **two** stock bridges" appears exactly once in the compiled I0 (unit test over the rendered template).
- `test_i0_stock_bridge_rule_stated_once` — asserts count of "stock bridge" occurrences in rendered I0 == 1.

---

## Wave 3 — Promote S4 Opener Directive to I0

**Problem:** The `s4_opener_directive` injected by `executive_summary_composition.py` into U0 (lowest authority slot) says: "S4 MUST use a non-stock opener on SVP strategy lanes with ≥3 brushstrokes." Because U0 has lower authority than I0 and appears later in the compiled prompt, Qwen may not consistently honour this on first pass — causing the synthesis regen that was the original trigger for the W1–W6 session.

**Fix:**
1. In `I0 → judge_alignment_contract → **S4:**` clause of `executive_summary.generate_scratch_v1.yaml`, append: "On SVP strategy lanes with ≥3 brushstrokes S4 MUST use a non-stock opener (e.g. `In parallel,` / `That operating foundation also,`) — S2 and S3 exhaust both available stock-bridge slots."
2. The runtime `s4_opener_directive` in `executive_summary_composition.py` remains as-is for per-run prescription (dynamic brushstroke count). W3 adds a static advisory in I0 that fires unconditionally — belt-and-suspenders.
3. No change to `executive_summary_composition.py` logic.

**Definition of Done:**
- `executive_summary.generate_scratch_v1.yaml` I0 `judge_alignment_contract` S4 clause contains the non-stock opener directive.
- `test_i0_s4_directive_present` — asserts the static directive is in rendered I0.
- Existing `test_composition_plan_s4_opener_directive_svp_lane` (from W4 session) still passes.

---

## Wave 4 — Reduce self_check + Cap JUDGE_REGEN_MAX_ATTEMPTS

**Problem A:** `self_check` requires 12+ boolean fields. Fields like `no_first_person`, `s5_no_derivatives_inventory`, `s5_no_derivatives_or_employer_inventory`, `no_extend_that_arc_toward_phrase`, `achievement_verb_opener_count_at_most_2`, `no_inline_source_tags`, `s6_no_looking_ahead_opener` are fully enforced by X2 gates deterministically. Qwen spends generation budget producing these booleans. For a local vLLM model with limited output token budget, this leaves less headroom for prose quality.

**Problem B:** `JUDGE_REGEN_MAX_ATTEMPTS = 10`. With E0 root cause unfixed (before W1), 10 cycles was the only way to eventually escape the structural attractor. After W1 reduces first-pass structural mimicry, 3 cycles is sufficient for marginal quality fixes. The current `REGEN_CAPS=1` path caps at 3 but is opt-in only.

**Fix:**
1. Reduce self_check in `I0 → self_check_requirements` to 5 fields: `executive_strategy_thesis_present`, `jd_used_as_proof_false`, `s6_forward_synthesis_not_recap`, `material_metrics_surfaced_in_display_rows_3_4_5`, `every_material_claim_in_claim_ledger`.
2. Update `R0` JSON schema in `executive_summary_pa.py` to mark only these 5 as required in `self_check`.
3. Set `JUDGE_REGEN_MAX_ATTEMPTS = 3` in `executive_summary_repair_policy.py`. Update `JUDGE_REGEN_MAX_ATTEMPTS_HARD_CAP = 10` (unchanged — operator can override).

**Definition of Done:**
- `self_check_requirements` in template contains exactly 5 field names.
- `JUDGE_REGEN_MAX_ATTEMPTS` constant = 3 in repair policy.
- `test_self_check_fields_count` — asserts 5 fields in rendered I0 self_check block.
- `test_judge_regen_max_attempts_default_is_3` — asserts `judge_regen_max_attempts()` returns 3 without env override.

---

## Wave 5 — Convert Retired Gold Example + Proof Re-run

**Problem:** `exec_summary_gold_base_resume_001` (excluded from compile) contains `"engineering scale-out"` and `"reusable platform services adopted across enterprise programs"` — both in `SRFS_FORBIDDEN_PHRASES_ALWAYS`. If accidentally re-included, these phrases would silently appear in the positive example and bias Qwen toward emitting them. There is also no negative example targeting these two specific phrases.

**Fix:**
1. Change `category: positive_gold` → `category: negative` and `authority: E0_STYLE_EXAMPLE_NOT_PROOF` → `authority: E0_NEGATIVE_FORBIDDEN_PHRASES` in `exec_summary_gold_base_resume_001`.
2. Update annotation to cite the specific forbidden phrases.
3. Run full Brown & Brown SVP proof re-run to confirm all X2 gates still pass after W1–W4 changes.

**Definition of Done:**
- `exec_summary_gold_base_resume_001.category == "negative"` in YAML.
- Proof run exits 0 with `x2_failed_gates: []`.
- `PRODUCT_QUALITY_STATUS: PASS`.

---

## Deferred Scope

```
DEFERRED_SCOPE: plan=qwen-prompt-regen-reduction-7481e3
  item="Exploratory full-paragraph regen flag (APPS_RG_EXEC_SUMMARY_EXPLORATORY_FULL_PARAGRAPH_REGEN)"
  reason="Opt-in only, off by default, no regen-cycle impact until enabled. Review after W1–W4 proof."
  p_band=P3

DEFERRED_SCOPE: plan=qwen-prompt-regen-reduction-7481e3
  item="Per-section prompt audit for non-executive-summary lanes (competencies, unify_bullets, ibm_bullets)"
  reason="Audit found no E0 metric contamination or regen-cycle risk in those lanes. Lower priority."
  p_band=P3

DEFERRED_SCOPE: plan=qwen-prompt-regen-reduction-7481e3
  item="Judge soft-fail threshold calibration (APPS_RG_EXEC_SUMMARY_JUDGE_PASS_FLOOR)"
  reason="Threshold tuning requires judge score distribution data from post-W1 runs. Separate calibration cycle."
  p_band=P2
```
