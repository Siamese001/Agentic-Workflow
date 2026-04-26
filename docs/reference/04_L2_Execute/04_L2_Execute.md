========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 04_L2_Execute
Canonical file: 04_L2_Execute.md
Overwrite mode: parent-thinned doctrine, no-overlap, child-owned implementation
Source refreshed from: 04_L2_Execute.md (parent-thinning refactor 2026-04-26 — E1-E5 worksteps, sealed artifact schema, failure/repair/exit matrix, terminal class details moved to 04.0..04.10 children, zero-loss)
Owner summary: L2 bounded execution. Owns E1 Prep, E2 Valid, E3 Exec, E4 Heal, E5 Seal, PTC sandbox execution, sealed artifacts, and proposed_state_diff only.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

======================================================================================================================================================
[4] L2 EXECUTE — v4
[4] THE BACK ROOMS | DOING THE WORK IN THE STACKS — PARENT DOCTRINE (CHILD-OWNED IMPLEMENTATION)
======================================================================================================================================================
- The active phase where the bounded work is performed, observed, repaired if safe, and sealed.
- L2 may run tools, models, retrieval-backed packets, validators, scripts, or one bounded workflow step.
- L2 does NOT choose the route, expand the workflow, ask humans directly, approve final egress, or commit durable state.
- Library Analogy:
  Assistants enter the restricted stacks with a signed work order. They may do the bounded work, record what happened,
  repair small safe defects, and seal the folder. They cannot change the catalog, invent authority, or sneak ink into L4.

======================================================================================================================================================
                                                    L2 ENTRY SHAPE
======================================================================================================================================================

                  [ SINGLE-STEP ROUTES ]                                             [ MANAGED WORKFLOW ROUTES ]
        [ L0: R3 Simple Grounded Read / R4 Single Action ]                         [ L0 -> L3 Orchestrate ]
                              │                                                                 │
                              │ [ one bounded execution packet ]                                │ [ current bounded step contract ]
                              │                                                                 │
                              ▼                                                                 ▼
                           ┌───────────────────────────────┬─────────────────────────────────────┐
                           ▼                               ▼                                     ▼
                 ┌───────────────────┐           ┌───────────────────┐                 ┌───────────────────┐
                 │ SIMPLE TASK       │           │ COMPLEX TASK      │                 │ RESUMED STEP      │
                 │ single work unit  │           │ first active node │                 │ next ready node   │
                 │ no L3 expansion   │           │ L3 shaped packet  │                 │ checkpoint resume │
                 └─────────┬─────────┘           └─────────┬─────────┘                 └─────────┬─────────┘
                           │                               │                                     │
                           └─────────────────────┬─────────┴───────────────┬─────────────────────┘
                                                 │ [ approved work order / signed packet ]
                                                 ▼

======================================================================================================================================================
                                                    TASK EXECUTION CORE — DOCTRINE
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TASK EXECUTION CORE                                                                                                                                │
│ Strict Rules: No human help | No permanent updates | Same blueprint/policy snapshot end-to-end                                                    │
│                                                                                                                                                    │
│ [!] L2 is the bounded execution room. It executes exactly the current packet, not the user's whole universe.                                       │
│ [!] L2 receives authority. It does not create authority.                                                                                           │
│ [!] L2 may generate a proposed state diff, but that diff is inert until Exit/UWG decisioning.                                                      │
│ [!] L2 does not bypass L4, L5, HITL, Exit Control, C0, Prompt Assembly, or L3.                                                                     │
│ [!] Packet arrives already governed with: compliance_hash / capability_token / sandbox_envelope / policy_hash / blueprint_hash.                    │
│ [!] Input may originate from L0 directly or from L3 as the current executable step.                                                                │
│ [!] VALIDATE and HEAL must operate against the same blueprint_hash / policy_hash / replay snapshot.                                                │
│ [!] Any result leaving L2 must be sealed, replayable, lineage-bound, terminal-classified, and evidence-carrying.                                   │
│                                                                                                                                                    │
│  ┌────────┐   ┌─────────┐   ┌─────────┐   ┌────────┐   ┌────────┐                                                                                  │
│  │E1: Prep│──►│E2: Valid│──►│E3: Exec │──►│E4: Heal│──►│E5: Seal│                                                                                  │
│  └────────┘   └─────────┘   └─▲───────┘   └─┬──────┘   └────────┘                                                                                  │
│                               │             │                                                                                                      │
│                               └──── retry ◄─┘                                                                                                      │
│                                                                                                                                                    │
│ E1 prepares the sealed room.                                                                                                                       │
│ E2 proves the work order can start.                                                                                                                │
│ E3 performs exactly one bounded attempt.                                                                                                           │
│ E4 repairs only safe, local, same-authority failures.                                                                                              │
│ E5 seals payload, traces, counters, replay receipts, and terminal class.                                                                           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

