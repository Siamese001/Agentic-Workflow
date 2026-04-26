========================================================================================================================
00C_RUNTIME_GATES_CURRENT_RUN_MESH_DETAILED.md
PARENT RUNTIME GATES CURRENT-RUN CONTROL MESH
MECE FULL OVERWRITE
========================================================================================================================

PURPOSE
------------------------------------------------------------------------------------------------------------------------
This parent file defines Runtime Gates as a cross-cutting current-run control mesh.

Runtime Gates decide whether a specific live packet, request, route, retrieval packet, prompt packet, tool call,
workflow step, model invocation, output, escalation, or write proposal is allowed to continue inside the CURRENT RUN.

Runtime Gates are not a sequential layer. They are a 00C foundation folder because they operate across U0, L1, L0, C0,
Prompt Assembly, L3, L2, Exit, UWG/L4, and the L6 learning firewall.

PARENT ROLE
------------------------------------------------------------------------------------------------------------------------
- Define the G01-G29 runtime gate mesh at doctrine level.
- Define the canonical GateVerdict contract.
- Define the allowed bounded runtime dispositions emitted by gates.
- Define the no-overlap boundary with L5, L4/UWG, Exit, L2, C0, Prompt Assembly, L0/L3, L1, U0, and L6.
- Define child ownership map.
- Define implementation acceptance criteria and proof commands.

PARENT DOES NOT OWN IMPLEMENTATION DETAIL
------------------------------------------------------------------------------------------------------------------------
The child files own implementation-grade gate mechanics. This parent is the map, vocabulary, and authority boundary.

SOURCE OWNERSHIP BOUNDARY
------------------------------------------------------------------------------------------------------------------------
Runtime Gates own current-run gate verdict requirements only.

Runtime Gates do not own:
- U0 envelope construction or request identity stamping;
- L1 intent interpretation or plan construction;
- L0 route selection authority;
- C0 retrieval and evidence-contract construction;
- Prompt Assembly slot construction;
- L3 workflow expansion;
- L2 execution, PTC sandbox execution, local repair, or artifact sealing;
- Exit's final X3 disposition;
- L5 certification evidence;
- UWG durable write admission;
- L4 durable state;
- L6 completed-run evaluation, RCA, or future-run learning promotion.

Runtime Gates feed Exit, L5, L2, L3, C0, Prompt Assembly, L0, L1, U0, UWG, and L6 with structured verdict evidence.
Those surfaces consume the verdicts inside their own authority boundaries.

GLOBAL NO-OVERLAP LOCK
------------------------------------------------------------------------------------------------------------------------
- U0 / Intake owns request envelope validation and request identity stamping.
- L1 owns intent interpretation, task_spec, query_spec, ambiguity register, and plan recommendation.
- L0 owns route selection and RouteContract authority.
- C0 owns evidence retrieval, shaping, verification, support score, and FinalEvidenceContract.
- Prompt Assembly owns signed provider-ready PromptEnvelope / CompiledPromptArtifact construction.
- L3 owns managed workflow shaping, DAG state, readiness, joins, retries, and bounded orchestration.
- L2 owns bounded execution, PTC sandbox execution, local repair, and sealed artifacts.
- Runtime Gates own G01-G29 current-run gate verdict requirements only.
- Exit Eval owns aggregate current-run disposition and X3 outcome selection.
- L5 owns policy, authority, origin-trust, egress, HITL re-clearance, replay/audit certification evidence.
- UWG owns durable write admission.
- L4 owns durable system-of-record state.
- L6 owns completed-run evaluation, RCA, proposal, and future-run learning promotion attempts.


FORBIDDEN OUTPUTS FROM THIS FOLDER
------------------------------------------------------------------------------------------------------------------------
Runtime Gates may emit GateVerdict records and recommended bounded dispositions. Runtime Gates must not:
- route with L0 authority;
- retrieve or score final evidence as C0;
- assemble prompts;
- execute tools, models, scripts, or PTC payloads;
- orchestrate workflow steps;
- approve final response release;
- commit durable state;
- certify L5 evidence as its own output;
- promote learning or mutate future-run surfaces;
- silently bypass, silently pass UNKNOWN, or expand its own authority.


CHILD FILE MAP
------------------------------------------------------------------------------------------------------------------------
- 00C.1_Runtime_Gates_G01_G05_Ingress_Identity_Intent_Safety_Risk_detailed.md
  Owns G01-G05 only: ingress, identity, intent, safety/policy, and risk-tier gate requirements.

- 00C.2_Runtime_Gates_G06_G10_HITL_Route_Retrieval_Evidence_Prompt_detailed.md
  Owns G06-G10 only: HITL, route selection, retrieval/grounding, evidence quality, prompt assembly gate requirements.

- 00C.3_Runtime_Gates_G11_G15_Tool_Model_Args_Egress_Sandbox_detailed.md
  Owns G11-G15 only: tool/model registry, tool args, tool/retrieved output trust, egress, fs/shell/data access.

- 00C.4_Runtime_Gates_G16_G20_Memory_Privacy_Workflow_Loop_Budget_detailed.md
  Owns G16-G20 only: memory access, privacy/cross-context, workflow trajectory, loop/retry/thrash, budget/SLO.

- 00C.5_Runtime_Gates_G21_G24_Output_Security_Replay_detailed.md
  Owns G21-G24 only: output schema, output quality, security/leakage, determinism/replay.

- 00C.6_Runtime_Gates_G25_G29_Anomaly_Exit_Write_Audit_Learning_Firewall_detailed.md
  Owns G25-G29 only: runtime anomaly, Exit-disposition eligibility, durable-write sovereignty, audit/trace completeness, learning firewall.

