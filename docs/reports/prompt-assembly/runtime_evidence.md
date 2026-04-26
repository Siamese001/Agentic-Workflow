# Prompt Assembly — Runtime Evidence Matrix

Source-of-truth doctrine files:

- **PARENT** — `docs/reference/03_L0_Routing/Prompt Assembly/Prompt_Assembly_detailed.md`
- **PA.0** — `docs/reference/03_L0_Routing/Prompt Assembly/PA.0_Boundary_Check_detailed.md`
- **PA.1** — `docs/reference/03_L0_Routing/Prompt Assembly/PA.1_Load_Resolve_Prompt_BOM_detailed.md`
- **PA.2** — `docs/reference/03_L0_Routing/Prompt Assembly/PA.2_Slot_Composition_detailed.md`
- **PA.3** — `docs/reference/03_L0_Routing/Prompt Assembly/PA.3_Airlock_Security_Pass_detailed.md`
- **PA.4** — `docs/reference/03_L0_Routing/Prompt Assembly/PA.4_Validate_Slot_Contract_detailed.md`
- **PA.5** — `docs/reference/03_L0_Routing/Prompt Assembly/PA.5_Token_Budget_Determinism_detailed.md`
- **PA.6** — `docs/reference/03_L0_Routing/Prompt Assembly/PA.6_Provider_Aware_Rendering_detailed.md`
- **PA.7** — `docs/reference/03_L0_Routing/Prompt Assembly/PA.7_Final_Emit_Compiled_Prompt_Artifact_detailed.md`

Runtime artifacts being verified:

- `agentic_core/prompt_governance/prompt_assembly/assembly_statuses.py`
- `agentic_core/prompt_governance/prompt_assembly/forbidden_outputs.py`
- `agentic_core/prompt_governance/prompt_assembly/doctrine_receipts.py`
- `agentic_core/prompt_governance/prompt_assembly/pipeline.py`

**Tally:** 165 PASS / 0 FAIL (of 165 requirements)

**Generated:** 2026-04-26T18:12:03.609284+00:00

## Category roll-up

| Category | Total | PASS | FAIL |
|---|---:|---:|---:|
| E2E | 4 | 4 | 0 |
| FORBID_RD | 24 | 24 | 0 |
| INVARIANT | 12 | 12 | 0 |
| MUST_EMIT | 58 | 58 | 0 |
| MUST_NOT_FENCE | 11 | 11 | 0 |
| SLOT_MAP | 11 | 11 | 0 |
| STATUS_SET | 45 | 45 | 0 |

## E2E

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | ALL | `E2E::dispatch_allowed` | Pipeline PASS path allows dispatch | **PASS** | `{"dispatch_allowed": true, "doctrine_status": "PA_ARTIFACT_NOT_SIGNED"}` |
| 2 | ALL | `E2E::stages_emitted` | Pipeline emits at least PA.0 and PA.7 receipts | **PASS** | `{"stages_emitted": ["PA.0", "PA.7"], "receipt_count": 2}` |
| 3 | ALL | `E2E::no_forbidden` | No pipeline receipt carries forbidden tokens under decision fields | **PASS** | `{"forbidden_hits": []}` |
| 4 | ALL | `E2E::aggregate_status` | Pipeline aggregate doctrine_status resolves to a PAStatus | **PASS** | `{"aggregate_status": "PA_ARTIFACT_NOT_SIGNED", "result_status": "PA_ARTIFACT_NOT_SIGNED", "match": true}` |

