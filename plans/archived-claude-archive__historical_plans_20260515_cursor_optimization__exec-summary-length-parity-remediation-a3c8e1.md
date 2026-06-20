---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\exec-summary-length-parity-remediation-a3c8e1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\exec-summary-length-parity-remediation-a3c8e1.md'
source_sha256: 52cfeaa097669562c43e0e2ebc04b940c2d085295a8d99909a948c1407003178
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan — Exec Summary Length-Parity Remediation (`a3c8e1`)

> **Slug**: `exec-summary-length-parity-remediation-a3c8e1`
> **Status**: Not Started
> **Tier**: T2 (multi-file, single-layer; apps_rg narrative pipeline)
> **Created**: 2026-05-08
> **Trigger run**: `artifacts/apps_rg/runs/r4_72afb54f` (Brown & Brown / SVP IT Strategy)
> **RCA basis**: All 6 generations (3 prompt variants × 2 retry rounds) of `hop_4b_exec_summary` produced 68–76 words against a 104–140 word band — 38–44% under-delivery.

---

## 1. Background — Why this plan exists

### 1.1 Observed failure (this run)

`hop_4b_exec_summary_scorecard_20260508T162947Z.json` shows three Qwen-32B-AWQ candidates:

| Variant | Temp | Words | Target | Range | Composite | Verdict |
|---|---|---|---|---|---|---|
| `structural_a_archetype_first` | 0.55 | 72 | 122 | [104, 140] | 0.6250 | length_parity FAIL |
| `structural_b_outcome_first` | 0.75 | 76 | 122 | [104, 140] | 0.6675 | length_parity + filler FAIL |
| `structural_c_priorities_first` | 0.95 | 68 | 122 | [104, 140] | 0.6315 | length_parity + filler FAIL |

The reinforced retry (`exec_summary_ensemble.py:99-140`) — which already quotes failed counts back at the model — also failed. Disposition: `HUMAN_REVIEW`, critical-section abort.

### 1.2 Root cause (Anthropic-attested)

Anthropic's official guidance at `https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-latency`:

> *"Due to how LLMs count tokens instead of words, asking for an exact word count or a word count limit is not as effective a strategy as asking for paragraph or sentence count limits."*

The current prompts at `apps_rg/integrations/hops/exec_summary_ensemble.py` are built almost entirely on word counts ("MUST be at least N words", "COUNT YOUR WORDS"). This is **the least reliable steering primitive applied to the model archetype that's worst at following it** (32B-AWQ quantized open-weights). Temperature variation (already 0.55/0.75/0.95) gives diversity of phrasing, not length — at every temperature in that band the model has internally decided "exec summary ≈ 75 words".

### 1.3 What's already implemented (do not duplicate)

| Mechanism | Location | State |
|---|---|---|
| 3 structural prompt variants | `exec_summary_ensemble.py:84-86` | ✅ |
| Temperature ladder 0.55/0.75/0.95 | same | ✅ |
| Reinforced retry quoting failed counts | `exec_summary_ensemble.py:99-140` | ✅ |
| Per-sentence word allocations | `_prompt_reinforced_*` | ✅ |
| Filler-intensifier blocklist | same | ✅ |
| `length_parity_strict_gate` ±15% | `per_cand_resume_gates.py:67-140` | ✅ |
| `quantified_outcome_count_gate` (≥2) | `per_cand_resume_gates.py:143-185` | ✅ but not in exec-summary stack |

---

## 2. Scope and Files In Scope

| File | Why |
|---|---|
| `apps_rg/integrations/hops/exec_summary_ensemble.py` | Prompt construction + retry orchestration |
| `apps_rg/integrations/gates/per_cand_resume_gates.py` | `length_parity_strict_gate` tolerance + new structural slot gate |
| `apps_rg/integrations/length_budget.py` | `budget_for_section` if asymmetric tolerance lands here |
| `apps_rg/integrations/hops/_ensemble_runner.py` | Critique-and-revise loop, N candidate count |
| `agentic_core/L0_routing/config/model_registry.py` | Routing critical hops to alternate generator (Tier C) |
| `tests/_apps_contract/test_w5_per_cand_gates.py` | Regression coverage for tolerance + new gate |
| `tests/_apps_contract/test_apps_rg_*.py` | New tests for sentence-count prompts + post-hoc expansion |

