# One-spine front bridge Wave 3 redo (runtime artifact proof)

Generated: 2026-05-19T15:34:05.600834+00:00
**STATUS: PASS**

**Runtime command:** `python -m apps_rg --section executive_summary --target-company Unify Consulting --target-role SVP Engineering, Agentic AI Platforms --jd apps_rg/config/default_jd_targeting.txt --manual-brief apps_rg/config/default_targeting_briefing.txt --allow-non-allow-exit-zero` (exit 0)

**ARTIFACT_ROOT:** `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_153230`
**RUN_DIR:** `exec_summary_20260519_153230`

## ARTIFACT_PROOF_MATRIX

| Claim | Artifact | Fields | Expected | Actual | Status |
|-------|----------|--------|----------|--------|--------|
| 1. Product-visible run emitted ValidatedRequest | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_153230/validated_request.json` | contract_type, producer_stage, consumer_stage, validation_status | ValidatedRequest / U0 / L1 / validation_status PASS | ValidatedRequest / U0 / L1 / PASS | **PASS** |
| 2. Product-visible run emitted L1PlanContract | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_153230/l1_plan_contract.json` | contract_type, producer_stage, consumer_stage, validated_request_ref, parent_contract_ref | L1PlanContract / L1 / L0 / refs to ValidatedRequest | L1PlanContract / L1 / L0 / validated_request.json / parent=8e371661… | **PASS** |
| 3. Product-visible run emitted RouteContract | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_153230/route_contract.json` | contract_type, producer_stage, consumer_stage, l1_plan_contract_ref, grounding_required, execution_form | RouteContract / L0 / section_lane_modular / l1 ref / grounding+execution_form | RouteContract / L0 / section_lane_modular / l1_plan_contract.json / gr=True / ef=SINGLE_STEP | **PASS** |
| 4. proof_pool_resolver ran only after front-spine preconditions | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_153230/section_front_spine_receipt.json` | precondition_status, validated_request_ref, l1_plan_contract_ref, route_contract_ref, proof_pool_entry_allowed | precondition PASS + refs + proof_pool_entry_allowed true | precond=PASS; entry_allowed=True; payload_precond=PASS | **PASS** |
| 5. Product-visible bypass blocked without front spine | `docs/reports/apps_rg/section_front_spine_precondition_blocked_proof.json` | raised, error_type, message | SectionFrontSpinePreconditionError raised | raised=True; type=SectionFrontSpinePreconditionError | **PASS** |
| 6. Fixture/dev bypass non-product-certified on product run | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_153230/section_front_spine_receipt.json` | fixture_dev_only, non_product_certified, product_certification | fixture_dev_only false; non_product_certified false; NOT_CLAIMED | fixture_dev_only=False; non_product_certified=False; cert=NOT_CLAIMED | **PASS** |
| 7. Downstream remains non-claimed | `artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260519_153230/section_front_spine_receipt.json` | spine_mode, canonical_c0_claimed, canonical_exit_claimed, product_certification | section_lane_modular; c0/exit false; NOT_CLAIMED | spine_mode=section_lane_modular; c0=False; exit=False; cert=NOT_CLAIMED | **PASS** |

## Explicit non-claims

- no claim of full canonical C0.2 dense retrieval unless Chroma dense path ran
- no claim of full canonical C0.3 graph traverse unless spine route traverse ran
- no claim of canonical C0.5 FinalEvidenceContract unless spine FEC emitted
- no claim of spine ExitDispositionReceipt or RuntimeExhaustBundle
- no claim of full canonical product certification
- no claim that section CLI is fully migrated past L0
