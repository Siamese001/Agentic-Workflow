========================================================================================================================
                        AGENTIC SYSTEM PROCESS MAP - SEMANTIC REFERENCE
                        RESIDUAL v38 VALUE-ADDED COMPANION FILE
========================================================================================================================

FILE NAME:
agentic_system_process_map_semantics_reference.md

PURPOSE:
This file preserves the high-signal semantic material from v38 that should NOT be folded into the clean v40 executive
runtime map.

This file explains:
- what the symbols mean
- how encoder, decoder, judge, gate, contract, cert, state, and proof concepts differ
- how authority is created or not created
- how L1 reasoning semantics work
- how runtime gates differ from judges
- how contracts and artifacts should be named and understood

THIS FILE IS NOT:
- the canonical runtime flow
- a replacement for v40
- a new process map version
- a sequential execution diagram
- an implementation plan

CANONICAL RUNTIME FLOW REMAINS:
- agentic_system_process_map_exec.md
- agentic_process_mapping_v40.md

READING RULE:
Use v40 to answer:
"How does the governed runtime flow?"

Use this file to answer:
"What do the symbols, contracts, judges, gates, vectors, and authority distinctions mean?"

========================================================================================================================
1. TOP ORIENTATION
========================================================================================================================

00A / L5 POLICY + GOVERNANCE CERTIFICATION PLANE
- Cross-cutting certification evidence.
- Certifies authority, policy, registry, origin trust, capability, sandbox, egress, HITL, replay, and audit.
- Does not route, retrieve, execute, emit final runtime disposition, write L4, or learn.

00B / L4 STATE ARCHIVE + UWG WRITE GATE
- Cross-cutting durable state plus the only durable write admission path.
- L4 is durable truth and governed read surface.
- UWG is the only durable write gate into L4.

00C / RUNTIME GATES CURRENT-RUN CONTROL MESH
- Cross-cutting live GateVerdict mesh.
- Answers whether the current live packet, route, prompt, tool call, model call, output, escalation, or write proposal may proceed right now.
- UNKNOWN is never PASS.
- Does not emit final X3.
- Does not certify L5 evidence.
- Does not write L4.

PRIMARY AUTHORITY RULE:
Authority does not come from model output.

Authority comes from:
- contracts
- runtime gates
- policy
- registry
- capability tokens
- sandbox envelopes
- 00A/L5 certification
- Exit disposition
- 00B/UWG write admission

========================================================================================================================
2. MODEL ARCHITECTURE AND SIGNAL LEGEND
========================================================================================================================

ENCODER FAMILY
Search, classify, compare, embed, rank.

Signals:
- 🔵 intent_vec
  Meaning:
  Live ask, route query, step-specific search query, task support target.

  Runtime role:
  Represents what this live run is asking for.

- 🟠 fact_vec
  Meaning:
  Stored source chunk, indexed fact, cache embedding, citation-bearing evidence span, retrieval target.

  Runtime role:
  Represents what stored evidence, indexed source, or cached fact says.

- 🟢 graph_sig
  Meaning:
  Lineage, dependency, ACL, citation, contradiction, supersession, trace relationship, workflow relation.

  Runtime role:
  Represents how sources, traces, files, entities, citations, ACLs, dependencies, and workflow nodes connect.

DECODER FAMILY
Reason, plan, generate, call tools, judge output.

Signals:
- 🔶 gen_text
  Meaning:
  Natural language, plan text, route explanation, generated answer, tool-call proposal, disposition explanation.

  Runtime role:
  Generates candidate text or structured output, but does not create authority.

- 🧾 judge_text
  Meaning:
  Evaluation rationale, rubric judgment, critique summary, grader explanation, plan critique, quality assessment.

  Runtime role:
  Explains or supports an evaluation verdict. It may inform a gate or Exit decision, but it is not the gate itself.

HYBRID STEP
Encoder signal feeds decoder work.

