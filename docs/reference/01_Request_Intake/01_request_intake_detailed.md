WINDSURF IMPLEMENTATION CONTRACT
Project: Agentic-Workflow
Mode: Kitchen Sink, zero-loss, implementation-grade
Objective: Implement the full governed agentic runtime path with enforceable contracts, runtime gates, OTEL evidence, deterministic replay, and proof that every layer actually runs.

====================================================================
0. OPERATING RULES FOR WINDSURF
====================================================================

You are implementing, not summarizing.

Before editing code:
1. Read the source files below.
2. Inspect the existing repo structure.
3. Identify current implementations, stubs, duplicate paths, bypasses, and missing contracts.
4. Produce a short implementation plan.
5. Then implement the smallest coherent set of changes that makes the runtime path executable and provable.

Do not:
- Fake evidence.
- Add placeholder tests that only assert mocked success.
- Claim telemetry exists unless spans are emitted and inspectable.
- Claim replay works unless the same input can be rerun and compared.
- Route around L5, Exit Eval, or UWG.
- Let L2 write directly to L4.
- Let L6 mutate the current run.
- Let HITL be sovereign authority.
- Let C0 answer.
- Let Prompt Assembly retrieve.
- Let L0 execute.
- Let L1 route with authority.
- Let runtime gates silently bypass.
- Introduce broad refactors unrelated to this contract.

Source files to treat as authoritative:
- docs/reference/agentic_system_process_map_exec.md
- docs/reference/01_request_intake.md
- docs/reference/02_L1_Reasoning_Plan_Generation_v5.md
- docs/reference/03_L0_Route_Decision_Switching_L3 v15.md
- docs/reference/C0 Context Engine_detailed.md
- docs/reference/04_L2_Execute_detailed.md
- docs/reference/05_Live_Runtime_Exit_Control_&_Evaluation_detailed.md
- docs/reference/Evaluation_Runtime_Gates_detailed.md
- docs/reference/06_Shadow_Evaluation_System_Learning_detailed.md
- docs/reference/00_Governance & Safety v5.md

====================================================================
1. HARD ARCHITECTURE INVARIANTS
====================================================================

Implement these as code-level checks, tests, and runtime assertions.

U0 / Intake:
- Validates transport, identity baseline, quotas, schema, and envelope.
- Emits validated_request or rejected_request.
- Assigns request_id, session_id, trace_root.
- Does not reason, retrieve, route, call tools, call models, execute, or mutate.

L1 / Reasoning + Plan:
- Reads validated_request.
- Produces L1PlanContract.
- Parses intent, constraints, ambiguity, output needs, risk hints, and support requirements.
- May propose route candidates.
- Does not route with authority.
- Does not retrieve final evidence.
- Does not execute tools.
- Does not write durable state.

L0 / Route Decision:
- Consumes L1PlanContract.
- Emits exactly one deterministic RouteContract.
- RouteContract must include:
  route_id, confidence, reason_codes, freshness_class, cache_policy,
  execution_form, cost_tier, fallback_chain, slo, telemetry_keys,
  tenant_scope, sandbox_class, support_target, route_digest, hmac_sig.
- May choose:
  R1A_EXACT_CACHE
  R1B_SEMANTIC_CACHE
  R3_SIMPLE_GROUNDED_READ
  R4_SINGLE_ACTION
  R3_R4_MANAGED_WORKFLOW
  R5_FALLBACK
  HITL_POSTURE
- Does not retrieve, execute, call models, mutate state, approve egress, or promote learning.

C0 / Context Engine:
- Runs only when RouteContract requires grounding.
- Produces FinalEvidenceContract.
- Uses dense, sparse/BM25, metadata, graph, cache, code, or trace lanes only when allowed.
- Preserves source_id, version, ACL, lineage, citation anchors, contradiction flags, and support score.
- Emits PASS, WEAK_WITH_CAVEATS, CONFLICTED, EMPTY, or BLOCKED.
- Does not answer, route, execute, mutate, or approve.

