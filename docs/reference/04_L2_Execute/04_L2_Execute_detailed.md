======================================================================================================================================================
[4] L2 EXECUTE — v4
[4] THE BACK ROOMS | DOING THE WORK IN THE STACKS
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
                                                    TASK EXECUTION CORE
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TASK EXECUTION CORE                                                                                                                                │
│ Strict Rules: No human help | No permanent updates | Same blueprint/policy snapshot end-to-end                                                    │
│                                                                                                                                                    │
│ [!] L2 is the bounded execution room. It executes exactly the current packet, not the user's whole universe.                                       │
│ [!] L2 receives authority. It does not create authority.                                                                                           │
│ [!] L2 may generate a proposed state diff, but that diff is inert until Exit/UWG decisioning.                                                      │
│ [!] L2 does not bypass L4, L5, HITL, Exit Control, C0, Prompt Assembly, or L3.                                                                      │
│ [!] Packet arrives already governed with: compliance_hash / capability_token / sandbox_envelope / policy_hash / blueprint_hash.                   │
│ [!] Input may originate from L0 directly or from L3 as the current executable step.                                                                │
│ [!] VALIDATE and HEAL must operate against the same blueprint_hash / policy_hash / replay snapshot.                                                │
│ [!] Any result leaving L2 must be sealed, replayable, lineage-bound, terminal-classified, and evidence-carrying.                                   │
│                                                                                                                                                    │
│  ┌────────┐   ┌─────────┐   ┌─────────┐   ┌────────┐   ┌────────┐                                                                                 │
│  │E1: Prep│──►│E2: Valid│──►│E3: Exec │──►│E4: Heal│──►│E5: Seal│                                                                                 │
│  └────────┘   └─────────┘   └─▲───────┘   └─┬──────┘   └────────┘                                                                                 │
│                               │             │                                                                                                     │
│                               └──── retry ◄─┘                                                                                                     │
│                                                                                                                                                    │
│ E1 prepares the sealed room.                                                                                                                       │
│ E2 proves the work order can start.                                                                                                                │
│ E3 performs exactly one bounded attempt.                                                                                                           │
│ E4 repairs only safe, local, same-authority failures.                                                                                              │
│ E5 seals payload, traces, counters, replay receipts, and terminal class.                                                                           │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼

======================================================================================================================================================
                                                    E1: PREP
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E1: PREP | PREPARATION DESK                                                                                                                       │
│ Purpose: Convert an approved work packet into a frozen, replayable, idempotent execution room.                                                     │
│ Library Persona: Intake Counter + Key Cabinet + Locked Study Room Clerk                                                                            │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ QUICK FLOW                                                                                                                                         │
│ [ Intake Counter ] ──► [ Freeze Env/Caps/Budget ] ──► [ Bind Idempotency Key ] ──► [ Bind Blueprint Hashes ] ──► [ Lineage Root ]                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ INPUTS                                                                                                                                             │
│ - signed_l0_packet OR l3_step_contract                                                                                                             │
│ - route_id / route_contract_id / execution_form                                                                                                    │
│ - step_id / node_id / workflow_id if L3-managed                                                                                                    │
│ - task_spec / tool_spec / model_spec / action_spec                                                                                                 │
│ - prompt_envelope or compiled prompt artifact if model execution is required                                                                        │
│ - capability_token / sandbox_envelope / compliance_hash                                                                                            │
│ - blueprint_hash / policy_hash / prompt_hash / input_hash                                                                                          │
│ - replay_key / attempt_seed / snapshot_manifest                                                                                                    │
│ - cost_tier / timeout / retry_ceiling / max_repair_count / SLO slice                                                                                │
│ - evidence_contract references when grounded execution is required                                                                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ L3 DETAIL / WORKSTEPS                                                                                                                              │
│ E1.1 Packet receive                                                                                                                                │
│ - Accept the signed L0 packet or L3 step contract exactly as handed off.                                                                            │
│ - Refuse packets that are partial, unsigned, stale, mutated in transit, or missing governing metadata.                                             │
│ - Preserve original user/task payload separately from normalized execution fields.                                                                  │
│                                                                                                                                                    │
│ E1.2 Authority bind                                                                                                                                │
│ - Confirm route_id, step_id, capability_token, compliance_hash, sandbox_envelope, and issuer identity are present.                                 │
│ - Bind current L2 authority to the received packet only.                                                                                            │
│ - Reject any implicit authority inferred from task wording, tool name, human note, or model output.                                                │
│                                                                                                                                                    │
│ E1.3 Environment freeze                                                                                                                           │
│ - Lock tool registry version, model/runtime version, provider lane, filesystem view, network rules, secrets scope, locale, and budget.            │
│ - Freeze environment variables relevant to execution.                                                                                              │
│ - Bind allowed file roots, allowed network destinations, allowed syscalls, and allowed memory surfaces.                                            │
│ - Block late tool discovery unless explicitly included in the packet.                                                                               │
│                                                                                                                                                    │
│ E1.4 Determinism bind                                                                                                                             │
│ - Bind blueprint_hash, policy_hash, prompt_hash, input_hash, replay_key, attempt_seed, snapshot_manifest, and clock policy.                       │
│ - Convert wall-clock needs to run-clock offsets when deterministic replay is required.                                                              │
│ - Bind stable IDs for artifacts, temp files, subprocess names, and attempt receipts.                                                               │
│                                                                                                                                                    │
│ E1.5 Idempotency guard                                                                                                                            │
│ - Derive stable run_id / idempotency_key so duplicate packets do not execute twice.                                                                │
│ - Detect duplicate packet family, duplicate tool call, duplicate model request, and replay resume collision.                                      │
│ - If duplicate is already sealed, return prior sealed receipt instead of rerunning.                                                                 │
│                                                                                                                                                    │
│ E1.6 Lineage root                                                                                                                                  │
│ - Attach parent_route_id, parent_plan_id, parent_step_id, workflow_id, node_id, ancestry chain, and same-run packet family.                       │
│ - Preserve C0 evidence lineage, Prompt Assembly manifest lineage, and L3 graph lineage where present.                                             │
│ - Create L2 lineage root so all attempts, repairs, errors, and artifacts tie back to the same folder.                                             │
│                                                                                                                                                    │
│ E1.7 Write lock                                                                                                                                   │
│ - Verify L2 has no direct L4/UWG commit path.                                                                                                      │
│ - Any mutation produced by L2 is stored only as proposed_state_diff.                                                                                │
│ - Disable direct persistence, live memory update, cache promotion, unapproved credential write, or external irreversible side effect.             │
│                                                                                                                                                    │
│ E1.8 Start receipt                                                                                                                                │
│ - Emit prep_receipt with frozen inputs, caps, budgets, lineage, hashes, environment digest, and replay metadata.                                  │
│ - Include refusal reason if prep cannot safely create an execution room.                                                                            │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ E1 OUTPUT CONTRACT                                                                                                                                 │
│ - prep_receipt_id                                                                                                                                  │
│ - frozen_execution_context                                                                                                                         │
│ - run_id / idempotency_key                                                                                                                         │
│ - lineage_root                                                                                                                                     │
│ - replay_bindings                                                                                                                                  │
│ - write_lock_assertion                                                                                                                             │
│ - ready_for_validation = true | false                                                                                                              │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ FAIL CONDITIONS                                                                                                                                    │
│ - missing capability_token                                                                                                                         │
│ - missing sandbox_envelope                                                                                                                         │
│ - policy_hash mismatch                                                                                                                             │
│ - stale blueprint_hash                                                                                                                             │
│ - duplicate in-flight idempotency key                                                                                                              │
│ - no replay snapshot for replay-required route                                                                                                     │
│ - L2 detects hidden write path                                                                                                                     │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────┘
                                                                       │
                                                                       ▼

