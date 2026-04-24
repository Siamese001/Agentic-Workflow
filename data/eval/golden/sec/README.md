# Security Judge Golden Dataset

Per `config/judges/rubrics.yaml` security rubrics SEC-001..002. Acceptance rules
match the parent `../README.md` (≥100 items/rubric, ≥2 raters, Cohen's κ ≥ 0.6).

## Rubrics covered
- `sec_prompt_injection_resistance/` — SEC-001 Prompt-Injection Resistance
- `sec_secret_leakage/` — SEC-002 Secret / PII Leakage

## Annotation queue
Items land here via `system_learning/adapters/golden_curation_adapter.py` (W2.3)
or `tools/eval/adversarial_generator.py` (W2.2). Human raters annotate using the
schema in `../README.md`; uncalibrated items MUST have `gold_score: null` and
`gold_outcome: "pending"`.

## Status (2026-04-23)
Scaffolding only. Zero calibrated items. Judges for these rubrics MUST NOT be
promoted to regression suite until ≥100 items each reach `gold_outcome: "scored"`
and inter-rater κ ≥ 0.6.
