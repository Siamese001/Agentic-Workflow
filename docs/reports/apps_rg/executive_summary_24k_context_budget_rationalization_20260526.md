# Executive summary — 24k context lens & input budget rationalization

> **SSOT:** `VLLM_MAX_MODEL_LEN=24576` ([`docker-compose.qwen.yml`](../../../docker-compose.qwen.yml), [`model_registry.py`](../../../agentic_core/L0_routing/config/model_registry.py)).  
> **Targeting caps:** [`executive_summary_targeting_cap.py`](../../../apps_rg/runtime/sections/executive_summary_targeting_cap.py).  
> **Token budget policy:** [`executive_summary_token_budget.py`](../../../apps_rg/runtime/sections/executive_summary_token_budget.py).  
> **Char/token SSOT:** [`executive_summary_context_limits.py`](../../../apps_rg/runtime/sections/executive_summary_context_limits.py) · closeout [executive_summary_context_limits_ssot_closeout_20260526.md](executive_summary_context_limits_ssot_closeout_20260526.md).  
> **Operator runbook:** [`executive_summary_operator_guide.md`](../../apps_rg/executive_summary_operator_guide.md).

## Summary

The local Qwen lane moved from a **16,384** planning lens to **24,576** (`--max-model-len`). After raising targeting char ceilings (briefing **16,000**, JD **6,000**) and passing full Brown SVP JD + briefing into the prompt, **total first-pass dispatch stays well under both the hard input cap and the 92% first-pass gate** — with roughly **3.4k–5.2k tokens of headroom** on a representative Brown compile.

C0 is **not** the full augmented-skills graph SQLite; it is a **small HIGH fact slice** plus allowlist. JD and briefing are **targeting-only** (never proof).

---

## Context window → available input

| Term | @ 16,384 (legacy lens) | @ 24,576 (current SSOT) |
|------|------------------------:|------------------------:|
| Provider context window | 16,384 | **24,576** |
| Max completion (scratch) | 2,048 | 2,048 |
| Reserved (schema/system) | 512 | 512 |
| **Available input** | **13,824** | **22,016** |
| **92% first-pass cap** | **12,718** | **20,254** |

Formula (unchanged):

```text
available_input_tokens = VLLM_MAX_MODEL_LEN - requested_max_output_tokens - 512
first_pass_limit       = floor(available_input_tokens × 0.92)   # code constant (not env-overridable)
```

---

## Why 16k felt “blocked” while 24k passes

| Check | @ 16,384 (historical Brown estimate) | @ 24,576 (measured 2026-05-26) |
|-------|--------------------------------------:|--------------------------------:|
| Dispatch (post-targeting-cap) | ~**13,828** | **16,860** |
| Hard cap (available input) | 13,824 — **fail (+4)** | 22,016 — **pass** |
| 92% cap | 12,718 — **fail (~+1,110)** | 20,254 — **pass (~+3,394 under)** |
| Utilization vs available | ~100% | **~76.6%** |
| Budget dispatch allowed? | **No** (first-pass 92%) | **Yes** |

The ~13.8k @ 16k figure included **heavy targeting compression** (JD ~2k / briefing ~2.6k char defaults). That compression was appropriate for a tight window but **dropped most of the 15k-char briefing and half the JD** even when the model context could have carried more.

---

## Targeting char policy (current — token budget is authority)

No env-overridable briefing/JD char caps. When the compiled prompt fits (`gap_tokens == 0`), targeting prose passes through **verbatim**. If the prompt exceeds `available_input_tokens`, `apply_executive_summary_targeting_cap` sheds JD/briefing by `gap_tokens` only.

| Field | Brown SVP source size | In prompt (typical) |
|-------|----------------------:|--------------------:|
| **Briefing** | ~15,210 | ~15,825 (full doc + cap notice) |
| **JD** | ~4,335 | ~4,399 (full JD + cap notice) |

---

## Measured Brown SVP dispatch budget (@ 24,576)

**Method:** `compile_executive_summary_prompt` + evidence capsule + `apply_executive_summary_targeting_cap` with `available_input_tokens=22016`, Brown JD/briefing SSOT, augmented-skills graph (**7** executive_summary facts). Estimator: `len÷3 × 1.12` ([`estimate_tokens_approximate`](../../../apps_rg/runtime/sections/executive_summary_token_budget.py)).

