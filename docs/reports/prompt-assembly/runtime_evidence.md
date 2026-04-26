# Prompt Assembly — Runtime Evidence Matrix

Source-of-truth doctrine files:

- **PARENT** — `docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/Prompt_Assembly_detailed.md`
- **PA.0** — `docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.0_Boundary_Check_detailed.md`
- **PA.1** — `docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.1_Load_Resolve_Prompt_BOM_detailed.md`
- **PA.2** — `docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.2_Slot_Composition_detailed.md`
- **PA.3** — `docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.3_Airlock_Security_Pass_detailed.md`
- **PA.4** — `docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.4_Validate_Slot_Contract_detailed.md`
- **PA.5** — `docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.5_Token_Budget_Determinism_detailed.md`
- **PA.6** — `docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.6_Provider_Aware_Rendering_detailed.md`
- **PA.7** — `docs/reference/03_L0_Routing_&_L3_Orch/Prompt Assembly/PA.7_Final_Emit_Compiled_Prompt_Artifact_detailed.md`

Runtime artifacts being verified:

- `agentic_core/prompt_governance/prompt_assembly/assembly_statuses.py`
- `agentic_core/prompt_governance/prompt_assembly/forbidden_outputs.py`
- `agentic_core/prompt_governance/prompt_assembly/doctrine_receipts.py`
- `agentic_core/prompt_governance/prompt_assembly/pipeline.py`

**Tally:** 240 PASS / 0 FAIL (of 240 requirements)

**Generated:** 2026-04-26T18:42:20.988111+00:00

## Category roll-up

| Category | Total | PASS | FAIL |
|---|---:|---:|---:|
| AGGREGATION | 5 | 5 | 0 |
| DETERMINISM | 8 | 8 | 0 |
| DOCTRINE_DRIFT | 16 | 16 | 0 |
| E2E | 4 | 4 | 0 |
| FORBID_DEEP | 5 | 5 | 0 |
| FORBID_FALSE_POSITIVE | 5 | 5 | 0 |
| FORBID_RD | 24 | 24 | 0 |
| INVARIANT | 12 | 12 | 0 |
| MUST_EMIT | 48 | 48 | 0 |
| MUST_NOT_FENCE | 11 | 11 | 0 |
| NEGATIVE_PATH | 36 | 36 | 0 |
| PARSER_ROBUSTNESS | 5 | 5 | 0 |
| PIPELINE_NEG | 3 | 3 | 0 |
| SLOT_MAP | 11 | 11 | 0 |
| STATUS_PARTITION_COMPLETE | 2 | 2 | 0 |
| STATUS_SET | 45 | 45 | 0 |

## AGGREGATION

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PARENT | `AGG::empty` | Empty receipt list aggregates to PA_READY (neutral) | **PASS** | `{"input": [], "result": "PA_READY"}` |
| 2 | PARENT | `AGG::single` | Single-receipt input round-trips through aggregator | **PASS** | `{"result": "PA_BUDGET_OVERFLOW"}` |
| 3 | PARENT | `AGG::all_ready` | All-PA_READY receipt list aggregates to PA_READY | **PASS** | `{"result": "PA_READY"}` |
| 4 | PARENT | `AGG::worst_wins` | Mixed-status input does NOT aggregate to PA_READY | **PASS** | `{"result": "PA_BUDGET_OVERFLOW", "non_ready": true}` |
| 5 | PARENT | `AGG::deterministic` | Aggregator is deterministic on identical input | **PASS** | `{"first": "PA_BUDGET_TRIMMED", "second": "PA_BUDGET_TRIMMED"}` |

## DETERMINISM

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PA.0 | `DET::PA.0` | PA.0 receipt builder is byte-deterministic | **PASS** | `{"stage": "PA.0", "first_byte_count": 804, "second_byte_count": 804, "byte_identical": true, "first_keys": ["assembly_gap_report", "bound…` |
| 2 | PA.1 | `DET::PA.1` | PA.1 receipt builder is byte-deterministic | **PASS** | `{"stage": "PA.1", "first_byte_count": 449, "second_byte_count": 449, "byte_identical": true, "first_keys": ["bom_gap_report", "bom_hash_r…` |
| 3 | PA.2 | `DET::PA.2` | PA.2 receipt builder is byte-deterministic | **PASS** | `{"stage": "PA.2", "first_byte_count": 696, "second_byte_count": 696, "byte_identical": true, "first_keys": ["doctrine_status", "policy_ha…` |
| 4 | PA.3 | `DET::PA.3` | PA.3 receipt builder is byte-deterministic | **PASS** | `{"stage": "PA.3", "first_byte_count": 691, "second_byte_count": 691, "byte_identical": true, "first_keys": ["AssemblySecurityPassReceipt"…` |
| 5 | PA.4 | `DET::PA.4` | PA.4 receipt builder is byte-deterministic | **PASS** | `{"stage": "PA.4", "first_byte_count": 630, "second_byte_count": 630, "byte_identical": true, "first_keys": ["SlotValidationReceipt", "aut…` |
| 6 | PA.5 | `DET::PA.5` | PA.5 receipt builder is byte-deterministic | **PASS** | `{"stage": "PA.5", "first_byte_count": 691, "second_byte_count": 691, "byte_identical": true, "first_keys": ["TokenBudgetLedger", "budget_…` |
| 7 | PA.6 | `DET::PA.6` | PA.6 receipt builder is byte-deterministic | **PASS** | `{"stage": "PA.6", "first_byte_count": 549, "second_byte_count": 549, "byte_identical": true, "first_keys": ["ProviderRenderManifest", "do…` |
| 8 | PA.7 | `DET::PA.7` | PA.7 receipt builder is byte-deterministic | **PASS** | `{"stage": "PA.7", "first_byte_count": 808, "second_byte_count": 808, "byte_identical": true, "first_keys": ["CompiledPromptArtifact", "co…` |

