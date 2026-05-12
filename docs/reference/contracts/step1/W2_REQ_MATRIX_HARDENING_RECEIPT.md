# W2 REQ_MATRIX Hardening Receipt

**Date**: 2026-05-12  
**Plan**: agentic-core-spine-contract-hardening-a7d4e1  
**Scope**: W2.P1 (L0/L3) + W2.P2 (C0) + W2.P3 (PA) — Route/Context/Prompt layers

---

## Summary

| Phase | File | Before (TBDs) | After (TBDs) | Status |
|-------|------|---------------|--------------|--------|
| W2.P1 | 03_L0_L3_REQ_MATRIX.md | ~88 | 0 | ✅ HARDENED |
| W2.P2 | 03A_C0_REQ_MATRIX.md | ~96 | 0 | ✅ HARDENED |
| W2.P3 | 03B_PA_REQ_MATRIX.md | ~96 | 0 | ✅ HARDENED |
| **Total** | | **~280** | **0** | **✅ W2 COMPLETE** |

---

## W2.P1: L0 Route Decision / L3 Orchestration Hardening

### Layer Contract Summary Added

#### L0 Route Decision
- **incoming_contracts**: L1PlanContract
- **outgoing_contracts**: RouteContract, RETTerminalPacket, GroundingRouteContract, ManagedWorkflowRouteContract, RouteRejected
- **required_l5_refs**: policy_hash, blueprint_hash, registry_digest_set, l5_governance_context_digest, route_manifest_hash, capability_ceiling, sandbox_requirement, replay_key, audit_manifest_ref
- **required_contract_gates**: route_selection_gate, route_determinism_gate, cache_reuse_gate, grounding_requirement_gate, cost_latency_budget_gate, hitl_posture_gate
- **receipts**: route_digest, route_telemetry, route_replay_receipt
- **otel_spans**: l0.route_preflight, l0.route_selection, l0.route_handoff
- **artifacts**: route_contract.json, route_telemetry.json
- **fail_closed_if**: no L1PlanContract, multiple routes emitted, route not replayable, registry digest missing, route widens authority

**L0 Boundary**: L0 chooses exactly one route. L0 must not retrieve, assemble prompts, execute, call tools/models, write L4, or learn.

#### L3 Orchestration
- **incoming_contracts**: ManagedWorkflowRouteContract
- **outgoing_contracts**: L3ToL2StepContract, SealedWorkflowPackage, L3StepBlocked
- **required_l5_refs**: managed_workflow_route_contract_ref, policy_hash, blueprint_hash, registry_digest_set, l5_governance_context_digest, capability_ceiling, sandbox_ceiling, replay_key, audit_manifest_ref
- **required_contract_gates**: workflow_trajectory_gate, loop_retry_thrash_gate, branch_join_budget_gate, step_authority_preservation_gate
- **receipts**: workflow_ledger, checkpoint_ref, branch_join_state, step_handoff_receipt
- **otel_spans**: l3.workflow_init, l3.step_scheduling, l3.handoff_to_l2
- **artifacts**: workflow_package.json, l3_ledger.json
- **fail_closed_if**: L3 chooses new route, workflow exceeds bounds, step widens authority, step adds unapproved tool/provider/credential, direct L4 write authorized

**L3 Boundary**: L3 sequences approved managed workflow steps only. L3 must not re-route, retrieve directly, assemble prompts, execute, approve output, write L4, or learn.

---

## W2.P2: C0 Context Engine Hardening

### Layer Contract Summary Added
- **incoming_contracts**: RouteContract with grounding_required = true
- **outgoing_contracts**: FinalEvidenceContract, EvidenceBlockedContract
- **required_l5_refs**: origin_trust_manifest_ref, source_lineage_map, acl_verification_receipts, freshness_receipts, contradiction_report, l5_governance_context_digest, audit_manifest_ref
- **required_contract_gates**: retrieval_legality_gate, evidence_quality_gate, acl_freshness_lineage_gate, contradiction_support_gate, retrieved_content_trust_gate, privacy_cross_context_gate
- **receipts**: evidence_receipt, citation_map, contradiction_report, support_status
- **otel_spans**: c0.preflight_grounding, c0.retrieval_plan, c0.evidence_fetch, c0.graph_rag, c0.shape_rerank, c0.weak_support_check, c0.final_evidence_seal
- **artifacts**: final_evidence_contract.json, c0_observability.json
- **fail_closed_if**: evidence required but unavailable, blocked source included, retrieved text becomes instruction, ACL/freshness/source lineage missing, support_status UNKNOWN treated as PASS

