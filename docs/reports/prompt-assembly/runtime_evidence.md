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

**Tally:** 387 PASS / 0 FAIL (of 387 requirements)

**Generated:** 2026-04-27T00:58:59.469203+00:00

## Category roll-up

| Category | Total | PASS | FAIL |
|---|---:|---:|---:|
| AGGREGATION | 5 | 5 | 0 |
| CHILD_FORBID_DOCTRINE | 24 | 24 | 0 |
| DETERMINISM | 8 | 8 | 0 |
| DOCTRINE_DRIFT | 16 | 16 | 0 |
| E2E | 4 | 4 | 0 |
| FORBID_DEEP | 5 | 5 | 0 |
| FORBID_FALSE_POSITIVE | 5 | 5 | 0 |
| FORBID_RD | 24 | 24 | 0 |
| INVARIANT | 12 | 12 | 0 |
| MUST_EMIT | 48 | 48 | 0 |
| MUST_NOT_DOCTRINE | 72 | 72 | 0 |
| MUST_NOT_FENCE | 11 | 11 | 0 |
| NEGATIVE_PATH | 36 | 36 | 0 |
| PA8_CONTRACTS | 13 | 13 | 0 |
| PA8_RULES | 4 | 4 | 0 |
| PA8_TESTS | 7 | 7 | 0 |
| PARENT_VOCAB | 20 | 20 | 0 |
| PARSER_EDGE_HARDENING | 7 | 7 | 0 |
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

## CHILD_FORBID_DOCTRINE

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PA.0 | `CHILD_FORBID::PA.0::parsed` | PA.0 forbidden-outputs block parses at least one token | **PASS** | `{"stage": "PA.0", "parsed_count": 22, "parent_master_count": 22}` |
| 2 | PA.0 | `CHILD_FORBID::PA.0::subset_of_parent` | PA.0 forbidden tokens are subset of parent master set | **PASS** | `{"stage": "PA.0", "parsed_count": 22, "parent_master_count": 22, "unknown_tokens": []}` |
| 3 | PA.0 | `CHILD_FORBID::PA.0::no_silent_drop` | PA.0 inherits every parent forbidden token (no silent drop) | **PASS** | `{"stage": "PA.0", "parsed_count": 22, "parent_master_count": 22, "missing_from_child": []}` |
| 4 | PA.1 | `CHILD_FORBID::PA.1::parsed` | PA.1 forbidden-outputs block parses at least one token | **PASS** | `{"stage": "PA.1", "parsed_count": 22, "parent_master_count": 22}` |
| 5 | PA.1 | `CHILD_FORBID::PA.1::subset_of_parent` | PA.1 forbidden tokens are subset of parent master set | **PASS** | `{"stage": "PA.1", "parsed_count": 22, "parent_master_count": 22, "unknown_tokens": []}` |
| 6 | PA.1 | `CHILD_FORBID::PA.1::no_silent_drop` | PA.1 inherits every parent forbidden token (no silent drop) | **PASS** | `{"stage": "PA.1", "parsed_count": 22, "parent_master_count": 22, "missing_from_child": []}` |
| 7 | PA.2 | `CHILD_FORBID::PA.2::parsed` | PA.2 forbidden-outputs block parses at least one token | **PASS** | `{"stage": "PA.2", "parsed_count": 22, "parent_master_count": 22}` |
| 8 | PA.2 | `CHILD_FORBID::PA.2::subset_of_parent` | PA.2 forbidden tokens are subset of parent master set | **PASS** | `{"stage": "PA.2", "parsed_count": 22, "parent_master_count": 22, "unknown_tokens": []}` |
| 9 | PA.2 | `CHILD_FORBID::PA.2::no_silent_drop` | PA.2 inherits every parent forbidden token (no silent drop) | **PASS** | `{"stage": "PA.2", "parsed_count": 22, "parent_master_count": 22, "missing_from_child": []}` |
| 10 | PA.3 | `CHILD_FORBID::PA.3::parsed` | PA.3 forbidden-outputs block parses at least one token | **PASS** | `{"stage": "PA.3", "parsed_count": 22, "parent_master_count": 22}` |
| 11 | PA.3 | `CHILD_FORBID::PA.3::subset_of_parent` | PA.3 forbidden tokens are subset of parent master set | **PASS** | `{"stage": "PA.3", "parsed_count": 22, "parent_master_count": 22, "unknown_tokens": []}` |
| 12 | PA.3 | `CHILD_FORBID::PA.3::no_silent_drop` | PA.3 inherits every parent forbidden token (no silent drop) | **PASS** | `{"stage": "PA.3", "parsed_count": 22, "parent_master_count": 22, "missing_from_child": []}` |
| 13 | PA.4 | `CHILD_FORBID::PA.4::parsed` | PA.4 forbidden-outputs block parses at least one token | **PASS** | `{"stage": "PA.4", "parsed_count": 22, "parent_master_count": 22}` |
| 14 | PA.4 | `CHILD_FORBID::PA.4::subset_of_parent` | PA.4 forbidden tokens are subset of parent master set | **PASS** | `{"stage": "PA.4", "parsed_count": 22, "parent_master_count": 22, "unknown_tokens": []}` |
| 15 | PA.4 | `CHILD_FORBID::PA.4::no_silent_drop` | PA.4 inherits every parent forbidden token (no silent drop) | **PASS** | `{"stage": "PA.4", "parsed_count": 22, "parent_master_count": 22, "missing_from_child": []}` |
| 16 | PA.5 | `CHILD_FORBID::PA.5::parsed` | PA.5 forbidden-outputs block parses at least one token | **PASS** | `{"stage": "PA.5", "parsed_count": 22, "parent_master_count": 22}` |
| 17 | PA.5 | `CHILD_FORBID::PA.5::subset_of_parent` | PA.5 forbidden tokens are subset of parent master set | **PASS** | `{"stage": "PA.5", "parsed_count": 22, "parent_master_count": 22, "unknown_tokens": []}` |
| 18 | PA.5 | `CHILD_FORBID::PA.5::no_silent_drop` | PA.5 inherits every parent forbidden token (no silent drop) | **PASS** | `{"stage": "PA.5", "parsed_count": 22, "parent_master_count": 22, "missing_from_child": []}` |
| 19 | PA.6 | `CHILD_FORBID::PA.6::parsed` | PA.6 forbidden-outputs block parses at least one token | **PASS** | `{"stage": "PA.6", "parsed_count": 22, "parent_master_count": 22}` |
| 20 | PA.6 | `CHILD_FORBID::PA.6::subset_of_parent` | PA.6 forbidden tokens are subset of parent master set | **PASS** | `{"stage": "PA.6", "parsed_count": 22, "parent_master_count": 22, "unknown_tokens": []}` |
| 21 | PA.6 | `CHILD_FORBID::PA.6::no_silent_drop` | PA.6 inherits every parent forbidden token (no silent drop) | **PASS** | `{"stage": "PA.6", "parsed_count": 22, "parent_master_count": 22, "missing_from_child": []}` |
| 22 | PA.7 | `CHILD_FORBID::PA.7::parsed` | PA.7 forbidden-outputs block parses at least one token | **PASS** | `{"stage": "PA.7", "parsed_count": 22, "parent_master_count": 22}` |
| 23 | PA.7 | `CHILD_FORBID::PA.7::subset_of_parent` | PA.7 forbidden tokens are subset of parent master set | **PASS** | `{"stage": "PA.7", "parsed_count": 22, "parent_master_count": 22, "unknown_tokens": []}` |
| 24 | PA.7 | `CHILD_FORBID::PA.7::no_silent_drop` | PA.7 inherits every parent forbidden token (no silent drop) | **PASS** | `{"stage": "PA.7", "parsed_count": 22, "parent_master_count": 22, "missing_from_child": []}` |

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