## DOCTRINE_DRIFT

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PA.0 | `DRIFT::PA.0::doctrine_resolves` | PA.0 doctrine STATUS VALUES all resolve to PAStatus members | **PASS** | `{"stage_doctrine_count": 4, "stage_runtime_count": 4, "only_in_doctrine": [], "only_in_runtime": []}` |
| 2 | PA.0 | `DRIFT::PA.0::runtime_grounded` | PA.0 STAGE_TO_STATUSES contains every doctrine status from .md | **PASS** | `{"stage_doctrine_count": 4, "stage_runtime_count": 4, "only_in_doctrine": [], "only_in_runtime": []}` |
| 3 | PA.1 | `DRIFT::PA.1::doctrine_resolves` | PA.1 doctrine STATUS VALUES all resolve to PAStatus members | **PASS** | `{"stage_doctrine_count": 3, "stage_runtime_count": 3, "only_in_doctrine": [], "only_in_runtime": []}` |
| 4 | PA.1 | `DRIFT::PA.1::runtime_grounded` | PA.1 STAGE_TO_STATUSES contains every doctrine status from .md | **PASS** | `{"stage_doctrine_count": 3, "stage_runtime_count": 3, "only_in_doctrine": [], "only_in_runtime": []}` |
| 5 | PA.2 | `DRIFT::PA.2::doctrine_resolves` | PA.2 doctrine STATUS VALUES all resolve to PAStatus members | **PASS** | `{"stage_doctrine_count": 3, "stage_runtime_count": 3, "only_in_doctrine": [], "only_in_runtime": []}` |
| 6 | PA.2 | `DRIFT::PA.2::runtime_grounded` | PA.2 STAGE_TO_STATUSES contains every doctrine status from .md | **PASS** | `{"stage_doctrine_count": 3, "stage_runtime_count": 3, "only_in_doctrine": [], "only_in_runtime": []}` |
| 7 | PA.3 | `DRIFT::PA.3::doctrine_resolves` | PA.3 doctrine STATUS VALUES all resolve to PAStatus members | **PASS** | `{"stage_doctrine_count": 5, "stage_runtime_count": 5, "only_in_doctrine": [], "only_in_runtime": []}` |
| 8 | PA.3 | `DRIFT::PA.3::runtime_grounded` | PA.3 STAGE_TO_STATUSES contains every doctrine status from .md | **PASS** | `{"stage_doctrine_count": 5, "stage_runtime_count": 5, "only_in_doctrine": [], "only_in_runtime": []}` |
| 9 | PA.4 | `DRIFT::PA.4::doctrine_resolves` | PA.4 doctrine STATUS VALUES all resolve to PAStatus members | **PASS** | `{"stage_doctrine_count": 6, "stage_runtime_count": 6, "only_in_doctrine": [], "only_in_runtime": []}` |
| 10 | PA.4 | `DRIFT::PA.4::runtime_grounded` | PA.4 STAGE_TO_STATUSES contains every doctrine status from .md | **PASS** | `{"stage_doctrine_count": 6, "stage_runtime_count": 6, "only_in_doctrine": [], "only_in_runtime": []}` |
| 11 | PA.5 | `DRIFT::PA.5::doctrine_resolves` | PA.5 doctrine STATUS VALUES all resolve to PAStatus members | **PASS** | `{"stage_doctrine_count": 4, "stage_runtime_count": 4, "only_in_doctrine": [], "only_in_runtime": []}` |
| 12 | PA.5 | `DRIFT::PA.5::runtime_grounded` | PA.5 STAGE_TO_STATUSES contains every doctrine status from .md | **PASS** | `{"stage_doctrine_count": 4, "stage_runtime_count": 4, "only_in_doctrine": [], "only_in_runtime": []}` |
| 13 | PA.6 | `DRIFT::PA.6::doctrine_resolves` | PA.6 doctrine STATUS VALUES all resolve to PAStatus members | **PASS** | `{"stage_doctrine_count": 5, "stage_runtime_count": 5, "only_in_doctrine": [], "only_in_runtime": []}` |
| 14 | PA.6 | `DRIFT::PA.6::runtime_grounded` | PA.6 STAGE_TO_STATUSES contains every doctrine status from .md | **PASS** | `{"stage_doctrine_count": 5, "stage_runtime_count": 5, "only_in_doctrine": [], "only_in_runtime": []}` |
| 15 | PA.7 | `DRIFT::PA.7::doctrine_resolves` | PA.7 doctrine STATUS VALUES all resolve to PAStatus members | **PASS** | `{"stage_doctrine_count": 6, "stage_runtime_count": 6, "only_in_doctrine": [], "only_in_runtime": []}` |
| 16 | PA.7 | `DRIFT::PA.7::runtime_grounded` | PA.7 STAGE_TO_STATUSES contains every doctrine status from .md | **PASS** | `{"stage_doctrine_count": 6, "stage_runtime_count": 6, "only_in_doctrine": [], "only_in_runtime": []}` |

