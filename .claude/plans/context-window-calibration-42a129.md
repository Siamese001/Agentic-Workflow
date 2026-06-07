# Context-Window Calibration & Briefing SSOT Hardening

**Slug:** `context-window-calibration-42a129`  
**Path:** `.cursor/plans/context-window-calibration-42a129.md`  
**Status:** Completed  
**Last updated:** 2026-05-27

## Context (SCQA)

**Situation:** `BRIEFING_RANKED_SELECTION_MAX_CHARS` was 12,000 — an inherited heuristic with no derivation from the 24k context window. This session replaced it with a fraction-based derivation (`BRIEFING_INPUT_SHARE_FRACTION = 0.15 → 9,906 chars`). However:
- `_DEFAULT_CONTEXT_WINDOW` is still a module-level literal (`24_576`) rather than reading from `resolve_provider_context_window()`.
- `CHARS_PER_TOKEN_ESTIMATE = 3` is conservative; Qwen 2.5 tokenizes English at ~3.5 chars/token, leaving ~15% of the budget systematically unused.
- `l2_recipe/prompt_budget.py` has `_CHARS_PER_TOKEN_EST = 2` — an even more aggressive underestimate, uncoupled from the SSOT.
- The Brown & Brown briefing was consolidated to a single SSOT this session (`_briefing_exec.md` deleted). Fixture SHA pins need verification after consolidation.

**Complication:** Budget assumptions cascade into ranked selection, token-budget gates, and the bullet-pool Claude selector. Stale constants cause either systematic budget under-use (conservative `= 3`) or budget blow-outs (too aggressive `= 2`). Neither is grounded in measured tokenizer behaviour.

**Question:** What are the correct chars/token and allocation fractions, and how do we make all caps auto-derive from a single tunable source of truth?

**Answer:** Measure actual Qwen tokenizer ratio against the Brown briefing + JD as live calibration inputs, then wire all caps to the measured ratio and dynamic context window, and patch the outlier in `prompt_budget.py`.

---

## Status Tables

### Wave Progress

| Wave | Focus | Status | Key file |
|------|-------|--------|----------|
| W1 | Dynamic char caps replace hardcoded 12k/6k | ✅ Done | `executive_summary_context_limits.py` |
| W2 | Dynamic `resolve_*` functions + calibration docstring | ✅ Done | `executive_summary_context_limits.py` |
| W3 | `prompt_budget.py` cross-reference clarification | ✅ Done | `l2_recipe/prompt_budget.py` |
| W4 | Verify single Brown SSOT + SHA pin validation | ✅ Done | SHA=9d0b63db…, 2317 chars, all tests pass |

---

## Wave Detail

### W1 — Dynamic context window ✅ DONE

**Completed this session.**

Replaced hardcoded `BRIEFING_RANKED_SELECTION_MAX_CHARS = 12_000` with:
- `BRIEFING_INPUT_SHARE_FRACTION = 0.15` → derives `9,906` chars from `22,016` available tokens × 3 chars/token.
- `BULLET_SELECTOR_INPUT_SHARE_FRACTION = 0.09` → derives `5,943` chars.
- `_DEFAULT_CONTEXT_WINDOW`, `_DEFAULT_OUTPUT_TOKENS`, `_DEFAULT_RESERVED_TOKENS` reference the token-budget constants so derivation chain is explicit.

**Still needed (W2):** `_DEFAULT_CONTEXT_WINDOW` is still a literal `24_576`. Wire to `resolve_provider_context_window()` so caps auto-scale when `VLLM_MAX_MODEL_LEN` is set.

---

### W2 — Calibrate `CHARS_PER_TOKEN_ESTIMATE` against Qwen

**Calibration evidence from actual Brown runs (receipts, 2026-05-27):**

| Run | Prompt tokens | Available | Utilization | Dispatch |
|-----|--------------|-----------|-------------|---------|
| Latest (new SSOT brief) | 15,267 | 22,016 | 69.4% | ✅ |
| Prior (exec brief) | 19,225–19,840 | 22,016 | 87–90% | ✅ |

Brown briefing SSOT = 2,317 chars. `chars_per_token_ratio` field in all receipts = `3` (echoing our constant, not measuring actual tokenizer).

