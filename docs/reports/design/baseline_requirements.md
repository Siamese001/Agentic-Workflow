# Baseline Requirements Catalog
**Phase**: Design Only — No code changes permitted  
**Date**: 2026-04-09  
**Corpus**: 00–06 lifecycle specs, C0–C7 control plane specs, agentic_process_mapping_v29.md  

---

## REQ-001
| Field | Value |
|---|---|
| **req_id** | REQ-001 |
| **category** | Intake / ingress validation |
| **requirement_statement** | Every inbound request MUST pass through an ingress envelope check that performs: (1) transport/form validation, (2) auth/identity verification and tenant binding, (3) quota and burst-control enforcement, (4) schema/required-field validation, (5) encoding normalization, and (6) stamping with request_id, session_id, trace_root, ingress_time, and caller_scope_baseline. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 01_request_intake.md, agentic_process_mapping_v29.md |
| **source_headings** | E1–E6 / FRONT DESK SECURITY CHECK / INGRESS OUTPUT CONTRACT |
| **rationale** | Prevents unvalidated, unauthorized, or malformed requests from entering reasoning/execution. |
| **invariant_or_rule** | "No semantic routing, no L1 planning, no C0 retrieval, no external calls, no mutation authority." |
| **expected_owner_layer** | L5/gateway (pre-L1) |
| **expected_runtime_phase** | Ingress (pre-pipeline) |
| **required_artifacts** | validated_request, request_id, session_id, trace_root, caller_scope_baseline, rejection_reason |
| **required_controls** | Auth gate, quota enforcer, schema validator, normalization filter |
| **required_tests** | Valid pass-through; rejected malformed; rate-limit deny; tenant mismatch deny; missing fields reject |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.97 |
| **HITL_required** | No |

---

## REQ-002
| Field | Value |
|---|---|
| **req_id** | REQ-002 |
| **category** | Intake / ingress validation |
| **requirement_statement** | The ingress layer MUST assign a globally unique request_id and session_id, and MUST start a trace_root for distributed tracing before any pipeline stage executes. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 01_request_intake.md |
| **source_headings** | E1 IS IT A REAL REQUEST?, E6 STAMPING THE TICKET |
| **rationale** | Enables end-to-end traceability and deterministic replay from a single root identifier. |
| **invariant_or_rule** | "request_id / trace_root started" before any downstream processing |
| **expected_owner_layer** | L5/gateway |
| **expected_runtime_phase** | Ingress |
| **required_artifacts** | request_id, session_id, trace_root with ingress_time stamp |
| **required_controls** | UUID assignment, timestamp bind, trace injection |
| **required_tests** | Unique ID per request; trace_root present in all downstream spans; replay can reconstruct trace from root |
| **severity_if_missing** | HIGH |
| **confidence_score** | 0.95 |
| **HITL_required** | No |

---

## REQ-003
| Field | Value |
|---|---|
| **req_id** | REQ-003 |
| **category** | L1 reasoning / plan contract |
| **requirement_statement** | L1 MUST produce a bounded plan output contract containing: proposed_route, query_spec, task_spec, route_risk/confidence, grounding_required flag, and declared assumptions/unresolved gaps. L1 MUST NOT retrieve evidence, route with authority, execute tools, or mutate durable state. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 02_L1_Reasoning_Plan_Generation.md, agentic_process_mapping_v29.md |
| **source_headings** | L1 PLAN OUTPUT CONTRACT, THE THINKING DESK, invariant |
| **rationale** | Separation of concerns: reasoning is isolated from execution. Prevents L1 from acquiring execution authority. |
| **invariant_or_rule** | "L1 produces the notepad plan only. It does not retrieve evidence, route with authority, or perform the work." |
| **expected_owner_layer** | L1 |
| **expected_runtime_phase** | Pre-routing (after ingress) |
| **required_artifacts** | proposed_route, query_spec, task_spec, route_risk, confidence, grounding_required, assumption_gaps |
| **required_controls** | L1 chokepoint enforcing no-execution invariant; plan validation loop (V1–V5) |
| **required_tests** | Plan passes V1 (goal alignment), V2 (policy safety), V3 (logic coherence); abstain on insufficient grounding; no tool calls within L1 |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.95 |
| **HITL_required** | No |

---

## REQ-004
| Field | Value |
|---|---|
| **req_id** | REQ-004 |
| **category** | L1 reasoning / plan contract |
| **requirement_statement** | L1 MUST load governing rules, compliance policies, escalation thresholds, prior examples (SOPs), and pre-approved plan templates from L4 read-only archive before plan synthesis. This context bundle MUST bound every generated plan. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 02_L1_Reasoning_Plan_Generation.md |
| **source_headings** | GATHERING RULES, EXAMPLES, AND PRIORS / M1–M4 |
| **rationale** | Plans must be policy-bounded; loading priors prevents L1 from inventing unconstrained actions. |
| **invariant_or_rule** | M2 SAFETY/POLICY: compliance bounds, disallowed actions, policy-safe bounds |
| **expected_owner_layer** | L1 (read from L4) |
| **expected_runtime_phase** | Pre-synthesis |
| **required_artifacts** | plan_bundle = schemas + policy + exemplars + priors + approved_patterns + limits |
| **required_controls** | L4 read-only access control; policy version bind |
| **required_tests** | Policy constraints reflected in plan; disallowed actions not proposed; policy_hash bound to plan |
| **severity_if_missing** | HIGH |
| **confidence_score** | 0.90 |
| **HITL_required** | No |

