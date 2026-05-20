# Phase 2 W13 — Senior-role archetype fixtures

**Status:** PASS (fixture/manifest only — not runtime release proof)  
**Plan:** `phase2-gtm-presales-remaining-f7a2c9`  
**Manifest SSOT:** [senior_role_fixture_manifest.json](docs/reports/apps_rg/fixtures/senior_roles/senior_role_fixture_manifest.json)

## Counts

| Metric | Value |
|--------|------:|
| Archetype fixtures | **7** |
| Regression examples | **7** |
| Graph nodes added (W13) | **0** |
| `BLOCKED_BY_GRAPH_GAP` | **false** |

## ARCHETYPE_FIXTURES_CREATED

1. `aig_carrier_agentic`
2. `lincoln_insurer_it_ai`
3. `citi_banking_platform_ai`
4. `brown_brokerage_it`
5. `anthropic_partner_applied_ai`
6. `gtm_presales_baseline`
7. **`ai_data_platform_professional_services`** (new)

## REGRESSION_EXAMPLES_MAPPED

| # | Archetype | Regression label |
|---|-----------|------------------|
| 1 | `aig_carrier_agentic` | AIG-style insurance carrier agentic transformation |
| 2 | `lincoln_insurer_it_ai` | Lincoln-style insurer IT strategy / AI enablement |
| 3 | `citi_banking_platform_ai` | Citi-style banking platform responsible AI |
| 4 | `brown_brokerage_it` | Brown & Brown-style insurance brokerage IT innovation |
| 5 | `anthropic_partner_applied_ai` | Anthropic-style partner applied AI architecture |
| 6 | `gtm_presales_baseline` | GTM/pre-sales technical accelerators baseline |
| 7 | `ai_data_platform_professional_services` | **EDB-style VP Global Professional Services (AI/data platform)** |

## Fixture 7 — AI/data platform professional services

**Purpose:** Generalized post-sales professional services leadership for AI/enterprise data platforms — not pure GTM/pre-sales, not pure customer success.

**Files:**

- [ai_data_platform_professional_services_jd.txt](docs/reports/apps_rg/fixtures/senior_roles/ai_data_platform_professional_services_jd.txt)
- [ai_data_platform_professional_services_brief.txt](docs/reports/apps_rg/fixtures/senior_roles/ai_data_platform_professional_services_brief.txt)
- [ai_data_platform_professional_services_regression_notes.txt](docs/reports/apps_rg/fixtures/senior_roles/ai_data_platform_professional_services_regression_notes.txt)

**Expected pillars (existing graph):** agentic platforms, cloud/data AWS, executive leadership, enterprise portfolio governance, revenue commercialization/operations, GTM presales motion, technical presales accelerators, hyperscaler partner GTM, applied AI partner architecture.

**Proposed-but-not-added (evidence gate):** `pillar_ai_data_platform_professional_services`; skill families for services P&L / CS-led growth — omitted because W13 manifest-only scope does not require new graph nodes.

## FORBIDDEN_CLAIMS_BLOCKED_BY_ARCHETYPE (fixture 7)

- Formal **VP Global Professional Services** title ownership without employment fact
- **Full services P&L** ownership
- **Utilization** / **margin** ownership as services executive
- **Customer success function** ownership
- **Product roadmap** ownership
- **Product feedback loops** external (`skill_partner_product_feedback_loops` DO_NOT_PROMOTE)
- Pre-sales solutioning relabeled as post-sales services P&L without evidence

**Allowed with guards:** partial alliance P&L via `skill_partner_pnl_oversight`; Unify delivery/commercialization HIGH paths; `skill_p2_gtm_presales_delivery_handoff` as pursuit→implementation boundary only.

## Distinction manifest (fixture 7)

| Motion | Manifest handling |
|--------|-------------------|
| Pre-sales solutioning | P2 GTM skills — pursuit phase |
| Post-sales implementation | Unify accelerator / go-live evidence |
| Customer success | Excluded skills; services/value-realization language |
| Professional services P&L | Forbidden ownership claim |
| Partner services delivery | W12 partner pillars; not partner engineering external |
| Product feedback loops | Excluded unless human-confirmed |

## W14 priority sections (fixture 7)

`unify_bullets`, `unify_narrative`, `competencies`, `executive_summary`

## Scope exclusions (honored)

- No `agentic_core` edits
- No prompt or runtime generation patches
- No broad runtime proof run
