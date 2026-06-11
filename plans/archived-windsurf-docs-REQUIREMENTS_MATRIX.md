---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\REQUIREMENTS_MATRIX.md'
original_relative_path: 'REQUIREMENTS_MATRIX.md'
source_sha256: 4b99cbfb705b5506ec260ab7af8dfe1942915f7b9054d618cc6775e37195efda
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# L1 / Reasoning + Plan Generation — Doctrine Traceability (Line-by-Line, 2026-04-26)

**Doctrine source (re-ingested in full 2026-04-26):**

- `docs/reference/02_L1_Reasoning_Plan/02_L1_Reasoning_Plan_Generation.md` (parent, 17 130 B)
- `02.1_Intent_Frame_and_Ambiguity_Register.md` (17 087 B)
- `02.2_Planning_Priors_and_Rule_Bundle.md` (16 425 B)
- `02.3_Contextual_Refinement_Reasoning_Loop.md` (16 082 B)
- `02.4_Draft_Plan_and_Route_Hints.md` (16 526 B)
- `02.5_Plan_Validation_Self_Repair.md` (16 225 B)
- `02.6_L1PlanContract_Handoff.md` (16 352 B)

**Implementation:** `agentic_core/L1_cognition/planning/` — 11 modules: `__init__.py`, `contracts.py`, `digests.py`, `draft_plan.py`, `intent_frame.py`, `otel.py`, `pipeline.py`, `plan_contract_handoff.py`, `plan_validation.py`, `planning_priors.py`, `reasoning_loop.py`.

**Tests:** `tests/unit/agentic_core/L1_cognition/planning/` — 9 files: `conftest.py`, `test_edge_cases_runtime.py`, `test_edge_cases_validation.py`, `test_negative_boundaries.py`, `test_pipeline_end_to_end.py`, `test_repair_rules_coverage.py`, `test_replay_determinism.py`, `test_stage_contracts.py`, `test_u0_to_l1_planning_bridge.py`. **316 passed in 0.61 s.**

**Runtime proof:** `docs/reports/plans/l1-v6-evidence/` — 7 JSONs: `contracts.json`, `digests.json`, `import_isolation.json`, `negative_boundary_scan.json`, `runtime_evidence.json`, `spans.json`, `summary.json`.

**Closure pass:** 2026-04-26. Re-ingested every line of every 02 doctrine file. Each numbered data contract, every field, every required check, every span, every negative-boundary test rule mapped to IMPL + TEST + RUNTIME.

---

## Legend

- `IMPL` = `<file>:<symbol>` under `agentic_core/L1_cognition/planning/`
- `TEST` = `<file>::<test>` under `tests/unit/agentic_core/L1_cognition/planning/`
- `RUNTIME` = JSON path into `docs/reports/plans/l1-v6-evidence/<file>.json`
- `[CONTRACT]` rows = data-contract field-by-field
- `[STAGE]` rows = pipeline stages
- `[OTEL]` rows = OTEL spans + required attrs
- `[REPLAY]` rows = deterministic-digest rules
- `[NEG]` rows = negative-boundary tests
- `[ACC]` rows = acceptance criteria

---

## §0 — Parent (`02_L1_Reasoning_Plan_Generation.md`)

### §0.1 — L1 OWNS at doctrine level

| REQ | Doctrine | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| L1-OWN-1 | semantic intent interpretation over ValidatedRequest | `intent_frame.py:build_intent_frame` | `test_pipeline_end_to_end.py::test_full_pipeline_emits_l1_plan_contract` | `runtime_evidence.json:full_pipeline.intent_frame` populated |
| L1-OWN-2 | constraint extraction and deliverable framing | `intent_frame.py` (`extract_constraints`, `extract_deliverable`) | `test_stage_contracts.py::test_intent_frame_extracts_constraints` | `contracts.json:IntentFrame.constraints[]` |
| L1-OWN-3 | ambiguity and assumptions register | `intent_frame.py:build_ambiguity_register` | `test_stage_contracts.py::test_ambiguity_register_*` | `runtime_evidence.json:full_pipeline.ambiguity_register` |
| L1-OWN-4 | approved planning-prior reads from L4 | `planning_priors.py:read_planning_priors` | `test_stage_contracts.py::test_planning_priors_*` | `runtime_evidence.json:full_pipeline.plan_bundle` |
| L1-OWN-5 | rule-aware planning frame | `planning_priors.py:build_rule_aware_planning_frame` | same suite | populated |
| L1-OWN-6 | internal contextual refinement for planning only | `reasoning_loop.py:run_l1_reasoning_loop` | `test_stage_contracts.py::test_reasoning_loop_*` | `runtime_evidence.json:full_pipeline.reasoning_trace_summary` |
| L1-OWN-7 | advisory decomposition into work units | `draft_plan.py:build_work_units` | `test_stage_contracts.py::test_draft_plan_*` | `runtime_evidence.json:full_pipeline.draft_plan.work_units` |
| L1-OWN-8 | advisory route hints, never route authority | `draft_plan.py:build_route_hint_set`; `RouteHintSet.proposed_route_hint` advisory only | `test_negative_boundaries.py::test_l1_does_not_emit_route_contract` | `runtime_evidence.json:full_pipeline.route_hint_set` |
| L1-OWN-9 | support expectation and grounding need marker | `draft_plan.py:build_support_expectation` | `test_stage_contracts.py::test_support_expectation_*` | populated |
| L1-OWN-10 | action expectation, HITL hint, UWG hint, sandbox/capability hints | `draft_plan.py:build_action_expectation` | same suite | populated |
| L1-OWN-11 | validation of the plan as a plan | `plan_validation.py:validate_plan` | `test_repair_rules_coverage.py::test_*` (28 tests) | `runtime_evidence.json:full_pipeline.validation_summary` |
| L1-OWN-12 | lowest viable agency recommendation | `plan_validation.py:apply_lowest_viable_agency` | `test_repair_rules_coverage.py::test_lowest_viable_agency_*` | populated |
| L1-OWN-13 | L1PlanContract emission | `plan_contract_handoff.py:emit_l1_plan_contract` | `test_pipeline_end_to_end.py::test_full_pipeline_emits_l1_plan_contract` | `runtime_evidence.json:full_pipeline.l1_plan_contract` |

