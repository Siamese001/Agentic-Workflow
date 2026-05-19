# Executive summary X1D judge blocker report (Wave 6)

**Reference run:** [exec_summary_20260519_103930](artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_103930)

**X3:** `X3_REVIEW_JUDGE_PROVIDER_BLOCKED` — quorum blocked because OpenAI judge could not call chat/completions.

## Judge roster

| Judge | Model | Status | Class |
|-------|-------|--------|-------|
| gemini_pro | gemini-3.1-pro-preview | MODEL_BACKED_FAIL (2.0/4.0) | Quality soft-fail |
| openai_chatgpt | gpt-5.5-pro | BLOCKED_PROVIDER_UNAVAILABLE | **Provider config** |
| anthropic_claude | claude-opus-4-6 | MODEL_BACKED_FAIL (2.4/4.0) | Quality soft-fail |

## OpenAI blocker (decisive for X3 code)

- **Configured:** `APPS_RG_OPENAI_JUDGE_MODEL_ENHANCED=gpt-5.5-pro`
- **API error:** HTTP 404 — not supported on `v1/chat/completions`
- **Fix:** Use `gpt-5.5` (or another chat-capable id) for enhanced OpenAI judges

## Gemini / Anthropic (not provider-blocked)

- Both returned valid JSON judge responses (`provider_available=true`).
- Failures are **quality/threshold** (scores below 0.8 normalized), not timeouts or 429.
- Root rubric mismatch: judge packet used **SRFS five-sentence arc** while graph-only lane is **non-SRFS** (X2 allows 2–3 sentences; SRFS gates skipped in `deterministic_gate_summary`).

## Proof eligibility accounting

- `run_manifest.proof_eligible=false` with `x3.pass=false`.
- Even after OpenAI fix, soft-fails block `X3_ALLOW` until all three judges model-back PASS.
- `--allow-non-allow-exit-zero` currently forces `plumbing_only` in `compute_lane_proof_bundle` (inspection hatch); Wave 7 separates exit waiver from proof classification.

## Wave 7 scope (no threshold weakening)

1. Env + resolver: chat-capable OpenAI judge model
2. Graph-only judge rubric aligned with non-SRFS X2 band
3. Inspection CLI hatch must not zero proof when product gates pass
