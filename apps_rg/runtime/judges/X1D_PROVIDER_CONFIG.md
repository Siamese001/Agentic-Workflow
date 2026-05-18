# X1D LLM judge provider configuration (Gemini / OpenAI / Anthropic)

Implementations live in `apps_rg/runtime/judges/executive_summary_x1d.py` and are imported by RG X1D judges for **executive_summary, headline, competencies, unify bullets/narrative, IBM bullets/narrative** — not executive-summary-only. Scope is still **apps_rg** (no spine change); judges do **not** change L2 generation, X2 hard gates, or X3 aggregation elsewhere.

## Model resolution precedence

| Provider | API key env | Preferred model env | Fallback model env | Code default (no env) |
|----------|-------------|---------------------|--------------------|------------------------|
| Gemini | `GOOGLE_API_KEY` (deprecated alias: `GEMINI_API_KEY`) | `APPS_RG_GOOGLE_JUDGE_MODEL` | `GOOGLE_AI_MODEL` (aliases: `GEMINI_MODEL`) | `gemini-2.0-flash` |
| OpenAI | `OPENAI_API_KEY` | `OPENAI_MODEL` | — | `gpt-4o` |
| Anthropic | `ANTHROPIC_API_KEY` | `APPS_RG_ANTHROPIC_JUDGE_MODEL` | `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` |

Provider request/response/raw-parse artifacts are written next to the **current run folder** (for example `.../executive_summary/mock/exec_summary_<ts>/` or the equivalent for other RG lanes). Each `provider_request` JSON records `resolved_model` and `resolved_model_source`. If no run directory is passed, dumps fall back under `artifacts/apps_rg/runtime_proofs/executive_summary/`.

## Anthropic fallback (opt-in)

Set `APPS_RG_ANTHROPIC_ALLOW_MODEL_FALLBACK=true` only if you accept a second API call after `404 not_found` on the requested model. When used, request/response artifacts include `original_model`, `fallback_model`, and `fallback_reason`. No fallback occurs unless this flag is exactly `true`.

## Common block states (honest, not coerced)

| Symptom | Typical `provider_status` | Fix |
|---------|---------------------------|-----|
| Gemini 429 / quota | `BLOCKED_PROVIDER_UNAVAILABLE` | Set `APPS_RG_GOOGLE_JUDGE_MODEL` (alias `APPS_RG_GEMINI_JUDGE_MODEL`) to a model with quota |
| Anthropic unknown model id | `BLOCKED_MODEL_NOT_FOUND` | Set `APPS_RG_ANTHROPIC_JUDGE_MODEL` to an id your API key supports |
| OpenAI score 9.2 / 8.0 without `score_scale` | `BLOCKED_SCHEMA_VALIDATION_ERROR` | Model must return `score_scale` of `0_to_1` or `0_to_5` with in-range score/threshold |

## Quick unblock (local `.env`)

```bash
APPS_RG_GOOGLE_JUDGE_MODEL=gemini-2.0-flash
APPS_RG_ANTHROPIC_JUDGE_MODEL=claude-3-5-sonnet-20241022
```

Keep generic `GOOGLE_AI_MODEL` / `GEMINI_MODEL` / `ANTHROPIC_MODEL` when you want different defaults elsewhere; RG X1D judges prefer `APPS_RG_GOOGLE_JUDGE_MODEL` (+ legacy `APPS_RG_GEMINI_JUDGE_MODEL`) when set.