======================================================================================================================================================
CHILD MAP — STAGE OWNERSHIP
======================================================================================================================================================

04.0  Sequencer / orchestrator parent glue (E1->E2->E3->E4->E5)        -> 04.0_L2_Sequencer_Orchestrator_Contract.md
04.1  Execution entry, authority binding, packet intake                -> 04.1_L2_Execution_Entry_Authority_and_Packet_Intake.md
04.2  E1 Prep — frozen execution room                                  -> 04.2_L2_E1_Prep_Frozen_Execution_Room.md
04.3  E2 Valid — work order check + gate check                         -> 04.3_L2_E2_Valid_Work_Order_and_Gate_Check.md
04.4  E3 Exec — attempt lanes + sandbox run                            -> 04.4_L2_E3_Exec_Attempt_Lanes_and_Sandbox_Run.md
04.5  E4 Heal — same-authority repair governor                         -> 04.5_L2_E4_Heal_Same_Authority_Repair_Governor.md
04.6  E5 Seal — sealed artifact + dispatch                             -> 04.6_L2_E5_Seal_Artifact_and_Dispatch.md
04.7  PTC sandbox execution (V2)                                       -> 04.7_L2_Programmatic_Tool_Calling_PTC_Sandbox.md
04.8  Observability / replay / anti-bypass tests                       -> 04.8_L2_Observability_Replay_Anti_Bypass_Tests.md
04.9  StateDiffCandidate and mutation intent (inert until Exit/UWG)    -> 04.9_L2_StateDiffCandidate_and_Mutation_Intent.md
04.10 Verify-then-execute local critique (optional)                    -> 04.10_L2_Verify_Then_Execute_Local_Critique.md

======================================================================================================================================================
ONE-PARAGRAPH STAGE SUMMARIES (parent doctrine level — implementation in children)
======================================================================================================================================================

E1 PREP — FROZEN EXECUTION ROOM
"Convert an approved work packet into a frozen, replayable, idempotent execution room." E1 receives signed_l0_packet or l3_step_contract with route_id, route_contract_id, execution_form, step_id/node_id/workflow_id (if L3-managed), task_spec/tool_spec/model_spec/action_spec, prompt_envelope, capability_token / sandbox_envelope / compliance_hash, blueprint_hash / policy_hash / prompt_hash / input_hash, replay_key / attempt_seed / snapshot_manifest, cost_tier / timeout / retry_ceiling / max_repair_count / SLO slice, and evidence_contract refs when grounded. It performs packet receive, authority bind, environment freeze (tool registry, model/runtime, provider lane, filesystem, network, secrets, locale, budget), determinism bind (hashes, replay key, attempt_seed, run-clock), idempotency guard (stable run_id, duplicate detection, prior-receipt return), lineage root attach, and write lock (no direct L4/UWG path). Emits prep_receipt, frozen_execution_context, run_id/idempotency_key, lineage_root, replay_bindings, write_lock_assertion, ready_for_validation. Fail conditions: missing capability_token, missing sandbox_envelope, policy_hash mismatch, stale blueprint_hash, duplicate in-flight idempotency key, no replay snapshot for replay-required route, hidden write path detected. Full mechanics in 04.2_L2_E1_Prep_Frozen_Execution_Room.md.

