========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: 99_End_to_End_Runtime_Proof_and_Acceptance.md
Layer / subsystem: 99 — End-to-End Runtime Proof and Acceptance (parent)
Parent file: docs/reference/README.md
Ownership surface: Cross-layer acceptance proof. Owns the **scenario-level** REQ_IDs that cross every layer; per-stage E2E REQ_IDs live in `99.1`..`99.10`; the compiler contract lives in `99.11`.
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: 99 owns proof harnesses only. It does not own runtime behavior, gate law, retrieval, prompt assembly, execution, durable-write admission, certification, or future-run learning.
Source authority notes: Anchored on `00X` REQ_ID registry; aligned with constitutional §22, §23, §24.
Predecessor preserved at: `99_End_to_End_Runtime_Proof_and_Acceptance.md.pre-reqid-rewrite.bak`
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent uniquely owns:
- the cross-layer scenario contract (Golden Path, Route Coverage, Contract Handoff, OTEL Tree, Replay, No-Bypass, Groundedness, Acceptance Commands, Mutation, Fixtures)
- the scenario-level REQ_IDs (`REQ-E2E-*`) and OTEL trace-tree REQ_IDs (`REQ-TRACE-*`) at the parent level
- the proof bundle minimum standard
- the acceptance rule that distinguishes a "looks correct" answer from a proven run

It does **not** own:
- per-scenario detail (lives in `99.1`..`99.10`)
- the requirements compiler (`99.11`)
- runtime behavior, gates, dispositions, or durable writes

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**: every layer's runtime artifacts, OTEL spans, validator receipts, replay receipts.

**Downstream outputs**: a release-blocking decision derived through `99.11`, plus the 10 E2E child proof bundles.

**Forbidden behaviors**: runtime mutation, retrieval, execution, gate verdict authoring, durable write, certification.

**Allowed outputs only**: scenario-level proof bundles and the release decision derived from them.

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
This parent owns rows under `REQ-E2E-*` and `REQ-TRACE-*`.

Per-scenario detailed REQ_IDs (e.g. `REQ-E2E-GOLDEN-PATH-*`, `REQ-E2E-REPLAY-*`) are owned by the matching child file.
The compiler-contract namespace `REQ-COMPILER-*` is owned by `99.11`.

4. ATOMIC REQUIREMENTS TABLE
------------------------------------------------------------------------------------------------------------------------

