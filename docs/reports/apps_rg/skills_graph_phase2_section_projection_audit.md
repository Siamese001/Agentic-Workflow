# Phase 2 GTM / Technical Pre-Sales — Section Projection Audit

**Generated:** 2026-05-19  
**Status:** PASS (read-only audit; no blocking runtime defects)  
**SSOT:** [skills_graph_phase2_gtm_presales_closeout.json](skills_graph_phase2_gtm_presales_closeout.json), [master_skills_arsenal_ledger.json](../../apps_rg/fact_inventory/master_skills_arsenal_ledger.json), [proof_pool_resolver.py](../../apps_rg/runtime/proof_pool_resolver.py)

## Pillars

| Pillar | Track | Pillar `section_fit` (thematic) |
|--------|-------|----------------------------------|
| `pillar_gtm_presales_motion` | `TRACK_DATA_TECH_CLOUD_ML` | exec_summary, competencies, unify_*, ibm_* (not headline) |
| `pillar_technical_presales_accelerators` | `TRACK_DATA_TECH_CLOUD_ML` | same |

Per-skill admission uses `allowed_sections` on each `skill_row` (stricter than pillar fit).

## Proof authority (all 7 sections)

| Check | Result |
|-------|--------|
| Default skills authority | `augmented_skills_graph` |
| `legacy_broad_skills_ledger=True` | Raises `ValueError` (fail closed) |
| `broad_skills_ledger_used_as_authority` | `false` all sections |
| Claim substrate | SRFS / candidate fact ledger (facts only, not skill labels) |
| Competencies / exec_summary expansion | `track_weighted_graph_expansion` (ACTIVE + external-eligible + `fact_id_links` only) |
| Headline / unify_* / ibm_* | SRFS slice + graph metadata (`allocate_section_facts_from_graph_substrate`) |

## Skill confidence & classification (17 nodes)

| Confidence | Skills |
|------------|--------|
| **HIGH** | `commercial_validation_pilots`, `presales_delivery_handoff`, `aws_modernization_patterns`, `devops_pipeline_blueprint`, `demoable_accelerator`, `reusable_accelerators`, `adoption_derisking`, `ibm_cloud_portfolio_anchor` |
| **MEDIUM** | All other ACTIVE GTM/tech skills with `fact_id_links` |
| **LOW / INTERNAL_ONLY** | `estimation_sizing_directional`, `anchor_major_airline_devops_aws` |

| Class | Skills |
|-------|--------|
| **Claim-eligible skill row** (ACTIVE, external-eligible, snippets/facts) | 15 skills (excludes INTERNAL_ONLY) |
| **Anchor-only** | `ibm_cloud_portfolio_anchor` — IBM **$30M** portfolio snippet; DRAFT; use IBM employment facts, not airline/$100M |
| **Directional / never external** | `estimation_sizing_directional`, `anchor_major_airline_devops_aws` |
| **DRAFT** (no `track_weighted` admission until ACTIVE) | `commercial_validation_pilots`, `presales_delivery_handoff`, `demoable_accelerator`, `adoption_derisking`, `ibm_cloud_portfolio_anchor` |

## SRFS-blocked / confirmation-queue facts (hybrid JD fixture)

Facts **not** in SRFS selected slices; on human-confirmation queue:

- `fact_solutions_001` → blocks **solution_mapping** claims in exec_summary / ibm_narrative / competencies
- `fact_solutions_002` → blocks **reference_architecture** claims in competencies / ibm_bullets
- `fact_partnerships_gtm_005` → blocks **stakeholder_alignment** in exec_summary / unify_narrative

Exec-summary expansion audit marks 29 facts `support_level: BLOCKED` for external governance; runtime SRFS still selects some MEDIUM facts elsewhere (e.g. `fact_revenue_ops_001` on IBM bullets path).

## Section rollups

See machine-readable matrix: [skills_graph_phase2_section_projection_audit.json](skills_graph_phase2_section_projection_audit.json) → `section_rollups`.

**Track expansion (exec_summary seed, hybrid JD):** admits only  
`skill_p2_gtm_discovery_qualification`, `skill_p2_gtm_enterprise_deal_support`, `skill_p2_gtm_executive_buyer_alignment`.

## Explicit non-claims (from closeout)

- No major-airline client or ~$100M engagement ownership
- Do not conflate IBM $30M portfolio with airline anchor
- No customer-success-primary claims added
- `fact_solutions_001` / `fact_solutions_002` remain confirmation-gated

## Blocking defects

**None.** DRAFT activation and INTERNAL_ONLY nodes are policy gates, not resolver bugs. Promote skills/facts via evidence uplift before expecting generated content.
