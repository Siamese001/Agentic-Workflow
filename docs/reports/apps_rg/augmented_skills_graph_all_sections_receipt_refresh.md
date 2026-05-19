# All-section receipt refresh (Wave 2)

**Status: PASS** — mock CLI runs for all seven canonical sections produced `section_input_usage_ledger.json` with dual-source fields.

## Proof mode

```text
python -m apps_rg --section <section> --provider mock --mock-judges --allow-test-mock-judges
```

Not live LLM product proof (`runtime_generation_status` is mock/stub). Receipt structure proof only.

## Per-section receipt checks

| Section | claim_evidence_source_type | skills_authority_source_type | skills_authority_status |
|---------|---------------------------|------------------------------|-------------------------|
| headline | candidate_fact_ledger | augmented_skills_graph | PASS |
| executive_summary | candidate_fact_ledger | augmented_skills_graph | PASS |
| competencies | candidate_fact_ledger | augmented_skills_graph | PASS |
| unify_bullets | candidate_fact_ledger | augmented_skills_graph | PASS |
| unify_narrative | candidate_fact_ledger | augmented_skills_graph | PASS |
| ibm_bullets | candidate_fact_ledger | augmented_skills_graph | PASS |
| ibm_narrative | selected_role_fact_set (+ candidate substrate) | augmented_skills_graph | PASS |

All ledgers include `required_input_usage.augmented_skills_graph` with authority `SKILLS_COMPETENCY_AUTHORITY`. `legacy_broad_skills_ledger_skills_authority` is false.

## unify_bullets

Resolver now applies `unify` company-hint allocation when the SRFS slice is empty, so unify_bullets uses candidate_fact_ledger instead of falling through to base_resume_fallback when the ledger is loadable.

Machine-readable: `augmented_skills_graph_all_sections_receipt_refresh.json`.
