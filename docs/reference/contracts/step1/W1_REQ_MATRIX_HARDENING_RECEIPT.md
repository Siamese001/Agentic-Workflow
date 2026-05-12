# W1 REQ_MATRIX Hardening Receipt

**Date**: 2026-05-12  
**Plan**: agentic-core-spine-contract-hardening-a7d4e1  
**Scope**: W1.P1 (U0) + W1.P2 (L1) — Layer matrix hardening

---

## Summary

| Phase | File | Before (TBDs) | After (TBDs) | Status |
|-------|------|---------------|--------------|--------|
| W1.P1 | 01_U0_INTAKE_REQ_MATRIX.md | ~86 | 0 | ✅ HARDENED |
| W1.P2 | 02_L1_PLAN_REQ_MATRIX.md | ~86 | 0 | ✅ HARDENED |
| **Total** | | **~172** | **0** | **✅ W1 COMPLETE** |

---

## W1.P1: U0 Request Intake Hardening

### Layer Contract Summary Added
- **incoming_contracts**: raw inbound envelope
- **outgoing_contracts**: ValidatedRequest, RejectedRequest
- **required_l5_refs**: origin_trust_manifest_ref, data_boundary_labels, policy_hash (when available), l5_governance_context_digest (when L5-certifiable), audit_manifest_ref
- **required_contract_gates**: request_ingress_gate, identity_tenant_session_gate, quota_idempotency_gate, origin_label_gate, malformed_duplicate_size_gate, intent_ambiguity_gate, safety_policy_gate, privacy_cross_context_gate
- **receipts**: intake_receipt, request_digest, origin_label_seed
- **otel_spans**: u0.envelope_validate, u0.identity_stamp, u0.handoff_to_l1
- **artifacts**: validated_request.json, rejected_request.json, intake_observability.json
- **fail_closed_if**: missing request_id, missing run_id, missing trace_root, missing origin labels, user text promoted into authority

### TBD Replacements (11 rows × ~8 columns)
All TBD_REQUIRED_RUNTIME_EVIDENCE, TBD_REQUIRED_SPAN, TBD_REQUIRED_ARTIFACT, TBD_REQUIRED_VALIDATOR, TBD_REQUIRED_TEST, TBD_REQUIRED_NEGATIVE_CONTROL, TBD_EXPECTED_FAIL_REASON, TBD_REQUIRED_REPLAY_CHECK replaced with concrete values.

### U0 Boundary Preserved
- U0 validates envelope, identity, session, quota, origin labels, and safe handoff
- U0 must not reason, route, retrieve, assemble prompts, execute, write L4, or learn

---

## W1.P2: L1 Reasoning/Plan Hardening

### Layer Contract Summary Added
- **incoming_contracts**: ValidatedRequest
- **outgoing_contracts**: L1PlanContract, L1PlanRejected
- **required_l5_refs**: policy_ref_set, planning_prior_refs, authority_scope expectation, risk_hint, grounding/action/HITL/UWG hints, data_boundary_labels, l5_governance_context_digest, audit_manifest_ref
- **required_contract_gates**: intent_ambiguity_gate, authority_separation_gate, safety_policy_gate, risk_tier_gate, planning_prior_read_gate, workflow_shape_precheck_gate
- **receipts**: plan_digest, ambiguity_register, support_expectation, action_expectation, route_hints
- **otel_spans**: l1.intent_frame, l1.planning_priors_read, l1.plan_validate, l1.handoff_to_l0
- **artifacts**: l1_plan_contract.json, l1_plan_observability.json
- **fail_closed_if**: L1 selects final route, L1 retrieves final evidence, L1 creates execution authority, ambiguity affects irreversible action and unresolved

### TBD Replacements (11 rows × ~8 columns)
All TBD placeholders replaced with concrete runtime evidence, span names, artifact paths, validators, test files, negative controls, fail reasons, and replay checks.

### L1 Boundary Preserved
- L1 interprets intent and creates advisory plan only
- L1 must not select final route, retrieve final evidence, assemble prompts, execute, approve egress, write L4, or create execution authority

---

## Verification Results

### Command 1: TBD Check
```bash
grep -n "TBD_" docs/reference/contracts/step1/01_U0_INTAKE_REQ_MATRIX.md docs/reference/contracts/step1/02_L1_PLAN_REQ_MATRIX.md
```
**Result**: No matches found ✅

### Command 2: 00C/G01-G29 Check
```bash
grep -n "00C\|G01\|G02\|G03\|G04\|G05\|G06\|G07\|G08\|G09\|G10\|G11\|G12\|G13\|G14\|G15\|G16\|G17\|G18\|G19\|G20\|G21\|G22\|G23\|G24\|G25\|G26\|G27\|G28\|G29" docs/reference/contracts/step1/01_U0_INTAKE_REQ_MATRIX.md docs/reference/contracts/step1/02_L1_PLAN_REQ_MATRIX.md
```
**Result**: No matches found ✅

### Command 3: Other REQ_MATRIX Files Unchanged
Confirmed: No modifications to:
- 00A_L5_REQ_MATRIX.md
- 00B_L4_UWG_REQ_MATRIX.md
- 03_L0_L3_REQ_MATRIX.md
- 03A_C0_REQ_MATRIX.md
- 03B_PA_REQ_MATRIX.md
- 04_L2_REQ_MATRIX.md
- 05_EXIT_REQ_MATRIX.md
- 06_L6_REQ_MATRIX.md
- 99_E2E_REQ_MATRIX.md

---

## Sign-off

| Criterion | Status |
|-----------|--------|
| 01_U0_INTAKE_REQ_MATRIX.md hardened | ✅ |
| 02_L1_PLAN_REQ_MATRIX.md hardened | ✅ |
| Zero TBD placeholders in W1 scope | ✅ |
| Zero 00C/G01-G29 references in W1 scope | ✅ |
| Layer boundaries preserved (U0, L1) | ✅ |
| REQ_ID-first structure preserved | ✅ |
| No new REQ_IDs introduced | ✅ |
| Contract gate terminology used throughout | ✅ |

---

## Next Steps

**🛑 STOP: W1 Complete. W2 NOT started.**

W2 scope (pending explicit approval):
- W2.P1: L0_L3_REQ_MATRIX hardening
- W2.P2: C0_REQ_MATRIX hardening
- W2.P3: PA_REQ_MATRIX hardening

---

**Receipt Generated**: 2026-05-12  
**W1 Status**: COMPLETE
