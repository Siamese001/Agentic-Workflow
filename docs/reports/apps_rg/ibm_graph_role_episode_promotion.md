# IBM Graph Role Episode Promotion Report

**Generated:** 2026-05-28T13:00:00Z  
**Wave:** `ibm_graph_promotion_wave_2026-05-28`  
**Employer:** IBM | `employment_exp_ibm_001`  
**Time Window:** 2017-04 to 2022-10  

## Scope Invariants

| Invariant | Status |
|-----------|--------|
| IBM only (Unify not modified) | ✓ ENFORCED |
| Unify skill_rows not touched | ✓ ENFORCED |
| `agentic_core/` not modified | ✓ ENFORCED |
| X2/X3 gates not weakened | ✓ ENFORCED |
| Archive prose not used as output prose | ✓ ENFORCED |
| HOLD/DO NOT PROMOTE metrics excluded | ✓ ENFORCED |

## IBM Skill Promotions

### New Skill Rows Added (4)

#### `skill_ibm_automated_release_pipelines`
- **Status:** `ACTIVE_CONFIRMED`
- **Employer:** IBM | Node: `employment_exp_ibm_001`
- **Time Window:** 2017-04 to 2022-10
- **Confidence:** HIGH
- **Allowed Sections:** ['ibm_bullets', 'ibm_narrative', 'competencies']
- **Archive Signals:** ['sig_ibm_003', 'sig_comp_002']
- **Graph Node Present:** True
- **Employment Edge:** `edge_employment_skill_employment_exp_ibm_001_skill_ibm_automated_release_pipelines` — True

#### `skill_ibm_devsecops_pipeline_security`
- **Status:** `ACTIVE_CONFIRMED`
- **Employer:** IBM | Node: `employment_exp_ibm_001`
- **Time Window:** 2017-04 to 2022-10
- **Confidence:** HIGH
- **Allowed Sections:** ['ibm_bullets', 'ibm_narrative', 'competencies']
- **Archive Signals:** ['sig_ibm_004', 'sig_comp_002']
- **Graph Node Present:** True
- **Employment Edge:** `edge_employment_skill_employment_exp_ibm_001_skill_ibm_devsecops_pipeline_security` — True

#### `skill_ibm_metadata_audit_rbac`
- **Status:** `ACTIVE_CONFIRMED`
- **Employer:** IBM | Node: `employment_exp_ibm_001`
- **Time Window:** 2017-04 to 2022-10
- **Confidence:** HIGH
- **Allowed Sections:** ['ibm_bullets', 'ibm_narrative', 'competencies']
- **Archive Signals:** ['sig_ibm_008']
- **Graph Node Present:** True
- **Employment Edge:** `edge_employment_skill_employment_exp_ibm_001_skill_ibm_metadata_audit_rbac` — True

#### `skill_ibm_watson_studio_analytics`
- **Status:** `ACTIVE`
- **Employer:** IBM | Node: `employment_exp_ibm_001`
- **Time Window:** 2017-04 to 2022-10
- **Confidence:** MEDIUM
- **Allowed Sections:** ['ibm_bullets', 'ibm_narrative']
- **Archive Signals:** ['sig_ibm_010']
- **Graph Node Present:** True
- **Employment Edge:** `edge_employment_skill_employment_exp_ibm_001_skill_ibm_watson_studio_analytics` — True

### DRAFT → ACTIVE Promotions (2)

#### `skill_confluent_streaming_platforms`
- **Status:** DRAFT → `ACTIVE_CONFIRMED`
- **Employer Binding Added:** IBM | `employment_exp_ibm_001`
- **Archive Signals Added:** ['sig_ibm_006', 'sig_ibm_007']
- **IBM Sections Added:** ['ibm_bullets', 'ibm_narrative']

#### `skill_risk_greek_stress_testing`
- **Status:** DRAFT → `ACTIVE_CONFIRMED`
- **Employer Binding Added:** IBM | `employment_exp_ibm_001`
- **Archive Signals Added:** ['sig_ibm_002']
- **IBM Sections Added:** ['ibm_bullets', 'ibm_narrative']

## Role Episode Bundles (6)

### `reb_ibm_cloud_modernization`
**Theme:** Cloud Modernization / Containerized Microservices  
**Employer:** IBM | **Time Window:** 2017-04 to 2022-10  
**Config Gate:** `BLOCKED_FOR_CONFIG_ENABLEMENT`  

**Graph Skill Nodes:** ['skill_sr_microservices_integration_platform', 'skill_sr_cloud_data_platform_engineering', 'skill_ibm_automated_release_pipelines']

**Held Metrics (HOLD — do not promote):**
- $15M modernization deals (HOLD - single source)
**Section Eligibility:** ['ibm_bullets', 'ibm_narrative']

### `reb_ibm_devsecops_reliability`
**Theme:** DevSecOps / Release Reliability  
**Employer:** IBM | **Time Window:** 2017-04 to 2022-10  
**Config Gate:** `BLOCKED_FOR_CONFIG_ENABLEMENT`  

**Graph Skill Nodes:** ['skill_ibm_devsecops_pipeline_security', 'skill_ibm_automated_release_pipelines', 'skill_ibm_metadata_audit_rbac']

