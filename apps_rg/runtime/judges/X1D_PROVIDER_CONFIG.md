# X1D LLM judge provider configuration (Gemini / OpenAI / Anthropic)

Implementations live in `apps_rg/runtime/judges/executive_summary_x1d.py` and are imported by RG X1D judges for **executive_summary, headline, competencies, unify bullets/narrative, IBM bullets/narrative** — not executive-summary-only. Scope is still **apps_rg** (no spine change); judges do **not** change L2 generation, X2 hard gates, or X3 aggregation elsewhere.

## Model resolution precedence

SSOT: `section_judge_profile.resolve_section_proof_judge_model` (tier matrix in `section_judge_policy.py`).

| Provider | API key env | ENHANCED judge env | STANDARD/BULLET judge env | Profile default (no env) |
|----------|-------------|--------------------|---------------------------|--------------------------|
| Gemini | `GOOGLE_API_KEY` | `APPS_RG_GOOGLE_JUDGE_MODEL_ENHANCED` | `APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD` | enhanced: `gemini-3.1-pro-preview`; standard: `gemini-2.5-pro` |
| OpenAI | `OPENAI_API_KEY` | `APPS_RG_OPENAI_JUDGE_MODEL_ENHANCED` (+ `APPS_RG_OPENAI_JUDGE_REASONING_EFFORT`) | `APPS_RG_OPENAI_JUDGE_MODEL_STANDARD` | enhanced: `gpt-5.5` (chat); standard: `gpt-5.5` — **not** `gpt-5.5-pro` (completions-only) |
| Anthropic | `ANTHROPIC_API_KEY` | `APPS_RG_ANTHROPIC_JUDGE_MODEL_ENHANCED` | `APPS_RG_ANTHROPIC_JUDGE_MODEL_STANDARD` | enhanced: `claude-opus-4-6`; standard: `claude-sonnet-4-6` |

Optional global override per provider: `APPS_RG_*_JUDGE_MODEL` (wins both tiers if set). General chat env vars (`OPENAI_MODEL`, `ANTHROPIC_MODEL`, `GOOGLE_AI_MODEL`) are **not** used for proof judges.

Provider request/response/raw-parse artifacts are written next to the **current run folder** (for example `.../executive_summary/mock/exec_summary_<ts>/` or the equivalent for other RG lanes). Each `provider_request` JSON records `resolved_model` and `resolved_model_source`. If no run directory is passed, dumps fall back under `artifacts/apps_rg/runtime_proofs/executive_summary/`.

## Anthropic fallback (opt-in)

Set `APPS_RG_ANTHROPIC_ALLOW_MODEL_FALLBACK=true` only if you accept a second API call after `404 not_found` on the requested model. When used, request/response artifacts include `original_model`, `fallback_model`, and `fallback_reason`. No fallback occurs unless this flag is exactly `true`.

## Common block states (honest, not coerced)

| Symptom | Typical `provider_status` | Fix |
|---------|---------------------------|-----|
| Gemini 429 / quota | `BLOCKED_PROVIDER_UNAVAILABLE` | Set `APPS_RG_GOOGLE_JUDGE_MODEL` (alias `APPS_RG_GEMINI_JUDGE_MODEL`) to a model with quota |
| Anthropic unknown model id | `BLOCKED_MODEL_NOT_FOUND` | Set `APPS_RG_ANTHROPIC_JUDGE_MODEL` to an id your API key supports |
| OpenAI score 9.2 / 8.0 without `score_scale` | `BLOCKED_SCHEMA_VALIDATION_ERROR` | Model must return `score_scale` of `0_to_1` or `0_to_5` with in-range score/threshold |
| OpenAI 400 `temperature` unsupported | `BLOCKED_PROVIDER_UNAVAILABLE` | gpt-5.x chat judges omit `temperature` (API default only) |
| OpenAI 400 `reasoning` unknown parameter | `BLOCKED_PROVIDER_UNAVAILABLE` | Do not send `reasoning.effort` except on o3/o4 families |

## Quick unblock (local `.env`)

```bash
APPS_RG_GOOGLE_JUDGE_MODEL_ENHANCED=gemini-3.1-pro-preview
APPS_RG_GOOGLE_JUDGE_MODEL_STANDARD=gemini-2.5-pro
APPS_RG_OPENAI_JUDGE_MODEL_ENHANCED=gpt-5.5
APPS_RG_OPENAI_JUDGE_MODEL_STANDARD=gpt-5.5
APPS_RG_ANTHROPIC_JUDGE_MODEL_ENHANCED=claude-opus-4-6
APPS_RG_ANTHROPIC_JUDGE_MODEL_STANDARD=claude-sonnet-4-6
```

Keep generic `GOOGLE_AI_*` / `OPENAI_MODEL` / `ANTHROPIC_MODEL` for non-judge paths only.