---

## REQ-005
| Field | Value |
|---|---|
| **req_id** | REQ-005 |
| **category** | L0 routing / route switching |
| **requirement_statement** | L0 MUST apply a pre-routing gate BEFORE any cache lookup or retrieval. This gate MUST check: tenant/ACL/region/confidentiality filters, effective/expiry date and freshness-band requirements, and version+route-policy bindings. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 03_Route_Decision_Switching.md |
| **source_headings** | PRE-ROUTING GATE |
| **rationale** | "pre-filter first so invalid scope never contaminates cache reuse or retrieval recall" |
| **invariant_or_rule** | Pre-filter is mandatory; no cache access before scope validation |
| **expected_owner_layer** | L0 |
| **expected_runtime_phase** | Routing (post-L1) |
| **required_artifacts** | Pre-routing gate decision; scope validation record |
| **required_controls** | ACL filter, freshness gate, version bind enforcer |
| **required_tests** | Expired scope denied before cache; cross-tenant request blocked; stale items evicted |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.93 |
| **HITL_required** | No |

---

## REQ-006
| Field | Value |
|---|---|
| **req_id** | REQ-006 |
| **category** | L0 routing / route switching |
| **requirement_statement** | L0 MUST implement four distinct routing paths: R1A (exact cache hit, bypass deep pipeline), R1B (semantic cache with policy-approval threshold), R3 (grounded retrieval via C0), R4 (external action dispatch packet), and R5 (safe fallback/abstain). Each path MUST be explicitly selected; no implicit default routing. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 03_Route_Decision_Switching.md |
| **source_headings** | D1–D4, R1A–R5 |
| **rationale** | Deterministic, auditable routing prevents silent path selection and enables replay. |
| **invariant_or_rule** | Route authority is separate from reasoning and retrieval authority. |
| **expected_owner_layer** | L0 |
| **expected_runtime_phase** | Routing |
| **required_artifacts** | route_decision_artifact with explicit path label, route_risk |
| **required_controls** | Route enforcement chokepoint; cache security guard (tenant/freshness); no silent fallback |
| **required_tests** | Exact hit bypasses retrieval; semantic hit respects threshold; grounding fires C0; fallback on no path |
| **severity_if_missing** | HIGH |
| **confidence_score** | 0.92 |
| **HITL_required** | No |

---

## REQ-007
| Field | Value |
|---|---|
| **req_id** | REQ-007 |
| **category** | C0 retrieval / evidence shaping / prompt assembly |
| **requirement_statement** | C0 context engine MUST execute a four-stage evidence pipeline: (C0.1) retrieval plan scoping ACL/freshness/version, (C0.2) dual-mode evidence fetch (dense+sparse), (C0.3) evidence shaping (dedupe, rerank, provenance, contradiction retention), (C0.4) evidence contract (support scoring, coverage gaps, abstain hints). C0 MUST NOT route or execute. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 03_Route_Decision_Switching.md, C5_Retrieval_Prompt_Assembly.md |
| **source_headings** | C0 CONTEXT ENGINE, C0.1–C0.4 |
| **rationale** | Grounded-only evidence assembly prevents hallucination; provenance retention enables audit. |
| **invariant_or_rule** | "C0 retrieves only. Neither side invents facts or policy." |
| **expected_owner_layer** | L0/L3 (C0 substrate) |
| **expected_runtime_phase** | Post-routing, pre-execution |
| **required_artifacts** | verified_chunks, cited_spans, source_ids, coverage_score, gaps, abstain_hint |
| **required_controls** | ACL prefilter, freshness filter, reranker, deduplication, contradiction flagging |
| **required_tests** | Stale chunks filtered; cross-tenant chunks blocked; support score computed; abstain on low coverage |
| **severity_if_missing** | HIGH |
| **confidence_score** | 0.90 |
| **HITL_required** | No |

---

## REQ-008
| Field | Value |
|---|---|
| **req_id** | REQ-008 |
| **category** | C0 retrieval / evidence shaping / prompt assembly |
| **requirement_statement** | Prompt assembly MUST execute a four-stage PA pipeline: (PA.1) load static blocks (system template, policy refs, output schema, persona), (PA.2) slot context (must-use vs optional evidence, citation anchors, C0 precedes U0), (PA.3) token budgeter (trim/stratify, reserve safety/schema, overflow→abstain), (PA.4) sign PromptEnvelope with HMAC and replay metadata. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 03_Route_Decision_Switching.md, C5_Retrieval_Prompt_Assembly.md |
| **source_headings** | PROMPT ASSEMBLY PA.1–PA.4, PROMPT CONTRACT |
| **rationale** | Signed envelope ensures prompt integrity; HMAC enables replay verification. |
| **invariant_or_rule** | "forbid U0/C0 policy invention"; "slot C0 before U0" |
| **expected_owner_layer** | L0/prompt_governance |
| **expected_runtime_phase** | Post-retrieval, pre-execution |
| **required_artifacts** | PromptEnvelope, PromptAssemblyStatus, HMAC, replay_metadata |
| **required_controls** | Token budget enforcer, slot precedence validator, HMAC signer |
| **required_tests** | C0 slots before U0 policy; overflow triggers abstain; HMAC verifiable on replay; schema slot reserved |
| **severity_if_missing** | HIGH |
| **confidence_score** | 0.88 |
| **HITL_required** | No |

