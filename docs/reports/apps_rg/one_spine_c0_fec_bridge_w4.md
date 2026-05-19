# One-spine C0/FEC bridge Wave 4 (runtime artifact proof)

Generated: 2026-05-19T15:44:53.011759+00:00
**STATUS: PASS**

**Runtime command:** `python -m apps_rg --section executive_summary --target-company Unify Consulting --target-role SVP Engineering, Agentic AI Platforms --jd apps_rg/config/default_jd_targeting.txt --manual-brief apps_rg/config/default_targeting_briefing.txt --allow-non-allow-exit-zero` (exit 0)

**ARTIFACT_ROOT:** `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_154356`
**RUN_DIR:** `exec_summary_20260519_154356`

## ARTIFACT_PROOF_MATRIX

| Claim | Artifact | Fields | Expected | Actual | Status |
|-------|----------|--------|----------|--------|--------|
| 1. RouteContract exists before FEC bridge | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_154356/route_contract.json` | contract_type, route_contract_ref | RouteContract present before bridge | RouteContract | **PASS** |
| 2. FEC bridge artifact emitted | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_154356/final_evidence_contract_bridge.json` | fec_bridge_mode, bridge_type, schema_version | final_evidence_contract_bridge.json with section_fec_bridge | mode=section_fec_bridge; type=FinalEvidenceContractBridge | **PASS** |
| 3. FEC bridge references RouteContract | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_154356/final_evidence_contract_bridge.json` | route_contract_ref | route_contract_ref=route_contract.json | route_contract.json | **PASS** |
| 4. FEC bridge references proof_pool/SRFS/skills graph lineage | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_154356/final_evidence_contract_bridge.json` | proof_pool_ref, proof_pool_digest, srfs_ref, citation_lineage_refs | proof_pool ref/digest + lineage refs | pool_ref=apps_rg\fact_inventory\master_skills_arsenal_ledger.json; lineage_count=66; srfs= | **PASS** |
| 5. FEC bridge has explicit support_status | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_154356/final_evidence_contract_bridge.json` | support_status | support_status present | SUPPORTED | **PASS** |
| 6. FEC bridge does not claim canonical C0.2/C0.3/C0.5 | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_154356/final_evidence_contract_bridge.json` | canonical_c0_2_claimed, canonical_c0_3_claimed, canonical_c0_5_claimed | all false on section bridge | c02=False; c03=False; c05=False | **PASS** |
| 7. PA consumed FEC bridge/canonical FEC | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_154356/compiled_prompt_artifact.json` | evidence_contract_consumed, fec_bridge_ref, fec_bridge_mode | evidence_contract_consumed true | consumed=True; ref=final_evidence_contract_bridge.json; mode=section_fec_bridge | **PASS** |
| 8. PA did not consume raw proof_pool directly | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_154356/compiled_prompt_artifact.json` | raw_proof_pool_direct_to_pa | raw_proof_pool_direct_to_pa false | False | **PASS** |
| 9. Product-visible PA bypass without FEC blocked | `docs/reports/apps_rg/section_pa_fec_precondition_blocked_proof.json` | raised, error_type | SectionFecBridgePreconditionError | raised=True; type=SectionFecBridgePreconditionError | **PASS** |
| 10. Fixture/dev bypass non-product-certified | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_154356/c0_fec_bridge_receipt.json` | fixture_dev_only, non_product_certified, product_certification | fixture_dev_only false on product run | fixture=False; non_cert=False; cert=NOT_CLAIMED | **PASS** |

## Explicit non-claims

- not canonical C0.2 dense retrieval unless spine Chroma dense path ran
- not canonical C0.3 governed graph traverse unless spine traverse ran
- not canonical C0.5 FinalEvidenceContract unless spine C0 emitted FEC
