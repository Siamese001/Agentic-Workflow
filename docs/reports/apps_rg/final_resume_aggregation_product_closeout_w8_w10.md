# Final resume aggregation product closeout — W8–W10

**STATUS: PARTIAL**

Structural aggregation and package X3 are proof-complete on **REAL_LLM** lane pins. **Product ALLOW remains blocked** by two REVIEW lanes (judge soft-fail), cross-section WARN gates, and explicit `product_review_required` policy.

## W8 — Blocked-lane audit

Artifact: [blocked_lane_matrix.json](../../artifacts/apps_rg/runtime_proofs/final_resume_assembly/blocked_lane_matrix.json)

| Lane | Rollup run | X3 | RGS | Blockers | Fix |
|------|------------|----|-----|----------|-----|
| headline | `headline_20260518_225908` | X3_REVIEW_JUDGE_SOFT_FAIL | REAL_LLM | judge_soft_fail, x3_review | Live judges all pass; no X2 regressions |
| executive_summary | `exec_summary_20260518_205434` | X3_ALLOW | REAL_LLM | (none) | Pinned — product ALLOW |
| unify_bullets | `unify_bullets_20260518_230943` | X3_ALLOW | REAL_LLM | (none) | Pinned — product ALLOW |
| ibm_narrative | `ibm_narrative_20260518_225555` | X3_ALLOW | REAL_LLM | (none) | Pinned — product ALLOW |
| ibm_bullets | `ibm_bullets_20260518_224815` | X3_REVIEW_JUDGE_SOFT_FAIL | REAL_LLM | judge_soft_fail, x3_review | Live judges all pass; metrics/ledger X2 |

Prior rollup pins used OFFLINE_CONTRACT_STUB / MOCK_PLUMBING runs (newer mtime). Root cause: `build_coherent_aggregation_rollup` picked latest proof-complete run without product ranking.

## W9 — Real-lane regeneration

- **Rollup pin-only** (existing REAL_LLM + X3_ALLOW): executive_summary, unify_bullets, ibm_narrative (+ unify_narrative, competencies unchanged).
- **Regeneration attempted** (REAL_LLM, no mock judges):
  - `headline_20260518_233123` → X3_BLOCK (X2 claim-ledger / input-usage failures; judges 2/3 fail)
  - `ibm_bullets_20260518_233233` → X3_BLOCK (X2 metrics/ledger failures; judges 2/3 soft-fail)
- **Not selected for rollup** — pinned runs remain best scored.

Artifact: [regenerated_lane_matrix.json](../../artifacts/apps_rg/runtime_proofs/final_resume_assembly/regenerated_lane_matrix.json)

Rollup rebuilt with `--product-proof` scoring: [build_coherent_aggregation_rollup.py](../../tools/apps_rg/build_coherent_aggregation_rollup.py).

## W10 — Product package proof

| Check | Result |
|-------|--------|
| Structural X2 | PASS (`gates_all_pass=true`) |
| Cross-section structural | PASS |
| Cross-section product | **FAIL** (WARN: duplicates, wording, x3_review_present) |
| Review lane policy | ALLOW×5, REVIEW×2 (headline, ibm_bullets), MOCK×0 |
| Package X3 | `X3_REVIEW_SECTION_JUDGE_STATUS`, `deterministic_blocked=false` |
| `product_allow_claimed` | **false** |

## Commands (exit 0)

```text
python -m compileall apps_rg -q
python tools/apps_rg/audit_blocked_lanes.py --write
python -m apps_rg --section headline --provider qwen_vllm --x1d-judges gemini_pro,openai_chatgpt,anthropic_claude --allow-non-allow-exit-zero
python -m apps_rg --section ibm_bullets --provider qwen_vllm --x1d-judges gemini_pro,openai_chatgpt,anthropic_claude --allow-non-allow-exit-zero
python tools/apps_rg/build_coherent_aggregation_rollup.py --write --product-proof
python -m apps_rg.runtime.assembly.final_resume_assembler
python -m apps_rg.runtime.package.resume_package_x3
pytest (unit + contract scoped) — 26 passed
git diff HEAD -- agentic_core — empty
```

## Path to PASS

1. Regenerate **headline** and **ibm_bullets** until `X3_ALLOW` + all model-backed judges pass + X2 pass (no gate weakening).
2. Rebuild rollup `--product-proof` and re-run assembler + package.
3. Resolve cross-section WARN (overlap / review-present) or accept documented product policy exception (WARN ≠ PASS for product).

## Non-claims

- JD/briefing are targeting-only.
- Regeneration used REAL_LLM; no OFFLINE_CONTRACT_STUB in rollup pin.
- No mocked-judge proof in rollup selection.
- Product ALLOW not claimed while REVIEW lanes or cross-section WARN remain.