======================================================================================================================================================
                                                    E2: VALID
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E2: VALID | WORK ORDER CHECK                                                                                                                       │
│ Purpose: Prove the packet is executable before any work starts.                                                                                    │
│ Library Persona: Packet Inspection Desk + Permit Checker + Side-Effect Inspector                                                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ QUICK FLOW                                                                                                                                         │
│ [ Packet Inspection Desk ] ──► [ Capability Check ] ──► [ Schema Check ] ──► [ Side-Effect Check ] ──► [ Start / Reject Stamp ]                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ INPUTS                                                                                                                                             │
│ - frozen_execution_context from E1                                                                                                                 │
│ - signed work packet                                                                                                                               │
│ - capability_token / sandbox_envelope                                                                                                              │
│ - route_contract / step_contract                                                                                                                   │
│ - tool/model/action schema                                                                                                                         │
│ - expected output contract                                                                                                                         │
│ - policy snapshot / replay envelope                                                                                                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ L3 DETAIL / WORKSTEPS                                                                                                                              │
│ E2.1 Signature chain                                                                                                                               │
│ - Verify packet integrity, issuer, handoff boundary, route contract, prompt envelope, and policy snapshot.                                        │
│ - Confirm no user content, retrieved content, tool output, or human note has overwritten authority fields.                                        │
│ - Validate HMAC/signature over manifest and critical execution fields.                                                                              │
│                                                                                                                                                    │
│ E2.2 Capability scope                                                                                                                              │
│ - Confirm requested tool/action/model is inside granted capability_token.                                                                           │
│ - Confirm capability is not broader than route purpose, side-effect class, tenant scope, or sandbox.                                              │
│ - Check provider/model lane against allowed registry.                                                                                              │
│ - Deny silent fallback to a different provider, model, tool, credential, or network path.                                                         │
│                                                                                                                                                    │
│ E2.3 Budget scope                                                                                                                                  │
│ - Validate timeout, retry ceiling, repair ceiling, token limit, compute limit, memory limit, IO quota, and circuit-breaker rules.                 │
│ - Confirm remaining route SLO can afford the attempt.                                                                                              │
│ - Reject packets that require open-ended autonomy or unbounded iteration.                                                                           │
│                                                                                                                                                    │
│ E2.4 Schema shape                                                                                                                                  │
│ - Check required fields, input schema, output schema, artifact contract, tool args, and allowed terminal classes.                                 │
│ - Validate enum values, path formats, IDs, dates, resource handles, and structured output expectations.                                           │
│ - Confirm model prompt packet, tool call packet, or script invocation can be serialized deterministically.                                        │
│                                                                                                                                                    │
│ E2.5 Side-effect class                                                                                                                             │
│ - Classify operation as read-only, sandbox write, external call, proposed mutation, irreversible action, or disallowed action.                    │
│ - Block anything outside sandbox envelope.                                                                                                         │
│ - Confirm proposed mutations remain inert until Exit/UWG.                                                                                          │
│ - Escalation-required actions cannot be executed here unless packet already includes the required clearance.                                      │
│                                                                                                                                                    │
│ E2.6 Safety sanity                                                                                                                                 │
│ - Check ACL, data boundary, policy tags, prompt/tool injection flags, retrieved-content quarantine flags, and sandbox escape indicators.          │
│ - Confirm content marked as data cannot become executable instruction.                                                                              │
│ - Confirm secrets are not exposed to unapproved tools, models, logs, or external egress.                                                           │
│                                                                                                                                                    │
│ E2.7 Executability check                                                                                                                           │
│ - Confirm the step can run as-is without asking humans, rerouting, replanning, broadening scope, or fetching new authority.                       │
│ - Confirm missing inputs are either optional, defaulted by contract, or terminal-fail/needs-help conditions.                                      │
│ - Confirm grounded routes have an evidence contract, citation anchors, and support target if required.                                            │
│                                                                                                                                                    │
│ E2.8 Validation receipt                                                                                                                            │
│ - PASS stamps Approved to Start and emits validation_packet_id.                                                                                     │
│ - FAIL creates sealed_rejection_packet before execution.                                                                                            │
│ - Rejection includes decisive rule, missing field, risk class, and whether L1/L0/L3 needs re-entry.                                               │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ VALIDATION DECISION TABLE                                                                                                                          │
│                                                                                                                                                    │
│ PASS                                                                                                                                                │
│ - packet is signed                                                                                                                                  │
│ - authority is scoped                                                                                                                               │
│ - schema is valid                                                                                                                                   │
│ - side effects fit envelope                                                                                                                        │
│ - budget is sufficient                                                                                                                             │
│ - replay metadata is bound                                                                                                                         │
│ - no direct write path exists                                                                                                                      │
│                                                                                                                                                    │
│ FAIL BEFORE EXECUTION                                                                                                                               │
│ - invalid signature                                                                                                                                 │
│ - action outside capability                                                                                                │
│ - missing sandbox envelope                                                                                                                         │
│ - malformed tool args                                                                                                                              │
│ - high-risk mutation lacks clearance                                                                                                                │
│ - prompt/evidence injection breach                                                                                                                  │
│ - unsupported output contract                                                                                                                       │
│ - no deterministic replay surface when required                                                                                                     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ E2 OUTPUT CONTRACT                                                                                                                                 │
│ - validation_packet_id                                                                                                                              │
│ - validation_status = PASS | FAIL                                                                                                                   │
│ - approved_work_order if PASS                                                                                                                       │
│ - sealed_rejection_packet if FAIL                                                                                                                   │
│ - decisive_rule_id                                                                                                                                  │
│ - capability_scope_summary                                                                                                                          │
│ - side_effect_class                                                                                                                                 │
│ - budget_snapshot                                                                                                                                   │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────┘
                                                                       │ [ Approved Work Order ]
                                           ┌───────────────────────────┴───────────────────────────┐
                                           │                                                       │
                                         pass                                                    fail
                                           │                                                       │
                                           ▼                                                       ▼

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐   ┌──────────────────────────────────────┐
│ continue to E3                                                                                                               │   │ REJECTED REQUEST FOLDER              │
│                                                                                                                              │   │ - rejection_packet_id                │
│                                                                                                                              │   │ - failed validation rule             │
│                                                                                                                              │   │ - side_effect_class                  │
│                                                                                                                              │   │ - missing/invalid authority field    │
│                                                                                                                              │   │ - no actual work was performed       │
│                                                                                                                              │   │ - sealed before execution            │
│                                                                                                                              │   │ - suggested re-entry target if any   │
│                                                                                                                              │   │   L1 / L0 / L3 / HITL / user clarify │
│                                                                                                                              │   └──────────────────┬───────────────────┘
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘                      │
                                                                                                                                                    ▼
                                                                                                                                        [ send to E5 Seal ]