## E2E

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | ALL | `E2E::dispatch_allowed` | Pipeline PASS path allows dispatch | **PASS** | `{"dispatch_allowed": true, "doctrine_status": "PA_ARTIFACT_NOT_SIGNED"}` |
| 2 | ALL | `E2E::stages_emitted` | Pipeline emits at least PA.0 and PA.7 receipts | **PASS** | `{"stages_emitted": ["PA.0", "PA.7"], "receipt_count": 2}` |
| 3 | ALL | `E2E::no_forbidden` | No pipeline receipt carries forbidden tokens under decision fields | **PASS** | `{"forbidden_hits": []}` |
| 4 | ALL | `E2E::aggregate_status` | Pipeline aggregate doctrine_status resolves to a PAStatus | **PASS** | `{"aggregate_status": "PA_ARTIFACT_NOT_SIGNED", "result_status": "PA_ARTIFACT_NOT_SIGNED", "match": true}` |

## FORBID_DEEP

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PARENT | `FORBID_DEEP::depth1` | FORBID_DEEP/depth1: Top-level decision field with forbidden token | **PASS** | `{"topology": "depth1", "expected_raise": true, "actually_raised": true, "message": "PA receipt contains forbidden PA output(s): $.decisio…` |
| 2 | PARENT | `FORBID_DEEP::depth2` | FORBID_DEEP/depth2: Forbidden token nested one level deep under decision field | **PASS** | `{"topology": "depth2", "expected_raise": true, "actually_raised": true, "message": "PA receipt contains forbidden PA output(s): $.compile…` |
| 3 | PARENT | `FORBID_DEEP::depth3` | FORBID_DEEP/depth3: Forbidden token nested three levels deep | **PASS** | `{"topology": "depth3", "expected_raise": true, "actually_raised": true, "message": "PA receipt contains forbidden PA output(s): $.wrapper…` |
| 4 | PARENT | `FORBID_DEEP::in_list` | FORBID_DEEP/in_list: Forbidden token inside list of dicts under decision-shaped key | **PASS** | `{"topology": "in_list", "expected_raise": true, "actually_raised": true, "message": "PA receipt contains forbidden PA output(s): $.decisi…` |
| 5 | PARENT | `FORBID_DEEP::list_of_lists` | FORBID_DEEP/list_of_lists: Forbidden token inside doubly-nested list | **PASS** | `{"topology": "list_of_lists", "expected_raise": true, "actually_raised": true, "message": "PA receipt contains forbidden PA output(s): $.…` |

