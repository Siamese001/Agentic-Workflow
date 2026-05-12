# W3 REQ_MATRIX Hardening Receipt

**Date**: 2026-05-12  
**Plan**: agentic-core-spine-contract-hardening-a7d4e1  
**Scope**: W3.P1 (L2 matrix) + W3.P2 (E1-E5 sub-sections) — Execution layer

---

## Baseline Captured (Before Hardening)

| Metric | Value |
|--------|-------|
| **Total TBD occurrences** | 102 |
| **Unique TBD tokens** | 8 |
| **TBD tokens list** | TBD_EXPECTED_FAIL_REASON, TBD_REQUIRED_ARTIFACT, TBD_REQUIRED_NEGATIVE_CONTROL, TBD_REQUIRED_REPLAY_CHECK, TBD_REQUIRED_RUNTIME_EVIDENCE, TBD_REQUIRED_SPAN, TBD_REQUIRED_TEST, TBD_REQUIRED_VALIDATOR |

---

## Summary

| Phase | File | Before (TBDs) | After (TBDs) | Status |
|-------|------|---------------|--------------|--------|
| W3.P1 | 04_L2_REQ_MATRIX.md | 102 | 0 | ✅ HARDENED |
| W3.P2 | E1-E5 sub-sections | (included above) | 0 | ✅ HARDENED |
| **Total** | | **102** | **0** | **✅ W3 COMPLETE** |

---

## W3.P1: L2 Execution Hardening

### Layer Contract Summary Added
- **incoming_contracts**: RouteContract, L3ToL2StepContract, PromptEnvelope / CompiledPromptArtifact (when model execution required), L2ExecutionPacket
- **outgoing_contracts**: FrozenExecutionContext, ExecutionValidationReceipt, AttemptReceipt, HealReceipt (when repair occurs), SealedL2Artifact
- **required_l5_refs**: capability_token, sandbox_envelope, policy_hash, blueprint_hash, registry_digest_set, provider/model/tool certification refs, egress certification refs (when provider/tool/network used), replay_key, audit_manifest_ref, l5_governance_context_digest
- **required_contract_gates**: tool_model_registry_gate, tool_argument_gate, external_egress_gate, sandbox_filesystem_shell_gate, memory_access_gate, privacy_cross_context_gate, output_schema_gate, replay_determinism_gate, audit_trace_completeness_gate
- **receipts**: prep_receipt, validation_receipt, attempt_receipt, optional_ptc_receipt, heal_receipt, seal_receipt
- **otel_spans**: l2.e1_prep, l2.e2_validate, l2.e3_execute, l2.e4_heal, l2.e5_seal, l2.handoff_to_exit
- **artifacts**: frozen_execution_context.json, execution_validation_receipt.json, attempt_receipt.json, heal_receipt.json (when applicable), sealed_l2_artifact.json, l2_observability.json
- **fail_closed_if**: authority missing/expired, capability scope exceeded, sandbox escape, policy/registry mismatch, egress without certification, schema violation, replay non-deterministic, audit trace incomplete, direct L4 write attempted

**L2 Boundary**: L2 receives authority and cannot create authority. L2 may execute exactly the bounded work order. L2 may emit proposed_state_diff only. L2 must not choose route, expand workflow, retrieve opportunistically, ask humans directly, approve egress, commit L4, or learn.

---

## W3.P2: E1-E5 Sub-Sections

### E1 Prep — Frozen Execution Room
| Element | Details |
|---------|---------|
| **Freezes** | route, step, capability_token, sandbox_envelope, policy_hash, blueprint_hash, registry_digest_set, provider/model/tool lanes, filesystem/network/credential scope, replay_key, attempt_seed, budget, idempotency |
| **Emits** | FrozenExecutionContext, prep_receipt |
| **OTEL Span** | l2.e1_prep |
| **Gate** | tool_model_registry_gate |

