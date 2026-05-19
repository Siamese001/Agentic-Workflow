# Live Qwen remaining blockers — Wave 1 inventory

**STATUS: RCA_COMPLETE**

Wave 1 inspects the four blocker runs cited in [live_qwen_all_section_outputs.json](live_qwen_all_section_outputs.json). Skills authority remained `augmented_skills_graph` PASS on all sections; blockers are generation/X2/judge shaped.

## Competencies (`competencies_20260518_233832`)

| Signal | Value |
|--------|--------|
| Provider | `qwen_vllm` attempted, `provider_available=false` |
| Error | `TimeoutError: timed out` (3 transport retries @ 60s) |
| `max_tokens` | 4096 |
| Compiled prompt | ~30,763 bytes |
| Output | Empty `competencies[]` |

**Root cause:** Transport timeout under prompt bloat + very high completion budget (4096 tokens), not skills-graph regression. The PA injects a large `VERIFIED_SKILL_INVENTORY_PROJECTION` block (12k-char cap) on top of employment facts.

**Planned fix (Wave 2):** Lower `COMPETENCIES_QWEN_MAX_TOKENS` to 1600, cap projection inject to 4500 chars, competencies-only chat timeout 120s (`APPS_RG_COMPETENCIES_QWEN_CHAT_TIMEOUT_SECONDS`).

## IBM bullets (`ibm_bullets_20260518_234400`)

| Failed X2 | Why |
|-----------|-----|
| `x2_ibm_metrics_preserved` | Model rewrote thin ledger facts; missing canonical `$15M`, `99.9%`, `30%`, `25%`, `50%` |
| `x2_claim_ledger_coverage_100` | `bul_ibm_*` output ids not in `allowed_fact_ids` (fact_* only); ledger roots lack `bul_ibm_*` for structural coverage |

**Root cause:** `candidate_fact_ledger` company-hint slice delivered 3 facts while gates expect five canonical IBM bullets + core metrics from locked resume copy.

**Planned fix:** Deterministic `hydrate_parsed_ibm_bullets_from_canonical_resume` when ledger slice &lt; 5 rows; union canonical `bul_ibm_*` into runtime allow-list.

## IBM narrative (`ibm_narrative_20260518_234511`)

**Root cause:** `reconcile_narrative_claim_ledger` fallback stamped `bul_ibm_001` while active allow-list is `fact_*` only — eight X2 gates failed on allow-list / pool membership.

**Planned fix:** `remap_ibm_narrative_claim_ledger_to_fact_pool` + fact-aware reconcile fallback.

## Executive summary (`exec_summary_20260518_233710`)

| Signal | Value |
|--------|--------|
| X2 | PASS (2–3 sentence mode) |
| X3 | `X3_REVIEW_JUDGE_SOFT_FAIL` |
| Judges | gemini_pro, openai_chatgpt, anthropic_claude below threshold |

**Root cause:** Judges apply five-sentence SRFS rubric; deterministic X2 for non-SRFS runs allows 2–3 sentences only. Safe expansion to five sentences would fail `x2_resume_display_sentence_count_2_3`.

**Planned fix:** Document as **open judge gap** (no gate weakening).

## Wave 1 commands

- `git diff -- agentic_core` → clean
- `python -m compileall apps_rg tests -q` → (run before Wave 2)
- Section CLI runs deferred to Wave 2 post-patch (prior runs captured above)