======================================================================================================================================================
                                                    E3: EXEC
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E3: EXEC | DOING THE WORK                                                                                                                           │
│ Purpose: Perform one bounded attempt inside the frozen room and classify the result.                                                                 │
│ Library Persona: Study Carrel + Tool Runner + Model Operator + Receipts Clerk                                                                       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ QUICK FLOW                                                                                                                                         │
│ [ Attempt Count++ ] ──► [ Invoke Tool / Model ] ──► [ Timeout / Circuit Breaker Watch ] ──► [ Capture Output ] ──► [ Classify ]                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ INPUTS                                                                                                                                             │
│ - approved_work_order from E2                                                                                                                       │
│ - validation_packet_id                                                                                                                              │
│ - frozen_execution_context                                                                                                                          │
│ - prompt/model/tool/action packet                                                                                                                   │
│ - sandbox envelope                                                                                                                                  │
│ - retry/repair counters                                                                                                                             │
│ - replay metadata                                                                                                                                   │
│ - expected artifact/output contract                                                                                                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ L3 DETAIL / WORKSTEPS                                                                                                                              │
│ E3.1 Attempt open                                                                                                                                   │
│ - Increment attempt_count.                                                                                                                          │
│ - Attach validation_packet_id, repair_attempt_id if applicable, and lineage_root.                                                                   │
│ - Start trace/span for attempt, tool call, model call, subprocess, file IO, network egress, and artifact generation.                               │
│ - Bind attempt to stable attempt_seed and run-clock offset.                                                                                         │
│                                                                                                                                                    │
│ E3.2 Invocation build                                                                                                                              │
│ - Assemble exact tool/model/script/action call from sealed packet only.                                                                              │
│ - No hidden parameters. No opportunistic extra tools. No unapproved retrieval. No authority expansion.                                             │
│ - For model calls: bind prompt artifact, response schema, tool schema, model lane, max tokens, and safety posture.                                │
│ - For tool calls: bind args, working directory, env allowlist, IO policy, and output capture mode.                                                  │
│ - For code/script calls: bind interpreter, command, cwd, input files, output files, temp dir, and deterministic seed.                              │
│                                                                                                                                                    │
│ E3.3 Sandbox run                                                                                                                                   │
│ - Execute inside frozen filesystem, network, syscall, memory, credential, timeout, and circuit-breaker envelope.                                  │
│ - Enforce read/write separation: sandbox writes are temporary artifacts, not durable L4 writes.                                                     │
│ - Enforce no live credential discovery or ambient network escape.                                                                                   │
│ - Enforce provider lane mapping and no silent fallback.                                                                                             │
│                                                                                                                                                    │
│ E3.4 Telemetry capture                                                                                                                             │
│ - Record trace_id, span_id, parent_span_id, latency, tokens, cost, compute use, memory use, stdout, stderr, return code, errors.                  │
│ - Record input/output byte counts, file touches, network destinations, model/tool name, provider lane, retry source, and circuit breaker state.    │
│ - Record evidence usage and citation IDs for grounded generation.                                                                                   │
│ - Record deterministic offsets rather than uncontrolled wall-clock dependencies where replay requires it.                                          │
│                                                                                                                                                    │
│ E3.5 Output capture                                                                                                                                │
│ - Collect final payload, raw tool result, structured model output, generated files, intermediate receipts, proposed state diff, and artifacts.      │
│ - Preserve partial output on timeout when policy allows best-effort sealed artifact.                                                                │
│ - Preserve unsafe/blocked output only as quarantined evidence, not as user-facing content.                                                          │
│                                                                                                                                                    │
│ E3.6 Local checks                                                                                                                                  │
│ - Verify parseability, declared schema, deterministic receipt shape, output contract, tool return class, file existence, and artifact hashes.      │
│ - Check model output for refusal requirements, unsupported claims, missing citations, schema drift, and injection echoes.                         │
│ - Check tool output for malformed response, unexpected side effects, missing fields, and nonzero exit status.                                     │
│                                                                                                                                                    │
│ E3.7 Result classify                                                                                                                               │
│ - SUCCESS: output satisfies local contract and can be sealed for downstream evaluation.                                                             │
│ - SOFT_REPAIRABLE: failure is local, bounded, same-authority, and likely fixable.                                                                   │
│ - FAIL_TERMINAL: cannot complete under current packet.                                                                                              │
│ - NEEDS_HELP: requires human, new authority, missing input, or route-level decision.                                                                │
│ - REJECTED: execution discovered a violation requiring stop.                                                                                        │
│ - DEGRADED_SUCCESS: usable partial result with caveats, if allowed by route contract.                                                              │
│                                                                                                                                                    │
│ E3.8 Attempt receipt                                                                                                                               │
│ - Seal attempt_receipt with inputs, outputs, counters, trace links, environment digest, result class, and decisive reason.                        │
│ - Include best_partial_artifact where available and allowed.                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ EXECUTION LANES                                                                                                                                    │
│                                                                                                                                                    │
│ READ / ANALYSIS LANE                                                                                                                               │
│ - uses provided evidence or bounded read surfaces                                                                                                  │
│ - produces answer, summary, comparison, extraction, or classification                                                                               │
│ - no durable mutation                                                                                                                              │
│                                                                                                                                                    │
│ MODEL LANE                                                                                                                                         │
│ - sends signed prompt artifact through provider/model gateway                                                                                       │
│ - schema-bound output if structured answer is required                                                                                              │
│ - output must be locally parsed before seal                                                                                                        │
│                                                                                                                                                    │
│ TOOL LANE                                                                                                                                          │
│ - invokes approved tool with validated args                                                                                                        │
│ - captures stdout/stderr/return object                                                                                                             │
│ - blocks unexpected side effects                                                                                                                   │
│                                                                                                                                                    │
│ ACTION LANE                                                                                                                                        │
│ - performs approved reversible or scoped action                                                                                                     │
│ - irreversible/high-impact action must already have required clearance                                                                              │
│ - any state mutation becomes proposed_state_diff unless the external tool action itself is the approved bounded action                             │
│                                                                                                                                                    │
│ ARTIFACT LANE                                                                                                                                      │
│ - generates file, report, chart, patch, draft, code, or structured bundle                                                                           │
│ - attaches artifact_hash, path, manifest, and provenance                                                                                            │
│ - no untracked artifact leaves L2                                                                                                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ E3 OUTPUT CONTRACT                                                                                                                                 │
│ - attempt_receipt_id                                                                                                                               │
│ - attempt_count                                                                                                                                    │
│ - result_class = SUCCESS | DEGRADED_SUCCESS | SOFT_REPAIRABLE | FAIL_TERMINAL | NEEDS_HELP | REJECTED                                            │
│ - output_payload or quarantined_payload                                                                                                            │
│ - generated_artifacts                                                                                                                              │
│ - proposed_state_diff                                                                                                                              │
│ - telemetry_bundle                                                                                                                                 │
│ - trace/span links                                                                                                                                 │
│ - local_check_results                                                                                                                              │
│ - decisive_reason_code                                                                                                                             │
└──────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────┘
                                                       │
                              ┌────────────────────────┼──────────────────────────┬──────────────────────────┐
                              │                        │                          │                          │
                              ▼                        ▼                          ▼                          ▼
                         [ SUCCESS ]             [ FIXABLE ]              [ COMPLETE FAILURE ]          [ NEEDS HELP ]
                              │                        │                          │                          │
                              │                        ▼                          │                          │
                              │                [ go to E4 Heal ]                  │                          │
                              │                                                   │                          │
                              └─────────────────────────────┬─────────────────────┴──────────────────────────┘
                                                            │
                                                            ▼

