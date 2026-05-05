========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: 03_L0_Route_Decision_Switching_L3.md
Layer / subsystem: 03 — L0 Route Decision and L3 Orchestration (parent)
Parent file: docs/reference/README.md
Ownership surface: L0 deterministic RouteContract emission AND L3 managed-workflow shaping (steps, dependencies, joins, retries, pause/resume, checkpoints).
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: L0 routes; L3 shapes managed workflows. Neither retrieves (C0), assembles prompts (PA), executes (L2), mutates (UWG), approves (L5), or evaluates (L6).
Source authority notes: Anchored on `00X` REQ_ID registry; aligned with constitutional §22, §23, §24.
Predecessor preserved at: `03_L0_Route_Decision_Switching_L3.md.pre-reqid-rewrite.bak`
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent uniquely owns:
- the rule that L0 emits **exactly one** deterministic `RouteContract` per `L1PlanContract`
- the rule that L3 only runs when `RouteContract.execution_form = managed_workflow`
- the route_digest determinism contract
- the L3WorkflowContract / L3StepContract handoff invariants

It does **not** own:
- per-stage detail (lives in `03.1`..`03.9`)
- retrieval (C0), prompt assembly (PA), execution (L2)
- managed-workflow internal step execution (those are L2 inside L3 shape)

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**: `L1PlanContract` (advisory route hints).
**Downstream outputs**: exactly one `RouteContract` per request; if `execution_form=managed_workflow`, then a `L3WorkflowContract` plus current `L3StepContract`.
**Forbidden behaviors**: retrieve, execute models or tools, mutate, approve, promote learning, change route mid-run, hide workflow expansion when not managed_workflow.
**Allowed outputs only**: `RouteContract`, `L3WorkflowContract`, `L3StepContract`, route telemetry, checkpoint receipts.

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
This pack owns rows under `REQ-L0-*` and `REQ-L3-*`.

4. ATOMIC REQUIREMENTS TABLE (PARENT-LEVEL INVARIANTS)
------------------------------------------------------------------------------------------------------------------------

