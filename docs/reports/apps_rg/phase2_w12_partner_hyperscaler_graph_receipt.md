# W12 partner / hyperscaler graph receipt

| Field | Value |
|-------|-------|
| **STATUS** | PASS |
| **PLAN_ID** | `phase2-gtm-presales-remaining-f7a2c9` |
| **WAVE** | W12-graph |
| **SCOPE_MATCH** | true |
| **PROOF_CLASSIFICATION** | `graph_materialization_receipt_only` |

## Counts

| Metric | Before | After |
|--------|--------|-------|
| Pillars | 27 | 29 |
| Skill rows | 158 | 162 |
| Graph edges | 1370 | 1406 |
| Phase bridge edges | 10 | 16 |

## Pre-edit evidence classification

| Topic | Class | Decision |
|-------|-------|----------|
| AWS partner / IBM–AWS alliance | DIRECT_EVIDENCE | DRAFT (existing `skill_partner_*`) |
| Co-sell SI/ISV | DIRECT_EVIDENCE | DRAFT (`fact_partnerships_gtm_003` MEDIUM) |
| Databricks Lakehouse | DIRECT_EVIDENCE | DRAFT (`skill_sr_w12_databricks_*`) |
| Hyperscaler alliance co-sell | DIRECT_EVIDENCE | DRAFT (`bul_ibm_005`) |
| Reference architecture / Solution Accelerator | DIRECT_EVIDENCE | DRAFT (`skill_sr_w12_industry_reference_*`) |
| Joint AI solutions | MEDIUM_NEEDS_HUMAN_CONFIRMATION | DRAFT (`fact_partnerships_gtm_001`) |
| Partner engineering | ABSENT_EVIDENCE | **DO_NOT_PROMOTE** |
| Product feedback loops | ABSENT_EVIDENCE | **DO_NOT_PROMOTE** |
| Snowflake | ABSENT_EVIDENCE | **DO_NOT_PROMOTE** (no skill) |
| Cloud marketplace listing | ABSENT_EVIDENCE | **DO_NOT_PROMOTE** (pillar forbidden phrases) |
| GSI enablement | ABSENT_EVIDENCE | **DO_NOT_PROMOTE** |

## Pillars added (2)

- [pillar_hyperscaler_marketplace_partner_gtm](apps_rg/fact_inventory/master_skills_arsenal_ledger.json) — alliance/co-sell/AWS/Databricks accreditation; **not** cloud marketplace listing
- [pillar_applied_ai_partner_architecture](apps_rg/fact_inventory/master_skills_arsenal_ledger.json) — reference architectures, joint solutions, solution accelerators

## Skills added (4)

| Skill | Evidence |
|-------|----------|
| `skill_sr_w12_databricks_lakehouse_fundamentals` | `cert_databricks_lakehouse_001`, engineering fact |
| `skill_sr_w12_hyperscaler_alliance_co_sell` | `bul_ibm_005` |
| `skill_sr_w12_joint_ai_solution_development` | `fact_partnerships_gtm_001` (MEDIUM) |
| `skill_sr_w12_industry_reference_architecture` | Industry Solutions archive, `fact_solutions_002` |

Existing 16 `skill_partner_*` rows retained; pending-source rows stay **external blocked**.

## Bridge edges (6 new families)

| Family | Route | Notes |
|--------|-------|-------|
| `hyperscaler_to_applied_ai_architecture` | hyperscaler → applied AI | Evidence: alliance + joint solution facts |
| `marketplace_to_partner_gtm` | hyperscaler → partner GTM | **Internal traversal** — co-sell only, not marketplace listing |
| `partner_engineering_to_reference_architecture` | cosell → applied AI | Uses presales/solution arch; **not** `skill_partner_partner_engineering` |
| `partner_ecosystem_to_ai_adoption` | partner GTM → agentic | Traversal only |
| `domain_expertise_to_section_eligibility` | hyperscaler → exec summary; applied AI → competencies | Section metadata |

## W8–W11 integrity

Required W8–W11 pillars and `skill_sr_*` (non-w12) rows verified intact after apply.

## Validation

| Check | Result |
|-------|--------|
| `validate_arsenal_ledger_shape` | PASS |
| `broad_skills_ledger` non-authority | PASS |
| `skill_partner_partner_engineering` external | **blocked** |
| `skill_partner_product_feedback_loops` external | **blocked** |
| Pytest graph subset (23) | PASS |

## Commands

```text
python apps_rg/fact_inventory/apply_phase2_senior_role_graph_w12.py  → 0
python -c ledger validation  → 0
pytest test_master_skills_arsenal_ledger + test_arsenal_graph_w4a + test_career_track_materialization_p1  → 0
```

## Next recommended wave

**W13** — senior-role fixtures and offline traversal receipts.