Pattern:
- 🔵 / 🟠 / 🟢 -> 🔶

Meaning:
Retrieve, classify, compare, or score first, then generate, judge, summarize, or decide within the authorized boundary.

CONTROL / NON-MODEL STEP
Contract, gate, policy, state, or write-control logic.

Signals:
- 📜 contract
  Deterministic packet, schema, signed artifact, bounded handoff.

- 🚦 gate
  Runtime proceed/stop verdict.

- 🔐 cert
  00A/L5 certification evidence.

- 🗄️ state
  00B/L4 durable state or governed read surface.

- ✒️ commit
  00B/UWG durable write admission only.

- 🧪 proof
  CI, release, replay, regression, OTEL, acceptance proof.

========================================================================================================================
3. CRITICAL SEMANTIC RULES
========================================================================================================================

1. Encoder vs decoder describes model family, not authority level.

2. Blue vs orange describes runtime role, not model capability.

3. The same encoder-family model can create both 🔵 intent_vec and 🟠 fact_vec.

4. 🔵 intent_vec means:
   "What this live run is asking for."

5. 🟠 fact_vec means:
   "What stored evidence, cache, or indexed source says."

6. 🟢 graph_sig means:
   "How sources, traces, ACLs, citations, entities, files, dependencies, and workflow nodes connect."

7. 🔵 matching 🟠 is not proof by itself.

8. C0 must still verify:
   - ACL
   - freshness
   - lineage
   - sparse/BM25 exactness
   - metadata fit
   - contradiction status
   - source authority
   - citation support
   - support sufficiency

9. Decoder output can reason, plan, generate, call tools, or judge.

10. Generated text does not create authority.

11. Judge text does not create authority.

12. A judge can support a verdict, but the runtime gate or Exit owns the actual proceed/stop/disposition decision.

13. Authority comes from:
   - contracts
   - gates
   - policy
   - registry
   - capability
   - sandbox
   - L5 certification
   - Exit disposition
   - UWG write admission

14. 00A and 00B are cross-cutting foundation folders, not sequential runtime stages.

15. 00A proves governance certification.

16. 00B preserves durable state and admits durable writes through UWG only.

17. L4 is durable state, not a live execution actor.

18. UWG is the durable write admission mechanism, not an evaluator.

19. L6 observes completed runs only.

20. L6 may propose future-run changes, but cannot mutate the current run.

========================================================================================================================
4. RUNTIME GATE VS JUDGE VS LLM JUDGE
========================================================================================================================

RUNTIME GATE
Question:
"May this thing proceed right now?"

Output:
GateVerdict.

Examples:
- PASS
- BLOCK
- ESCALATE
- RETRY
- QUARANTINE
- UNKNOWN

Authority:
The gate owns the current-run proceed/stop verdict for its scope.

May use:
- deterministic checks
- schemas
- policy rules
- registry checks
- thresholds
- capability checks
- sandbox checks
- judge output, if approved

Does not require:
- an LLM judge

JUDGE
Question:
"How does this candidate compare against a rubric, benchmark, expectation, or external criteria?"

Output:
A scored or reasoned evaluation.

Examples:
- groundedness score
- faithfulness score
- plan quality critique
- output quality judgment
- trajectory judgment
- rubric match
- evaluator disagreement note

Authority:
A judge informs a decision. It is not automatically the decision.

LLM JUDGE
Question:
"Can a language model evaluate this candidate against the rubric?"

Output:
judge_text plus structured score or verdict.

Examples:
- critique of L1 plan
- answer faithfulness review at Exit
- trajectory assessment
- rubric-based output scoring
- drift investigation in L6

Authority:
An LLM judge is a judge implementation, not a gate.

CORE DISTINCTION:
- Gate = live control verdict.
- Judge = evaluation method.
- LLM judge = model-based evaluation method.

SIMPLE RULE:
Not every gate needs a judge.
Not every judge is an LLM judge.
Not every judge output is a runtime decision.