E2 VALID — WORK ORDER CHECK
"Prove the packet is executable before any work starts." E2 takes frozen_execution_context plus signed work packet, capability_token / sandbox_envelope, route_contract / step_contract, tool/model/action schema, expected output contract, and policy/replay envelope. It validates signature chain, capability scope, budget scope, schema shape, side-effect class (read-only, sandbox write, external call, proposed mutation, irreversible action, disallowed action), safety sanity (ACL, data boundary, prompt/tool injection, retrieved-content quarantine, sandbox escape indicators), and executability (can run as-is without humans, reroute, or replanning). PASS emits Approved Work Order; FAIL creates sealed_rejection_packet before execution with decisive_rule_id and re-entry suggestion (L1/L0/L3/HITL/clarify). Output: validation_packet_id, validation_status, approved_work_order, sealed_rejection_packet, decisive_rule_id, capability_scope_summary, side_effect_class, budget_snapshot. Full validation decision table and gate mechanics in 04.3_L2_E2_Valid_Work_Order_and_Gate_Check.md.

E3 EXEC — ATTEMPT LANES + SANDBOX RUN
"Perform one bounded attempt inside the frozen room and classify the result." E3 takes approved_work_order, validation_packet_id, frozen_execution_context, prompt/model/tool/action packet, sandbox envelope, retry/repair counters, replay metadata, expected artifact/output contract. It opens an attempt (count++, attempt_seed, traces), builds invocation from sealed packet only (no hidden parameters, no opportunistic tools, no unapproved retrieval, no authority expansion), runs in sandbox with read/write separation, captures telemetry (trace_id, span_id, latency, tokens, cost, compute, memory, stdout/stderr, return code, errors, evidence usage, citation IDs), captures output (final payload, raw tool result, structured model output, generated files, intermediate receipts, proposed_state_diff, artifacts), runs local checks (parseability, schema, deterministic receipt shape, tool return class, file existence, artifact hashes, citation completeness, injection echoes, side-effect surprises), and classifies result: SUCCESS / SOFT_REPAIRABLE / FAIL_TERMINAL / NEEDS_HELP / REJECTED / DEGRADED_SUCCESS. Five execution lanes — READ/ANALYSIS, MODEL, TOOL, ACTION, ARTIFACT — each with their own bounding rules. Output: attempt_receipt_id, attempt_count, result_class, output_payload or quarantined_payload, generated_artifacts, proposed_state_diff, telemetry_bundle, trace/span links, local_check_results, decisive_reason_code. Full mechanics in 04.4_L2_E3_Exec_Attempt_Lanes_and_Sandbox_Run.md.

E4 HEAL — SAME-AUTHORITY REPAIR GOVERNOR
"Repair only local, bounded, same-authority defects without changing route, policy, scope, or durable state." E4 entered when E3 produces SOFT_REPAIRABLE or DEGRADED needing cleanup. It binds failure record (reason_code, parent_packet_id, failed_attempt_id, failed_span_id, error class, local check failure), localizes the failure (schema, parse, timeout, transient dependency, tool return, missing optional field, malformed artifact, format mismatch, citation formatting, output contract defect, deterministic receipt defect, recoverable model/tool error) versus non-repairable causes (missing authority, missing critical user input, blocked ACL, unsafe content, policy conflict, irreversible risk, route mismatch, stale policy, need for human approval), chooses a bounded repair (retry same call, normalize output, repair JSON/schema, reformat, tighten schema, adjust deterministic serialization, retry transient tool, preserve partial artifact, convert partial to failure note), enforces snapshot guard (same blueprint_hash/policy_hash/caps/sandbox/prompt_hash/replay_key/source_snapshot — provider fallback blocked unless contract permits), enforces oscillation guard (repair_count, attempt_count, repeated reason_code, repeated span failure, retry ceiling, cost ceiling, remaining SLO; thrash detection — same error twice, alternating schema defects, repeated timeouts, repeated null output, degraded citation loop), revalidates (E2/E3-compatible checks under original authority and output contract, no hidden instruction or mutation), and seals heal_receipt with before/after hashes. Allowed repairs: JSON repair, schema coercion for known deterministic fields, output reformat, transient-tool retry, checkpoint resume, oversized-output trim preserving required fields, nonfatal-warning-to-caveat conversion, partial-output attachment if contract permits. Disallowed: choosing a different route, retrieving new evidence without C0 contract, asking humans directly, broadening sandbox/credentials, silently switching provider/model/tool, committing state, inventing missing facts, treating human text as authority, overriding policy because output "looks right". Output: heal_receipt_id, repair_status (REPAIRED / NOT_REPAIRED / QUARANTINED / NEEDS_HELP / FAIL_TERMINAL), repair_tactic, before_hash/after_hash, repair_count, attempt_count, oscillation_status, snapshot_guard_status, next_action (RETURN_TO_E3 / SEND_TO_E5). Full mechanics and repair decision table in 04.5_L2_E4_Heal_Same_Authority_Repair_Governor.md.