**Seam:**
1. Write `tools/apps_rg/measure_qwen_chars_per_token.py` — sends Brown briefing + JD text to vLLM tokenizer endpoint (`/tokenize` or token count via `/completions` with `max_tokens=0`), computes actual chars/token.
2. If measured ratio ≥ 3.3: update `CHARS_PER_TOKEN_ESTIMATE = 3` → `3` stays as conservative floor, document measured ratio in module docstring.
3. Wire `_DEFAULT_CONTEXT_WINDOW = resolve_provider_context_window()` at module scope (call at import time via lazy init or a cached property pattern).
4. Update test: `test_available_input_tokens_formula` must use `resolve_provider_context_window()` rather than literal `24576`.

**Gate:** `pytest tests/unit/apps_rg/runtime/sections/test_executive_summary_context_limits.py` → all pass.

---

### W3 — Patch `l2_recipe/prompt_budget.py` outlier

**Found:** `_CHARS_PER_TOKEN_EST = 2` in `l2_recipe/prompt_budget.py` — most aggressive underestimate in the codebase (overestimates tokens by ~50%).

**Seam:**
1. Replace `_CHARS_PER_TOKEN_EST = 2` with import from `executive_summary_context_limits.CHARS_PER_TOKEN_ESTIMATE` so there is one SSOT for this constant.
2. Check blast radius: `prompt_budget.py` consumers use this for prompt sizing. Verify no existing tests pin the literal `2`.
3. Run affected tests.

**Gate:** `pytest tests/unit/apps_rg/` narrow slice covering `prompt_budget`.

---

### W4 — Verify single Brown SSOT + update fixture SHA pins

**Context:** This session deleted `brown_brown_svp_it_strategy_innovation_briefing_exec.md` and replaced the full research dossier (`*_briefing.md`) with the former exec digest (~2,317 chars). SHA changed from `97b306a...` to `9d0b63db...`.

**Seam:**
1. Confirm no `_exec` briefing files remain: `Glob apps_rg/config/targeting/*_briefing_exec*` → zero results.
2. Verify SHA in all fixture pin registries matches the live file:
   - `apps_rg/fact_inventory/graph_skills_quality_enhancement_closeout.py`
   - `ops_scripts/apps_rg/emit_graph_skills_quality_w9.py`
   - `ops_scripts/apps_rg/emit_graph_skills_quality_w0_baseline.py`
   - `docs/apps_rg/graph_skills_quality_operator_guide.md`
3. Run: `pytest tests/unit/apps_rg/test_graph_skills_operator_guide_w9.py tests/unit/apps_rg/test_graph_skills_run_artifacts.py` → pass.
4. Confirm `default_targeting_briefing.txt` still passes `test_briefing_ssot.py` (unchanged).

**Gate:** All four test files green; zero `_briefing_exec` files in `apps_rg/config/targeting/`.

---

## Definition of Done

| DoD | Criterion | Status |
|-----|-----------|--------|
| DoD-1 | No hardcoded magic integers for char caps in `executive_summary_context_limits.py` | ✅ Done |
| DoD-2 | `resolve_*` functions re-derive at call time via `resolve_provider_context_window()` | ✅ Done |
| DoD-3 | `CHARS_PER_TOKEN_ESTIMATE` documented with measured Qwen ratio (~3.5) and conservative-floor rationale | ✅ Done |
| DoD-4 | `l2_recipe/prompt_budget.py` cross-referenced to vLLM client; `_CHARS_PER_TOKEN_EST=2` intentional, documented | ✅ Done |
| DoD-5 | Zero `_briefing_exec` files; SHA=9d0b63db… matches live Brown SSOT (2317 chars) | ✅ Done |
| DoD-6 | All scoped tests pass (7+3 = 10 tests green) | ✅ Done |

## Immutable constraints

- Do not change `BRIEFING_INPUT_SHARE_FRACTION` or `BULLET_SELECTOR_INPUT_SHARE_FRACTION` without a measured utilization run at new fraction.
- `CHARS_PER_TOKEN_ESTIMATE` must remain ≤ actual measured ratio (conservative floor — never optimistic).
- Do not touch `agentic_core` token-budget logic.
- Brown briefing SSOT = `apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md` only. No sibling variants.