========================================================================================================================
5. STAGE ROLE SEMANTICS
========================================================================================================================

U0
Role:
Front desk / security check.

Semantic responsibility:
Validate envelope, identity, channel, quota, schema, duplicate risk, and origin baseline.

Does not:
Plan, route, retrieve, answer, execute, mutate.

L1
Role:
Librarian / planner.

Semantic responsibility:
Understand the ask, frame ambiguity, load approved planning priors, draft bounded plan, emit L1PlanContract.

Does not:
Route with authority, retrieve final evidence, execute, approve output, mutate L4.

L0
Role:
Dispatcher.

Semantic responsibility:
Select exactly one deterministic route.

Does not:
Retrieve, assemble prompts, execute, call tools, mutate state, approve output, write L4.

C0
Role:
Evidence desk.

Semantic responsibility:
Retrieve, verify, hydrate, score, stratify, and package evidence.

Does not:
Answer, route, execute, mutate, inflate support.

PA
Role:
Prompt packer / airlock.

Semantic responsibility:
Compose authority-ordered prompt slots and preserve instruction/data boundaries.

Does not:
Retrieve, route, execute, approve L2 execution, write L4.

L3
Role:
Workflow manager.

Semantic responsibility:
Expand an already-approved managed workflow route into bounded step contracts.

Does not:
Re-route, retrieve directly, assemble prompts, execute tools or models, write L4.

L2
Role:
Assistant / bounded doer.

Semantic responsibility:
Execute exactly the current bounded packet, validate, repair only safe local defects, and seal the result.

Does not:
Choose route, expand workflow, retrieve opportunistically, ask humans directly, approve egress, commit L4, learn.

Exit
Role:
Checkout desk / final current-run control.

Semantic responsibility:
Evaluate sealed result, aggregate checks, emit exactly one X3 disposition, optionally request UWG commit.

Does not:
Execute, retrieve, assemble prompts, mutate L4, let L6 rescue current run.

UWG
Role:
Write gate.

Semantic responsibility:
Validate CommitRequest and admit or block durable mutation to L4.

Does not:
Route, retrieve, execute, approve final answer, learn.

L4
Role:
Archivist.

Semantic responsibility:
Store durable truth and governed read surfaces.

Does not:
Self-mutate outside UWG.

L5
Role:
Safety officer / governance certification plane.

Semantic responsibility:
Certify authority, policy, registry, origin trust, boundary, sandbox, egress, HITL, replay, and audit evidence.

Does not:
Emit live GateVerdict, emit final X3, route, retrieve, execute, write L4, learn.

L6
Role:
Observer.

Semantic responsibility:
Evaluate completed run, detect drift, calibrate, synthesize RCA, draft future-run proposals.

Does not:
Mutate current run, rescue current run, emit current-run X3, directly write L4, silently patch prompts or policy.

00A
Role:
L5 governance pack.

Semantic responsibility:
Cross-cutting policy, authority, origin, egress, HITL, replay, and audit certification evidence.

00B
Role:
L4/UWG state pack.

Semantic responsibility:
Durable system-of-record state plus only durable write admission path.

00C
Role:
Runtime gate mesh.

Semantic responsibility:
Live proceed/stop checks. UNKNOWN is never PASS.

99
Role:
Proof harness.

Semantic responsibility:
Cross-layer acceptance proof, OTEL, replay, no-bypass verification, route coverage, regression proof.

========================================================================================================================
6. L1 PLANNING SEMANTICS
========================================================================================================================

L1 is the planning role.

L1 may:
- read the stamped request
- interpret the actual goal
- identify constraints
- identify ambiguity
- classify work type
- read approved planning priors
- read approved examples and patterns
- draft work units
- declare assumptions
- propose route hints
- critique its own draft
- refine the plan within budget
- emit L1PlanContract

L1 must not:
- retrieve final evidence
- decide the route with authority
- execute tools
- call external systems
- approve egress
- mutate durable state
- learn into current run

