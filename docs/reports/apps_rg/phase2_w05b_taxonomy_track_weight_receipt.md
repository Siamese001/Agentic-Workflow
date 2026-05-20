# W0.5b — Senior-role taxonomy split and track-weight profile design

| Field | Value |
|-------|-------|
| **STATUS** | PASS |
| **PLAN_ID** | `phase2-gtm-presales-remaining-f7a2c9` |
| **WAVE** | W0.5b |
| **AUDIT_ID** | `senior_role_graph_gap_analysis_20260520` |
| **SCOPE_MATCH** | true — taxonomy YAML + design-only track weights only |
| **PROOF_CLASSIFICATION** | taxonomy_config_and_design_receipt_only |

## Role families added (7)

Added to [master_role_family_taxonomy.yaml](apps_rg/config/domain_contract/master_role_family_taxonomy.yaml); count **13 → 20**.

| ID | Gap / role anchor |
|----|-------------------|
| `INSURANCE_CARRIER_TRANSFORMATION` | GAP-001 — AIG |
| `INSURER_IT_AI_ENABLEMENT` | GAP-004 — Lincoln |
| `INSURANCE_BROKERAGE_IT_INNOVATION` | GAP-001 — Brown & Brown |
| `BANKING_PLATFORM_AI` | GAP-008 — Citi |
| `REGULATED_AI_GOVERNANCE` | GAP-010, GAP-014 |
| `PARTNER_APPLIED_AI_ARCHITECTURE` | GAP-009 — Anthropic |
| `HYPERSCALER_MARKETPLACE_GTM` | GAP-003, GAP-009 |

JD/briefing keywords are **targeting signals only** — not proof of domain ownership.

## Where families lived before

All seven IDs were **absent** from the taxonomy SSOT. Senior roles were scored through overlapping legacy families:

- Carrier / brokerage conflation → actuarial + `AI_GOVERNANCE_RISK` / `PARTNERSHIPS_GTM`
- Insurer IT → `ENGINEERING_PLATFORM`
- Banking platform → `ENGINEERING_PLATFORM` + `AI_GOVERNANCE_RISK`
- Partner / hyperscaler → `PARTNERSHIPS_GTM` only

## Pillar mapping (existing vs proposed)

**Existing** pillars are in [master_skills_arsenal_ledger.json](apps_rg/fact_inventory/master_skills_arsenal_ledger.json) (21 pillars today). **Proposed** pillars are backlog-only until W8–W11-graph.

| Role family | Existing pillars (traversal today) | Proposed pillars (W8–W11) |
|-------------|-----------------------------------|---------------------------|
| `INSURANCE_CARRIER_TRANSFORMATION` | actuarial, embedded_options_insurance, agentic_ai, regulatory_governance | `pillar_insurance_carrier_transformation`, `pillar_underwriting_claims_ops_ai` |
| `INSURER_IT_AI_ENABLEMENT` | cloud_data_aws, agentic_ai, actuarial, executive | `pillar_insurer_it_strategy_ai_enablement`, `pillar_enterprise_portfolio_governance` |
| `INSURANCE_BROKERAGE_IT_INNOVATION` | gtm_presales, cloud_data_aws, executive | `pillar_insurance_brokerage_distribution`, `pillar_interoperability_integration_ecosystem` |
| `BANKING_PLATFORM_AI` | regulatory_governance, agentic_ai, cloud_data_aws, enterprise_risk | `pillar_banking_platform_responsible_ai` |
| `REGULATED_AI_GOVERNANCE` | regulatory_governance, enterprise_risk, risk_management | (split taxonomy; no new pillar required in backlog) |
| `PARTNER_APPLIED_AI_ARCHITECTURE` | partner_gtm, presales, technical_presales, cosell | `pillar_applied_ai_partner_architecture` |
| `HYPERSCALER_MARKETPLACE_GTM` | partner_gtm, gtm_presales, cloud_data_aws | `pillar_hyperscaler_marketplace_partner_gtm` |

Each new taxonomy row includes `proposed_pillar_ids` (documentation field; ignored by `infer_role_family_priorities`).

## Track-weight profiles

| Item | Result |
|------|--------|
| Design SSOT | [senior_role_track_weight_profiles_design.yaml](apps_rg/config/domain_contract/senior_role_track_weight_profiles_design.yaml) — `status: design_only_not_loaded_at_runtime` |
| Runtime live weights | **BLOCKED_BY_CODE_CHANGE_REQUIRED** |
| Code paths | `ROLE_FAMILY_TRACK_WEIGHTS`, `TAXONOMY_TO_PROJECTION_ROLE`, `infer_projection_role_family_key` in [track_weighted_graph_expansion.py](apps_rg/fact_inventory/track_weighted_graph_expansion.py) |
| JD inference without code | **Yes** — `infer_role_family_priorities` reads taxonomy YAML |
| Per-fixture override without code | **Yes** — `weight_override` / W13 fixtures |

**Smoke test:** JD *"insurance carrier agentic AI transformation underwriting claims operations"* → top taxonomy `INSURANCE_CARRIER_TRANSFORMATION`, but projection key `SVP_ENGINEERING_AI_PLATFORM` with **default** weights (0.10 / 0.25 / 0.65) because the new IDs are not in `TAXONOMY_TO_PROJECTION_ROLE`.

Reference pattern for config-driven composites: [composite_projection_profiles.yaml](apps_rg/config/domain_contract/composite_projection_profiles.yaml) (ledger-backed; separate from track weights).

## Files changed

- [master_role_family_taxonomy.yaml](apps_rg/config/domain_contract/master_role_family_taxonomy.yaml)
- [senior_role_track_weight_profiles_design.yaml](apps_rg/config/domain_contract/senior_role_track_weight_profiles_design.yaml)
- [phase2_w05b_taxonomy_track_weight_receipt.json](docs/reports/apps_rg/phase2_w05b_taxonomy_track_weight_receipt.json)
- [phase2_w05b_taxonomy_track_weight_receipt.md](docs/reports/apps_rg/phase2_w05b_taxonomy_track_weight_receipt.md)

## Commands run

| Command | Exit code |
|---------|-----------|
| `python -c` taxonomy load — 20 families, 7 additions, unique IDs | 0 |
| `pytest test_cro_projection_profile_hardening::test_taxonomy_has_no_standalone_cro_role_family` | 0 |
| `python` smoke — carrier/brokerage JD inference + projection fallback | 0 |

## Explicit non-claims

No new proof for: underwriting, claims, policy admin, billing, brokerage ownership, transaction banking, payments, liquidity, trade, investor/issuer services, fraud ops, Fed/regulator-facing work, marketplace co-sell, Databricks/Snowflake/GCP/Azure exclusivity, partner sales, airline ~$100M engagement, or technical estimation/sizing.

## Next recommended wave

**W8–W11-graph** — evidence-gated proposed pillars and bridge-edge families (backlog step 2), then **W12-graph** partner DRAFT activation. Track-weight **code** wiring should land with or before **W13** fixtures if offline traversal must use designed weights without `weight_override`.