## FORBID_FALSE_POSITIVE

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PARENT | `FORBID_FP::substring_allow` | FORBID_FALSE_POSITIVE/substring_allow: scanner does NOT flag legitimate use | **PASS** | `{"topology": "substring_allow", "expected_raise": false, "actually_raised": false, "message": "", "rationale": "Forbidden tokens must mat…` |
| 2 | PARENT | `FORBID_FP::substring_deny` | FORBID_FALSE_POSITIVE/substring_deny: scanner does NOT flag legitimate use | **PASS** | `{"topology": "substring_deny", "expected_raise": false, "actually_raised": false, "message": "", "rationale": "Forbidden tokens must matc…` |
| 3 | PARENT | `FORBID_FP::chunk_disposition` | FORBID_FALSE_POSITIVE/chunk_disposition: scanner does NOT flag legitimate use | **PASS** | `{"topology": "chunk_disposition", "expected_raise": false, "actually_raised": false, "message": "", "rationale": "Forbidden tokens must m…` |
| 4 | PARENT | `FORBID_FP::chunk_extraction_label` | FORBID_FALSE_POSITIVE/chunk_extraction_label: scanner does NOT flag legitimate use | **PASS** | `{"topology": "chunk_extraction_label", "expected_raise": false, "actually_raised": false, "message": "", "rationale": "Forbidden tokens m…` |
| 5 | PARENT | `FORBID_FP::metadata_string` | FORBID_FALSE_POSITIVE/metadata_string: scanner does NOT flag legitimate use | **PASS** | `{"topology": "metadata_string", "expected_raise": false, "actually_raised": false, "message": "", "rationale": "Forbidden tokens must mat…` |

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
| 1 | PA.0 | `EMIT::PA.0::PAAssemblyInput` | PA.0 receipt emits doctrine output `PAAssemblyInput` | **PASS** | `{"doctrine_field": "PAAssemblyInput", "present_in_receipt": true, "match_kind": "alias", "matched_via_aliases": ["required_input_inventor…` |
| 2 | PA.0 | `EMIT::PA.0::BoundaryCheckReceipt` | PA.0 receipt emits doctrine output `BoundaryCheckReceipt` | **PASS** | `{"doctrine_field": "BoundaryCheckReceipt", "present_in_receipt": true, "match_kind": "alias", "matched_via_aliases": ["boundary_status_re…` |
| 3 | PA.0 | `EMIT::PA.0::required_input_inventory` | PA.0 receipt emits doctrine output `required_input_inventory` | **PASS** | `{"doctrine_field": "required_input_inventory", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_ke…` |
| 4 | PA.0 | `EMIT::PA.0::upstream_reference_map` | PA.0 receipt emits doctrine output `upstream_reference_map` | **PASS** | `{"doctrine_field": "upstream_reference_map", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys…` |
| 5 | PA.0 | `EMIT::PA.0::assembly_gap_report` | PA.0 receipt emits doctrine output `assembly_gap_report` | **PASS** | `{"doctrine_field": "assembly_gap_report", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": …` |
| 6 | PA.0 | `EMIT::PA.0::boundary_status_receipt` | PA.0 receipt emits doctrine output `boundary_status_receipt` | **PASS** | `{"doctrine_field": "boundary_status_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_key…` |
| 7 | PA.1 | `EMIT::PA.1::PromptBOM` | PA.1 receipt emits doctrine output `PromptBOM` | **PASS** | `{"doctrine_field": "PromptBOM", "present_in_receipt": true, "match_kind": "alias", "matched_via_aliases": ["component_hash_map", "compone…` |
| 8 | PA.1 | `EMIT::PA.1::bom_resolution_receipt` | PA.1 receipt emits doctrine output `bom_resolution_receipt` | **PASS** | `{"doctrine_field": "bom_resolution_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys…` |
| 9 | PA.1 | `EMIT::PA.1::component_inventory` | PA.1 receipt emits doctrine output `component_inventory` | **PASS** | `{"doctrine_field": "component_inventory", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": …` |
| 10 | PA.1 | `EMIT::PA.1::component_hash_map` | PA.1 receipt emits doctrine output `component_hash_map` | **PASS** | `{"doctrine_field": "component_hash_map", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": […` |
| 11 | PA.1 | `EMIT::PA.1::bom_gap_report` | PA.1 receipt emits doctrine output `bom_gap_report` | **PASS** | `{"doctrine_field": "bom_gap_report", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": ["bom…` |
| 12 | PA.1 | `EMIT::PA.1::bom_hash_receipt` | PA.1 receipt emits doctrine output `bom_hash_receipt` | **PASS** | `{"doctrine_field": "bom_hash_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": ["b…` |
| 13 | PA.2 | `EMIT::PA.2::StructuredPromptSlots` | PA.2 receipt emits doctrine output `StructuredPromptSlots` | **PASS** | `{"doctrine_field": "StructuredPromptSlots", "present_in_receipt": true, "match_kind": "alias", "matched_via_aliases": ["slot_authority_ma…` |
| 14 | PA.2 | `EMIT::PA.2::slot_composition_receipt` | PA.2 receipt emits doctrine output `slot_composition_receipt` | **PASS** | `{"doctrine_field": "slot_composition_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_ke…` |
| 15 | PA.2 | `EMIT::PA.2::slot_authority_map` | PA.2 receipt emits doctrine output `slot_authority_map` | **PASS** | `{"doctrine_field": "slot_authority_map", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": […` |
| 16 | PA.2 | `EMIT::PA.2::slot_lineage_map` | PA.2 receipt emits doctrine output `slot_lineage_map` | **PASS** | `{"doctrine_field": "slot_lineage_map", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": ["d…` |
| 17 | PA.2 | `EMIT::PA.2::slot_conflict_map` | PA.2 receipt emits doctrine output `slot_conflict_map` | **PASS** | `{"doctrine_field": "slot_conflict_map", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": ["…` |
| 18 | PA.2 | `EMIT::PA.2::structured_slots_hash_receipt` | PA.2 receipt emits doctrine output `structured_slots_hash_receipt` | **PASS** | `{"doctrine_field": "structured_slots_hash_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "recei…` |
| 19 | PA.3 | `EMIT::PA.3::AssemblySecurityPassReceipt` | PA.3 receipt emits doctrine output `AssemblySecurityPassReceipt` | **PASS** | `{"doctrine_field": "AssemblySecurityPassReceipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt…` |
| 20 | PA.3 | `EMIT::PA.3::safe_slot_payload_map` | PA.3 receipt emits doctrine output `safe_slot_payload_map` | **PASS** | `{"doctrine_field": "safe_slot_payload_map", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys"…` |
| 21 | PA.3 | `EMIT::PA.3::rejected_slot_payload_report` | PA.3 receipt emits doctrine output `rejected_slot_payload_report` | **PASS** | `{"doctrine_field": "rejected_slot_payload_report", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receip…` |
| 22 | PA.3 | `EMIT::PA.3::prompt_like_payload_report` | PA.3 receipt emits doctrine output `prompt_like_payload_report` | **PASS** | `{"doctrine_field": "prompt_like_payload_report", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_…` |
| 23 | PA.3 | `EMIT::PA.3::safe_extraction_map` | PA.3 receipt emits doctrine output `safe_extraction_map` | **PASS** | `{"doctrine_field": "safe_extraction_map", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": …` |
| 24 | PA.3 | `EMIT::PA.3::security_gap_report` | PA.3 receipt emits doctrine output `security_gap_report` | **PASS** | `{"doctrine_field": "security_gap_report", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": …` |
| 25 | PA.4 | `EMIT::PA.4::SlotValidationReceipt` | PA.4 receipt emits doctrine output `SlotValidationReceipt` | **PASS** | `{"doctrine_field": "SlotValidationReceipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys"…` |
| 26 | PA.4 | `EMIT::PA.4::validation_gap_report` | PA.4 receipt emits doctrine output `validation_gap_report` | **PASS** | `{"doctrine_field": "validation_gap_report", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys"…` |
| 27 | PA.4 | `EMIT::PA.4::authority_order_receipt` | PA.4 receipt emits doctrine output `authority_order_receipt` | **PASS** | `{"doctrine_field": "authority_order_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_key…` |
| 28 | PA.4 | `EMIT::PA.4::context_contract_receipt` | PA.4 receipt emits doctrine output `context_contract_receipt` | **PASS** | `{"doctrine_field": "context_contract_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_ke…` |
| 29 | PA.4 | `EMIT::PA.4::tool_schema_binding_receipt` | PA.4 receipt emits doctrine output `tool_schema_binding_receipt` | **PASS** | `{"doctrine_field": "tool_schema_binding_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt…` |
| 30 | PA.4 | `EMIT::PA.4::validation_hash_receipt` | PA.4 receipt emits doctrine output `validation_hash_receipt` | **PASS** | `{"doctrine_field": "validation_hash_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_key…` |
| 31 | PA.5 | `EMIT::PA.5::TokenBudgetLedger` | PA.5 receipt emits doctrine output `TokenBudgetLedger` | **PASS** | `{"doctrine_field": "TokenBudgetLedger", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": ["…` |
| 32 | PA.5 | `EMIT::PA.5::deterministic_trimming_receipt` | PA.5 receipt emits doctrine output `deterministic_trimming_receipt` | **PASS** | `{"doctrine_field": "deterministic_trimming_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "rece…` |
| 33 | PA.5 | `EMIT::PA.5::stable_prefix_receipt` | PA.5 receipt emits doctrine output `stable_prefix_receipt` | **PASS** | `{"doctrine_field": "stable_prefix_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys"…` |
| 34 | PA.5 | `EMIT::PA.5::overflow_gap_report` | PA.5 receipt emits doctrine output `overflow_gap_report` | **PASS** | `{"doctrine_field": "overflow_gap_report", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": …` |
| 35 | PA.5 | `EMIT::PA.5::canonical_hash_input_manifest` | PA.5 receipt emits doctrine output `canonical_hash_input_manifest` | **PASS** | `{"doctrine_field": "canonical_hash_input_manifest", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "recei…` |
| 36 | PA.5 | `EMIT::PA.5::budget_status_receipt` | PA.5 receipt emits doctrine output `budget_status_receipt` | **PASS** | `{"doctrine_field": "budget_status_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys"…` |
| 37 | PA.6 | `EMIT::PA.6::ProviderRenderManifest` | PA.6 receipt emits doctrine output `ProviderRenderManifest` | **PASS** | `{"doctrine_field": "ProviderRenderManifest", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys…` |
| 38 | PA.6 | `EMIT::PA.6::rendered_prompt_packet` | PA.6 receipt emits doctrine output `rendered_prompt_packet` | **PASS** | `{"doctrine_field": "rendered_prompt_packet", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys…` |
| 39 | PA.6 | `EMIT::PA.6::provider_field_mapping_receipt` | PA.6 receipt emits doctrine output `provider_field_mapping_receipt` | **PASS** | `{"doctrine_field": "provider_field_mapping_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "rece…` |
| 40 | PA.6 | `EMIT::PA.6::provider_feature_gap_report` | PA.6 receipt emits doctrine output `provider_feature_gap_report` | **PASS** | `{"doctrine_field": "provider_feature_gap_report", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt…` |
| 41 | PA.6 | `EMIT::PA.6::schema_render_receipt` | PA.6 receipt emits doctrine output `schema_render_receipt` | **PASS** | `{"doctrine_field": "schema_render_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys"…` |
| 42 | PA.6 | `EMIT::PA.6::tool_render_receipt` | PA.6 receipt emits doctrine output `tool_render_receipt` | **PASS** | `{"doctrine_field": "tool_render_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": …` |
| 43 | PA.7 | `EMIT::PA.7::CompiledPromptArtifact` | PA.7 receipt emits doctrine output `CompiledPromptArtifact` | **PASS** | `{"doctrine_field": "CompiledPromptArtifact", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys…` |
| 44 | PA.7 | `EMIT::PA.7::compiled_prompt_artifact_receipt` | PA.7 receipt emits doctrine output `compiled_prompt_artifact_receipt` | **PASS** | `{"doctrine_field": "compiled_prompt_artifact_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "re…` |
| 45 | PA.7 | `EMIT::PA.7::manifest_hash_receipt` | PA.7 receipt emits doctrine output `manifest_hash_receipt` | **PASS** | `{"doctrine_field": "manifest_hash_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys"…` |
| 46 | PA.7 | `EMIT::PA.7::hmac_signature_receipt` | PA.7 receipt emits doctrine output `hmac_signature_receipt` | **PASS** | `{"doctrine_field": "hmac_signature_receipt", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys…` |
| 47 | PA.7 | `EMIT::PA.7::l2_handoff_envelope` | PA.7 receipt emits doctrine output `l2_handoff_envelope` | **PASS** | `{"doctrine_field": "l2_handoff_envelope", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_keys": …` |
| 48 | PA.7 | `EMIT::PA.7::final_artifact_gap_report` | PA.7 receipt emits doctrine output `final_artifact_gap_report` | **PASS** | `{"doctrine_field": "final_artifact_gap_report", "present_in_receipt": true, "match_kind": "direct", "matched_via_aliases": [], "receipt_k…` |

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