## MUST_NOT_DOCTRINE

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PA.0 | `MUST_NOT::PA.0::parsed` | PA.0 MUST NOT block parses at least one keyword | **PASS** | `{"stage": "PA.0", "parsed_count": 8}` |
| 2 | PA.0 | `MUST_NOT::PA.0::retrieve` | PA.0 MUST NOT `retrieve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "retrieve", "mapped_to": ["call_provider", "execute_tool"], "covered_by_parent_master": ["call_provider", "execute_tool"]}` |
| 3 | PA.0 | `MUST_NOT::PA.0::route` | PA.0 MUST NOT `route` maps to runtime forbidden tokens | **PASS** | `{"keyword": "route", "mapped_to": ["REROUTE"], "covered_by_parent_master": ["REROUTE"]}` |
| 4 | PA.0 | `MUST_NOT::PA.0::call` | PA.0 MUST NOT `call` maps to runtime forbidden tokens | **PASS** | `{"keyword": "call", "mapped_to": ["call_provider"], "covered_by_parent_master": ["call_provider"]}` |
| 5 | PA.0 | `MUST_NOT::PA.0::execute` | PA.0 MUST NOT `execute` maps to runtime forbidden tokens | **PASS** | `{"keyword": "execute", "mapped_to": ["approve_execution", "execute_tool"], "covered_by_parent_master": ["approve_execution", "execute_too…` |
| 6 | PA.0 | `MUST_NOT::PA.0::approve` | PA.0 MUST NOT `approve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "approve", "mapped_to": ["approve_execution", "approve_output", "approve_write"], "covered_by_parent_master": ["approve_execu…` |
| 7 | PA.0 | `MUST_NOT::PA.0::commit` | PA.0 MUST NOT `commit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "commit", "mapped_to": ["COMMIT_REQUEST", "approve_write", "mutate_l4"], "covered_by_parent_master": ["COMMIT_REQUEST", "appr…` |
| 8 | PA.0 | `MUST_NOT::PA.0::emit` | PA.0 MUST NOT `emit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "emit", "mapped_to": ["ALLOW", "ALLOW_FINISH", "BLOCK_COMMIT", "COMMIT_REQUEST", "DENY", "ESCALATE_HITL", "REROUTE"], "covere…` |
| 9 | PA.0 | `MUST_NOT::PA.0::silently` | PA.0 MUST NOT `silently` maps to runtime forbidden tokens | **PASS** | `{"keyword": "silently", "mapped_to": ["MARK_DEGRADED", "SAFE_FALLBACK"], "covered_by_parent_master": ["MARK_DEGRADED", "SAFE_FALLBACK"]}` |
| 10 | PA.1 | `MUST_NOT::PA.1::parsed` | PA.1 MUST NOT block parses at least one keyword | **PASS** | `{"stage": "PA.1", "parsed_count": 8}` |
| 11 | PA.1 | `MUST_NOT::PA.1::retrieve` | PA.1 MUST NOT `retrieve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "retrieve", "mapped_to": ["call_provider", "execute_tool"], "covered_by_parent_master": ["call_provider", "execute_tool"]}` |
| 12 | PA.1 | `MUST_NOT::PA.1::route` | PA.1 MUST NOT `route` maps to runtime forbidden tokens | **PASS** | `{"keyword": "route", "mapped_to": ["REROUTE"], "covered_by_parent_master": ["REROUTE"]}` |
| 13 | PA.1 | `MUST_NOT::PA.1::call` | PA.1 MUST NOT `call` maps to runtime forbidden tokens | **PASS** | `{"keyword": "call", "mapped_to": ["call_provider"], "covered_by_parent_master": ["call_provider"]}` |
| 14 | PA.1 | `MUST_NOT::PA.1::execute` | PA.1 MUST NOT `execute` maps to runtime forbidden tokens | **PASS** | `{"keyword": "execute", "mapped_to": ["approve_execution", "execute_tool"], "covered_by_parent_master": ["approve_execution", "execute_too…` |
| 15 | PA.1 | `MUST_NOT::PA.1::approve` | PA.1 MUST NOT `approve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "approve", "mapped_to": ["approve_execution", "approve_output", "approve_write"], "covered_by_parent_master": ["approve_execu…` |
| 16 | PA.1 | `MUST_NOT::PA.1::commit` | PA.1 MUST NOT `commit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "commit", "mapped_to": ["COMMIT_REQUEST", "approve_write", "mutate_l4"], "covered_by_parent_master": ["COMMIT_REQUEST", "appr…` |
| 17 | PA.1 | `MUST_NOT::PA.1::emit` | PA.1 MUST NOT `emit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "emit", "mapped_to": ["ALLOW", "ALLOW_FINISH", "BLOCK_COMMIT", "COMMIT_REQUEST", "DENY", "ESCALATE_HITL", "REROUTE"], "covere…` |
| 18 | PA.1 | `MUST_NOT::PA.1::silently` | PA.1 MUST NOT `silently` maps to runtime forbidden tokens | **PASS** | `{"keyword": "silently", "mapped_to": ["MARK_DEGRADED", "SAFE_FALLBACK"], "covered_by_parent_master": ["MARK_DEGRADED", "SAFE_FALLBACK"]}` |
| 19 | PA.2 | `MUST_NOT::PA.2::parsed` | PA.2 MUST NOT block parses at least one keyword | **PASS** | `{"stage": "PA.2", "parsed_count": 8}` |
| 20 | PA.2 | `MUST_NOT::PA.2::retrieve` | PA.2 MUST NOT `retrieve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "retrieve", "mapped_to": ["call_provider", "execute_tool"], "covered_by_parent_master": ["call_provider", "execute_tool"]}` |
| 21 | PA.2 | `MUST_NOT::PA.2::route` | PA.2 MUST NOT `route` maps to runtime forbidden tokens | **PASS** | `{"keyword": "route", "mapped_to": ["REROUTE"], "covered_by_parent_master": ["REROUTE"]}` |
| 22 | PA.2 | `MUST_NOT::PA.2::call` | PA.2 MUST NOT `call` maps to runtime forbidden tokens | **PASS** | `{"keyword": "call", "mapped_to": ["call_provider"], "covered_by_parent_master": ["call_provider"]}` |
| 23 | PA.2 | `MUST_NOT::PA.2::execute` | PA.2 MUST NOT `execute` maps to runtime forbidden tokens | **PASS** | `{"keyword": "execute", "mapped_to": ["approve_execution", "execute_tool"], "covered_by_parent_master": ["approve_execution", "execute_too…` |
| 24 | PA.2 | `MUST_NOT::PA.2::approve` | PA.2 MUST NOT `approve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "approve", "mapped_to": ["approve_execution", "approve_output", "approve_write"], "covered_by_parent_master": ["approve_execu…` |
| 25 | PA.2 | `MUST_NOT::PA.2::commit` | PA.2 MUST NOT `commit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "commit", "mapped_to": ["COMMIT_REQUEST", "approve_write", "mutate_l4"], "covered_by_parent_master": ["COMMIT_REQUEST", "appr…` |
| 26 | PA.2 | `MUST_NOT::PA.2::emit` | PA.2 MUST NOT `emit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "emit", "mapped_to": ["ALLOW", "ALLOW_FINISH", "BLOCK_COMMIT", "COMMIT_REQUEST", "DENY", "ESCALATE_HITL", "REROUTE"], "covere…` |
| 27 | PA.2 | `MUST_NOT::PA.2::silently` | PA.2 MUST NOT `silently` maps to runtime forbidden tokens | **PASS** | `{"keyword": "silently", "mapped_to": ["MARK_DEGRADED", "SAFE_FALLBACK"], "covered_by_parent_master": ["MARK_DEGRADED", "SAFE_FALLBACK"]}` |
| 28 | PA.3 | `MUST_NOT::PA.3::parsed` | PA.3 MUST NOT block parses at least one keyword | **PASS** | `{"stage": "PA.3", "parsed_count": 8}` |
| 29 | PA.3 | `MUST_NOT::PA.3::retrieve` | PA.3 MUST NOT `retrieve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "retrieve", "mapped_to": ["call_provider", "execute_tool"], "covered_by_parent_master": ["call_provider", "execute_tool"]}` |
| 30 | PA.3 | `MUST_NOT::PA.3::route` | PA.3 MUST NOT `route` maps to runtime forbidden tokens | **PASS** | `{"keyword": "route", "mapped_to": ["REROUTE"], "covered_by_parent_master": ["REROUTE"]}` |
| 31 | PA.3 | `MUST_NOT::PA.3::call` | PA.3 MUST NOT `call` maps to runtime forbidden tokens | **PASS** | `{"keyword": "call", "mapped_to": ["call_provider"], "covered_by_parent_master": ["call_provider"]}` |
| 32 | PA.3 | `MUST_NOT::PA.3::execute` | PA.3 MUST NOT `execute` maps to runtime forbidden tokens | **PASS** | `{"keyword": "execute", "mapped_to": ["approve_execution", "execute_tool"], "covered_by_parent_master": ["approve_execution", "execute_too…` |
| 33 | PA.3 | `MUST_NOT::PA.3::approve` | PA.3 MUST NOT `approve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "approve", "mapped_to": ["approve_execution", "approve_output", "approve_write"], "covered_by_parent_master": ["approve_execu…` |
| 34 | PA.3 | `MUST_NOT::PA.3::commit` | PA.3 MUST NOT `commit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "commit", "mapped_to": ["COMMIT_REQUEST", "approve_write", "mutate_l4"], "covered_by_parent_master": ["COMMIT_REQUEST", "appr…` |
| 35 | PA.3 | `MUST_NOT::PA.3::emit` | PA.3 MUST NOT `emit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "emit", "mapped_to": ["ALLOW", "ALLOW_FINISH", "BLOCK_COMMIT", "COMMIT_REQUEST", "DENY", "ESCALATE_HITL", "REROUTE"], "covere…` |
| 36 | PA.3 | `MUST_NOT::PA.3::silently` | PA.3 MUST NOT `silently` maps to runtime forbidden tokens | **PASS** | `{"keyword": "silently", "mapped_to": ["MARK_DEGRADED", "SAFE_FALLBACK"], "covered_by_parent_master": ["MARK_DEGRADED", "SAFE_FALLBACK"]}` |
| 37 | PA.4 | `MUST_NOT::PA.4::parsed` | PA.4 MUST NOT block parses at least one keyword | **PASS** | `{"stage": "PA.4", "parsed_count": 8}` |
| 38 | PA.4 | `MUST_NOT::PA.4::retrieve` | PA.4 MUST NOT `retrieve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "retrieve", "mapped_to": ["call_provider", "execute_tool"], "covered_by_parent_master": ["call_provider", "execute_tool"]}` |
| 39 | PA.4 | `MUST_NOT::PA.4::route` | PA.4 MUST NOT `route` maps to runtime forbidden tokens | **PASS** | `{"keyword": "route", "mapped_to": ["REROUTE"], "covered_by_parent_master": ["REROUTE"]}` |
| 40 | PA.4 | `MUST_NOT::PA.4::call` | PA.4 MUST NOT `call` maps to runtime forbidden tokens | **PASS** | `{"keyword": "call", "mapped_to": ["call_provider"], "covered_by_parent_master": ["call_provider"]}` |
| 41 | PA.4 | `MUST_NOT::PA.4::execute` | PA.4 MUST NOT `execute` maps to runtime forbidden tokens | **PASS** | `{"keyword": "execute", "mapped_to": ["approve_execution", "execute_tool"], "covered_by_parent_master": ["approve_execution", "execute_too…` |
| 42 | PA.4 | `MUST_NOT::PA.4::approve` | PA.4 MUST NOT `approve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "approve", "mapped_to": ["approve_execution", "approve_output", "approve_write"], "covered_by_parent_master": ["approve_execu…` |
| 43 | PA.4 | `MUST_NOT::PA.4::commit` | PA.4 MUST NOT `commit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "commit", "mapped_to": ["COMMIT_REQUEST", "approve_write", "mutate_l4"], "covered_by_parent_master": ["COMMIT_REQUEST", "appr…` |
| 44 | PA.4 | `MUST_NOT::PA.4::emit` | PA.4 MUST NOT `emit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "emit", "mapped_to": ["ALLOW", "ALLOW_FINISH", "BLOCK_COMMIT", "COMMIT_REQUEST", "DENY", "ESCALATE_HITL", "REROUTE"], "covere…` |
| 45 | PA.4 | `MUST_NOT::PA.4::silently` | PA.4 MUST NOT `silently` maps to runtime forbidden tokens | **PASS** | `{"keyword": "silently", "mapped_to": ["MARK_DEGRADED", "SAFE_FALLBACK"], "covered_by_parent_master": ["MARK_DEGRADED", "SAFE_FALLBACK"]}` |
| 46 | PA.5 | `MUST_NOT::PA.5::parsed` | PA.5 MUST NOT block parses at least one keyword | **PASS** | `{"stage": "PA.5", "parsed_count": 8}` |
| 47 | PA.5 | `MUST_NOT::PA.5::retrieve` | PA.5 MUST NOT `retrieve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "retrieve", "mapped_to": ["call_provider", "execute_tool"], "covered_by_parent_master": ["call_provider", "execute_tool"]}` |
| 48 | PA.5 | `MUST_NOT::PA.5::route` | PA.5 MUST NOT `route` maps to runtime forbidden tokens | **PASS** | `{"keyword": "route", "mapped_to": ["REROUTE"], "covered_by_parent_master": ["REROUTE"]}` |
| 49 | PA.5 | `MUST_NOT::PA.5::call` | PA.5 MUST NOT `call` maps to runtime forbidden tokens | **PASS** | `{"keyword": "call", "mapped_to": ["call_provider"], "covered_by_parent_master": ["call_provider"]}` |
| 50 | PA.5 | `MUST_NOT::PA.5::execute` | PA.5 MUST NOT `execute` maps to runtime forbidden tokens | **PASS** | `{"keyword": "execute", "mapped_to": ["approve_execution", "execute_tool"], "covered_by_parent_master": ["approve_execution", "execute_too…` |
| 51 | PA.5 | `MUST_NOT::PA.5::approve` | PA.5 MUST NOT `approve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "approve", "mapped_to": ["approve_execution", "approve_output", "approve_write"], "covered_by_parent_master": ["approve_execu…` |
| 52 | PA.5 | `MUST_NOT::PA.5::commit` | PA.5 MUST NOT `commit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "commit", "mapped_to": ["COMMIT_REQUEST", "approve_write", "mutate_l4"], "covered_by_parent_master": ["COMMIT_REQUEST", "appr…` |
| 53 | PA.5 | `MUST_NOT::PA.5::emit` | PA.5 MUST NOT `emit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "emit", "mapped_to": ["ALLOW", "ALLOW_FINISH", "BLOCK_COMMIT", "COMMIT_REQUEST", "DENY", "ESCALATE_HITL", "REROUTE"], "covere…` |
| 54 | PA.5 | `MUST_NOT::PA.5::silently` | PA.5 MUST NOT `silently` maps to runtime forbidden tokens | **PASS** | `{"keyword": "silently", "mapped_to": ["MARK_DEGRADED", "SAFE_FALLBACK"], "covered_by_parent_master": ["MARK_DEGRADED", "SAFE_FALLBACK"]}` |
| 55 | PA.6 | `MUST_NOT::PA.6::parsed` | PA.6 MUST NOT block parses at least one keyword | **PASS** | `{"stage": "PA.6", "parsed_count": 8}` |
| 56 | PA.6 | `MUST_NOT::PA.6::retrieve` | PA.6 MUST NOT `retrieve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "retrieve", "mapped_to": ["call_provider", "execute_tool"], "covered_by_parent_master": ["call_provider", "execute_tool"]}` |
| 57 | PA.6 | `MUST_NOT::PA.6::route` | PA.6 MUST NOT `route` maps to runtime forbidden tokens | **PASS** | `{"keyword": "route", "mapped_to": ["REROUTE"], "covered_by_parent_master": ["REROUTE"]}` |
| 58 | PA.6 | `MUST_NOT::PA.6::call` | PA.6 MUST NOT `call` maps to runtime forbidden tokens | **PASS** | `{"keyword": "call", "mapped_to": ["call_provider"], "covered_by_parent_master": ["call_provider"]}` |
| 59 | PA.6 | `MUST_NOT::PA.6::execute` | PA.6 MUST NOT `execute` maps to runtime forbidden tokens | **PASS** | `{"keyword": "execute", "mapped_to": ["approve_execution", "execute_tool"], "covered_by_parent_master": ["approve_execution", "execute_too…` |
| 60 | PA.6 | `MUST_NOT::PA.6::approve` | PA.6 MUST NOT `approve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "approve", "mapped_to": ["approve_execution", "approve_output", "approve_write"], "covered_by_parent_master": ["approve_execu…` |
| 61 | PA.6 | `MUST_NOT::PA.6::commit` | PA.6 MUST NOT `commit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "commit", "mapped_to": ["COMMIT_REQUEST", "approve_write", "mutate_l4"], "covered_by_parent_master": ["COMMIT_REQUEST", "appr…` |
| 62 | PA.6 | `MUST_NOT::PA.6::emit` | PA.6 MUST NOT `emit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "emit", "mapped_to": ["ALLOW", "ALLOW_FINISH", "BLOCK_COMMIT", "COMMIT_REQUEST", "DENY", "ESCALATE_HITL", "REROUTE"], "covere…` |
| 63 | PA.6 | `MUST_NOT::PA.6::silently` | PA.6 MUST NOT `silently` maps to runtime forbidden tokens | **PASS** | `{"keyword": "silently", "mapped_to": ["MARK_DEGRADED", "SAFE_FALLBACK"], "covered_by_parent_master": ["MARK_DEGRADED", "SAFE_FALLBACK"]}` |
| 64 | PA.7 | `MUST_NOT::PA.7::parsed` | PA.7 MUST NOT block parses at least one keyword | **PASS** | `{"stage": "PA.7", "parsed_count": 8}` |
| 65 | PA.7 | `MUST_NOT::PA.7::retrieve` | PA.7 MUST NOT `retrieve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "retrieve", "mapped_to": ["call_provider", "execute_tool"], "covered_by_parent_master": ["call_provider", "execute_tool"]}` |
| 66 | PA.7 | `MUST_NOT::PA.7::route` | PA.7 MUST NOT `route` maps to runtime forbidden tokens | **PASS** | `{"keyword": "route", "mapped_to": ["REROUTE"], "covered_by_parent_master": ["REROUTE"]}` |
| 67 | PA.7 | `MUST_NOT::PA.7::call` | PA.7 MUST NOT `call` maps to runtime forbidden tokens | **PASS** | `{"keyword": "call", "mapped_to": ["call_provider"], "covered_by_parent_master": ["call_provider"]}` |
| 68 | PA.7 | `MUST_NOT::PA.7::execute` | PA.7 MUST NOT `execute` maps to runtime forbidden tokens | **PASS** | `{"keyword": "execute", "mapped_to": ["approve_execution", "execute_tool"], "covered_by_parent_master": ["approve_execution", "execute_too…` |
| 69 | PA.7 | `MUST_NOT::PA.7::approve` | PA.7 MUST NOT `approve` maps to runtime forbidden tokens | **PASS** | `{"keyword": "approve", "mapped_to": ["approve_execution", "approve_output", "approve_write"], "covered_by_parent_master": ["approve_execu…` |
| 70 | PA.7 | `MUST_NOT::PA.7::commit` | PA.7 MUST NOT `commit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "commit", "mapped_to": ["COMMIT_REQUEST", "approve_write", "mutate_l4"], "covered_by_parent_master": ["COMMIT_REQUEST", "appr…` |
| 71 | PA.7 | `MUST_NOT::PA.7::emit` | PA.7 MUST NOT `emit` maps to runtime forbidden tokens | **PASS** | `{"keyword": "emit", "mapped_to": ["ALLOW", "ALLOW_FINISH", "BLOCK_COMMIT", "COMMIT_REQUEST", "DENY", "ESCALATE_HITL", "REROUTE"], "covere…` |
| 72 | PA.7 | `MUST_NOT::PA.7::silently` | PA.7 MUST NOT `silently` maps to runtime forbidden tokens | **PASS** | `{"keyword": "silently", "mapped_to": ["MARK_DEGRADED", "SAFE_FALLBACK"], "covered_by_parent_master": ["MARK_DEGRADED", "SAFE_FALLBACK"]}` |

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