**Out of scope** (do not edit):
- Other narrative HOPs (HOP-3, HOP-4A, HOP-4C) — keep their existing prompt shapes
- L3 orchestration / cert pipeline
- vLLM container args (Tier C only — gated to its own wave)

## 3. Non-Goals

- Re-tuning all narrative HOPs to sentence-count framing — exec_summary first, generalize later.
- Replacing Qwen-32B globally — Tier C is opt-in for the critical hop only.
- Adding new judge models or rubric dimensions.
- Modifying R1A / R1B cache behavior.
- Touching the contamination guard or wizard surface.

---

## 4. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| **W1 — Tier A: high-ROI, low-risk** | P1.1, P1.2, P1.3 | Sentence-count primary; asymmetric tolerance; deterministic post-hoc expansion | ~12k | Single-module edits; no new deps | Not Started | apps_rg fresh run on Brown & Brown produces exec_summary in [104,153] band on first round; zero `length_parity` failures across 3 trial company runs |
| **W2 — Tier B: medium-ROI prompt patterns** | P2.1, P2.2, P2.3 | XML slots; critique-revise loop; raise ensemble N=3→5 | ~18k | Adds ~8–12s latency to critical hop | Not Started | exec_summary acceptance rate ≥90% on first round across 5 trial runs; latency Δ ≤+12s |
| **W3 — Tier C: decoding-layer hard floor** | P3.1, P3.2 | vLLM `min_tokens` + repetition_penalty; conditional generator routing | ~20k | vLLM ≥0.6 supports `min_tokens`; routing config has critical-hop override slot | Not Started | exec_summary length-parity = 100% across 10 trial runs OR rollback if tail-repetition rate >5% |
| **W4 — Adjacent gate hardening** | P4.1, P4.2 | Add `quantified_outcome_count` to exec-summary stack; add `structural_slot_coverage` gate; first-person ban for exec_summary | ~8k | Compositional with W1; safe regardless of W2/W3 outcome | Not Started | All exec_summary outputs satisfy ≥2 quantified outcomes + 4 structural slots present + zero "I"/"my" leading verbs |
| **W5 — Verification + capture** | P5.1, P5.2 | 10-trial benchmark across 5 companies × 2 seed lengths; capture `eval_harness_outcome` ledger rows; close plan | ~6k | W1 minimum landed; W2/W3 conditional | Not Started | Length-parity pass rate ≥95% in benchmark; calibration report posted; Notion row → Completed |