======================================================================================================================================================
                                                    E4: HEAL
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E4: HEAL | FIXING DESK                                                                                                                             │
│ Purpose: Repair only local, bounded, same-authority defects without changing route, policy, scope, or durable state.                               │
│ Library Persona: Repair Bench + Error Localizer + Retry Governor                                                                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ QUICK FLOW                                                                                                                                         │
│ [ Failure Record ] ──► [ Localize ] ──► [ Bound Repair ] ──► [ Snapshot Guard ] ──► [ Oscillation Guard ] ──► [ Revalidate ] ──► [ Retry / Give Up ]│
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ INPUTS                                                                                                                                             │
│ - failed attempt_receipt from E3                                                                                                                    │
│ - result_class = SOFT_REPAIRABLE or DEGRADED needing cleanup                                                                                        │
│ - original packet family                                                                                                                           │
│ - same blueprint_hash / policy_hash / capability_token / sandbox_envelope                                                                           │
│ - retry/repair counters                                                                                                                            │
│ - allowed repair taxonomy                                                                                                                          │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ L3 DETAIL / WORKSTEPS                                                                                                                              │
│ E4.1 Failure record                                                                                                                                │
│ - Bind reason_code, parent_packet_id, failed_attempt_id, failed_span_id, error class, and local check failure.                                     │
│ - Separate observed symptom from suspected root cause.                                                                                              │
│ - Preserve original failed output for audit, but quarantine if unsafe.                                                                              │
│                                                                                                                                                    │
│ E4.2 Localize                                                                                                                                      │
│ - Isolate failure as one of: schema, parse, timeout, transient dependency, tool return, missing optional field, malformed artifact,                │
│   format mismatch, citation formatting, output contract defect, deterministic receipt defect, or recoverable model/tool error.                    │
│ - Identify non-repairable causes: missing authority, missing critical user input, blocked ACL, unsafe content, policy conflict,                    │
│   irreversible risk, route mismatch, stale policy, or need for human approval.                                                                      │
│                                                                                                                                                    │
│ E4.3 Repair plan                                                                                                                                   │
│ - Choose bounded fix only: retry same call, normalize output, repair JSON/schema, reformat, tighten schema, adjust deterministic                   │
│   serialization, retry transient tool, preserve partial artifact, or convert partial artifact to failure note.                                    │
│ - No new route. No new plan. No new tool. No new source. No new policy. No broader sandbox.                                                        │
│ - If repair would require scope expansion, mark NEEDS_HELP or FAIL_TERMINAL.                                                                        │
│                                                                                                                                                    │
│ E4.4 Snapshot guard                                                                                                                                │
│ - Verify same blueprint_hash, policy_hash, caps, sandbox envelope, prompt hash, replay key, and source snapshot.                                  │
│ - Block repair if any governing surface changed mid-run.                                                                                           │
│ - Block repair if provider fallback would change model identity without explicit contract permission.                                             │
│                                                                                                                                                    │
│ E4.5 Oscillation guard                                                                                                                             │
│ - Check repair_count, attempt_count, repeated reason_code, repeated span failure, retry ceiling, cost ceiling, and remaining SLO.                 │
│ - Detect thrash patterns: same error twice, alternating schema defects, repeated timeouts, repeated null output, degraded citation loop.           │
│ - Stop early if another retry is unlikely to improve result.                                                                                       │
│                                                                                                                                                    │
│ E4.6 Revalidation                                                                                                                                  │
│ - Run repaired packet through E2/E3-compatible checks.                                                                                              │
│ - Confirm repair remains inside original authority and output contract.                                                                             │
│ - Confirm no hidden instruction, unsafe echo, or mutation snuck into the repaired payload.                                                         │
│                                                                                                                                                    │
│ E4.7 Heal receipt                                                                                                                                  │
│ - Seal repair_attempt_id, failure class, repair tactic, delta, counters, skipped alternatives, and outcome.                                      │
│ - Attach before/after payload hashes.                                                                                                              │
│ - Attach reason if repair is denied.                                                                                                               │
│                                                                                                                                                    │
│ E4.8 Outcome                                                                                                                                       │
│ - PASS -> back to E3 under same packet family.                                                                                                     │
│ - FAIL -> NEEDS_HELP / ESCALATE_ARTIFACT / FAIL_TERMINAL.                                                                                          │
│ - QUARANTINE -> unsafe artifact sealed for downstream review only.                                                                                 │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ALLOWED REPAIR TAXONOMY                                                                                                                            │
│                                                                                                                                                    │
│ SAFE LOCAL REPAIRS                                                                                                                                 │
│ - JSON repair where source content is intact                                                                                                       │
│ - schema coercion for known deterministic fields                                                                                                   │
│ - output reformat to required shape                                                                                                                │
│ - retry same transient tool call within ceiling                                                                                                    │
│ - resume from existing checkpoint                                                                                                                  │
│ - trim oversized output while preserving required fields                                                                                           │
│ - convert nonfatal artifact warning into caveat                                                                                                    │
│ - attach partial output if contract permits                                                                                                        │
│                                                                                                                                                    │
│ DISALLOWED REPAIRS                                                                                                                                 │
│ - choosing a different route                                                                                                                       │
│ - retrieving new evidence without C0 contract                                                                                                      │
│ - asking a human directly                                                                                                                          │
│ - broadening sandbox or credentials                                                                                                                │
│ - silently switching provider/model/tool                                                                                                           │
│ - committing state                                                                                                                                 │
│ - inventing missing facts                                                                                                                          │
│ - treating human text as authority                                                                                                                 │
│ - overriding policy because output “looks right”                                                                                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REPAIR DECISION TABLE                                                                                                                              │
│                                                                                                                                                    │
│ repairable? yes + within same authority + under ceilings + deterministic snapshot intact                                                            │
│     -> repaired packet returns to E3                                                                                                                │
│                                                                                                                                                    │
│ repairable? no, but useful partial exists                                                                                                          │
│     -> seal DEGRADED_SUCCESS or NEEDS_HELP with partial artifact, depending on contract                                                             │
│                                                                                                                                                    │
│ repair would need new authority / new source / human decision / broader side effect                                                                  │
│     -> stop and seal NEEDS_HELP or ESCALATE_ARTIFACT                                                                                                │
│                                                                                                                                                    │
│ repair reveals safety / policy / sandbox breach                                                                                                    │
│     -> stop and seal REJECTED / FAIL_TERMINAL with quarantine                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ E4 OUTPUT CONTRACT                                                                                                                                 │
│ - heal_receipt_id                                                                                                                                  │
│ - repair_status = REPAIRED | NOT_REPAIRED | QUARANTINED | NEEDS_HELP | FAIL_TERMINAL                                                               │
│ - repair_tactic                                                                                                                                    │
│ - before_hash / after_hash                                                                                                                         │
│ - repair_count                                                                                                                                     │
│ - attempt_count                                                                                                                                    │
│ - oscillation_status                                                                                                                               │
│ - snapshot_guard_status                                                                                                                            │
│ - next_action = RETURN_TO_E3 | SEND_TO_E5                                                                                                          │
└───────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                 repaired              not repaired
                    │                       │
                    ▼                       ▼
             [ back to E3 ]         [ GIVE UP / NEED HELP ]
                                            │
                                            ▼