## PA8_CONTRACTS

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PA.8 | `PA8_CONTRACTS::parsed` | PA.8 CONTRACTS TO IMPLEMENT block parses at least one field | **PASS** | `{"parsed_count": 12}` |
| 2 | PA.8 | `PA8_CONTRACT::proof_id` | PA.8 contract field `proof_id` absorbed by runtime symbol or receipt key | **PASS** | `{"contract_field": "proof_id", "absorbed_by": "compiled_prompt_artifact_id", "present_on_pa_surface": false, "present_in_pa_receipt_union…` |
| 3 | PA.8 | `PA8_CONTRACT::prompt_bom_ref` | PA.8 contract field `prompt_bom_ref` absorbed by runtime symbol or receipt key | **PASS** | `{"contract_field": "prompt_bom_ref", "absorbed_by": "prompt_bom_id", "present_on_pa_surface": false, "present_in_pa_receipt_union": true}` |
| 4 | PA.8 | `PA8_CONTRACT::compiled_prompt_artifact_ref` | PA.8 contract field `compiled_prompt_artifact_ref` absorbed by runtime symbol or receipt key | **PASS** | `{"contract_field": "compiled_prompt_artifact_ref", "absorbed_by": "CompiledPromptArtifact", "present_on_pa_surface": false, "present_in_p…` |
| 5 | PA.8 | `PA8_CONTRACT::slot_order` | PA.8 contract field `slot_order` absorbed by runtime symbol or receipt key | **PASS** | `{"contract_field": "slot_order", "absorbed_by": "SLOT_ORDER", "present_on_pa_surface": true, "present_in_pa_receipt_union": false}` |
| 6 | PA.8 | `PA8_CONTRACT::slot_hashes` | PA.8 contract field `slot_hashes` absorbed by runtime symbol or receipt key | **PASS** | `{"contract_field": "slot_hashes", "absorbed_by": "structured_slots_hash_receipt", "present_on_pa_surface": false, "present_in_pa_receipt_…` |
| 7 | PA.8 | `PA8_CONTRACT::higher_authority_override_map` | PA.8 contract field `higher_authority_override_map` absorbed by runtime symbol or receipt key | **PASS** | `{"contract_field": "higher_authority_override_map", "absorbed_by": "slot_authority_map", "present_on_pa_surface": false, "present_in_pa_r…` |
| 8 | PA.8 | `PA8_CONTRACT::lower_authority_override_attempts` | PA.8 contract field `lower_authority_override_attempts` absorbed by runtime symbol or receipt key | **PASS** | `{"contract_field": "lower_authority_override_attempts", "absorbed_by": "slot_conflict_map", "present_on_pa_surface": false, "present_in_p…` |
| 9 | PA.8 | `PA8_CONTRACT::blocked_attempts` | PA.8 contract field `blocked_attempts` absorbed by runtime symbol or receipt key | **PASS** | `{"contract_field": "blocked_attempts", "absorbed_by": "rejected_slot_payload_report", "present_on_pa_surface": false, "present_in_pa_rece…` |
| 10 | PA.8 | `PA8_CONTRACT::provider_render_hash` | PA.8 contract field `provider_render_hash` absorbed by runtime symbol or receipt key | **PASS** | `{"contract_field": "provider_render_hash", "absorbed_by": "ProviderRenderManifest", "present_on_pa_surface": false, "present_in_pa_receip…` |
| 11 | PA.8 | `PA8_CONTRACT::response_schema_binding_ref` | PA.8 contract field `response_schema_binding_ref` absorbed by runtime symbol or receipt key | **PASS** | `{"contract_field": "response_schema_binding_ref", "absorbed_by": "R0SchemaBinding", "present_on_pa_surface": true, "present_in_pa_receipt…` |
| 12 | PA.8 | `PA8_CONTRACT::hmac_sig` | PA.8 contract field `hmac_sig` absorbed by runtime symbol or receipt key | **PASS** | `{"contract_field": "hmac_sig", "absorbed_by": "hmac_signature_receipt", "present_on_pa_surface": false, "present_in_pa_receipt_union": true}` |
| 13 | PA.8 | `PA8_CONTRACT::deterministic_digest` | PA.8 contract field `deterministic_digest` absorbed by runtime symbol or receipt key | **PASS** | `{"contract_field": "deterministic_digest", "absorbed_by": "manifest_hash_receipt", "present_on_pa_surface": false, "present_in_pa_receipt…` |