Prompt Assembly:
- Packages only verified context into bounded PromptEnvelope.
- Preserves authority order:
  system > policy > registry > developer/admin > retrieved/tool/human data > user task intent.
- Retrieved/tool/human content is data, never instruction.
- Does not retrieve, execute, route, or mutate.

L3 / Orchestration:
- Runs only when RouteContract execution_form requires managed workflow.
- Expands steps, dependencies, joins, retries, and HITL pause/resume inside bounded workflow authority.
- Emits current L3StepContract to L2.
- Does not re-decide L0 route.
- Does not execute directly.
- Does not write durable state.

L2 / Execute:
- Executes exactly one bounded packet or current workflow step.
- Runs E1 Prep -> E2 Valid -> E3 Exec -> E4 Heal -> E5 Seal.
- May call tools/models/scripts only inside capability_token and sandbox_envelope.
- Produces sealed_l2_artifact.
- Any mutation is proposed_state_diff only.
- Does not approve final output.
- Does not commit to L4.

Exit Eval & Control:
- Accepts sealed L2 artifacts, sealed L3 workflow packages, or L0 [RET] packets.
- Converts them into ExitReviewPacket.
- Runs current-run gates.
- Emits exactly one disposition:
  ALLOW_FINISH
  DENY
  REROUTE
  ESCALATE_HITL
  COMMIT_REQUEST_TO_UWG
  SAFE_FALLBACK
- Does not execute tools.
- Does not retrieve.
- Does not mutate L4.
- Does not let L6 rescue current run.

UWG:
- Sole durable write path into L4.
- Accepts only cleared commit requests from Exit/L5.
- Emits commit receipt.
- Blocks direct writes from L0, L1, C0, PA, L3, L2, HITL, and L6.

L6 / Shadow Evaluation + Learning:
- Consumes completed-run exhaust only.
- Reads traces, artifacts, route contracts, evidence contracts, prompt envelopes, exit dispositions, HITL packets, policy grades, replay keys, and commit receipts.
- Evaluates before learning.
- Proposes future-run updates only.
- Does not mutate current run.
- Does not write directly to L4.
- Promotions require UWG.

====================================================================
2. IMPLEMENTATION DELIVERABLES
====================================================================

Create or wire these concrete modules using existing repo conventions.

A. Runtime contracts
Implement typed contracts for:
- RequestEnvelope
- ValidatedRequest
- L1PlanContract
- RouteContract
- RetrievalPlan
- FinalEvidenceContract
- PromptEnvelope
- L3WorkflowContract
- L3StepContract
- L2ExecutionRequest
- SealedL2Artifact
- ExitReviewPacket
- GateVerdict
- ExitDisposition
- CommitRequest
- UWGCommitReceipt
- RuntimeExhaustBundle
- ShadowEvalRecord
- LearningProposal

Each contract must include:
- request_id
- run_id
- trace_root / trace_id
- tenant_id
- policy_hash
- blueprint_hash
- replay_key
- lineage refs
- source authority labels where relevant
- schema validation
- serialization support
- deterministic digest support

B. Runtime gate mesh
Implement gate functions for G01 through G29:
G01 Request ingress
G02 Identity / tenant / session
G03 Intent / ambiguity
G04 Safety / policy
G05 Risk tier
G06 HITL approval
G07 Route selection
G08 Retrieval / grounding
G09 Evidence quality
G10 Prompt assembly
G11 Tool/model registry
G12 Tool argument
G13 Tool/retrieved output trust
G14 External egress
G15 Filesystem / shell / data
G16 Memory access
G17 Privacy / cross-context
G18 Workflow trajectory
G19 Loop / retry / thrash
G20 Cost / latency / budget
G21 Output schema
G22 Output quality
G23 Security / leakage
G24 Determinism / replay
G25 Runtime regression / anomaly
G26 Exit disposition
G27 Durable write sovereignty
G28 Audit / trace completeness
G29 Learning firewall