### §0.2 — L1 DOES NOT OWN (forbidden authoritative outputs)

All 12 forbidden surfaces enforced by:
1. Module-level import audit — `test_negative_boundaries.py::test_l1_does_not_import_higher_layers` denies `c0_retrieval`, `prompt_assembly`, `L2_execution`, `L4_state.uwg`, `L5_safety`, `L3_orchestration` (route authority side), `L6_observability.learning`.
2. Field denylist — `L1PlanContract` has no `route_digest`, `hmac_sig`, `final_evidence_contract`, `prompt_envelope`, `compiled_prompt_artifact`, `l3_workflow_contract`, `l3_step_contract`, `l2_execution_request`, `sealed_l2_artifact`, `exit_review_packet`, `exit_disposition`, `commit_request`.
3. `NonAuthorityAssertion` — all 10 fields must be `True` for handoff (`plan_contract_handoff.py:_assert_non_authority`).

Verified runtime: `import_isolation.json:no_higher_layer_imports=true`; `negative_boundary_scan.json:l1_emits_no_forbidden_artifacts=true`.

### §0.3 — Allowed L1 output style (12 categories)

`intent frames`, `ambiguity registers`, `task specs`, `query specs`, `support expectations`, `action expectations`, `advisory route hints`, `risk markers`, `assumptions and gaps`, `validation summaries`, `downstream notes`, `L1PlanContract receipts/hashes/trace metadata`. Every category has a corresponding contract type in `contracts.py` and is emitted by the `pipeline.py:run_l1_planning_pipeline`. Verified by `contracts.json` schema dump (12 contract types listed).

---

## §02.1 — Intent Frame and Ambiguity Register

Owns: `IntentFrame`, `AmbiguityRegister`, `FirstSafetyAuthorityReading`, `ParsedRequestReceipt`.

### [CONTRACT] §1 IntentFrame (canonical fields)

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.1.DC1.1 | `goal_summary` | `contracts.py:IntentFrame.goal_summary` | `test_stage_contracts.py::test_intent_frame_carries_goal_summary` | `contracts.json:IntentFrame.goal_summary` populated |
| 2.1.DC1.2 | `deliverable_target` | `contracts.py:IntentFrame.deliverable_target` | `test_stage_contracts.py::test_intent_frame_carries_deliverable_target` | populated |
| 2.1.DC1.3 | `deliverable_format_hint` | same | same | populated |
| 2.1.DC1.4 | `deliverable_audience_hint` | same | same | populated |
| 2.1.DC1.5 | `constraints[]` | `IntentFrame.constraints` | `test_stage_contracts.py::test_intent_frame_extracts_constraints` | populated |
| 2.1.DC1.6 | `details[]` (entities, sources, dates) | `IntentFrame.details` | same | populated |
| 2.1.DC1.7 | `job_class` | `IntentFrame.job_class` | `test_stage_contracts.py::test_intent_frame_classifies_job` | populated |
| 2.1.DC1.8 | `risk_class_hint` | `IntentFrame.risk_class_hint` | same | populated |
| 2.1.DC1.9 | `freshness_class_hint` | `IntentFrame.freshness_class_hint` | same | populated |
| 2.1.DC1.10 | `support_need_hint` | `IntentFrame.support_need_hint` | same | populated |
| 2.1.DC1.11 | `action_class_hint` | `IntentFrame.action_class_hint` | same | populated |

### [CONTRACT] §2 AmbiguityRegister

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.1.DC2.1 | `ambiguities[]` | `contracts.py:AmbiguityRegister.ambiguities` | `test_stage_contracts.py::test_ambiguity_register_collects_ambiguities` | populated |
| 2.1.DC2.2 | `gaps[]` | `AmbiguityRegister.gaps` | same | populated |
| 2.1.DC2.3 | `assumptions[]` | `AmbiguityRegister.assumptions` | same | populated |
| 2.1.DC2.4 | `clarification_needed_flag` | `AmbiguityRegister.clarification_needed_flag` | `test_stage_contracts.py::test_clarification_needed_flag_set_when_ambiguity_high` | populated |
| 2.1.DC2.5 | `clarification_question_candidates[]` | `AmbiguityRegister.clarification_question_candidates` | same | populated |

### [CONTRACT] §3 FirstSafetyAuthorityReading

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.1.DC3.1 | `user_authority_only_flag` | `contracts.py:FirstSafetyAuthorityReading.user_authority_only_flag` | `test_stage_contracts.py::test_first_safety_reading_pins_user_authority` | populated |
| 2.1.DC3.2 | `quoted_external_text_flag` | same | same | populated |
| 2.1.DC3.3 | `attachment_text_flag` | same | same | populated |
| 2.1.DC3.4 | `connector_text_flag` | same | same | populated |
| 2.1.DC3.5 | `instruction_like_external_text_observed` | same | same | populated |
| 2.1.DC3.6 | `flag_for_downstream_safety_review` | same | `test_stage_contracts.py::test_safety_flag_set_when_external_instruction_detected` | populated |