### E2 Valid — Work Order Validation
| Element | Details |
|---------|---------|
| **Validates** | signature chain, capability scope, sandbox scope, schema, side-effect class, budget, safety, route match, ACL, provider/tool/model/connector registry status |
| **Emits** | ExecutionValidationReceipt |
| **Blocking** | anything other than PASS_EXECUTE blocks E3 |
| **OTEL Span** | l2.e2_validate |
| **Gates** | tool_argument_gate, external_egress_gate, sandbox_filesystem_shell_gate, memory_access_gate, privacy_cross_context_gate |

### E3 Exec — Execution Attempt Lanes
| Element | Details |
|---------|---------|
| **Executes** | one approved lane: READ_ANALYSIS, MODEL, TOOL, ACTION, ARTIFACT, OPTIONAL_PTC_SANDBOX |
| **Captures** | AttemptReceipt, telemetry, output payload, raw result, errors, proposed_state_diff |
| **PTC** | inside E3 only; same capability, sandbox, policy, blueprint, replay, budget |
| **OTEL Span** | l2.e3_execute |
| **Gates** | output_schema_gate, replay_determinism_gate |

### E4 Heal — Same-Authority Repair
| Element | Details |
|---------|---------|
| **Same-authority** | repairs under bounded authority only |
| **Allowed** | schema repair, output reformat, transient retry, checkpoint resume, deterministic trim |
| **Disallowed** | missing authority, blocked ACL, policy conflict, route mismatch, stale policy/registry, sandbox gap, HITL need, provider/tool substitution, direct write bypass |
| **Emits** | HealReceipt |
| **OTEL Span** | l2.e4_heal |

### E5 Seal — Artifact Sealing
| Element | Details |
|---------|---------|
| **Emits** | SealedL2Artifact |
| **Packages** | payload, evidence refs, prompt refs, receipts, telemetry, counters, errors, replay manifest, audit refs, terminal_class, decisive_reason |
| **Invariants** | proposed_state_diff inert; durable_commit_occurred=false |
| **OTEL Span** | l2.e5_seal, l2.handoff_to_exit |
| **Gate** | audit_trace_completeness_gate |

---

## Verification Results

### Command 1: TBD Check
```bash
grep -n "TBD_" docs/reference/contracts/step1/04_L2_REQ_MATRIX.md
```
**Result**: No matches found ✅ (0 remaining of 102)

### Command 2: 00C/G01-G29 Check
```bash
grep -n "00C\|G01\|G02\|...\|G29" docs/reference/contracts/step1/04_L2_REQ_MATRIX.md
```
**Result**: No matches found ✅

### Command 3: Files Changed
Only `04_L2_REQ_MATRIX.md` modified in W3 scope ✅

### Command 4: Markdown/Table Sanity
- Layer Contract Summary table: ✅ Valid
- E1-E5 sub-section tables: ✅ Valid
- REQ matrix table: ✅ Valid (13 data rows + header)
- Table dividers: ✅ 18-column format preserved

---

## Sign-off

| Criterion | Status |
|-----------|--------|
| 04_L2_REQ_MATRIX.md hardened | ✅ |
| E1-E5 sub-sections added | ✅ |
| 102 TBD placeholders replaced | ✅ |
| Zero TBD remaining | ✅ |
| Zero 00C/G01-G29 references | ✅ |
| Layer boundary preserved (L2) | ✅ |
| REQ_ID-first structure preserved | ✅ |
| No new REQ_IDs introduced | ✅ |
| Contract gate terminology used | ✅ |
| 9 contract gates defined | ✅ |
| 11 L5 refs specified | ✅ |
| 6 OTEL spans defined | ✅ |

---

## Next Steps

**🛑 STOP: W3 Complete. W4 NOT started.**

W4 scope (pending explicit approval):
- W4.P1: 05_EXIT_REQ_MATRIX.md hardening
- W4.P2: 00B_L4_UWG_REQ_MATRIX.md hardening
- W4.P3: 06_L6_REQ_MATRIX.md hardening

---

**Receipt Generated**: 2026-05-12  
**W3 Status**: COMPLETE  
**Baseline TBDs**: 102 → 0
