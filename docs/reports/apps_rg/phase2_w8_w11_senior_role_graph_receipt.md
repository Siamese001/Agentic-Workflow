# W8–W11 senior-role graph receipt

| Field | Value |
|-------|-------|
| **STATUS** | PASS |
| **PLAN_ID** | `phase2-gtm-presales-remaining-f7a2c9` |
| **WAVE** | W8–W11-graph |
| **SCOPE_MATCH** | true |
| **PROOF_CLASSIFICATION** | `graph_materialization_receipt_only` |

## Counts

| Metric | Before | After |
|--------|--------|-------|
| Pillars | 21 | 27 |
| Skill rows | 148 | 158 |
| Graph edges | 1281 | 1370 |
| Phase bridge edges | 0 | 10 |

## Pillars added (6)

| Pillar | Wave | Status |
|--------|------|--------|
| [pillar_insurance_carrier_transformation](apps_rg/fact_inventory/master_skills_arsenal_ledger.json) | W8 | Evidence-backed (InsurTech employment) |
| [pillar_underwriting_claims_ops_ai](apps_rg/fact_inventory/master_skills_arsenal_ledger.json) | W8 | Internal traversal only — no external section eligibility |
| [pillar_insurer_it_strategy_ai_enablement](apps_rg/fact_inventory/master_skills_arsenal_ledger.json) | W9 | Evidence-backed |
| [pillar_enterprise_portfolio_governance](apps_rg/fact_inventory/master_skills_arsenal_ledger.json) | W9 | Evidence-backed (governance facts) |
| [pillar_banking_platform_responsible_ai](apps_rg/fact_inventory/master_skills_arsenal_ledger.json) | W10 | Basel/CCAR + regulated FI fluency — not transaction banking |
| [pillar_interoperability_integration_ecosystem](apps_rg/fact_inventory/master_skills_arsenal_ledger.json) | W11 | Microservices/integration — not brokerage |

## Pillars deferred (1)

- **`pillar_insurance_brokerage_distribution`** — no brokerage/distribution strings in Phase I archive or candidate ledger; Brown & Brown targeting remains taxonomy-only until evidence (W11-deferred).

W12 pillars (`pillar_hyperscaler_marketplace_partner_gtm`, `pillar_applied_ai_partner_architecture`) intentionally **not** added.

## Skills added (10)

All grounded in base resume, Phase I archive, or candidate facts. One **INTERNAL_ONLY** row blocks underwriting/claims externalization.

| Skill | Pillar | Support | External gate |
|-------|--------|---------|---------------|
| `skill_sr_insurtech_legacy_cloud_modernization` | carrier | DIRECT archive | eligible |
| `skill_sr_insurtech_regulated_insurer_controls` | carrier | DIRECT archive | eligible |
| `skill_sr_insurance_systems_resilience_internal` | uw/claims internal | INTERNAL_ONLY | **blocked** |
| `skill_sr_insurtech_cto_it_enablement` | insurer IT | DIRECT + exp fact | eligible |
| `skill_sr_cloud_data_platform_engineering` | insurer IT | DERIVED + fact | eligible |
| `skill_sr_enterprise_portfolio_data_governance` | portfolio gov | DERIVED MEDIUM | eligible* |
| `skill_sr_basel_ccar_lineage_regulatory` | banking AI | DERIVED HIGH | eligible* |
| `skill_sr_banking_ai_governance_controls` | banking AI | DERIVED MEDIUM | eligible* |
| `skill_sr_regulated_financial_institutions_fluency` | banking AI | DIRECT archive | eligible |
| `skill_sr_microservices_integration_platform` | interop | DERIVED | eligible |

\*Candidate MEDIUM/HIGH facts still subject to exec_summary SRFS policy and human confirm — graph does not auto-promote MEDIUM.

## Bridge edges (10, directional)

| Family | Source → Target | Policy |
|--------|-----------------|--------|
| `actuarial_to_insurer_ai_strategy` | actuarial → insurer IT | traversal |
| `actuarial_to_agentic_transformation` | actuarial → carrier + agentic | traversal |
| `insurance_to_underwriting_claims_ops` | carrier → uw internal pillar | **internal only** |
| `insurtech_to_insurer_it_strategy` | carrier → insurer IT | traversal |
| `basel_ccar_to_ai_auditability` | regulatory → banking AI | traversal |
| `regulatory_governance_to_responsible_ai` | regulatory → banking AI | traversal |
| `data_lineage_to_ai_traceability` | regulatory → agentic | traversal |
| `domain_expertise_to_section_eligibility` | carrier → exec summary; banking → competencies | section metadata |

## Analysis summary (pre-edit)

1. **Ledger before:** 21 pillars, 148 skills, 0 phase-bridge edges (gap analysis audit).
2. **Evidence sources:** `exp_insurtech_001` / bullets; `fact_governance_001/003/004`; `fact_engineering_platform_*`; Phase I Basel/CCAR archive lines.
3. **Safe ACTIVE vs DRAFT:** Pillar nodes are structural; skills remain mostly **DRAFT/ACTIVE** per materializer — only DIRECT archive + employment spine → **ACTIVE_CONFIRMED** (3 senior skills). Underwriting-adjacent bullet → **INTERNAL_ONLY** skill.
4. **Brokerage:** deferred — no source-backed nodes.
5. **Sections:** `pillar_underwriting_claims_ops_ai` has all `section_fit: false`; exec_summary policy unchanged.

## Validation

| Check | Result |
|-------|--------|
| `validate_arsenal_ledger_shape` | PASS |
| `broad_skills_ledger` non-authority | PASS |
| Taxonomy 20 families load | PASS |
| Pytest arsenal + w4a + career track (23) | PASS |
| `test_agentic_core_diff_empty` | FAIL (pre-existing `guardian_report.json` drift) |

## Commands

```text
python apps_rg/fact_inventory/apply_phase2_senior_role_graph_w8_w11.py  → 0
python -c ledger validation  → 0
pytest test_master_skills_arsenal_ledger (subset) + test_arsenal_graph_w4a + test_career_track_materialization_p1  → 0
```

## Next recommended wave

**W12-graph** — partner/hyperscaler DRAFT activation. Then **W13** fixtures + offline traversal. Track-weight Python wiring remains optional (W0.5b blocked).