| REQ_ID | Requirement | Owner | Inputs | Outputs | Runtime Evidence | OTEL Span | Artifact / Receipt | Validator | Negative Control | Expected Fail Reason | Replay Check | Release Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-L0-ROUTE-EXACTLY-ONE-001` | L0 MUST emit exactly one `RouteContract` per accepted `L1PlanContract`. Dual-route or zero-route emissions are FAIL. | 03.2, 03.5 | `L1PlanContract` | `RouteContract` | `route_id` count = 1 per `request_id` | `l0.route_decision` parent span | `route_contract_<request_id>.json` | `validator: l0_one_route_validator` (release-gate) | `NC-L0-DUAL-ROUTE-001`: emit two `RouteContract` for one request | `dual_route_emitted` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-L0-DETERMINISTIC-DIGEST-001` | The `route_digest` MUST be deterministic for a fixed `(L1PlanContract, policy_hash, blueprint_hash, registry_digest_set)`. | 03.5 | plan + governance | `RouteContract` | replay shows identical `route_digest` | `l0.route_decision` attribute `route_digest` | `route_contract.json` | `validator: l0_route_digest_validator` (release-gate) | `NC-L0-DIGEST-DRIFT-001`: route_digest differs across replay | `route_digest_drift` | `byte_identical` | DOC_ONLY |
| `REQ-L0-EXECUTION-FORM-001` | `RouteContract.execution_form` MUST be one of {`exact_cache`, `semantic_cache`, `fallback`, `grounded_read`, `single_action`, `managed_workflow`, `hitl`}. | 03.2..03.4 | route input | `RouteContract` | `execution_form` ∈ allowed set | `l0.execution_form` event | `route_contract.json` | `validator: l0_execution_form_validator` (release-gate) | `NC-L0-UNKNOWN-FORM-001`: emit unknown execution_form | `unknown_execution_form` | `byte_identical` | DOC_ONLY |
| `REQ-L0-NO-RETRIEVE-EXECUTE-001` | L0 MUST NOT retrieve evidence, call models, execute tools, or mutate state. | 03 | (governance) | (none) | trace under `l0.*` contains no `c0.*`, `pa.*`, `l2.*`, `uwg.*` children | NOT_APPLICABLE: anti-pattern detection in compiler | `compiler_anti_cheat_findings.json` | `validator: l0_no_side_effect_validator` (release-gate) | `NC-L0-RETRIEVE-LEAK-001`: L0 invokes retrieval | `l0_side_effect_violation` | `byte_identical` | DOC_ONLY |
| `REQ-L0-HMAC-SIGNED-001` | L0 MUST sign every `RouteContract` with an HMAC tied to `policy_hash` and `blueprint_hash`. | 03.5 | route | `RouteContract` | `hmac_sig` field present and verifiable | `l0.route_sign` event | `route_contract.json` | `validator: l0_hmac_validator` (release-gate) | `NC-L0-HMAC-FORGE-001`: forge route_digest without valid hmac | `route_hmac_invalid` | `byte_identical` | DOC_ONLY |
| `REQ-L0-CACHE-FALLBACK-001` | When `execution_form ∈ {exact_cache, semantic_cache, fallback}`, L0 MUST emit a terminal route packet without invoking C0/PA/L2. | 03.3 | cache hit / fallback | terminal route packet | downstream layer spans absent | `l0.cache_terminal` span | `route_contract.json` | `validator: l0_cache_terminal_validator` (release-gate) | `NC-L0-CACHE-LEAK-001`: cache hit still invokes C0 | `cache_terminal_violation` | `byte_identical` | DOC_ONLY |
| `REQ-L0-GROUNDED-HANDOFF-001` | When `execution_form ∈ {grounded_read, single_action, managed_workflow}`, L0 MUST hand off to C0 (when grounding required), PA, and the appropriate execution path. | 03.4 | route | handoff event | downstream span lineage intact | `l0.handoff` span | `route_contract.json` | `validator: l0_handoff_validator` (release-gate) | `NC-L0-HIDDEN-HANDOFF-001`: route claims grounded but skips C0 | `grounded_route_skipped_c0` | `byte_identical` | DOC_ONLY |
| `REQ-L3-MANAGED-WORKFLOW-ELIGIBLE-001` | L3 MUST run only when `RouteContract.execution_form=managed_workflow`. Otherwise L3 MUST NOT expand a workflow. | 03.6 | RouteContract | `L3WorkflowContract` or no-op | absence of `l3.*` spans for non-workflow routes | `l3.eligibility_check` span | `l3_workflow_contract.json` | `validator: l3_eligibility_validator` (release-gate) | `NC-L3-HIDDEN-EXPANSION-001`: L3 expands a single-action route | `hidden_workflow_expansion` | `byte_identical` | DOC_ONLY |
| `REQ-L3-DAG-BOUNDED-001` | The L3 workflow DAG MUST be bounded (max depth, max breadth, no cycles); cycles are FAIL. | 03.6 | workflow plan | `L3WorkflowContract` | `dag_metrics` populated; cycle_count=0 | `l3.dag_validate` span | `l3_workflow_contract.json` | `validator: l3_dag_validator` (release-gate) | `NC-L3-CYCLE-001`: introduce cycle in DAG | `l3_dag_cycle_detected` | `byte_identical` | DOC_ONLY |
| `REQ-L3-STEP-LEDGER-001` | L3 MUST maintain a step ledger with readiness, dependencies, retries, joins, and checkpoint state for each step. | 03.7 | DAG state | step ledger | per-step `state ∈ {pending, ready, in_progress, done, failed, skipped}` | `l3.step_ledger` events | `l3_step_ledger_<workflow_id>.json` | `validator: l3_step_ledger_validator` (release-gate) | `NC-L3-LEDGER-DRIFT-001`: step ledger inconsistent with span trace | `l3_ledger_trace_mismatch` | `byte_identical` | DOC_ONLY |
| `REQ-L3-CONCURRENCY-COMPLETION-001` | L3 MUST manage concurrency, quality fallback, and completion ExitPkg emission. | 03.8 | workflow exec | ExitPkg | `concurrency_metrics` recorded; ExitPkg emitted on completion | `l3.completion` span | `l3_completion_exit_pkg.json` | `validator: l3_completion_validator` (release-gate) | `NC-L3-DOUBLE-COMPLETE-001`: workflow emits two ExitPkg | `l3_dual_completion` | `byte_identical` | DOC_ONLY |
| `REQ-L3-L2-HANDOFF-001` | L3 MUST hand off the current `L3StepContract` to L2 with checkpoint context; resume MUST be idempotent. | 03.9 | step ready | `L3StepContract` | step contract carries `checkpoint_id`, `idempotency_key` | `l3.l2_handoff` span | `l3_step_contract.json` | `validator: l3_l2_handoff_validator` (release-gate) | `NC-L3-RESUME-NONIDEMPOTENT-001`: resume executes step twice | `l3_resume_double_execute` | `byte_identical` | DOC_ONLY |
| `REQ-L0-NO-REROUTE-MID-RUN-001` | L0 MUST NOT re-decide route mid-run. Once `RouteContract` is emitted, the run's route is sealed. | 03.5 | (governance) | (none) | trace shows single route_decision span per request | NOT_APPLICABLE: span uniqueness | `route_contract.json` | `validator: l0_no_reroute_mid_run_validator` (release-gate) | `NC-L0-REROUTE-MID-001`: emit second route mid-run | `route_changed_mid_run` | `byte_identical` | DOC_ONLY |

5. RUNTIME EVIDENCE CONTRACT
------------------------------------------------------------------------------------------------------------------------
`RouteContract` MUST carry: `route_id`, `request_id`, `plan_id`, `trace_root`, `trace_id`, `span_id`, `route_digest`, `hmac_sig`, `execution_form`, `policy_hash`, `blueprint_hash`, `registry_digest_set`, `replay_key`, `content_hash`, `lineage`, `terminal=bool`.

`L3WorkflowContract` MUST carry: `workflow_id`, `route_id`, `dag_metrics`, `step_count`, `policy_hash`, `blueprint_hash`, `replay_key`, `content_hash`, `lineage`.