- 00C.7_Runtime_Gates_Verdict_Schema_Disposition_Matrix_detailed.md
  Owns canonical GateVerdict schema, result/disposition vocabularies, aggregation handoff semantics, and how gate verdicts flow to Exit.

- 00C.8_Runtime_Gates_Observability_Tests_and_Anti_Bypass_detailed.md
  Owns OTEL span names, proof commands, anti-bypass tests, acceptance criteria, and runtime-vs-CI/CD separation tests.

CANONICAL CURRENT-RUN DISPOSITION VOCABULARY
------------------------------------------------------------------------------------------------------------------------
Every runtime gate may recommend one bounded disposition:
- ALLOW
- DENY
- CLARIFY
- ABSTAIN
- REROUTE
- SHRINK_SCOPE
- RETRY
- HEAL
- ESCALATE_HITL
- QUARANTINE
- REDACT
- SAFE_FALLBACK
- MARK_DEGRADED
- COMMIT_REQUEST
- BLOCK_COMMIT

Hard invariant:
- A gate disposition is a bounded recommendation/verdict.
- Exit owns final X3 disposition.
- UWG owns durable mutation admission.
- No runtime gate may silently bypass, mutate durable state, or expand its own authority.

CANONICAL GATE VERDICT CONTRACT
------------------------------------------------------------------------------------------------------------------------
GateVerdict {
  gate_id: G01..G29,
  gate_family,
  gate_surface,
  primary_layer,
  evaluated_packet_ref,
  request_id,
  run_id,
  trace_root,
  trace_id,
  tenant_id,
  policy_hash,
  blueprint_hash,
  replay_key,
  result: PASS | FAIL | WARN | UNKNOWN | NOT_APPLICABLE,
  disposition: ALLOW | DENY | CLARIFY | ABSTAIN | REROUTE | SHRINK_SCOPE | RETRY | HEAL |
               ESCALATE_HITL | QUARANTINE | REDACT | SAFE_FALLBACK | MARK_DEGRADED |
               COMMIT_REQUEST | BLOCK_COMMIT,
  severity: INFO | LOW | MEDIUM | HIGH | CRITICAL,
  reason_codes: string[],
  score,
  threshold,
  grader_type: code | LLM_JUDGE | hybrid | human_calibrated | policy_rule,
  evidence_refs: string[],
  replay_refs: string[],
  source_lineage_refs: string[],
  confidence,
  abstain_flag,
  remediation_hint,
  deterministic_digest,
  created_at_run_offset,
  schema_version
}

Hard rules:
- UNKNOWN is never converted to PASS.
- WARN may continue only where policy permits and must remain visible to Exit.
- GateVerdict is evidence for Exit and audit. It is not the final ExitDisposition.
- COMMIT_REQUEST means submit proposed mutation to UWG only. It is not a write.


TOP-LEVEL FLOW
------------------------------------------------------------------------------------------------------------------------
U0 Intake emits a validated request or rejection.
L1 emits a plan and support/action expectations.
L0 emits exactly one RouteContract.
C0, Prompt Assembly, L3, and L2 produce governed packets and sealed artifacts.
Runtime Gates evaluate each live packet at its appropriate surface.
Exit consumes gate verdicts and emits exactly one X3 disposition.
UWG accepts only cleared commit requests from Exit.
L6 consumes sealed exhaust after runtime boundary only.

ASCII CONTROL VIEW
------------------------------------------------------------------------------------------------------------------------
[U0] -> G01/G02/G03/G04
  -> [L1] -> G03/G04/G05/G18
  -> [L0] -> G07/G08/G20
  -> [C0] -> G08/G09/G13/G16/G17/G23
  -> [PA] -> G10/G13/G17/G23
  -> [L3] -> G18/G19/G20/G25
  -> [L2] -> G11/G12/G14/G15/G21/G24
  -> [EXIT] -> G22/G23/G26/G28 + aggregate all prior verdicts
  -> [UWG/L4 if commit] -> G27
  -> [L6 after runtime] -> G25 evidence + G29 firewall

IMPLEMENTATION ACCEPTANCE CRITERIA
------------------------------------------------------------------------------------------------------------------------
This 00C folder is complete only when:
- Each G01-G29 gate has a typed evaluator, deterministic input contract, and GateVerdict output.
- Every gate can return PASS / FAIL / WARN / UNKNOWN / NOT_APPLICABLE.
- UNKNOWN never becomes PASS.
- Every gate emits reason_codes, evidence_refs, replay_refs, confidence, threshold, and remediation_hint.
- Gate verdicts are visible to Exit and L6 exhaust.
- Gates do not duplicate owner-layer implementation details.
- Runtime regression protection is implemented as live anomaly containment only.
- CI/CD promotion gates remain out of scope.
- Anti-bypass tests prove no layer can skip required gates.

PROOF COMMANDS EXPECTED FROM WINDSURF
------------------------------------------------------------------------------------------------------------------------
- python -m pytest tests/runtime_gates -q
- python -m pytest tests/runtime_gates/test_gate_verdict_schema.py -q
- python -m pytest tests/runtime_gates/test_gate_mesh_no_bypass.py -q
- python -m pytest tests/runtime_gates/test_runtime_vs_cicd_regression_boundary.py -q
- python -m pytest tests/runtime_gates/test_gate_otel_trace_coverage.py -q

========================================================================================================================
END 00C_RUNTIME_GATES_CURRENT_RUN_MESH_DETAILED.md
========================================================================================================================