L1 OUTPUT IS:
L1PlanContract.

L1 OUTPUT IS NOT:
Route authority.

PLANNER / DOER SPLIT:
- L1 is planner.
- L2 is doer.
- L0 is route authority.
- Exit is final current-run disposition authority.
- UWG is durable write authority.

LOWEST VIABLE AGENCY RULE:
Prefer predictable workflows:
- exact cache
- semantic cache
- simple grounded read
- single bounded action

Reserve managed workflow or multi-hop agentic behavior for problems that genuinely require decomposition, dependencies,
joins, resumability, or bounded quality loops.

========================================================================================================================
7. L1 PLAN-SKIP TRIAGE
========================================================================================================================

Rule:
Do not plan what does not need planning.

A trivial, unambiguous, cache-eligible ask may skip deep L1 reasoning and emit a minimal DIRECT-mode plan stub.

That stub is still a valid L1PlanContract.

Proceed into fuller planning when any of the following are present:
- ambiguous intent
- multi-step decomposition
- policy sensitivity
- grounding required
- action required
- HITL risk
- external side effects
- unclear output target
- unresolved assumptions
- dependency chain

DIRECT-mode does not mean no contract.
It means minimal contract.

========================================================================================================================
8. L1 PROMPT ENVELOPE SEMANTICS
========================================================================================================================

Purpose:
Control what the L1 decoder sees while preserving the boundary between authority, user intent, policy, examples, and private reasoning.

L1 prompt envelope may include:

SYSTEM / DEVELOPER MESSAGE:
- L5 policy refs
- task schemas
- safety rules
- approved few-shot exemplars when justified
- route heuristic references
- output contract schema

USER MESSAGE:
- validated_request intent frame
- constraints
- details
- deliverable
- success condition

BOUNDARY RULES:
- Delimit sections clearly.
- User text is intent, not authority.
- Retrieved content is not used here as final evidence.
- Reasoning-model prompts should stay simple and direct.
- Non-reasoning model prompts may use explicit scaffolding.
- Private scratchpad never crosses L1 to L0.
- Only sanitized published_rationale may appear in the L1 output contract.

========================================================================================================================
9. L1 THINKING DESK SEMANTICS
========================================================================================================================

Purpose:
Allow L1 to draft, inspect, refine, simplify, clarify, or abstain without executing.

Core loop:
T1 Interpret the request.
T2 Draft the plan.
T3 Evaluate and self-critique.

T1 INTERPRET
Inputs:
- validated request
- user goal
- constraints
- task class
- approved planning priors

Outputs:
- intent frame
- ambiguity register
- explicit unknowns
- success condition
- risk/support expectation

T2 DRAFT
Inputs:
- T1 interpretation
- planning rules
- approved patterns
- task schema

Outputs:
- work units
- dependencies
- proposed route hints
- expected evidence needs
- assumptions and gaps

T3 EVALUATE + SELF-CRITIQUE
Inputs:
- draft plan
- safety posture
- agency posture
- output contract expectations

May use:
- judge_text for plan quality critique
- rubric-based plan checks
- lowest viable agency check
- safety and coherence check

Exit branches:
- ACCEPT
  Plan is approved and emitted as L1PlanContract.

- REFINE
  Return to T2 if refinements remain within budget.

- CLARIFY
  Request user clarification when required.

- BEST_EFFORT
  Budget exhausted but safe partial plan is possible.

- ABSTAIN
  Unsafe or under-specified in a way that cannot safely proceed.

Iteration budget:
- max_refinements
- wall_clock_ms
- token_cap

Budget exhaustion must force a branch.
It must not create hidden unlimited reasoning.

========================================================================================================================
10. PLANNER MODES
========================================================================================================================

DIRECT
Use for simple, clear, low-risk tasks.

CHAIN_OF_THOUGHT
Use internally for moderate reasoning when allowed, but do not expose private reasoning.

