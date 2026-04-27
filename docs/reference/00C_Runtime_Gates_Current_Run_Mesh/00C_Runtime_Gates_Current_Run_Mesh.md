========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical filename: 00C_Runtime_Gates_Current_Run_Mesh.md
Layer / subsystem: 00C — Runtime Gates Current-Run Mesh (parent)
Parent file: docs/reference/README.md
Ownership surface: G01–G29 GateVerdict law and the gate observability/anti-bypass surface. Parent owns the GateVerdict schema invariants and the per-gate parent REQ_ID. Per-gate detail (G01..G29) lives in `00C.1`..`00C.6`. The gate-to-layer invocation map lives in `00C.9`.
Overwrite mode: full-file, no-overlap, executable contract
No-overlap boundary: 00C owns gate verdict law only. It does not own Exit X3 aggregation (that is `05`), L5 certification evidence (that is `00A`), durable write admission (that is `00B.6`), or end-to-end scenario proof (that is `99`).
Source authority notes: Anchored on `00X` REQ_ID registry; aligned with constitutional §22, §23, §24.
Predecessor preserved at: `00C_Runtime_Gates_Current_Run_Mesh.md.pre-reqid-rewrite.bak`
========================================================================================================================

1. PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent uniquely owns:
- the GateVerdict schema invariants (one binding contract every G01..G29 verdict MUST satisfy)
- the parent REQ_ID per gate (`REQ-GATE-G01-*` through `REQ-GATE-G29-*`)
- the UNKNOWN/NOT_APPLICABLE handling rule
- the gate-to-disposition matrix invariants (per-gate detail in `00C.7`)
- the anti-bypass parent invariants

It does **not** own:
- the per-gate body of evidence (lives in `00C.1`..`00C.6` per gate band)
- the Exit aggregation logic (lives in `05`)
- L5 certification evidence (lives in `00A`)
- durable write admission (lives in `00B.6`)

2. AUTHORITY BOUNDARY
------------------------------------------------------------------------------------------------------------------------
**Upstream inputs**: layer events that invoke a gate (per `00C.9` invocation map).

**Downstream outputs**: a `GateVerdict` per gate invocation; consumed by 05 Exit aggregation.

**Forbidden behaviors**:
- 00C MUST NOT make final disposition decisions (Exit owns X3).
- 00C MUST NOT mutate L4 directly (UWG owns durable write admission).
- 00C MUST NOT issue certification evidence (L5 owns this).
- 00C MUST NOT silently treat UNKNOWN as PASS.

**Allowed outputs only**: `GateVerdict` artifacts conformant to §5.

3. REQ_ID NAMESPACE
------------------------------------------------------------------------------------------------------------------------
This parent owns rows under `REQ-GATE-G01-*` through `REQ-GATE-G29-*` and the cross-gate invariants `REQ-GATE-VERDICT-*`.

Per-gate detail rows (e.g. `REQ-GATE-G06-HITL-INVOKE-001`) live in the matching `00C.x` child file.

4. ATOMIC REQUIREMENTS TABLE (PARENT-LEVEL INVARIANTS)
------------------------------------------------------------------------------------------------------------------------