---

## REQ-009
| Field | Value |
|---|---|
| **req_id** | REQ-009 |
| **category** | L2 execution / validation / healing |
| **requirement_statement** | All L2 execution MUST route through a single `authorize_and_execute()` chokepoint that: (1) validates context completeness, (2) validates capability token, (3) binds active policy_hash and blueprint_hash, (4) classifies action, (5) requires human review for HUMAN_GATED actions, (6) runs guardrail evaluation, (7) aborts on DENY/ERROR/TIMEOUT/UNKNOWN, (8) routes all mutations through UWG. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 04_Live_Task_Dispatch_Execution.md, C0_Governance_Safety_Enforcement.md |
| **source_headings** | GLOBAL L2 INVARIANTS, E1–E3, execution_guardrail_chokepoint.py docstring |
| **rationale** | Single execution chokepoint prevents unauthorized execution and mutation bypasses. |
| **invariant_or_rule** | "No direct write bypass to L4. Any raw write attempt is a gravity breach and is blocked." |
| **expected_owner_layer** | L2 |
| **expected_runtime_phase** | Execution |
| **required_artifacts** | validation_packet_id, capability_token, policy_hash, blueprint_hash, idempotency_key |
| **required_controls** | execution_guardrail_chokepoint, capability token validator, policy resolver, UWG routing |
| **required_tests** | Missing token → PermissionError; DENY → abort with trace; HUMAN_GATED without approval → HumanReviewRequired; mutation bypassed UWG → blocked |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.97 |
| **HITL_required** | No |

---

## REQ-010
| Field | Value |
|---|---|
| **req_id** | REQ-010 |
| **category** | L2 execution / validation / healing |
| **requirement_statement** | L2 MUST implement an E4 heal loop that: logs precise reason_code, requires parent_packet_id, performs bounded SSOT repair only, verifies hash/replay integrity during repair, tracks repair_count, checks oscillation/retry threshold, and escalates to ESCALATE_ARTIFACT or FAIL_TERMINAL on exhaustion. Heal loop MUST read the SAME blueprint_hash/policy_hash snapshot as execution. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 04_Live_Task_Dispatch_Execution.md, C3_Healing_Remediation_Escalation.md |
| **source_headings** | E4: HEAL LOOP, HEALING TIER ROUTER |
| **rationale** | Bounded repair prevents infinite loops; same-snapshot requirement ensures determinism. |
| **invariant_or_rule** | "VALIDATE and HEAL read the SAME blueprint_hash / policy_hash snapshot" |
| **expected_owner_layer** | L2/L5 |
| **expected_runtime_phase** | Execution (repair path) |
| **required_artifacts** | repair_count, reason_code, parent_packet_id, oscillation_threshold |
| **required_controls** | Repair counter, oscillation guard, SSOT-only repair enforcer, escalation trigger |
| **required_tests** | Repair threshold exceeded → FAIL_TERMINAL; repair uses same blueprint_hash; oscillation detected → escalate |
| **severity_if_missing** | HIGH |
| **confidence_score** | 0.88 |
| **HITL_required** | No |

---

## REQ-011
| Field | Value |
|---|---|
| **req_id** | REQ-011 |
| **category** | L2 execution / validation / healing |
| **requirement_statement** | L2 MUST seal its output in an E5 artifact containing: final answer/artifact, execution traces/ancestry, replay receipts and counters, reason codes, and terminal class (SUCCESS/FAIL/ESCALATE/REJECTED). No durable commit may occur in L2; only sealed artifacts are emitted. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 04_Live_Task_Dispatch_Execution.md |
| **source_headings** | E5: SEAL THE FINAL FOLDER |
| **rationale** | Commit authority belongs exclusively to UWG; sealing without committing enforces this boundary. |
| **invariant_or_rule** | "no durable commit here. L2 only emits sealed artifacts for downstream control." |
| **expected_owner_layer** | L2 |
| **expected_runtime_phase** | Post-execution, pre-exit |
| **required_artifacts** | sealed L2 artifact, terminal_class, replay_keys, validation_counters, execution_lineage |
| **required_controls** | Sealed artifact contract, no-direct-write enforcer |
| **required_tests** | L2 artifact verified as sealed (immutable); no write path accessible from L2; terminal_class present |
| **severity_if_missing** | HIGH |
| **confidence_score** | 0.92 |
| **HITL_required** | No |

---

