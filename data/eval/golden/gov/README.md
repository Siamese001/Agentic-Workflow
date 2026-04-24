# Governance Judge Golden Dataset

Per `config/judges/rubrics.yaml` governance rubrics GOV-001..003. Acceptance rules
match the parent `../README.md` (≥100 items/rubric, ≥2 raters, Cohen's κ ≥ 0.6).

## Rubrics covered
- `gov_policy_compliance/` — GOV-001 Policy Compliance
- `gov_authorization_hygiene/` — GOV-002 Authorization Hygiene
- `gov_audit_completeness/` — GOV-003 Audit Completeness

## Annotation queue
Items land here via `system_learning/adapters/golden_curation_adapter.py` (W2.3)
or `tools/eval/dueling_llm_synth.py` (W2.4). Human raters annotate using the
schema in `../README.md`; uncalibrated items MUST have `gold_score: null` and
`gold_outcome: "pending"`.

## Status (2026-04-23)
Scaffolding only. Zero calibrated items. Judges for these rubrics MUST NOT be
promoted to regression suite until ≥100 items each reach `gold_outcome: "scored"`
and inter-rater κ ≥ 0.6.