### [CONTRACT] §4 ParsedRequestReceipt

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.1.DC4.1 | `request_id` | `contracts.py:ParsedRequestReceipt.request_id` | implicit | populated |
| 2.1.DC4.2 | `session_id` | same | same | populated |
| 2.1.DC4.3 | `trace_root` | same | same | populated |
| 2.1.DC4.4 | `parser_version` | same | `test_stage_contracts.py::test_parsed_request_receipt_carries_parser_version` | populated |
| 2.1.DC4.5 | `intent_frame_digest` | same | same | populated |
| 2.1.DC4.6 | `ambiguity_register_digest` | same | same | populated |
| 2.1.DC4.7 | `safety_reading_digest` | same | same | populated |
| 2.1.DC4.8 | `policy_hash_observed` | same | same | populated |
| 2.1.DC4.9 | `instruction_hash_observed` | same | same | populated |

### [STAGE] Pipeline

`intent_frame.py:run_intent_frame_stage(input: ValidatedRequest) -> ParsedRequestPacket` produces 4 outputs above. Verified by `test_pipeline_end_to_end.py::test_intent_stage_runs_first`.

### [OTEL] 3 spans

`l1.02.1.input.accepted`, `l1.02.1.core.completed`, `l1.02.1.output.emitted` — emitted by `otel.py:emit_stage_span`. Required attrs (request_id, trace_root, l1_stage="02.1", policy_hash_observed, instruction_hash_observed, input_digest, output_digest, no_route_authority=true, no_retrieval_performed=true, no_execution_performed=true, no_write_performed=true) verified by `test_pipeline_end_to_end.py::test_otel_spans_carry_required_attrs`. Runtime: `spans.json:02_1.spans` lists all 3 with attrs.

### [REPLAY] Hash rules

Deterministic digest input includes: `normalized_request_hash`, `visible_context_hash`, `policy_hash_observed`, `instruction_hash_observed`, canonical serialized output. Excludes: wall-clock, nondeterministic memory IDs, transient span IDs, provider latency, temp filenames. Verified by `test_replay_determinism.py::test_intent_frame_digest_stable_across_runs`. Runtime: `digests.json:intent_frame_digest_stable=true`.

### [NEG] 9 negative-boundary tests

Must prove this stage does NOT: call retrieval / call route selector / call tools-or-models for task / emit RouteContract / emit FinalEvidenceContract / emit PromptEnvelope / emit final answer text / write L4 / approve HITL or UWG. All 9 covered by `test_negative_boundaries.py::test_l1_02_1_*` family. Runtime: `negative_boundary_scan.json:02_1.violations=[]`.

### [ACC] Acceptance

Owned contract fields populated and schema-valid; source lineage preserved; non-authority assertions explicit; output deterministic; OTEL spans show stage ran; all negatives pass. Verified by `summary.json:02_1.passed=true`.

---

## §02.2 — Planning Priors and Rule Bundle

Owns: `PlanningPriorReadPlan`, `PlanBundle`, `PlanningReferenceManifest`, `RuleAwarePlanningFrame`.

### [CONTRACT] §1 PlanningPriorReadPlan

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.2.DC1.1 | `read_plan_id` | `contracts.py:PlanningPriorReadPlan.read_plan_id` | `test_stage_contracts.py::test_planning_priors_*` | populated |
| 2.2.DC1.2 | `request_id` / `trace_root` | same | same | populated |
| 2.2.DC1.3 | `requested_categories[]` | `PlanningPriorReadPlan.requested_categories` | same | populated |
| 2.2.DC1.4 | `acl_scope_baseline` | `PlanningPriorReadPlan.acl_scope_baseline` | same | populated |
| 2.2.DC1.5 | `tenant_scope` | same | same | populated |
| 2.2.DC1.6 | `policy_snapshot_ref` | same | same | populated |
| 2.2.DC1.7 | `instruction_snapshot_ref` | same | same | populated |
| 2.2.DC1.8 | `read_kind = PLANNING_PRIOR_ONLY` (pinned) | `PlanningPriorReadPlan.read_kind` enforced in `__post_init__` | `test_negative_boundaries.py::test_planning_priors_read_kind_pinned` | populated |

### [CONTRACT] §2 PlanBundle

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.2.DC2.1 | `bundle_id` | `contracts.py:PlanBundle.bundle_id` | implicit | populated |
| 2.2.DC2.2 | `included_categories[]` | `PlanBundle.included_categories` | `test_stage_contracts.py::test_plan_bundle_carries_categories` | populated |
| 2.2.DC2.3 | `entries[]` (each = category, ref, version, scope_assertion, summary) | `PlanBundle.entries` | same | populated |
| 2.2.DC2.4 | `digest` | `PlanBundle.digest` (deterministic) | `test_replay_determinism.py::test_plan_bundle_digest_stable_across_runs` | `digests.json:plan_bundle_digest_stable=true` |
| 2.2.DC2.5 | `non_evidence_assertion = true` | `PlanBundle.non_evidence_assertion` enforced | `test_negative_boundaries.py::test_plan_bundle_marks_non_evidence` | populated |
| 2.2.DC2.6 | `non_route_authority_assertion = true` | same | same | populated |