## REQ-012
| Field | Value |
|---|---|
| **req_id** | REQ-012 |
| **category** | Exit control / runtime evaluation |
| **requirement_statement** | The exit control layer MUST evaluate the sealed L2 artifact against four dimensions: (X1A) current rules/rubrics, (X1B) prompt/format fit and schema completeness, (X1C) policy pass/fail including secrets check, mutation authorization, and replay env completeness, (X1D) groundedness, citation support, abstain correctness. The exit MUST produce one of four explicit dispositions: ALLOW_RESPONSE, DENY/RETURN, ESCALATE_TO_HITL, COMMIT_TO_UWG. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 05_Live_Runtime_Exit_Control.md |
| **source_headings** | X1 CURRENT-RUN EVALUATION, X2 FINAL EXIT GATES |
| **rationale** | Final current-run checkpoint prevents unsafe/incomplete/unevaluated output from reaching the patron or UWG. |
| **invariant_or_rule** | "live runtime disposition is explicit. No silent fallbacks, no hidden commit path, no ungated human modification." |
| **expected_owner_layer** | L5 (exit plane) |
| **expected_runtime_phase** | Post-L2, pre-response |
| **required_artifacts** | exit_disposition enum, evaluation scores (X1A–X1D), reason_code |
| **required_controls** | Four-dimensional scorer, explicit disposition gate, no-silent-fallback enforcer |
| **required_tests** | Secrets revealed → DENY; policy fail → DENY; low confidence → ESCALATE; grounded + safe → ALLOW; commit path → UWG only |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.70 |
| **HITL_required** | YES — exit gate implementation path ambiguous; see HITL-003 |

---

## REQ-013
| Field | Value |
|---|---|
| **req_id** | REQ-013 |
| **category** | HITL / escalation / re-clearance |
| **requirement_statement** | HITL escalation MUST implement a freeze-materialize-review-re-clear sequence: (H1) freeze authority_state=FROZEN, write_auth=NONE; (H2) materialize bounded packet with reason_code, evidence, policy_state; (H3) human reviews bounded packet only, decides APPROVE/MODIFY_DIFF/REJECT+rationale; (H4) human input treated as untrusted DATA until L5 re-clear; APPROVE routes through L5 confirmation gate before ALLOW or COMMIT. No human change may bypass L5 re-clearance. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 05_Live_Runtime_Exit_Control.md |
| **source_headings** | HITL AIRLOCK + MATERIALIZATION, HUMAN REVIEW CORE, HITL RE-CLEARANCE |
| **rationale** | Human input is untrusted; re-clearance prevents human-injected policy bypass. |
| **invariant_or_rule** | "no human change bypasses L5 re-clear" |
| **expected_owner_layer** | L5 |
| **expected_runtime_phase** | Post-exit-gate (escalation path) |
| **required_artifacts** | HITL packet (bounded), review_decision, rationale, re-clearance_result |
| **required_controls** | Freeze enforcer, materialization gate, re-clearance loop, L5 confirmation gate |
| **required_tests** | MODIFY_DIFF without re-clear → blocked; APPROVE bypassing L5 → blocked; bounded packet only (no live state exposure) |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.85 |
| **HITL_required** | YES — re-clearance loop implementation ambiguous; see HITL-004 |

---

## REQ-014
| Field | Value |
|---|---|
| **req_id** | REQ-014 |
| **category** | State sovereignty / write governance / UWG |
| **requirement_statement** | The Universal Write Gateway (UWG) MUST be the sole ink path to L4. It MUST: (1) verify signature/compliance_hash/active policy_hash, (2) verify capability token write authorization, (3) perform RBAC/blast-radius/before-after diff validation, (4) claim exclusive write lock (no ghost writes), (5) execute durable commit + hash-chain append, (6) refresh read surfaces / alias swap / audit sync. No direct write from L2, HITL, L6, or any other layer. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 05_Live_Runtime_Exit_Control.md, C4_State_Sovereignty_Universal_Write_Governance.md |
| **source_headings** | UWG/VAULT CLERK PATH, HARD LAW OF THE LIBRARY |
| **rationale** | Single serialized write gate prevents race conditions, ghost writes, and unauthorized mutations. |
| **invariant_or_rule** | "No direct L2 write | No direct HITL write | No direct L6 write | No live bypass." |
| **expected_owner_layer** | L2/L4 (UWG authority) |
| **expected_runtime_phase** | Write commit path |
| **required_artifacts** | write_lock, hash_chain_entry, commit_receipt, audit_sync_record |
| **required_controls** | Serialized write queue, signature verifier, RBAC checker, blast-radius validator, read-surface refresher |
| **required_tests** | Concurrent write → serialized; direct L2 write → blocked; missing capability token → rejected; hash-chain verifiable after commit |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.95 |
| **HITL_required** | No |

---

