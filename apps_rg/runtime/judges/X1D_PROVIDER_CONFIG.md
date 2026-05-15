# X1D executive-summary judge provider configuration

Scope: `apps_rg/runtime/judges/executive_summary_x1d.py` only. Does not change L2 generation, X2, or X3.

## Model resolution precedence

| Provider | API key env | Preferred model env | Fallback model env | Code default (no env) |
|----------|-------------|---------------------|--------------------|------------------------|
| Gemini | `GEMINI_API_KEY` | `APPS_RG_GEMINI_JUDGE_MODEL` | `GEMINI_MODEL` | `gemini-2.0-flash` |
| OpenAI | `OPENAI_API_KEY` | `OPENAI_MODEL` | — | `gpt-4o` |
| Anthropic | `ANTHROPIC_API_KEY` | `APPS_RG_ANTHROPIC_JUDGE_MODEL` | `ANTHROPIC_MODEL` | `claude-3-5-sonnet-20241022` |

Artifacts record `resolved_model` and `resolved_model_source` on each judge `provider_request` JSON under `artifacts/apps_rg/runtime_proofs/executive_summary/`.

## Anthropic fallback (opt-in)

Set `APPS_RG_ANTHROPIC_ALLOW_MODEL_FALLBACK=true` only if you accept a second API call after `404 not_found` on the requested model. When used, request/response artifacts include `original_model`, `fallback_model`, and `fallback_reason`. No fallback occurs unless this flag is exactly `true`.

## Common block states (honest, not coerced)

| Symptom | Typical `provider_status` | Fix |
|---------|---------------------------|-----|
| Gemini 429 / quota | `BLOCKED_PROVIDER_UNAVAILABLE` | Set `APPS_RG_GEMINI_JUDGE_MODEL` to a model with quota, or wait for reset |
| Anthropic unknown model id | `BLOCKED_MODEL_NOT_FOUND` | Set `APPS_RG_ANTHROPIC_JUDGE_MODEL` to an id your API key supports |
| OpenAI score 9.2 / 8.0 without `score_scale` | `BLOCKED_SCHEMA_VALIDATION_ERROR` | Model must return `score_scale` of `0_to_1` or `0_to_5` with in-range score/threshold |

## Quick unblock (local `.env`)

```bash
APPS_RG_GEMINI_JUDGE_MODEL=gemini-2.0-flash
APPS_RG_ANTHROPIC_JUDGE_MODEL=claude-3-5-sonnet-20241022
```

Keep generic `GEMINI_MODEL` / `ANTHROPIC_MODEL` for other apps; X1D judges prefer the `APPS_RG_*` vars when set.
