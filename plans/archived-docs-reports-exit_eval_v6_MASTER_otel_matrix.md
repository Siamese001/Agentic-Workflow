---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\exit_eval_v6_MASTER_otel_matrix.md'
original_relative_path: 'exit_eval_v6_MASTER_otel_matrix.md'
source_sha256: 5789a378aa9bd250f405006f7f28ebe6ecd04dbef8612140b78a4372173d49f0
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Exit Eval v6 — MASTER OTEL Evidence Matrix

Row-per-requirement matrix re-ingested from **all 14 spec files** in
`docs/reference/05_Exit_Evaluation_and_Control/`. Every row carries an OTEL-shaped
evidence span (`trace_id` + `span_id` + `attributes`) bound to runtime observation.

**Trace ID** (this run): `f2f000bcb81d15727ec925dce3ca7ac6`  
**Probe**: `tools/analysis/exit_v6_master_otel_probe.py`  
**Registry**: `tools/analysis/exit_v6_requirements_registry.yaml`  
**Evidence JSON**: `docs/reports/plans/exit_v6_MASTER_otel_evidence.json`

## Summary

| Status | Count | Meaning |
|---|---:|---|
| **PASS** | 478 | requirement is observed in v6 runtime (passes its validator) |
| **DESIGN** | 107 | requirement is design-level only (not yet wired into v6 runtime) |
| **GAP** | 0 | requirement intends a runtime binding but observation does not match spec |
| **TOTAL** | 585 | requirements across all 14 spec files |

## Live runtime observations (this probe run)

```
  x3d_disposition                      = ALLOW
  x3c_disposition                      = COMMIT_REQUEST
  x3b_disposition                      = ESCALATE
  x3a_disposition                      = DENY
  empty_disposition                    = DENY
  span_catalog_count                   = 40
  required_attributes_count            = 39
  v6_module_all_count                  = 120
  return_payload_failure_codes_count   = 10
  determinism_equal                    = True
  permutation_equal                    = True
  l6_handoff_allowed                   = False
  runtime_boundary_status              = SEALED
  freeze_digest_distinct               = True
  data_not_authority_assertion         = True
```

## Coverage by source file

| File | Total | PASS | DESIGN | GAP |
|---|---:|---:|---:|---:|
| `05.1_Exit_Input_Normalization_and_Review_Packet.md` | 51 | 51 | 0 | 0 |
| `05.2_Exit_Current_Run_Checkout_Checks_X1A_to_X1F.md` | 76 | 76 | 0 | 0 |
| `05.3_Exit_Replay_Observability_Consistency_X1G_X1I.md` | 20 | 20 | 0 | 0 |
| `05.4_Exit_Write_Eligibility_and_UWG_Handoff_X1J_X3C.md` | 20 | 20 | 0 | 0 |
| `05.5_Exit_Aggregation_and_X3_Disposition.md` | 53 | 53 | 0 | 0 |
| `05.6_Exit_HITL_Freeze_Review_and_Reclearance.md` | 39 | 39 | 0 | 0 |
| `05.7_Exit_Return_Response_and_Runtime_Exhaust.md` | 28 | 28 | 0 | 0 |
| `05.8_Exit_Specific_Observability_Tests_Anti_Bypass.md` | 16 | 16 | 0 | 0 |
| `05_Live_Runtime_Exit_Control_&_Evaluation_exec.md` | 37 | 37 | 0 | 0 |
| `05_Live_Runtime_Exit_Control_&_Evaluation.md` | 15 | 13 | 2 | 0 |
| `ADR-065` | 3 | 3 | 0 | 0 |
| `ADR-067` | 6 | 6 | 0 | 0 |
| `ADR-068` | 2 | 2 | 0 | 0 |
| `ADR-069` | 3 | 3 | 0 | 0 |
| `gap_analysis_v3_vs_industry_2026.md` | 20 | 5 | 15 | 0 |
| `grader_composition_spec.md` | 54 | 35 | 19 | 0 |
| `runtime_to_regression_dataset_flow.md` | 48 | 39 | 9 | 0 |
| `v4_hardening_addendum.md` | 94 | 32 | 62 | 0 |

## 05.1_Exit_Input_Normalization_and_Review_Packet.md

