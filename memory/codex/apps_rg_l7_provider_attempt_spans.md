# apps_rg L7 Provider Attempt Spans

Protected memory type: ProceduralPattern

- name: `ProceduralPattern:AppsRgL7ProviderAttemptSpans`
- entityType: `ProceduralPattern`

Observations:

- apps_rg provider RCAs should read `provider_attempt_spans` instead of reconstructing timing from scattered provider response, transport progress, and fallback receipt fields.
- Direct provider calls emit `provider_attempt_spans` and `provider_attempt_timing_summary` inside `provider_response.json` through `apps_rg/runtime/providers/external_provider.py`.
- Claude availability fallback emits requested+fallback spans inside `apps_rg_availability_fallback.provider_attempt_spans` and mirrors the combined span list onto `provider_response.provider_attempt_spans`.
- Section L7 binding manifests read `provider_response.json` and expose `provider_attempt_spans`, `provider_attempt_span_refs`, `provider_attempt_span_source`, and `provider_attempt_timing_summary`.
- Do not infer fallback timing from `model_attempts` alone; that list is legacy compatibility, while `provider_attempt_spans` is the normalized RCA surface.
- Plan: `plans/apps-rg-l7-provider-attempt-spans-a4f9c2.md`; validated: 2026-06-28.