## PA8_RULES

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PA.8 | `PA8_RULE::C0` | PA.8 rule `C0`: C0/tool/human text are data-only slots | **PASS** | `{"rule_keyword": "C0", "runtime_symbol": "detect_authority_violations", "present_in_doctrine": true, "present_in_runtime": true}` |
| 2 | PA.8 | `PA8_RULE::R0` | PA.8 rule `R0`: R0 schema is bound to provider-native fields | **PASS** | `{"rule_keyword": "R0", "runtime_symbol": "R0SchemaBinding", "present_in_doctrine": true, "present_in_runtime": true}` |
| 3 | PA.8 | `PA8_RULE::Provider` | PA.8 rule `Provider`: Provider rendering must not silently reorder authority slots | **PASS** | `{"rule_keyword": "Provider", "runtime_symbol": "render_for_provider", "present_in_doctrine": true, "present_in_runtime": true}` |
| 4 | PA.8 | `PA8_RULE::Token` | PA.8 rule `Token`: Token trimming must never drop S0/D0/required policy refs/R0 | **PASS** | `{"rule_keyword": "Token", "runtime_symbol": "BUDGET_TRIM_ORDER", "present_in_doctrine": true, "present_in_runtime": true}` |

## PA8_TESTS

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PA.8 | `PA8_TESTS::parsed` | PA.8 TEST REQUIREMENTS block parses at least one test name | **PASS** | `{"parsed_count": 6}` |
| 2 | PA.8 | `PA8_TEST::test_pa_blocks_c0_instruction_promotion` | PA.8 test `test_pa_blocks_c0_instruction_promotion` is covered (literal or equivalent) | **PASS** | `{"test_name": "test_pa_blocks_c0_instruction_promotion", "literal_present": true, "equivalents_matched": ["c0_instruction", "detect_autho…` |
| 3 | PA.8 | `PA8_TEST::test_pa_blocks_human_text_as_authority` | PA.8 test `test_pa_blocks_human_text_as_authority` is covered (literal or equivalent) | **PASS** | `{"test_name": "test_pa_blocks_human_text_as_authority", "literal_present": true, "equivalents_matched": ["human_text", "test_pa3_u0_airlo…` |
| 4 | PA.8 | `PA8_TEST::test_pa_schema_bound_native_not_only_prose` | PA.8 test `test_pa_schema_bound_native_not_only_prose` is covered (literal or equivalent) | **PASS** | `{"test_name": "test_pa_schema_bound_native_not_only_prose", "literal_present": true, "equivalents_matched": ["R0", "schema_binding", "tes…` |
| 5 | PA.8 | `PA8_TEST::test_pa_provider_render_preserves_slot_order` | PA.8 test `test_pa_provider_render_preserves_slot_order` is covered (literal or equivalent) | **PASS** | `{"test_name": "test_pa_provider_render_preserves_slot_order", "literal_present": true, "equivalents_matched": ["render_for_provider", "sl…` |
| 6 | PA.8 | `PA8_TEST::test_pa_token_trim_preserves_required_authority_slots` | PA.8 test `test_pa_token_trim_preserves_required_authority_slots` is covered (literal or equivalent) | **PASS** | `{"test_name": "test_pa_token_trim_preserves_required_authority_slots", "literal_present": true, "equivalents_matched": ["BUDGET_TRIM_ORDE…` |
| 7 | PA.8 | `PA8_TEST::test_pa_never_calls_retrieval_or_execution` | PA.8 test `test_pa_never_calls_retrieval_or_execution` is covered (literal or equivalent) | **PASS** | `{"test_name": "test_pa_never_calls_retrieval_or_execution", "literal_present": true, "equivalents_matched": ["MUST_NOT_FENCE", "test_doct…` |