## FORBID_RD

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PARENT | `FORBID_RD::DISP::ABSTAIN` | Forbidden disposition `ABSTAIN` registered | **PASS** | `{"token": "ABSTAIN", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 2 | PARENT | `FORBID_RD::DISP::ALLOW` | Forbidden disposition `ALLOW` registered | **PASS** | `{"token": "ALLOW", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 3 | PARENT | `FORBID_RD::DISP::ALLOW_FINISH` | Forbidden disposition `ALLOW_FINISH` registered | **PASS** | `{"token": "ALLOW_FINISH", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 4 | PARENT | `FORBID_RD::DISP::BLOCK_COMMIT` | Forbidden disposition `BLOCK_COMMIT` registered | **PASS** | `{"token": "BLOCK_COMMIT", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 5 | PARENT | `FORBID_RD::DISP::CLARIFY` | Forbidden disposition `CLARIFY` registered | **PASS** | `{"token": "CLARIFY", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 6 | PARENT | `FORBID_RD::DISP::COMMIT_REQUEST` | Forbidden disposition `COMMIT_REQUEST` registered | **PASS** | `{"token": "COMMIT_REQUEST", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 7 | PARENT | `FORBID_RD::DISP::DENY` | Forbidden disposition `DENY` registered | **PASS** | `{"token": "DENY", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 8 | PARENT | `FORBID_RD::DISP::ESCALATE_HITL` | Forbidden disposition `ESCALATE_HITL` registered | **PASS** | `{"token": "ESCALATE_HITL", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 9 | PARENT | `FORBID_RD::DISP::HEAL` | Forbidden disposition `HEAL` registered | **PASS** | `{"token": "HEAL", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 10 | PARENT | `FORBID_RD::DISP::MARK_DEGRADED` | Forbidden disposition `MARK_DEGRADED` registered | **PASS** | `{"token": "MARK_DEGRADED", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 11 | PARENT | `FORBID_RD::DISP::QUARANTINE` | Forbidden disposition `QUARANTINE` registered | **PASS** | `{"token": "QUARANTINE", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 12 | PARENT | `FORBID_RD::DISP::REDACT` | Forbidden disposition `REDACT` registered | **PASS** | `{"token": "REDACT", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 13 | PARENT | `FORBID_RD::DISP::REROUTE` | Forbidden disposition `REROUTE` registered | **PASS** | `{"token": "REROUTE", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 14 | PARENT | `FORBID_RD::DISP::RETRY` | Forbidden disposition `RETRY` registered | **PASS** | `{"token": "RETRY", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 15 | PARENT | `FORBID_RD::DISP::SAFE_FALLBACK` | Forbidden disposition `SAFE_FALLBACK` registered | **PASS** | `{"token": "SAFE_FALLBACK", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 16 | PARENT | `FORBID_RD::DISP::SHRINK_SCOPE` | Forbidden disposition `SHRINK_SCOPE` registered | **PASS** | `{"token": "SHRINK_SCOPE", "kind": "runtime_disposition", "present_in_FORBIDDEN_DISPOSITIONS": true}` |
| 17 | PARENT | `FORBID_RD::VERB::approve_execution` | Forbidden execution verb `approve_execution` registered | **PASS** | `{"token": "approve_execution", "kind": "execution_verb", "present_in_FORBIDDEN_EXECUTION_VERBS": true}` |
| 18 | PARENT | `FORBID_RD::VERB::approve_output` | Forbidden execution verb `approve_output` registered | **PASS** | `{"token": "approve_output", "kind": "execution_verb", "present_in_FORBIDDEN_EXECUTION_VERBS": true}` |
| 19 | PARENT | `FORBID_RD::VERB::approve_write` | Forbidden execution verb `approve_write` registered | **PASS** | `{"token": "approve_write", "kind": "execution_verb", "present_in_FORBIDDEN_EXECUTION_VERBS": true}` |
| 20 | PARENT | `FORBID_RD::VERB::call_provider` | Forbidden execution verb `call_provider` registered | **PASS** | `{"token": "call_provider", "kind": "execution_verb", "present_in_FORBIDDEN_EXECUTION_VERBS": true}` |
| 21 | PARENT | `FORBID_RD::VERB::execute_tool` | Forbidden execution verb `execute_tool` registered | **PASS** | `{"token": "execute_tool", "kind": "execution_verb", "present_in_FORBIDDEN_EXECUTION_VERBS": true}` |
| 22 | PARENT | `FORBID_RD::VERB::mutate_l4` | Forbidden execution verb `mutate_l4` registered | **PASS** | `{"token": "mutate_l4", "kind": "execution_verb", "present_in_FORBIDDEN_EXECUTION_VERBS": true}` |
| 23 | PARENT | `FORBID_RD::GUARD::raises` | assert_no_forbidden raises when a forbidden token appears under a decision field | **PASS** | `{"payload": {"doctrine_status": "PA_READY", "decision": "ALLOW"}, "raised": true, "exception_message": "PA receipt contains forbidden PA …` |
| 24 | PARENT | `FORBID_RD::GUARD::field_aware` | assert_no_forbidden does NOT flag chunk-level data labels | **PASS** | `{"payload": {"doctrine_status": "PA_SECURITY_PASS", "prompt_like_payload_report": [{"chunk_id": "c1", "disposition": "QUARANTINE"}]}, "ra…` |

## INVARIANT

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PARENT | `INV::PA.I1` | PA.I1 — Prompt Assembly composes only (no retrieve/execute/route/call/write). | **PASS** | `{"forbidden_substrings": ["retrieve", "execute_tool", "call_provider", "approve_write", "mutate_l4"], "callables_matched": []}` |
| 2 | PARENT | `INV::PA.I2` | PA.I2 — PA does not alter C0 evidence (classifier records unchanged across receipt build). | **PASS** | `{"pre_records": [["", "", "PASS"]], "post_records": [["", "", "PASS"]]}` |
| 3 | PARENT | `INV::PA.I3` | PA.I3 — Slot/artifact receipts preserve origin/authority/source/replay refs. | **PASS** | `{"required_refs": ["request_id", "route_id", "plan_id", "policy_hash", "replay_key", "run_id", "trace_id"], "presence_map": {"request_id"…` |
| 4 | PARENT | `INV::PA.I4` | PA.I4 — User text is task intent only (U0 authority=ZERO, rank below mid-tier). | **PASS** | `{"u0_authority_label": "ZERO", "u0_rank": 40}` |
| 5 | PARENT | `INV::PA.I5` | PA.I5 — Retrieved/tool content (C0) is data unless higher authority binds it. | **PASS** | `{"c0": [60, "INFORMATIONAL"], "higher_authority_slots": {"S0": [100, "ABSOLUTE"], "D0": [90, "BINDING"], "I0": [80, "GOVERNED"]}}` |
| 6 | PARENT | `INV::PA.I6` | PA.I6 — Lower-authority slots cannot override higher (rank order preserved). | **PASS** | `{"stack_codes_in_order": ["S0", "D0", "I0", "E0", "C0", "M0", "U0", "Y0", "H0", "R0"], "stack_ranks_in_order": [100, 90, 80, 70, 60, 50, …` |
| 7 | PARENT | `INV::PA.I7` | PA.I7 — Tools and schemas have dedicated provider-native receipt slots. | **PASS** | `{"schema_render_receipt_present": true, "tool_render_receipt_present": true, "provider_field_mapping_receipt_present": true, "receipt_key…` |
| 8 | PARENT | `INV::PA.I8` | PA.I8 — Required content cannot be silently dropped (overflow surfaces PA_BUDGET_OVERFLOW). | **PASS** | `{"doctrine_status_emitted": "PA_BUDGET_OVERFLOW", "expected": "PA_BUDGET_OVERFLOW", "rationale": "Required content overflow surfaces a ga…` |
| 9 | PARENT | `INV::PA.I9` | PA.I9 — Canonical structured-slot bytes drive manifest_hash (receipts present). | **PASS** | `{"pa5_has_canonical_hash_input_manifest": true, "pa7_has_manifest_hash_receipt": true}` |
| 10 | PARENT | `INV::PA.I10` | PA.I10 — Determinism: same inputs produce identical budget outputs. | **PASS** | `{"run1_status": "OK", "run2_status": "OK", "run1_input_tokens": 600, "run2_input_tokens": 600, "run1_can_dispatch": true, "run2_can_dispa…` |
| 11 | PARENT | `INV::PA.I11` | PA.I11 — Emit gap evidence when constraints cannot be preserved. | **PASS** | `{"doctrine_status_emitted": "PA_INPUT_INCOMPLETE", "expected": "PA_INPUT_INCOMPLETE", "rationale": "Missing required input must surface g…` |
| 12 | PARENT | `INV::PA.I12` | PA.I12 — PA.7 handoff is artifact only; carries no runtime disposition tokens. | **PASS** | `{"raised_forbidden": false, "exception_message": "", "receipt_doctrine_status": "PA_L2_HANDOFF_READY"}` |

## MUST_EMIT

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PA.0 | `EMIT::PA.0::stage` | PA.0 receipt emits `stage` | **PASS** | `{"field": "stage", "present_in_receipt": true, "receipt_keys": ["assembly_gap_report", "boundary_status_receipt", "doctrine_status", "pla…` |
| 2 | PA.0 | `EMIT::PA.0::doctrine_status` | PA.0 receipt emits `doctrine_status` | **PASS** | `{"field": "doctrine_status", "present_in_receipt": true, "receipt_keys": ["assembly_gap_report", "boundary_status_receipt", "doctrine_sta…` |
| 3 | PA.0 | `EMIT::PA.0::boundary_status_receipt` | PA.0 receipt emits `boundary_status_receipt` | **PASS** | `{"field": "boundary_status_receipt", "present_in_receipt": true, "receipt_keys": ["assembly_gap_report", "boundary_status_receipt", "doct…` |
| 4 | PA.0 | `EMIT::PA.0::required_input_inventory` | PA.0 receipt emits `required_input_inventory` | **PASS** | `{"field": "required_input_inventory", "present_in_receipt": true, "receipt_keys": ["assembly_gap_report", "boundary_status_receipt", "doc…` |
| 5 | PA.0 | `EMIT::PA.0::upstream_reference_map` | PA.0 receipt emits `upstream_reference_map` | **PASS** | `{"field": "upstream_reference_map", "present_in_receipt": true, "receipt_keys": ["assembly_gap_report", "boundary_status_receipt", "doctr…` |
| 6 | PA.0 | `EMIT::PA.0::assembly_gap_report` | PA.0 receipt emits `assembly_gap_report` | **PASS** | `{"field": "assembly_gap_report", "present_in_receipt": true, "receipt_keys": ["assembly_gap_report", "boundary_status_receipt", "doctrine…` |
| 7 | PA.1 | `EMIT::PA.1::stage` | PA.1 receipt emits `stage` | **PASS** | `{"field": "stage", "present_in_receipt": true, "receipt_keys": ["bom_gap_report", "bom_hash_receipt", "bom_resolution_receipt", "componen…` |
| 8 | PA.1 | `EMIT::PA.1::doctrine_status` | PA.1 receipt emits `doctrine_status` | **PASS** | `{"field": "doctrine_status", "present_in_receipt": true, "receipt_keys": ["bom_gap_report", "bom_hash_receipt", "bom_resolution_receipt",…` |
| 9 | PA.1 | `EMIT::PA.1::bom_resolution_receipt` | PA.1 receipt emits `bom_resolution_receipt` | **PASS** | `{"field": "bom_resolution_receipt", "present_in_receipt": true, "receipt_keys": ["bom_gap_report", "bom_hash_receipt", "bom_resolution_re…` |
| 10 | PA.1 | `EMIT::PA.1::component_inventory` | PA.1 receipt emits `component_inventory` | **PASS** | `{"field": "component_inventory", "present_in_receipt": true, "receipt_keys": ["bom_gap_report", "bom_hash_receipt", "bom_resolution_recei…` |
| 11 | PA.1 | `EMIT::PA.1::component_hash_map` | PA.1 receipt emits `component_hash_map` | **PASS** | `{"field": "component_hash_map", "present_in_receipt": true, "receipt_keys": ["bom_gap_report", "bom_hash_receipt", "bom_resolution_receip…` |
| 12 | PA.1 | `EMIT::PA.1::bom_gap_report` | PA.1 receipt emits `bom_gap_report` | **PASS** | `{"field": "bom_gap_report", "present_in_receipt": true, "receipt_keys": ["bom_gap_report", "bom_hash_receipt", "bom_resolution_receipt", …` |
| 13 | PA.1 | `EMIT::PA.1::bom_hash_receipt` | PA.1 receipt emits `bom_hash_receipt` | **PASS** | `{"field": "bom_hash_receipt", "present_in_receipt": true, "receipt_keys": ["bom_gap_report", "bom_hash_receipt", "bom_resolution_receipt"…` |
| 14 | PA.2 | `EMIT::PA.2::stage` | PA.2 receipt emits `stage` | **PASS** | `{"field": "stage", "present_in_receipt": true, "receipt_keys": ["doctrine_status", "policy_hash", "replay_key", "request_id", "slot_autho…` |
| 15 | PA.2 | `EMIT::PA.2::doctrine_status` | PA.2 receipt emits `doctrine_status` | **PASS** | `{"field": "doctrine_status", "present_in_receipt": true, "receipt_keys": ["doctrine_status", "policy_hash", "replay_key", "request_id", "…` |
| 16 | PA.2 | `EMIT::PA.2::slot_composition_receipt` | PA.2 receipt emits `slot_composition_receipt` | **PASS** | `{"field": "slot_composition_receipt", "present_in_receipt": true, "receipt_keys": ["doctrine_status", "policy_hash", "replay_key", "reque…` |
| 17 | PA.2 | `EMIT::PA.2::slot_authority_map` | PA.2 receipt emits `slot_authority_map` | **PASS** | `{"field": "slot_authority_map", "present_in_receipt": true, "receipt_keys": ["doctrine_status", "policy_hash", "replay_key", "request_id"…` |
| 18 | PA.2 | `EMIT::PA.2::slot_lineage_map` | PA.2 receipt emits `slot_lineage_map` | **PASS** | `{"field": "slot_lineage_map", "present_in_receipt": true, "receipt_keys": ["doctrine_status", "policy_hash", "replay_key", "request_id", …` |
| 19 | PA.2 | `EMIT::PA.2::slot_conflict_map` | PA.2 receipt emits `slot_conflict_map` | **PASS** | `{"field": "slot_conflict_map", "present_in_receipt": true, "receipt_keys": ["doctrine_status", "policy_hash", "replay_key", "request_id",…` |
| 20 | PA.2 | `EMIT::PA.2::structured_slots_hash_receipt` | PA.2 receipt emits `structured_slots_hash_receipt` | **PASS** | `{"field": "structured_slots_hash_receipt", "present_in_receipt": true, "receipt_keys": ["doctrine_status", "policy_hash", "replay_key", "…` |
| 21 | PA.3 | `EMIT::PA.3::stage` | PA.3 receipt emits `stage` | **PASS** | `{"field": "stage", "present_in_receipt": true, "receipt_keys": ["AssemblySecurityPassReceipt", "doctrine_status", "policy_hash", "prompt_…` |
| 22 | PA.3 | `EMIT::PA.3::doctrine_status` | PA.3 receipt emits `doctrine_status` | **PASS** | `{"field": "doctrine_status", "present_in_receipt": true, "receipt_keys": ["AssemblySecurityPassReceipt", "doctrine_status", "policy_hash"…` |
| 23 | PA.3 | `EMIT::PA.3::AssemblySecurityPassReceipt` | PA.3 receipt emits `AssemblySecurityPassReceipt` | **PASS** | `{"field": "AssemblySecurityPassReceipt", "present_in_receipt": true, "receipt_keys": ["AssemblySecurityPassReceipt", "doctrine_status", "…` |
| 24 | PA.3 | `EMIT::PA.3::safe_slot_payload_map` | PA.3 receipt emits `safe_slot_payload_map` | **PASS** | `{"field": "safe_slot_payload_map", "present_in_receipt": true, "receipt_keys": ["AssemblySecurityPassReceipt", "doctrine_status", "policy…` |
| 25 | PA.3 | `EMIT::PA.3::rejected_slot_payload_report` | PA.3 receipt emits `rejected_slot_payload_report` | **PASS** | `{"field": "rejected_slot_payload_report", "present_in_receipt": true, "receipt_keys": ["AssemblySecurityPassReceipt", "doctrine_status", …` |
| 26 | PA.3 | `EMIT::PA.3::prompt_like_payload_report` | PA.3 receipt emits `prompt_like_payload_report` | **PASS** | `{"field": "prompt_like_payload_report", "present_in_receipt": true, "receipt_keys": ["AssemblySecurityPassReceipt", "doctrine_status", "p…` |
| 27 | PA.3 | `EMIT::PA.3::safe_extraction_map` | PA.3 receipt emits `safe_extraction_map` | **PASS** | `{"field": "safe_extraction_map", "present_in_receipt": true, "receipt_keys": ["AssemblySecurityPassReceipt", "doctrine_status", "policy_h…` |
| 28 | PA.3 | `EMIT::PA.3::security_gap_report` | PA.3 receipt emits `security_gap_report` | **PASS** | `{"field": "security_gap_report", "present_in_receipt": true, "receipt_keys": ["AssemblySecurityPassReceipt", "doctrine_status", "policy_h…` |
| 29 | PA.4 | `EMIT::PA.4::stage` | PA.4 receipt emits `stage` | **PASS** | `{"field": "stage", "present_in_receipt": true, "receipt_keys": ["SlotValidationReceipt", "authority_order_receipt", "context_contract_rec…` |
| 30 | PA.4 | `EMIT::PA.4::doctrine_status` | PA.4 receipt emits `doctrine_status` | **PASS** | `{"field": "doctrine_status", "present_in_receipt": true, "receipt_keys": ["SlotValidationReceipt", "authority_order_receipt", "context_co…` |
| 31 | PA.4 | `EMIT::PA.4::SlotValidationReceipt` | PA.4 receipt emits `SlotValidationReceipt` | **PASS** | `{"field": "SlotValidationReceipt", "present_in_receipt": true, "receipt_keys": ["SlotValidationReceipt", "authority_order_receipt", "cont…` |
| 32 | PA.4 | `EMIT::PA.4::validation_gap_report` | PA.4 receipt emits `validation_gap_report` | **PASS** | `{"field": "validation_gap_report", "present_in_receipt": true, "receipt_keys": ["SlotValidationReceipt", "authority_order_receipt", "cont…` |
| 33 | PA.4 | `EMIT::PA.4::authority_order_receipt` | PA.4 receipt emits `authority_order_receipt` | **PASS** | `{"field": "authority_order_receipt", "present_in_receipt": true, "receipt_keys": ["SlotValidationReceipt", "authority_order_receipt", "co…` |
| 34 | PA.4 | `EMIT::PA.4::context_contract_receipt` | PA.4 receipt emits `context_contract_receipt` | **PASS** | `{"field": "context_contract_receipt", "present_in_receipt": true, "receipt_keys": ["SlotValidationReceipt", "authority_order_receipt", "c…` |
| 35 | PA.4 | `EMIT::PA.4::tool_schema_binding_receipt` | PA.4 receipt emits `tool_schema_binding_receipt` | **PASS** | `{"field": "tool_schema_binding_receipt", "present_in_receipt": true, "receipt_keys": ["SlotValidationReceipt", "authority_order_receipt",…` |
| 36 | PA.4 | `EMIT::PA.4::validation_hash_receipt` | PA.4 receipt emits `validation_hash_receipt` | **PASS** | `{"field": "validation_hash_receipt", "present_in_receipt": true, "receipt_keys": ["SlotValidationReceipt", "authority_order_receipt", "co…` |
| 37 | PA.5 | `EMIT::PA.5::stage` | PA.5 receipt emits `stage` | **PASS** | `{"field": "stage", "present_in_receipt": true, "receipt_keys": ["TokenBudgetLedger", "budget_status_receipt", "canonical_hash_input_manif…` |
| 38 | PA.5 | `EMIT::PA.5::doctrine_status` | PA.5 receipt emits `doctrine_status` | **PASS** | `{"field": "doctrine_status", "present_in_receipt": true, "receipt_keys": ["TokenBudgetLedger", "budget_status_receipt", "canonical_hash_i…` |
| 39 | PA.5 | `EMIT::PA.5::TokenBudgetLedger` | PA.5 receipt emits `TokenBudgetLedger` | **PASS** | `{"field": "TokenBudgetLedger", "present_in_receipt": true, "receipt_keys": ["TokenBudgetLedger", "budget_status_receipt", "canonical_hash…` |
| 40 | PA.5 | `EMIT::PA.5::deterministic_trimming_receipt` | PA.5 receipt emits `deterministic_trimming_receipt` | **PASS** | `{"field": "deterministic_trimming_receipt", "present_in_receipt": true, "receipt_keys": ["TokenBudgetLedger", "budget_status_receipt", "c…` |
| 41 | PA.5 | `EMIT::PA.5::stable_prefix_receipt` | PA.5 receipt emits `stable_prefix_receipt` | **PASS** | `{"field": "stable_prefix_receipt", "present_in_receipt": true, "receipt_keys": ["TokenBudgetLedger", "budget_status_receipt", "canonical_…` |
| 42 | PA.5 | `EMIT::PA.5::overflow_gap_report` | PA.5 receipt emits `overflow_gap_report` | **PASS** | `{"field": "overflow_gap_report", "present_in_receipt": true, "receipt_keys": ["TokenBudgetLedger", "budget_status_receipt", "canonical_ha…` |
| 43 | PA.5 | `EMIT::PA.5::canonical_hash_input_manifest` | PA.5 receipt emits `canonical_hash_input_manifest` | **PASS** | `{"field": "canonical_hash_input_manifest", "present_in_receipt": true, "receipt_keys": ["TokenBudgetLedger", "budget_status_receipt", "ca…` |
| 44 | PA.6 | `EMIT::PA.6::stage` | PA.6 receipt emits `stage` | **PASS** | `{"field": "stage", "present_in_receipt": true, "receipt_keys": ["ProviderRenderManifest", "doctrine_status", "policy_hash", "provider_fea…` |
| 45 | PA.6 | `EMIT::PA.6::doctrine_status` | PA.6 receipt emits `doctrine_status` | **PASS** | `{"field": "doctrine_status", "present_in_receipt": true, "receipt_keys": ["ProviderRenderManifest", "doctrine_status", "policy_hash", "pr…` |
| 46 | PA.6 | `EMIT::PA.6::ProviderRenderManifest` | PA.6 receipt emits `ProviderRenderManifest` | **PASS** | `{"field": "ProviderRenderManifest", "present_in_receipt": true, "receipt_keys": ["ProviderRenderManifest", "doctrine_status", "policy_has…` |
| 47 | PA.6 | `EMIT::PA.6::provider_field_mapping_receipt` | PA.6 receipt emits `provider_field_mapping_receipt` | **PASS** | `{"field": "provider_field_mapping_receipt", "present_in_receipt": true, "receipt_keys": ["ProviderRenderManifest", "doctrine_status", "po…` |
| 48 | PA.6 | `EMIT::PA.6::schema_render_receipt` | PA.6 receipt emits `schema_render_receipt` | **PASS** | `{"field": "schema_render_receipt", "present_in_receipt": true, "receipt_keys": ["ProviderRenderManifest", "doctrine_status", "policy_hash…` |
| 49 | PA.6 | `EMIT::PA.6::tool_render_receipt` | PA.6 receipt emits `tool_render_receipt` | **PASS** | `{"field": "tool_render_receipt", "present_in_receipt": true, "receipt_keys": ["ProviderRenderManifest", "doctrine_status", "policy_hash",…` |
| 50 | PA.6 | `EMIT::PA.6::provider_feature_gap_report` | PA.6 receipt emits `provider_feature_gap_report` | **PASS** | `{"field": "provider_feature_gap_report", "present_in_receipt": true, "receipt_keys": ["ProviderRenderManifest", "doctrine_status", "polic…` |
| 51 | PA.7 | `EMIT::PA.7::stage` | PA.7 receipt emits `stage` | **PASS** | `{"field": "stage", "present_in_receipt": true, "receipt_keys": ["CompiledPromptArtifact", "compiled_prompt_artifact_receipt", "doctrine_s…` |
| 52 | PA.7 | `EMIT::PA.7::doctrine_status` | PA.7 receipt emits `doctrine_status` | **PASS** | `{"field": "doctrine_status", "present_in_receipt": true, "receipt_keys": ["CompiledPromptArtifact", "compiled_prompt_artifact_receipt", "…` |
| 53 | PA.7 | `EMIT::PA.7::CompiledPromptArtifact` | PA.7 receipt emits `CompiledPromptArtifact` | **PASS** | `{"field": "CompiledPromptArtifact", "present_in_receipt": true, "receipt_keys": ["CompiledPromptArtifact", "compiled_prompt_artifact_rece…` |
| 54 | PA.7 | `EMIT::PA.7::compiled_prompt_artifact_receipt` | PA.7 receipt emits `compiled_prompt_artifact_receipt` | **PASS** | `{"field": "compiled_prompt_artifact_receipt", "present_in_receipt": true, "receipt_keys": ["CompiledPromptArtifact", "compiled_prompt_art…` |
| 55 | PA.7 | `EMIT::PA.7::manifest_hash_receipt` | PA.7 receipt emits `manifest_hash_receipt` | **PASS** | `{"field": "manifest_hash_receipt", "present_in_receipt": true, "receipt_keys": ["CompiledPromptArtifact", "compiled_prompt_artifact_recei…` |
| 56 | PA.7 | `EMIT::PA.7::hmac_signature_receipt` | PA.7 receipt emits `hmac_signature_receipt` | **PASS** | `{"field": "hmac_signature_receipt", "present_in_receipt": true, "receipt_keys": ["CompiledPromptArtifact", "compiled_prompt_artifact_rece…` |
| 57 | PA.7 | `EMIT::PA.7::l2_handoff_envelope` | PA.7 receipt emits `l2_handoff_envelope` | **PASS** | `{"field": "l2_handoff_envelope", "present_in_receipt": true, "receipt_keys": ["CompiledPromptArtifact", "compiled_prompt_artifact_receipt…` |
| 58 | PA.7 | `EMIT::PA.7::final_artifact_gap_report` | PA.7 receipt emits `final_artifact_gap_report` | **PASS** | `{"field": "final_artifact_gap_report", "present_in_receipt": true, "receipt_keys": ["CompiledPromptArtifact", "compiled_prompt_artifact_r…` |

## MUST_NOT_FENCE

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PARENT | `FENCE::retrieve_evidence` | No public callable named `*retrieve_evidence*` in prompt_assembly surface | **PASS** | `{"forbidden_substring": "retrieve_evidence", "callable_count_scanned": 46, "matches": []}` |
| 2 | PARENT | `FENCE::call_provider` | No public callable named `*call_provider*` in prompt_assembly surface | **PASS** | `{"forbidden_substring": "call_provider", "callable_count_scanned": 46, "matches": []}` |
| 3 | PARENT | `FENCE::execute_tool` | No public callable named `*execute_tool*` in prompt_assembly surface | **PASS** | `{"forbidden_substring": "execute_tool", "callable_count_scanned": 46, "matches": []}` |
| 4 | PARENT | `FENCE::approve_output` | No public callable named `*approve_output*` in prompt_assembly surface | **PASS** | `{"forbidden_substring": "approve_output", "callable_count_scanned": 46, "matches": []}` |
| 5 | PARENT | `FENCE::approve_execution` | No public callable named `*approve_execution*` in prompt_assembly surface | **PASS** | `{"forbidden_substring": "approve_execution", "callable_count_scanned": 46, "matches": []}` |
| 6 | PARENT | `FENCE::approve_write` | No public callable named `*approve_write*` in prompt_assembly surface | **PASS** | `{"forbidden_substring": "approve_write", "callable_count_scanned": 46, "matches": []}` |
| 7 | PARENT | `FENCE::mutate_l4` | No public callable named `*mutate_l4*` in prompt_assembly surface | **PASS** | `{"forbidden_substring": "mutate_l4", "callable_count_scanned": 46, "matches": []}` |
| 8 | PARENT | `FENCE::commit_state` | No public callable named `*commit_state*` in prompt_assembly surface | **PASS** | `{"forbidden_substring": "commit_state", "callable_count_scanned": 46, "matches": []}` |
| 9 | PARENT | `FENCE::route_request` | No public callable named `*route_request*` in prompt_assembly surface | **PASS** | `{"forbidden_substring": "route_request", "callable_count_scanned": 46, "matches": []}` |
| 10 | PARENT | `FENCE::reroute` | No public callable named `*reroute*` in prompt_assembly surface | **PASS** | `{"forbidden_substring": "reroute", "callable_count_scanned": 46, "matches": []}` |
| 11 | PARENT | `FENCE::SURFACE_INVENTORY` | Public callables in prompt_assembly surface (informational) | **PASS** | `{"public_callables": ["aggregate_doctrine_status", "assert_no_forbidden", "boundary_check", "build_budget_report", "build_dispatch_outcom…` |

## SLOT_MAP

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PA.2 | `SLOT::S0` | Canonical slot `S0` (auth=ABSOLUTE, rank=100) constructs cleanly | **PASS** | `{"slot": "S0", "rank": 100, "doctrine_label": "ABSOLUTE", "constructed_code": "S0", "constructed_rank": 100}` |
| 2 | PA.2 | `SLOT::D0` | Canonical slot `D0` (auth=BINDING, rank=90) constructs cleanly | **PASS** | `{"slot": "D0", "rank": 90, "doctrine_label": "BINDING", "constructed_code": "D0", "constructed_rank": 90}` |
| 3 | PA.2 | `SLOT::I0` | Canonical slot `I0` (auth=GOVERNED, rank=80) constructs cleanly | **PASS** | `{"slot": "I0", "rank": 80, "doctrine_label": "GOVERNED", "constructed_code": "I0", "constructed_rank": 80}` |
| 4 | PA.2 | `SLOT::E0` | Canonical slot `E0` (auth=GUIDING, rank=70) constructs cleanly | **PASS** | `{"slot": "E0", "rank": 70, "doctrine_label": "GUIDING", "constructed_code": "E0", "constructed_rank": 70}` |
| 5 | PA.2 | `SLOT::C0` | Canonical slot `C0` (auth=INFORMATIONAL, rank=60) constructs cleanly | **PASS** | `{"slot": "C0", "rank": 60, "doctrine_label": "INFORMATIONAL", "constructed_code": "C0", "constructed_rank": 60}` |
| 6 | PA.2 | `SLOT::M0` | Canonical slot `M0` (auth=PRIVATE, rank=50) constructs cleanly | **PASS** | `{"slot": "M0", "rank": 50, "doctrine_label": "PRIVATE", "constructed_code": "M0", "constructed_rank": 50}` |
| 7 | PA.2 | `SLOT::U0` | Canonical slot `U0` (auth=ZERO, rank=40) constructs cleanly | **PASS** | `{"slot": "U0", "rank": 40, "doctrine_label": "ZERO", "constructed_code": "U0", "constructed_rank": 40}` |
| 8 | PA.2 | `SLOT::Y0` | Canonical slot `Y0` (auth=ANALYTIC, rank=30) constructs cleanly | **PASS** | `{"slot": "Y0", "rank": 30, "doctrine_label": "ANALYTIC", "constructed_code": "Y0", "constructed_rank": 30}` |
| 9 | PA.2 | `SLOT::H0` | Canonical slot `H0` (auth=PROPOSED, rank=20) constructs cleanly | **PASS** | `{"slot": "H0", "rank": 20, "doctrine_label": "PROPOSED", "constructed_code": "H0", "constructed_rank": 20}` |
| 10 | PA.2 | `SLOT::R0` | Canonical slot `R0` (auth=SCHEMA, rank=10) constructs cleanly | **PASS** | `{"slot": "R0", "rank": 10, "doctrine_label": "SCHEMA", "constructed_code": "R0", "constructed_rank": 10}` |
| 11 | PA.2 | `SLOT::AUTHORITY_ORDER` | AuthorityStack preserves doctrine high->low authority order | **PASS** | `{"codes_in_stack_order": ["S0", "D0", "I0", "E0", "C0", "M0", "U0", "Y0", "H0", "R0"], "ranks_in_stack_order": [100, 90, 80, 70, 60, 50, …` |

## STATUS_SET

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PA.0 | `STATUS::PA.0::PA_READY` | PA.0 doctrine status `PA_READY` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_READY", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_READY"}` |
| 2 | PA.0 | `STATUS::PA.0::PA_INPUT_INCOMPLETE` | PA.0 doctrine status `PA_INPUT_INCOMPLETE` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_INPUT_INCOMPLETE", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_INPUT_INCOMPLETE"}` |
| 3 | PA.0 | `STATUS::PA.0::PA_BOUNDARY_MISMATCH` | PA.0 doctrine status `PA_BOUNDARY_MISMATCH` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_BOUNDARY_MISMATCH", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_BOUNDARY_MISMATCH"}` |
| 4 | PA.0 | `STATUS::PA.0::PA_REQUIRES_UPSTREAM_REPAIR` | PA.0 doctrine status `PA_REQUIRES_UPSTREAM_REPAIR` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_REQUIRES_UPSTREAM_REPAIR", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_REQUIRES_UPSTREAM_REPAIR"}` |
| 5 | PA.1 | `STATUS::PA.1::PA_BOM_RESOLVED` | PA.1 doctrine status `PA_BOM_RESOLVED` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_BOM_RESOLVED", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_BOM_RESOLVED"}` |
| 6 | PA.1 | `STATUS::PA.1::PA_BOM_GAP` | PA.1 doctrine status `PA_BOM_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_BOM_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_BOM_GAP"}` |
| 7 | PA.1 | `STATUS::PA.1::PA_REQUIRES_UPSTREAM_REPAIR` | PA.1 doctrine status `PA_REQUIRES_UPSTREAM_REPAIR` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_REQUIRES_UPSTREAM_REPAIR", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_REQUIRES_UPSTREAM_REPAIR"}` |
| 8 | PA.2 | `STATUS::PA.2::PA_SLOTS_COMPOSED` | PA.2 doctrine status `PA_SLOTS_COMPOSED` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_SLOTS_COMPOSED", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_SLOTS_COMPOSED"}` |
| 9 | PA.2 | `STATUS::PA.2::PA_SLOT_COMPOSITION_GAP` | PA.2 doctrine status `PA_SLOT_COMPOSITION_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_SLOT_COMPOSITION_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_SLOT_COMPOSITION_GAP"}` |
| 10 | PA.2 | `STATUS::PA.2::PA_AUTHORITY_CONFLICT` | PA.2 doctrine status `PA_AUTHORITY_CONFLICT` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_AUTHORITY_CONFLICT", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_AUTHORITY_CONFLICT"}` |
| 11 | PA.3 | `STATUS::PA.3::PA_SECURITY_PASS` | PA.3 doctrine status `PA_SECURITY_PASS` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_SECURITY_PASS", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_SECURITY_PASS"}` |
| 12 | PA.3 | `STATUS::PA.3::PA_SECURITY_GAP` | PA.3 doctrine status `PA_SECURITY_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_SECURITY_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_SECURITY_GAP"}` |
| 13 | PA.3 | `STATUS::PA.3::PA_SAFE_EXTRACTION_PARTIAL` | PA.3 doctrine status `PA_SAFE_EXTRACTION_PARTIAL` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_SAFE_EXTRACTION_PARTIAL", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_SAFE_EXTRACTION_PARTIAL"}` |
| 14 | PA.3 | `STATUS::PA.3::PA_SLOT_PAYLOAD_REJECTED` | PA.3 doctrine status `PA_SLOT_PAYLOAD_REJECTED` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_SLOT_PAYLOAD_REJECTED", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_SLOT_PAYLOAD_REJECTED"}` |
| 15 | PA.3 | `STATUS::PA.3::PA_REQUIRES_UPSTREAM_REPAIR` | PA.3 doctrine status `PA_REQUIRES_UPSTREAM_REPAIR` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_REQUIRES_UPSTREAM_REPAIR", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_REQUIRES_UPSTREAM_REPAIR"}` |
| 16 | PA.4 | `STATUS::PA.4::PA_SLOT_CONTRACT_VALID` | PA.4 doctrine status `PA_SLOT_CONTRACT_VALID` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_SLOT_CONTRACT_VALID", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_SLOT_CONTRACT_VALID"}` |
| 17 | PA.4 | `STATUS::PA.4::PA_SLOT_CONTRACT_INVALID` | PA.4 doctrine status `PA_SLOT_CONTRACT_INVALID` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_SLOT_CONTRACT_INVALID", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_SLOT_CONTRACT_INVALID"}` |
| 18 | PA.4 | `STATUS::PA.4::PA_CONTEXT_CONTRACT_GAP` | PA.4 doctrine status `PA_CONTEXT_CONTRACT_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_CONTEXT_CONTRACT_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_CONTEXT_CONTRACT_GAP"}` |
| 19 | PA.4 | `STATUS::PA.4::PA_AUTHORITY_INVERSION_GAP` | PA.4 doctrine status `PA_AUTHORITY_INVERSION_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_AUTHORITY_INVERSION_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_AUTHORITY_INVERSION_GAP"}` |
| 20 | PA.4 | `STATUS::PA.4::PA_SCHEMA_BINDING_GAP` | PA.4 doctrine status `PA_SCHEMA_BINDING_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_SCHEMA_BINDING_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_SCHEMA_BINDING_GAP"}` |
| 21 | PA.4 | `STATUS::PA.4::PA_TOOL_BINDING_GAP` | PA.4 doctrine status `PA_TOOL_BINDING_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_TOOL_BINDING_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_TOOL_BINDING_GAP"}` |
| 22 | PA.5 | `STATUS::PA.5::PA_BUDGET_FIT` | PA.5 doctrine status `PA_BUDGET_FIT` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_BUDGET_FIT", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_BUDGET_FIT"}` |
| 23 | PA.5 | `STATUS::PA.5::PA_BUDGET_TRIMMED` | PA.5 doctrine status `PA_BUDGET_TRIMMED` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_BUDGET_TRIMMED", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_BUDGET_TRIMMED"}` |
| 24 | PA.5 | `STATUS::PA.5::PA_BUDGET_OVERFLOW` | PA.5 doctrine status `PA_BUDGET_OVERFLOW` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_BUDGET_OVERFLOW", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_BUDGET_OVERFLOW"}` |
| 25 | PA.5 | `STATUS::PA.5::PA_REQUIRES_UPSTREAM_REPAIR` | PA.5 doctrine status `PA_REQUIRES_UPSTREAM_REPAIR` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_REQUIRES_UPSTREAM_REPAIR", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_REQUIRES_UPSTREAM_REPAIR"}` |
| 26 | PA.6 | `STATUS::PA.6::PA_RENDERED` | PA.6 doctrine status `PA_RENDERED` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_RENDERED", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_RENDERED"}` |
| 27 | PA.6 | `STATUS::PA.6::PA_RENDER_GAP` | PA.6 doctrine status `PA_RENDER_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_RENDER_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_RENDER_GAP"}` |
| 28 | PA.6 | `STATUS::PA.6::PA_PROVIDER_FEATURE_GAP` | PA.6 doctrine status `PA_PROVIDER_FEATURE_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_PROVIDER_FEATURE_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_PROVIDER_FEATURE_GAP"}` |
| 29 | PA.6 | `STATUS::PA.6::PA_SCHEMA_RENDER_GAP` | PA.6 doctrine status `PA_SCHEMA_RENDER_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_SCHEMA_RENDER_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_SCHEMA_RENDER_GAP"}` |
| 30 | PA.6 | `STATUS::PA.6::PA_TOOL_RENDER_GAP` | PA.6 doctrine status `PA_TOOL_RENDER_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_TOOL_RENDER_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_TOOL_RENDER_GAP"}` |
| 31 | PA.7 | `STATUS::PA.7::PA_ARTIFACT_SIGNED` | PA.7 doctrine status `PA_ARTIFACT_SIGNED` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_ARTIFACT_SIGNED", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_ARTIFACT_SIGNED"}` |
| 32 | PA.7 | `STATUS::PA.7::PA_ARTIFACT_NOT_SIGNED` | PA.7 doctrine status `PA_ARTIFACT_NOT_SIGNED` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_ARTIFACT_NOT_SIGNED", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_ARTIFACT_NOT_SIGNED"}` |
| 33 | PA.7 | `STATUS::PA.7::PA_SIGNATURE_GAP` | PA.7 doctrine status `PA_SIGNATURE_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_SIGNATURE_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_SIGNATURE_GAP"}` |
| 34 | PA.7 | `STATUS::PA.7::PA_MANIFEST_HASH_GAP` | PA.7 doctrine status `PA_MANIFEST_HASH_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_MANIFEST_HASH_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_MANIFEST_HASH_GAP"}` |
| 35 | PA.7 | `STATUS::PA.7::PA_L2_HANDOFF_READY` | PA.7 doctrine status `PA_L2_HANDOFF_READY` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_L2_HANDOFF_READY", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_L2_HANDOFF_READY"}` |
| 36 | PA.7 | `STATUS::PA.7::PA_L2_HANDOFF_GAP` | PA.7 doctrine status `PA_L2_HANDOFF_GAP` exists in PAStatus | **PASS** | `{"doctrine_value": "PA_L2_HANDOFF_GAP", "resolves_to_PAStatus": true, "PAStatus_member_value": "PA_L2_HANDOFF_GAP"}` |
| 37 | PA.0 | `PARTITION::PA.0` | PA.0 STAGE_TO_STATUSES contains every doctrine status | **PASS** | `{"doctrine_count": 4, "runtime_count": 4, "missing_in_runtime": [], "extra_in_runtime": []}` |
| 38 | PA.1 | `PARTITION::PA.1` | PA.1 STAGE_TO_STATUSES contains every doctrine status | **PASS** | `{"doctrine_count": 3, "runtime_count": 3, "missing_in_runtime": [], "extra_in_runtime": []}` |
| 39 | PA.2 | `PARTITION::PA.2` | PA.2 STAGE_TO_STATUSES contains every doctrine status | **PASS** | `{"doctrine_count": 3, "runtime_count": 3, "missing_in_runtime": [], "extra_in_runtime": []}` |
| 40 | PA.3 | `PARTITION::PA.3` | PA.3 STAGE_TO_STATUSES contains every doctrine status | **PASS** | `{"doctrine_count": 5, "runtime_count": 5, "missing_in_runtime": [], "extra_in_runtime": []}` |
| 41 | PA.4 | `PARTITION::PA.4` | PA.4 STAGE_TO_STATUSES contains every doctrine status | **PASS** | `{"doctrine_count": 6, "runtime_count": 6, "missing_in_runtime": [], "extra_in_runtime": []}` |
| 42 | PA.5 | `PARTITION::PA.5` | PA.5 STAGE_TO_STATUSES contains every doctrine status | **PASS** | `{"doctrine_count": 4, "runtime_count": 4, "missing_in_runtime": [], "extra_in_runtime": []}` |
| 43 | PA.6 | `PARTITION::PA.6` | PA.6 STAGE_TO_STATUSES contains every doctrine status | **PASS** | `{"doctrine_count": 5, "runtime_count": 5, "missing_in_runtime": [], "extra_in_runtime": []}` |
| 44 | PA.7 | `PARTITION::PA.7` | PA.7 STAGE_TO_STATUSES contains every doctrine status | **PASS** | `{"doctrine_count": 6, "runtime_count": 6, "missing_in_runtime": [], "extra_in_runtime": []}` |
| 45 | ALL | `STATUS::CLOSURE` | Doctrine status union is a subset of runtime PAStatus | **PASS** | `{"doctrine_union_size": 33, "runtime_pastatus_size": 33, "missing": []}` |

