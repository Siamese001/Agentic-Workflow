========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: 02_L1_Reasoning_Plan_Generation.md
Layer / subsystem: 02 — L1 Reasoning Plan (parent)
Parent file: docs/reference/README.md
Ownership surface: Intent interpretation, ambiguity register, query_spec, task_spec, planning priors, contextual refinement, draft plan with route hints, plan validation/self-repair, L1PlanContract handoff.
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: L1 owns advisory plan only. It does not route with authority (L0), retrieve final evidence (C0), execute (L2), mutate (UWG), approve (L5), or evaluate (L6).
Source authority notes: Anchored on `00X` REQ_ID registry; aligned with constitutional §22, §23, §24.
Predecessor preserved at: `02_L1_Reasoning_Plan_Generation.md.pre-reqid-rewrite.bak`
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent uniquely owns:
- the L1PlanContract schema invariants
- the rule that L1 emits route _hints_ only, not RouteContracts
- the rule that L1 does not perform final retrieval or execution
- the support-expectation contract bound to grounding need

It does **not** own:
- per-stage detail (lives in `02.1`..`02.6`)
- routing authority (L0)
- retrieval (C0)
- prompt assembly (PA)

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**: `ValidatedRequest` from U0.
**Downstream outputs**: `L1PlanContract` (handed to L0).
**Forbidden behaviors**: routing with authority, final retrieval, execution, durable mutation, approval.
**Allowed outputs only**: `L1PlanContract`, optional `AmbiguityRegister`, route hints (advisory).

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
This pack owns rows under `REQ-L1-*`.

4. ATOMIC REQUIREMENTS TABLE (PARENT-LEVEL INVARIANTS)
------------------------------------------------------------------------------------------------------------------------

| REQ_ID | Requirement | Owner | Inputs | Outputs | Runtime Evidence | OTEL Span | Artifact / Receipt | Validator | Negative Control | Expected Fail Reason | Replay Check | Release Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-L1-PLAN-NO-EXECUTE-001` | L1 MUST NOT execute tools, models, or scripts; L1 MUST NOT make durable writes; L1 MUST NOT issue a final answer. | 02 | `ValidatedRequest` | `L1PlanContract` | trace contains no `l2.*`, no `uwg.commit`, no terminal output spans under `l1.*` | `l1.plan` parent span | `l1_plan_contract_<request_id>.json` | `validator: l1_no_execute_validator` (release-gate) | `NC-L1-EXECUTE-LEAK-001`: L1 invokes a tool | `l1_executed_tool` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-L1-INTENT-FRAME-001` | L1 MUST emit `intent_frame`, `task_spec`, `query_spec`, and `support_expectation` in the plan contract. | 02.1, 02.4 | `ValidatedRequest` | `L1PlanContract` | all 4 fields present and schema-valid | `l1.intent_frame` span | `l1_plan_contract.json` | `validator: l1_intent_frame_validator` (release-gate) | `NC-L1-INTENT-MISSING-001`: emit plan without `intent_frame` | `intent_frame_missing` | `byte_identical` | DOC_ONLY |
| `REQ-L1-AMBIGUITY-REGISTER-001` | When ambiguity is detected, L1 MUST emit an `AmbiguityRegister` with concrete clarification candidates and a non-empty `clarify_or_proceed_decision`. | 02.1 | `ValidatedRequest` | `L1PlanContract.ambiguity_register` | register present when ambiguity detected | `l1.ambiguity` span | `l1_plan_contract.json` | `validator: l1_ambiguity_validator` (release-gate) | `NC-L1-HIDDEN-AMBIGUITY-001`: ambiguous request emits plan without register | `ambiguity_suppressed` | `byte_identical` | DOC_ONLY |
| `REQ-L1-PLAN-PRIORS-001` | L1 MUST bind a versioned planning priors / rule-bundle id to the plan contract. | 02.2 | priors source | plan contract | `plan_priors_id` and `rule_bundle_id` fields populated | `l1.plan_priors` span | `l1_plan_contract.json` | `validator: l1_priors_validator` (release-gate) | `NC-L1-PRIORS-DRIFT-001`: plan emitted without priors id | `plan_priors_missing` | `byte_identical` | DOC_ONLY |
| `REQ-L1-REFINE-LOOP-BOUND-001` | The L1 contextual-refinement loop MUST be bounded; iterations MUST NOT exceed the configured max; exit conditions MUST be enumerated. | 02.3 | refinement state | plan contract | `refine_iterations`, `refine_exit_reason` populated | `l1.refine_loop` span with iteration events | `l1_plan_contract.json` | `validator: l1_refine_loop_validator` (release-gate) | `NC-L1-REFINE-OSCILLATE-001`: refinement loops indefinitely | `refine_loop_exceeded_max` | `byte_identical` per fixed seed | DOC_ONLY |
| `REQ-L1-ROUTE-HINTS-ADVISORY-001` | L1 MAY emit `route_hints[]` only; route hints are advisory, never authoritative. L0 owns the deterministic route. | 02.4 | plan state | plan contract | `route_hints[]` present, `route_authority=false` | `l1.route_hints` span | `l1_plan_contract.json` | `validator: l1_route_hints_advisory_validator` (release-gate) | `NC-L1-ROUTE-AUTHORITY-001`: L1 emits a `RouteContract` | `l1_emitted_route_contract` | `byte_identical` | DOC_ONLY |
| `REQ-L1-PLAN-VALIDATION-001` | L1 MUST run plan validation (schema + safety + risk preview) before emitting `L1PlanContract`; failed validation triggers self-repair or rejection. | 02.5 | draft plan | plan contract or rejection | `validation_receipt_id`, `self_repair_attempts` | `l1.plan_validation` span | `l1_plan_contract.json` or `l1_rejection.json` | `validator: l1_plan_validation_validator` (release-gate) | `NC-L1-VALIDATION-SKIP-001`: plan emitted with validation skipped | `plan_validation_skipped` | `byte_identical` | DOC_ONLY |
| `REQ-L1-HANDOFF-CONTRACT-001` | L1 MUST emit exactly one `L1PlanContract` per request; L0 MUST refuse any non-`L1PlanContract` input. | 02.6 | validated plan | `L1PlanContract` | one and only one plan_id per request_id | `l1.handoff_to_l0` span | `l1_plan_contract.json` | `validator: l1_handoff_validator` (release-gate) | `NC-L1-DUAL-PLAN-001`: emit two plans for one request | `dual_plan_emitted` | `byte_identical` | DOC_ONLY |