======================================================================================================================================================
                                                    E5: SEAL
======================================================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E5: SEAL | SEAL THE FINAL FOLDER                                                                                                                   │
│ Purpose: Convert success, rejection, failure, partial, or needs-help into a downstream-safe sealed L2 artifact.                                    │
│ Library Persona: Records Folder Sealing + Evidence Binder + Dispatch Clerk                                                                         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ QUICK FLOW                                                                                                                                         │
│ [ Package Payload ] ──► [ Attach Traces / Lineage ] ──► [ Attach Replay Receipts & Counters ] ──► [ Seal L2 Artifact ]                           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ INPUTS                                                                                                                                             │
│ - prep_receipt                                                                                                                                     │
│ - validation receipt or rejection packet                                                                                                           │
│ - attempt receipts                                                                                                                                 │
│ - heal receipts                                                                                                                                    │
│ - final output payload or failure record                                                                                                           │
│ - telemetry bundle                                                                                                                                 │
│ - trace/span links                                                                                                                                 │
│ - generated artifacts                                                                                                                              │
│ - proposed_state_diff                                                                                                                              │
│ - replay metadata                                                                                                                                  │
│ - lineage root                                                                                                                                     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ L3 DETAIL / WORKSTEPS                                                                                                                              │
│ E5.1 Payload package                                                                                                                               │
│ - Include final answer, generated artifact, tool result, model result, proposed action result, rejection, failure, or needs-help record.          │
│ - Include degraded/partial output only if route contract permits it.                                                                                │
│ - Quarantine unsafe payloads and prevent direct user exposure.                                                                                     │
│                                                                                                                                                    │
│ E5.2 Evidence package                                                                                                                              │
│ - Attach evidence refs, source IDs, citation anchors, C0 contract refs, notes, state diff, stdout/stderr summary, and partial outputs.            │
│ - Preserve contradiction flags, unsupported gaps, caveats, and support-score hints where available.                                                │
│ - Preserve artifact manifests and hashes.                                                                                                         │
│                                                                                                                                                    │
│ E5.3 Trace package                                                                                                                                 │
│ - Attach trace_id, span_ids, attempt receipts, repair receipts, tool/model invocation records, lineage root, and ancestry chain.                  │
│ - Attach latency, token, cost, retry, repair, timeout, and circuit-breaker counters.                                                               │
│ - Attach route/workflow join keys for L6 correlation.                                                                                              │
│                                                                                                                                                    │
│ E5.4 Replay package                                                                                                                                │
│ - Attach replay_key, input_hash, blueprint_hash, policy_hash, prompt_hash, snapshot_manifest, deterministic receipts, and counters.               │
│ - Include idempotency key and duplicate-detection status.                                                                                          │
│ - Include environment digest and provider/tool registry digest.                                                                                    │
│                                                                                                                                                    │
│ E5.5 Terminal stamp                                                                                                                                │
│ - Classify SUCCESS / DEGRADED_SUCCESS / FAILURE / NEEDS_HELP / REJECTED.                                                                           │
│ - Include decisive reason code and short explanation.                                                                                              │
│ - Mark whether downstream Exit may allow, deny, reroute, escalate, or consider commit request.                                                     │
│                                                                                                                                                    │
│ E5.6 Contract check                                                                                                                                │
│ - Verify sealed artifact satisfies the downstream post-L2 evaluation/disposition contract.                                                        │
│ - Confirm required fields exist for Exit Control, L6 telemetry, HITL packetization, and UWG commit request if applicable.                         │
│ - Confirm no durable commit occurred inside L2.                                                                                                    │
│                                                                                                                                                    │
│ E5.7 Commit boundary                                                                                                                               │
│ - Assert no durable write occurred.                                                                                                                │
│ - Any mutation remains proposed_state_diff only.                                                                                                  │
│ - Any external action must be represented with exact action receipt and authorization lineage.                                                     │
│ - Any commit request must go to Exit/UWG, not L4 directly.                                                                                         │
│                                                                                                                                                    │
│ E5.8 Dispatch receipt                                                                                                                              │
│ - Emit sealed_l2_artifact_id for Evaluation Spine, Exit Spine, UWG decisioning, L6 audit, and L3 workflow merge if managed.                       │
│ - If this was an L3 step, return step_result_status, artifacts, errors, and next-step hints to L3 through the governed channel.                   │
│ - If this was a single-step route, dispatch directly to Exit Eval & Control.                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ SEALED L2 ARTIFACT CONTENTS                                                                                                                       │
│                                                                                                                                                    │
│ identity                                                                                                                                           │
│ - sealed_l2_artifact_id                                                                                                                            │
│ - run_id                                                                                                                                           │
│ - route_id / route_contract_id                                                                                                                     │
│ - workflow_id / step_id if applicable                                                                                                              │
│ - parent_plan_id / parent_route_id / parent_step_id                                                                                                │
│                                                                                                                                                    │
│ governance                                                                                                                                         │
│ - compliance_hash                                                                                                                                  │
│ - policy_hash                                                                                                                                      │
│ - blueprint_hash                                                                                                                                   │
│ - capability_token reference                                                                                                                       │
│ - sandbox_envelope reference                                                                                                                       │
│ - side_effect_class                                                                                                                                │
│                                                                                                                                                    │
│ execution                                                                                                                                          │
│ - payload                                                                                                                                          │
│ - artifacts                                                                                                                                        │
│ - proposed_state_diff                                                                                                                              │
│ - stdout/stderr summary                                                                                                                            │
│ - tool/model/action receipts                                                                                                                       │
│ - attempt_count                                                                                                                                    │
│ - repair_count                                                                                                                                     │
│                                                                                                                                                    │
│ evidence                                                                                                                                           │
│ - source refs                                                                                                                                      │
│ - cited spans                                                                                                                                      │
│ - C0 evidence contract refs                                                                                                                        │
│ - support gaps                                                                                                                                     │
│ - contradiction flags                                                                                                                              │
│                                                                                                                                                    │
│ replay                                                                                                                                             │
│ - replay_key                                                                                                                                       │
│ - input_hash                                                                                                                                       │
│ - prompt_hash                                                                                                                                      │
│ - snapshot_manifest                                                                                                                                │
│ - deterministic receipts                                                                                                                           │
│ - environment digest                                                                                                                               │
│                                                                                                                                                    │
│ observability                                                                                                                                      │
│ - trace_id                                                                                                                                         │
│ - span_ids                                                                                                                                         │
│ - latency / token / cost metrics                                                                                                                   │
│ - timeout / circuit breaker status                                                                                                                 │
│ - route/workflow join keys                                                                                                                         │
│                                                                                                                                                    │
│ terminal                                                                                                                                           │
│ - terminal_class                                                                                                                                   │
│ - reason_code                                                                                                                                      │
│ - downstream_recommendation                                                                                                                        │
│ - user_visible_safe = true | false                                                                                                                 │
│ - commit_requested = true | false                                                                                                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ TERMINAL CLASS MEANINGS                                                                                                                            │
│                                                                                                                                                    │
│ SUCCESS                                                                                                                                            │
│ - Local contract satisfied. Send to Exit for final current-run review.                                                                              │
│                                                                                                                                                    │
│ DEGRADED_SUCCESS                                                                                                                                   │
│ - Useful partial result exists. Caveats and missing support must remain explicit downstream.                                                        │
│                                                                                                                                                    │
│ FAILURE                                                                                                                                            │
│ - Work could not complete under current packet, but no policy breach occurred.                                                                       │
│                                                                                                                                                    │
│ NEEDS_HELP                                                                                                                                         │
│ - Requires missing input, new authority, HITL, reroute, or broader workflow decision.                                                               │
│                                                                                                                                                    │
│ REJECTED                                                                                                                                           │
│ - Packet or execution violated a rule, safety boundary, injection guard, sandbox guard, or authority boundary.                                    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ E5 OUTPUT CONTRACT                                                                                                                                 │
│ - sealed_l2_artifact_id                                                                                                                            │
│ - terminal_class                                                                                                                                   │
│ - final_payload or failure_payload                                                                                                                 │
│ - evidence_bundle                                                                                                                                  │
│ - trace_bundle                                                                                                                                     │
│ - replay_bundle                                                                                                                                    │
│ - proposed_state_diff if any                                                                                                                       │
│ - downstream_recommendation                                                                                                                        │
│ - commit_requested = true | false                                                                                                                  │
│ - dispatch_target = EXIT_CONTROL | L3_MERGE | HITL_PACKETIZATION | UWG_REQUEST_CANDIDATE                                                           │
│                                                                                                                                                    │
│ invariant: NO durable commit here. L2 only emits sealed artifacts for downstream control.                                                          │
└──────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────┘
                                                                       │ [ Sealed Folders / Step Results ]
                                                                       ▼
                                      [ DISPATCH TO POST-L2 CONTROL + EVALUATION + DISPOSITION [5] ]