| REQ_ID | Requirement | Owner | Inputs | Outputs | Runtime Evidence | OTEL Span | Artifact / Receipt | Validator | Negative Control | Expected Fail Reason | Replay Check | Release Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-E2E-PROOF-BUNDLE-MIN-001` | Every accepted scenario MUST produce a proof bundle containing scenario_id, request_id, run_id, trace_root, policy_hash, blueprint_hash, replay_key, RouteContract or terminal route packet, FinalEvidenceContract when grounding is required, PromptEnvelope or CompiledPromptArtifact when model execution is required, sealed L2 artifact or terminal RET packet, ExitReviewPacket, X1 verdict bundle, X3 disposition, CommitRequest+UWG receipt when durable mutation is requested, RuntimeExhaustBundle, OTEL span tree, replay comparison receipt, no-bypass assertion, artifact manifest with deterministic digest. | 99 | scenario fixture | `proof_bundle.tar.gz` | every listed object present and hash-linked | `e2e.proof_bundle` (parent); child layer spans linked via parent/child | `proof_bundle.sha256` | `validator: proof_bundle_completeness_validator` (release-gate) | `NC-E2E-MISSING-OBJECT-001`: omit ExitReviewPacket from a non-cache scenario | `proof_bundle_object_missing` | `byte_identical` of bundle digest under fixed inputs | DOC_ONLY (until 99.x impl lands) |
| `REQ-E2E-NOT-RUNTIME-AUTHORITY-001` | The 99 pack MUST NOT emit live runtime dispositions or own gate law; it observes and proves. | 99 | (governance) | (none) | scenario receipts contain only proof statuses | NOT_APPLICABLE: 99 emits no runtime decision span | `governance_check.json` | `validator: e2e_no_runtime_authority_validator` (CI) | `NC-E2E-RUNTIME-LEAK-001`: 99 child file emits `ALLOW_FINISH` | `e2e_emitted_runtime_disposition` | `digest_match_only` against allowed-vocabulary set | DOC_ONLY |
| `REQ-E2E-GOLDEN-PATH-CHAIN-001` | The Golden Path scenario MUST prove U0 → L1 → L0 → C0 → PA → L2 → Exit emits the expected contracts and trace spans in that order. | 99.1 | golden fixture | bundle | full chain present in trace | parent span `e2e.golden_path` with 7 child spans matching layers | `golden_path_bundle.json` | `validator: golden_path_chain_validator` (release-gate) | `NC-E2E-GOLDEN-MISSING-PA-001`: bypass PA span | `pa_span_missing_in_chain` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-E2E-ROUTE-COVERAGE-001` | The Route Coverage scenario MUST exercise every RouteContract execution_form (cache, fallback, grounded read, single action, managed workflow, HITL). | 99.2 | route fixtures | bundle | each route exercised at least once with distinct route_digest | `e2e.route_coverage` parent + 6 child spans | `route_coverage_bundle.json` | `validator: route_coverage_validator` (release-gate) | `NC-E2E-ROUTE-SKIP-001`: skip managed_workflow execution_form | `route_form_uncovered` | `digest_match_only` per route_digest | DOC_ONLY |
| `REQ-E2E-CONTRACT-HANDOFF-001` | Every layer-to-layer handoff MUST emit the upstream contract id in the downstream contract's `lineage` and the downstream span's `attributes.parent_contract_id`. | 99.3 | full chain | bundle | lineage chain unbroken | parent/child spans carry `parent_contract_id` | `contract_handoff_bundle.json` | `validator: contract_handoff_validator` (release-gate) | `NC-E2E-LINEAGE-BREAK-001`: drop lineage on PA→L2 handoff | `lineage_chain_break` | `byte_identical` | DOC_ONLY |
| `REQ-TRACE-ROOT-COMPLETE-001` | Every E2E scenario MUST emit a single `trace_root` span; all layer spans MUST be descendants of this root with intact parent_span_id chains. | 99.4 | OTEL export | bundle | trace tree single-rooted | `trace_root` is ROOT; all child spans recursively reachable | `otel_trace_export.json` | `validator: trace_completeness_validator` (release-gate) | `NC-TRACE-DUAL-ROOT-001`: emit two roots in one run | `multiple_trace_roots` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-TRACE-PARENT-CHILD-LINK-001` | Every layer span MUST declare the correct parent_span_id; orphan spans are not allowed. | 99.4 | OTEL export | bundle | every span has resolvable parent in same trace_root | parent/child links validated | `otel_chain_validation.json` | `validator: otel_chain_validator` (release-gate) | `NC-TRACE-ORPHAN-SPAN-001`: emit span with parent_span_id pointing nowhere | `parent_span_unresolvable` | `byte_identical` | DOC_ONLY |
| `REQ-E2E-REPLAY-DETERMINISTIC-001` | Every scenario MUST replay byte-identical (or semantic-identical with declared allowed_nondeterminism) under the same input fingerprint, policy_hash, blueprint_hash, registry_digest, and source_snapshot_manifest. | 99.5 | scenario fixture × 2 runs | bundle | digests match per declared `match_type` | `e2e.replay` parent + 2 child runs | `replay_receipt.json` | `validator: e2e_replay_validator` (release-gate) | `NC-E2E-REPLAY-DRIFT-001`: inject wall-clock dependency in PA hash | `replay_drift_unallowed_field` | `byte_identical` declared explicitly per scenario | DOC_ONLY |
| `REQ-E2E-NO-BYPASS-001` | Every scenario MUST prove no layer bypassed L5 certification, 00C runtime gates, Exit, UWG, or L6 firewalls. | 99.6 | scenario | bundle | bypass attempts logged and blocked | `e2e.no_bypass` span with attempted-bypass attributes | `no_bypass_bundle.json` | `validator: no_bypass_validator` (release-gate) | `NC-E2E-DIRECT-L4-WRITE-001`: L2 attempts L4 write directly | `direct_l4_write_attempt` | `byte_identical` of bypass-attempt log | DOC_ONLY |
| `REQ-E2E-GROUNDEDNESS-001` | When grounding is required, every claim in the model output MUST trace to a citation in `FinalEvidenceContract`; ungrounded claims fail the row. | 99.7 | model output | bundle | claims-to-citations mapping complete | `e2e.groundedness` parent | `groundedness_bundle.json` | `validator: groundedness_validator` (release-gate) | `NC-E2E-FAB-CITATION-001`: model adds a citation that does not exist in evidence | `fabricated_citation` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-E2E-ACCEPTANCE-COMMANDS-001` | The acceptance harness MUST expose a single deterministic command per scenario that produces the proof bundle. | 99.8 | scenario | bundle | command output reproducible | `e2e.acceptance_run` span | `acceptance_log.json` | `validator: acceptance_command_validator` (release-gate) | `NC-E2E-COMMAND-DRIFT-001`: change command flags between runs | `command_invocation_drift` | `byte_identical` of bundle | DOC_ONLY |
| `REQ-E2E-MUTATION-FAULTS-001` | The mutation testing scenario MUST inject boundary faults (weak evidence, unsafe output, replay mismatch, trace gap, direct-write attempt) and prove each fault is caught with the matching `Expected Fail Reason`. | 99.9 | mutation set | bundle | each fault produces correct fail_reason_code | `e2e.mutation` parent + per-fault child | `mutation_bundle.json` | `validator: mutation_fault_validator` (release-gate) | `NC-E2E-FAULT-WRONG-REASON-001`: caught with reason `unknown_error` instead of declared reason | `fault_caught_with_wrong_reason` | `byte_identical` per fault | DOC_ONLY |
| `REQ-E2E-FIXTURES-CANONICAL-001` | The fixture families F1..F10 MUST be enumerated, hashed, and replay-bound; each fixture has stable `fixture_id`. | 99.10 | fixtures dir | bundle | fixture_id stable, content_hash stable | NOT_APPLICABLE: fixtures are static input | `fixtures_index.json` | `validator: fixtures_index_validator` (CI) | `NC-E2E-FIXTURE-MUTATION-001`: silent fixture content change | `fixture_content_hash_drift` | `byte_identical` of fixture content_hash | DOC_ONLY |
| `REQ-E2E-COMPILER-RELEASE-DECISION-001` | Release decision MUST be derived through `99.11`'s compiler bundle and the `release_blocking` flag MUST be authoritative; no other surface may override it. | 99.11 | compiler bundle | release decision | `release_decision.json` carries `release_blocking` and `bundle_sha256` | `req_compiler.release_decision` | `release_decision.json` | `validator: release_decision_validator` (release-gate) | `NC-E2E-RELEASE-OVERRIDE-001`: human bypass without REQ_ID | `release_decision_bypass` | `digest_match_only` | DOC_ONLY |