E5 SEAL — SEALED ARTIFACT + DISPATCH
"Convert success, rejection, failure, partial, or needs-help into a downstream-safe sealed L2 artifact." E5 takes prep_receipt, validation receipt or rejection packet, attempt receipts, heal receipts, final output payload or failure record, telemetry bundle, trace/span links, generated artifacts, proposed_state_diff, replay metadata, and lineage root. It packages payload (include final answer, generated artifact, tool result, model result, proposed action result, rejection, failure, or needs-help record; degraded/partial only if route contract permits; quarantine unsafe payloads), packages evidence (refs, source IDs, citation anchors, C0 contract refs, notes, state diff, stdout/stderr summary, partial outputs, contradiction flags, unsupported gaps, caveats, support-score hints, artifact manifests/hashes), packages traces (trace_id, span_ids, attempt receipts, repair receipts, tool/model invocation records, lineage root, ancestry chain, latency/token/cost/retry/repair/timeout/circuit-breaker counters, route/workflow join keys for L6 correlation), packages replay (replay_key, input_hash, blueprint_hash, policy_hash, prompt_hash, snapshot_manifest, deterministic receipts, idempotency key, environment digest, provider/tool registry digest), stamps terminal class (SUCCESS / DEGRADED_SUCCESS / FAILURE / NEEDS_HELP / REJECTED with decisive reason and downstream-recommendation hint), runs contract check (sealed artifact satisfies post-L2 contract, fields exist for Exit Control / L6 telemetry / HITL packetization / UWG commit-request, no durable commit occurred), enforces commit boundary (no durable write, mutations remain proposed_state_diff only, external actions represented with exact action receipt + authorization lineage, commit requests go to Exit/UWG never L4 directly), and emits dispatch_receipt with sealed_l2_artifact_id for Evaluation Spine, Exit Spine, UWG decisioning, L6 audit, and L3 workflow merge if managed. SealedL2Artifact contains identity (sealed_l2_artifact_id, run_id, route_id/route_contract_id, workflow_id/step_id, parent_plan_id/parent_route_id/parent_step_id), governance (compliance_hash, policy_hash, blueprint_hash, capability_token ref, sandbox_envelope ref, side_effect_class), execution (payload, artifacts, proposed_state_diff, stdout/stderr summary, tool/model/action receipts, attempt_count, repair_count), evidence (source refs, cited spans, C0 contract refs, support gaps, contradiction flags), replay (replay_key, input_hash, prompt_hash, snapshot_manifest, deterministic receipts, environment digest), observability (trace_id, span_ids, latency/token/cost metrics, timeout/circuit-breaker status, route/workflow join keys), and terminal (terminal_class, reason_code, downstream_recommendation, user_visible_safe, commit_requested). Output: sealed_l2_artifact_id, terminal_class, final_payload or failure_payload, evidence_bundle, trace_bundle, replay_bundle, proposed_state_diff if any, downstream_recommendation, commit_requested, dispatch_target (EXIT_CONTROL / L3_MERGE / HITL_PACKETIZATION / UWG_REQUEST_CANDIDATE). Invariant: NO durable commit at E5. Full mechanics, full sealed-artifact schema, and terminal class meanings in 04.6_L2_E5_Seal_Artifact_and_Dispatch.md.

PTC SANDBOX EXECUTION (V2)
Programmatic Tool Calling V2 sandbox controls — when L2 must execute model-driven tool sequences inside the bounded room. Owns sandbox envelope mechanics, ambient-tool denial, deterministic invocation logging, and cross-tool coordination boundaries. PTC is L2-owned, never L1- or L3-owned. Full mechanics in 04.7_L2_Programmatic_Tool_Calling_PTC_Sandbox.md.

OBSERVABILITY / REPLAY / ANTI-BYPASS
The L2-wide failure/repair/exit matrix (malformed JSON output, transient tool timeout, nonzero tool return, missing required input, action outside capability, sandbox escape attempt, policy hash mismatch, weak evidence for grounded ask, proposed durable write, duplicate packet, route mismatch — each mapped to L2 classification, L2 may do, L2 must not do), aggregate OTEL span tree contract (e1.prep, e2.valid, e3.exec, e3.lane.*, e4.heal, e5.seal), deterministic replay invariants, and stage-spanning anti-bypass tests live in 04.8_L2_Observability_Replay_Anti_Bypass_Tests.md.