## REQ-015
| Field | Value |
|---|---|
| **req_id** | REQ-015 |
| **category** | Governance / safety / policy enforcement |
| **requirement_statement** | C0-Governance MUST operate as a cross-cutting plane spanning all runtime layers (apps→L1→L0/L3→L2→exit→HITL→UWG) with: (G1) invocation triage (static/runtime/human-reentry modes), (G2) authority context loading per-tenant, (G3) structure check (layer isolation, placement audit), (G4) registry validation (identity, model allowlist, digest integrity), (G5) shape classification (dual-tag clash, resource-capability alignment), (G6) policy chokepoint (risk tiering, plan-to-action alignment), (G7) sovereign egress (provider mapping, prompt injection detection, replay sealing, fail-closed only). |
| **explicit_or_inferred** | Explicit |
| **source_files** | C0_Governance_Safety_Enforcement.md |
| **source_headings** | G1–G7, DUAL ENFORCEMENT RAILS, THE DECISION RAIL |
| **rationale** | Dual-rail (static prevention + runtime containment) governance ensures no layer operates without policy bind. |
| **invariant_or_rule** | "Policy: Fail-Closed Only" |
| **expected_owner_layer** | L5 (cross-cutting) |
| **expected_runtime_phase** | All phases |
| **required_artifacts** | compliance_hash, audit_log, replay_envelope, capability_token, sandbox_envelope |
| **required_controls** | Static lane + runtime lane, policy chokepoint, sovereign egress with injection detector |
| **required_tests** | Prompt injection detected and blocked; disallowed model rejected; layer inversion blocked; compliance_hash attached to approved execution |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.93 |
| **HITL_required** | No |

---

## REQ-016
| Field | Value |
|---|---|
| **req_id** | REQ-016 |
| **category** | Capability / tool / model / network / memory gating |
| **requirement_statement** | C7-Capability plane MUST gate every resource access via: (G1) classify access type (read/tool/model/network/memory/write), (G2) registry+allowed-set validation with ACL check, (G3) lane routing, (G4) generate capability_token + sandbox_envelope with scope, expiration, and timeout, (G5) intercept-and-validate call (argument shape, injection check, risk tier), (G6) sovereign egress with no-silent-fallback policy, (G7) invocation record (audit log + replay envelope append). |
| **explicit_or_inferred** | Explicit |
| **source_files** | C7_Capability_Tool_Model_Access_Control_Plane.md |
| **source_headings** | G1–G7, GOVERNED LANES |
| **rationale** | Every capability access must be ticketed, intercepted, and recorded to enable audit and replay. |
| **invariant_or_rule** | "Need Power → Check Roster → Issue Ticket → Guard the Call → Approved Lane Only → Record It." |
| **expected_owner_layer** | L3/L5 |
| **expected_runtime_phase** | Pre-execution (capability grant) |
| **required_artifacts** | capability_token, sandbox_envelope, invocation_record, provider_mapping |
| **required_controls** | Registry validator, ticket issuer, call interceptor, sovereign egress, audit appender |
| **required_tests** | Unregistered tool blocked; capability_token expiry enforced; network call without ticket → denied; invocation record verifiable on replay |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.90 |
| **HITL_required** | No |

---

## REQ-017
| Field | Value |
|---|---|
| **req_id** | REQ-017 |
| **category** | Replay / determinism / integrity |
| **requirement_statement** | C1-Determinism plane MUST: (1) build a replay_envelope binding replay_key to active policy_hash per run, (2) propagate a Freeze signal (L0→L3→L5→L2) halting wall-clock updates, (3) wrap every tool/model invocation with a ReplayGuard that intercepts: no wall clock, no raw random, no uuid4, no live network, no mixed-state reads, (4) execute under guard, (5) produce one stable W<n>-DETERMINISM-DIGEST. Violations → STOP + FAULT_TELEMETRY; no silent non-replayable continuation. |
| **explicit_or_inferred** | Explicit |
| **source_files** | C1_Deterministic_Replay_Execution_Integrity.md |
| **source_headings** | BUILD REPLAY ENVELOPE, REPLAY MODE PROPAGATION, REPLAY GUARD, SEAL FINAL DETERMINISM DIGEST |
| **rationale** | Identical inputs + envelope + clock + reads must always produce identical digest. |
| **invariant_or_rule** | "same input + same envelope + same clock + same reads → same digest" |
| **expected_owner_layer** | L0 (inject), L3 (propagate), L5 (enforce), L2 (execute), L6 (verify) |
| **expected_runtime_phase** | All execution phases |
| **required_artifacts** | replay_key, replay_envelope, determinism_digest (W<n>-DETERMINISM-DIGEST) |
| **required_controls** | Replay envelope builder, freeze signal propagator, replay guard interceptor, digest sealer |
| **required_tests** | Same inputs → same digest; wall-clock access → violation; raw random → violation; replay mismatch → FAULT_TELEMETRY |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.93 |
| **HITL_required** | No |

---