Every gate must return:
{
  gate_id,
  result: PASS | FAIL | WARN | UNKNOWN | NOT_APPLICABLE,
  disposition: ALLOW | DENY | CLARIFY | ABSTAIN | REROUTE | SHRINK_SCOPE | RETRY | HEAL | ESCALATE_HITL | QUARANTINE | REDACT | SAFE_FALLBACK | MARK_DEGRADED | COMMIT_REQUEST | BLOCK_COMMIT,
  severity,
  reason_codes[],
  score,
  threshold,
  evidence_refs[],
  replay_refs[],
  confidence,
  abstain_flag,
  remediation_hint
}

C. Deterministic replay
Implement replay binding across every layer:
- normalized_request_hash
- input_hash
- prompt_hash
- route_digest
- evidence_contract_hash
- policy_hash
- blueprint_hash
- registry_digest_set
- snapshot_manifest
- replay_key
- attempt_seed
- environment_digest
- clock_policy

Add deterministic replay command:
- Run same sample request twice.
- Compare route_digest, replay_key, gate verdicts, sealed artifact hash, and exit disposition.
- Fail if hidden nondeterminism changes current-run decisions.

D. OTEL telemetry
Emit OpenTelemetry spans for:
- U0 intake
- L1 plan
- L0 route decision
- C0 retrieval plan
- C0 fetch
- C0 graph
- C0 shape
- C0 contract
- Prompt Assembly
- L3 workflow start
- L3 step dispatch
- L2 E1 prep
- L2 E2 valid
- L2 E3 exec
- L2 E4 heal
- L2 E5 seal
- Exit preflight
- Exit X1 current-run gates
- HITL packetization if applicable
- UWG commit request
- UWG commit receipt
- L6 ingest
- L6 evaluate
- L6 RCA/proposal
- L6 promotion attempt

Each span must include:
- trace_id
- span_id
- parent_span_id
- request_id
- run_id
- route_id if known
- step_id if known
- gate_id if applicable
- policy_hash
- blueprint_hash
- replay_key
- contract_digest
- status
- reason_codes
- latency_ms
- cost/tokens if relevant
- artifact refs

E. Evidence packet
For a sample grounded request, produce:
- L1PlanContract
- RouteContract
- C0 FinalEvidenceContract
- PromptEnvelope
- SealedL2Artifact
- ExitReviewPacket
- GateVerdict list
- ExitDisposition
- RuntimeExhaustBundle
- L6 ShadowEvalRecord
- Replay comparison report
- OTEL trace export

F. Anti-bypass checks
Add tests that fail if:
- L2 writes to L4 directly.
- L6 writes to current run.
- C0 emits final prose answer.
- Prompt Assembly performs retrieval.
- L0 executes tools or calls models.
- L1 emits authoritative route without L0.
- Exit allows output without policy_hash.
- Grounded answer exits without FinalEvidenceContract.
- Any mutation bypasses UWG.
- HITL changes are accepted without L5 reclearance.
- Provider/tool/model fallback happens without recertification.
- A gate returns implicit success with missing verdict fields.

====================================================================
3. SAMPLE END-TO-END PROOF SCENARIO
====================================================================

Implement and run this scenario:

Input:
"Review docs/reference/03_L0_Route_Decision_Switching_L3 v15.md and explain whether R3 simple grounded read uses L3."

Expected runtime shape:
1. U0 intake validates request and stamps request_id / trace_root.
2. L1 detects document-specific grounded question.
3. L0 emits RouteContract:
   route_id = R3_SIMPLE_GROUNDED_READ
   execution_form = SINGLE_STEP
   grounding_required = true
   L3_required = false