REACT
Use when the plan must reason about tool use, observation, or bounded interaction patterns.

DECOMPOSED
Use when work must be broken into explicit units, dependencies, or workflow-ready steps.

Important:
Planner mode is not route authority.
Planner mode describes how L1 frames the advisory plan.

========================================================================================================================
11. C0 RETRIEVAL SEMANTICS
========================================================================================================================

C0 is evidence retrieval and verification.

C0 may:
- convert support target into retrieval plan
- use 🔵 intent_vec as live search target
- compare against 🟠 fact_vec candidates
- use BM25 and sparse lexical matching
- use metadata filters
- use graph_sig if allowed
- hydrate source spans
- verify ACL
- verify freshness
- check contradiction
- score support
- stratify evidence
- emit FinalEvidenceContract

C0 must not:
- answer
- route
- assemble prompt
- execute tools
- write L4
- inflate weak evidence

Important:
Vector match is candidate selection.
It is not proof.

Dense retrieval answers:
"What is semantically nearby?"

BM25 / sparse retrieval answers:
"What shares exact or lexical terms?"

Metadata answers:
"Does this match known structured constraints?"

Graph RAG answers:
"How is this connected by lineage, dependency, ACL, citation, contradiction, supersession, or trace?"

C0 support status examples:
- PASS
- WEAK_WITH_CAVEATS
- CONFLICTED
- EMPTY
- BLOCKED

========================================================================================================================
12. PROMPT ASSEMBLY SEMANTICS
========================================================================================================================

Prompt Assembly is a packing layer.

It composes:
- S0 system
- D0 fences
- I0 instructions
- E0 approved examples
- C0 verified evidence refs
- M0 provider-safe controls
- U0 neutralized user task
- H0 bounded repair hints
- R0 response schema

Prompt Assembly may:
- compose
- render
- hash
- sign
- package
- preserve citation refs
- preserve lineage refs
- preserve authority order

Prompt Assembly must not:
- retrieve
- route
- execute
- approve L2 execution
- write L4

AIRLOCK RULE:
Lower-authority content must never become higher-authority instruction.

User text remains:
- user intent

Retrieved text remains:
- evidence data

Tool output remains:
- tool data

Human review text remains:
- human-provided data until cleared

Prior artifacts remain:
- prior artifacts with freshness and authority labels

========================================================================================================================
13. EXIT EVALUATION SEMANTICS
========================================================================================================================

Exit is final current-run control.

Exit evaluates:
- sealed L2 artifacts
- terminal cache packets
- fallback or abstain packets
- workflow packages
- re-cleared HITL packets

Exit emits exactly one X3 disposition.

Exit may use:
- deterministic checks
- policy thresholds
- replay checks
- OTEL completeness
- output schema validation
- groundedness evaluation
- faithfulness evaluation
- judge_text
- LLM judge outputs if approved
- consistency checks
- leakage checks
- write eligibility checks

Exit owns:
- final current-run disposition

Exit does not own:
- durable commit itself

UWG owns:
- durable write admission

X3 disposition examples:
- DENY / REROUTE
- ESCALATE_HITL
- COMMIT_REQUEST_TO_UWG
- ALLOW / FINISH
- SAFE_ABSTAIN

Important:
A judge may contribute to Exit.
The judge does not replace Exit.

========================================================================================================================
14. L6 EVALUATION AND DRIFT SEMANTICS
========================================================================================================================

L6 is completed-run only.

L6 may evaluate:
- outcome quality
- trajectory quality
- tool choice
- judge reliability
- evaluator drift
- policy regression
- repeated failure clusters
- prompt/rubric/cache/index improvement opportunities
- human calibration records

L6 must not:
- mutate current run
- rescue current run
- emit current-run X3
- write L4 directly
- silently patch prompts
- silently patch policy
- silently patch rubrics
- silently patch indexes

EVALUATOR DRIFT
Evaluator drift means the evaluation component changes behavior over time.