## REQ-018
| Field | Value |
|---|---|
| **req_id** | REQ-018 |
| **category** | Observability / telemetry / anomaly signals |
| **requirement_statement** | C2-Observability plane MUST: (1) read sealed execution traces, exit dispositions, and L4 telemetry shelf; (2) perform four-check spine: time audit, isolation check (seed verify, replay strictness), drift detection (budget/thrash/spikes), packet seal (provenance); (3) emit BUS_D/BUS_E live control signals (deny/re-enter/escalate) to exit gate; (4) emit BUS_T async telemetry (metrics, timing, drift) → L6EvidenceBundle → learning loop. |
| **explicit_or_inferred** | Explicit |
| **source_files** | C2_Observability_Telemetry_Control_Signals.md |
| **source_headings** | L6 VERIFY SPINE, BUS D/BUS E/BUS T, L6EvidenceBundle |
| **rationale** | Real-time anomaly detection enables current-run intervention; async telemetry feeds future learning. |
| **invariant_or_rule** | "does not execute | does not route | generates signals only" |
| **expected_owner_layer** | L6 |
| **expected_runtime_phase** | Post-execution, concurrent with exit |
| **required_artifacts** | L6EvidenceBundle (replay_key, determinism_status, anomaly_flags, audit_traces, normalized_metrics) |
| **required_controls** | Time auditor, isolation checker, drift detector, packet sealer, bus emitters (D/E/T) |
| **required_tests** | Drift detected → BUS_D signal; budget thrash detected; determinism_status reflects guard result; metrics include Recall@K, MRR, citation_precision |
| **severity_if_missing** | HIGH |
| **confidence_score** | 0.88 |
| **HITL_required** | No |

---

## REQ-019
| Field | Value |
|---|---|
| **req_id** | REQ-019 |
| **category** | Observability / telemetry / anomaly signals |
| **requirement_statement** | The ingestion pipeline MUST emit index quality metrics (Recall@K, NDCG/MRR, citation precision, support rate, drift/staleness) to an index eval feedback loop (00.8) that drives: chunking tuning, enrichment tuning, dense/sparse balance adjustment, and partial/full reindex triggers. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 00_ingestion_pipeline_index_build.md |
| **source_headings** | 00.8 INDEX EVAL + FEEDBACK LOOP |
| **rationale** | Without feedback, index quality degrades silently. |
| **invariant_or_rule** | reindex_trigger from staleness/drift signals |
| **expected_owner_layer** | knowledge/L4 |
| **expected_runtime_phase** | Offline (post-ingestion) |
| **required_artifacts** | Recall@K, NDCG, MRR, citation_precision, support_rate, staleness_flag, reindex_trigger |
| **required_controls** | Eval feedback loop, reindex scheduler |
| **required_tests** | Low Recall@K triggers reindex; staleness flag triggers tombstone + reindex; metrics computed per ingestion run |
| **severity_if_missing** | MEDIUM |
| **confidence_score** | 0.82 |
| **HITL_required** | No |

---

## REQ-020
| Field | Value |
|---|---|
| **req_id** | REQ-020 |
| **category** | Shadow evaluation / learning / promotion |
| **requirement_statement** | C6-Evaluation MUST execute an eight-step promotion pipeline: (1–3) archive freeze, (4) case file compilation with incident IDs, (5) incident investigation with RCA, (6) rule drafting (propose only, no live changes), (7) Commandant's Gauntlet (shadow replay + regression + SME sign-off + sovereign approve/veto), (8) knowledge extraction routing to destination class. All promotions MUST commit via Master Ledger Commit (sole write path). |
| **explicit_or_inferred** | Explicit |
| **source_files** | C6_Evaluation_Learning_Promotion_System.md, 06_Shadow_Evaluation_System_Learning.md |
| **source_headings** | S4 SYSTEM LEARNING PIPELINE, COMMANDANT'S GAUNTLET, MASTER LEDGER COMMIT |
| **rationale** | Learning mutations must be approved, replayed, and version-controlled before affecting future runs. |
| **invariant_or_rule** | "Learning signals are recorded for later only; they do not mutate the completed run live." |
| **expected_owner_layer** | L6/L4 (UWG) |
| **expected_runtime_phase** | Async post-run (night-shift only) |
| **required_artifacts** | incident_id, RCA_packet, proposed_rules, promotion_packet (edition_id, rollout_band, destination_class), ledger_commit_receipt |
| **required_controls** | Archive freeze, commandant gate, shadow replay validator, SME sign-off, sole-ink clerk |
| **required_tests** | Promotion rejected without SME approval; live run unaffected by in-progress promotion; rollback on commandant fail; ledger commit verifiable |
| **severity_if_missing** | HIGH |
| **confidence_score** | 0.87 |
| **HITL_required** | YES — commandant sign-off path; see HITL-005 |

---

## REQ-021
| Field | Value |
|---|---|
| **req_id** | REQ-021 |
| **category** | Shadow evaluation / learning / promotion |
| **requirement_statement** | The shadow eval layer (L6) MUST perform four types of async evaluation: (S2A) outcome evals (task completion, groundedness, citation, abstain, escalation correctness), (S2B) trajectory evals (tool selection order, arg correctness, retry thrash, policy compliance), (S2C) governance regressions (exact-match drift, schema drift, API drift, rubric/grader drift, gate regression), (S2D) human calibration (SME adjudication, spot checks, grader calibration). All evaluation is read-only and future-run only. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 06_Shadow_Evaluation_System_Learning.md, C6_Evaluation_Learning_Promotion_System.md |
| **source_headings** | S2 ASYNC EVALUATION, L6 ANALYSIS CORE |
| **rationale** | Multi-dimensional evaluation enables detection of subtle regressions not visible in single-metric scoring. |
| **invariant_or_rule** | "Strict Observer Rule: evidence only, no patron impact, reads only" |
| **expected_owner_layer** | L6 |
| **expected_runtime_phase** | Async post-run |
| **required_artifacts** | unified_score_packet (S2A–S2D), severity_class, drift_flags, calibration_record |
| **required_controls** | Read-only access enforcer, score aggregator, bus_p/bus_t emitters |
| **required_tests** | Outcome eval fires on completed runs; trajectory eval checks tool order; drift detected on schema change; SME calibration affects future thresholds |
| **severity_if_missing** | HIGH |
| **confidence_score** | 0.85 |
| **HITL_required** | No |

