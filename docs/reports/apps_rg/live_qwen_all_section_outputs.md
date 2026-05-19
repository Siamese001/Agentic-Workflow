# Live Qwen — all section outputs

**STATUS: PARTIAL**

Generated: 2026-05-18T23:45:56Z

## Receipt

```text
STATUS: PARTIAL
FILES_CHANGED:
- [live_qwen_all_section_outputs.md](docs/reports/apps_rg/live_qwen_all_section_outputs.md)
- [live_qwen_all_section_outputs.json](docs/reports/apps_rg/live_qwen_all_section_outputs.json)
COMMANDS_RUN:
- python -m compileall apps_rg tests -q
- python -m apps_rg --section headline --provider qwen_vllm --allow-non-allow-exit-zero
- python -m apps_rg --section executive_summary --provider qwen_vllm --allow-non-allow-exit-zero
- python -m apps_rg --section competencies --provider qwen_vllm --allow-non-allow-exit-zero
- python -m apps_rg --section unify_bullets --provider qwen_vllm --allow-non-allow-exit-zero
- python -m apps_rg --section unify_narrative --provider qwen_vllm --allow-non-allow-exit-zero
- python -m apps_rg --section ibm_bullets --provider qwen_vllm --allow-non-allow-exit-zero
- python -m apps_rg --section ibm_narrative --provider qwen_vllm --allow-non-allow-exit-zero
- git diff -- agentic_core
SECTION_OUTPUTS:
### headline
- run_dir: `artifacts/apps_rg/runtime_proofs/headline/real/headline_20260518_233603`
- artifact: `headline_output.txt`

```
SVP Engineering | Governed Agentic Platforms | Production AI Reliability | Enterprise Scale
```

### executive_summary
- run_dir: `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260518_233710`
- artifact: `resume_display_text.txt`

```
Engineering executive with expertise in designing and operationalizing governed agentic AI platforms for regulated enterprise environments. Built software dependency graph intelligence to enhance architecture visibility and reduce refactor risk, while scaling the ML engineering organization from 8 to 28 specialists, improving reliability and auditability of AI systems.
```

### competencies
- run_dir: `artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260518_233832`
- artifact: `competencies_section_output.json`

```
{
  "schema_version": "1",
  "section_id": "competencies",
  "canonical_aggregation_note": "CANONICAL_DOWNSTREAM_AGGREGATION_INPUT — use this file as the sole bundle-shaped join surface for competencies (display_lines, competencies[], claim_ledger, proof-boundary flags, X2/X3 refs). competencies_output.json is legacy competencies[] only; provider_response.json is transport-only diagnostic.",
  "artifact_role_bundle": {
    "competencies_section_output.json": "canonical_downstream_aggregation_input",
    "competencies_output.json": "legacy_competencies_array_only",
    "provider_response.json": "diagnostic_transport_metadata_only",
    "l2_output.json": "rich_runtime_section_object_with_refs"
  },
  "display_lines": [],
  "competencies": [],
  "claim_ledger": [],
  "selected_fact_ids": [
    "fact_certs_001",
    "fact_consulting_001",
    "fact_engineering_platform_001",
    "fact_engineering_platform_002",
    "fact_engineering_platform_003",
    "fact_engineering_platform_004",
    "fact_engineering_platform_004_metric_06dd515f",
    "fact_engineering_platform_005",
    "fact_engineering_platform_006",
    "fact_engineering_platform_006_metric_6f3de275",
    "fact_exec_002",
    "fact_exec_002_metric_c880fce9",
    "fact_governance_003",
    "fact_governance_003_metric_e5abeb74",
    "fact_quant_hpc_001",
    "fact_quant_hpc_001_metric_219867bb",
    "fact_quant_hpc_002",
    "fact_quant_hpc_002_metric_bed54a9b",
    "fact_quant_hpc_003"
  ],
  "targeting_only": true,
  "jd_used_as_proof": false,
  "briefing_used_as_proof": false,
  "companion_context_used_as_proof": false,
  "runtime_generation_status": "BLOCKED",
  "x2_gate_outputs_ref": "artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260518_233832/x2_gate_outputs.json",
  "x3_disposition_ref": "artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260518_233832/x3_disposition.json",
  "section_input_usage_ledger_ref": "artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260518_233832/section_input_usage_ledger.json",
  "proof_eligible": false,
  "proof_scope": "plumbing_only",
  "product_quality_status": "FAIL",
  "x3_code": "X3_BLOCK",
  "l6_shadow_eval_package_ref": "artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260518_233832/l6_shadow_eval_package.json",
  "l6_shadow_learning_ref": "artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260518_233832/l6_shadow_learning.json",
  "l6_future_run_proposals_ref": "artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260518_233832/l6_future_run_proposals.json",
  "l6_shadow_rca_sketch_ref": "artifacts/apps_rg/runtime_proofs/competencies/real/competencies_20260518_233832/l6_shadow_rca_sketch.json"
}
```

### unify_bullets
- run_dir: `artifacts/apps_rg/runtime_proofs/unify_bullets/real/unify_bullets_20260518_234153`
- artifact: `unify_bullets_output.txt`

```
- bul_unify_001: Designed and operationalized governed agentic AI platform capabilities for regulated enterprise workflows, incorporating deterministic routing, multi-agent orchestration, GraphRAG retrieval, sandboxed execution, policy gating, validation controls, and replayable execution traces.
- bul_unify_002: Built and applied software dependency graph intelligence to accelerate legacy-system analysis, exposing dependency chains, improving architecture visibility, and reducing refactor risk.
- bul_unify_003: Strengthened retrieval quality, context assembly, evaluation gates, telemetry instrumentation, rollback controls, and AI CI/CD standards to ensure AI behavior is traceable, supportable, and repeatable.
- bul_unify_004: Standardized AI lifecycle practices across intake, validation, execution, monitoring, and remediation, reducing lab-to-production cycle time from six months to three weeks while maintaining auditability and runtime stability.
- bul_unify_005: Architected cloud-native microservices across AWS and Databricks Lakehouse, integrating enterprise data pipelines, vector services, API gateways, identity controls, and highly available execution layers.
- bul_unify_006: Productized agentic AI primitives into reusable platform services, generating $22M in IP-led revenue, expanding gross margins by 20%, and scaling the ML engineering organization from 8 to 28 specialists.
```

### unify_narrative
- run_dir: `artifacts/apps_rg/runtime_proofs/unify_narrative/real/unify_narrative_20260518_234310`
- artifact: `unify_narrative_output.txt`

```
Led the platform roadmap, core systems architecture, and commercialization of a production-grade generative AI Solution Accelerator at Unify Consulting, converting bespoke client delivery into reusable IP deployed across enterprise lines of business.
```

### ibm_bullets
- run_dir: `artifacts/apps_rg/runtime_proofs/ibm_bullets/real/ibm_bullets_20260518_234400`
- artifact: `ibm_bullets_output.txt`

```
- bul_ibm_001: Directed large-scale regulatory IT transformations and legacy-modernization programs for major financial institutions.
- bul_ibm_002: Implemented Basel III / CCAR data lineage, cataloging, and automated validation frameworks that reduced regulatory reporting errors by 40%.
- bul_ibm_003: Re-architected monolithic risk analytics with containerized microservices and HPC, reducing calculation or stress-testing cycles by 40%.
- bul_ibm_004: Enabled real-time stress testing by implementing containerized microservices and HPC solutions.
- bul_ibm_005: Modernized legacy systems for major financial institutions, ensuring compliance with regulatory requirements.
```

### ibm_narrative
- run_dir: `artifacts/apps_rg/runtime_proofs/ibm_narrative/real/ibm_narrative_20260518_234511`
- artifact: `ibm_narrative_output.txt`

```
At IBM, led enterprise-scale cloud, data, lineage and observability initiatives for regulated financial services, establishing the reliability and governance discipline that supported later production AI platform leadership.
```

SKILLS_GRAPH_RECEIPTS:
| section | skills_authority_source_type | skills_authority_status | claim_evidence_source_type | legacy_broad_skills_ledger_skills_authority | x2_status | x3_code | proof_eligible |
|---------|------------------------------|-------------------------|----------------------------|-----------------------------------------------|-----------|---------|----------------|
| headline | augmented_skills_graph | PASS | candidate_fact_ledger | False | PASS | X3_ALLOW | False |
| executive_summary | augmented_skills_graph | PASS | candidate_fact_ledger | False | PASS | X3_REVIEW_JUDGE_SOFT_FAIL | False |
| competencies | augmented_skills_graph | PASS | candidate_fact_ledger | False | FAIL | X3_BLOCK | False |
| unify_bullets | augmented_skills_graph | PASS | candidate_fact_ledger | False | PASS | X3_ALLOW | False |
| unify_narrative | augmented_skills_graph | PASS | candidate_fact_ledger | False | PASS | X3_ALLOW | True |
| ibm_bullets | augmented_skills_graph | PASS | candidate_fact_ledger | False | FAIL | X3_BLOCK | False |
| ibm_narrative | augmented_skills_graph | PASS | candidate_fact_ledger | False | FAIL | X3_BLOCK | False |

AGENTIC_CORE_DIFF_STATUS: clean

EXPLICIT_NON_CLAIMS:
- CLI exit 0 with --allow-non-allow-exit-zero does not imply X3 ALLOW or proof_eligible.
- This wave proves live Qwen generation + augmented_skills_graph authority presence, not full certification.

OPEN_GAPS:
- competencies: Qwen/vLLM TimeoutError — empty competencies[]; runtime_generation_status BLOCKED
- executive_summary: X3_REVIEW_JUDGE_SOFT_FAIL (skills authority PASS)
- ibm_bullets: X2 FAIL / X3_BLOCK (live Qwen output present)
- ibm_narrative: X2 FAIL / X3_BLOCK (live Qwen output present)

NOTES:
- Live Qwen body generation: 6/7 (competencies timed out)
- Skills authority augmented_skills_graph PASS: 7/7
- X3 ALLOW: 3/7 (headline, unify_bullets, unify_narrative)
```