**Promotable Metrics:**
- 10% FinOps savings via CI/CD best practices (unique metric from Chief AI Officer resume)
**Section Eligibility:** ['ibm_bullets', 'ibm_narrative']

### `reb_ibm_streaming_realtime_analytics`
**Theme:** Streaming / Near-Real-Time Analytics  
**Employer:** IBM | **Time Window:** 2017-04 to 2022-10  
**Config Gate:** `BLOCKED_FOR_CONFIG_ENABLEMENT`  

**Graph Skill Nodes:** ['skill_confluent_streaming_platforms', 'skill_sr_cloud_data_platform_engineering']
**Section Eligibility:** ['ibm_bullets', 'ibm_narrative']

### `reb_ibm_metadata_audit_governance`
**Theme:** Metadata / Audit Trail / RBAC Governance  
**Employer:** IBM | **Time Window:** 2017-04 to 2022-10  
**Config Gate:** `BLOCKED_FOR_CONFIG_ENABLEMENT`  

**Graph Skill Nodes:** ['skill_ibm_metadata_audit_rbac', 'skill_sr_basel_ccar_lineage_regulatory']
**Section Eligibility:** ['ibm_bullets', 'ibm_narrative']

### `reb_ibm_hpc_risk_analytics`
**Theme:** Risk Analytics / HPC Stress Testing  
**Employer:** IBM | **Time Window:** 2017-04 to 2022-10  
**Config Gate:** `BLOCKED_FOR_CONFIG_ENABLEMENT`  

**Graph Skill Nodes:** ['skill_risk_greek_stress_testing', 'skill_sr_cloud_data_platform_engineering', 'skill_confluent_streaming_platforms']

**Held Metrics (HOLD — do not promote):**
- $15M modernization deals (HOLD - single source, SAE only)
**Section Eligibility:** ['ibm_bullets', 'ibm_narrative']

### `reb_ibm_hyperscaler_alliance_partner`
**Theme:** IBM-AWS Hyperscaler Alliance / Partner Execution  
**Employer:** IBM | **Time Window:** 2017-04 to 2022-10  
**Config Gate:** `BLOCKED_FOR_CONFIG_ENABLEMENT`  

**Graph Skill Nodes:** ['skill_partner_ibm_aws_alliance_joint_revenue', 'skill_sr_w12_hyperscaler_alliance_co_sell', 'skill_partner_co_selling']

**Promotable Metrics:**
- 20% joint revenue growth (PROMOTABLE - consistent across 2 resumes, IBM-AWS alliance context)
- $10M IBM ARR (PROMOTABLE - consistent across 2 resumes, IBM Salesforce pipeline context)

**Held Metrics (HOLD — do not promote):**
- $30M Cloud Pak partner revenue (HOLD - single source, CTO Resume only)
**Section Eligibility:** ['ibm_bullets', 'ibm_narrative']

## Metric Decisions

### Promotable

| Metric | Context | Note |
|--------|---------|------|
| 20% joint revenue growth | IBM-AWS alliance co-sell | — |
| $10M IBM ARR | IBM Salesforce pipeline expansion | — |
| 10% FinOps savings | DevSecOps CI/CD practices | unique metric - verify with base resume before use |

### HOLD (Single Source — Do Not Promote Yet)

- **$15M modernization deals** — HOLD - single source (SAE only)
- **$30M Cloud Pak partner revenue** — HOLD - single source (CTO Resume only)

### DO NOT PROMOTE (Overloaded Across Multiple Contexts)

- **25%** — DO NOT PROMOTE - overloaded across 6+ contexts
- **30%** — DO NOT PROMOTE - overloaded across 8+ contexts
- **35%** — DO NOT PROMOTE - overloaded across 6+ contexts
- **40%** — DO NOT PROMOTE - most overloaded metric in archive

## Config Decision

**Status:** `BLOCKED_FOR_CONFIG_ENABLEMENT`

- `ibm_bullets.graph_expansion_allowed` = `False`  (unchanged)
- `ibm_narrative.graph_expansion_allowed` = `False`  (unchanged)

> role_episode_bundle consumption is not yet implemented in the ibm_bullets or ibm_narrative section generation path. Config change requires: (1) section generator wired to consume role_episode_bundle_id, (2) flat skill list consumption prohibited, (3) assert_role_episode_bundle_id_present() called before graph context use.

Config enablement requires:
1. Section generator wired to consume `role_episode_bundle_id` (not flat skill lists)
2. `assert_role_episode_bundle_id_present()` called before graph context is used
3. Flat skill list consumption explicitly prohibited in section generator

## Ledger State After Wave

| Metric | Count |
|--------|-------|
| Total `skill_rows` | 177 |
| Total `graph_nodes` | 240 |
| Total `graph_edges` | 1441 |

## Tests Added

- `tests/unit/apps_rg/test_ibm_graph_role_episode_promotion.py (129 tests)`

## Acceptance Gate Results

| Gate | Result |
|------|--------|
| `python -m compileall apps_rg -q` | ✓ exit 0 |
| IBM promotion tests (129 tests) | ✓ 129/129 PASS |
| `git diff --name-only agentic_core/` | ✓ empty |
| JSON report validates | ✓ valid |
| Bundles JSON validates | ✓ valid |