| REQ_ID | Requirement | Owner | Inputs | Outputs | Runtime Evidence | OTEL Span | Artifact / Receipt | Validator | Negative Control | Expected Fail Reason | Replay Check | Release Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `REQ-GATE-VERDICT-SCHEMA-001` | Every G01–G29 invocation MUST emit a GateVerdict with: `gate_id` ∈ {G01..G29}, `result` ∈ {`PASS`, `FAIL`, `UNKNOWN`, `NOT_APPLICABLE`}, `disposition` ∈ {`ALLOW`, `DENY`, `REROUTE_HINT`, `ESCALATE_HINT`, `BLOCK_COMMIT`, `NA`}, `severity` ∈ {`info`, `low`, `medium`, `high`, `critical`}, `reason_codes[]`, `score`, `threshold`, `evidence_refs[]`, `replay_refs[]`, `confidence`, `abstain_flag`, `remediation_hint`. | 00C | gate input | `gate_verdict.json` | every required field non-null per row's applicability | `gate.<gate_id>` span with `attributes.gate_id`, `attributes.result`, `attributes.disposition`, `attributes.severity`, `attributes.reason_codes`, `attributes.score` | `gate_verdict_<gate_id>.json` | `validator: gate_verdict_schema_validator` (release-gate) | `NC-GATE-MISSING-FIELD-001`: emit verdict missing `reason_codes` | `gate_verdict_field_missing` | `byte_identical` per fixture | DOC_ONLY |
| `REQ-GATE-VERDICT-UNKNOWN-NOT-PASS-001` | UNKNOWN MUST NEVER be treated as PASS by any consumer; the verdict consumer (Exit aggregation) MUST treat UNKNOWN as a release-blocking distinct state. | 00C | gate verdict | (consumer behavior) | `gate_verdict.result=UNKNOWN` produces `gate_verdict.disposition` ∈ {`ESCALATE_HINT`, `DENY`} per gate-class; never `ALLOW` | `gate.<gate_id>` event `unknown_emitted` | `gate_verdict.json` | `validator: gate_unknown_handling_validator` (release-gate) | `NC-GATE-UNKNOWN-AS-PASS-001`: pipeline maps UNKNOWN→ALLOW | `unknown_treated_as_pass` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-VERDICT-NA-JUSTIFY-001` | A `NOT_APPLICABLE` verdict MUST carry `reason_codes` containing a justification token; empty justification escalates to UNKNOWN. | 00C | gate input | gate verdict | `result=NOT_APPLICABLE` always paired with `reason_codes` non-empty | `gate.<gate_id>` attribute `na_reason` | `gate_verdict.json` | `validator: gate_na_justification_validator` (release-gate) | `NC-GATE-NA-EMPTY-001`: emit NA with empty reason | `na_missing_reason_escalated_to_unknown` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-VERDICT-NO-INFER-PASS-001` | A consumer MUST NOT infer PASS from missing evidence; absence of a verdict is `UNKNOWN`, not `PASS`. | 00C | (consumer behavior) | (consumer behavior) | absence of `gate_verdict_<gate_id>.json` for an applicable gate is treated as UNKNOWN | NOT_APPLICABLE: missing-span detection in compiler | `compiler missing_artifacts.json` | `validator: gate_presence_validator` (release-gate) | `NC-GATE-MISSING-VERDICT-001`: omit a required gate verdict | `gate_verdict_missing_for_applicable_gate` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G01-INGRESS-001` | G01 (Ingress) MUST emit a verdict for every ValidatedRequest before L1 receives the request. | 00C.1 | ValidatedRequest | gate_verdict | verdict bound to `request_id` and `trace_root` | `gate.G01.ingress` span child of intake | `gate_verdict_G01.json` | `validator: g01_ingress_validator` (release-gate) | `NC-GATE-G01-SKIP-001`: L1 receives without G01 verdict | `g01_ingress_skipped` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G02-IDENTITY-001` | G02 (Identity) MUST verify caller scope and emit verdict before any retrieval, execution, or write. | 00C.1 | ValidatedRequest | gate_verdict | verdict bound to `caller_scope_baseline` | `gate.G02.identity` span | `gate_verdict_G02.json` | `validator: g02_identity_validator` (release-gate) | `NC-GATE-G02-SCOPE-DRIFT-001`: scope changes mid-run | `caller_scope_drift_detected` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G03-INTENT-001` | G03 (Intent) MUST emit a verdict during L1 plan generation. | 00C.1 | L1PlanContract | gate_verdict | verdict bound to `plan_id` | `gate.G03.intent` span | `gate_verdict_G03.json` | `validator: g03_intent_validator` (release-gate) | `NC-GATE-G03-SKIP-001`: L1 emits plan without G03 | `g03_intent_skipped` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G04-SAFETY-001` | G04 (Safety) MUST emit a verdict at L1 plan finalization and reject unsafe plans. | 00C.1 | L1PlanContract | gate_verdict | verdict carries `safety_class` | `gate.G04.safety` span | `gate_verdict_G04.json` | `validator: g04_safety_validator` (release-gate) | `NC-GATE-G04-UNSAFE-PASS-001`: unsafe plan emits PASS | `unsafe_plan_passed_g04` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G05-RISK-001` | G05 (Risk) MUST emit a risk-tier verdict tied to the planned route. | 00C.1 | L1PlanContract+route hint | gate_verdict | verdict carries `risk_tier_band` | `gate.G05.risk` span | `gate_verdict_G05.json` | `validator: g05_risk_validator` (release-gate) | `NC-GATE-G05-MISLABEL-001`: high-risk plan labeled low | `risk_tier_mislabel` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G06-HITL-001` | G06 (HITL invoke) MUST emit a verdict whenever route requires human input. | 00C.2 | RouteContract | gate_verdict | verdict carries `hitl_reason` | `gate.G06.hitl` span | `gate_verdict_G06.json` | `validator: g06_hitl_validator` (release-gate) | `NC-GATE-G06-AUTO-PROCEED-001`: HITL-required route proceeds without human | `hitl_required_but_auto_proceeded` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G07-ROUTE-001` | G07 (Route) MUST emit a verdict for the deterministic route_digest. | 00C.2 | RouteContract | gate_verdict | verdict carries `route_digest` | `gate.G07.route` span | `gate_verdict_G07.json` | `validator: g07_route_validator` (release-gate) | `NC-GATE-G07-DUAL-ROUTE-001`: emit two RouteContracts in one run | `dual_route_emitted` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G08-RETRIEVAL-001` | G08 (Retrieval) MUST emit a verdict for any C0 retrieval. | 00C.2 | RetrievalPlan | gate_verdict | verdict carries `retrieval_plan_hash` | `gate.G08.retrieval` span | `gate_verdict_G08.json` | `validator: g08_retrieval_validator` (release-gate) | `NC-GATE-G08-HIDDEN-RETRIEVAL-001`: layer retrieves outside C0 without G08 | `hidden_retrieval_no_verdict` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G09-EVIDENCE-001` | G09 (Evidence) MUST emit a verdict on FinalEvidenceContract. | 00C.2 | FinalEvidenceContract | gate_verdict | verdict carries `support_score`, `contradiction_flag`, `evidence_contract_hash` | `gate.G09.evidence` span | `gate_verdict_G09.json` | `validator: g09_evidence_validator` (release-gate) | `NC-GATE-G09-WEAK-PASS-001`: weak evidence labeled PASS | `weak_evidence_passed_g09` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G10-PROMPT-001` | G10 (Prompt) MUST emit a verdict on every PromptEnvelope. | 00C.2 | PromptEnvelope | gate_verdict | verdict carries `prompt_hash`, `authority_order_intact`, `injection_findings` | `gate.G10.prompt` span | `gate_verdict_G10.json` | `validator: g10_prompt_validator` (release-gate) | `NC-GATE-G10-INJECT-001`: prompt admits retrieved instruction as system instruction | `prompt_authority_violation` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G11-TOOL-001` | G11 (Tool) MUST emit a verdict for every L2 tool invocation. | 00C.3 | ToolInvocation | gate_verdict | verdict carries `tool_id`, `capability_token` | `gate.G11.tool` span | `gate_verdict_G11.json` | `validator: g11_tool_validator` (release-gate) | `NC-GATE-G11-AMBIENT-001`: tool invoked outside capability_token scope | `ambient_tool_use` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G12-MODEL-001` | G12 (Model) MUST emit a verdict for every model call. | 00C.3 | ModelInvocation | gate_verdict | verdict carries `provider_id`, `model_id`, `egress_class` | `gate.G12.model` span | `gate_verdict_G12.json` | `validator: g12_model_validator` (release-gate) | `NC-GATE-G12-PROVIDER-FALLBACK-001`: silent provider switch | `silent_provider_fallback` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G13-ARGS-001` | G13 (Args) MUST validate tool/model arguments against schema and policy. | 00C.3 | tool_args | gate_verdict | verdict carries `args_schema_hash`, `policy_violations[]` | `gate.G13.args` span | `gate_verdict_G13.json` | `validator: g13_args_validator` (release-gate) | `NC-GATE-G13-INJECTION-ARG-001`: arg contains injected directive | `arg_injection_detected` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G14-EGRESS-001` | G14 (Egress) MUST emit a verdict for every external call leaving sandbox. | 00C.3 | egress request | gate_verdict | verdict carries `destination`, `egress_class`, `provider_governance_hash` | `gate.G14.egress` span | `gate_verdict_G14.json` | `validator: g14_egress_validator` (release-gate) | `NC-GATE-G14-DARK-EGRESS-001`: external call without verdict | `dark_egress` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G15-SANDBOX-001` | G15 (Sandbox) MUST emit a verdict on every sandbox boundary cross. | 00C.3 | sandbox event | gate_verdict | verdict carries `sandbox_envelope_hash`, `breach_signals[]` | `gate.G15.sandbox` span | `gate_verdict_G15.json` | `validator: g15_sandbox_validator` (release-gate) | `NC-GATE-G15-ESCAPE-001`: sandbox escape attempt | `sandbox_escape_attempt` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G16-MEMORY-001` | G16 (Memory) MUST emit a verdict on memory reads/writes per allowed scope. | 00C.4 | memory op | gate_verdict | verdict carries `memory_scope`, `acl_class` | `gate.G16.memory` span | `gate_verdict_G16.json` | `validator: g16_memory_validator` (release-gate) | `NC-GATE-G16-CROSS-TENANT-001`: cross-tenant memory read | `cross_tenant_memory_access` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G17-PRIVACY-001` | G17 (Privacy) MUST emit a verdict on PII/PHI handling. | 00C.4 | data event | gate_verdict | verdict carries `pii_class`, `redaction_status` | `gate.G17.privacy` span | `gate_verdict_G17.json` | `validator: g17_privacy_validator` (release-gate) | `NC-GATE-G17-PII-LEAK-001`: PII present in egress payload | `pii_egress_leak` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G18-WORKFLOW-001` | G18 (Workflow) MUST emit a verdict at every L3 workflow step boundary. | 00C.4 | step event | gate_verdict | verdict carries `step_id`, `workflow_id` | `gate.G18.workflow` span | `gate_verdict_G18.json` | `validator: g18_workflow_validator` (release-gate) | `NC-GATE-G18-HIDDEN-STEP-001`: workflow expansion without G18 | `hidden_workflow_expansion` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G19-LOOP-001` | G19 (Loop) MUST emit a verdict on iteration / repair loop boundaries. | 00C.4 | loop event | gate_verdict | verdict carries `loop_id`, `iteration_count`, `oscillation_signal` | `gate.G19.loop` span | `gate_verdict_G19.json` | `validator: g19_loop_validator` (release-gate) | `NC-GATE-G19-OSCILLATE-001`: oscillation passes through | `loop_oscillation_unflagged` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G20-BUDGET-001` | G20 (Budget) MUST emit a verdict on cost/time/token budgets at every consume point. | 00C.4 | budget event | gate_verdict | verdict carries `budget_kind`, `consumed`, `limit` | `gate.G20.budget` span | `gate_verdict_G20.json` | `validator: g20_budget_validator` (release-gate) | `NC-GATE-G20-OVERSPEND-001`: budget exhausted but allowed | `budget_exhausted_allowed` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G21-OUTPUT-001` | G21 (Output) MUST emit a verdict on the final output payload. | 00C.5 | output payload | gate_verdict | verdict carries `output_hash`, `safety_findings[]` | `gate.G21.output` span | `gate_verdict_G21.json` | `validator: g21_output_validator` (release-gate) | `NC-GATE-G21-UNSAFE-OUTPUT-001`: unsafe output passes | `unsafe_output_passed` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G22-SECURITY-001` | G22 (Security) MUST emit a verdict on security posture (auth, integrity, freshness). | 00C.5 | security event | gate_verdict | verdict carries `security_findings[]` | `gate.G22.security` span | `gate_verdict_G22.json` | `validator: g22_security_validator` (release-gate) | `NC-GATE-G22-STALE-CRED-001`: stale credential admitted | `stale_credential_admitted` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G23-REPLAY-001` | G23 (Replay) MUST emit a verdict on replay digest comparison. | 00C.5 | replay event | gate_verdict | verdict carries `replay_match_type` | `gate.G23.replay` span | `gate_verdict_G23.json` | `validator: g23_replay_validator` (release-gate) | `NC-GATE-G23-DRIFT-001`: replay digest mismatch passes | `replay_drift_passed` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G24-AUDIT-001` | G24 (Audit) MUST emit a verdict on audit completeness. | 00C.5 | audit ledger event | gate_verdict | verdict carries `audit_chain_hash`, `gaps[]` | `gate.G24.audit` span | `gate_verdict_G24.json` | `validator: g24_audit_validator` (release-gate) | `NC-GATE-G24-CHAIN-BREAK-001`: audit chain break passes | `audit_chain_break` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G25-ANOMALY-001` | G25 (Anomaly) MUST emit a verdict on anomaly signals. | 00C.6 | anomaly signal | gate_verdict | verdict carries `anomaly_class`, `score` | `gate.G25.anomaly` span | `gate_verdict_G25.json` | `validator: g25_anomaly_validator` (release-gate) | `NC-GATE-G25-IGNORE-ANOMALY-001`: high-score anomaly ignored | `anomaly_ignored` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G26-EXIT-001` | G26 (Exit) MUST emit a verdict at the Exit boundary precondition (Exit X1 entry). | 00C.6 | ExitReviewPacket | gate_verdict | verdict carries `exit_packet_id` | `gate.G26.exit` span | `gate_verdict_G26.json` | `validator: g26_exit_validator` (release-gate) | `NC-GATE-G26-EXIT-SKIP-001`: Exit reached without G26 | `exit_precondition_skipped` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G27-WRITE-001` | G27 (Write) MUST emit a verdict on UWG commit eligibility. | 00C.6 | CommitRequest | gate_verdict | verdict carries `commit_request_id`, `eligibility_codes[]` | `gate.G27.write` span | `gate_verdict_G27.json` | `validator: g27_write_validator` (release-gate) | `NC-GATE-G27-DIRECT-WRITE-001`: durable write without G27 | `direct_l4_write_attempt` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G28-TRACE-COMPLETE-001` | G28 (Trace Completeness) MUST emit a verdict on the OTEL span tree completeness for the run. | 00C.6 | trace export | gate_verdict | verdict carries `trace_root`, `expected_spans[]`, `missing_spans[]` | `gate.G28.trace` span | `gate_verdict_G28.json` | `validator: g28_trace_completeness_validator` (release-gate) | `NC-GATE-G28-MISSING-SPAN-001`: required span absent | `required_span_missing` | `byte_identical` | DOC_ONLY |
| `REQ-GATE-G29-LEARNING-FIREWALL-001` | G29 (Learning Firewall) MUST emit a verdict on any L6 promotion attempt. | 00C.6 | L6 proposal | gate_verdict | verdict carries `proposal_id`, `gauntlet_status` | `gate.G29.firewall` span | `gate_verdict_G29.json` | `validator: g29_learning_firewall_validator` (release-gate) | `NC-GATE-G29-LIVE-MUTATE-001`: L6 mutates current run | `l6_live_mutation_attempt` | `byte_identical` | DOC_ONLY |