## PARENT_VOCAB

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PARENT | `PARENT_VOCAB::parsed` | Parent doctrine STATUS VOCABULARY parsed at least one entry | **PASS** | `{"parsed_count": 19}` |
| 2 | PARENT | `PARENT_VOCAB::PA_READY` | Parent status `PA_READY` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_READY", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 3 | PARENT | `PARENT_VOCAB::PA_INPUT_INCOMPLETE` | Parent status `PA_INPUT_INCOMPLETE` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_INPUT_INCOMPLETE", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 4 | PARENT | `PARENT_VOCAB::PA_BOUNDARY_MISMATCH` | Parent status `PA_BOUNDARY_MISMATCH` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_BOUNDARY_MISMATCH", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 5 | PARENT | `PARENT_VOCAB::PA_BOM_RESOLVED` | Parent status `PA_BOM_RESOLVED` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_BOM_RESOLVED", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 6 | PARENT | `PARENT_VOCAB::PA_BOM_GAP` | Parent status `PA_BOM_GAP` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_BOM_GAP", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 7 | PARENT | `PARENT_VOCAB::PA_SLOTS_COMPOSED` | Parent status `PA_SLOTS_COMPOSED` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_SLOTS_COMPOSED", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 8 | PARENT | `PARENT_VOCAB::PA_SECURITY_PASS` | Parent status `PA_SECURITY_PASS` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_SECURITY_PASS", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 9 | PARENT | `PARENT_VOCAB::PA_SECURITY_GAP` | Parent status `PA_SECURITY_GAP` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_SECURITY_GAP", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 10 | PARENT | `PARENT_VOCAB::PA_SLOT_CONTRACT_VALID` | Parent status `PA_SLOT_CONTRACT_VALID` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_SLOT_CONTRACT_VALID", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 11 | PARENT | `PARENT_VOCAB::PA_SLOT_CONTRACT_INVALID` | Parent status `PA_SLOT_CONTRACT_INVALID` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_SLOT_CONTRACT_INVALID", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 12 | PARENT | `PARENT_VOCAB::PA_BUDGET_FIT` | Parent status `PA_BUDGET_FIT` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_BUDGET_FIT", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 13 | PARENT | `PARENT_VOCAB::PA_BUDGET_TRIMMED` | Parent status `PA_BUDGET_TRIMMED` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_BUDGET_TRIMMED", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 14 | PARENT | `PARENT_VOCAB::PA_BUDGET_OVERFLOW` | Parent status `PA_BUDGET_OVERFLOW` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_BUDGET_OVERFLOW", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 15 | PARENT | `PARENT_VOCAB::PA_RENDERED` | Parent status `PA_RENDERED` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_RENDERED", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 16 | PARENT | `PARENT_VOCAB::PA_RENDER_GAP` | Parent status `PA_RENDER_GAP` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_RENDER_GAP", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 17 | PARENT | `PARENT_VOCAB::PA_ARTIFACT_SIGNED` | Parent status `PA_ARTIFACT_SIGNED` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_ARTIFACT_SIGNED", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 18 | PARENT | `PARENT_VOCAB::PA_ARTIFACT_NOT_SIGNED` | Parent status `PA_ARTIFACT_NOT_SIGNED` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_ARTIFACT_NOT_SIGNED", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 19 | PARENT | `PARENT_VOCAB::PA_L2_HANDOFF_READY` | Parent status `PA_L2_HANDOFF_READY` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_L2_HANDOFF_READY", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |
| 20 | PARENT | `PARENT_VOCAB::PA_REQUIRES_UPSTREAM_REPAIR` | Parent status `PA_REQUIRES_UPSTREAM_REPAIR` exists in PAStatus and is claimed by at least one stage | **PASS** | `{"status": "PA_REQUIRES_UPSTREAM_REPAIR", "in_runtime_PAStatus": true, "claimed_by_stage": true}` |

