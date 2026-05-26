# Commercial MEDIUM claim output containment

**Status:** PASS

## Sections tested

`unify_bullets`, `unify_narrative`, `ibm_bullets`, `ibm_narrative`

## Headline / executive_summary (HIGH-only)

### `headline`
- `fact_quant_hpc_001` [HIGH] eligible_high_with_metrics_requires_source_trace
- `fact_quant_hpc_003` [HIGH] eligible_high_qualitative
- `fact_engineering_platform_004` [HIGH] eligible_high_with_metrics_requires_source_trace
- `fact_consulting_001` [HIGH] eligible_high_qualitative
- `fact_engineering_platform_002` [HIGH] eligible_high_qualitative
### `executive_summary`
- `fact_certs_001` [HIGH] eligible_high_qualitative
- `fact_engineering_platform_006` [HIGH] eligible_high_with_metrics_requires_source_trace
- `fact_engineering_platform_001` [HIGH] eligible_high_qualitative
- `fact_exec_002` [HIGH] eligible_high_with_metrics_requires_source_trace
- `fact_governance_003` [HIGH] eligible_high_with_metrics_requires_source_trace
- `fact_quant_hpc_002` [HIGH] eligible_high_with_metrics_requires_source_trace

## Claim-eligible MEDIUM by section

- **unify_bullets**: ['fact_revenue_ops_003', 'fact_sales_accounts_001', 'fact_partnerships_gtm_001', 'fact_partnerships_gtm_003']
- **unify_narrative**: []
- **ibm_bullets**: ['fact_revenue_ops_004', 'fact_revenue_ops_002', 'fact_revenue_ops_001', 'fact_partnerships_gtm_002', 'fact_revenue_ops_005', 'fact_sales_accounts_002']
- **ibm_narrative**: ['fact_sales_accounts_003']

## Overclaim verdicts

- `fact_revenue_ops_003` @ unify_bullets: **PASS** (archive hit=0.923)
- `fact_sales_accounts_001` @ unify_bullets: **PASS** (archive hit=1.0)
- `fact_partnerships_gtm_001` @ unify_bullets: **PASS** (archive hit=1.0)
- `fact_partnerships_gtm_003` @ unify_bullets: **PASS** (archive hit=1.0)
- `fact_revenue_ops_004` @ ibm_bullets: **PASS** (archive hit=0.938)
- `fact_revenue_ops_002` @ ibm_bullets: **PASS** (archive hit=0.929)
- `fact_revenue_ops_001` @ ibm_bullets: **PASS** (archive hit=1.0)
- `fact_partnerships_gtm_002` @ ibm_bullets: **PASS** (archive hit=1.0)
- `fact_revenue_ops_005` @ ibm_bullets: **PASS** (archive hit=1.0)
- `fact_sales_accounts_002` @ ibm_bullets: **PASS** (archive hit=1.0)
- `fact_sales_accounts_003` @ ibm_narrative: **PASS** (archive hit=1.0)

## Blocked facts

- In pools: `[]` (expected `[]`)