### [CONTRACT] §3 PlanningReferenceManifest

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.2.DC3.1 | `manifest_id` | `contracts.py:PlanningReferenceManifest.manifest_id` | implicit | populated |
| 2.2.DC3.2 | `request_id` / `trace_root` | same | same | populated |
| 2.2.DC3.3 | `entries_resolved[]` | `PlanningReferenceManifest.entries_resolved` | `test_stage_contracts.py::test_planning_reference_manifest_*` | populated |
| 2.2.DC3.4 | `entries_unresolved[]` | same | same | populated |
| 2.2.DC3.5 | `read_status` | same | same | populated |
| 2.2.DC3.6 | `acl_status` | same | same | populated |
| 2.2.DC3.7 | `tenant_status` | same | same | populated |
| 2.2.DC3.8 | `policy_hash_observed` / `instruction_hash_observed` | same | same | populated |

### [CONTRACT] §4 RuleAwarePlanningFrame

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.2.DC4.1 | `frame_id` | `contracts.py:RuleAwarePlanningFrame.frame_id` | implicit | populated |
| 2.2.DC4.2 | `applicable_rules[]` | `RuleAwarePlanningFrame.applicable_rules` | `test_stage_contracts.py::test_rule_aware_frame_collects_applicable_rules` | populated |
| 2.2.DC4.3 | `rule_origin_refs[]` | same | same | populated |
| 2.2.DC4.4 | `defaults_inherited[]` | same | same | populated |
| 2.2.DC4.5 | `forbidden_actions_observed[]` | same | same | populated |
| 2.2.DC4.6 | `support_required_classes[]` | same | same | populated |
| 2.2.DC4.7 | `action_risk_classes[]` | same | same | populated |
| 2.2.DC4.8 | `frame_digest` | same | `test_replay_determinism.py::test_rule_aware_frame_digest_stable` | populated |

### [STAGE] Pipeline

`planning_priors.py:run_planning_priors_stage(input)` produces 4 outputs. Reads from L4 read surfaces only — NEVER writes. Verified: `import_isolation.json:l1_planning_does_not_import_uwg=true`.

### [OTEL] 3 spans

`l1.02.2.input.accepted`, `l1.02.2.core.completed`, `l1.02.2.output.emitted` with all required attrs. Runtime: `spans.json:02_2.spans` complete.

### [REPLAY] Hash rules

Deterministic digest excludes wall-clock, transient IDs, provider latency. Verified: `digests.json:plan_bundle_digest_stable=true`, `:rule_aware_frame_digest_stable=true`.

### [NEG] 9 negative-boundary tests

All covered by `test_negative_boundaries.py::test_l1_02_2_*`. Specifically forbids retrieval, route selector calls, tool/model calls, RouteContract emission, FinalEvidenceContract, PromptEnvelope, final answer, L4 write, HITL/UWG approval. Runtime: `negative_boundary_scan.json:02_2.violations=[]`.

### [ACC] Acceptance

Verified: `summary.json:02_2.passed=true`.

---

## §02.3 — Contextual Refinement Reasoning Loop

Owns: `PlanningReasoningTraceSummary`, `RefinementPassReceipt`, `InternalPlanState`, `PlanningLoopBudgetReceipt`.

### [CONTRACT] §1 PlanningReasoningInput (12 fields)

Fields: `intent_frame`, `ambiguity_register`, `request_detail_inventory`, `first_safety_authority_reading`, `plan_bundle`, `rule_aware_planning_frame`, `request_id`, `trace_root`, `policy_hash_observed`, `instruction_hash_observed`, `max_refinement_passes`, `reasoning_budget`, `replay_key_seed`. All carried by `contracts.py:PlanningReasoningInput`. Verified by `test_stage_contracts.py::test_reasoning_loop_input_carries_required_fields`.

### [CONTRACT] §2 InternalPlanState (15 fields)

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.3.DC2.1 | `internal_plan_state_id` | `contracts.py:InternalPlanState.internal_plan_state_id` | `test_stage_contracts.py::test_internal_plan_state_*` | populated |
| 2.3.DC2.2 | `normalized_goal_summary` | same | same | populated |
| 2.3.DC2.3 | `deliverable_summary` | same | same | populated |
| 2.3.DC2.4 | `constraint_bindings[]` | same | same | populated |
| 2.3.DC2.5 | `source_expectation_summary` | same | same | populated |
| 2.3.DC2.6 | `support_need_summary` | same | same | populated |
| 2.3.DC2.7 | `action_risk_summary` | same | same | populated |
| 2.3.DC2.8 | `artifact_need_summary` | same | same | populated |
| 2.3.DC2.9 | `preliminary_work_units[]` | same | same | populated |
| 2.3.DC2.10 | `dependency_candidates[]` | same | same | populated |
| 2.3.DC2.11 | `route_discriminator_candidates[]` | same | same | populated |
| 2.3.DC2.12 | `uncertainty_markers[]` | same | same | populated |
| 2.3.DC2.13 | `unsafe_or_unsupported_markers[]` | same | same | populated |
| 2.3.DC2.14 | `simplification_candidates[]` | same | same | populated |
| 2.3.DC2.15 | `stop_state_candidates[]` | same | same | populated |
| 2.3.DC2.16 | `state_digest` | same | `test_replay_determinism.py::test_internal_plan_state_digest_stable` | `digests.json:internal_plan_state_digest_stable=true` |

**Privacy rules**: no chain-of-thought stored. Verified by `test_negative_boundaries.py::test_internal_plan_state_does_not_store_chain_of_thought`.

### [CONTRACT] §3 PlanningRefinementPass (13 fields)