## NEGATIVE_PATH

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PA.0 | `NEG::PA.0::PA_BOUNDARY_MISMATCH` | PA.0 aggregator round-trips PA_BOUNDARY_MISMATCH | **PASS** | `{"stage": "PA.0", "input_status": "PA_BOUNDARY_MISMATCH", "aggregated_status": "PA_BOUNDARY_MISMATCH", "round_trip": true}` |
| 2 | PA.0 | `NEG::PA.0::PA_INPUT_INCOMPLETE` | PA.0 aggregator round-trips PA_INPUT_INCOMPLETE | **PASS** | `{"stage": "PA.0", "input_status": "PA_INPUT_INCOMPLETE", "aggregated_status": "PA_INPUT_INCOMPLETE", "round_trip": true}` |
| 3 | PA.0 | `NEG::PA.0::PA_READY` | PA.0 aggregator round-trips PA_READY | **PASS** | `{"stage": "PA.0", "input_status": "PA_READY", "aggregated_status": "PA_READY", "round_trip": true}` |
| 4 | PA.0 | `NEG::PA.0::PA_REQUIRES_UPSTREAM_REPAIR` | PA.0 aggregator round-trips PA_REQUIRES_UPSTREAM_REPAIR | **PASS** | `{"stage": "PA.0", "input_status": "PA_REQUIRES_UPSTREAM_REPAIR", "aggregated_status": "PA_REQUIRES_UPSTREAM_REPAIR", "round_trip": true}` |
| 5 | PA.1 | `NEG::PA.1::PA_BOM_GAP` | PA.1 aggregator round-trips PA_BOM_GAP | **PASS** | `{"stage": "PA.1", "input_status": "PA_BOM_GAP", "aggregated_status": "PA_BOM_GAP", "round_trip": true}` |
| 6 | PA.1 | `NEG::PA.1::PA_BOM_RESOLVED` | PA.1 aggregator round-trips PA_BOM_RESOLVED | **PASS** | `{"stage": "PA.1", "input_status": "PA_BOM_RESOLVED", "aggregated_status": "PA_BOM_RESOLVED", "round_trip": true}` |
| 7 | PA.1 | `NEG::PA.1::PA_REQUIRES_UPSTREAM_REPAIR` | PA.1 aggregator round-trips PA_REQUIRES_UPSTREAM_REPAIR | **PASS** | `{"stage": "PA.1", "input_status": "PA_REQUIRES_UPSTREAM_REPAIR", "aggregated_status": "PA_REQUIRES_UPSTREAM_REPAIR", "round_trip": true}` |
| 8 | PA.2 | `NEG::PA.2::PA_AUTHORITY_CONFLICT` | PA.2 aggregator round-trips PA_AUTHORITY_CONFLICT | **PASS** | `{"stage": "PA.2", "input_status": "PA_AUTHORITY_CONFLICT", "aggregated_status": "PA_AUTHORITY_CONFLICT", "round_trip": true}` |
| 9 | PA.2 | `NEG::PA.2::PA_SLOTS_COMPOSED` | PA.2 aggregator round-trips PA_SLOTS_COMPOSED | **PASS** | `{"stage": "PA.2", "input_status": "PA_SLOTS_COMPOSED", "aggregated_status": "PA_SLOTS_COMPOSED", "round_trip": true}` |
| 10 | PA.2 | `NEG::PA.2::PA_SLOT_COMPOSITION_GAP` | PA.2 aggregator round-trips PA_SLOT_COMPOSITION_GAP | **PASS** | `{"stage": "PA.2", "input_status": "PA_SLOT_COMPOSITION_GAP", "aggregated_status": "PA_SLOT_COMPOSITION_GAP", "round_trip": true}` |
| 11 | PA.3 | `NEG::PA.3::PA_REQUIRES_UPSTREAM_REPAIR` | PA.3 aggregator round-trips PA_REQUIRES_UPSTREAM_REPAIR | **PASS** | `{"stage": "PA.3", "input_status": "PA_REQUIRES_UPSTREAM_REPAIR", "aggregated_status": "PA_REQUIRES_UPSTREAM_REPAIR", "round_trip": true}` |
| 12 | PA.3 | `NEG::PA.3::PA_SAFE_EXTRACTION_PARTIAL` | PA.3 aggregator round-trips PA_SAFE_EXTRACTION_PARTIAL | **PASS** | `{"stage": "PA.3", "input_status": "PA_SAFE_EXTRACTION_PARTIAL", "aggregated_status": "PA_SAFE_EXTRACTION_PARTIAL", "round_trip": true}` |
| 13 | PA.3 | `NEG::PA.3::PA_SECURITY_GAP` | PA.3 aggregator round-trips PA_SECURITY_GAP | **PASS** | `{"stage": "PA.3", "input_status": "PA_SECURITY_GAP", "aggregated_status": "PA_SECURITY_GAP", "round_trip": true}` |
| 14 | PA.3 | `NEG::PA.3::PA_SECURITY_PASS` | PA.3 aggregator round-trips PA_SECURITY_PASS | **PASS** | `{"stage": "PA.3", "input_status": "PA_SECURITY_PASS", "aggregated_status": "PA_SECURITY_PASS", "round_trip": true}` |
| 15 | PA.3 | `NEG::PA.3::PA_SLOT_PAYLOAD_REJECTED` | PA.3 aggregator round-trips PA_SLOT_PAYLOAD_REJECTED | **PASS** | `{"stage": "PA.3", "input_status": "PA_SLOT_PAYLOAD_REJECTED", "aggregated_status": "PA_SLOT_PAYLOAD_REJECTED", "round_trip": true}` |
| 16 | PA.4 | `NEG::PA.4::PA_AUTHORITY_INVERSION_GAP` | PA.4 aggregator round-trips PA_AUTHORITY_INVERSION_GAP | **PASS** | `{"stage": "PA.4", "input_status": "PA_AUTHORITY_INVERSION_GAP", "aggregated_status": "PA_AUTHORITY_INVERSION_GAP", "round_trip": true}` |
| 17 | PA.4 | `NEG::PA.4::PA_CONTEXT_CONTRACT_GAP` | PA.4 aggregator round-trips PA_CONTEXT_CONTRACT_GAP | **PASS** | `{"stage": "PA.4", "input_status": "PA_CONTEXT_CONTRACT_GAP", "aggregated_status": "PA_CONTEXT_CONTRACT_GAP", "round_trip": true}` |
| 18 | PA.4 | `NEG::PA.4::PA_SCHEMA_BINDING_GAP` | PA.4 aggregator round-trips PA_SCHEMA_BINDING_GAP | **PASS** | `{"stage": "PA.4", "input_status": "PA_SCHEMA_BINDING_GAP", "aggregated_status": "PA_SCHEMA_BINDING_GAP", "round_trip": true}` |
| 19 | PA.4 | `NEG::PA.4::PA_SLOT_CONTRACT_INVALID` | PA.4 aggregator round-trips PA_SLOT_CONTRACT_INVALID | **PASS** | `{"stage": "PA.4", "input_status": "PA_SLOT_CONTRACT_INVALID", "aggregated_status": "PA_SLOT_CONTRACT_INVALID", "round_trip": true}` |
| 20 | PA.4 | `NEG::PA.4::PA_SLOT_CONTRACT_VALID` | PA.4 aggregator round-trips PA_SLOT_CONTRACT_VALID | **PASS** | `{"stage": "PA.4", "input_status": "PA_SLOT_CONTRACT_VALID", "aggregated_status": "PA_SLOT_CONTRACT_VALID", "round_trip": true}` |
| 21 | PA.4 | `NEG::PA.4::PA_TOOL_BINDING_GAP` | PA.4 aggregator round-trips PA_TOOL_BINDING_GAP | **PASS** | `{"stage": "PA.4", "input_status": "PA_TOOL_BINDING_GAP", "aggregated_status": "PA_TOOL_BINDING_GAP", "round_trip": true}` |
| 22 | PA.5 | `NEG::PA.5::PA_BUDGET_FIT` | PA.5 aggregator round-trips PA_BUDGET_FIT | **PASS** | `{"stage": "PA.5", "input_status": "PA_BUDGET_FIT", "aggregated_status": "PA_BUDGET_FIT", "round_trip": true}` |
| 23 | PA.5 | `NEG::PA.5::PA_BUDGET_OVERFLOW` | PA.5 aggregator round-trips PA_BUDGET_OVERFLOW | **PASS** | `{"stage": "PA.5", "input_status": "PA_BUDGET_OVERFLOW", "aggregated_status": "PA_BUDGET_OVERFLOW", "round_trip": true}` |
| 24 | PA.5 | `NEG::PA.5::PA_BUDGET_TRIMMED` | PA.5 aggregator round-trips PA_BUDGET_TRIMMED | **PASS** | `{"stage": "PA.5", "input_status": "PA_BUDGET_TRIMMED", "aggregated_status": "PA_BUDGET_TRIMMED", "round_trip": true}` |
| 25 | PA.5 | `NEG::PA.5::PA_REQUIRES_UPSTREAM_REPAIR` | PA.5 aggregator round-trips PA_REQUIRES_UPSTREAM_REPAIR | **PASS** | `{"stage": "PA.5", "input_status": "PA_REQUIRES_UPSTREAM_REPAIR", "aggregated_status": "PA_REQUIRES_UPSTREAM_REPAIR", "round_trip": true}` |
| 26 | PA.6 | `NEG::PA.6::PA_PROVIDER_FEATURE_GAP` | PA.6 aggregator round-trips PA_PROVIDER_FEATURE_GAP | **PASS** | `{"stage": "PA.6", "input_status": "PA_PROVIDER_FEATURE_GAP", "aggregated_status": "PA_PROVIDER_FEATURE_GAP", "round_trip": true}` |
| 27 | PA.6 | `NEG::PA.6::PA_RENDERED` | PA.6 aggregator round-trips PA_RENDERED | **PASS** | `{"stage": "PA.6", "input_status": "PA_RENDERED", "aggregated_status": "PA_RENDERED", "round_trip": true}` |
| 28 | PA.6 | `NEG::PA.6::PA_RENDER_GAP` | PA.6 aggregator round-trips PA_RENDER_GAP | **PASS** | `{"stage": "PA.6", "input_status": "PA_RENDER_GAP", "aggregated_status": "PA_RENDER_GAP", "round_trip": true}` |
| 29 | PA.6 | `NEG::PA.6::PA_SCHEMA_RENDER_GAP` | PA.6 aggregator round-trips PA_SCHEMA_RENDER_GAP | **PASS** | `{"stage": "PA.6", "input_status": "PA_SCHEMA_RENDER_GAP", "aggregated_status": "PA_SCHEMA_RENDER_GAP", "round_trip": true}` |
| 30 | PA.6 | `NEG::PA.6::PA_TOOL_RENDER_GAP` | PA.6 aggregator round-trips PA_TOOL_RENDER_GAP | **PASS** | `{"stage": "PA.6", "input_status": "PA_TOOL_RENDER_GAP", "aggregated_status": "PA_TOOL_RENDER_GAP", "round_trip": true}` |
| 31 | PA.7 | `NEG::PA.7::PA_ARTIFACT_NOT_SIGNED` | PA.7 aggregator round-trips PA_ARTIFACT_NOT_SIGNED | **PASS** | `{"stage": "PA.7", "input_status": "PA_ARTIFACT_NOT_SIGNED", "aggregated_status": "PA_ARTIFACT_NOT_SIGNED", "round_trip": true}` |
| 32 | PA.7 | `NEG::PA.7::PA_ARTIFACT_SIGNED` | PA.7 aggregator round-trips PA_ARTIFACT_SIGNED | **PASS** | `{"stage": "PA.7", "input_status": "PA_ARTIFACT_SIGNED", "aggregated_status": "PA_ARTIFACT_SIGNED", "round_trip": true}` |
| 33 | PA.7 | `NEG::PA.7::PA_L2_HANDOFF_GAP` | PA.7 aggregator round-trips PA_L2_HANDOFF_GAP | **PASS** | `{"stage": "PA.7", "input_status": "PA_L2_HANDOFF_GAP", "aggregated_status": "PA_L2_HANDOFF_GAP", "round_trip": true}` |
| 34 | PA.7 | `NEG::PA.7::PA_L2_HANDOFF_READY` | PA.7 aggregator round-trips PA_L2_HANDOFF_READY | **PASS** | `{"stage": "PA.7", "input_status": "PA_L2_HANDOFF_READY", "aggregated_status": "PA_L2_HANDOFF_READY", "round_trip": true}` |
| 35 | PA.7 | `NEG::PA.7::PA_MANIFEST_HASH_GAP` | PA.7 aggregator round-trips PA_MANIFEST_HASH_GAP | **PASS** | `{"stage": "PA.7", "input_status": "PA_MANIFEST_HASH_GAP", "aggregated_status": "PA_MANIFEST_HASH_GAP", "round_trip": true}` |
| 36 | PA.7 | `NEG::PA.7::PA_SIGNATURE_GAP` | PA.7 aggregator round-trips PA_SIGNATURE_GAP | **PASS** | `{"stage": "PA.7", "input_status": "PA_SIGNATURE_GAP", "aggregated_status": "PA_SIGNATURE_GAP", "round_trip": true}` |

