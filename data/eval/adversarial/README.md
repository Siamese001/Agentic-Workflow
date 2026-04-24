# Adversarial / Red-Team Dataset

Populated by `tools/eval/adversarial_generator.py` (W2.2). Items target the
`sec_prompt_injection_resistance` and `sec_secret_leakage` rubrics defined
in `config/judges/rubrics.yaml`.

## Layout
Each subdirectory groups items by mutation family:
- `prompt_injection/`
- `typoglycemia/`
- `unicode_homoglyph/`
- `role_reversal/`
- `secret_bait/`

## Item schema
Adversarial items extend the golden schema with `source_item_id`, `mutation`,
and `gold_outcome: "pending"` until a human rater annotates.

## Promotion rule
Adversarial items are NEVER auto-promoted to the regression suite. Each item
MUST be annotated by ≥2 raters and pass κ ≥ 0.6 before it counts toward the
rubric's calibrated population.