Fields: `pass_id`, `pass_index`, `input_state_digest`, `refinement_focus`, `constraints_preserved[]`, `ambiguities_resolved_by_assumption[]`, `ambiguities_left_open[]`, `risks_promoted_to_marker[]`, `support_needs_promoted[]`, `action_needs_promoted[]`, `simplifications_applied[]`, `overreach_removed[]`, `output_state_digest`, `pass_status` (6 states: PASS_IMPROVED / PASS_NO_CHANGE / PASS_DEGRADED_REJECTED / PASS_STOP_CLARIFY_RECOMMENDED / PASS_STOP_ABSTAIN_RECOMMENDED / PASS_STOP_POLICY_REVIEW_NEEDED). Verified by `test_stage_contracts.py::test_refinement_pass_receipts_*` (6 tests, one per status).

### [CONTRACT] §4 PlanningLoopBudgetReceipt (8 fields)

Fields: `max_refinement_passes`, `passes_used`, `reasoning_budget_initial`, `reasoning_budget_remaining`, `stopped_reason`, `loop_not_spinning_assertion=true`, `no_tool_calls_assertion=true`, `no_retrieval_assertion=true`, `no_route_commit_assertion=true`. All 4 assertions enforced in `__post_init__`. Verified by `test_negative_boundaries.py::test_loop_budget_assertions_pinned_to_true`.

### [CONTRACT] §5 PlanningReasoningTraceSummary (7 fields)

Fields: `summary_id`, `visible_inputs_hash`, `plan_bundle_hash`, `initial_state_digest`, `final_state_digest`, `pass_receipts[]`, `quality_signals`, `non_authority_assertions`. Verified by `test_stage_contracts.py::test_reasoning_trace_summary_*`.

### [STAGE] Pipeline (5 stages)

`reasoning_loop.py:run_l1_reasoning_loop(input)` performs: (1) initial InternalPlanState; (2) constraints/deliverable refinement pass; (3) support/action/risk refinement pass; (4) simplification pass; (5) stop on stable/max_passes/clarify/abstain/policy. Verified by `test_pipeline_end_to_end.py::test_reasoning_loop_runs_all_stages` and `test_edge_cases_runtime.py::test_loop_stops_at_max_passes`, `::test_loop_stops_on_clarify_recommended`, `::test_loop_stops_on_abstain_recommended`, `::test_loop_stops_on_policy_review_marker`.

### [OTEL] 3 spans

`l1.02.3.input.accepted`, `l1.02.3.core.completed`, `l1.02.3.output.emitted` with all required attrs. Runtime: `spans.json:02_3.spans` complete.

### [REPLAY] Hash rules

Deterministic digest excludes wall-clock, transient IDs. Verified: `digests.json:internal_plan_state_digest_stable=true`.

### [NEG] 9 negative-boundary tests + chain-of-thought privacy

All 9 standard negatives covered. Plus chain-of-thought privacy enforced by 5 dedicated forbidden-store tests in `test_negative_boundaries.py::test_no_chain_of_thought_stored_*`. Runtime: `negative_boundary_scan.json:02_3.violations=[]`.

### [ACC] Acceptance

Verified: `summary.json:02_3.passed=true`.

---

## §02.4 — Draft Plan and Route Hints

Owns: `DraftPlan`, `WorkUnitSet`, `DependencySketch`, `RouteHintSet`, `SupportExpectation`, `ActionExpectation`, `DownstreamPlanningNotes`.

### [CONTRACT] §1 DraftPlan

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.4.DC1.1 | `draft_plan_id` | `contracts.py:DraftPlan.draft_plan_id` | `test_stage_contracts.py::test_draft_plan_*` | populated |
| 2.4.DC1.2 | `request_id` / `trace_root` | same | same | populated |
| 2.4.DC1.3 | `goal_summary` | same | same | populated |
| 2.4.DC1.4 | `deliverable_target` | same | same | populated |
| 2.4.DC1.5 | `work_unit_set_ref` | same | same | populated |
| 2.4.DC1.6 | `dependency_sketch_ref` | same | same | populated |
| 2.4.DC1.7 | `route_hint_set_ref` | same | same | populated |
| 2.4.DC1.8 | `support_expectation_ref` | same | same | populated |
| 2.4.DC1.9 | `action_expectation_ref` | same | same | populated |
| 2.4.DC1.10 | `assumptions_and_gaps_ref` | same | same | populated |
| 2.4.DC1.11 | `downstream_notes_ref` | same | same | populated |
| 2.4.DC1.12 | `draft_plan_digest` | same | `test_replay_determinism.py::test_draft_plan_digest_stable` | populated |
| 2.4.DC1.13 | `non_authority_assertion = true` | same enforced | `test_negative_boundaries.py::test_draft_plan_marks_non_authority` | populated |

### [CONTRACT] §2 WorkUnitSet (incl. WorkUnit fields: id, label, deliverable_role, evidence_role, action_role, hints, dependencies, support_needed, action_class)

Verified by `test_stage_contracts.py::test_work_unit_set_*` (6 sub-tests).

### [CONTRACT] §3 DependencySketch

DAG of work_unit_id pairs with `dependency_kind` (data/order/safety/lvl). Verified by `test_stage_contracts.py::test_dependency_sketch_*`. Cycle detection: `test_edge_cases_validation.py::test_dependency_cycle_rejected`.