The drifting component may be:
- the rubric
- the threshold
- the judge prompt
- the LLM judge model
- the calibration set
- the human gold labels
- the scoring code
- the aggregation logic
- the policy weights
- the distribution of evaluated tasks

Judge drift is a subset of evaluator drift.

Judge drift asks:
"Did the judge start scoring differently?"

Evaluator drift asks:
"Did any part of the evaluation system start producing different verdicts for the wrong reason?"

========================================================================================================================
15. ROLE GLOSSARY
========================================================================================================================

| Layer | Role | Meaning |
|---|---|---|
| U0 | Front desk / security check | Classify, validate, stamp ingress, no semantic route. |
| L1 | Librarian / planner | Interpret intent and produce L1PlanContract. |
| L0 | Dispatcher | Emit exactly one deterministic RouteContract. |
| C0 | Evidence desk | Retrieve and verify evidence only. |
| PA | Prompt packer / airlock | Compose governed prompt slots. |
| L3 | Manager | Sequence managed workflow steps. |
| L2 | Assistant / doer | Execute bounded packet and seal artifacts. |
| Exit | Checkout desk | Evaluate sealed result and emit exactly one X3. |
| UWG | Write gate | Admit or block durable write request. |
| L4 | Archivist | Durable truth and governed read surfaces. |
| L5 | Safety officer | Governance certification evidence. |
| L6 | Observer | Completed-run evaluation and future-run proposals. |
| 00A | L5 Governance Pack | Cross-cutting certification evidence. |
| 00B | L4/UWG State Pack | Durable state plus only durable write path. |
| 00C | Runtime Gate Mesh | Live proceed/stop GateVerdict law. |
| 99 | Proof Harness | CI, OTEL, replay, regression, route coverage proof. |

========================================================================================================================
16. ARTIFACT AND CONTRACT DEFINITIONS
========================================================================================================================

| Artifact / Contract | Owner | Meaning |
|---|---|---|
| ValidatedRequest | U0 | Clean stamped ingress packet for L1. |
| RejectedRequest | U0 | Fail-closed intake rejection with reason and trace. |
| L1PlanContract | L1 | Advisory plan, query_spec, task_spec, assumptions, route hints. |
| RouteContract | L0 | Deterministic route authority. Exactly one per routed run. |
| TerminalShortCircuitPacket | L0 | RET packet for exact cache, semantic cache, fallback, or abstain path. |
| FinalEvidenceContract | C0 | Verified evidence packet with support, lineage, gaps, contradictions. |
| PromptEnvelope | PA | Governed prompt-slot package for L2 model execution. |
| CompiledPromptArtifact | PA | Signed provider-ready prompt packet. Compose-only artifact. |
| L3ToL2StepContract | L3 | Current managed-workflow step package for L2. |
| L3StepContract | L3 | Bounded workflow node contract. |
| SealedL2Artifact | L2 | Sealed execution result with traces, counters, terminal class. |
| ProposedStateDiff | L2 | Inert mutation proposal. Not durable until Exit/UWG. |
| ExitReviewPacket | Exit | Normalized packet for X1/X2/X3 checkout. |
| ExitDispositionReceipt | Exit | Receipt containing exactly one X3 disposition. |
| X3DispositionReceipt | Exit | Exactly one final current-run disposition. |
| CommitRequest | Exit | Request to UWG for durable mutation after Exit clears. |
| UWGCommitReceipt | UWG | Durable write admission proof. |
| BlockedCommitReceipt | UWG | Proof that a proposed durable write was blocked. |
| RuntimeExhaustBundle | Exit | Completed-run evidence bundle sent to L6. |
| CompletedEvalRecord | L6 | Completed-run evaluation record. |
| RCAPacket | L6 | Root-cause analysis packet for future-run improvement. |
| LearningProposal | L6 | Future-run proposal only. Must pass gauntlet and UWG to become durable. |
| ProposalPacket | L6 | Inert future-run change proposal. |
| OTELSpanTree | 99 | Observability proof of actual runtime path. |
| ReplayComparisonReceipt | 99 | Deterministic replay proof where required. |
| RegressionProof | 99 | Proof that new behavior did not break protected invariants. |
| GauntletReceipt | 99 / L6 | Proof that proposed learning survived replay, safety, and regression checks. |