## PARSER_EDGE_HARDENING

| # | Stage | ID | Requirement | Status | Evidence (truncated) |
|---:|---|---|---|:---:|---|
| 1 | PARENT | `PARSER_EDGE::trailing_colon_heading` | PARSER_EDGE/trailing_colon_heading: Heading with trailing colon is recognised | **PASS** | `{"case": "trailing_colon_heading", "args": ["STATUS VALUES"], "expected": ["One", "Two"], "actual": ["One", "Two"], "description": "Headi…` |
| 2 | PARENT | `PARSER_EDGE::tab_indented_bullet` | PARSER_EDGE/tab_indented_bullet: Tab-indented bullets are captured | **PASS** | `{"case": "tab_indented_bullet", "args": ["STATUS VALUES"], "expected": ["TabOne", "TabTwo"], "actual": ["TabOne", "TabTwo"], "description…` |
| 3 | PARENT | `PARSER_EDGE::asterisk_marker` | PARSER_EDGE/asterisk_marker: Asterisk-style bullets are captured | **PASS** | `{"case": "asterisk_marker", "args": ["STATUS VALUES"], "expected": ["Star1", "Star2"], "actual": ["Star1", "Star2"], "description": "Aste…` |
| 4 | PARENT | `PARSER_EDGE::unicode_bullet_marker` | PARSER_EDGE/unicode_bullet_marker: Unicode-bullet (U+2022) markers are captured | **PASS** | `{"case": "unicode_bullet_marker", "args": ["STATUS VALUES"], "expected": ["UniOne", "UniTwo"], "actual": ["UniOne", "UniTwo"], "descripti…` |
| 5 | PARENT | `PARSER_EDGE::heading_lookalike_in_prose` | PARSER_EDGE/heading_lookalike_in_prose: `STATUS VALUES` mid-prose does not start a section | **PASS** | `{"case": "heading_lookalike_in_prose", "args": ["STATUS VALUES"], "expected": [], "actual": [], "description": "`STATUS VALUES` mid-prose…` |
| 6 | PARENT | `PARSER_EDGE::heading_with_no_underline` | PARSER_EDGE/heading_with_no_underline: Heading without underline separator still captures bullets | **PASS** | `{"case": "heading_with_no_underline", "args": ["STATUS VALUES"], "expected": ["HeadOne", "HeadTwo"], "actual": ["HeadOne", "HeadTwo"], "d…` |
| 7 | PARENT | `PARSER_EDGE::csv_forbidden_block_split` | PARSER_EDGE/csv_forbidden_block_split: CSV-style forbidden bullet returns every comma-split token | **PASS** | `{"case": "csv_forbidden_block_split", "args": ["FORBIDDEN OUTPUTS FROM THIS CHILD"], "expected": ["ALPHA", "BETA", "GAMMA", "DELTA"], "ac…` |

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