5. RUNTIME EVIDENCE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 99-bundle artifact MUST carry, per child:
- `scenario_id`, `fixture_id`, `request_id`, `run_id`, `trace_root`
- `policy_hash`, `blueprint_hash`, `replay_key`
- per-layer contract IDs and content_hashes (RouteContract, FinalEvidenceContract, PromptEnvelope, sealed_l2_artifact, ExitReviewPacket, X3 disposition receipt, CommitRequest+UWG receipt where applicable)
- `runtime_exhaust_bundle_id`
- `otel_trace_export.sha256`
- `replay_receipt.sha256`
- `no_bypass_bundle.sha256`
- `compiler_bundle.sha256`

6. OTEL SPAN CONTRACT
------------------------------------------------------------------------------------------------------------------------
Required parent span tree per scenario:
```
e2e.scenario [ROOT trace_root]
├── e2e.golden_path  (or e2e.route_coverage / e2e.replay / e2e.no_bypass / e2e.mutation depending on scenario_type)
├── e2e.contract_handoff
├── e2e.groundedness                     [skipped if grounding not required]
├── e2e.acceptance_run
└── e2e.proof_bundle
```

Layer-internal spans (`u0.*`, `l1.*`, `l0.*`, `c0.*`, `pa.*`, `l3.*`, `l2.*`, `exit.*`, `uwg.*`, `l5.*`, `l6.*`, `gate.G01..G29.*`) are owned by their respective layer files but MUST be descendants of `e2e.scenario` for E2E runs.

Required attributes on `e2e.scenario`:
- `scenario_id`, `fixture_id`, `request_id`, `policy_hash`, `blueprint_hash`, `replay_key`, `compiler_bundle_sha256`

Status code rules:
- `OK` for proven scenarios
- `ERROR` with `attributes.fail_reason_code` matching the row's Expected Fail Reason for negative-control scenarios

7. VALIDATOR CONTRACT
------------------------------------------------------------------------------------------------------------------------
Validators owned by 99 parent are listed in §4. Each is a release-gate scope validator emitting a `ValidatorReceipt` per `99.11` §7. Per-scenario validators are owned by 99.1..99.10.

