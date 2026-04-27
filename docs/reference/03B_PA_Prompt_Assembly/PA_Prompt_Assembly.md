========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: PA_Prompt_Assembly.md
Layer / subsystem: 03B — PA Prompt Assembly (parent)
Parent file: docs/reference/README.md
Ownership surface: Prompt Bill-of-Materials resolution; slot composition; airlock security pass; slot-contract validation; token-budget determinism; provider-aware rendering; final emission of `PromptEnvelope` / `CompiledPromptArtifact`; authority red-team slot verification.
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: PA assembles prompts. It does not retrieve (C0), route (L0), execute (L2), commit (UWG), approve (L5), evaluate (L6), or answer.
Source authority notes: Anchored on `00X` REQ_ID registry; aligned with constitutional §22, §23, §24.
Predecessor preserved at: `PA_Prompt_Assembly.md.pre-reqid-rewrite.bak`
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent uniquely owns:
- the authority-tiered slot order rule (`system > policy > tool_contract > task > evidence > tool_outputs > human_input`)
- the rule that retrieved/tool/human content is data, never instruction
- the deterministic prompt rendering contract
- the PromptEnvelope / CompiledPromptArtifact emission invariants
- the slot red-team verification contract

It does **not** own:
- per-stage detail (lives in `PA.0`..`PA.8`)
- retrieval, routing, execution, durable mutation, approval, evaluation, answering

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**: `RouteContract`, `FinalEvidenceContract` (when grounded), governance artifacts, user task, output schema, execution metadata.
**Downstream outputs**: `PromptEnvelope` and/or `CompiledPromptArtifact` handed to L2 (or to L0 for terminal cache routes if applicable per `RouteContract.execution_form`).
**Forbidden behaviors**: retrieving evidence, routing, executing, mutating, approving, answering; allowing retrieved/tool/human content into instruction tier.
**Allowed outputs only**: `PromptEnvelope`, `CompiledPromptArtifact`, slot-contract receipts, token-budget receipts, red-team-scan receipts.

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
This pack owns rows under `REQ-PA-*`.

4. ATOMIC REQUIREMENTS TABLE (PARENT-LEVEL INVARIANTS)
------------------------------------------------------------------------------------------------------------------------

