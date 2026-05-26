# Competencies schema consumer inventory — W1.0

**Plan:** [prompt-judge-x2-alignment-closeout-c8e4a2](../../.cursor/plans/prompt-judge-x2-alignment-closeout-c8e4a2.md)  
**Date:** 2026-05-26  
**Proof class:** static

## SSOT decision

| Layer | Canonical key | Notes |
|-------|---------------|-------|
| Prompt U0 (W1.3) | `categories[]` with `terms[].text` | Primary emission contract |
| JSON schema | `categories` required; `competencies` optional legacy mirror | [competencies_pa.py](../../apps_rg/runtime/sections/competencies_pa.py) |
| Runtime sync | `sync_categories_competencies()` | [competencies_v3_contract.py](../../apps_rg/runtime/sections/competencies_v3_contract.py) |

## Consumers (read path — keep legacy adapters)

| Consumer | Path | Reads | Action |
|----------|------|-------|--------|
| Lane runtime | `competencies_lane_runtime.py` | `parsed.get("competencies")` | OK — post-sync mirror |
| Lane execution | `competencies_lane_execution.py` | `competencies` + `sync_categories_competencies` | OK — sync before gates |
| Modular export | `modular_rg_output_builder._competencies_to_skills` | `comp_l2.get("competencies")` | OK — category-shaped list |
| Rollup | `generated_lane_rollup.py` | `l2.get("competencies")` | OK — L2 artifact key |
| Bullet pool selector | `bullet_pool_claude_selector.py` | `competencies` in pool paths | OK — transitional |
| Claim ledger | `canonical_exec_summary_v2.py` | `competencies` | OK — companion context |
| Full resume coherence | `full_resume_llm_coherence.py` | `competencies` | OK — snapshot |

## Term key `term` vs `text`

| Location | Status |
|----------|--------|
| X2 validators | Require `text` (+ `source_fact_id`) per [competencies_x2.py](../../apps_rg/runtime/validators/competencies_x2.py) |
| `competencies_v3_contract.legacy_term_from_v3` | Emits both `text` and `term` for adapters |
| Prompt U0 (W1.3) | Teaches `text` only |

## W1.3 change scope

- U0 teaches `categories` (not `competencies` as top-level output key).
- No removal of runtime `competencies[]` mirror — required for export/lane consumers until a dedicated migration plan.