5. RUNTIME EVIDENCE CONTRACT (GATE VERDICT SCHEMA — BINDING)
------------------------------------------------------------------------------------------------------------------------
Every `GateVerdict` artifact MUST be a JSON object with these fields:

```
{
  "gate_id": "G01" | ... | "G29",
  "result": "PASS" | "FAIL" | "UNKNOWN" | "NOT_APPLICABLE",
  "disposition": "ALLOW" | "DENY" | "REROUTE_HINT" | "ESCALATE_HINT" | "BLOCK_COMMIT" | "NA",
  "severity": "info" | "low" | "medium" | "high" | "critical",
  "reason_codes": [str, ...],
  "score": float | null,
  "threshold": float | null,
  "evidence_refs": [str, ...],
  "replay_refs": [str, ...],
  "confidence": float in [0.0, 1.0],
  "abstain_flag": bool,
  "remediation_hint": str | null,
  "req_id": "REQ-GATE-G##-...",
  "trace_id": str,
  "span_id": str,
  "policy_hash": str,
  "blueprint_hash": str,
  "replay_key": str
}
```

`reason_codes` MUST be non-empty when `result` ∈ {`FAIL`, `UNKNOWN`, `NOT_APPLICABLE`}. Empty `reason_codes` for these states is `FAKE` per `00X` §11.