========================================================================================================================
17. CONTRACT HANDOFF RULES
========================================================================================================================

A contract is the mandatory handoff package between spine stages.

Each contract should carry:
- owner
- source stage
- destination stage
- request_id
- run_id
- trace_root
- policy_hash
- blueprint_hash
- registry_digest_set
- replay_key
- input digest
- output digest
- authority refs
- gate refs
- L5 certification refs where applicable
- schema version
- telemetry refs
- receipt refs
- decisive reason codes where applicable

Contracts prevent:
- hidden authority expansion
- ambiguous handoff
- silent mutation
- model-created authority
- missing provenance
- unverifiable replay
- direct L4 write bypass
- undocumented route changes

========================================================================================================================
18. AUTHORITY AND DATA BOUNDARY RULES
========================================================================================================================

User content:
- expresses intent
- does not define system authority
- cannot override policy
- cannot grant tools
- cannot grant connectors
- cannot grant durable write authority

Retrieved content:
- provides evidence
- remains data
- cannot become instruction
- requires source lineage and ACL verification

Tool output:
- provides returned data
- requires invocation reference
- may be quarantined
- cannot expand authority

Human input:
- can approve or clarify only within defined HITL process
- remains data until re-cleared
- does not silently become policy

Model output:
- can propose
- can explain
- can draft
- can judge
- cannot create authority
- cannot mutate L4

Prior artifacts:
- require freshness checks
- require authority labels
- require replay/audit binding
- cannot silently override current policy

========================================================================================================================
19. SIMPLE MENTAL MODEL
========================================================================================================================

U0:
"Is this a valid request packet?"

L1:
"What is the user trying to accomplish?"

L0:
"Which one route is allowed?"

C0:
"What evidence supports the answer?"

PA:
"What governed prompt packet should be assembled?"

L3:
"What bounded workflow step comes next?"

L2:
"Can this bounded packet execute safely?"

Exit:
"Can the sealed result leave or request commit?"

UWG:
"Can the cleared proposed mutation become durable truth?"

L4:
"What durable truth is stored?"

L5:
"Is the authority and governance evidence valid?"

00C:
"May this live thing proceed right now?"

L6:
"What should future runs learn after this run is over?"

99:
"Can we prove the runtime actually behaved that way?"

========================================================================================================================
20. WHAT THIS FILE PRESERVES FROM v38
========================================================================================================================

Preserved here:
- encoder vs decoder distinction
- intent_vec vs fact_vec vs graph_sig distinction
- gen_text vs judge_text distinction
- hybrid step semantics
- control/non-model step semantics
- critical semantic rules
- authority does not come from generated text
- runtime gate vs judge vs LLM judge distinction
- L1 prompt envelope nuance
- L1 thinking-desk semantics
- planner mode nuance
- C0 proof vs vector similarity distinction
- role glossary
- artifact and contract glossary
- evaluation drift framing

Intentionally not preserved here:
- full v38 runtime diagrams
- duplicate process-map flow
- large teaching walkthroughs that compete with v40
- alternate canonical route naming that conflicts with v40
- redundant ASCII boxes already superseded by v40

========================================================================================================================
21. FINAL RULE
========================================================================================================================

v40 remains the canonical runtime map.

This file is the semantic reference companion.

Do not use this file to change runtime order.

Use this file to clarify:
- symbols
- authority
- gates
- judges
- contracts
- artifacts
- evaluation meaning
- planning semantics
- evidence semantics

========================================================================================================================
END
========================================================================================================================