STATEDIFFCANDIDATE AND MUTATION INTENT
"Any mutation produced by L2 is stored only as proposed_state_diff." This child owns the inert mutation-candidate package shape — fields, validation, hashing, and the assertion that the candidate cannot self-promote into a durable write. Exit/UWG decides commit; L4 is the only durable write surface. Full mechanics in 04.9_L2_StateDiffCandidate_and_Mutation_Intent.md.

VERIFY-THEN-EXECUTE LOCAL CRITIQUE
Optional same-authority local critique pass for high-risk packets — runs after E3 success, before E5 seal, to surface obvious self-inconsistency, citation drift, or schema regression. Critique runs under the same authority, the same sandbox, and the same blueprint/policy snapshot. Cannot reroute, escalate, or expand scope. Full mechanics in 04.10_L2_Verify_Then_Execute_Local_Critique.md.

======================================================================================================================================================
L2 FAILURE / REPAIR / EXIT MATRIX (pointer — full table in 04.8)
======================================================================================================================================================

The L2-wide failure/repair/exit matrix mapping observed conditions (malformed JSON output, transient tool timeout, nonzero tool return, missing required input, action outside capability, sandbox escape attempt, policy hash mismatch, weak evidence for grounded ask, proposed durable write, duplicate packet, route mismatch) to L2 classification, allowed L2 actions, and forbidden L2 actions lives in 04.8_L2_Observability_Replay_Anti_Bypass_Tests.md.

======================================================================================================================================================
                                                    L2 INVARIANTS
======================================================================================================================================================

[1] L2 executes exactly one bounded packet or current L3 step.
[2] L2 does not decide the route.
[3] L2 does not expand a workflow.
[4] L2 does not retrieve new evidence unless the packet explicitly grants a bounded read/tool action.
[5] L2 does not call humans directly.
[6] L2 does not create new authority.
[7] L2 does not persist durable state.
[8] L2 does not write to L4.
[9] L2 does not bypass UWG.
[10] L2 does not silently switch tools, models, providers, credentials, or sandboxes.
[11] L2 can repair only local, bounded, same-authority defects.
[12] L2 must preserve replay metadata, trace lineage, evidence lineage, and terminal classification.
[13] L2 must seal every outcome, including rejection and failure.
[14] L2 emits artifacts for Exit, L3 merge, L6 audit, HITL review, or UWG decisioning only.
[15] The current run is never rescued by future learning. L6 may learn later, but L2 must finish honestly now.

======================================================================================================================================================
                                                    COMPACT MENTAL MODEL
======================================================================================================================================================

L0 or L3 hands L2 a locked work order.
        │
        ▼
E1 creates the locked room.
        │
        ▼
E2 checks the permit.
        │
        ▼
E3 does the work.
        │
        ▼
E4 fixes only safe local mistakes.
        │
        ▼
E5 seals the folder.
        │
        ▼
Exit Control decides whether it can leave, reroute, escalate, deny, or request UWG commit.

======================================================================================================================================================
END OF [4] L2 EXECUTE — v4
======================================================================================================================================================
======================================================================================================================================================
GAP-CLOSED PARENT UPDATE | APRIL 2026 MECE REVIEW
======================================================================================================================================================
This parent now explicitly recognizes the full L2 closure set:
- 04.0_L2_Sequencer_Orchestrator_Contract.md owns E1->E2->E3->E4->E5 parent glue.
- 04.6_L2_E5_Seal_Artifact_and_Dispatch.md owns SealedL2Artifact and dispatch receipt.
- 04.7_L2_Programmatic_Tool_Calling_PTC_Sandbox.md owns PTC V2 sandbox execution controls.
- 04.9_L2_StateDiffCandidate_and_Mutation_Intent.md owns inert mutation candidate packaging only.
- 04.10_L2_Verify_Then_Execute_Local_Critique.md owns optional same-authority local critique.
L2 still does not route, retrieve, assemble prompts, approve final egress, write L4, or learn for future runs.