6. OTEL SPAN CONTRACT
------------------------------------------------------------------------------------------------------------------------
Every gate emits one span `gate.<gate_id>` whose parent is the layer span that invoked the gate per `00C.9` invocation map. Required attributes:
- `gate_id`, `result`, `disposition`, `severity`, `score`, `threshold`, `confidence`, `abstain_flag`
- `req_id`, `policy_hash`, `blueprint_hash`, `replay_key`
- `attributes.fail_reason_code` when `result=FAIL` or `result=UNKNOWN` (must match `reason_codes[0]`)

Status code rule: `OK` for `PASS`/`NOT_APPLICABLE` with reason; `ERROR` for `FAIL` and `UNKNOWN`.

7. VALIDATOR CONTRACT
------------------------------------------------------------------------------------------------------------------------
- `gate_verdict_schema_validator` (release-gate): structural verification per §5.
- `gate_unknown_handling_validator` (release-gate): UNKNOWN never maps to ALLOW.
- `gate_na_justification_validator` (release-gate): NOT_APPLICABLE always paired with non-empty `reason_codes`.
- `gate_presence_validator` (release-gate): every applicable gate per `00C.9` invocation map has a verdict.
- Per-gate validators (G01..G29) each live in their child file but receive the same release-gate scope.

8. NEGATIVE CONTROL CONTRACT
------------------------------------------------------------------------------------------------------------------------
Each `NC-GATE-*` listed in §4 has a target REQ_ID, tamper kind, expected validator, and `Expected Fail Reason` matching the row. The 4 cross-gate negative controls (`MISSING-FIELD`, `UNKNOWN-AS-PASS`, `NA-EMPTY`, `MISSING-VERDICT`) are mandatory at the parent level.