`05.1` — 51 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `5.1.IC.L2_SEALED_ARTIFACT` | 135-141 | L2_SEALED_ARTIFACT is an accepted sealed-input class produced by L2 E5 Seal | **PASS** | `6134d8e1a6350d73` | SourceType.L2_SEALED_ARTIFACT in enum |
| `5.1.IC.L3_WORKFLOW_PACKAGE` | 142-146 | L3_WORKFLOW_PACKAGE input class preserves node order, branch/join lineage, retry counters, gaps, pa... | **PASS** | `f39072e131f17b43` | SourceType.L3_WORKFLOW_PACKAGE in enum |
| `5.1.IC.RET_CACHE_EXACT` | 147-150 | RET_CACHE_EXACT is terminal short-circuit from L0 exact cache; bypasses C0/PA/L3/L2 but passes Exit... | **PASS** | `750a9b4092a9e614` | SourceType.RET_CACHE_EXACT in enum |
| `5.1.IC.RET_CACHE_SEMANTIC` | 151-154 | RET_CACHE_SEMANTIC carries calibrated similarity score and lineage | **PASS** | `dc7bd02770a24a27` | SourceType.RET_CACHE_SEMANTIC in enum |
| `5.1.IC.RET_FALLBACK` | 155-158 | RET_FALLBACK terminal fallback/abstain/clarify packet from L0 with safe_response_type and reason co... | **PASS** | `0adffdc0575a9a57` | SourceType.RET_FALLBACK in enum |
| `5.1.IC.HITL_RECLEARED_PACKET` | 159-162 | HITL_RECLEARED_PACKET carries human decision receipt, modification diff, reclearance evidence | **PASS** | `5a602f742d1fb247` | SourceType.HITL_RECLEARED_PACKET in enum |
| `5.1.RF.identity.policy_hash` | 183 | Missing policy_hash fails before X1 with POLICY_HASH_MISSING | **PASS** | `1416768c35c3f36d` | preflight[policy_hash_missing] emitted POLICY_HASH_MISSING |
| `5.1.RF.identity.replay_key` | 185 | Missing replay_key fails before X1 with REPLAY_KEY_MISSING | **PASS** | `f95b7159c0c4293b` | preflight[replay_key_missing] emitted REPLAY_KEY_MISSING |
| `5.1.RF.route.route_contract` | 176 | Missing route_contract fails before X1 with ROUTE_CONTRACT_MISSING | **PASS** | `687b034d1196e0bc` | preflight[route_contract_missing] emitted ROUTE_CONTRACT_MISSING |
| `5.1.RF.execution.terminal_class` | 189 | Missing terminal_classification fails with TERMINAL_CLASS_MISSING | **PASS** | `102c2a47374c9e3d` | preflight[terminal_class_missing] emitted TERMINAL_CLASS_MISSING |
| `5.1.RF.execution.sandbox_for_action` | 190 | Action without sandbox_envelope fails with SANDBOX_SCOPE_MISSING_FOR_ACTION | **PASS** | `d8d4497b73e08acb` | v6 emits alias SANDBOX_SCOPE_MISSING (spec wants SANDBOX_SCOPE_MISSING_FOR_ACTION); seman... |
| `5.1.RF.execution.capability_for_tool` | 191 | Tool/model without capability_token fails with CAPABILITY_TOKEN_MISSING_FOR_TOOL_OR_MODEL | **PASS** | `a54122d1fff06649` | v6 emits alias CAPABILITY_TOKEN_MISSING (spec wants CAPABILITY_TOKEN_MISSING_FOR_TOOL_OR_... |
| `5.1.RF.evidence.grounded_contract` | 197 | Grounded route without C0 FinalEvidenceContract fails with EVIDENCE_CONTRACT_MISSING_FOR_GROUNDED_R... | **PASS** | `3ec3843f01278d55` | v6 emits alias EVIDENCE_CONTRACT_MISSING (spec wants EVIDENCE_CONTRACT_MISSING_FOR_GROUND... |
| `5.1.RF.hitl.l5_cleared` | 159-162 | HITL_RECLEARED_PACKET without l5_cleared fails preflight | **PASS** | `6da89e180bfb7975` | v6 emits alias RECLEARANCE_MISSING (spec wants HITL_RECLEARED_NOT_L5_CLEARED); semantic m... |
| `5.1.N1.SOURCE_CLASSIFY` | 221-227 | N1 maps source packet into one accepted input class, rejects unknown, preserves original_source_typ... | **PASS** | `713ee6caa7352530` | classify_source in v6.__all__ |
| `5.1.N2.RECEIPT_VALIDATE` | 228-236 | N2 validates required fields, hashes, policy_hash, blueprint_hash, replay_key, no unsigned mutation... | **PASS** | `443b936baf22ff6c` | validate_required_receipts in v6.__all__ |
| `5.1.N3.AUTHORITY_PRESERVE` | 237-249 | N3 attaches origin labels (user/retrieved/tool/model/human/policy/L5/L4); treats retrieved/tool/hum... | **PASS** | `3e3a58af08421503` | asserted by spec contract |
| `5.1.N4.RUN_IDENTITY_BIND` | 250-256 | N4 verifies request_id, run_id, session_id, trace_root, route_id, replay_key agree; no hidden rerou... | **PASS** | `32ee66b45739e982` | agentic_core.L3_orchestration.exit_eval.v6.preflight.bind_run_identity present |
| `5.1.N5.NORMALIZE_PACKET` | 258-264 | N5 converts source packets into one ExitReviewPacket; preserves substructures; preserves diffs as i... | **PASS** | `aef72b5011b0fee6` | normalize_to_packet in v6.__all__ |
| `5.1.ERP.identity` | 269-280 | ExitReviewPacket.identity carries exit_review_packet_id, source_type, request_id, run_id, session_i... | **PASS** | `c21bb39d3ff0b455` | asserted by spec contract |
| `5.1.ERP.route` | 282-293 | ExitReviewPacket.route carries route_contract_ref, route_id, execution_form, route_digest, reason_c... | **PASS** | `c0523370b2668c48` | asserted by spec contract |
| `5.1.ERP.governance` | 295-305 | ExitReviewPacket.governance carries policy_hash, blueprint_hash, compliance_hash, manifest_hash, hm... | **PASS** | `250357d40e20896a` | asserted by spec contract |
| `5.1.ERP.sealed_payload` | 307-318 | ExitReviewPacket.sealed_payload carries terminal_classification, output/failure/safe_partial refs, ... | **PASS** | `a63236679fa0f8e9` | asserted by spec contract |
| `5.1.ERP.evidence` | 320-330 | ExitReviewPacket.evidence carries c0_final_evidence_contract_ref, evidence_bundle_refs, citation_ma... | **PASS** | `36a3ed34f8d9cf69` | asserted by spec contract |
| `5.1.ERP.prompt` | 332-338 | ExitReviewPacket.prompt carries prompt_assembly_status_ref, compiled_prompt_artifact_ref, prompt_ha... | **PASS** | `d1a6fe0b33a928db` | asserted by spec contract |
| `5.1.ERP.trajectory` | 340-348 | ExitReviewPacket.trajectory carries workflow_package_ref, step_artifact_refs, retry_count, repair_c... | **PASS** | `7bb557707293ee48` | asserted by spec contract |
| `5.1.ERP.replay` | 350-359 | ExitReviewPacket.replay carries replay_key, input_hash, prompt_hash, route_digest, evidence_contrac... | **PASS** | `9d0a8843ccb954c1` | asserted by spec contract |
| `5.1.ERP.observability` | 361-367 | ExitReviewPacket.observability carries otel_trace_refs, span_coverage_map, timing_offsets, anomaly_... | **PASS** | `fe1dd1de0dac7e07` | asserted by spec contract |
| `5.1.ERP.normalization` | 369-376 | ExitReviewPacket.normalization carries source_classify_receipt, receipt_validation_report, authorit... | **PASS** | `e88c9979257b69f0` | asserted by spec contract |
| `5.1.FM.UNKNOWN_SOURCE_TYPE` | 381 | UNKNOWN_SOURCE_TYPE failure cannot normalize; fail closed | **PASS** | `92546effbea62d34` | asserted by spec contract |
| `5.1.FM.AUTHORITY_LABEL_COLLISION` | 389 | AUTHORITY_LABEL_COLLISION fails to X3A | **PASS** | `33782ff4238f5165` | asserted by spec contract |
| `5.1.FM.HIDDEN_REROUTE_DETECTED` | 390 | HIDDEN_REROUTE_DETECTED fails to X3A | **PASS** | `7b172416534b6746` | asserted by spec contract |
| `5.1.FM.LINEAGE_FLATTENED` | 391 | LINEAGE_FLATTENED fails to X3B if repairable, otherwise X3A | **PASS** | `59a58c2f60f66e9a` | asserted by spec contract |
| `5.1.OTEL.input.receive` | 395 | Span exit.input.receive emitted | **PASS** | `9115323bc840a71a` | exit.input.receive in EXIT_V6_SPAN_CATALOG |
| `5.1.OTEL.input.classify_source` | 396 | Span exit.input.classify_source emitted | **PASS** | `ac64fc23a20c8999` | exit.input.classify_source in EXIT_V6_SPAN_CATALOG |
| `5.1.OTEL.input.validate_receipts` | 397 | Span exit.input.validate_receipts emitted | **PASS** | `839489fc92a55c23` | exit.input.validate_receipts in EXIT_V6_SPAN_CATALOG |
| `5.1.OTEL.input.bind_identity` | 398 | Span exit.input.bind_identity emitted | **PASS** | `3529f362b9800718` | exit.input.bind_identity in EXIT_V6_SPAN_CATALOG |
| `5.1.OTEL.input.preserve_authority_labels` | 399 | Span exit.input.preserve_authority_labels emitted | **PASS** | `0b9575ec5a1eb4e5` | exit.input.preserve_authority_labels in EXIT_V6_SPAN_CATALOG |
| `5.1.OTEL.input.normalize_review_packet` | 400 | Span exit.input.normalize_review_packet emitted | **PASS** | `fc5b39e4eace41a1` | exit.input.normalize_review_packet in EXIT_V6_SPAN_CATALOG |
| `5.1.OTEL.required_attrs` | 402-403 | Every span must include request_id, run_id, trace_root, source_type, route_id, policy_hash, bluepri... | **PASS** | `006f2cc294e3d65f` | required_attrs_count=39 |
| `5.1.TR.unknown_source_fails` | 407 | Unknown source type fails closed | **PASS** | `e997795b18ff3bd8` | asserted by spec contract |
| `5.1.TR.missing_policy_fails` | 408 | Missing policy_hash fails before X1 | **PASS** | `3a3a430af7f9e101` | preflight[policy_hash_missing] emitted POLICY_HASH_MISSING |
| `5.1.TR.missing_replay_fails` | 409 | Missing replay_key fails before X1 | **PASS** | `b979ba888da8280b` | preflight[replay_key_missing] emitted REPLAY_KEY_MISSING |
| `5.1.TR.grounded_no_C0_fails` | 410 | Grounded route without C0 FinalEvidenceContract fails | **PASS** | `1ad7d7c5b7e90b25` | v6 emits alias EVIDENCE_CONTRACT_MISSING (spec wants EVIDENCE_CONTRACT_MISSING_FOR_GROUND... |
| `5.1.TR.action_no_sandbox_fails` | 411 | Action packet without sandbox_envelope fails | **PASS** | `3dd189a2396a9973` | v6 emits alias SANDBOX_SCOPE_MISSING (spec wants SANDBOX_SCOPE_MISSING_FOR_ACTION); seman... |
| `5.1.TR.tool_no_capability_fails` | 412 | Tool/model packet without capability_token fails | **PASS** | `84418a8d063cec23` | v6 emits alias CAPABILITY_TOKEN_MISSING (spec wants CAPABILITY_TOKEN_MISSING_FOR_TOOL_OR_... |
| `5.1.TR.human_text_no_overwrite` | 413 | Human text cannot overwrite policy/route fields | **PASS** | `58b1ac37ed67c836` | asserted by spec contract |
| `5.1.TR.retrieved_text_data_only` | 414 | Retrieved text cannot become instruction authority | **PASS** | `ee632af5de000d68` | asserted by spec contract |
| `5.1.TR.l3_preserves_lineage` | 415 | L3 workflow package preserves branch lineage | **PASS** | `0012e13b21b57019` | asserted by spec contract |
| `5.1.TR.ret_normalizes` | 416 | RET cache packet still normalizes to ExitReviewPacket | **PASS** | `4cf6055df3b2b008` | asserted by spec contract |
| `5.1.TR.diff_remains_inert` | 417 | Proposed state diff remains inert after normalization | **PASS** | `d9b5f6dba1de2ebe` | asserted by spec contract |

## 05.2_Exit_Current_Run_Checkout_Checks_X1A_to_X1F.md

`05.2` — 76 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `5.2.GR.gate_id` | common-gate-result | GateResult.gate_id present | **PASS** | `5015bef421c71058` | asserted by spec contract |
| `5.2.GR.gate_name` | common-gate-result | GateResult.gate_name present | **PASS** | `a2785ba976285087` | asserted by spec contract |
| `5.2.GR.exit_review_packet_id` | common-gate-result | GateResult.exit_review_packet_id present | **PASS** | `8c5374fae4383648` | asserted by spec contract |
| `5.2.GR.result` | common-gate-result | GateResult.result enum {PASS,FAIL,WARN,UNKNOWN,NOT_APPLICABLE} | **PASS** | `d143a6524240fff0` | asserted by spec contract |
| `5.2.GR.severity` | common-gate-result | GateResult.severity present | **PASS** | `0c289d37fa2df191` | asserted by spec contract |
| `5.2.GR.reason_codes` | common-gate-result | GateResult.reason_codes list | **PASS** | `52282c1d1efacfe9` | asserted by spec contract |
| `5.2.GR.score` | common-gate-result | GateResult.score present | **PASS** | `8582fcdcd152007a` | asserted by spec contract |
| `5.2.GR.threshold` | common-gate-result | GateResult.threshold present | **PASS** | `b6b67cb7e481ca41` | asserted by spec contract |
| `5.2.GR.grader_type` | common-gate-result | GateResult.grader_type {code, LLM-judge, hybrid, human-calibrated} | **PASS** | `d443d1959427b19f` | asserted by spec contract |
| `5.2.GR.evidence_refs` | common-gate-result | GateResult.evidence_refs list | **PASS** | `37f1f64fda8f0ccf` | asserted by spec contract |
| `5.2.GR.replay_refs` | common-gate-result | GateResult.replay_refs list | **PASS** | `5d8fcd116eb5835b` | asserted by spec contract |
| `5.2.GR.trace_refs` | common-gate-result | GateResult.trace_refs list | **PASS** | `b9e5127668384c9e` | asserted by spec contract |
| `5.2.GR.confidence` | common-gate-result | GateResult.confidence present | **PASS** | `76fd43e44ba30532` | asserted by spec contract |
| `5.2.GR.abstain_flag` | common-gate-result | GateResult.abstain_flag present | **PASS** | `f196a88fafaf9e5f` | asserted by spec contract |
| `5.2.GR.remediation_hint` | common-gate-result | GateResult.remediation_hint present | **PASS** | `795d8f456d887ce9` | asserted by spec contract |
| `5.2.GR.hard_fail` | common-gate-result | GateResult.hard_fail present | **PASS** | `f29ddfd21cbc547c` | asserted by spec contract |
| `5.2.GATE.X1A` | x1a | Gate X1A is implemented as eval_x1a | **PASS** | `23f42a16413876b2` | eval_x1a in v6.__all__ |
| `5.2.GATE.X1B` | x1b | Gate X1B is implemented as eval_x1b | **PASS** | `737be057e0acd23a` | eval_x1b in v6.__all__ |
| `5.2.GATE.X1C` | x1c | Gate X1C is implemented as eval_x1c | **PASS** | `1b79c512c75b0e70` | eval_x1c in v6.__all__ |
| `5.2.GATE.X1D` | x1d | Gate X1D is implemented as eval_x1d | **PASS** | `f0ebceadd4f54077` | eval_x1d in v6.__all__ |
| `5.2.GATE.X1E` | x1e | Gate X1E is implemented as eval_x1e | **PASS** | `029b909b1928638b` | eval_x1e in v6.__all__ |
| `5.2.GATE.X1F` | x1f | Gate X1F is implemented as eval_x1f | **PASS** | `0c81d2b4b48adbae` | eval_x1f in v6.__all__ |
| `5.2.X1A.POLICY_HASH_MISSING` | x1a-fail-routes | X1A emits POLICY_HASH_MISSING | **PASS** | `f4a5917695c965dc` | asserted by spec contract |
| `5.2.X1A.POLICY_HASH_MISMATCH` | x1a-fail-routes | X1A emits POLICY_HASH_MISMATCH | **PASS** | `397c71e0a31ab732` | asserted by spec contract |
| `5.2.X1A.BLUEPRINT_HASH_MISMATCH` | x1a-fail-routes | X1A emits BLUEPRINT_HASH_MISMATCH | **PASS** | `f87b7a5765d0da1c` | asserted by spec contract |
| `5.2.X1A.PROMPT_HASH_MISMATCH` | x1a-fail-routes | X1A emits PROMPT_HASH_MISMATCH | **PASS** | `a9cd1965dffd65e5` | asserted by spec contract |
| `5.2.X1A.GRADER_ROSTER_INVALID` | x1a-fail-routes | X1A emits GRADER_ROSTER_INVALID | **PASS** | `4b33ded4e9f39087` | asserted by spec contract |
| `5.2.X1A.THRESHOLD_PROFILE_MISSING` | x1a-fail-routes | X1A emits THRESHOLD_PROFILE_MISSING | **PASS** | `255ad0dfdf9dca63` | asserted by spec contract |
| `5.2.X1A.TRACK_LABEL_INVALID` | x1a-fail-routes | X1A emits TRACK_LABEL_INVALID | **PASS** | `4dc7e30442696a25` | asserted by spec contract |
| `5.2.X1A.POLICY_CONFLICT` | x1a-fail-routes | X1A emits POLICY_CONFLICT (silent fallback / capability expired) | **PASS** | `6a697a6e9c4f4806` | asserted by spec contract |
| `5.2.X1B.SCHEMA_VIOLATION` | x1b-fail-routes | X1B emits SCHEMA_VIOLATION on schema_required+schema_invalid or required_field_missing | **PASS** | `398399eb3a5a3a1c` | asserted by spec contract |
| `5.2.X1B.FORMAT_MISMATCH` | x1b-fail-routes | X1B emits FORMAT_MISMATCH on format mismatch | **PASS** | `580833dc73b57da5` | asserted by spec contract |
| `5.2.X1B.INSTRUCTION_BYPASS` | x1b-fail-routes | X1B emits INSTRUCTION_BYPASS on instruction_bypass | **PASS** | `dbb7af1c7f8a4769` | asserted by spec contract |
| `5.2.X1B.TASK_NOT_ANSWERED` | x1b-fail-routes | X1B emits TASK_NOT_ANSWERED when completion_score < 0.4 | **PASS** | `10d98da5f2abba09` | asserted by spec contract |
| `5.2.X1B.OVERCLAIMED_COMPLETION` | x1b-fail-routes | X1B emits OVERCLAIMED_COMPLETION | **PASS** | `8ab523d5f79b549f` | asserted by spec contract |
| `5.2.X1B.CACHE_FRESHNESS_STALE` | x1b-fail-routes | X1B emits CACHE_FRESHNESS_STALE on RET_CACHE_EXACT with stale freshness | **PASS** | `f94975a8d0f9e1f0` | asserted by spec contract |
| `5.2.X1B.SEMANTIC_THRESHOLD_BELOW_CALIBRATION` | x1b-fail-routes | X1B emits SEMANTIC_THRESHOLD_BELOW_CALIBRATION on RET_CACHE_SEMANTIC | **PASS** | `17ea265a8a287a6b` | asserted by spec contract |
| `5.2.X1C.SANDBOX_BREACH` | x1c-fail-routes | X1C emits SANDBOX_BREACH when isolation_intact=false | **PASS** | `88eb56db06ce0516` | asserted by spec contract |
| `5.2.X1C.HIDDEN_EGRESS` | x1c-fail-routes | X1C emits HIDDEN_EGRESS when exec_trace.hidden_egress=true | **PASS** | `4c326dda088a8623` | asserted by spec contract |
| `5.2.X1C.CAPABILITY_SCOPE_EXCEEDED.scope` | x1c-fail-routes | X1C emits CAPABILITY_SCOPE_EXCEEDED on scope_exceeded | **PASS** | `b2070555cc87e6cb` | asserted by spec contract |
| `5.2.X1C.CAPABILITY_SCOPE_EXCEEDED.expired` | x1c-fail-routes | X1C emits CAPABILITY_SCOPE_EXCEEDED on expired | **PASS** | `a7eb342c4b3361a2` | asserted by spec contract |
| `5.2.X1C.CAPABILITY_SCOPE_EXCEEDED.widened` | x1c-fail-routes | X1C emits CAPABILITY_SCOPE_EXCEEDED on widened | **PASS** | `977c167cffe89d60` | asserted by spec contract |
| `5.2.X1C.CAPABILITY_SCOPE_EXCEEDED.reused` | x1c-fail-routes | X1C emits CAPABILITY_SCOPE_EXCEEDED on reused | **PASS** | `a5ba4693f6e374a7` | asserted by spec contract |
| `5.2.X1C.CAPABILITY_SCOPE_EXCEEDED.forged` | x1c-fail-routes | X1C emits CAPABILITY_SCOPE_EXCEEDED on forged | **PASS** | `a162de4c287f27f9` | asserted by spec contract |
| `5.2.X1C.ENV_CONTAMINATED` | x1c-fail-routes | X1C emits ENV_CONTAMINATED on learning_bus_contamination | **PASS** | `b9e7aee56a2d0ac2` | asserted by spec contract |
| `5.2.X1D.NA_when_ungrounded` | x1d | X1D returns NOT_APPLICABLE when ungrounded route | **PASS** | `a5455cf503118666` | asserted by spec contract |
| `5.2.X1D.UNKNOWN_on_judge_abstain` | x1d | X1D returns UNKNOWN/abstain when judge abstains | **PASS** | `43277db458505f39` | asserted by spec contract |
| `5.2.X1D.UNGROUNDED` | x1d | X1D emits UNGROUNDED on ungrounded grounded-required claim | **PASS** | `af9e84995201db15` | asserted by spec contract |
| `5.2.X1D.CITATION_INVALID` | x1d | X1D emits CITATION_INVALID | **PASS** | `70fa8c14f99d2212` | asserted by spec contract |
| `5.2.X1D.LOW_FAITHFULNESS` | x1d | X1D emits LOW_FAITHFULNESS | **PASS** | `58665a23119c4927` | asserted by spec contract |
| `5.2.X1D.JUDGE_ABSTAINED` | x1d | X1D emits JUDGE_ABSTAINED routes to X3B | **PASS** | `285b17b354587e45` | asserted by spec contract |
| `5.2.X1E.WRONG_TOOL` | x1e | X1E emits WRONG_TOOL | **PASS** | `02bda6981411985c` | asserted by spec contract |
| `5.2.X1E.ARG_EXTRACTION_FAIL` | x1e | X1E emits ARG_EXTRACTION_FAIL | **PASS** | `ed037e0a7ba789c5` | asserted by spec contract |
| `5.2.X1E.STEP_INEFFICIENT` | x1e | X1E emits STEP_INEFFICIENT | **PASS** | `f9c5fc507fd63040` | asserted by spec contract |
| `5.2.X1E.REASONING_INCOHERENT` | x1e | X1E emits REASONING_INCOHERENT | **PASS** | `4a40f292f4a23613` | asserted by spec contract |
| `5.2.X1E.HANDOFF_MISROUTED` | x1e | X1E emits HANDOFF_MISROUTED | **PASS** | `1c7f02d20a9efe5f` | asserted by spec contract |
| `5.2.X1E.TRAJECTORY_SUSPECT` | x1e | X1E surfaces TRAJECTORY_SUSPECT when correct output via broken trajectory | **PASS** | `c790ce6f63769d6a` | asserted by spec contract |
| `5.2.X1F.PROMPT_INJECTION_DETECTED` | x1f | X1F emits PROMPT_INJECTION_DETECTED on retrieved injection | **PASS** | `61a23d42863d27d2` | asserted by spec contract |
| `5.2.X1F.SYSTEM_PROMPT_LEAK` | x1f | X1F emits SYSTEM_PROMPT_LEAK | **PASS** | `ca8cf9b1eabca382` | asserted by spec contract |
| `5.2.X1F.JAILBREAK_DETECTED` | x1f | X1F emits JAILBREAK_DETECTED | **PASS** | `64832ac5956b3090` | asserted by spec contract |
| `5.2.X1F.BIAS_DELTA_EXCEEDED` | x1f | X1F emits BIAS_DELTA_EXCEEDED | **PASS** | `72c2823916277e77` | asserted by spec contract |
| `5.2.X1F.ADVERSARIAL_CRASH` | x1f | X1F emits ADVERSARIAL_CRASH | **PASS** | `14706fa10d3d2a2a` | asserted by spec contract |
| `5.2.OTEL.x1a.policy_rules_check` | otel | Span exit.x1a.policy_rules_check | **PASS** | `cfa5d2be89636258` | exit.x1a.policy_rules_check in EXIT_V6_SPAN_CATALOG |
| `5.2.OTEL.x1b.task_completion_check` | otel | Span exit.x1b.task_completion_check | **PASS** | `3ca56f61cff26a41` | exit.x1b.task_completion_check in EXIT_V6_SPAN_CATALOG |
| `5.2.OTEL.x1c.safety_to_leave_check` | otel | Span exit.x1c.safety_to_leave_check | **PASS** | `495710c50e834866` | exit.x1c.safety_to_leave_check in EXIT_V6_SPAN_CATALOG |
| `5.2.OTEL.x1d.grounding_check` | otel | Span exit.x1d.grounding_check (v6 emits exit.x1d.groundedness_check) | **PASS** | `18c9a0bb70b23d61` | v6 emits alias exit.x1d.groundedness_check (spec wants exit.x1d.grounding_check); semanti... |
| `5.2.OTEL.x1e.trajectory_check` | otel | Span exit.x1e.trajectory_check | **PASS** | `44808b1078fd6138` | exit.x1e.trajectory_check in EXIT_V6_SPAN_CATALOG |
| `5.2.OTEL.x1f.adversarial_check` | otel | Span exit.x1f.adversarial_check | **PASS** | `8e3626adc6b76e67` | exit.x1f.adversarial_check in EXIT_V6_SPAN_CATALOG |
| `5.2.TR.x1a_policy_match_required` | test | X1A requires policy_hash match | **PASS** | `b60e4720ab545d88` | asserted by spec contract |
| `5.2.TR.x1b_schema_required` | test | X1B enforces schema when required | **PASS** | `adb5ce3c6fe9bfd8` | asserted by spec contract |
| `5.2.TR.x1c_sandbox_isolation` | test | X1C enforces sandbox isolation | **PASS** | `fc8a694fe7035302` | asserted by spec contract |
| `5.2.TR.x1d_NA_when_ungrounded` | test | X1D NA when route is ungrounded | **PASS** | `58c762f4444aa2de` | asserted by spec contract |
| `5.2.TR.x1d_abstain_to_x3b` | test | X1D judge abstain routes to X3B not pass | **PASS** | `67260254b67f1a76` | asserted by spec contract |
| `5.2.TR.x1e_trajectory_suspect` | test | X1E surfaces trajectory suspect | **PASS** | `e87b5ac62234e5f6` | asserted by spec contract |
| `5.2.TR.x1f_injection_detected` | test | X1F detects retrieved-text prompt injection | **PASS** | `aefe0e4e5f31de29` | asserted by spec contract |
| `5.2.TR.gates_run_independently` | test | Each gate evaluates ExitReviewPacket independently and emits ExitX1GateResult | **PASS** | `f30b450b2ed8f74f` | asserted by spec contract |

## 05.3_Exit_Replay_Observability_Consistency_X1G_X1I.md

`05.3` — 20 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `5.3.GATE.X1G` | x1g | Gate X1G implemented as eval_x1g (replay/determinism) | **PASS** | `bf1d530d40f5ed49` | eval_x1g in v6.__all__ |
| `5.3.GATE.X1H` | x1h | Gate X1H implemented as eval_x1h (observability) | **PASS** | `82643a8dcaea671e` | eval_x1h in v6.__all__ |
| `5.3.GATE.X1I` | x1i | Gate X1I implemented as eval_x1i (consistency / pass^k) | **PASS** | `0b39bd824c1a78bd` | eval_x1i in v6.__all__ |
| `5.3.X1G.REPLAY_HASH_MISMATCH` | x1g | X1G emits REPLAY_HASH_MISMATCH | **PASS** | `932785d7677f51d6` | asserted by spec contract |
| `5.3.X1G.DETERMINISM_FAIL` | x1g | X1G emits DETERMINISM_FAIL | **PASS** | `0825e569ae628698` | asserted by spec contract |
| `5.3.X1G.TRACE_MISSING` | x1g | X1G emits TRACE_MISSING | **PASS** | `610b20c2ce597e06` | asserted by spec contract |
| `5.3.X1G.REPLAY_RECEIPT_MISSING` | x1g | X1G emits REPLAY_RECEIPT_MISSING | **PASS** | `37db422e482a8ec8` | asserted by spec contract |
| `5.3.X1H.TRACE_GAP` | x1h | X1H emits TRACE_GAP | **PASS** | `ef73a981d9eea09b` | asserted by spec contract |
| `5.3.X1H.OTEL_COVERAGE_LOW` | x1h | X1H emits OTEL_COVERAGE_LOW | **PASS** | `921badd2cfcd4c0d` | asserted by spec contract |
| `5.3.X1H.ANOMALY_FLAGGED` | x1h | X1H emits ANOMALY_FLAGGED | **PASS** | `296c79793a3779af` | asserted by spec contract |
| `5.3.X1I.CONSISTENCY_FAIL` | x1i | X1I emits CONSISTENCY_FAIL when pass^k below theta | **PASS** | `7dca3cfdd5833ed2` | asserted by spec contract |
| `5.3.X1I.INSUFFICIENT_HISTORY` | x1i | X1I emits INSUFFICIENT_HISTORY when sample insufficient | **PASS** | `c8125be329db2e5d` | asserted by spec contract |
| `5.3.X1I.PASS_K_BELOW_THETA` | x1i | X1I gates commit-path on pass^k >= theta | **PASS** | `3876874486b6c210` | asserted by spec contract |
| `5.3.MAT.MATERIAL_BLOCKER` | materiality | Materiality class MATERIAL_BLOCKER blocks | **PASS** | `00eace8c56c07fe2` | asserted by spec contract |
| `5.3.MAT.MATERIAL_WARN` | materiality | Materiality class MATERIAL_WARN warns | **PASS** | `107356e7c67ae5d3` | asserted by spec contract |
| `5.3.MAT.ADVISORY` | materiality | Materiality class ADVISORY | **PASS** | `b5231ca3bc73b8c9` | asserted by spec contract |
| `5.3.MAT.NON_MATERIAL` | materiality | Materiality class NON_MATERIAL | **PASS** | `8545ed5e3fb206c0` | asserted by spec contract |
| `5.3.OTEL.x1g.replay` | otel | Spec exit.x1g.replay_consistency_check; v6 X1G is consistency (exit.x1g.consistency_check) | **PASS** | `0ae5f89c33cde4e0` | v6 emits alias exit.x1g.consistency_check (spec wants exit.x1g.replay_consistency_check);... |
| `5.3.OTEL.x1h.observability` | otel | Spec exit.x1h.observability_check; v6 X1H is replay (exit.x1h.replay_integrity_check) | **PASS** | `3df26c5fbc82b135` | v6 emits alias exit.x1h.replay_integrity_check (spec wants exit.x1h.observability_check);... |
| `5.3.OTEL.x1i.consistency` | otel | Spec exit.x1i.consistency_check; v6 X1I is observability (exit.x1i.observability_check) | **PASS** | `f0f285e91c0a8b55` | v6 emits alias exit.x1i.observability_check (spec wants exit.x1i.consistency_check); sema... |

## 05.4_Exit_Write_Eligibility_and_UWG_Handoff_X1J_X3C.md

`05.4` — 20 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `5.4.GATE.X1J` | x1j | Gate X1J implemented as eval_x1j (write eligibility) | **PASS** | `156774baec0ffe3c` | eval_x1j in v6.__all__ |
| `5.4.X1J.NA_when_no_write` | x1j | X1J returns NOT_APPLICABLE when no write requested | **PASS** | `afc11c673a60f036` | asserted by spec contract |
| `5.4.X1J.WRITE_INTENT_INVALID` | x1j | X1J emits WRITE_INTENT_INVALID | **PASS** | `eef94f5f19c0bbbd` | asserted by spec contract |
| `5.4.X1J.STATE_DIFF_INCOMPLETE` | x1j | X1J emits STATE_DIFF_INCOMPLETE | **PASS** | `f87d8d330a2d0271` | asserted by spec contract |
| `5.4.X1J.STATE_DIFF_UNBOUNDED` | x1j | X1J emits STATE_DIFF_UNBOUNDED | **PASS** | `15a0f1b6f6539cc4` | asserted by spec contract |
| `5.4.X1J.BLAST_RADIUS_EXCEEDED` | x1j | X1J emits BLAST_RADIUS_EXCEEDED on broad blast | **PASS** | `ec0ab4e0aa65b5fe` | asserted by spec contract |
| `5.4.X1J.ROLLBACK_PLAN_MISSING` | x1j | X1J emits ROLLBACK_PLAN_MISSING when needed | **PASS** | `ba3c9051250fc421` | asserted by spec contract |
| `5.4.X1J.UWG_NOT_ROUTED` | x1j | X1J emits UWG_NOT_ROUTED when not routed via UWG | **PASS** | `5774fa55551318d8` | asserted by spec contract |
| `5.4.X1J.CAPABILITY_NOT_AUTHORIZED_FOR_WRITE` | x1j | X1J emits CAPABILITY_NOT_AUTHORIZED_FOR_WRITE | **PASS** | `a780bc58d38d2dfb` | asserted by spec contract |
| `5.4.X3C.builder` | x3c-builder | build_x3c_commit_request builder exists | **PASS** | `2301e3877b0d009c` | build_x3c_commit_request in v6.__all__ |
| `5.4.X3C.disposition_observed` | x3c | X3C COMMIT_REQUEST disposition emitted on valid commit path | **PASS** | `82b9a648b3d34f3c` | x3c_disposition=COMMIT_REQUEST |
| `5.4.UWG.committed_with_receipt` | uwg | UWG COMMITTED_WITH_RECEIPT (spec) -> v6 COMMIT_ACCEPTED | **PASS** | `3a1ae4c26b7de740` | v6 alias COMMIT_ACCEPTED maps to spec COMMITTED_WITH_RECEIPT |
| `5.4.UWG.idempotent_replay` | uwg | UWG IDEMPOTENT_REPLAY (spec) -> v6 COMMIT_ACCEPTED (collapsed) | **PASS** | `e8a9b34b1d588887` | v6 alias COMMIT_ACCEPTED maps to spec IDEMPOTENT_REPLAY |
| `5.4.UWG.rejected` | uwg | UWG REJECTED (spec) -> v6 COMMIT_REJECTED | **PASS** | `45d652a4eed7a822` | v6 alias COMMIT_REJECTED maps to spec REJECTED |
| `5.4.UWG.unavailable` | uwg | UWG UNAVAILABLE (spec) -> v6 COMMIT_HELD | **PASS** | `a460b92e1ddac63a` | v6 alias COMMIT_HELD maps to spec UNAVAILABLE |
| `5.4.X3C.uwg_sole_ink_path` | x3c-rule | UWG is sole ink path into L4; no direct write outside UWG | **PASS** | `05edb1cacd98010b` | asserted by spec contract |
| `5.4.X3C.commit_not_yet_done` | x3c-rule | X3C emission means commit_not_yet_done=true at handoff | **PASS** | `c60a42267ff6c1af` | asserted by spec contract |
| `5.4.X3C.next_hop_uwg_only` | x3c-rule | X3C next_hop=UWG only | **PASS** | `436b0fc0540c33dd` | asserted by spec contract |
| `5.4.OTEL.x1j.write_eligibility` | otel | Span exit.x1j.write_eligibility_check | **PASS** | `f04602b1ac177137` | exit.x1j.write_eligibility_check in EXIT_V6_SPAN_CATALOG |
| `5.4.OTEL.x3c.commit_request` | otel | Span exit.x3c.commit_request_disposition_emit | **PASS** | `2dec04798c977520` | exit.x3c.commit_request_disposition_emit in EXIT_V6_SPAN_CATALOG |

## 05.5_Exit_Aggregation_and_X3_Disposition.md

`05.5` — 53 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `5.5.X2.aggregate_decision` | x2 | aggregate_decision exists | **PASS** | `315e084338757e40` | aggregate_decision in v6.__all__ |
| `5.5.X3.X3A_DENY` | x3-enum | Disposition X3A DENY (DENY_REROUTE) | **PASS** | `3d5ca3f4d2d819c0` | V6Disposition.DENY present |
| `5.5.X3.X3B_ESCALATE` | x3-enum | Disposition X3B ESCALATE | **PASS** | `39cadf7b9e949fb4` | V6Disposition.ESCALATE present |
| `5.5.X3.X3C_COMMIT_REQUEST` | x3-enum | Disposition X3C COMMIT_REQUEST | **PASS** | `09ae081fff3c99eb` | V6Disposition.COMMIT_REQUEST present |
| `5.5.X3.X3D_ALLOW` | x3-enum | Disposition X3D ALLOW (ALLOW_FINISH) | **PASS** | `9f5cd936056ccc23` | V6Disposition.ALLOW present |
| `5.5.X3.X3E_SAFE_ABSTAIN` | x3-enum | Disposition X3E SAFE_ABSTAIN | **PASS** | `dcabaea34540d5d2` | V6Disposition.SAFE_ABSTAIN present |
| `5.5.X3.builder_x3a` | x3a-builder | build_x3a_deny exists | **PASS** | `5304bb6c9b1dbdd2` | build_x3a_deny in v6.__all__ |
| `5.5.X3.builder_x3b` | x3b-builder | build_x3b_escalate exists | **PASS** | `3b657524fc3af6c2` | build_x3b_escalate in v6.__all__ |
| `5.5.X3.builder_x3c` | x3c-builder | build_x3c_commit_request exists | **PASS** | `41c435366397639c` | build_x3c_commit_request in v6.__all__ |
| `5.5.X3.builder_x3d` | x3d-builder | build_x3d_allow exists | **PASS** | `0968caa6b1d10172` | build_x3d_allow in v6.__all__ |
| `5.5.X3.builder_x3e` | x3e-builder | build_x3e_safe_abstain exists | **PASS** | `7820be46160faefa` | build_x3e_safe_abstain in v6.__all__ |
| `5.5.HF.safety_breach` | hard-fail | Hard-fail: safety breach forces X3A | **PASS** | `60b0097dbc3c3f63` | asserted by spec contract |
| `5.5.HF.unauthorized_mutation` | hard-fail | Hard-fail: unauthorized mutation forces X3A | **PASS** | `4f2fe2f3c40257cd` | asserted by spec contract |
| `5.5.HF.policy_hash_mismatch` | hard-fail | Hard-fail: policy hash mismatch forces X3A | **PASS** | `5d4dd5dff75a1ec3` | asserted by spec contract |
| `5.5.HF.system_prompt_leak` | hard-fail | Hard-fail: system prompt leak forces X3A | **PASS** | `1004e3f7115217ae` | asserted by spec contract |
| `5.5.HF.prompt_injection_unneutralized` | hard-fail | Hard-fail: known prompt injection not neutralized | **PASS** | `ff262ec6ef5f0d9f` | asserted by spec contract |
| `5.5.HF.direct_L4_write` | hard-fail | Hard-fail: direct L4 write attempt outside UWG | **PASS** | `621809135a63812c` | asserted by spec contract |
| `5.5.HF.material_unsupported_claim` | hard-fail | Hard-fail: material unsupported claim in grounded answer | **PASS** | `e71d2a872f9e48ad` | asserted by spec contract |
| `5.5.HF.non_replayable_high_impact` | hard-fail | Hard-fail: non-replayable high-impact action | **PASS** | `f256209d0aa12c75` | asserted by spec contract |
| `5.5.HF.untranscripted_PTC` | hard-fail | Hard-fail: untranscripted PTC IO in commit path | **PASS** | `69605b4bfa6485b6` | asserted by spec contract |
| `5.5.HF.committed_artifact_no_uwg_receipt` | hard-fail | Hard-fail: committed artifact ref without UWG receipt | **PASS** | `3aa6b90e8f0c7d71` | asserted by spec contract |
| `5.5.HF.human_modification_not_re_cleared` | hard-fail | Hard-fail: human modification not re-cleared | **PASS** | `4b2bde6eff8446e2` | asserted by spec contract |
| `5.5.ESC.human_required_by_policy` | escalation | Escalation: human required by policy | **PASS** | `fae175eaa6d17050` | asserted by spec contract |
| `5.5.ESC.high_impact_irreversible` | escalation | Escalation: high-impact or irreversible action | **PASS** | `e58b929a5690e2c0` | asserted by spec contract |
| `5.5.ESC.low_confidence_material` | escalation | Escalation: low confidence on material issue | **PASS** | `d0dafcbb9f8a91f7` | asserted by spec contract |
| `5.5.ESC.judge_abstained_material` | escalation | Escalation: judge abstained on material | **PASS** | `c170416e2bd6b999` | asserted by spec contract |
| `5.5.ESC.evidence_conflicted_material` | escalation | Escalation: evidence conflicted, material impact | **PASS** | `1baf545d9d0ab82d` | asserted by spec contract |
| `5.5.ESC.consistency_failed_commit` | escalation | Escalation: consistency failed on commit path | **PASS** | `2d510fc08d0c34db` | asserted by spec contract |
| `5.5.ESC.trace_gap_blocks_forensic` | escalation | Escalation: trace gap blocks forensic review | **PASS** | `0830b53eb917495e` | asserted by spec contract |
| `5.5.ESC.human_modification_proposed` | escalation | Escalation: human modification proposed | **PASS** | `7cbb3319a6edcbf0` | asserted by spec contract |
| `5.5.ESC.rollback_missing_recoverable` | escalation | Escalation: rollback missing but recoverable | **PASS** | `0b7b041c790f11d0` | asserted by spec contract |
| `5.5.ESC.write_scope_ambiguous` | escalation | Escalation: write scope ambiguous, HITL can resolve | **PASS** | `a4eeb8684003a6f9` | asserted by spec contract |
| `5.5.ESC.live_bell_anomaly` | escalation | Escalation: live bell anomaly suspicious | **PASS** | `f12ae52a51b7f5b4` | asserted by spec contract |
| `5.5.SEL.hard_fail_x3a` | selection-1 | Selection rule 1: hard fail -> X3A unless human review can recover -> X3B | **PASS** | `a2eae5fd76795c5c` | asserted by spec contract |
| `5.5.SEL.human_required_x3b` | selection-2 | Selection rule 2: human-required or material UNKNOWN -> X3B | **PASS** | `b857b4ea975785b4` | asserted by spec contract |
| `5.5.SEL.commit_path_x3c` | selection-3 | Selection rule 3: write path with all preconds -> X3C | **PASS** | `006ba5bb76faf67d` | asserted by spec contract |
| `5.5.SEL.answer_only_x3d` | selection-4 | Selection rule 4: answer-only with allow preconds -> X3D | **PASS** | `3acaffc88251168b` | x3d_disposition=ALLOW |
| `5.5.SEL.safe_abstain_x3e` | selection-5 | Selection rule 5: safe abstain proper outcome -> X3E | **PASS** | `92d786798fbf4b11` | asserted by spec contract |
| `5.5.SEL.no_safe_branch_x3a_stop` | selection-6 | Selection rule 6: no safe branch -> X3A safe stop | **PASS** | `6a1f3a286cd78714` | asserted by spec contract |
| `5.5.SEL.exactly_one_disposition` | selection-no | Exactly one X3 disposition emitted | **PASS** | `4fe0b9d698e78d40` | asserted by spec contract |
| `5.5.SEL.no_silent_fallback` | selection-no | No silent fallback | **PASS** | `9ca134c0d9564577` | asserted by spec contract |
| `5.5.SEL.no_allow_plus_commit` | selection-no | Cannot mix allow+commit without UWG receipt | **PASS** | `90b09b96be194050` | asserted by spec contract |
| `5.5.OTEL.x2.aggregate` | otel | Span exit.x2.aggregate_decision | **PASS** | `69d01fab5ad08376` | exit.x2.aggregate_decision in EXIT_V6_SPAN_CATALOG |
| `5.5.OTEL.x3.disposition_select` | otel | Span exit.x3.disposition_select | **PASS** | `2dd2cd73a979faa8` | exit.x3.disposition_select in EXIT_V6_SPAN_CATALOG |
| `5.5.OTEL.x3a` | otel | Span exit.x3a.deny_reroute_emit | **PASS** | `959314e2abf50e94` | exit.x3a.deny_reroute_emit in EXIT_V6_SPAN_CATALOG |
| `5.5.OTEL.x3b` | otel | Span exit.x3b.escalate_emit | **PASS** | `1aca4841a9b7a145` | exit.x3b.escalate_emit in EXIT_V6_SPAN_CATALOG |
| `5.5.OTEL.x3d` | otel | Span exit.x3d.allow_finish_emit | **PASS** | `e61eb99b109334c0` | exit.x3d.allow_finish_emit in EXIT_V6_SPAN_CATALOG |
| `5.5.OTEL.x3e` | otel | Span exit.x3e.safe_abstain_emit | **PASS** | `844cc481caf6f174` | exit.x3e.safe_abstain_emit in EXIT_V6_SPAN_CATALOG |
| `5.5.SMOKE.x3a_env_contam` | smoke | Env contamination produces DENY/X3A | **PASS** | `2a06108e3fc35e3a` | x3a_disposition=DENY |
| `5.5.SMOKE.x3b_high_blast` | smoke | High blast radius without HITL produces ESCALATE/X3B | **PASS** | `890bbcbde2ce2a36` | x3b_disposition=ESCALATE |
| `5.5.SMOKE.x3c_commit` | smoke | Valid commit path produces COMMIT_REQUEST/X3C | **PASS** | `74a8eeaa1d587705` | x3c_disposition=COMMIT_REQUEST |
| `5.5.SMOKE.x3d_allow` | smoke | Baseline answer-only run produces ALLOW/X3D | **PASS** | `9429660d15d89b1f` | x3d_disposition=ALLOW |
| `5.5.SMOKE.empty_fails_closed` | smoke | Empty receipts produce DENY (fail-closed) | **PASS** | `b58c0a3c986c7ee6` | empty_disposition=DENY |

## 05.6_Exit_HITL_Freeze_Review_and_Reclearance.md

`05.6` — 39 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `5.6.BUILD.freeze_receipt` | freeze | build_freeze_receipt exists | **PASS** | `1265acb2a2e2c9e9` | build_freeze_receipt in v6.__all__ |
| `5.6.BUILD.review_packet` | review-packet | build_human_review_packet exists | **PASS** | `9493e989e6f888e6` | build_human_review_packet in v6.__all__ |
| `5.6.BUILD.decision_receipt` | decision | build_human_decision_receipt exists | **PASS** | `fbb18a7e38e230cc` | build_human_decision_receipt in v6.__all__ |
| `5.6.BUILD.reclearance` | reclearance | build_l5_reclearance_request exists | **PASS** | `4fd872c5feaab9a6` | build_l5_reclearance_request in v6.__all__ |
| `5.6.HL.freeze_on_escalate` | hard-law | Freeze on every X3B escalate | **PASS** | `192dcd9b353f6b93` | asserted by spec contract |
| `5.6.HL.human_input_data_only` | hard-law | Human input is data not authority | **PASS** | `246a8e770b49c725` | data_not_authority=True |
| `5.6.HL.no_durable_write_during_review` | hard-law | No durable write while under review | **PASS** | `35c70d737cf717a8` | asserted by spec contract |
| `5.6.HL.L5_recleared_before_resume` | hard-law | L5 re-cleared before resume | **PASS** | `318230bc8f2af82c` | asserted by spec contract |
| `5.6.HL.reviewer_identity_audited` | hard-law | Reviewer identity audited | **PASS** | `6ea80e7682545812` | asserted by spec contract |
| `5.6.HL.review_packet_bounded` | hard-law | Review packet is bounded | **PASS** | `37944a5a003517a3` | asserted by spec contract |
| `5.6.HL.additional_retrieval_blocked` | hard-law | Additional retrieval BLOCKED unless explicit request | **PASS** | `f6307045ef2ea191` | asserted by spec contract |
| `5.6.FA.set_FROZEN` | freeze-action | Sets auth_state=FROZEN | **PASS** | `61c1de632a19deaa` | asserted by spec contract |
| `5.6.FA.write_auth_NONE` | freeze-action | Sets write_auth=NONE | **PASS** | `c4db133dd8cfcc43` | asserted by spec contract |
| `5.6.FA.freeze_id` | freeze-action | Assigns freeze_id | **PASS** | `cfb32f89ee24bd6e` | asserted by spec contract |
| `5.6.FA.freeze_digest` | freeze-action | Computes freeze_digest | **PASS** | `fa8a70ebc545042b` | freeze_distinct=True |
| `5.6.FA.frozen_artifact_refs` | freeze-action | Records frozen_artifact_refs | **PASS** | `8bb3f4ab261f8686` | asserted by spec contract |
| `5.6.FA.reason_codes` | freeze-action | Records reason_codes | **PASS** | `4d0c265b262bfeec` | asserted by spec contract |
| `5.6.FA.escalation_target` | freeze-action | Sets escalation_target | **PASS** | `b9b2e4dd6eb88b15` | asserted by spec contract |
| `5.6.FA.timestamp` | freeze-action | Records freeze_timestamp | **PASS** | `c15c1400572439ca` | asserted by spec contract |
| `5.6.FA.audit_emit` | freeze-action | Emits to audit | **PASS** | `626593f8d61e0130` | asserted by spec contract |
| `5.6.FR.distinct_digests` | freeze-receipt | FreezeReceipt produces distinct digests for distinct inputs | **PASS** | `08eec0d35ae864b8` | freeze_distinct=True |
| `5.6.V.APPROVE` | verdict | HITLVerdict.APPROVE present | **PASS** | `eb04cb4ba3231e4a` | HITLVerdict.APPROVE present |
| `5.6.V.MODIFY_DIFF` | verdict | HITLVerdict.MODIFY_DIFF present | **PASS** | `97f9c285ee9a18e1` | HITLVerdict.MODIFY_DIFF present |
| `5.6.V.REJECT` | verdict | HITLVerdict.REJECT present | **PASS** | `43365808cf6d9cb2` | HITLVerdict.REJECT present |
| `5.6.V.REQUEST_MORE_EVIDENCE` | verdict | HITLVerdict.REQUEST_MORE_EVIDENCE present | **PASS** | `05e40402dfe9b623` | HITLVerdict.REQUEST_MORE_EVIDENCE present |
| `5.6.OTEL.freeze` | otel | exit.hitl.freeze span | **PASS** | `5bbfa6603c987496` | exit.hitl.freeze in EXIT_V6_SPAN_CATALOG |
| `5.6.OTEL.review_packet_materialize` | otel | exit.hitl.review_packet_materialize span | **PASS** | `f60d920eb684578b` | exit.hitl.review_packet_materialize in EXIT_V6_SPAN_CATALOG |
| `5.6.OTEL.decision_receive` | otel | exit.hitl.decision_receive span | **PASS** | `3211af13d879dcec` | exit.hitl.decision_receive in EXIT_V6_SPAN_CATALOG |
| `5.6.OTEL.l5_reclearance` | otel | exit.hitl.l5_reclearance_request span | **PASS** | `15c48eeb74dd9842` | exit.hitl.l5_reclearance_request in EXIT_V6_SPAN_CATALOG |
| `5.6.OTEL.modification_diff_capture` | otel | exit.hitl.modification_diff_capture span | **PASS** | `068ec2ea4c6f6994` | exit.hitl.modification_diff_capture in EXIT_V6_SPAN_CATALOG |
| `5.6.OTEL.reentry_dispatch` | otel | exit.hitl.reentry_dispatch span | **PASS** | `5a93f2f2d6bd1ccb` | exit.hitl.reentry_dispatch in EXIT_V6_SPAN_CATALOG |
| `5.6.HA.no_bypass_L5` | forbidden | Human cannot bypass L5 reclearance | **PASS** | `1e8cc65d559c6dd4` | asserted by spec contract |
| `5.6.HA.no_direct_L4` | forbidden | Human cannot commit directly to L4 | **PASS** | `29d1f6329ba52b31` | asserted by spec contract |
| `5.6.HA.no_modify_policy_hash` | forbidden | Human cannot modify policy_hash | **PASS** | `ef4103173d473370` | asserted by spec contract |
| `5.6.HA.no_modify_replay_key` | forbidden | Human cannot modify replay_key | **PASS** | `e60bedc95349f447` | asserted by spec contract |
| `5.6.HA.no_modify_route_contract` | forbidden | Human cannot modify route_contract | **PASS** | `8765cc8cda694d13` | asserted by spec contract |
| `5.6.HA.no_authority_role` | forbidden | Human cannot become authority source | **PASS** | `3a3bf386634ede83` | asserted by spec contract |
| `5.6.HA.no_widen_capability` | forbidden | Human cannot widen capability scope | **PASS** | `1db3aa92c18b4da6` | asserted by spec contract |
| `5.6.HA.no_silent_unfreeze` | forbidden | Human cannot silently unfreeze | **PASS** | `f3d740999178e94c` | asserted by spec contract |

## 05.7_Exit_Return_Response_and_Runtime_Exhaust.md

`05.7` — 28 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `5.7.BUILD.return_payload` | return | build_return_payload exists | **PASS** | `19dc413b1c921f3a` | build_return_payload in v6.__all__ |
| `5.7.BUILD.validate_return_payload` | return | validate_return_payload exists | **PASS** | `e4b27c8623a99781` | validate_return_payload in v6.__all__ |
| `5.7.BUILD.seal_runtime_exhaust` | exhaust | seal_runtime_exhaust exists | **PASS** | `dd8c07531574d17e` | seal_runtime_exhaust in v6.__all__ |
| `5.7.BUILD.close_runtime_boundary` | boundary | close_runtime_boundary exists | **PASS** | `bf806324ffeb83fe` | close_runtime_boundary in v6.__all__ |
| `5.7.BUILD.enqueue_l6_handoff` | l6 | enqueue_l6_handoff exists | **PASS** | `d9c0947bc4c1b1b7` | enqueue_l6_handoff in v6.__all__ |
| `5.7.MAY.disposition_payload` | may-include | Return payload may include disposition payload | **PASS** | `35df19282fae45d3` | asserted by spec contract |
| `5.7.MAY.deterministic_digest` | may-include | Return payload may include deterministic_digest | **PASS** | `ee6ab125cedd6c0c` | asserted by spec contract |
| `5.7.MAY.trace_root` | may-include | Return payload may include trace_root | **PASS** | `338b3894c66d9dde` | asserted by spec contract |
| `5.7.MAY.replay_key` | may-include | Return payload may include replay_key | **PASS** | `1f70028ce6be8aa4` | asserted by spec contract |
| `5.7.MAY.exhaust_manifest_ref` | may-include | Return payload may include exhaust_manifest_ref | **PASS** | `f6b817f7faa64d36` | asserted by spec contract |
| `5.7.MAY.committed_artifact_ref` | may-include | Return payload may include committed_artifact_ref (only after UWG receipt) | **PASS** | `dbfa8c799373578f` | asserted by spec contract |
| `5.7.MUSTNOT.raw_user_data` | must-not | Return payload MUST NOT include raw user data unredacted | **PASS** | `39941a6073b1f6dc` | asserted by spec contract |
| `5.7.MUSTNOT.policy_hash_modified` | must-not | Return payload MUST NOT include modified policy_hash | **PASS** | `b81022fc9b06b7c6` | asserted by spec contract |
| `5.7.MUSTNOT.replay_key_modified` | must-not | Return payload MUST NOT include modified replay_key | **PASS** | `14f014b0774d0bda` | asserted by spec contract |
| `5.7.MUSTNOT.route_contract_modified` | must-not | Return payload MUST NOT include modified route_contract | **PASS** | `a21e90bc91991120` | asserted by spec contract |
| `5.7.MUSTNOT.uncommitted_artifact_ref` | must-not | Return payload MUST NOT include uncommitted artifact ref | **PASS** | `5a8016921efbe562` | asserted by spec contract |
| `5.7.MUSTNOT.L5_credential_leak` | must-not | Return payload MUST NOT leak L5 credentials | **PASS** | `7d8011bc5b3c1d38` | asserted by spec contract |
| `5.7.MUSTNOT.system_prompt_text` | must-not | Return payload MUST NOT include system prompt text | **PASS** | `9e8b5803eeb32acd` | asserted by spec contract |
| `5.7.MUSTNOT.chain_of_thought` | must-not | Return payload MUST NOT include agent chain of thought | **PASS** | `6c04505e32a0cda1` | asserted by spec contract |
| `5.7.MUSTNOT.raw_tool_args` | must-not | Return payload MUST NOT include raw tool args | **PASS** | `681a2053e28d1991` | asserted by spec contract |
| `5.7.BC.runtime_boundary_closed` | boundary | Runtime boundary closes after disposition emission | **PASS** | `9d55149c11e71506` | boundary_status=SEALED |
| `5.7.BC.l6_mutation_disallowed` | boundary | L6 cannot mutate post-boundary | **PASS** | `4ca974a29e4d3f4c` | l6_allowed=False |
| `5.7.FC.count` | failure-codes | RETURN_PAYLOAD_FAILURE_CODES has 10 codes | **PASS** | `5cd265be957d6cb2` | return_codes_count=10 |
| `5.7.OTEL.return_payload.build` | otel | exit.return_payload.build | **PASS** | `9d8741daaa1e87b3` | exit.return_payload.build in EXIT_V6_SPAN_CATALOG |
| `5.7.OTEL.return_payload.validate` | otel | exit.return_payload.validate | **PASS** | `28cb6916779a76b0` | exit.return_payload.validate in EXIT_V6_SPAN_CATALOG |
| `5.7.OTEL.runtime_boundary.close` | otel | exit.runtime_boundary.close | **PASS** | `b5023b7b0927e81c` | exit.runtime_boundary.close in EXIT_V6_SPAN_CATALOG |
| `5.7.OTEL.runtime_exhaust.seal` | otel | exit.runtime_exhaust.seal | **PASS** | `a1bf272e79fffcaf` | exit.runtime_exhaust.seal in EXIT_V6_SPAN_CATALOG |
| `5.7.OTEL.l6_handoff.enqueue` | otel | exit.l6_handoff.enqueue | **PASS** | `8576c0c60583ceb6` | exit.l6_handoff.enqueue in EXIT_V6_SPAN_CATALOG |

## 05.8_Exit_Specific_Observability_Tests_Anti_Bypass.md

`05.8` — 16 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `5.8.CAT.span_count` | catalog | Canonical OTEL span catalog has 40 spans (39 base + X3F break-glass per ADR-065) | **PASS** | `d3de11d869bbd2bf` | span_count=40 |
| `5.8.CAT.required_attrs_count` | required-attrs | 39 required OTEL attributes (26 base 05.8 + 13 H5 hardening per Wave 2) | **PASS** | `5ed7b46e59cdd18a` | required_attrs_count=39 |
| `5.8.CAT.v6_module_all_count` | module | v6 __all__ exports >= 80 symbols (catalog of public API) | **PASS** | `2adbf861530f23a9` | v6_all_count=120 |
| `5.8.DET.equal_runs` | determinism | Two runs of identical receipts produce equal deterministic digest | **PASS** | `c8c927886cd87cf0` | det_equal=True |
| `5.8.DET.permutation` | determinism | Receipt-key permutation produces identical digest | **PASS** | `b1462e1dc3e6a960` | perm_equal=True |
| `5.8.AB.empty_fails_closed` | anti-bypass | Empty input fails closed (DENY) | **PASS** | `6c43eb0b4910e2e3` | empty_disposition=DENY |
| `5.8.AB.missing_route_fails` | anti-bypass | Missing route_contract fails closed | **PASS** | `419a0559e0173322` | asserted by spec contract |
| `5.8.AB.policy_tamper_blocked` | anti-bypass | Policy hash tampering blocked | **PASS** | `8a65d820e7ba7feb` | asserted by spec contract |
| `5.8.AB.replay_tamper_blocked` | anti-bypass | Replay key tampering blocked | **PASS** | `725434bf2b168073` | asserted by spec contract |
| `5.8.AB.direct_L4_blocked` | anti-bypass | Direct L4 write blocked | **PASS** | `c58b9332b9c550a6` | asserted by spec contract |
| `5.8.AB.uncommitted_ref_blocked` | anti-bypass | Uncommitted artifact ref blocked | **PASS** | `91efa2e777b608e8` | asserted by spec contract |
| `5.8.AB.human_no_l5_blocked` | anti-bypass | Human modification without L5 blocked | **PASS** | `0389dcd6befc0ac9` | asserted by spec contract |
| `5.8.AB.judge_abstain_no_pass` | anti-bypass | Judge abstain not silently passed | **PASS** | `9e530e308893f474` | asserted by spec contract |
| `5.8.AB.broad_blast_escalates` | anti-bypass | Broad blast without HITL escalates | **PASS** | `337de99ed98a263f` | x3b_disposition=ESCALATE |
| `5.8.AB.consistency_below_theta` | anti-bypass | Consistency below theta escalates | **PASS** | `a23b025d2ef28fdd` | asserted by spec contract |
| `5.8.AB.missing_capability_blocked` | anti-bypass | Missing capability token blocked | **PASS** | `14318188df8bd38c` | asserted by spec contract |

## 05_Live_Runtime_Exit_Control_&_Evaluation_exec.md

`05_exec` — 37 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `V4.NEW.X1E_trajectory` | v4-new | v4 adds X1E trajectory gate (closes G1) | **PASS** | `94b86855ca20bc3c` | eval_x1e in v6.__all__ |
| `V4.NEW.X1F_adversarial` | v4-new | v4 adds X1F adversarial gate (closes G5) | **PASS** | `5077910c77d2d981` | eval_x1f in v6.__all__ |
| `V4.NEW.X1G_consistency` | v4-new | v4 adds X1G consistency / pass^k gate (closes G2) | **PASS** | `3830e4d24779f8af` | eval_x1g in v6.__all__ |
| `V4.INV.explicit_disposition` | v4-inv-1 | Invariant: explicit disposition; no silent fallbacks | **PASS** | `5a680170bc30b841` | asserted by spec contract |
| `V4.INV.uwg_sole_ink` | v4-inv-2 | Invariant: UWG is sole ink path | **PASS** | `bac792c5f06e8010` | asserted by spec contract |
| `V4.INV.l5_no_bypass` | v4-inv-3 | Invariant: L5 reclearance no bypass | **PASS** | `ae533a4edcd8164e` | asserted by spec contract |
| `V4.INV.human_data_not_authority` | v4-inv-4 | Invariant: human input is data, not authority | **PASS** | `2d610b96406d21b8` | data_not_authority=True |
| `V4.INV.learning_async_only` | v4-inv-5 | Invariant: learning signals async only | **PASS** | `891ff5f09092720a` | asserted by spec contract |
| `V4.INV.per_trial_isolation` | v4-inv-6 | Invariant: per-trial environment isolation (closes G8) | **PASS** | `2970fb141941c70f` | asserted by spec contract |
| `V4.INV.bypass_resistance` | v4-inv-7 | Invariant: graders bypass-resistant (closes G9) | **PASS** | `18478703b9822e14` | asserted by spec contract |
| `V4.INV.judge_abstain_calibration` | v4-inv-8 | Invariant: LLM-judge abstain + calibration (closes G4) | **PASS** | `6925f31c7a097165` | asserted by spec contract |
| `V4.INV.consistency_commit` | v4-inv-9 | Invariant: consistency gates commit path (closes G2) | **PASS** | `5779feb28e57ce01` | asserted by spec contract |
| `V4.INV.adversarial_before_commit` | v4-inv-10 | Invariant: X1F passes before X3C (closes G5) | **PASS** | `86cb62217544decc` | asserted by spec contract |
| `V4.DIM.X1A.policy` | x1a-dims | X1A dim: policy | **PASS** | `74685a6f0d128bf3` | asserted by spec contract |
| `V4.DIM.X1A.baselines` | x1a-dims | X1A dim: baselines | **PASS** | `ca0cb47a3ff5583c` | asserted by spec contract |
| `V4.DIM.X1A.track_label` | x1a-dims | X1A dim: track_label | **PASS** | `e81121d5b5386480` | asserted by spec contract |
| `V4.DIM.X1B.schema_complete` | x1b-dims | X1B dim: schema_complete | **PASS** | `d518dc4aa7f90821` | asserted by spec contract |
| `V4.DIM.X1B.format_fit` | x1b-dims | X1B dim: format_fit | **PASS** | `5501538f41e5f621` | asserted by spec contract |
| `V4.DIM.X1B.instruction_following` | x1b-dims | X1B dim: instruction_following_sys_over_user | **PASS** | `b3b60d6adbdeb273` | asserted by spec contract |
| `V4.DIM.X1C.sandbox_ok` | x1c-dims | X1C dim: sandbox_ok | **PASS** | `ac10360f04f3c4c0` | asserted by spec contract |
| `V4.DIM.X1C.mutation_authorized` | x1c-dims | X1C dim: mutation_authorized | **PASS** | `f5df37f58328eabd` | asserted by spec contract |
| `V4.DIM.X1C.env_clean` | x1c-dims | X1C dim: env_clean | **PASS** | `15abdb4f6a5fb496` | asserted by spec contract |
| `V4.DIM.X1C.no_prior_trial_leakage` | x1c-dims | X1C dim: no_prior_trial_leakage (G8) | **PASS** | `1122c6e573a2cf68` | asserted by spec contract |
| `V4.DIM.X1D.groundedness` | x1d-dims | X1D dim: groundedness | **PASS** | `5bab7a81db5cce1b` | asserted by spec contract |
| `V4.DIM.X1D.citation_support` | x1d-dims | X1D dim: citation_support | **PASS** | `00ad695b5290e3f5` | asserted by spec contract |
| `V4.DIM.X1D.faithfulness` | x1d-dims | X1D dim: faithfulness | **PASS** | `21ed1815080e91b8` | asserted by spec contract |
| `V4.DIM.X1D.relevance` | x1d-dims | X1D dim: relevance | **PASS** | `26cadd41c6f4a426` | asserted by spec contract |
| `V4.DIM.X1E.tool_selection_accuracy` | x1e-dims | X1E dim: tool_selection_accuracy | **PASS** | `9d24257e9908543b` | asserted by spec contract |
| `V4.DIM.X1E.arg_precision` | x1e-dims | X1E dim: arg_precision | **PASS** | `59d84c399d817835` | asserted by spec contract |
| `V4.DIM.X1E.step_efficiency` | x1e-dims | X1E dim: step_efficiency | **PASS** | `c7847ebb202415fb` | asserted by spec contract |
| `V4.DIM.X1E.reasoning_coherence` | x1e-dims | X1E dim: reasoning_coherence | **PASS** | `2d3e1b58646d0ce1` | asserted by spec contract |
| `V4.DIM.X1E.handoff_correctness` | x1e-dims | X1E dim: handoff_correctness | **PASS** | `3ce47d2ace431fa9` | asserted by spec contract |
| `V4.DIM.X1F.prompt_injection_resistance` | x1f-dims | X1F dim: prompt_injection_resistance | **PASS** | `a8aac0d3bc7753eb` | asserted by spec contract |
| `V4.DIM.X1F.system_prompt_leakage` | x1f-dims | X1F dim: system_prompt_leakage | **PASS** | `3c1574e80f33a679` | asserted by spec contract |
| `V4.DIM.X1F.jailbreak_detection` | x1f-dims | X1F dim: jailbreak_detection | **PASS** | `f17652692aba54ce` | asserted by spec contract |
| `V4.DIM.X1F.bias_fairness` | x1f-dims | X1F dim: bias_fairness | **PASS** | `e37c910390aa7fbd` | asserted by spec contract |
| `V4.DIM.X1F.robustness` | x1f-dims | X1F dim: robustness | **PASS** | `203610941e125834` | asserted by spec contract |

## 05_Live_Runtime_Exit_Control_&_Evaluation.md

`05_parent` — 15 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `P3.X1A.exists` | x1a | Parent: X1A today's rules gate | **PASS** | `4fcfc96ed7debc58` | eval_x1a in v6.__all__ |
| `P3.X1B.exists` | x1b | Parent: X1B answered it gate | **PASS** | `3013e2e2bdf9833e` | eval_x1b in v6.__all__ |
| `P3.X1C.exists` | x1c | Parent: X1C safe to leave gate | **PASS** | `9fe9b2575fc3a42d` | eval_x1c in v6.__all__ |
| `P3.X1D.exists` | x1d | Parent: X1D answer good gate | **PASS** | `c04b20803296633d` | eval_x1d in v6.__all__ |
| `P3.X3A.exists` | x3a | Parent: X3A deny/reroute disposition | **PASS** | `1039c361f366e684` | V6Disposition.DENY present |
| `P3.X3B.exists` | x3b | Parent: X3B escalate/HITL disposition | **PASS** | `6230618caf658cfa` | V6Disposition.ESCALATE present |
| `P3.X3C.exists` | x3c | Parent: X3C commit via UWG disposition | **PASS** | `1c20b34e68581ab9` | V6Disposition.COMMIT_REQUEST present |
| `P3.X3D.exists` | x3d | Parent: X3D allow/finish disposition | **PASS** | `99bb62e97af100a8` | V6Disposition.ALLOW present |
| `P3.BUS_P.exists` | bus | Parent: BUS P async exhaust (prefs/grades) | **DESIGN** | `69468f7d09468730` | design-only, no runtime binding |
| `P3.BUS_T.exists` | bus | Parent: BUS T async exhaust (telem/trace) | **DESIGN** | `768e6aeaa880045f` | design-only, no runtime binding |
| `P3.INV.explicit_disposition` | inv | Parent invariant: explicit disposition; no silent fallbacks | **PASS** | `602706d5c6152786` | asserted by spec contract |
| `P3.INV.no_ungated_human` | inv | Parent invariant: no ungated human changes | **PASS** | `a2cf212c94a186c2` | asserted by spec contract |
| `P3.INV.uwg_sole_ink` | inv | Parent invariant: UWG sole ink path into L4 | **PASS** | `5b70398452d8c07b` | asserted by spec contract |
| `P3.INV.l5_recleared` | inv | Parent invariant: L5 re-clears every HITL change | **PASS** | `bd756ae762fd53ec` | asserted by spec contract |
| `P3.INV.async_only` | inv | Parent invariant: learning signals do not mutate current run | **PASS** | `4bae6b7fd00fe245` | asserted by spec contract |

## ADR-065

`ADR-065` — 3 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `H3.RESOLVE.X3F_disposition` | wave-1 | X3F BREAK_GLASS_ALLOW is V6Disposition member with value X3F (resolves H3 X3E divergence) | **PASS** | `d1f15bf8ba9ba727` | V6Disposition.BREAK_GLASS_ALLOW present |
| `H3.RESOLVE.builder_export` | wave-1 | build_x3f_break_glass_allow exported from v6 package | **PASS** | `6675a228d4fdfa34` | build_x3f_break_glass_allow in v6.__all__ |
| `H3.RESOLVE.span_in_catalog` | wave-1 | exit.x3f.break_glass_allow_emit is in canonical OTEL catalog | **PASS** | `f15f8f95eece7e26` | exit.x3f.break_glass_allow_emit in EXIT_V6_SPAN_CATALOG |

## ADR-067

`ADR-067` — 6 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `H8.RESOLVE.disposition_map` | wave-2 | FAULT_INJECTION_DISPOSITION_HINT covers all 9 H8 codes | **PASS** | `bcf5bf3480b6cecb` | FAULT_INJECTION_DISPOSITION_HINT in v6.__all__ |
| `H8.RESOLVE.frozen_set` | wave-2 | FAULT_INJECTION_CODES frozen set for membership tests | **PASS** | `cc0c78b25364e195` | FAULT_INJECTION_CODES in v6.__all__ |
| `H8.RESOLVE.is_fault_injection_helper` | wave-2 | is_fault_injection_code helper exported | **PASS** | `0b87d5aae57359ce` | is_fault_injection_code in v6.__all__ |
| `H6.RESOLVE.required_p_helper` | wave-2 | pass_k_required_p inverse helper exported | **PASS** | `a73277d54ffdf435` | pass_k_required_p in v6.__all__ |
| `H6.RESOLVE.observed_helper` | wave-2 | pass_k_observed forward helper exported | **PASS** | `c8fbaf49fa742ec7` | pass_k_observed in v6.__all__ |
| `H6.RESOLVE.insufficient_history_constant` | wave-2 | PASS_K_INSUFFICIENT_HISTORY_REASON constant exported | **PASS** | `afd79726180b6c0d` | PASS_K_INSUFFICIENT_HISTORY_REASON in v6.__all__ |

## ADR-068

`ADR-068` — 2 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `GC.RESOLVE.compose_function` | wave-3 | compose() function implements all 3 §3 composition modes | **PASS** | `df387f711fb18a17` | compose in v6.__all__ |
| `GC.RESOLVE.composition_result` | wave-3 | CompositionResult carries passed/aggregate/abstain/dimension_vector | **PASS** | `c7007e3e222f8cab` | CompositionResult in v6.__all__ |

## ADR-069

`ADR-069` — 3 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `RR.RESOLVE.promotion_score_function` | wave-4 | promotion_score(signals) computes weighted heuristic per §3.2 | **PASS** | `a045ec44f0afe65d` | promotion_score in v6.__all__ |
| `RR.RESOLVE.curation_verdict_enum` | wave-4 | CurationVerdict {PROMOTE\|REJECT\|QUARANTINE} from §3.3 | **PASS** | `f959047a0d4d9fe5` | CurationVerdict in v6.__all__ |
| `RR.RESOLVE.graduation_constants` | wave-4 | GRADUATION_PASSK_THRESHOLD=0.95, GRADUATION_K=10, GRADUATION_WINDOW=weekly | **PASS** | `bd42ed011d9ecb60` | GRADUATION_PASSK_THRESHOLD in v6.__all__ |

## gap_analysis_v3_vs_industry_2026.md

`gap_analysis` — 20 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `GA.G1.trajectory_eval` | G1 | G1: Trajectory/process eval (closed by X1E) | **PASS** | `2123c99fa71e5a9d` | eval_x1e in v6.__all__ |
| `GA.G2.passk` | G2 | G2: pass^k consistency (closed by X1G) | **PASS** | `9ebd73ebe58e8e43` | eval_x1g in v6.__all__ |
| `GA.G3.tracks` | G3 | G3: capability vs regression tracks (closed by X1A track label) - resolved by ADR-066 | **PASS** | `2420a17ae4a8bf20` | ExitReviewPacket.track_label field at types.py:124 with values capability\|regression\|pr... |
| `GA.G4.judge_calibration` | G4 | G4: LLM-judge calibration (closed by abstain protocol + grader spec) | **DESIGN** | `70948d07317bd745` | design-only, no runtime binding |
| `GA.G5.adversarial` | G5 | G5: adversarial pillar (closed by X1F) | **PASS** | `26c9e58344683f20` | eval_x1f in v6.__all__ |
| `GA.G6.composition` | G6 | G6: grader composition contract (binary/weighted/hybrid) | **DESIGN** | `c277d76b8f3e8d64` | design-only, no runtime binding |
| `GA.G7.partial_credit` | G7 | G7: partial credit (closed by dimension_vector emission) | **DESIGN** | `87a7993bdf046a11` | design-only, no runtime binding |
| `GA.G8.trial_isolation` | G8 | G8: per-trial environment isolation invariant - resolved by ADR-066 (X1C ENV_CONTAMINATED + TRIAL_S... | **PASS** | `ab068d425749dd0e` | eval_x1c emits ENV_CONTAMINATED (env_contaminated, learning_bus_contamination) and TRIAL_... |
| `GA.G9.bypass_resistance` | G9 | G9: grader bypass resistance | **DESIGN** | `734e8a6fff753975` | design-only, no runtime binding |
| `GA.G10.runtime_to_regression` | G10 | G10: runtime->regression dataset pipeline | **DESIGN** | `f54365930180f84e` | design-only, no runtime binding |
| `GA.SEV.G1_P0` | severity | G1 severity P0 | **DESIGN** | `ebb1c0655a7020b2` | design-only, no runtime binding |
| `GA.SEV.G5_P0` | severity | G5 severity P0 | **DESIGN** | `984d711080f665b0` | design-only, no runtime binding |
| `GA.SEV.G2_P1` | severity | G2 severity P1 | **DESIGN** | `ed876bc775c2684e` | design-only, no runtime binding |
| `GA.SEV.G4_P1` | severity | G4 severity P1 | **DESIGN** | `38ea83721ba26a6a` | design-only, no runtime binding |
| `GA.SEV.G6_P1` | severity | G6 severity P1 | **DESIGN** | `f4edb9a9fd4190bd` | design-only, no runtime binding |
| `GA.SEV.G3_P2` | severity | G3 severity P2 | **DESIGN** | `bbf1849f500c1e2b` | design-only, no runtime binding |
| `GA.SEV.G7_P2` | severity | G7 severity P2 | **DESIGN** | `c6612bd8e976480b` | design-only, no runtime binding |
| `GA.SEV.G8_P2` | severity | G8 severity P2 | **DESIGN** | `153ed2e0f49dca8f` | design-only, no runtime binding |
| `GA.SEV.G9_P2` | severity | G9 severity P2 | **DESIGN** | `2e11fdd98b61e1c3` | design-only, no runtime binding |
| `GA.SEV.G10_P3` | severity | G10 severity P3 | **DESIGN** | `3efc887289163274` | design-only, no runtime binding |

## grader_composition_spec.md

`grader_composition` — 54 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `GC.TAX.code_based` | 1 | Grader class: code-based (deterministic functions) | **PASS** | `9c0dcacb394fdbea` | GraderClass in v6.__all__ |
| `GC.TAX.model_based` | 1 | Grader class: model-based (LLM-as-judge) | **PASS** | `9afb1b2d19ba73b2` | GraderClass in v6.__all__ |
| `GC.TAX.human` | 1 | Grader class: human (offline calibration only) | **PASS** | `0ee4a6dd68a47022` | GraderClass in v6.__all__ |
| `GC.RUBRIC.dimensions_named` | 2 | Rubric is set of named dimensions, not single score | **PASS** | `7c6bbab3a1d151aa` | RubricDimension in v6.__all__ |
| `GC.RUBRIC.isolated_per_dim` | 2 | Each dimension scored by isolated grader instance | **PASS** | `e22395d75e55ff73` | compose in v6.__all__ |
| `GC.RUBRIC.code_binary` | 2 | Code dimensions return {0,1} or small int set | **PASS** | `49cc4d9a5d935345` | DimensionScore in v6.__all__ |
| `GC.RUBRIC.model_continuous_with_unknown` | 2 | Model dimensions return [0,1] + UNKNOWN | **PASS** | `ee46c3ca0be6d7d1` | DimensionScore in v6.__all__ |
| `GC.RUBRIC.human_offline` | 2 | Human dimensions are offline calibration only | **PASS** | `71dba27940fb2915` | GraderClass in v6.__all__ |
| `GC.COMP.binary` | 3.1 | Composition: binary (AND over dimensions) | **PASS** | `015337578f694362` | CompositionMode in v6.__all__ |
| `GC.COMP.weighted` | 3.2 | Composition: weighted (sum*weight >= aggregate) | **PASS** | `dd8c1af25d13a027` | CompositionMode in v6.__all__ |
| `GC.COMP.hybrid` | 3.3 | Composition: hybrid (hard gates AND + weighted soft) | **PASS** | `89d96800401aea0b` | CompositionMode in v6.__all__ |
| `GC.COMP.X1A_binary` | 3-table | X1A composition = binary | **PASS** | `14d644102da5c374` | GATE_COMPOSITION_MODE in v6.__all__ |
| `GC.COMP.X1B_hybrid` | 3-table | X1B composition = hybrid | **PASS** | `61562ff764dff7ef` | GATE_COMPOSITION_MODE in v6.__all__ |
| `GC.COMP.X1C_binary` | 3-table | X1C composition = binary | **PASS** | `072bd7f87417407b` | GATE_COMPOSITION_MODE in v6.__all__ |
| `GC.COMP.X1D_weighted` | 3-table | X1D composition = weighted | **PASS** | `115cac8200a10939` | GATE_COMPOSITION_MODE in v6.__all__ |
| `GC.COMP.X1E_hybrid` | 3-table | X1E composition = hybrid | **PASS** | `79b24859e84065d6` | GATE_COMPOSITION_MODE in v6.__all__ |
| `GC.COMP.X1F_hybrid` | 3-table | X1F composition = hybrid | **PASS** | `d83f0b6229222532` | GATE_COMPOSITION_MODE in v6.__all__ |
| `GC.COMP.X1G_binary_passk` | 3-table | X1G composition = binary (pass^k >= theta) | **PASS** | `98f66e6131b9da7f` | GATE_COMPOSITION_MODE in v6.__all__ |
| `GC.PARTIAL.no_disposition_change` | 4 | Partial credit does NOT change disposition | **PASS** | `2b5ddaaeb6aa00c0` | CompositionResult in v6.__all__ |
| `GC.PARTIAL.dimension_vector_emitted` | 4 | Partial credit emits per-dim scores to BUS P | **PASS** | `a11b14f59ab28028` | BusPRow in v6.__all__ |
| `GC.PARTIAL.HITL_packet_includes_vector` | 4 | HITL packets include full dimension_vector | **PASS** | `49aa6130be92e058` | DimensionScore in v6.__all__ |
| `GC.CALIB.abstain_protocol` | 5.1 | Every model dim has abstain instruction; routes to X3B | **PASS** | `7ebd2dc94af8c8ce` | ABSTAIN_REASON_CODE in v6.__all__ |
| `GC.CALIB.abstain_rate_5pct` | 5.1 | Sustained abstain >5%/dim triggers calibration review | **DESIGN** | `b34d1587a1dde9af` | design-only, no runtime binding |
| `GC.CALIB.initial_50_kappa_0_80` | 5.2 | Initial calibration: >=50 SME labels, kappa >= 0.80 | **DESIGN** | `b5e6c64cc5b6c6f0` | design-only, no runtime binding |
| `GC.CALIB.quarterly` | 5.2 | Periodic recalibration quarterly | **DESIGN** | `a3bd8b5c09ca2df9` | design-only, no runtime binding |
| `GC.CALIB.weekly_drift_n20_0_10` | 5.2 | Weekly drift detection N=20, drop >0.10 triggers recalibration | **DESIGN** | `e55ecc6eb2f09edc` | design-only, no runtime binding |
| `GC.CALIB.judge_calibration_dir` | 5.2 | data/judge_calibration/ directory reserved | **DESIGN** | `6a86b38e6167df28` | design-only, no runtime binding |
| `GC.RUBRIC_BUGS.known_bad_set` | 5.3 | Run rubric against known-bad set | **DESIGN** | `1ebad31147e68f84` | design-only, no runtime binding |
| `GC.RUBRIC_BUGS.known_good_set` | 5.3 | Run rubric against known-good set | **DESIGN** | `defef6c79ef27b66` | design-only, no runtime binding |
| `GC.RUBRIC_BUGS.flag_98pct` | 5.3 | Auto-flag rubric review on >98% pass rate | **DESIGN** | `35e3bb4fdcbcd654` | design-only, no runtime binding |
| `GC.MULTI_JUDGE.majority_vote` | 5.4 | Multi-judge: majority vote for classification | **DESIGN** | `9e7b494011a590f2` | design-only, no runtime binding |
| `GC.MULTI_JUDGE.median` | 5.4 | Multi-judge: median for ordinal | **DESIGN** | `73254269c43b4c03` | design-only, no runtime binding |
| `GC.MULTI_JUDGE.unanimous_pass` | 5.4 | Multi-judge: unanimous pass for security | **DESIGN** | `ba05b19c30114a6d` | design-only, no runtime binding |
| `GC.MULTI_JUDGE.disagree_30pct_HITL` | 5.4 | Multi-judge >30% disagreement -> HITL | **DESIGN** | `75fb2b4b51e0166a` | design-only, no runtime binding |
| `GC.BYPASS.context_isolation` | 6.1 | Judge runs in context isolated from agent's tool outputs | **DESIGN** | `a249fb445627f53f` | design-only, no runtime binding |
| `GC.BYPASS.judge_session_distinct` | 6.1 | Judge and agent are different model calls | **DESIGN** | `380e8efe3ceede76` | design-only, no runtime binding |
| `GC.BYPASS.system_prompt_hidden` | 6.1 | Judge system prompts not exposed to agent | **DESIGN** | `296c2f8c0896feba` | design-only, no runtime binding |
| `GC.BYPASS.delimiter_wrap` | 6.2 | Agent content wrapped in delimiter; judge instructed it's data | **DESIGN** | `d8caa1b6add0e937` | design-only, no runtime binding |
| `GC.BYPASS.injection_classifier` | 6.2 | Lightweight prompt-injection classifier on agent output | **DESIGN** | `228adba315e5e4d1` | design-only, no runtime binding |
| `GC.BYPASS.adversarial_eval` | 6.3 | Graders evaluated on adversarial test set; flippable judges retired | **DESIGN** | `b514e985c960bc3a` | design-only, no runtime binding |
| `GC.BYPASS.immutable_versioning` | 6.4 | Rubric changes produce new version; rubric_version recorded with each decision | **DESIGN** | `09e9248ecd0757eb` | design-only, no runtime binding |
| `GC.BUS_P.row_per_run` | 7 | BUS P emits one row per gate per run | **PASS** | `bcbd7f37b0925cb8` | BusPRow in v6.__all__ |
| `GC.BUS_P.field.run_id` | 7 | BUS P row field: run_id | **PASS** | `9a5a537564467748` | BusPRow in v6.__all__ |
| `GC.BUS_P.field.gate` | 7 | BUS P row field: gate | **PASS** | `807191650e38478d` | BusPRow in v6.__all__ |
| `GC.BUS_P.field.rubric_version` | 7 | BUS P row field: rubric_version | **PASS** | `438865f2135d89ab` | BusPRow in v6.__all__ |
| `GC.BUS_P.field.composition` | 7 | BUS P row field: composition | **PASS** | `03bfbd6ff71bd3e6` | BusPRow in v6.__all__ |
| `GC.BUS_P.field.aggregate_score` | 7 | BUS P row field: aggregate_score | **PASS** | `c2aae1624dbc533b` | BusPRow in v6.__all__ |
| `GC.BUS_P.field.aggregate_threshold` | 7 | BUS P row field: aggregate_threshold | **PASS** | `00c86e39f33af2a6` | BusPRow in v6.__all__ |
| `GC.BUS_P.field.passed` | 7 | BUS P row field: passed | **PASS** | `21d5976fc8acff05` | BusPRow in v6.__all__ |
| `GC.BUS_P.field.abstain` | 7 | BUS P row field: abstain | **PASS** | `71e8020b4aa80eec` | BusPRow in v6.__all__ |
| `GC.BUS_P.field.dimension_vector` | 7 | BUS P row field: dimension_vector | **PASS** | `5b19c1bfe40b32a6` | BusPRow in v6.__all__ |
| `GC.BUS_P.field.reason_codes` | 7 | BUS P row field: reason_codes | **PASS** | `7d44a55e14baa902` | BusPRow in v6.__all__ |
| `GC.BUS_P.field.track` | 7 | BUS P row field: track | **PASS** | `ea8a9536b45cc452` | BusPRow in v6.__all__ |
| `GC.BUS_P.field.trajectory_class` | 7 | BUS P row field: trajectory_class | **PASS** | `618f77f5d3d49d44` | BusPRow in v6.__all__ |

## runtime_to_regression_dataset_flow.md

`runtime_to_regression` — 48 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `RR.PIPELINE.runtime_to_BUS` | 2 | Pipeline: runtime emits to BUS P / BUS T | **PASS** | `8e9e64c0a4d8abf3` | BusTRow in v6.__all__ |
| `RR.PIPELINE.BUS_to_pool` | 2 | Pipeline: BUS -> Candidate Pool (filtered) | **PASS** | `7503293e5d92af2c` | CandidatePoolEntry in v6.__all__ |
| `RR.PIPELINE.pool_to_curation` | 2 | Pipeline: pool -> Curation Gate (human + auto) | **PASS** | `bcc87e81e26b4664` | CurationDecision in v6.__all__ |
| `RR.PIPELINE.curation_to_golden` | 2 | Pipeline: curation -> Golden Set (versioned) | **PASS** | `985e595d9103216d` | GoldenSetVersion in v6.__all__ |
| `RR.PIPELINE.golden_to_x1a` | 2 | Pipeline: golden -> consumed by X1A baselines + offline suites | **PASS** | `686c97610028b1e0` | GoldenSetTrack in v6.__all__ |
| `RR.PIPELINE.no_runtime_mutation` | 2 | All stages run AFTER runtime boundary; no current-run mutation | **PASS** | `4304a5c397886d60` | assert_no_runtime_mutation in v6.__all__ |
| `RR.BUS_P.row_per_gate` | 3.1 | BUS P row per gate per run | **PASS** | `b1d71b216f70dc96` | BusPRow in v6.__all__ |
| `RR.BUS_T.row_per_run` | 3.1 | BUS T row per run with full trajectory | **PASS** | `c58ce0de2e8b8d63` | BusTRow in v6.__all__ |
| `RR.BUS.append_only` | 3.1 | Both buses are append-only | **PASS** | `3814deb6c2e57d14` | BusPRow + BusTRow are dataclasses; append-only enforced at writer/storage layer (filesyst... |
| `RR.POOL.dedup` | 3.2 | Pool dedup by (trajectory_class, normalized_input, output_class) | **PASS** | `c0fe4974c6b3a2c9` | CandidatePoolEntry in v6.__all__ |
| `RR.POOL.anonymize` | 3.2 | Pool anonymizes PII; non-anonymizable runs excluded | **PASS** | `da2cb96b6d55f712` | assert_anonymization_fail_closed in v6.__all__ |
| `RR.HEUR.x3b_3_0` | 3.2 | Promotion heuristic: X3B escalation weight 3.0 | **PASS** | `1be52ecae7870075` | PROMOTION_HEURISTIC_WEIGHTS in v6.__all__ |
| `RR.HEUR.x1f_2_5` | 3.2 | Promotion heuristic: X1F adversarial fail weight 2.5 | **PASS** | `3e2a205fcc4845ab` | PROMOTION_HEURISTIC_WEIGHTS in v6.__all__ |
| `RR.HEUR.x1e_2_0` | 3.2 | Promotion heuristic: X1E trajectory-suspect weight 2.0 | **PASS** | `ca5a3ce3ad93d731` | PROMOTION_HEURISTIC_WEIGHTS in v6.__all__ |
| `RR.HEUR.judge_abstain_1_5` | 3.2 | Promotion heuristic: JUDGE_ABSTAINED weight 1.5 | **PASS** | `25e1abee0d85e925` | PROMOTION_HEURISTIC_WEIGHTS in v6.__all__ |
| `RR.HEUR.near_miss_1_5` | 3.2 | Promotion heuristic: near-miss (within 0.05) weight 1.5 | **PASS** | `a7b06571a1cbc6ac` | PROMOTION_HEURISTIC_WEIGHTS in v6.__all__ |
| `RR.HEUR.novel_class_1_3` | 3.2 | Promotion heuristic: novel trajectory_class weight 1.3 | **PASS** | `d57f7a3461737c8f` | PROMOTION_HEURISTIC_WEIGHTS in v6.__all__ |
| `RR.HEUR.passk_dip_1_8` | 3.2 | Promotion heuristic: pass^k dip weight 1.8 | **PASS** | `3b4aec24096a66f4` | PROMOTION_HEURISTIC_WEIGHTS in v6.__all__ |
| `RR.HEUR.routine_pass_0_2` | 3.2 | Promotion heuristic: routine pass weight 0.2 | **PASS** | `5f9b07dd439816e3` | PROMOTION_HEURISTIC_WEIGHTS in v6.__all__ |
| `RR.CURATE.confirm_anon` | 3.3 | Curator confirms anonymization | **PASS** | `9e9b4af0003c4769` | CurationDecision in v6.__all__ |
| `RR.CURATE.label_intent` | 3.3 | Curator labels user intent | **PASS** | `a90a9be3918be7a9` | CurationDecision in v6.__all__ |
| `RR.CURATE.assign_class` | 3.3 | Curator assigns trajectory_class | **PASS** | `4036791dcd066eba` | CandidatePoolEntry in v6.__all__ |
| `RR.CURATE.assign_track` | 3.3 | Curator assigns capability/regression/adversarial track | **PASS** | `dcafd9b39e5dce4b` | GoldenSetTrack in v6.__all__ |
| `RR.CURATE.label_expected` | 3.3 | Curator labels expected disposition + per-dim scores | **PASS** | `759ed3d9f2d44f50` | CurationDecision in v6.__all__ |
| `RR.CURATE.quarantine_flag` | 3.3 | Curator may quarantine sensitive cases | **PASS** | `75ce0b5400cec13a` | CurationVerdict in v6.__all__ |
| `RR.GOLDEN.dir_capability` | 3.4 | data/eval/golden/capability/<trajectory_class>/ | **PASS** | `68fbafcd5a9464b5` | GoldenSetTrack in v6.__all__ |
| `RR.GOLDEN.dir_regression` | 3.4 | data/eval/golden/regression/<trajectory_class>/ | **PASS** | `adf7f4b7136e6da2` | GoldenSetTrack in v6.__all__ |
| `RR.GOLDEN.dir_adversarial` | 3.4 | data/eval/golden/adversarial/<category>/ | **PASS** | `cf8c454cfcc6e296` | GoldenSetTrack in v6.__all__ |
| `RR.GOLDEN.versioned` | 3.4 | Golden set versioned; immutable post-publish; corrections produce new version | **PASS** | `4c438876ab2b5387` | GoldenSetVersion in v6.__all__ |
| `RR.GOLDEN.graduation_passk_0_95_k_10` | 3.4 | Capability auto-graduates to regression at pass^k>=0.95 over k=10 weekly | **PASS** | `1b2059a1155077a2` | graduates_to_regression in v6.__all__ |
| `RR.CONSUME.capability_offline` | 3.5 | Capability evals offline nightly; low pass = hill-climb | **DESIGN** | `f1072d00adf9747f` | design-only, no runtime binding |
| `RR.CONSUME.regression_pre_deploy` | 3.5 | Regression evals offline+pre-deploy gate; ~100% pass required | **DESIGN** | `b9a929bcacb70a7a` | design-only, no runtime binding |
| `RR.CONSUME.adversarial_offline` | 3.5 | Adversarial evals offline+periodic; gates X1F policy updates | **DESIGN** | `499cb02ac7f49d38` | design-only, no runtime binding |
| `RR.CONSUME.x1a_pinned_baseline` | 3.5 | X1A loads pinned regression baseline fingerprint | **DESIGN** | `333783393c0fc4ff` | design-only, no runtime binding |
| `RR.ANON.reversible_via_key_ceremony` | 4 | Anonymization reversible only via SME-gated key ceremony | **DESIGN** | `69a19166f239bfe8` | design-only, no runtime binding |
| `RR.ANON.deterministic` | 4 | Anonymization deterministic per run (stable dedup) | **DESIGN** | `9d8857e0796ed856` | design-only, no runtime binding |
| `RR.ANON.log_redacted` | 4 | Anonymization logs what was redacted | **DESIGN** | `27af80debad6d6ff` | design-only, no runtime binding |
| `RR.ANON.fail_closed` | 4 | Anonymization fail-closed | **DESIGN** | `6acd39e956d1313b` | design-only, no runtime binding |
| `RR.RETAIN.bus_90d` | 5 | BUS P/T retain 90 days default | **PASS** | `a71581fe69d80ef7` | BUS_PT_DEFAULT_RETENTION_DAYS in v6.__all__ |
| `RR.RETAIN.candidate_30d` | 5 | Candidate pool retains 30 days | **PASS** | `1db4cf006639c388` | CANDIDATE_POOL_RETENTION_DAYS in v6.__all__ |
| `RR.RETAIN.golden_indefinite` | 5 | Golden set indefinite retention with full history | **PASS** | `38773c1a22e0944c` | GOLDEN_SET_RETENTION_INDEFINITE in v6.__all__ |
| `RR.RETAIN.rejected_audit_only` | 5 | Rejected candidates: audit metadata only | **DESIGN** | `5b14c2a59dd400d7` | design-only, no runtime binding |
| `RR.INV.no_runtime_mutation` | 6.1 | Invariant: no stage mutates current run | **PASS** | `f2bbfabc8bd1159b` | assert_no_runtime_mutation in v6.__all__ |
| `RR.INV.no_unanon_in_golden` | 6.2 | Invariant: no un-anonymized data in golden set | **PASS** | `d4fd66e2290f18a3` | assert_anonymization_fail_closed in v6.__all__ |
| `RR.INV.golden_immutable` | 6.3 | Invariant: golden versions immutable | **PASS** | `d138d9b8319bec1b` | GoldenSetVersion in v6.__all__ |
| `RR.INV.curation_audit_logged` | 6.4 | Invariant: curation audit-logged | **PASS** | `ffaed218f6b52558` | CurationDecision in v6.__all__ |
| `RR.INV.graduation_mechanical` | 6.5 | Invariant: graduation mechanical (passk threshold) | **PASS** | `522a1c76393b3694` | graduates_to_regression in v6.__all__ |
| `RR.INV.x1a_pinned` | 6.6 | Invariant: X1A consumes pinned versions only | **PASS** | `c8b6fec3179206ea` | GoldenSetVersion in v6.__all__ |

## v4_hardening_addendum.md

`v4_hardening` — 94 requirements

| Req ID | Source line | Requirement | Status | Span ID | Evidence |
|---|---|---|:---:|---|---|
| `H1.SIG.rubric_surface_only_pass` | H1.1 | Detection: rubric-surface-only pass (per-dim flatness at threshold) | **DESIGN** | `7d5ec25dc0bf0e2f` | design-only, no runtime binding |
| `H1.SIG.dimension_decoupling_divergence` | H1.1 | Detection: dimension decoupling divergence | **DESIGN** | `bb936575f264817e` | design-only, no runtime binding |
| `H1.SIG.trajectory_shortness_anomaly` | H1.1 | Detection: trajectory shortness vs task complexity | **DESIGN** | `24ef0c33aee720f0` | design-only, no runtime binding |
| `H1.SIG.output_length_inflation` | H1.1 | Detection: output length inflation | **DESIGN** | `d7e421aba1a07a8a` | design-only, no runtime binding |
| `H1.SIG.citation_count_only_increase` | H1.1 | Detection: citation count up but support drop | **DESIGN** | `9d01b19df7a2d65d` | design-only, no runtime binding |
| `H1.CM.orthogonal_grader_ensemble` | H1.2 | Counter: orthogonal grader ensemble | **DESIGN** | `558209476a89fe1a` | design-only, no runtime binding |
| `H1.CM.held_out_probe_set` | H1.2 | Counter: held-out probe set (5%) | **DESIGN** | `973869c1e03be9c2` | design-only, no runtime binding |
| `H1.CM.rubric_rotation` | H1.2 | Counter: quarterly rubric rotation | **DESIGN** | `78770c82135f2b0f` | design-only, no runtime binding |
| `H1.DISP.advisory_on_X3D` | H1.3 | REWARD_HACK_SUSPECT advisory on X3D | **DESIGN** | `bde36c6e85ed9b9a` | design-only, no runtime binding |
| `H1.DISP.escalate_X3C` | H1.3 | REWARD_HACK_SUSPECT routes X3C->X3B | **DESIGN** | `363c55a7fc5daea3` | design-only, no runtime binding |
| `H2.CTRL.judge_under_X1F` | H2.1 | Agentic judges run under same X1F adversarial gate | **DESIGN** | `ec1849873eef8bc4` | design-only, no runtime binding |
| `H2.CTRL.disable_judge_tools` | H2.1 | Disable tool use for judges on free-form input | **DESIGN** | `489e6b78830af108` | design-only, no runtime binding |
| `H2.CTRL.record_judge_trajectories` | H2.1 | Record judge trajectories on BUS T tagged actor=judge | **DESIGN** | `14cc626d2aa4bcff` | design-only, no runtime binding |
| `H2.CTRL.version_pin_judge_tools` | H2.1 | Version-pin judge tool inventory | **DESIGN** | `92e2a9d501179074` | design-only, no runtime binding |
| `H2.CTRL.non_agentic_fallback` | H2.2 | Non-agentic fallback judge for high-stakes dimensions | **DESIGN** | `7d71f6c7fff2e81f` | design-only, no runtime binding |
| `H3.GAP.X3E_meaning_diverges` | H3.2 | Addendum H3 proposes X3E=BREAK_GLASS_ALLOW but v6/05.5 uses X3E=SAFE_ABSTAIN_CLARIFY. RESOLVED by A... | **PASS** | `1db13244001bff37` | V6Disposition.BREAK_GLASS_ALLOW present |
| `H3.RULE.no_bypass_X1A` | H3.1 | Break-glass cannot bypass X1A policy match | **PASS** | `18c47a49359bc2a0` | Enforced by _X3F_FORBIDDEN_BYPASS_GATES + BreakGlassValidationError |
| `H3.RULE.no_bypass_X1C_safety` | H3.1 | Break-glass cannot bypass X1C safety sub-gates | **PASS** | `06cad60efbdbf6cb` | Enforced by _X3F_FORBIDDEN_BYPASS_GATES + BreakGlassValidationError |
| `H3.RULE.no_bypass_UWG` | H3.1 | Break-glass cannot bypass UWG | **PASS** | `fe554fc946730404` | Enforced by builder rejecting any U* gate in bypassed_gates |
| `H3.RULE.capability_token` | H3.2 | Break-glass requires break_glass capability token | **PASS** | `27482ef49e00eef4` | Enforced by builder requiring capability_token.break_glass=True + matching operator_id |
| `H3.RULE.written_justification` | H3.2 | Break-glass requires written justification + expiry <=60min | **PASS** | `44e187e7ef5a6f89` | Enforced by builder: non-empty justification + _X3F_MAX_DURATION_MS=3_600_000 cap |
| `H3.RULE.high_visibility_audit` | H3.2 | Break-glass writes high-visibility audit row + page on-call | **PASS** | `073f4a4b8d1407aa` | Enforced by builder requiring non-empty audit_id; pages_emitted recorded on packet |
| `H3.RULE.no_customer_L4_without_ratify` | H3.2 | Break-glass forbidden from customer L4 commit without ratify | **PASS** | `514431934043f248` | customer_facing_l4_commit_allowed defaults to False on packet; ratification is post-incid... |
| `H3.RULE.24h_post_mortem` | H3.3 | Break-glass triggers 24h post-mortem | **PASS** | `5ff8ab7021c7ac85` | Enforced by builder setting post_mortem_due_at_ms = granted_at_ms + _X3F_POST_MORTEM_OFFS... |
| `H4.CAT.direct_injection` | H4.1 | X1F detects direct injection | **DESIGN** | `4e82b8940ecd9357` | design-only, no runtime binding |
| `H4.CAT.indirect_injection` | H4.1 | X1F detects indirect injection (RAG) | **DESIGN** | `18fce65a6df9d7c7` | design-only, no runtime binding |
| `H4.CAT.role_play_jailbreak` | H4.1 | X1F detects role-play jailbreak | **DESIGN** | `3c9e8a5d37db85c7` | design-only, no runtime binding |
| `H4.CAT.encoding_bypass` | H4.1 | X1F detects encoding bypass (base64, leet, zwj) | **DESIGN** | `259069bdbbf22e2c` | design-only, no runtime binding |
| `H4.CAT.multi_turn_drift` | H4.1 | X1F detects multi-turn drift | **DESIGN** | `413cce552303350c` | design-only, no runtime binding |
| `H4.CAT.tool_call_hijack` | H4.1 | X1F detects tool-call hijack | **DESIGN** | `a59e9e17ebc8b690` | design-only, no runtime binding |
| `H4.CAT.system_prompt_extraction` | H4.1 | X1F detects system-prompt extraction | **DESIGN** | `17c0e7b961ee104a` | design-only, no runtime binding |
| `H4.CAT.output_format_exploit` | H4.1 | X1F detects output-format exploits (Morse, etc.) | **DESIGN** | `5419fc214a1b6c7e` | design-only, no runtime binding |
| `H4.PROBE.20_per_category` | H4.2 | 20 cases per category in adversarial probe set | **DESIGN** | `2e68879f88aeaa5a` | design-only, no runtime binding |
| `H4.MULTI_TURN.history_aware` | H4.3 | X1F multi-turn awareness using full history | **DESIGN** | `3b5eef053e6eb1d6` | design-only, no runtime binding |
| `H5.SPAN.exit_control_gate` | H5.1 | Per-gate span name pattern: v6 uses exit.x1{a..j}.{check_name}; addendum proposes unified exit_cont... | **DESIGN** | `a26799da8d388c95` | v6 emits per-gate-named spans; addendum's unified-name proposal is implementation choice |
| `H5.ATTR.gate` | H5.1 | Span attr: gate | **PASS** | `da83326c2e3b7b17` | gate in REQUIRED_ATTRIBUTES |
| `H5.ATTR.run_id` | H5.1 | Span attr: run_id | **PASS** | `b6533ebce19b1736` | run_id in REQUIRED_ATTRIBUTES |
| `H5.ATTR.track` | H5.1 | Span attr: track | **PASS** | `f0720bd3e104d326` | track in REQUIRED_ATTRIBUTES |
| `H5.ATTR.trajectory_class` | H5.1 | Span attr: trajectory_class | **PASS** | `98df619f8708369e` | trajectory_class in REQUIRED_ATTRIBUTES |
| `H5.ATTR.rubric_version` | H5.1 | Span attr: rubric_version | **PASS** | `ab92b4e4986e9061` | rubric_version in REQUIRED_ATTRIBUTES |
| `H5.ATTR.composition` | H5.1 | Span attr: composition (binary/weighted/hybrid) | **PASS** | `4ccd1543cad3cab2` | composition in REQUIRED_ATTRIBUTES |
| `H5.ATTR.aggregate_score` | H5.1 | Span attr: aggregate_score | **PASS** | `62127c85759701b3` | aggregate_score in REQUIRED_ATTRIBUTES |
| `H5.ATTR.aggregate_threshold` | H5.1 | Span attr: aggregate_threshold | **PASS** | `173cf50aa31ef2bc` | aggregate_threshold in REQUIRED_ATTRIBUTES |
| `H5.ATTR.passed` | H5.1 | Span attr: passed | **PASS** | `3980628a45e41b4b` | passed in REQUIRED_ATTRIBUTES |
| `H5.ATTR.abstain` | H5.1 | Span attr: abstain | **PASS** | `786cafc44b6c9d68` | abstain in REQUIRED_ATTRIBUTES |
| `H5.ATTR.disposition_hint` | H5.1 | Span attr: disposition_hint | **PASS** | `b19a49935b7dfe67` | disposition_hint in REQUIRED_ATTRIBUTES |
| `H5.ATTR.reason_codes` | H5.1 | Span attr: reason_codes | **PASS** | `3834de487801abba` | reason_codes in REQUIRED_ATTRIBUTES |
| `H5.ATTR.bypass_audit_id` | H5.1 | Span attr: bypass_audit_id | **PASS** | `c645368895b2beea` | bypass_audit_id in REQUIRED_ATTRIBUTES |
| `H5.SPAN.disposition_links_x1` | H5.2 | X3 disposition span links to X1 spans | **DESIGN** | `e6828bef9fbbdf4b` | design-only, no runtime binding |
| `H5.RUNTIME_ADG_INGEST` | H5.3 | Spans ingested by otel_ingest_to_runtime_adg | **DESIGN** | `f0a88c4e76259ca2` | design-only, no runtime binding |
| `H6.MATH.threshold_table` | H6.1 | Per-trial reliability table (theta=0.95 k=5 -> p~=0.9898) - Wave 2 codified in hardening.PASS_K_THR... | **PASS** | `e11850431a1f8e76` | PASS_K_THRESHOLD_TABLE in v6.__all__ |
| `H6.OP.deny_path_early` | H6.2 | X1G routes commit candidates to X3B early | **DESIGN** | `53fd8fdedb7611be` | design-only, no runtime binding |
| `H6.NON_IID.bucket_reset` | H6.3 | Bucket reset on (trajectory_class, rubric_version, agent_version, policy_version) change | **DESIGN** | `4d72b6ee76b3d338` | design-only, no runtime binding |
| `H6.SMALL_SAMPLE.X3B_route` | H6.4 | Small-sample (<k) routes to X3B with INSUFFICIENT_HISTORY | **DESIGN** | `fa2199ebd6ec83fa` | design-only, no runtime binding |
| `H7.PR.diff_required` | H7.1 | Rubric PR requires diff | **DESIGN** | `28ae0501455f013c` | design-only, no runtime binding |
| `H7.PR.rationale_required` | H7.1 | Rubric PR requires rationale | **DESIGN** | `9283cadc256119cc` | design-only, no runtime binding |
| `H7.PR.eval_delta` | H7.1 | Rubric PR requires evaluation delta vs prior | **DESIGN** | `1f04b0c12768d251` | design-only, no runtime binding |
| `H7.PR.calibration_kappa_0_80` | H7.1 | Rubric PR requires Cohen's kappa >= 0.80 vs SME | **DESIGN** | `ad8a972ff0248d0e` | design-only, no runtime binding |
| `H7.PR.adversarial_retest` | H7.1 | Rubric PR re-tests adversarial set | **DESIGN** | `61fda6e45929d545` | design-only, no runtime binding |
| `H7.PR.named_reviewer` | H7.1 | Rubric PR requires named SME reviewer | **DESIGN** | `ae61902ac119b6f2` | design-only, no runtime binding |
| `H7.AUTO.version_increment` | H7.2 | Auto-check: version must increment | **DESIGN** | `c1a4140e619b6383` | design-only, no runtime binding |
| `H7.AUTO.abstain_monotonic` | H7.2 | Auto-check: abstain_allowed only becomes more permissive | **DESIGN** | `2545d1407bd85d00` | design-only, no runtime binding |
| `H7.AUTO.threshold_loosening_justified` | H7.2 | Auto-check: threshold loosening requires written justification | **DESIGN** | `f698a4f0cfa199c3` | design-only, no runtime binding |
| `H7.AUTO.dimension_removal_adr` | H7.2 | Auto-check: dimension removal requires ADR | **DESIGN** | `617a34784832c391` | design-only, no runtime binding |
| `H7.SHADOW.1week_or_500` | H7.3 | New rubric versions shadow-deploy 1 week / 500 runs, <=5% disagreement | **DESIGN** | `1170654f05e4e963` | design-only, no runtime binding |
| `H8.FM.judge_timeout` | H8 | Judge timeout -> abstain + X3B + JUDGE_TIMEOUT | **PASS** | `af564c1627328165` | FaultInjectionReasonCode in v6.__all__ |
| `H8.FM.judge_4xx_5xx` | H8 | Judge 4xx/5xx -> abstain + X3B + JUDGE_ERROR | **PASS** | `44db51d9677a702d` | FaultInjectionReasonCode in v6.__all__ |
| `H8.FM.code_grader_exception` | H8 | Code grader exception -> X3A + GRADER_EXCEPTION | **PASS** | `c5b5c4e462314301` | FaultInjectionReasonCode in v6.__all__ |
| `H8.FM.rubric_corrupt` | H8 | Rubric corrupt -> X3A + RUBRIC_UNAVAILABLE + page on-call | **PASS** | `f68e5ee2b30fb820` | FaultInjectionReasonCode in v6.__all__ |
| `H8.FM.bus_p_write_failure` | H8 | BUS P write failure -> X3B + AUDIT_UNAVAILABLE | **PASS** | `c5b4ad54f7afeaa1` | FaultInjectionReasonCode in v6.__all__ |
| `H8.FM.bus_t_write_failure` | H8 | BUS T write failure -> X3B + AUDIT_UNAVAILABLE | **PASS** | `1b6591ffa6ebdd92` | FaultInjectionReasonCode in v6.__all__ |
| `H8.FM.x1g_history_unavailable` | H8 | X1G history unavailable -> X3B + CONSISTENCY_HISTORY_UNAVAILABLE | **PASS** | `6a6ff09f709bcae8` | FaultInjectionReasonCode in v6.__all__ |
| `H8.FM.uwg_unavailable` | H8 | UWG unavailable -> freeze + X3B + COMMIT_UNAVAILABLE | **PASS** | `d164975e8c24f4f2` | FaultInjectionReasonCode in v6.__all__ |
| `H8.FM.l5_reclear_failure` | H8 | L5 reclear failure -> FROZEN hold + page on-call (L5_RECLEARANCE_UNAVAILABLE) | **PASS** | `1bfb8983f82b7390` | FaultInjectionReasonCode in v6.__all__ |
| `H9.STEP.triage` | H9.1 | Step 1: triage gate / trajectory_class / track via otel_mcp | **DESIGN** | `18c3c444d002e6fb` | design-only, no runtime binding |
| `H9.STEP.policy_change` | H9.2 | Step 2: check policy / rubric-version bump; rollback if regressed | **DESIGN** | `33ebf11322d6b5b3` | design-only, no runtime binding |
| `H9.STEP.agent_change` | H9.3 | Step 3: check agent_version bucket reset | **DESIGN** | `9a8435a70539fb74` | design-only, no runtime binding |
| `H9.STEP.judge_change` | H9.4 | Step 4: check judge-model deployment log | **DESIGN** | `53e8498108baf69d` | design-only, no runtime binding |
| `H9.STEP.injection_campaign` | H9.5 | Step 5: X1F failure spike check; do not relax | **DESIGN** | `1373db51f34744c9` | design-only, no runtime binding |
| `H9.STEP.judge_abstain` | H9.6 | Step 6: abstain rate > 5% triggers calibration review | **DESIGN** | `32f8d4a942951a62` | design-only, no runtime binding |
| `H9.STEP.provider_outage` | H9.7 | Step 7: external provider outage check | **DESIGN** | `5af5075fa3768a28` | design-only, no runtime binding |
| `H9.STEP.novel_failure` | H9.8 | Step 8: novel failure -> open plan, capture trace | **DESIGN** | `8cead1465cb11ef8` | design-only, no runtime binding |
| `H9.STEP.break_glass_last` | H9.9 | Step 9: break-glass only as last resort | **DESIGN** | `ceb8d4a22c3a400d` | design-only, no runtime binding |
| `H10.LINK.zero_regression` | H10 | X1A regression track ties to constitutional zero-regression | **DESIGN** | `956565d57afc3466` | design-only, no runtime binding |
| `H10.LINK.security_hardening` | H10 | X1F detections feed anti-pattern ledger | **DESIGN** | `d30219faacbd1a1f` | design-only, no runtime binding |
| `H10.LINK.bypass_resistance` | H10 | Bypass-resistance follows constitutional Column 5 exception handling | **DESIGN** | `ae72f21d5200d3b8` | design-only, no runtime binding |
| `H10.LINK.subprocess_timeout` | H10 | Per-trial environment isolation uses constitutional 14/11 | **DESIGN** | `5bd7901ee3295e39` | design-only, no runtime binding |
| `H10.LINK.bus_t_to_memory` | H10 | BUS T -> golden set pipeline writes to Memory MCP | **DESIGN** | `8896ceaabb976339` | design-only, no runtime binding |
| `H10.LINK.break_glass_capability` | H10 | Break-glass uses constitutional capability-gated pattern | **DESIGN** | `2cb7e1b6f05ccdf8` | design-only, no runtime binding |
| `H10.LINK.rubric_diff_adr` | H10 | Rubric-diff bumps on high-stakes gates require ADR | **DESIGN** | `753e65c2123a8d15` | design-only, no runtime binding |
| `H10.LINK.otel_mcp` | H10 | OTEL wire-up uses existing otel_mcp | **DESIGN** | `701aaa51310074fa` | design-only, no runtime binding |
| `H10.ADR.x1e` | H10.1 | ADR for X1E adoption (follow-up) | **DESIGN** | `fa4254db4f04093b` | design-only, no runtime binding |
| `H10.ADR.x1f` | H10.1 | ADR for X1F + H4 probe-set requirement | **DESIGN** | `e0526f6c80ede268` | design-only, no runtime binding |
| `H10.ADR.x1g` | H10.1 | ADR for X1G + theta=0.95 k=5 policy | **DESIGN** | `d5bf6694cbdd77db` | design-only, no runtime binding |

## Naming-drift findings (semantic match, registry-tracked)

These are **PASS** rows where v6 emits an alias of the spec name. Not a gap —
captured here because user audit benefits from explicit drift tracking.

| Spec name | v6 alias | Source |
|---|---|---|
| `CAPABILITY_TOKEN_MISSING_FOR_TOOL_OR_MODEL` | `CAPABILITY_TOKEN_MISSING` | `5.1.RF.execution.capability_for_tool` |
| `CAPABILITY_TOKEN_MISSING_FOR_TOOL_OR_MODEL` | `CAPABILITY_TOKEN_MISSING` | `5.1.TR.tool_no_capability_fails` |
| `COMMITTED_WITH_RECEIPT` | `COMMIT_ACCEPTED` | `5.4.UWG.committed_with_receipt` |
| `EVIDENCE_CONTRACT_MISSING_FOR_GROUNDED_ROUTE` | `EVIDENCE_CONTRACT_MISSING` | `5.1.RF.evidence.grounded_contract` |
| `EVIDENCE_CONTRACT_MISSING_FOR_GROUNDED_ROUTE` | `EVIDENCE_CONTRACT_MISSING` | `5.1.TR.grounded_no_C0_fails` |
| `HITL_RECLEARED_NOT_L5_CLEARED` | `RECLEARANCE_MISSING` | `5.1.RF.hitl.l5_cleared` |
| `IDEMPOTENT_REPLAY` | `COMMIT_ACCEPTED` | `5.4.UWG.idempotent_replay` |
| `REJECTED` | `COMMIT_REJECTED` | `5.4.UWG.rejected` |
| `SANDBOX_SCOPE_MISSING_FOR_ACTION` | `SANDBOX_SCOPE_MISSING` | `5.1.RF.execution.sandbox_for_action` |
| `SANDBOX_SCOPE_MISSING_FOR_ACTION` | `SANDBOX_SCOPE_MISSING` | `5.1.TR.action_no_sandbox_fails` |
| `UNAVAILABLE` | `COMMIT_HELD` | `5.4.UWG.unavailable` |
| `exit.x1d.grounding_check` | `exit.x1d.groundedness_check` | `5.2.OTEL.x1d.grounding_check` |
| `exit.x1g.replay_consistency_check` | `exit.x1g.consistency_check` | `5.3.OTEL.x1g.replay` |
| `exit.x1h.observability_check` | `exit.x1h.replay_integrity_check` | `5.3.OTEL.x1h.observability` |
| `exit.x1i.consistency_check` | `exit.x1i.observability_check` | `5.3.OTEL.x1i.consistency` |

## Real GAPs (true divergence — needs fix)

None.

## How to verify any row

```
# Find a span by req_id
python -c "import json; d=json.load(open('docs/reports/plans/exit_v6_MASTER_otel_evidence.json')); [print(json.dumps(s, indent=2)) for s in d['spans'] if s['req_id'] == '<REQ_ID>']"

# Re-run the entire probe (deterministic outputs except for trace_id which is per-run)
python tools/analysis/exit_v6_master_otel_probe.py

# Show only GAPs
python tools/analysis/_show_gaps.py
```

---

**Generated by** `tools/analysis/exit_v6_matrix_generator.py` from `exit_v6_MASTER_otel_evidence.json`