## 5. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| **P1.1** | Reframe prompts to sentence-count primary | `exec_summary_ensemble.py` | Re-author all 6 prompt builders without breaking structural diversity | 4k | Not Started |
| **P1.2** | Asymmetric tolerance (-10% / +25%) | `per_cand_resume_gates.py`, `length_budget.py`, `exec_summary_ensemble.py` | Update gate signature + tests; comment with RCA so 2026-05-08 tightening rationale isn't undone | 4k | Not Started |
| **P1.3** | Programmatic post-hoc expansion | `exec_summary_ensemble.py`, new helper module | Append a marquee_outcome sentence when candidate is ≥20 words short and otherwise gate-clean; provenance must trace appended sentence | 4k | Not Started |
| **P2.1** | XML structural slots in prompts | `exec_summary_ensemble.py` | Embed `<sentence_1_archetype>`/`<sentence_2_outcomes>`/etc.; parse out at render time | 6k | Not Started |
| **P2.2** | Critique-and-revise retry round | `exec_summary_ensemble.py`, `_ensemble_runner.py` | Replace second-round retry with critique→revise; preserve archive_dir traces | 6k | Not Started |
| **P2.3** | Raise candidate count 3→5 with controlled temperature spread | `_ensemble_runner.py`, `exec_summary_ensemble.py` | Latency budget; adjust archive_dir naming for 5 cands | 6k | Not Started |
| **P3.1** | vLLM `min_tokens` plumb-through | `agentic_core/L0_routing/config/model_registry.py`, generator client | Sampling param surface; Qwen-AWQ tail-repetition risk; needs `repetition_penalty` co-tuning | 12k | Not Started |
| **P3.2** | Critical-hop generator routing override | `model_registry.py`, `exec_summary_ensemble.py` | Conditional generator selection without polluting non-critical hops; cost guard | 8k | Not Started |
| **P4.1** | Add `quantified_outcome_count` to exec-summary gate stack | `per_cand_resume_gates.py`, `_ensemble_runner.py` | Existing gate, just wire it; expect 1–2 candidate failures on early Qwen runs | 4k | Not Started |
| **P4.2** | New gates: `structural_slot_coverage`, `first_person_lead_ban` for exec_summary | `per_cand_resume_gates.py`, `registry.py` | Regex/keyword markers per slot; recruiter-tone first-person ban (3rd-person voice) | 4k | Not Started |
| **P5.1** | 10-trial benchmark + ledger capture | `tools/apps_rg/`, `eval_harness_outcome` ledger | 5 companies × 2 seed lengths; capture pass-rate, latency Δ, candidate distribution | 4k | Not Started |
| **P5.2** | Plan closeout + Notion sync | Notion Plans DB | `WAVE_COMPLETE:` marker per wave; Notion row → Completed; AG queue drain | 2k | Not Started |

---

## 6. Detailed Wave Plans

### W1 — Tier A (highest ROI)

#### P1.1 — Sentence-count primary

Rewrite `_prompt_archetype_first`, `_prompt_outcome_first`, `_prompt_priorities_first` and all 3 reinforced variants. Replace word-count framing with **sentence-count + per-sentence content slot** framing:

```
Write EXACTLY 4 sentences. Each sentence 25–35 words.
Sentence 1: Archetype + accurate tenure (e.g. '24+ years') — single fact-dense sentence.
Sentence 2: Two quantified outcomes joined by 'and', with %, $, or scale.
Sentence 3: Engagement model + 3-item capability cluster.
Sentence 4: Value thesis with measurable business outcome.
```

Anthropic doctrine: sentences are token-anchored verifiable units; words are not. Repeat the sentence-count constraint at the **end** of the prompt (primacy + recency).

#### P1.2 — Asymmetric tolerance

Change `length_parity_strict_gate` to accept `tolerance_below` and `tolerance_above` separately. Default: `(0.10, 0.25)`. Backwards-compatible: `tolerance: float` still accepted, applied symmetrically. Threshold profile updates for exec_summary only — leave bullet-level gates symmetric.

```python
def length_parity_strict_gate(
    artifact, context,
    *,
    tolerance_below: float | None = None,
    tolerance_above: float | None = None,
    tolerance: float = 0.15,
) -> GateVerdict: ...
```

For 122-word reference, range becomes `[110, 153]` (vs current `[104, 140]`). The 5 failing candidates (68/72/76/68/—/—) still fail this — **the asymmetry alone does not paper over the under-delivery**; it only stops penalizing the model for landing slightly long.

#### P1.3 — Post-hoc expansion (deterministic rescue)

When all candidates fail length_parity AND no candidate has length within 30% AND otherwise pass non-length gates, append a deterministic sentence built from `marquee_outcomes[0]` not yet present in the candidate. Tag the appended sentence with provenance metadata so master_bullets traceability is preserved. Bounded to one append; if still short, fall through to current human-review disposition.

### W2 — Tier B (medium ROI)

#### P2.1 — XML structural slots