9. REPLAY CONTRACT
------------------------------------------------------------------------------------------------------------------------
Every gate verdict artifact MUST replay byte-identical for the same `(gate_id, request_id, policy_hash, blueprint_hash, replay_key, input)`. Allowed nondeterminism: only `span_id`, `trace_id` (which are run-scoped). Any field-level diff is release-blocking.

10. RELEASE GATE CONTRACT
------------------------------------------------------------------------------------------------------------------------
A 00C row's `Release Gate` is `PASS` only when:
- Gate verdict shape conforms to §5
- UNKNOWN never mapped to ALLOW
- NOT_APPLICABLE rows carry a justification
- The compiler `99.11` reports no anti-cheat finding for this gate
- The gate's negative control trips with the matching `Expected Fail Reason`

11. NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
**This file owns**: GateVerdict schema invariants and per-gate parent REQ_IDs.

**Related files own**: per-gate detail in `00C.1`..`00C.6`; the disposition matrix in `00C.7`; the gate observability/anti-bypass tests in `00C.8`; the gate-to-layer invocation map in `00C.9`.

**Forbidden duplicated ownership**: 00C MUST NOT define final dispositions (Exit X3); 00C MUST NOT issue certification (L5); 00C MUST NOT mutate L4 (UWG). 05/00A/00B MUST NOT redefine GateVerdict schema.