5. RUNTIME EVIDENCE CONTRACT
------------------------------------------------------------------------------------------------------------------------
`L1PlanContract` MUST carry: `plan_id`, `request_id`, `trace_root`, `trace_id`, `span_id`, `intent_frame`, `task_spec`, `query_spec`, `support_expectation`, `ambiguity_register?`, `route_hints[]`, `route_authority=false`, `plan_priors_id`, `rule_bundle_id`, `refine_iterations`, `refine_exit_reason`, `validation_receipt_id`, `self_repair_attempts`, `policy_hash`, `blueprint_hash`, `replay_key`, `content_hash`, `lineage`.

6. OTEL SPAN CONTRACT
------------------------------------------------------------------------------------------------------------------------
Span tree under `u0.intake → l1.plan`:
- `l1.intent_frame`, `l1.ambiguity`, `l1.plan_priors`, `l1.refine_loop`, `l1.route_hints`, `l1.plan_validation`, `l1.handoff_to_l0`

Required attributes: `req_id`, `request_id`, `plan_id`, `policy_hash`, `blueprint_hash`, `replay_key`, `parent_contract_id` (= validated_request_id).

7. VALIDATOR CONTRACT
------------------------------------------------------------------------------------------------------------------------
- `l1_no_execute_validator` (release-gate)
- `l1_intent_frame_validator` (release-gate)
- `l1_ambiguity_validator` (release-gate)
- `l1_priors_validator` (release-gate)
- `l1_refine_loop_validator` (release-gate)
- `l1_route_hints_advisory_validator` (release-gate)
- `l1_plan_validation_validator` (release-gate)
- `l1_handoff_validator` (release-gate)

8. NEGATIVE CONTROL CONTRACT
------------------------------------------------------------------------------------------------------------------------
Each `NC-L1-*` row in §4 is mandatory; the `NC-L1-EXECUTE-LEAK-001` and `NC-L1-ROUTE-AUTHORITY-001` are critical-severity (L1 must not violate L0/L2 authority).

9. REPLAY CONTRACT
------------------------------------------------------------------------------------------------------------------------
For fixed `(ValidatedRequest, plan_priors_id, rule_bundle_id, policy_hash, blueprint_hash, seed)`, `L1PlanContract.content_hash` MUST be byte-identical. Allowed nondeterminism: `plan_id`, `span_id`, `trace_id`, `created_at_utc`.

10. RELEASE GATE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 02 row's `Release Gate` is `PASS` only when L1 validates plan, emits a single contract, never executes, never claims route authority, and all negative controls trip correctly.

11. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**: L1 plan generation invariants.

**Related files own**: per-stage detail in `02.1`..`02.6`.

**Forbidden duplicated ownership**: L1 MUST NOT route (L0), retrieve final evidence (C0), execute (L2), mutate (UWG), or approve (L5).

**Forbidden output vocabulary**: `ALLOW_FINISH`, `DENY`, `REROUTE`, `ESCALATE_HITL`, `COMMIT_REQUEST_TO_UWG`, `SAFE_FALLBACK`, `durable_write_committed`, `policy_certified`, `route_changed`, `workflow_expanded`, `evidence_contract_issued`, `prompt_envelope_constructed`, `learning_promoted`. The phrase `route_committed` is forbidden; L1 produces only `route_hints[]`.

12. CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- `02.1_Intent_Frame_and_Ambiguity_Register.md` — `REQ-L1-INTENT-*`, `REQ-L1-AMBIGUITY-*`
- `02.2_Planning_Priors_and_Rule_Bundle.md` — `REQ-L1-PRIORS-*`
- `02.3_Contextual_Refinement_Reasoning_Loop.md` — `REQ-L1-REFINE-*`
- `02.4_Draft_Plan_and_Route_Hints.md` — `REQ-L1-DRAFT-*`, `REQ-L1-ROUTE-HINTS-*`
- `02.5_Plan_Validation_Self_Repair.md` — `REQ-L1-VALIDATION-*`
- `02.6_L1PlanContract_Handoff.md` — `REQ-L1-HANDOFF-*`

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
- Every parent invariant row in §4 has all 13 cells filled.
- L1 forbidden vocabulary in §11 reproduces the global ban.
- The 6 child files own per-stage REQ_IDs (deferred for full conversion).

END OF 02 — L1 REASONING PLAN PARENT
========================================================================================================================