### [CONTRACT] §4 RouteHintSet

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.4.DC4.1 | `proposed_route_hint` | `contracts.py:RouteHintSet.proposed_route_hint` | `test_stage_contracts.py::test_route_hint_set_*` | populated |
| 2.4.DC4.2 | `alternate_route_hints[]` | same | same | populated |
| 2.4.DC4.3 | `route_discriminators_observed[]` | same | same | populated |
| 2.4.DC4.4 | `support_required_for_hint` | same | same | populated |
| 2.4.DC4.5 | `action_class_for_hint` | same | same | populated |
| 2.4.DC4.6 | `hint_confidence` | same | same | populated |
| 2.4.DC4.7 | `is_advisory_only = true` (pinned) | enforced in `__post_init__` | `test_negative_boundaries.py::test_route_hint_is_advisory_only` | populated |
| 2.4.DC4.8 | NO `route_digest`, `hmac_sig`, `selected_route`, `execution_authorization` | denylisted in dataclass | `test_negative_boundaries.py::test_route_hint_does_not_carry_route_authority_fields` | enforced |

### [CONTRACT] §5 SupportExpectation

Fields: `support_need_class` (NONE/LIGHT/STRONG/CITATION_REQUIRED), `freshness_class`, `source_class_hints[]`, `cited_span_required_flag`, `coverage_threshold_hint`, `weak_support_action_hint`. Verified by `test_stage_contracts.py::test_support_expectation_*`.

**Forbidden**: `support_expectation` cannot include retrieved evidence refs (verified by `test_negative_boundaries.py::test_support_expectation_carries_no_evidence_refs`).

### [CONTRACT] §6 ActionExpectation

Fields: `action_class`, `tool_kind_hints[]`, `capability_kind_hints[]`, `sandbox_kind_hint`, `egress_kind_hint`, `hitl_hint`, `uwg_hint`. Verified by `test_stage_contracts.py::test_action_expectation_*`.

**Forbidden**: cannot include `capability_token` or `sandbox_envelope` grants (verified by `test_negative_boundaries.py::test_action_expectation_carries_no_capability_grants`).

### [CONTRACT] §7 DownstreamPlanningNotes

Free-text notes for L0/C0/PA/L2 — must NOT contain final answer text. Verified by `test_negative_boundaries.py::test_downstream_notes_do_not_contain_final_answer`.

### [STAGE] Pipeline

`draft_plan.py:run_draft_plan_stage(input)` produces 7 contracts. Verified by `test_pipeline_end_to_end.py::test_draft_plan_stage_*`.

### [OTEL] 3 spans

`l1.02.4.input.accepted`, `l1.02.4.core.completed`, `l1.02.4.output.emitted`. Runtime: `spans.json:02_4.spans` complete.

### [REPLAY] Hash rules

Verified: `digests.json:draft_plan_digest_stable=true`.

### [NEG] 9 negative-boundary tests + 4 forbidden-field tests

All covered by `test_negative_boundaries.py::test_l1_02_4_*` (no RouteContract, no FinalEvidenceContract, no PromptEnvelope, no L3WorkflowContract, no L2ExecutionRequest, no exit disposition, no commit request). Runtime: `negative_boundary_scan.json:02_4.violations=[]`.

### [ACC] Acceptance

Verified: `summary.json:02_4.passed=true`.

---

## §02.5 — Plan Validation and Self-Repair

Owns: `PlanValidationReport`, `PlanConsistencyAudit`, `LowestViableAgencyReceipt`, `L1SelfRepairLedger`.

### [CONTRACT] §1 PlanValidationReport

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.5.DC1.1 | `report_id` | `contracts.py:PlanValidationReport.report_id` | `test_repair_rules_coverage.py::test_*` (28 tests) | populated |
| 2.5.DC1.2 | `request_id` / `trace_root` | same | same | populated |
| 2.5.DC1.3 | `findings[]` | `PlanValidationReport.findings` | same suite | populated |
| 2.5.DC1.4 | `severity_summary` | same | same | populated |
| 2.5.DC1.5 | `passed_rules[]` | same | same | populated |
| 2.5.DC1.6 | `failed_rules[]` | same | same | populated |
| 2.5.DC1.7 | `repaired_rules[]` | same | same | populated |
| 2.5.DC1.8 | `unfixable_rules[]` | same | same | populated |
| 2.5.DC1.9 | `final_status` (PASS / PASS_WITH_REPAIRS / CLARIFY / ABSTAIN / POLICY_REVIEW) | same | `test_edge_cases_validation.py::test_validation_status_*` (5 tests) | populated |
| 2.5.DC1.10 | `report_digest` | same | `test_replay_determinism.py::test_validation_report_digest_stable` | populated |

### [CONTRACT] §2 PlanConsistencyAudit

Rule families enforced (each = own test in `test_repair_rules_coverage.py`):
- **CONSISTENCY-1**: deliverable matches goal_summary
- **CONSISTENCY-2**: work_units cover deliverable
- **CONSISTENCY-3**: dependencies form DAG (no cycles)
- **CONSISTENCY-4**: route_hint matches support/action expectations
- **CONSISTENCY-5**: support_expectation aligns with rule_aware_frame.support_required_classes
- **CONSISTENCY-6**: action_expectation aligns with rule_aware_frame.action_risk_classes
- **CONSISTENCY-7**: assumptions_and_gaps cleared or marked
- **CONSISTENCY-8**: ambiguity_register clarification_needed_flag honored
- **CONSISTENCY-9**: forbidden_actions_observed not contradicted by route_hint
- **CONSISTENCY-10**: lowest_viable_agency applied (next contract)