`L3StepContract` MUST carry: `step_id`, `workflow_id`, `parent_contract_id` (= `route_id` or upstream step), `checkpoint_id`, `idempotency_key`, `policy_hash`, `blueprint_hash`, `replay_key`, `content_hash`.

6. OTEL SPAN CONTRACT
------------------------------------------------------------------------------------------------------------------------
Required spans:
- `l0.route_input_preflight`, `l0.route_decision` (parent), `l0.execution_form`, `l0.route_sign`, `l0.cache_terminal` | `l0.handoff`
- `l3.eligibility_check`, `l3.dag_validate`, `l3.step_ledger`, `l3.completion`, `l3.l2_handoff`

Required attributes: `req_id`, `route_id`, `route_digest`, `execution_form`, `policy_hash`, `blueprint_hash`, `replay_key`, `parent_contract_id`.

7. VALIDATOR CONTRACT
------------------------------------------------------------------------------------------------------------------------
- `l0_one_route_validator`, `l0_route_digest_validator`, `l0_execution_form_validator`, `l0_no_side_effect_validator`, `l0_hmac_validator`, `l0_cache_terminal_validator`, `l0_handoff_validator`, `l0_no_reroute_mid_run_validator` (all release-gate)
- `l3_eligibility_validator`, `l3_dag_validator`, `l3_step_ledger_validator`, `l3_completion_validator`, `l3_l2_handoff_validator` (all release-gate)

8. NEGATIVE CONTROL CONTRACT
------------------------------------------------------------------------------------------------------------------------
Each `NC-L0-*` and `NC-L3-*` row in §4 is mandatory. `NC-L0-DUAL-ROUTE-001`, `NC-L0-RETRIEVE-LEAK-001`, `NC-L3-HIDDEN-EXPANSION-001`, and `NC-L0-REROUTE-MID-001` are critical-severity.

9. REPLAY CONTRACT
------------------------------------------------------------------------------------------------------------------------
For fixed `(L1PlanContract, policy_hash, blueprint_hash, registry_digest_set)`, `route_digest`, `RouteContract.content_hash`, and (when applicable) `L3WorkflowContract.content_hash` MUST replay byte-identical. Allowed nondeterminism: `route_id`, `workflow_id`, `step_id`, `span_id`, `trace_id`, `created_at_utc`.

10. RELEASE GATE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 03 row's `Release Gate` is `PASS` only when: exactly one route, deterministic digest, no hidden side effects, no mid-run reroute, L3 only on workflow routes, bounded DAG, idempotent resume.

11. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**: L0 RouteContract authority and L3 managed-workflow shaping.

**Related files own**: per-stage detail in `03.1`..`03.9`; the cache file `R1B Semantic Cache v2.md`; the gap analysis file is historical only.

**Forbidden duplicated ownership**: L0/L3 MUST NOT retrieve (C0), assemble prompts (PA), execute (L2), mutate (UWG), approve (L5), or evaluate (L6).

**Forbidden output vocabulary**: `ALLOW_FINISH`, `DENY`, `SAFE_FALLBACK`, `COMMIT_REQUEST_TO_UWG`, `durable_write_committed`, `policy_certified`, `evidence_contract_issued`, `prompt_envelope_constructed`, `learning_promoted`. The token `route_changed` is forbidden mid-run.

12. CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- `03.1_L0_Route_Input_and_Preflight.md` — `REQ-L0-PREFLIGHT-*`
- `03.2_L0_Deterministic_Route_Selection.md` — `REQ-L0-SELECT-*`
- `03.3_L0_Cache_Fallback_HITL_Routes.md` — `REQ-L0-CACHE-*`, `REQ-L0-FALLBACK-*`, `REQ-L0-HITL-*`
- `03.4_L0_Grounded_and_Action_Route_Handoffs.md` — `REQ-L0-GROUNDED-*`, `REQ-L0-ACTION-*`
- `03.5_L0_RouteContract_Telemetry_Replay.md` — `REQ-L0-DIGEST-*`, `REQ-L0-HMAC-*`, `REQ-L0-TELEMETRY-*`
- `03.6_L3_Managed_Workflow_Eligibility_and_DAG.md` — `REQ-L3-ELIG-*`, `REQ-L3-DAG-*`
- `03.7_L3_Step_Readiness_State_Ledger_and_Context_Bus.md` — `REQ-L3-LEDGER-*`
- `03.8_L3_Concurrency_Quality_Fallback_Completion_ExitPkg.md` — `REQ-L3-COMPLETION-*`, `REQ-L3-CONCURRENCY-*`
- `03.9_L3_L2_Step_Handoff_Checkpoint_Resume.md` — `REQ-L3-HANDOFF-*`, `REQ-L3-RESUME-*`

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
- Every parent invariant row in §4 has all 13 cells filled.
- Forbidden output vocabulary in §11 reproduces the global ban.
- The 9 child files own per-stage REQ_IDs (deferred for full conversion).
- The orphan file `03_L0_Route_Decision_Switching_L3 exec.md` (with embedded space) is flagged for archive in `00X` superseded ledger.

END OF 03 — L0/L3 PARENT
========================================================================================================================