```
Return your answer as:
<exec_summary>
  <s1_archetype>...</s1_archetype>
  <s2_outcomes>...</s2_outcomes>
  <s3_engagement>...</s3_engagement>
  <s4_thesis>...</s4_thesis>
</exec_summary>
```

Parse + concatenate at render time. Anthropic explicitly recommends XML format indicators for steerability. Forces 4 distinct slots; raises floor word count by construction.

#### P2.2 — Critique-and-revise loop

Replace second-round retry with: (a) feed failed draft back as `<draft>...</draft>`, (b) ask model to **critique its own draft** against criteria (sentence count, quantified outcomes, archetype lead), (c) ask for a revised draft. This is Anthropic's prompt library pattern for length/tone targets and out-performs raw re-generation in IFEval-style benchmarks.

#### P2.3 — N=5 candidates

Raise ensemble from 3 → 5 with temperatures `[0.45, 0.65, 0.75, 0.85, 0.95]`. Best-of-5 has substantially higher chance of in-band landing. Latency budget: ~+8s per critical hop run (parallel calls). Add latency telemetry to `eval_harness_outcome`.

### W3 — Tier C (decoding-layer hard floor)

#### P3.1 — vLLM `min_tokens`

vLLM `SamplingParams` supports `min_tokens` (forces continuation past EOS until reached). For 122-word target ≈ 165 tokens; set `min_tokens=140` to guarantee floor. Co-tune `repetition_penalty=1.15` and `presence_penalty=0.4` to suppress tail repetition. Risk: incoherence / over-claim — mitigated by P4 gates.

#### P3.2 — Critical-hop generator routing

Add `generator_override` in `cert_route_registry.yaml` (or `model_registry.py`) for `hop_4b_exec_summary` only. Optional: route this single hop to Anthropic Claude when `ANTHROPIC_API_KEY` set; fall back to Qwen-32B with min_tokens guard. Keep all non-critical hops on Qwen.

### W4 — Adjacent gate hardening

#### P4.1 — Wire `quantified_outcome_count` into exec-summary stack

Already implemented at `per_cand_resume_gates.py:143`; not currently in exec-summary's per-cand gate list (`registry.py`). Add. Min 2 outcomes already aligned with prompt instruction.

#### P4.2 — New gates

- **`structural_slot_coverage_gate`**: regex/keyword marker check that each of {archetype, outcome, engagement_model, value_thesis} is present.
- **`first_person_lead_ban_gate`**: exec_summary candidates leading with "I have / I am / I specialize" downgraded; recruiters expect 3rd-person executive voice.

### W5 — Verification + capture

#### P5.1 — Benchmark

10-trial run: 5 companies (Brown & Brown, plus 4 others from existing `_interactive_brief_*.json`) × 2 seed lengths (~80 words, ~140 words). Capture per-trial:
- length_parity pass rate
- candidate distribution (mean, σ word count)
- latency Δ vs baseline
- cost Δ (token usage)

Write to `eval_harness_outcome` ledger with `score_band="length_parity_remediation"`.

#### P5.2 — Closeout

`WAVE_COMPLETE:` marker per wave; `PHASE_COMPLETE:` per phase. AG_QUEUE_SEED at plan top for any AG decisions encountered (likely 1: choose between W2 and W3 if W1 alone is insufficient). Notion Plans row Status → Completed; AI Summary updated with benchmark results.

---

## 7. ADG Graph-Layer Evidence

This is a **defect-fix plan, not a refactoring plan** (no module relocation, no new layer crossings, no new edges). Constitutional §22 requires graph-layer evidence for T2/T3 *refactoring* — not bounded defect fixes. Documented for completeness:

- **Affected node**: `apps_rg.integrations.hops.exec_summary_ensemble` (single module)
- **Layer**: L1 cognition (apps_rg owns its own cognition surface; not crossing into L2/L3)
- **Fan-in**: ~1 (only `apps_rg.narrative_pass` calls `generate_exec_summary`)
- **Fan-out**: 3 (`_ensemble_runner`, `length_budget`, `mirror_terms` registry)
- **Hotspot archetype**: `STATE_NODE` (mutates ensemble retry state) — not `CENTRAL_DEPENDENCY` or `ORCHESTRATOR`
- **Surface intersections**: none of the 5 (Execution, Write, Security, State, Observability) — pure prompt-construction logic
- **No new MV / P-view rows expected** post-remediation