| REQ_ID | Requirement | Owner | Inputs | Outputs | Runtime Evidence | OTEL Span | Artifact / Receipt | Validator | Negative Control | Expected Fail Reason | Replay Check | Release Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-PA-AUTHORITY-ORDER-001` | The slot authority order MUST be: `system > policy > tool_contract > task > evidence > tool_outputs > human_input`. PA MUST emit a slot-order receipt confirming this order. | PA.2, PA.8 | slot inputs | `PromptEnvelope` | envelope `slots[]` ordered as required; `slot_order_receipt.id` linked | `pa.slot_compose` span; `attributes.slot_order_hash` | `prompt_envelope.json`, `slot_order_receipt.json` | `validator: pa_authority_order_validator` (release-gate) | `NC-PA-ORDER-VIOLATION-001`: place evidence above policy | `pa_authority_order_violation` | `byte_identical` | DOC_ONLY |
| `REQ-PA-DATA-NOT-INSTRUCTION-001` | PA MUST treat retrieved evidence, tool outputs, and human input as data; instruction-tier escalation is FAIL. | PA.3, PA.8 | slot inputs | `PromptEnvelope` | every non-system/policy slot has `tier=data`; airlock receipt records injection findings | `pa.airlock` span | `airlock_receipt.json` | `validator: pa_data_not_instruction_validator` (release-gate) | `NC-PA-INJECT-PROMOTE-001`: a retrieved slot annotated as `system` | `non_authoritative_slot_promoted_to_instruction` | `byte_identical` | DOC_ONLY |
| `REQ-PA-NO-FETCH-NO-EXECUTE-001` | PA MUST NOT retrieve or execute; PA assembles only. | 03B | (governance) | (none) | trace under `pa.*` contains no `c0.*` or `l2.*` children | NOT_APPLICABLE: anti-pattern detection | `compiler_anti_cheat_findings.json` | `validator: pa_no_side_effect_validator` (release-gate) | `NC-PA-FETCH-LEAK-001`: PA invokes retrieval | `pa_side_effect_violation` | `byte_identical` | DOC_ONLY |
| `REQ-PA-PROMPT-BOM-001` | PA MUST resolve a deterministic Prompt Bill-of-Materials (BOM) referencing every slot source by content_hash. | PA.1 | inputs | BOM | `prompt_bom.json` carries all slot source hashes | `pa.bom_resolve` span | `prompt_bom.json` | `validator: pa_bom_validator` (release-gate) | `NC-PA-BOM-DRIFT-001`: BOM differs across replay for same inputs | `pa_bom_drift` | `byte_identical` | DOC_ONLY |
| `REQ-PA-SLOT-CONTRACT-001` | PA MUST validate every slot against its slot contract before emission. Schema or policy violation is FAIL. | PA.4 | composed slots | validation receipt | `slot_validation_receipt.json` | `pa.slot_validate` span | `slot_validation_receipt.json` | `validator: pa_slot_contract_validator` (release-gate) | `NC-PA-SLOT-INVALID-001`: emit envelope with invalid slot | `pa_slot_contract_violation` | `byte_identical` | DOC_ONLY |
| `REQ-PA-TOKEN-BUDGET-001` | PA MUST enforce a token budget that is deterministic for fixed inputs. | PA.5 | composed slots | budget receipt | `token_budget_receipt.json` carries `budget`, `consumed`, `truncations[]` | `pa.token_budget` span | `token_budget_receipt.json` | `validator: pa_token_budget_validator` (release-gate) | `NC-PA-BUDGET-DRIFT-001`: same inputs produce different consumption | `pa_token_budget_drift` | `byte_identical` | DOC_ONLY |
| `REQ-PA-PROVIDER-RENDER-001` | Provider-aware rendering MUST be deterministic; rendering for the same `(provider_id, model_id, slots)` produces identical output. | PA.6 | composed envelope | rendered prompt | `compiled_prompt_artifact.content_hash` deterministic | `pa.render` span | `compiled_prompt_artifact.json` | `validator: pa_render_determinism_validator` (release-gate) | `NC-PA-RENDER-DRIFT-001`: rendering varies for same inputs | `pa_render_drift` | `byte_identical` | DOC_ONLY |
| `REQ-PA-PROMPT-ENVELOPE-EMIT-001` | PA MUST emit exactly one `PromptEnvelope` per L2 invocation; envelope is HMAC-signed and links upstream contracts. | PA.7 | rendered prompt | `PromptEnvelope` | one envelope per `request_id`/`step_id`; `prompt_hash`, `hmac_sig` set | `pa.emit_envelope` span | `prompt_envelope.json` | `validator: pa_envelope_emit_validator` (release-gate) | `NC-PA-DUAL-ENVELOPE-001`: emit two envelopes for one invocation | `pa_dual_envelope` | `byte_identical` | DOC_ONLY |
| `REQ-PA-RED-TEAM-SLOT-001` | PA MUST run a red-team slot scan against known prompt-injection patterns and emit a verification receipt. | PA.8 | composed envelope | red-team receipt | `red_team_scan_receipt.json` lists findings (may be empty) | `pa.red_team_scan` span | `red_team_scan_receipt.json` | `validator: pa_red_team_validator` (release-gate) | `NC-PA-REDTEAM-EVADE-001`: known injection bypasses scan | `pa_red_team_evasion` | `byte_identical` | DOC_ONLY |

5. RUNTIME EVIDENCE CONTRACT
------------------------------------------------------------------------------------------------------------------------
`PromptEnvelope` MUST carry: `prompt_envelope_id`, `request_id`, `route_id`, `step_id?`, `trace_root`, `trace_id`, `span_id`, `slots[]` (each `tier`, `source_id`, `content_hash`), `slot_order_hash`, `prompt_bom_id`, `slot_validation_receipt_id`, `token_budget_receipt_id`, `compiled_prompt_artifact_id?`, `red_team_scan_receipt_id`, `prompt_hash`, `hmac_sig`, `policy_hash`, `blueprint_hash`, `replay_key`, `content_hash`, `lineage`.

`CompiledPromptArtifact` MUST carry the rendered prompt body bound to provider/model and its `content_hash`.

6. OTEL SPAN CONTRACT
------------------------------------------------------------------------------------------------------------------------
Required spans (children of `pa.run`): `pa.boundary_check`, `pa.bom_resolve`, `pa.slot_compose`, `pa.airlock`, `pa.slot_validate`, `pa.token_budget`, `pa.render`, `pa.emit_envelope`, `pa.red_team_scan`.

Required attributes: `req_id`, `request_id`, `route_id`, `prompt_envelope_id`, `policy_hash`, `blueprint_hash`, `replay_key`, `parent_contract_id`.

7. VALIDATOR CONTRACT
------------------------------------------------------------------------------------------------------------------------
- `pa_authority_order_validator`, `pa_data_not_instruction_validator`, `pa_no_side_effect_validator`, `pa_bom_validator`, `pa_slot_contract_validator`, `pa_token_budget_validator`, `pa_render_determinism_validator`, `pa_envelope_emit_validator`, `pa_red_team_validator` (all release-gate)

8. NEGATIVE CONTROL CONTRACT
------------------------------------------------------------------------------------------------------------------------
Each `NC-PA-*` row in §4 is mandatory. `NC-PA-ORDER-VIOLATION-001`, `NC-PA-INJECT-PROMOTE-001`, and `NC-PA-REDTEAM-EVADE-001` are critical-severity.

9. REPLAY CONTRACT
------------------------------------------------------------------------------------------------------------------------
For fixed `(RouteContract, FinalEvidenceContract, governance, user task, output schema, execution metadata, provider_id, model_id, policy_hash, blueprint_hash)`, `PromptEnvelope.content_hash`, `CompiledPromptArtifact.content_hash`, `prompt_hash`, `slot_order_hash` MUST replay byte-identical.

10. RELEASE GATE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 03B row's `Release Gate` is `PASS` only when: authority order intact; data-not-instruction enforced; deterministic BOM; slot contract validated; token budget deterministic; render deterministic; one envelope; red-team scan completed.

11. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**: PA prompt assembly invariants.

**Related files own**: per-stage detail in `PA.0`..`PA.8`; `REQUIREMENT_TRACEABILITY_MATRIX.md` is historical (subsumed by `00X` registry per `00X §13`).

**Forbidden duplicated ownership**: PA MUST NOT retrieve, route, execute, commit, approve, evaluate, or answer.

**Forbidden output vocabulary**: `ALLOW_FINISH`, `DENY`, `REROUTE`, `ESCALATE_HITL`, `COMMIT_REQUEST_TO_UWG`, `SAFE_FALLBACK`, `durable_write_committed`, `policy_certified`, `route_changed`, `workflow_expanded`, `evidence_contract_issued`, `learning_promoted`. The token `prompt_envelope_constructed` is allowed only inside `PromptEnvelope.status`.

12. CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- `PA.0_Boundary_Check.md` — `REQ-PA-BOUNDARY-*`
- `PA.1_Load_Resolve_Prompt_BOM.md` — `REQ-PA-BOM-*`
- `PA.2_Slot_Composition.md` — `REQ-PA-COMPOSE-*`
- `PA.3_Airlock_Security_Pass.md` — `REQ-PA-AIRLOCK-*`
- `PA.4_Validate_Slot_Contract.md` — `REQ-PA-SLOT-VAL-*`
- `PA.5_Token_Budget_Determinism.md` — `REQ-PA-TOKEN-*`
- `PA.6_Provider_Aware_Rendering.md` — `REQ-PA-RENDER-*`
- `PA.7_Final_Emit_Compiled_Prompt_Artifact.md` — `REQ-PA-EMIT-*`
- `PA.8_Authority_RedTeam_Slot_Verification.md` — `REQ-PA-REDTEAM-*`, `REQ-PA-ORDER-*`

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
- Every parent invariant row in §4 has all 13 cells filled.
- Forbidden output vocabulary in §11 reproduces the global ban.
- The 9 child files own per-stage REQ_IDs (deferred for full conversion).
- Authority order rule is binding and validated.

END OF 03B — PA PROMPT ASSEMBLY PARENT
========================================================================================================================