---

## REQ-022
| Field | Value |
|---|---|
| **req_id** | REQ-022 |
| **category** | Security / ACL / tenancy / freshness / scope |
| **requirement_statement** | The ingestion pipeline MUST bind ACL, tenant identifiers, confidentiality tiers, freshness bands, effective/expiry dates, and embedding schema versions to each chunk at the metadata binding stage (00.5), BEFORE vector embedding. This metadata MUST be enforced at runtime retrieval via pre-retrieval gate. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 00_ingestion_pipeline_index_build.md |
| **source_headings** | 00.5 METADATA BINDING — CRITICAL |
| **rationale** | Late ACL binding allows cross-tenant contamination. Binding at ingestion time is the only safe order. |
| **invariant_or_rule** | "CRITICAL: Metadata is bound here to enable strict pre-retrieval gating in the Inference Pipeline" |
| **expected_owner_layer** | knowledge/ingestion |
| **expected_runtime_phase** | Offline ingestion |
| **required_artifacts** | bounded_chunk (ACL + tenant_id + confidentiality_tier + freshness_band + effective_date + expiry_date + embedding_schema_version) |
| **required_controls** | ACL binder, freshness stamper, version stamper, pre-retrieval gate at runtime |
| **required_tests** | Chunk without ACL rejected at ingestion; expired chunk filtered at retrieval; cross-tenant chunk blocked; schema version mismatch detected |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.95 |
| **HITL_required** | No |

---

## REQ-023
| Field | Value |
|---|---|
| **req_id** | REQ-023 |
| **category** | Security / ACL / tenancy / freshness / scope |
| **requirement_statement** | C0 retrieval MUST apply ACL prefilter and tenant isolation BEFORE vector search (not after reranking). Cross-tenant chunks MUST never be returned regardless of similarity score. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 03_Route_Decision_Switching.md, C5_Retrieval_Prompt_Assembly.md |
| **source_headings** | PRE-ROUTING GATE, C0.1 RETRIEVAL PLAN |
| **rationale** | Post-retrieval ACL filtering is insufficient; high-similarity cross-tenant chunks may slip through. |
| **invariant_or_rule** | "pre-filter first so invalid scope never contaminates cache reuse or retrieval recall" |
| **expected_owner_layer** | L0/knowledge/gates |
| **expected_runtime_phase** | Pre-retrieval |
| **required_artifacts** | ACL-filtered retrieval plan, tenant_isolation_proof |
| **required_controls** | PreRetrievalGate with ACL+tenant enforcer |
| **required_tests** | Cross-tenant chunk with high similarity score → blocked; expired chunk despite ACL pass → blocked |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.93 |
| **HITL_required** | No |

---

## REQ-024
| Field | Value |
|---|---|
| **req_id** | REQ-024 |
| **category** | Testing / auditability / traceability / evidence |
| **requirement_statement** | Every execution run MUST produce a Proof of Ledger standard artifact containing: catalog_digest, staff_roster, desk_tools_hash, night_shift_protocol_hash, and knowledge_state_digest (rules_state_hash + catalog_state_hash + staff_prior_hash + rubric_baseline_hash). Every historical catalog edit MUST be reconstructable from the sealed incident logbook envelope. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 06_Shadow_Evaluation_System_Learning.md |
| **source_headings** | PROOF OF LEDGER STANDARD |
| **rationale** | Full reconstruction requirement means audit is not optional; the logbook is the compliance evidence. |
| **invariant_or_rule** | "every historical catalog edit must be reconstructable from the sealed incident logbook envelope" |
| **expected_owner_layer** | L4/L6/UWG |
| **expected_runtime_phase** | Post-commit |
| **required_artifacts** | catalog_digest, staff_roster_hash, desk_tools_hash, night_shift_hash, knowledge_state_digest |
| **required_controls** | Ledger seal, hash-chain verify, audit trail enforcer |
| **required_tests** | Catalog edit reconstructable from logbook; knowledge_state_digest changes on any state mutation; audit trail survives process restart |
| **severity_if_missing** | HIGH |
| **confidence_score** | 0.85 |
| **HITL_required** | No |

---