If the plan grows to add a new generator routing surface (W3.P3.2), graph-layer evidence will be added at that wave's start.

---

## 8. Risks and Rollback

| Risk | Probability | Mitigation | Rollback |
|---|---|---|---|
| Tier A asymmetric tolerance accidentally accepts truncated outputs | Low | -10% floor still rejects current 68-76 word outputs (would need >99 words to pass) | Revert tolerance to symmetric 0.15 |
| Sentence-count framing breaks structural diversity | Medium | Keep 3 prompt variants; sentence-count layered on top | Restore word-count framing branch |
| Post-hoc expansion appends sentence misaligned with company facets | Medium | Append only from `marquee_outcomes` (already JD-aligned); provenance traceable | Disable post-hoc; fall through to human review |
| vLLM `min_tokens` produces tail repetition | Medium-High | Repetition penalty + max_tokens cap; W4 gates catch bad output | Disable `min_tokens`; revert to W1+W2 stack |
| Anthropic generator routing leaks API cost | Low | Critical-hop only; conditional on env var | Remove override from `cert_route_registry.yaml` |

---

## 9. Success Criteria (plan-level)

After W1 complete:
- 5 trial runs across 5 companies: ≥4/5 produce exec_summary in [110, 153] band on first round.
- Zero `length_parity` failures in 3 consecutive Brown & Brown runs.

After W5 complete:
- 10-trial benchmark: length_parity pass rate ≥95% on first round.
- Latency Δ ≤ +12s on critical hop.
- `eval_harness_outcome` ledger captures 10 rows with calibration metrics.
- Notion Plans row → Completed.

---

## 10. AG Queue Seeds

`AG_QUEUE_SEED: plan=exec-summary-length-parity-remediation-a3c8e1 id=ag-w2-or-w3 depends_on= title=Choose W2 (prompt-pattern bundle) vs W3 (decoding-layer hard floor) if W1 alone misses ≥95% target`

`AG_QUEUE_SEED: plan=exec-summary-length-parity-remediation-a3c8e1 id=ag-tier-c-anthropic-routing depends_on=ag-w2-or-w3 title=Approve routing critical hop to Anthropic Claude when ANTHROPIC_API_KEY available (cost vs reliability tradeoff)`

`AG_QUEUE_SEED: plan=exec-summary-length-parity-remediation-a3c8e1 id=ag-generalize-other-hops depends_on=ag-w2-or-w3 title=Generalize sentence-count framing to HOP-4A (headline) and HOP-4C (competencies) after exec_summary stable`

---

## 11. References

- `https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-latency` — word-count vs sentence-count guidance
- `https://docs.anthropic.com/en/prompt-library/library` — XML format indicators, "tell what to do, not what not to do"
- `https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips` — prompt structure for long inputs
- IFEval benchmark (Google Research) — verifiable instruction-following including word counts
- arxiv 2502.14255 — prompt length vs domain task accuracy
- Trigger run: `artifacts/apps_rg/runs/r4_72afb54f/narrative/candidates/hop_4b_exec_summary_scorecard_20260508T162947Z.json`
- Existing implementation: `apps_rg/integrations/hops/exec_summary_ensemble.py:99-140` (reinforced retry — already tried and insufficient)
- Constitutional §22 (ADG graph-layer for T2/T3), §30 (Author-Gate capture), §35 (queue drain), §36 (plan registration)

---

## 12. Plan Registration

`PLAN_CREATED: slug=exec-summary-length-parity-remediation-a3c8e1 path=.windsurf/plans/exec-summary-length-parity-remediation-a3c8e1.md status=Not Started`