8. NEGATIVE CONTROL CONTRACT
------------------------------------------------------------------------------------------------------------------------
Each `NC-E2E-*` and `NC-TRACE-*` control listed in §4 has:
- `control_id`
- `target_req_id`
- `tamper_kind` (described in row)
- `expected_validator`
- `expected_fail_reason` (matches row)
- a `nc_receipt` artifact recording `result`, `reason_code`, `evidence_refs`

Rule: `result=tripped` AND `reason_code != Expected Fail Reason` → row is `FAKE`.

9. REPLAY CONTRACT
------------------------------------------------------------------------------------------------------------------------
- Every scenario MUST declare its `expected_replay_check` ∈ {`byte_identical`, `semantic_identical`, `digest_match_only`, `not_applicable`}.
- The replay receipt for the scenario records first/second `trace_root`, all 7 digest comparisons (route, evidence, prompt, sealed_artifact, gate_verdict, exit_disposition, compiler_bundle), `match_type`, and `allowed_nondeterminism[]`.
- Allowed nondeterminism is bounded by the child file's declaration; any other diff is release-blocking.

10. RELEASE GATE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 99-scenario row's status is computed by `99.11`. The 99 parent imposes the additional rule:
- A scenario is `PASS` only when every layer span listed in §6 is present, every contract object listed in §5 is hash-linked, the replay match_type matches the declared expectation, and no negative-control row is in the release-blocking set.

11. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**: scenario-level proof contracts (`REQ-E2E-*` parent rows, `REQ-TRACE-*` parent rows), the proof bundle minimum standard, the acceptance rule.

**Related files own**:
- `99.1`..`99.10` own per-scenario details
- `99.11` owns the compiler contract
- Each layer pack owns its layer-internal REQ_IDs

**Forbidden duplicated ownership**: the 99 pack MUST NOT redefine layer-internal REQ_IDs; the layer packs MUST NOT redefine `REQ-E2E-*` rows.

**Forbidden output vocabulary**: `ALLOW_FINISH`, `DENY`, `REROUTE`, `ESCALATE_HITL`, `COMMIT_REQUEST_TO_UWG`, `SAFE_FALLBACK`, `durable_write_committed`, `policy_certified`, `route_changed`, `workflow_expanded`, `evidence_contract_issued`, `prompt_envelope_constructed`, `learning_promoted`.

12. CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- `99.1_E2E_Golden_Path_Runtime_Proof.md` — `REQ-E2E-GOLDEN-PATH-*`
- `99.2_E2E_Route_Path_Coverage_Proof.md` — `REQ-E2E-ROUTE-*`
- `99.3_E2E_Contract_Emission_and_Handoff_Proof.md` — `REQ-E2E-CONTRACT-*`
- `99.4_E2E_OTEL_Trace_and_Span_Tree_Proof.md` — `REQ-TRACE-*`
- `99.5_E2E_Deterministic_Replay_Proof.md` — `REQ-E2E-REPLAY-*`
- `99.6_E2E_No_Bypass_and_Sovereignty_Proof.md` — `REQ-E2E-BYPASS-*`
- `99.7_E2E_Evidence_Prompt_Output_Groundedness_Proof.md` — `REQ-E2E-GROUNDED-*`
- `99.8_E2E_Acceptance_Commands_and_Proof_Bundle.md` — `REQ-E2E-ACCEPTANCE-*`
- `99.9_E2E_Mutation_Testing_Boundary_Faults.md` — `REQ-E2E-MUTATION-*`
- `99.10_E2E_Fixtures_Replay_Harness_Commands.md` — `REQ-E2E-FIXTURE-*`
- `99.11_E2E_Requirements_To_Runtime_Evidence_Compiler.md` — `REQ-COMPILER-*`

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
- Every row in §4 has all 13 cells filled.
- The proof bundle minimum standard in §5 enumerates every required object.
- The OTEL span tree in §6 lists `e2e.scenario` as ROOT and all required child spans.
- Negative-control rows pair with `Expected Fail Reason` cells.
- The release-gate rule is fail-closed (release-blocking unless every applicable row is `PASS` or `NOT_APPLICABLE` with reason).
- The child file map in §12 references all 11 children including `99.11`.
- The no-overlap lock in §11 forbids the duplicated-ownership and vocabulary leak surfaces.

END OF 99 — END-TO-END RUNTIME PROOF AND ACCEPTANCE PARENT
========================================================================================================================