**Forbidden output vocabulary**: `ALLOW_FINISH`, `durable_write_committed`, `policy_certified`, `route_changed`, `workflow_expanded`, `evidence_contract_issued`, `prompt_envelope_constructed`, `learning_promoted`. 00C may emit `ALLOW`/`DENY`/`REROUTE_HINT`/`ESCALATE_HINT`/`BLOCK_COMMIT`/`NA` only inside a `GateVerdict.disposition` field — never as a top-level pack output.

12. CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- `00C.1_Runtime_Gates_G01_G05_Ingress_Identity_Intent_Safety_Risk.md` — `REQ-GATE-G01-*`..`REQ-GATE-G05-*`
- `00C.2_Runtime_Gates_G06_G10_HITL_Route_Retrieval_Evidence_Prompt.md` — `REQ-GATE-G06-*`..`REQ-GATE-G10-*`
- `00C.3_Runtime_Gates_G11_G15_Tool_Model_Args_Egress_Sandbox.md` — `REQ-GATE-G11-*`..`REQ-GATE-G15-*`
- `00C.4_Runtime_Gates_G16_G20_Memory_Privacy_Workflow_Loop_Budget.md` — `REQ-GATE-G16-*`..`REQ-GATE-G20-*`
- `00C.5_Runtime_Gates_G21_G24_Output_Security_Replay.md` — `REQ-GATE-G21-*`..`REQ-GATE-G24-*` (note: covers G21..G24)
- `00C.6_Runtime_Gates_G25_G29_Anomaly_Exit_Write_Audit_Learning_Firewall.md` — `REQ-GATE-G25-*`..`REQ-GATE-G29-*`
- `00C.7_Runtime_Gates_Verdict_Schema_Disposition_Matrix.md` — disposition-matrix REQ_IDs
- `00C.8_Runtime_Gates_Observability_Tests_and_Anti_Bypass.md` — anti-bypass / observability REQ_IDs
- `00C.9_RG_Layer_Integration_Invocation_Map.md` — gate-to-layer invocation map REQ_IDs

13. ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
- Every cross-gate invariant row in §4 has all 13 cells filled.
- Every G01..G29 has at least one parent-level row in §4 with non-blank evidence cells.
- The GateVerdict schema in §5 enumerates every required field and its allowed values.
- The OTEL span contract in §6 names `gate.<gate_id>` with required attributes.
- The 4 cross-gate negative controls in §8 are listed.
- The replay contract in §9 is byte-identical for fixed inputs.
- The release-gate rule in §10 is fail-closed.
- The no-overlap lock in §11 forbids cross-pack vocabulary leaks.

END OF 00C — RUNTIME GATES CURRENT-RUN MESH PARENT
========================================================================================================================