======================================================================================================================================================
                                                    L2 FAILURE / REPAIR / EXIT MATRIX
======================================================================================================================================================

┌───────────────────────────────┬──────────────────────────────────────┬──────────────────────────────────────┬────────────────────────────────────────┐
│ OBSERVED CONDITION             │ L2 CLASSIFICATION                    │ L2 MAY DO                            │ L2 MUST NOT DO                         │
├───────────────────────────────┼──────────────────────────────────────┼──────────────────────────────────────┼────────────────────────────────────────┤
│ malformed JSON output          │ SOFT_REPAIRABLE                      │ repair schema, revalidate, retry      │ invent missing facts                    │
│ transient tool timeout         │ SOFT_REPAIRABLE                      │ bounded retry if budget remains       │ infinite retry / switch tool silently   │
│ nonzero tool return            │ SOFT_REPAIRABLE or FAIL_TERMINAL     │ capture stderr, classify, maybe retry │ hide error                              │
│ missing required input         │ NEEDS_HELP                           │ seal need-help packet                 │ ask human directly or guess             │
│ action outside capability      │ REJECTED                             │ seal rejection                        │ execute anyway                          │
│ sandbox escape attempt         │ REJECTED                             │ quarantine, seal, stop                │ broaden sandbox                         │
│ policy hash mismatch           │ REJECTED                             │ stop and seal                         │ continue under stale policy             │
│ weak evidence for grounded ask │ DEGRADED / NEEDS_HELP                │ seal caveated partial or fail         │ fabricate confidence                    │
│ proposed durable write         │ SUCCESS with proposed diff only      │ include proposed_state_diff           │ write to L4 directly                    │
│ duplicate packet               │ PRIOR_RECEIPT or REJECT_DUPLICATE    │ return sealed prior receipt           │ execute twice                           │
│ route mismatch                 │ NEEDS_HELP / FAIL_TERMINAL           │ seal re-entry need                    │ re-route inside L2                      │
└───────────────────────────────┴──────────────────────────────────────┴──────────────────────────────────────┴────────────────────────────────────────┘

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