## PARSER_ROBUSTNESS

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PARENT | `PARSER::missing_section` | PARSER/missing_section: Section absent from doc returns empty list | **PASS** | `{"case": "missing_section", "section": "STATUS VALUES", "expected": [], "actual": [], "description": "Section absent from doc returns emp…` |
| 2 | PARENT | `PARSER::blank_file` | PARSER/blank_file: Empty doc returns empty list | **PASS** | `{"case": "blank_file", "section": "STATUS VALUES", "expected": [], "actual": [], "description": "Empty doc returns empty list"}` |
| 3 | PARENT | `PARSER::repeated_heading` | PARSER/repeated_heading: Parser stops at first blank line after items, ignoring later repeats | **PASS** | `{"case": "repeated_heading", "section": "STATUS VALUES", "expected": ["A", "B"], "actual": ["A", "B"], "description": "Parser stops at fi…` |
| 4 | PARENT | `PARSER::non_bullet_noise` | PARSER/non_bullet_noise: Parser stops at first non-bullet, non-empty line | **PASS** | `{"case": "non_bullet_noise", "section": "STATUS VALUES", "expected": ["One"], "actual": ["One"], "description": "Parser stops at first no…` |
| 5 | PARENT | `PARSER::section_terminated_by_next_heading` | PARSER/section_terminated_by_next_heading: Section is terminated by the next recognised heading | **PASS** | `{"case": "section_terminated_by_next_heading", "section": "STATUS VALUES", "expected": ["One", "Two"], "actual": ["One", "Two"], "descrip…` |