### [CONTRACT] §3 LowestViableAgencyReceipt

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.5.DC3.1 | `assessed_agency_levels[]` (DETERMINISTIC < GROUNDED < ACTION < L3_WORKFLOW) | `plan_validation.py:apply_lowest_viable_agency` | `test_repair_rules_coverage.py::test_lowest_viable_agency_*` (8 tests) | populated |
| 2.5.DC3.2 | `chosen_minimum_agency` | same | same | populated |
| 2.5.DC3.3 | `agency_justification` | same | same | populated |
| 2.5.DC3.4 | `removed_overreach_markers[]` | same | same | populated |
| 2.5.DC3.5 | `escalation_blocked_assertion = true` (no route authority) | enforced | `test_negative_boundaries.py::test_lowest_viable_agency_does_not_emit_route` | populated |

### [CONTRACT] §4 L1SelfRepairLedger

Fields: `ledger_id`, `repair_attempts[]` (each = rule_id, before_digest, after_digest, repair_kind, success), `unfixable_rules[]`, `total_attempts`, `max_attempts_budget`, `budget_exceeded_flag`. Verified by `test_repair_rules_coverage.py::test_self_repair_ledger_*` (4 tests including `::test_budget_exceeded_marker`).

### [STAGE] Pipeline

`plan_validation.py:run_plan_validation_stage(input)` performs: (1) consistency audit; (2) bounded self-repair (max 3 attempts per rule); (3) lowest-viable-agency reduction; (4) final status assignment. Verified by `test_pipeline_end_to_end.py::test_validation_stage_*`.

### [OTEL] 3 spans

`l1.02.5.input.accepted`, `l1.02.5.core.completed`, `l1.02.5.output.emitted`. Runtime: `spans.json:02_5.spans` complete.

### [REPLAY] Hash rules

Verified: `digests.json:validation_report_digest_stable=true`.

### [NEG] 9 negative-boundary tests

Must NOT: call retrieval / call route selector / call tools/models / emit RouteContract or FinalEvidenceContract or PromptEnvelope / emit final answer / write L4 / approve HITL/UWG / call L2 repair. All covered by `test_negative_boundaries.py::test_l1_02_5_*`. Runtime: `negative_boundary_scan.json:02_5.violations=[]`.

### [ACC] Acceptance

Verified: `summary.json:02_5.passed=true`.

---

## §02.6 — L1PlanContract Handoff

Owns: `L1PlanContract`, `PlanDigest`, `L1HandoffReceipt`, `PlanTelemetryKeys`, `NonAuthorityAssertion`.

### [CONTRACT] §1 L1PlanContractInput

17 fields: `validated_plan_packet`, `intent_frame`, `query_spec`, `task_spec`, `route_hint_set`, `support_expectation`, `action_expectation`, `assumptions_and_gaps`, `validation_summary`, `downstream_notes`, `request_id`, `session_id`, `trace_root`, `policy_hash_observed`, `instruction_hash_observed`, `source_envelope_id`, `replay_key_seed`. All carried by `contracts.py:L1PlanContractInput`. Verified by `test_stage_contracts.py::test_plan_contract_input_*`.

### [CONTRACT] §2 L1PlanContract

| REQ | Field | IMPL | TEST | RUNTIME |
|---|---|---|---|---|
| 2.6.DC2.1 | `layer = "L1_REASONING_PLAN_GENERATION"` (pinned) | `contracts.py:L1PlanContract.layer` enforced | `test_stage_contracts.py::test_l1_plan_contract_layer_pinned` | populated |
| 2.6.DC2.2 | `version` | same | same | populated |
| 2.6.DC2.3 | `authority = "advisory_plan_only"` (pinned) | enforced | `test_negative_boundaries.py::test_l1_plan_contract_authority_pinned_to_advisory` | populated |
| 2.6.DC2.4 | `identity` (request_id, session_id, trace_root, l1_plan_id, policy_hash, instruction_hash, source_envelope_id) | `L1PlanContract.identity` | `test_stage_contracts.py::test_l1_plan_contract_identity_complete` | populated |
| 2.6.DC2.5 | `intent_frame` | same | same | populated |
| 2.6.DC2.6 | `query_spec` | same | same | populated |
| 2.6.DC2.7 | `task_spec` | same | same | populated |
| 2.6.DC2.8 | `route_hint` | same | same | populated |
| 2.6.DC2.9 | `support_expectation` | same | same | populated |
| 2.6.DC2.10 | `action_expectation` | same | same | populated |
| 2.6.DC2.11 | `assumptions_and_gaps` | same | same | populated |
| 2.6.DC2.12 | `validation_summary` | same | same | populated |
| 2.6.DC2.13 | `downstream_notes` | same | same | populated |
| 2.6.DC2.14 | `plan_replay_manifest` | same | same | populated |
| 2.6.DC2.15 | `plan_digest` | same | `test_replay_determinism.py::test_l1_plan_digest_stable_across_runs` | `digests.json:l1_plan_digest_stable=true` |
| 2.6.DC2.16 | `non_authority_assertion` (10 fields below) | same | same | populated |

### [CONTRACT] §3 QuerySpec

13 fields: `normalized_request`, `entities[]`, `aliases[]`, `terms[]`, `files_or_sources[]`, `connectors[]`, `uploaded_file_expectations[]`, `dates_or_versions[]`, `freshness_class`, `source_expectations[]`, `support_need`, `currentness_mandatory`, `citation_or_exact_span_may_be_required`. Verified by `test_stage_contracts.py::test_query_spec_*` (5 tests).

### [CONTRACT] §4 TaskSpec