## REQ-025
| Field | Value |
|---|---|
| **req_id** | REQ-025 |
| **category** | Intake / ingestion pipeline |
| **requirement_statement** | The ingestion pipeline MUST implement corpus-aware chunking (00.4) with four distinct strategies: (1) policy/long docs: section-aware boundaries + parent-child markers + eval-tuned overlap; (2) incident/trace: event-boundary chunks + temporal adjacency + no-paragraph-splitting; (3) code/config: symbol+block extraction + file lineage + dependency metadata; (4) visuals/tables: page/element-aware + multimodal flag. No generic default chunking permitted. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 00_ingestion_pipeline_index_build.md |
| **source_headings** | 00.4 CHUNKING POLICY — Corpus Classifier |
| **rationale** | Generic chunking produces poor retrieval quality across heterogeneous document types. |
| **invariant_or_rule** | "Corpus Classifier: Route to specific chunking strategy. No generic defaults." |
| **expected_owner_layer** | knowledge/chunking |
| **expected_runtime_phase** | Offline ingestion |
| **required_artifacts** | Corpus-typed chunk with strategy_id, parent-child markers, type-specific metadata |
| **required_controls** | Corpus classifier, four strategy engines, parent-child hydrate markers |
| **required_tests** | Policy doc → section-aware chunks; incident → event-boundary; code → symbol-aware; visual → multimodal flagged |
| **severity_if_missing** | MEDIUM |
| **confidence_score** | 0.90 |
| **HITL_required** | No |

---

## REQ-026
| Field | Value |
|---|---|
| **req_id** | REQ-026 |
| **category** | Intake / ingestion pipeline |
| **requirement_statement** | The ingestion pipeline MUST maintain a lifecycle+state-sync stage (00.3) that performs: dedupe checksum, version comparison, tombstone of stale data, preservation of graph lineage, and reindex trigger for changed records. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 00_ingestion_pipeline_index_build.md |
| **source_headings** | 00.3 LIFECYCLE + STATE SYNC |
| **rationale** | Without deduplication and tombstoning, stale/duplicated chunks corrupt retrieval quality. |
| **invariant_or_rule** | Dedupe → version compare → tombstone → preserve lineage → reindex |
| **expected_owner_layer** | knowledge/lifecycle |
| **expected_runtime_phase** | Offline ingestion |
| **required_artifacts** | dedupe_checksum, version_diff, tombstone_record, lineage_preservation_proof |
| **required_controls** | Dedupe engine, version comparator, tombstone enforcer, lineage graph |
| **required_tests** | Duplicate doc suppressed; stale version tombstoned before reindex; graph lineage preserved after tombstone |
| **severity_if_missing** | MEDIUM |
| **confidence_score** | 0.88 |
| **HITL_required** | No |

---

## REQ-027
| Field | Value |
|---|---|
| **req_id** | REQ-027 |
| **category** | L0 routing / route switching |
| **requirement_statement** | L0 MUST publish four storage surfaces at runtime handoff (00.9): raw_text_vector, contextual_text_vector, sparse keyword surfaces, canonical raw chunks, and parent-child lineage. These MUST be available as distinct retrieval rails in C0. |
| **explicit_or_inferred** | Explicit |
| **source_files** | 00_ingestion_pipeline_index_build.md, 00C_index_materialization_runtime_handoff.md |
| **source_headings** | 00.9 PUBLISH RETRIEVAL ASSETS / RUNTIME HANDOFF |
| **rationale** | Dual-vector + sparse + canonical + lineage rails enable hybrid retrieval with fallback paths. |
| **invariant_or_rule** | All five surfaces published before runtime can begin |
| **expected_owner_layer** | knowledge/L4 |
| **expected_runtime_phase** | Offline→runtime boundary |
| **required_artifacts** | raw_text_vector index, contextual_text_vector index, sparse keyword index, canonical raw store, parent-child index |
| **required_controls** | Index materialization gate, handoff readiness check |
| **required_tests** | Runtime queries blocked until all five surfaces present; dense and sparse recall both return results |
| **severity_if_missing** | HIGH |
| **confidence_score** | 0.88 |
| **HITL_required** | No |

---

## REQ-028
| Field | Value |
|---|---|
| **req_id** | REQ-028 |
| **category** | Governance / safety / policy enforcement |
| **requirement_statement** | C3-Healing plane MUST implement zero-loss failure containment: on sovereignty error, logic violation, or ghost write attempt, IMMEDIATELY freeze the run, lock UWG pending diffs, route to healing router, emit L4 audit note, and tune L6 future thresholds. The mandate is: "Fix if safe → Escalate by rule → Record every step → Never mutate in secret." |
| **explicit_or_inferred** | Explicit |
| **source_files** | C3_Healing_Remediation_Escalation.md |
| **source_headings** | ZERO-LOSS FAILURE CONTAINMENT |
| **rationale** | Silent mutation on failure violates state sovereignty and makes replay impossible. |
| **invariant_or_rule** | "Never mutate in secret." |
| **expected_owner_layer** | L5/L2 |
| **expected_runtime_phase** | Execution (failure path) |
| **required_artifacts** | freeze_record, pending_diff_lock, audit_note, L6_threshold_update |
| **required_controls** | Freeze gate, UWG lock, audit emitter, L6 feedback channel |
| **required_tests** | Ghost write attempt → freeze + audit; sovereignty violation → immediate freeze; secret mutation attempt → blocked and recorded |
| **severity_if_missing** | CRITICAL |
| **confidence_score** | 0.90 |
| **HITL_required** | No |

---

*Requirements catalog complete: 28 baseline requirements across 15 categories.*