## PIPELINE_NEG

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | ALL | `PIPE_NEG::missing_plan_contract` | Pipeline with missing plan_contract publishes PA_INPUT_INCOMPLETE | **PASS** | `{"dispatch_allowed": false, "doctrine_status": "PA_INPUT_INCOMPLETE"}` |
| 2 | ALL | `PIPE_NEG::missing_route_contract` | Pipeline with missing route_contract refuses dispatch | **PASS** | `{"dispatch_allowed": false, "doctrine_status": "PA_INPUT_INCOMPLETE"}` |
| 3 | ALL | `PIPE_NEG::no_forbidden_in_failure_path` | Pipeline negative-path receipts contain zero forbidden tokens | **PASS** | `{"forbidden_hits": []}` |

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

## STATUS_PARTITION_COMPLETE

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | ALL | `STATUS::no_orphans` | Every PAStatus member is claimed by at least one stage | **PASS** | `{"runtime_count": 33, "claimed_count": 33, "orphans": []}` |
| 2 | ALL | `STATUS::cross_stage_documented` | Cross-stage statuses match the documented set | **PASS** | `{"observed": {"PA_REQUIRES_UPSTREAM_REPAIR": ["PA.0", "PA.1", "PA.3", "PA.5"]}, "expected_keys": ["PA_REQUIRES_UPSTREAM_REPAIR"]}` |

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

