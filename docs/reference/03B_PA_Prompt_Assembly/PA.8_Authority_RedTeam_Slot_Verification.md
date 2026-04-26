========================================================================================================================
PA.8 AUTHORITY RED-TEAM AND SLOT FORMAL VERIFICATION
GAP-CLOSED FULL OVERWRITE | MECE | IMPLEMENTATION-GRADE | WINDSURF-EXECUTABLE
========================================================================================================================

PURPOSE
------------------------------------------------------------------------------------------------------------------------
Define Prompt Assembly-specific formal and adversarial tests for slot authority, injection boundaries, provider rendering, schema binding, and no hidden retrieval or execution.

SOURCE ALIGNMENT
------------------------------------------------------------------------------------------------------------------------
This file closes the April 2026 gap review without moving ownership across boundaries.
It is additive to the existing MECE split and does not make this folder the owner of upstream or downstream decisions.

GLOBAL NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
- U0 / Intake owns request envelope validation and request identity stamping.
- L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and plan recommendation.
- L0 owns route selection and RouteContract authority.
- L3 owns managed workflow shaping, readiness, checkpointing, and step handoff when the route is workflow-managed.
- 03A C0 owns retrieval, evidence shaping, verification, support score, and FinalEvidenceContract.
- 03B Prompt Assembly owns signed provider-ready PromptEnvelope / CompiledPromptArtifact construction.
- L2 owns bounded execution of exactly one approved packet or current L3 step, including local validation, execution, repair, seal, and receipts.
- 00C Runtime Gates own reusable current-run gate law, GateVerdict schema, live gate invocation map, and gate observability.
- 05 Exit owns current-run checkout, aggregation, X3 disposition, HITL freeze/review flow, and CommitRequest handoff to UWG.
- 00A L5 owns governance certification evidence and re-clearance evidence, not live dispositions.
- 00B L4/UWG owns durable state and durable write admission.
- 06 L6 owns completed-run evaluation, RCA, proposal drafting, gauntlet proof, and future-run learning attempts only.
- 99 owns end-to-end acceptance proof that the whole chain actually ran and respected boundaries.

FORBIDDEN OUTPUTS FROM THIS FILE
------------------------------------------------------------------------------------------------------------------------
This file must not emit or own final runtime dispositions unless explicitly stated as a Runtime Gate or Exit owner file.
Layer-local receipts may contain recommendation hints, result classes, candidate diffs, or proof statuses, but they may not
silently grant route authority, durable write authority, final egress approval, or future-run learning promotion.

UNIQUE OWNERSHIP SURFACE
------------------------------------------------------------------------------------------------------------------------
Prompt Assembly owns prompt packet construction and can prove slot authority. It does not own runtime safety dispositions or
full red-team program governance.

THIS FILE OWNS
------------------------------------------------------------------------------------------------------------------------
- SlotAuthorityProof.
- PromptInjectionFixtureSet for PA-local slot tests.
- ProviderRenderEquivalenceReceipt.
- SchemaBindingProof for R0 provider-native schemas.
- PA no-retrieval/no-execution assertions.

CONTRACTS TO IMPLEMENT
------------------------------------------------------------------------------------------------------------------------
SlotAuthorityProof:
- proof_id
- prompt_bom_ref
- compiled_prompt_artifact_ref
- slot_order
- slot_hashes
- higher_authority_override_map
- lower_authority_override_attempts[]
- blocked_attempts[]
- provider_render_hash
- response_schema_binding_ref
- hmac_sig
- deterministic_digest

PromptInjectionFixture:
- fixture_id
- injected_slot = U0 | C0 | E0 | H0 | tool_output | human_text
- injection_payload_ref
- expected_boundary = data_only | quarantine | redact | reject_packet
- expected_preserved_authority_order
- expected_no_instruction_promotion

RULES
------------------------------------------------------------------------------------------------------------------------
- C0, tool output, and human text are data-only slots.
- R0 schema is bound to provider-native schema fields where supported, not merely prose.
- Provider rendering must not reorder authority slots silently.
- Token trimming must never drop S0, D0, required policy refs, or R0 schema binding.

TEST REQUIREMENTS
------------------------------------------------------------------------------------------------------------------------
- test_pa_blocks_c0_instruction_promotion
- test_pa_blocks_human_text_as_authority
- test_pa_schema_bound_native_not_only_prose
- test_pa_provider_render_preserves_slot_order
- test_pa_token_trim_preserves_required_authority_slots
- test_pa_never_calls_retrieval_or_execution