**C0 Boundary**: C0 retrieves, hydrates, scores, stratifies, verifies evidence. C0 must not answer, route, assemble prompts, execute, write L4, or inflate support.

---

## W2.P3: PA Prompt Assembly Hardening

### Layer Contract Summary Added
- **incoming_contracts**: L1PlanContract, RouteContract, FinalEvidenceContract when grounding_required = true, L5 refs, schema refs
- **outgoing_contracts**: PromptEnvelope / CompiledPromptArtifact, PromptAssemblyRejected
- **required_l5_refs**: policy_hash, blueprint_hash, registry_digest_set, origin_trust_manifest_ref, l5_governance_context_digest, provider lane certification refs, egress certification refs when applicable, replay_manifest, audit_manifest_ref
- **required_contract_gates**: prompt_boundary_gate, instruction_data_boundary_gate, slot_authority_order_gate, schema_binding_gate, provider_rendering_gate, deterministic_trim_gate
- **receipts**: prompt_envelope, compiled_prompt_artifact, slot_validity_receipt, provider_manifest_ref
- **otel_spans**: pa.bom_load, pa.slot_composition, pa.airlock_security, pa.slot_validation, pa.token_budget, pa.provider_rendering, pa.final_emit
- **artifacts**: prompt_envelope.json, compiled_prompt_artifact.json, pa_observability.json
- **fail_closed_if**: PA retrieves non-C0 evidence, user text becomes instruction, slot order violates authority, airlock allows unauthorized slot, provider/egress binding missing, provider variance non-deterministic, instruction/data boundary violated

**PA Boundary**: PA composes, renders, hashes, signs, and packages only. PA must not retrieve, route, execute, approve L2 execution, write L4, or learn.

---

## Verification Results

### Command 1: TBD Check
```bash
grep -n "TBD_" docs/reference/contracts/step1/03_L0_L3_REQ_MATRIX.md docs/reference/contracts/step1/03A_C0_REQ_MATRIX.md docs/reference/contracts/step1/03B_PA_REQ_MATRIX.md
```
**Result**: No matches found ✅

### Command 2: 00C/G01-G29 Check
```bash
grep -n "00C\|G01\|G02\|G03\|G04\|G05\|G06\|G07\|G08\|G09\|G10\|G11\|G12\|G13\|G14\|G15\|G16\|G17\|G18\|G19\|G20\|G21\|G22\|G23\|G24\|G25\|G26\|G27\|G28\|G29" docs/reference/contracts/step1/03_L0_L3_REQ_MATRIX.md docs/reference/contracts/step1/03A_C0_REQ_MATRIX.md docs/reference/contracts/step1/03B_PA_REQ_MATRIX.md
```
**Result**: No matches found ✅

### Command 3: Other REQ_MATRIX Files Unchanged
Confirmed: No modifications to:
- 01_U0_INTAKE_REQ_MATRIX.md (W1 scope — unchanged)
- 02_L1_PLAN_REQ_MATRIX.md (W1 scope — unchanged)
- 04_L2_REQ_MATRIX.md (W3 scope — untouched)
- 05_EXIT_REQ_MATRIX.md (W4 scope — untouched)
- 00B_L4_UWG_REQ_MATRIX.md (W4 scope — untouched)
- 06_L6_REQ_MATRIX.md (W4 scope — untouched)
- 99_E2E_REQ_MATRIX.md (W5 scope — untouched)

---

## Sign-off

| Criterion | Status |
|-----------|--------|
| 03_L0_L3_REQ_MATRIX.md hardened | ✅ |
| 03A_C0_REQ_MATRIX.md hardened | ✅ |
| 03B_PA_REQ_MATRIX.md hardened | ✅ |
| Zero TBD placeholders in W2 scope | ✅ |
| Zero 00C/G01-G29 references in W2 scope | ✅ |
| Layer boundaries preserved (L0, L3, C0, PA) | ✅ |
| REQ_ID-first structure preserved | ✅ |
| No new REQ_IDs introduced | ✅ |
| Contract gate terminology used throughout | ✅ |

---

## Next Steps

**🛑 STOP: W2 Complete. W3 NOT started.**

W3 scope (pending explicit approval):
- W3.P1: L2_REQ_MATRIX hardening (04_L2_REQ_MATRIX.md)
- W3.P2: L2 E1-E5 sub-sections

---

**Receipt Generated**: 2026-05-12  
**W2 Status**: COMPLETE