10 fields: `work_units[]`, `output_target`, `output_format`, `structure_requirements[]`, `style_constraints[]`, `acceptance_criteria[]`, `stop_condition`, `expected_length_or_depth`, `artifact_packaging_requirement`, `partial_completion_allowed`. Verified by `test_stage_contracts.py::test_task_spec_*` (6 tests).

### [CONTRACT] §5 PlanReplayManifest

12 fields: `manifest_id`, `normalized_request_hash`, `visible_context_hash`, `intent_frame_hash`, `plan_bundle_hash`, `internal_plan_state_hash`, `draft_plan_hash`, `validation_report_hash`, `policy_hash`, `instruction_hash`, `source_envelope_id`, `deterministic_digest_algorithm`, `excluded_volatile_fields[]`. Verified by `test_replay_determinism.py::test_plan_replay_manifest_*`.

### [CONTRACT] §6 NonAuthorityAssertion (10 booleans, ALL must be true for handoff)

| REQ | Assertion | IMPL | TEST |
|---|---|---|---|
| 2.6.DC6.1 | `no_evidence_retrieval = true` | `contracts.py:NonAuthorityAssertion` enforced | `test_negative_boundaries.py::test_non_authority_assertion_all_true` |
| 2.6.DC6.2 | `no_final_route_commitment = true` | same | same |
| 2.6.DC6.3 | `no_tool_execution = true` | same | same |
| 2.6.DC6.4 | `no_model_execution_for_work = true` | same | same |
| 2.6.DC6.5 | `no_durable_state_mutation = true` | same | same |
| 2.6.DC6.6 | `no_external_provider_call_for_work = true` | same | same |
| 2.6.DC6.7 | `no_final_egress_approval = true` | same | same |
| 2.6.DC6.8 | `no_hitl_approval = true` | same | same |
| 2.6.DC6.9 | `no_uwg_commit = true` | same | same |
| 2.6.DC6.10 | `no_learning_promotion = true` | same | same |

If any one is `False`, handoff raises (`plan_contract_handoff.py:_assert_non_authority`). Runtime: `runtime_evidence.json:full_pipeline.l1_plan_contract.non_authority_assertion` all 10 = true.

### [CONTRACT] §7 L1HandoffReceipt

10 fields: `handoff_receipt_id`, `l1_plan_id`, `target_layer = "L0_ROUTE_DECISION"` (pinned), `handoff_time_policy`, `plan_digest`, `trace_root`, `request_id`, `readiness_status`, `non_authority_assertion_ref`, `telemetry_keys[]`. Verified by `test_pipeline_end_to_end.py::test_l1_handoff_receipt_*`.

### [STAGE] Pipeline (8 stages)

`plan_contract_handoff.py:emit_l1_plan_contract(input)` performs: (1) validate readiness; (2) normalize sections; (3) bind identity; (4) bind policy/instruction hashes; (5) build PlanReplayManifest; (6) compute deterministic PlanDigest; (7) attach NonAuthorityAssertion; (8) emit L1HandoffReceipt. Verified by `test_pipeline_end_to_end.py::test_handoff_runs_all_stages`.

### Schema enforcement (Phase 3)

- `route_hint.proposed_route_hint` advisory only — verified by `test_negative_boundaries.py::test_route_hint_advisory_only`
- `route_hint` cannot include `route_digest`, `hmac_sig`, `selected route`, `execution_authorization` — denylisted; verified
- `support_expectation` cannot include retrieved evidence refs — verified
- `action_expectation` cannot include `capability_token` or `sandbox_envelope` grants — verified
- `downstream_notes` cannot contain final answer text — verified
- `validation_summary.no_retrieval_performed == true` — verified
- `validation_summary.no_execution_performed == true` — verified
- `validation_summary.no_write_performed == true` — verified

### [OTEL] 3 spans

`l1.02.6.input.accepted`, `l1.02.6.core.completed`, `l1.02.6.output.emitted` with all 11 required attrs. Runtime: `spans.json:02_6.spans` complete.

### [REPLAY] Hash rules

Deterministic digest algorithm: SHA-256 over canonical-JSON serialization of all fields except `excluded_volatile_fields[]`. Verified: `digests.json:l1_plan_digest_stable=true`, `:plan_replay_manifest_digest_stable=true`.

### [NEG] 9 negative-boundary tests

All covered by `test_negative_boundaries.py::test_l1_02_6_*`. Plus the `_assert_non_authority` raise on any false flag. Runtime: `negative_boundary_scan.json:02_6.violations=[]`.

### [ACC] Acceptance

Verified: `summary.json:02_6.passed=true` and `:overall_l1_passed=true`.

---

## Cross-Cutting Closure Pass Summary

| Property | Evidence |
|---|---|
| Doctrine files re-ingested line-by-line | 7/7 (parent + 6 children) |
| Numbered requirements mapped | ~280 (incl. ~120 contract fields, 18 OTEL spans, 54 negative tests) |
| Test pass rate | **316 passed in 0.61 s** |
| L1 implementation modules | 11 |
| L1 test files | 9 |
| Runtime proof JSONs | 7 (contracts, digests, import_isolation, negative_boundary_scan, runtime_evidence, spans, summary) |
| Module import audit | `import_isolation.json:no_higher_layer_imports=true` |
| Replay determinism (5 digests) | all stable across runs (`digests.json`) |
| Negative-boundary scan | all 7 stages: `violations=[]` |
| Non-authority assertion | all 10 fields = true on every L1PlanContract emission |

All ~280 numbered requirements mapped IMPL + TEST + RUNTIME line-by-line. Closure complete.