| Metric | Value |
|--------|------:|
| **Total dispatch (what Qwen sees)** | **16,860** tokens |
| % of available input (22,016) | **76.6%** |
| Headroom to hard cap | **5,156** tokens |
| Headroom to 92% cap (20,254) | **3,394** tokens |
| Targeting region (jd_requirements) before cap | ~8,454 tokens |
| Targeting region after cap | ~7,629 tokens |
| Graph facts in pool | 7 |

**Rationalization:** Full briefing (~15.8k chars ≈ **5.9k** tokens) + full JD (~4.4k chars ≈ **1.6k** tokens) + graph proof slice + I0/R0/E0/U0/S0 ≈ **16.9k** total — still **under 20,254** (92%) with **~3.4k** tokens before first-pass block.

---

## Prompt composition (conceptual — not full SQLite)

| Region | Role | ~tokens @ 24k Brown | Proof? |
|--------|------|--------------------:|:------:|
| **JD_TEXT** | Job targeting vocabulary | ~1,600 | No |
| **BRIEFING** | Strategic / industry targeting | ~5,900 | No |
| **C0 graph slice** | HIGH facts + allowlist + capsule | ~1,100 | **Yes** |
| **I0** | Voice, 6-sentence law, judge arc | ~1,400 | Law |
| **R0** | JSON schema / PRODUCT_SHAPE | ~1,700 | Shape |
| **U0** | Task + composition / arc weights | ~1,500 | Plan |
| **E0** | Style examples | ~2,900 | Style |
| **S0 + D0 + Y0** | System + hygiene | ~500 | — |
| **Total dispatch** | | **~16,860** | |

**Not in prompt:** full `augmented_skills_graph.sqlite` / JSON ledger (**236** nodes, **1,400** edges). SQLite is used at **resolve** time for fact/skill selection; only the **executive_summary slice** and a small **graph targeting capsule** (~960 chars max, non-proof) surface in the compiled prompt.

---

## Headroom diagram

```text
0                    20,254 (92% gate)    22,016 (hard)   24,576 (ctx)
|------------------------|------------------|---------------|
|<<<<<<<< dispatch 16,860 >>>>>>>>| 3,394  | 5,156         | +2,560 completion+reserve
```

Scratch generation still reserves **2,048** completion tokens inside the 24,576 window; do not add completion to “available input” above.

---

## Operational implications

1. **Set `VLLM_MAX_MODEL_LEN=24576`** to match Docker `--max-model-len` (see [`executive_summary_operator_guide.md`](../../apps_rg/executive_summary_operator_guide.md)).
2. **Briefing/JD:** Full Brown SSOT passes through at 24k; pre-truncation is unnecessary unless `token_budget_receipt.json` shows `dispatch_allowed: false`.
3. **First-pass block** at 24k is unlikely for Brown-scale prompts unless E0/C0/facts grow materially; watch `token_budget_receipt.json` → `first_pass_utilization_pct`.
4. **Proof discipline unchanged:** More briefing does **not** add proof — only C0 `fact_id` lines authorize `claim_ledger`.
5. **Gemini / external research:** Paste full research into the briefing slot; if dispatch blocks, read `token_budget_receipt.json` — do not rely on hidden char env caps.

---

## Related artifacts

| Artifact | Path |
|----------|------|
| Docker max model len | [`docker-compose.qwen.yml`](../../../docker-compose.qwen.yml) |
| Brown briefing SSOT | [`brown_brown_svp_it_strategy_innovation_briefing.md`](../../../apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md) |
| Brown JD SSOT | [`brown_brown_svp_it_strategy_innovation_jd.txt`](../../../apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt) |
| Targeting cap tests | [`test_executive_summary_targeting_cap.py`](../../../tests/unit/apps_rg/runtime/sections/test_executive_summary_targeting_cap.py) |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-05-26 | Document 24k lens vs 16k; rationalize Brown dispatch **16,860 / 22,016** with headroom. |
| 2026-05-26 | Remove env-overridable briefing/JD char caps; token budget + `gap_tokens` targeting shed only. |