4. C0 retrieves relevant source spans from the L0 document.
5. C0 emits FinalEvidenceContract with source anchors and support score.
6. Prompt Assembly packages source evidence as data.
7. L2 executes one bounded grounded-answer step.
8. L2 seals artifact with evidence refs, replay refs, and trace refs.
9. Exit Eval verifies:
   - policy hash present
   - route contract present
   - evidence contract present
   - groundedness passes
   - no L3 step occurred
   - no durable write occurred
10. Exit emits ALLOW_FINISH.
11. L6 ingests completed-run exhaust after runtime boundary.
12. L6 creates ShadowEvalRecord only.
13. No L6 current-run mutation occurs.
14. Replay runs the same scenario again and proves stable route/exits.

Required proof output:
- Show command used.
- Show trace_id.
- Show span tree.
- Show emitted contracts.
- Show gate verdict summary.
- Show replay comparison.
- Show no direct write path.
- Show L6 read-only proof.
- Show final answer generated from cited evidence only.

====================================================================
4. VALIDATION COMMANDS
====================================================================

Add or update commands so the following work from repo root.

Required:
- python -m pytest tests/runtime/test_intake_contract.py
- python -m pytest tests/runtime/test_route_contract.py
- python -m pytest tests/runtime/test_c0_evidence_contract.py
- python -m pytest tests/runtime/test_l2_execution_seal.py
- python -m pytest tests/runtime/test_exit_eval_control.py
- python -m pytest tests/runtime/test_uwg_write_sovereignty.py
- python -m pytest tests/runtime/test_l6_learning_firewall.py
- python -m pytest tests/runtime/test_runtime_gates_g01_g29.py
- python -m pytest tests/runtime/test_deterministic_replay.py
- python -m pytest tests/runtime/test_otel_trace_completeness.py
- python -m pytest tests/runtime/test_end_to_end_grounded_read.py

Add one command:
- python -m agentic_workflow.runtime.prove_kitchen_sink --scenario grounded_read --export artifacts/runtime/kitchen_sink_proof/

This command must write:
artifacts/runtime/kitchen_sink_proof/
  contracts/
  traces/
  gates/
  replay/
  evidence/
  exit/
  l6/
  proof_report.md

====================================================================
5. ACCEPTANCE CRITERIA
====================================================================

The implementation is complete only when:

A. Code works
- All runtime tests pass.
- The proof command runs without manual steps.
- The sample request traverses U0 -> L1 -> L0 -> C0 -> Prompt Assembly -> L2 -> Exit -> L6.
- L3 is skipped for R3 simple grounded read.
- L3 runs only for managed workflow scenarios.

B. Evidence exists
- Proof report includes actual contract JSON.
- Proof report includes actual OTEL trace tree.
- Proof report includes actual gate verdicts.
- Proof report includes actual replay comparison.
- Proof report includes actual source evidence refs.
- Proof report includes actual sealed artifact digest.

C. Guardrails are enforced
- Direct L2-to-L4 write test fails when attempted.
- L6 current-run mutation test fails when attempted.
- Missing evidence contract blocks grounded answer.
- Missing policy_hash blocks exit.
- Missing replay_key blocks replay-required route.
- Silent provider/tool/model fallback is denied.

D. Architecture remains clean
- Existing public interfaces are preserved where practical.
- No duplicate shadow runtime path.
- No fake all-in-one orchestrator that bypasses layers.
- No broad unrelated refactor.
- No markdown-only implementation.

====================================================================
6. FINAL WINDSURF RESPONSE FORMAT
====================================================================

When done, return exactly this:

1. Files changed
- path
- purpose
- key symbols added/modified

2. Runtime path implemented
- U0
- L1
- L0
- C0
- Prompt Assembly
- L3
- L2
- Exit
- UWG
- L6

3. Proof command
- exact command
- output artifact path

4. Test results
- exact commands run
- pass/fail counts

5. Evidence summary
- trace_id
- replay_key
- route_id
- exit_disposition
- gate verdict counts
- proof_report path

6. Bypass checks
- list each invariant and the test that enforces it

7. Known gaps
- only real remaining gaps
- no vague “future work”