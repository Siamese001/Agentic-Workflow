===================================================================================================================
[2] L1 REASONING + PLAN GENERATION — v5
[2] THE RESEARCH DESK | FIGURING OUT THE SEARCH PLAN
===================================================================================================================

- The senior reference librarian reads the stamped request slip, understands the actual goal, loads governing
  rules and priors, and writes the bounded plan that later routing may act on.

- L1 may interpret, decompose, compare options, draft a plan, inspect the plan, self-correct, simplify, or abstain.

- L1 may read approved planning references from L4, such as policies, rubrics, route heuristics, schema patterns,
  prior examples, and safe decomposition templates.

- L1 does NOT retrieve factual evidence for the final answer.

- L1 does NOT route with authority.

- L1 does NOT execute tools.

- L1 does NOT call external providers for work.

- L1 does NOT mutate durable state.

- L1 does NOT approve final egress.

- Inside L1 only, the model's transformer layers perform contextual refinement on the visible request, governing
  instruction frame, and planning priors so the planner can interpret the goal precisely before writing the
  notepad plan.

- Exec-summary semantic ladder preserved:
    PARSE INTENT -> DRAFT PLAN -> VALIDATE

- L1 output is a plan contract, not the work product.
  It is advisory to L0, bounded by policy, replayable, inspectable, and explicitly non-executing.

- Library analogy:
    Patron gives a messy request slip.
    Senior Research Librarian understands the real ask.
    Research Librarian writes a notepad plan.
    Hallway Director / Dispatcher later decides the actual route.

===================================================================================================================
L1 AUTHORITY BOUNDARY
===================================================================================================================

┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ WHAT L1 IS                                                                                                      │
│ - Planning intelligence                                                                                         │
│ - Intent interpreter                                                                                            │
│ - Constraint binder                                                                                             │
│ - Work decomposition author                                                                                     │
│ - Risk and ambiguity register                                                                                   │
│ - Proposed route advisor                                                                                        │
│ - Lowest viable agency recommender                                                                              │
│ - Downstream support expectation writer                                                                         │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ WHAT L1 IS NOT                                                                                                  │
│ - Not the router                                                                                                │
│ - Not the retriever                                                                                             │
│ - Not the executor                                                                                              │
│ - Not the tool caller                                                                                           │
│ - Not the writer                                                                                                │
│ - Not the exit approver                                                                                         │
│ - Not the durable memory owner                                                                                  │
│ - Not the policy override authority                                                                             │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ HARD LAW                                                                                                        │
│ - L1 may recommend.                                                                                             │
│ - L0 routes.                                                                                                    │
│ - C0 retrieves.                                                                                                 │
│ - Prompt Assembly packages.                                                                                     │
│ - L2 executes.                                                                                                  │
│ - Exit Control disposes.                                                                                        │
│ - UWG commits.                                                                                                  │
│ - L6 observes and learns for future runs only.                                                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


                                                          │
                                                          │ [ stamped validated request from [1] intake ]
                                                          │
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L1 INPUT CONTRACT                                                                                                │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ REQUIRED INPUTS                                                                                                  │
│ - validated_request                                                                                              │
│ - request_id / session_id / trace_root                                                                           │
│ - caller_scope_baseline / tenant binding / access baseline                                                       │
│ - normalized user payload                                                                                        │
│ - ingress rejection state if intake failed                                                                       │
│ - origin-trust labels from governance if already attached                                                        │
│ - current policy_hash / instruction_hash if available                                                            │
│ - visible conversation context allowed for this run                                                              │
│ - active user constraints and system constraints                                                                 │
│ - known artifact references, file names, URLs, uploaded objects, or source handles                               │
│ - request freshness hints                                                                                        │
│ - output channel expectations                                                                                    │
│ - available planning priors from L4 read surfaces                                                                │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ INPUT NORMALIZATION EXPECTATION                                                                                  │
│ - The request is already structurally valid.                                                                      │
│ - The request is not yet semantically routed.                                                                     │
│ - The request is not yet grounded.                                                                                │
│ - The request is not yet executed.                                                                                │
│ - The request may contain ambiguous language, conflicting constraints, unsafe instructions, or hidden asks.       │
│ - L1 must separate patron intent from executable system authority.                                                │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │
                                                           │ [ goal ]
                                                           ▼

┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ READING THE PATRON'S SLIP [ PARSE INTENT ]                                                                      │
│                                                                                                                 │
│ L1 turns the stamped ingress slip into an intent frame. It distinguishes what the patron asked for from how the  │
│ system may safely satisfy it. This is where ambiguity, constraints, requested format, success criteria, and      │
│ downstream support expectations are made explicit before any route is selected.                                  │
│                                                                                                                 │
│ invariant: L1 may understand the ask deeply, but understanding is not authority to act.                          │
│                                                                                                                 │
│ ┌──────────────────────────────┐┌──────────────────────────────┐┌──────────────────────────────┐┌──────────────┐│
│ │ I1 WHAT DO THEY WANT?        ││ I2 WHAT ARE THEIR RULES?     ││ I3 SPECIFIC DETAILS          ││ I4 JOB CLASS ││
│ │ - primary objective          ││ - hard constraints           ││ - entities / actors          ││ - summarize  ││
│ │ - actual desired end-state   ││ - soft constraints           ││ - exact numbers / vars       ││ - compare    ││
│ │ - answer / plan / artifact   ││ - scope boundaries           ││ - requested output format    ││ - explain    ││
│ │ - success condition          ││ - exclusions                 ││ - explicit deliverable       ││ - analyze    ││
│ │ - audience / user need       ││ - must / should / avoid      ││ - filenames / systems        ││ - classify   ││
│ │ - implicit real goal         ││ - time / freshness ask       ││ - dates / versions           ││ - plan       ││
│ │ - desired next step          ││ - privacy / safety cap       ││ - source names / connectors  ││ - act        ││
│ │ - outcome definition         ││ - style / tone rules         ││ - cited sources needed?      ││ - create     ││
│ │ - completion threshold       ││ - forbidden shortcuts        ││ - direct quote needed?       ││ - edit       ││
│ │ - stakeholder orientation    ││ - authority boundaries       ││ - schema / table / ASCII     ││ - retrieve   ││
│ │ - one-shot vs iterative need ││ - no-go conditions           ││ - artifact output required?  ││ - decide     ││
│ │ - likely hidden concern      ││ - compliance posture         ││ - external action requested? ││ - escalate   ││
│ └──────────────┬───────────────┘└──────────────┬───────────────┘└──────────────┬───────────────┘└──────┬───────┘│
│             [parse]                         [bound]                         [extract]              [frame]      │
│                └──────────────────────────────┴──────────────────────────────┴───────────────────────┘          │
│                                                           ▼                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ INTENT FRAME                                                                                              │  │
│  │ - normalized_goal                                                                                         │  │
│  │ - user_visible_deliverable                                                                                │  │
│  │ - audience / tone / structure requirements                                                                │  │
│  │ - constraints and exclusions                                                                              │  │
│  │ - entities, files, systems, dates, numbers, variables                                                     │  │
│  │ - support requirement: none / citation / source span / code location / policy clause / evidence bundle    │  │
│  │ - freshness requirement: stable / current / recent / exact-date / live                                    │  │
│  │ - action requirement: no action / read action / reversible action / write proposal / high-impact action   │  │
│  │ - artifact requirement: inline answer / file / doc / slide / spreadsheet / code / diagram                 │  │
│  │ - completion condition                                                                                    │  │
│  │ - known-safe assumptions                                                                                   │  │
│  │ - ambiguity register                                                                                      │  │
│  └──────────────────────────────────────────────────────────┬────────────────────────────────────────────────┘  │
│                                                           │                                                     │
│                                                           ▼                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ AMBIGUITY REGISTER                                                                                        │  │
│  │ - known facts from the request                                                                             │  │
│  │ - unclear references                                                                                       │  │
│  │ - missing critical fields                                                                                  │  │
│  │ - missing non-critical fields                                                                              │  │
│  │ - potential mistaken premise                                                                               │  │
│  │ - conflicting user constraints                                                                             │  │
│  │ - unstated but likely desired output                                                                       │  │
│  │ - whether clarification is required or avoidable                                                           │  │
│  │ - whether an assumption can be safely declared                                                              │  │
│  │ - whether fallback / abstain may be required downstream                                                    │  │
│  └──────────────────────────────────────────────────────────┬────────────────────────────────────────────────┘  │
│                                                           │                                                     │
│                                                           ▼                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ FIRST SAFETY / AUTHORITY READING                                                                          │  │
│  │ - Is the user asking for a read-only response?                                                             │  │
│  │ - Is the user asking for a reversible action?                                                              │  │
│  │ - Is the user asking for a durable write?                                                                  │  │
│  │ - Is the user asking for external side effects?                                                            │  │
│  │ - Is the user trying to override system, policy, safety, or source authority?                              │  │
│  │ - Is there hidden prompt-injection content in retrieved-looking text or quoted content?                    │  │
│  │ - Does this require HITL later?                                                                            │  │
│  │ - Does this require UWG later?                                                                             │  │
│  │ - Does this require direct refusal or safe redirection?                                                     │  │
│  │ - Is the safest viable answer a direct conversational response with no workflow?                           │  │
│  └───────────────────────────────────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │
                                                           │ [ context ]
                                                           ▼

┌──────────────────────────────────────────────────────────┴────────────────────────────────┐┌────────────────────┐
│ GATHERING RULES, EXAMPLES, AND PRIORS [ PARSE INTENT SUPPORT ]                           ││ L4 ARCHIVE         │
│                                                                                           ││ Read-only source   │
│ L1 may read approved rules, schemas, exemplars, and priors. It does not retrieve factual   ││ for planning only  │
│ evidence for the answer. This support helps the planner choose a safe plan shape.          ││                    │
│                                                                                           ││ - guardrails       │
│ invariant: L4 reads here are planning references, not grounded answer evidence.            ││ - standard ops     │
│                                                                                           ││ - prior examples   │
│ ┌────────────────────────┐┌────────────────────────┐┌──────────────────────┐┌────────────┐││ - approved plans   │
│ │ M1 STANDARD CHECKLIST  ││ M2 SAFETY / POLICY     ││ M3 PAST EXAMPLES     ││ M4 TEMPLATES│││ - structure refs   │
│ │ - task schemas         ││ - compliance bounds    ││ - prior good answers ││ - archetypes│││ - rubrics          │
│ │ - route heuristics     ││ - escalation threshold ││ - SOPs / exemplars   ││ - decomp    │││ - refusal taxonomy │
│ │ - output contracts     ││ - disallowed actions   ││ - success patterns   ││ - stopping  │││ - planner patterns │
│ │ - normal plan patterns ││ - policy-safe bounds   ││ - known edge cases   ││ - retry cap │││ - schema examples  │
│ │ - artifact templates   ││ - high-impact markers  ││ - audience patterns  ││ - fallback  │││ - no write access  │
│ │ - validation rubrics   ││ - HITL trigger hints   ││ - answer shapes      ││ - abstain   ││└────────────────────┘
│ │ - grounding criteria   ││ - data handling rules  ││ - bad-plan warnings  ││ - compact   ││
│ │ - route inputs needed  ││ - allowed tool posture ││ - route examples     ││ - workflow  ││
│ │ - schema requirements  ││ - refusal taxonomy     ││ - anti-patterns      ││ - repair    ││
│ │ - citation standards   ││ - authority ladder     ││ - concise examples   ││ - response  ││
│ └───────────┬────────────┘└───────────┬────────────┘└──────────┬───────────┘└─────┬──────┘│
│          [load]                    [bound]                  [merge]           [bundle]   │
│             └────────────────────────┴────────────────────────┴──────────────────┘       │
│                                                          ▼                                │
│ ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ PLAN BUNDLE                                                                            │ │
│ │ - schemas                                                                              │ │
│ │ - active policy posture                                                                │ │
│ │ - route heuristics                                                                     │ │
│ │ - safe decomposition patterns                                                          │ │
│ │ - output format expectations                                                           │ │
│ │ - citation and support standards                                                       │ │
│ │ - escalation and HITL hints                                                            │ │
│ │ - lowest viable agency rules                                                           │ │
│ │ - fallback and abstention patterns                                                     │ │
│ │ - artifact-specific handling rules                                                     │ │
│ │ - replay and determinism considerations                                                │ │
│ └──────────────────────────────────────────────────────────┬────────────────────────────┘ │
│                                                          │                                │
│                                                          ▼                                │
│ ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ RULE-AWARE PLANNING FRAME                                                             │ │
│ │ - what can be answered directly                                                        │ │
│ │ - what must be grounded                                                                │ │
│ │ - what must be routed through C0                                                       │ │
│ │ - what must be executed by L2                                                          │ │
│ │ - what must be orchestrated by L3                                                      │ │
│ │ - what must be escalated                                                               │ │
│ │ - what must be refused or safely redirected                                            │ │
│ │ - what can be assumed                                                                  │ │
│ │ - what must be clarified                                                               │ │
│ │ - what must remain proposal-only                                                       │ │
│ │ - what must never be written directly                                                  │ │
│ └───────────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │
                                                           │ [ reason ]
                                                           ▼

┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ THE THINKING DESK [ L1 REASONING LOOP ]                                                                         │
│                                                                                                                 │
│ invariant: internal non-linearity stays here only. L1 can draft, inspect, refine, simplify, or abstain, but     │
│ cannot execute.                                                                                                 │
│                                                                                                                 │
│ This is the only place where the model performs internal contextual refinement of the visible request and its    │
│ loaded instruction frame. The result is not an answer. It is a better plan specification.                        │
│                                                                                                                 │
│ transformer note: visible tokens are mixed into richer internal states so the planner can bind goals,            │
│ constraints, entities, risks, and output expectations correctly.                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                 │
│ ┌───────────────────────────────────────┐┌────────────────────────────────┐┌──────────────────────────────────┐ │
│ │ T1 CONTEXTUAL REFINEMENT OF REQUEST   ││ T2 SIMULTANEOUS ATTENTION PASS ││ T3 POST-ATTENTION SHARPENING     │ │
│ │ - visible tokens enter with x_i       ││ - q_i = x_i W_Q                ││ - Residual 1: x_i + z_i          │ │
│ │ - position marks order / structure    ││ - k_i = x_i W_K                ││ - Norm 1 stabilizes feature scale│ │
│ │ - request is one visible set          ││ - v_i = x_i W_V                ││ - FFN sharpens each token indep. │ │
│ │ - system / policy tokens visible      ││ - heads compare visible tokens ││ - Residual 2 preserves identity  │ │
│ │ - examples may influence shape        ││ - constraints attend to goals  ││ - Norm 2 prepares next layer     │ │
│ │ - no routing authority here           ││ - entities attend to actions   ││ - ambiguity becomes more visible│ │
│ │ - pronouns become contextual          ││ - format binds to deliverable  ││ - irrelevant phrasing is damped │ │
│ │ - entities bind to roles              ││ - task words map to work class ││ - plan-relevant features sharpen│ │
│ │ - constraints bind to target          ││ - all visible tokens mix       ││ - still no evidence retrieval   │ │
│ │ - safety terms bind to policy         ││ - no external call is made     ││ - still no tool execution       │ │
│ │ - user intent stays non-authoritative ││ - no C0 retrieval happens      ││ - still no route commitment     │ │
│ └───────────────────┬───────────────────┘└────────────────┬───────────────┘└────────────────┬─────────────────┘ │
│                  [project]                              [mix]                           [sharpen]               │
│                     └─────────────────────────────────────┼─────────────────────────────────┘                   │
│                                                           ▼                                                     │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ T4 WHAT THE MODEL IS DOING INTERNALLY [ PARSE INTENT INTERNALS ]                                           │ │
│ │                                                                                                             │ │
│ │ ATTENTION MATH                                                                                              │ │
│ │ - affinity scores:        s_i,j = q_i • k_j^T                                                               │ │
│ │ - attention weights:      w_i,j = exp(s_i,j) / Σ exp(s_i,k)                                                 │ │
│ │ - context mix:            z_i   = Σ (w_i,j * v_j)                                                          │ │
│ │ - residual preservation:  x_i   -> x_i + z_i                                                               │ │
│ │ - layer normalization:    stabilizes feature scale                                                          │ │
│ │ - feed-forward network:   sharpens token-local features after token-to-token mixing                         │ │
│ │                                                                                                             │ │
│ │ PRACTICAL EFFECT                                                                                            │ │
│ │ - "draft this" is separated from "send this"                                                              │ │
│ │ - "find this" is separated from "answer from memory"                                                       │ │
│ │ - "summarize this uploaded file" is separated from "search the web"                                       │ │
│ │ - "overwrite below" is separated from "make a new file"                                                    │ │
│ │ - "current" or "latest" becomes a freshness flag                                                           │ │
│ │ - "cite" becomes a support target                                                                          │ │
│ │ - "delete", "send", "book", or "commit" becomes an action / write-risk marker                            │ │
│ │ - "my file", "Google Drive", or "uploaded doc" becomes a source expectation                               │ │
│ │ - constraints bind to the correct deliverable                                                               │ │
│ │ - style preferences bind to external-facing writing tasks                                                   │ │
│ │ - high-impact or irreversible actions become escalation candidates                                          │ │
│ │                                                                                                             │ │
│ │ HARD INVARIANT                                                                                              │ │
│ │ - This is internal model interpretation.                                                                    │ │
│ │ - It is not retrieval.                                                                                      │ │
│ │ - It is not route commitment.                                                                               │ │
│ │ - It is not execution.                                                                                      │ │
│ │ - It is not durable learning.                                                                               │ │
│ └─────────────────────────────────────────────────────────┬───────────────────────────────────────────────────┘ │
│                                                           │                                                     │
│                                                           │ [ interpret ]
│                                                           ▼
│ ┌───────────────────────────┐┌───────────────────────────┐┌───────────────────────────────────────────────────┐ │
│ │ P1 BREAK INTO BABY STEPS  ││ P2 PUT IN ORDER           ││ P3 PICK THE AISLES [ DRAFT PLAN ]                │ │
│ │ - atomic work units       ││ - sequential vs parallel  ││ - proposed routes only                            │ │
│ │ - sub-goal boundaries     ││ - what unlocks what       ││ - R1A exact cache hint if safe                    │ │
│ │ - missing-info markers    ││ - dependency graph        ││ - R1B semantic cache hint if safe                 │ │
│ │ - explicit unknowns       ││ - stopping points         ││ - R3 grounded context path if needed              │ │
│ │ - evidence need markers   ││ - prerequisite checks     ││ - R4 single action path if needed                 │ │
│ │ - tool need markers       ││ - independent shards      ││ - R3/R4 managed workflow if needed                │ │
│ │ - output sections         ││ - max-loop boundaries     ││ - R5 fallback if unsafe / unsupported             │ │
│ │ - acceptance criteria     ││ - retry / repair posture  ││ - HITL hint if high-risk                          │ │
│ │ - artifact requirements   ││ - fan-out possibility     ││ - UWG hint if durable write requested             │ │
│ │ - citation obligations    ││ - join / merge needs      ││ - C0 requirement if grounding needed              │ │
│ │ - risk flags              ││ - escalation points       ││ - direct answer if no route needed                │ │
│ │ - possible stop states    ││ - completion state        ││ - no final route authority here                   │ │
│ └─────────────┬─────────────┘└─────────────┬─────────────┘│ - no C0 retrieval here                            │ │
│            [split]                      [order]           │ - no tool / model execution here                  │ │
│               └────────────────────────────┼──────────────┴─────────────────────────┬─────────────────────────┘ │
│                                            ▼                                      [map]                         │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ P4 WRITE THE DRAFT PLAN [ DRAFT PLAN OUTPUT ]                                                              │ │
│ │                                                                                                             │ │
│ │ ROUTE HINTS, NOT ROUTE AUTHORITY                                                                            │ │
│ │ - proposed_route_hint: R1A_EXACT_CACHE / R1B_SEMANTIC_CACHE / R3_GROUNDED_READ / R4_SINGLE_ACTION           │ │
│ │ - proposed_route_hint: R3R4_MANAGED_WORKFLOW / R5_FALLBACK                                                  │ │
│ │ - route_reason_codes                                                                                        │ │
│ │ - route_risk / confidence                                                                                   │ │
│ │ - fallback expectation                                                                                      │ │
│ │                                                                                                             │ │
│ │ QUERY SPEC                                                                                                  │ │
│ │ - normalized ask                                                                                            │ │
│ │ - entities / aliases / terms                                                                                │ │
│ │ - files / systems / locations                                                                               │ │
│ │ - dates / versions / freshness class                                                                        │ │
│ │ - source expectations                                                                                       │ │
│ │ - user-provided context boundaries                                                                          │ │
│ │ - whether external browsing or connector search may be required                                             │ │
│ │ - whether currentness is mandatory                                                                          │ │
│ │                                                                                                             │ │
│ │ TASK SPEC                                                                                                   │ │
│ │ - work units                                                                                                │ │
│ │ - output target                                                                                             │ │
│ │ - format constraints                                                                                        │ │
│ │ - style constraints                                                                                         │ │
│ │ - success condition                                                                                         │ │
│ │ - acceptance criteria                                                                                       │ │
│ │ - stop condition                                                                                            │ │
│ │ - expected length / depth                                                                                   │ │
│ │ - artifact packaging requirement                                                                            │ │
│ │ - whether partial completion is acceptable                                                                  │ │
│ │                                                                                                             │ │
│ │ SUPPORT EXPECTATION                                                                                         │ │
│ │ - grounding_required: yes / no / conditional                                                                │ │
│ │ - support_target: none / citation / direct quote / code span / policy clause / evidence bundle              │ │
│ │ - evidence class expectation: docs / code / logs / tables / web / email / calendar / file library           │ │
│ │ - source freshness expectation                                                                              │ │
│ │ - contradiction handling expectation                                                                        │ │
│ │ - cite-or-abstain posture                                                                                   │ │
│ │                                                                                                             │ │
│ │ ACTION EXPECTATION                                                                                          │ │
│ │ - tool/action expectation: none / candidate tool class / write proposal only / external side effect         │ │
│ │ - whether action can be done in one bounded step                                                            │ │
│ │ - whether L3 workflow may be needed                                                                         │ │
│ │ - whether HITL may be needed                                                                                │ │
│ │ - whether UWG commit may be needed                                                                          │ │
│ │ - whether sandbox / capability token will be required downstream                                            │ │
│ │                                                                                                             │ │
│ │ ESCALATION MARKERS                                                                                          │ │
│ │ - high-impact domain                                                                                        │ │
│ │ - irreversible mutation                                                                                     │ │
│ │ - ambiguous authority                                                                                       │ │
│ │ - unsafe instruction                                                                                        │ │
│ │ - insufficient support                                                                                      │ │
│ │ - policy conflict                                                                                           │ │
│ │ - private / sensitive data handling                                                                         │ │
│ │ - external egress risk                                                                                      │ │
│ │                                                                                                             │ │
│ │ LOWEST VIABLE AGENCY RECOMMENDATION                                                                         │ │
│ │ - answer directly                                                                                           │ │
│ │ - grounded read                                                                                             │ │
│ │ - single bounded action                                                                                     │ │
│ │ - managed workflow                                                                                          │ │
│ │ - ask a clarification                                                                                       │ │
│ │ - abstain / refuse / safe redirect                                                                          │ │
│ │                                                                                                             │ │
│ │ invariant: this is still a notepad plan. L0 must make the actual route decision.                            │ │
│ └─────────────────────────────────────────────────────────┬───────────────────────────────────────────────────┘ │
│                                                           │                                                     │
│                                                           │ [ inspect ]
│                                                           ▼
│ ┌─────────────────────────────┐┌──────────────────────────────┐┌──────────────────────────────────────────────┐ │
│ │ V1 DID WE LISTEN?           ││ V2 IS IT SAFE?               ││ V3 DOES IT MAKE SENSE? [ VALIDATE ]          │ │
│ │ - answers actual goal       ││ - within policy bounds       ││ - dependencies resolve                       │ │
│ │ - respects constraints      ││ - escalation if needed       ││ - coherent sub-task order                    │ │
│ │ - right deliverable         ││ - no forbidden action        ││ - admits unknowns                            │ │
│ │ - right format              ││ - no unsafe tool assumption  ││ - no circular dependency                     │ │
│ │ - audience and tone fit     ││ - no hidden write authority  ││ - enough support target detail               │ │
│ │ - no invented requirements  ││ - no HITL bypass             ││ - executable by downstream layers            │ │
│ │ - explicit asks handled     ││ - no UWG bypass              ││ - fallback path explicit                     │ │
│ │ - constraints not dropped   ││ - no policy override by U0   ││ - route hint is internally consistent        │ │
│ │ - hidden ask captured       ││ - sensitive info bounded     ││ - no over-splitting                          │ │
│ │ - output target clear       ││ - external egress flagged    ││ - no under-specified action                  │ │
│ └──────────────┬──────────────┘└──────────────┬───────────────┘└───────────────────────┬──────────────────────┘ │
│             [check]                        [check]                                  [check]                     │
│                └──────────────────────────────┼────────────────────────────────────────┘                        │
│                                               ▼                                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ V3A PLAN CONSISTENCY AUDIT                                                                                  │ │
│ │ - If route hint is cache, support target must not require fresh evidence.                                    │ │
│ │ - If route hint is grounded read, C0 must be required and L2 must receive an evidence contract.              │ │
│ │ - If route hint is single action, action must be bounded and not require multi-step dependency state.         │ │
│ │ - If route hint is managed workflow, there must be a real reason for L3: dependencies, branching, joins,     │ │
│ │   multiple source packets, retries, parallel-safe shards, or resumable state.                                │ │
│ │ - If route hint is fallback, reason_code must explain why direct completion is unsafe or unsupported.         │ │
│ │ - If durable mutation is possible, UWG must be marked downstream.                                            │ │
│ │ - If high-risk action is possible, HITL must be marked downstream.                                           │ │
│ │ - If evidence is weak, plan must not pretend confidence.                                                     │ │
│ │ - If user asks for "full overwrite", deliverable must preserve structure and not append unrelated notes.     │ │
│ └─────────────────────────────────────────────────────────┬───────────────────────────────────────────────────┘ │
│                                                           │                                                     │
│                               ┌───────────────────────────┴───────────────────────────┐                         │
│                               ▼                                                       ▼                         │
│ ┌────────────────────────────────────────┐ ┌────────────────────────────────────────────────────────────────┐   │
│ │ V4 CAN IT BE SIMPLER?                  │ │ V5 SHOULD WE ABSTAIN OR CLARIFY?                               │   │
│ │ - lowest viable agency                 │ │ - insufficient support path                                    │   │
│ │ - no over-complication                 │ │ - clarify if missing critical detail                           │   │
│ │ - erase and restart if weak            │ │ - abstain if bounded completion impossible                     │   │
│ │ - prefer direct answer if safe         │ │ - fallback if unsafe, unsupported, or out of scope             │   │
│ │ - avoid workflow when one step works   │ │ - do not ask clarification for non-critical gaps               │   │
│ │ - avoid tool use when prose is enough  │ │ - declare assumption if safe and useful                        │   │
│ │ - avoid grounding if stable/common     │ │ - flag when grounding is mandatory before answer               │   │
│ │ - shrink to route-relevant core        │ │ - flag when HITL or UWG may be required later                  │   │
│ │ - remove decorative complexity         │ │ - flag when user-provided premise may be wrong                 │   │
│ │ - keep only useful substeps            │ │ - flag when source access is missing                           │   │
│ │ - cap loops and retries                │ │ - choose safe partial if full answer cannot be supported       │   │
│ └───────────────────┬────────────────────┘ └────────────────────────────────┬───────────────────────────────┘   │
│                  [check]                                                 [check]                                │
│                     └─────────────────────────────────┬─────────────────────┘                                   │
│                                                       ▼                                                         │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ V6 SELF-REPAIR LOOP                                                                                         │ │
│ │                                                                                                             │ │
│ │ IF PLAN FAILS VALIDATION                                                                                    │ │
│ │ - repair dropped constraint                                                                                 │ │
│ │ - repair missing output target                                                                              │ │
│ │ - repair unsafe route hint                                                                                  │ │
│ │ - repair unclear support expectation                                                                        │ │
│ │ - repair over-broad action assumption                                                                       │ │
│ │ - repair missing fallback                                                                                   │ │
│ │ - repair missing HITL / UWG hint                                                                            │ │
│ │ - repair unnecessary workflow                                                                               │ │
│ │ - repair excessive clarification                                                                            │ │
│ │ - repair unsupported certainty                                                                              │ │
│ │                                                                                                             │ │
│ │ LOOP LIMIT                                                                                                  │ │
│ │ - refine once or twice inside L1                                                                            │ │
│ │ - if still weak, mark clarify / abstain / fallback                                                          │ │
│ │ - do not spin indefinitely                                                                                  │ │
│ │ - do not call tools to rescue the plan                                                                      │ │
│ │ - do not perform C0 retrieval to rescue the plan                                                            │ │
│ └─────────────────────────────────────────────────────────┬───────────────────────────────────────────────────┘ │
│                                                           ▼                                                     │
│                    [ pass -> approve | fail -> refine / simplify / clarify / abstain ]                          │
│                                                           │                                                     │
│                                                           ▼                                                     │
│       [ final L1 notepad = bounded plan + assumptions + risks + support expectations + no execution authority ] │
└───────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────┘
                                                            │
                                                            │ [ output ]
                                                            ▼

┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L1 PLAN OUTPUT CONTRACT                                                                                         │
│                                                                                                                 │
│ REQUIRED FIELDS                                                                                                 │
│                                                                                                                 │
│ 1. identity                                                                                                     │
│ - request_id                                                                                                    │
│ - trace_root                                                                                                    │
│ - l1_plan_id                                                                                                    │
│ - policy_hash observed                                                                                          │
│ - instruction_hash observed                                                                                     │
│ - source envelope id                                                                                            │
│                                                                                                                 │
│ 2. intent_frame                                                                                                 │
│ - normalized_goal                                                                                               │
│ - user_visible_deliverable                                                                                      │
│ - work_class                                                                                                    │
│ - audience / style / tone                                                                                       │
│ - success_condition                                                                                             │
│ - explicit constraints                                                                                          │
│ - exclusions                                                                                                    │
│ - hidden or implied goal                                                                                        │
│                                                                                                                 │
│ 3. query_spec                                                                                                   │
│ - normalized request                                                                                            │
│ - entities / aliases / terms                                                                                    │
│ - dates / versions / freshness                                                                                  │
│ - source expectations                                                                                           │
│ - connector expectations                                                                                        │
│ - uploaded file expectations                                                                                    │
│ - whether direct citation / exact span / live source may be required                                            │
│                                                                                                                 │
│ 4. task_spec                                                                                                    │
│ - work units                                                                                                    │
│ - output target                                                                                                 │
│ - output format                                                                                                 │
│ - structure requirements                                                                                        │
│ - constraints                                                                                                   │
│ - acceptance criteria                                                                                           │
│ - stop condition                                                                                                │
│ - partial completion posture                                                                                    │
│ - artifact requirements                                                                                         │
│                                                                                                                 │
│ 5. route_hint                                                                                                   │
│ - proposed_route_hint: R1A_EXACT_CACHE / R1B_SEMANTIC_CACHE / R3_GROUNDED_READ / R4_SINGLE_ACTION               │
│ - proposed_route_hint: R3R4_MANAGED_WORKFLOW / R5_FALLBACK                                                      │
│ - reason_codes                                                                                                  │
│ - route_risk                                                                                                    │
│ - confidence                                                                                                    │
│ - fallback_chain_hint                                                                                           │
│ - cost / latency sensitivity                                                                                    │
│ - single-step vs workflow recommendation                                                                        │
│                                                                                                                 │
│ 6. support_expectation                                                                                          │
│ - grounding_required: yes / no / conditional                                                                    │
│ - support_target: none / citation / direct span / code location / policy clause / evidence bundle               │
│ - evidence class expectation                                                                                    │
│ - freshness class                                                                                               │
│ - contradiction handling                                                                                        │
│ - cite-or-abstain posture                                                                                       │
│ - weak support handling                                                                                         │
│                                                                                                                 │
│ 7. action_expectation                                                                                           │
│ - no action / read-only / candidate tool class / reversible action / write proposal / high-impact action        │
│ - sandbox need hint                                                                                             │
│ - capability token need hint                                                                                    │
│ - external egress hint                                                                                          │
│ - HITL hint                                                                                                     │
│ - UWG hint                                                                                                      │
│ - irreversible action marker                                                                                    │
│                                                                                                                 │
│ 8. assumptions_and_gaps                                                                                         │
│ - declared assumptions                                                                                          │
│ - unresolved gaps                                                                                               │
│ - missing critical details                                                                                      │
│ - missing non-critical details                                                                                  │
│ - clarification recommendation                                                                                  │
│ - abstain / fallback marker                                                                                     │
│                                                                                                                 │
│ 9. validation_summary                                                                                           │
│ - listened_to_user: pass / fail                                                                                 │
│ - safety_checked: pass / fail / needs_policy                                                                    │
│ - coherent_plan: pass / fail                                                                                    │
│ - lowest_viable_agency_applied: yes / no                                                                        │
│ - no_execution_authority_asserted: yes                                                                          │
│ - no_retrieval_performed: yes                                                                                   │
│ - no_write_performed: yes                                                                                       │
│                                                                                                                 │
│ 10. downstream_notes                                                                                            │
│ - for L0: route-discriminating facts                                                                            │
│ - for C0 if used: retrieval support target                                                                      │
│ - for Prompt Assembly if used: required slots and output schema hint                                             │
│ - for L2 if used: bounded step shape                                                                            │
│ - for Exit Control: risk / escalation / egress notes                                                            │
│ - for L6: telemetry keys worth observing                                                                        │
│                                                                                                                 │
│ EXPLICIT NON-AUTHORITY                                                                                          │
│ - no evidence retrieval                                                                                         │
│ - no final route commitment                                                                                     │
│ - no tool execution                                                                                             │
│ - no durable state mutation                                                                                     │
│ - no external provider call for work                                                                            │
│ - no final egress approval                                                                                      │
│ - no HITL approval                                                                                              │
│ - no UWG commit                                                                                                 │
│                                                                                                                 │
│ invariant: L1 produces the notepad plan only. It does not retrieve evidence, route with authority, execute, or  │
│ perform the work.                                                                                               │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │
                                                           │ [ handoff ]
                                                           ▼
                                          [ Send to Hallway Director [3] L0 ROUTING ]


===================================================================================================================
L1 PLAN CONTRACT — CANONICAL SHAPE
===================================================================================================================

{
  "layer": "L1_REASONING_PLAN_GENERATION",
  "version": "v5",
  "authority": "advisory_plan_only",

  "identity": {
    "request_id": "<from_intake>",
    "trace_root": "<from_intake>",
    "l1_plan_id": "<stable_plan_id>",
    "policy_hash": "<observed_policy_hash>",
    "instruction_hash": "<observed_instruction_hash>",
    "source_envelope_id": "<validated_request_envelope>"
  },

  "intent_frame": {
    "normalized_goal": "<plain-language goal>",
    "deliverable": "<answer | plan | artifact | file | action proposal>",
    "work_class": "<summarize | compare | explain | analyze | plan | act | create | edit | retrieve | decide>",
    "audience": "<intended audience>",
    "style_constraints": ["<style rule>"],
    "hard_constraints": ["<must / must not>"],
    "soft_constraints": ["<preference>"],
    "success_condition": "<what done means>",
    "implicit_goal": "<likely real goal if inferable>"
  },

  "query_spec": {
    "entities": ["<entity>"],
    "files_or_sources": ["<file/source expectation>"],
    "dates_or_versions": ["<date/version>"],
    "freshness_class": "<stable | recent | live | exact-date>",
    "source_expectations": ["<uploaded file | file library | drive | web | email | calendar | none>"],
    "support_need": "<none | citation | direct span | code location | policy clause | evidence bundle>"
  },

  "task_spec": {
    "work_units": ["<unit 1>", "<unit 2>"],
    "output_target": "<target>",
    "format": "<prose | bullets | table | ascii | code | artifact>",
    "acceptance_criteria": ["<criterion>"],
    "stop_condition": "<when to stop>",
    "partial_completion_allowed": true
  },

  "route_hint": {
    "proposed_route_hint": "<R1A_EXACT_CACHE | R1B_SEMANTIC_CACHE | R3_GROUNDED_READ | R4_SINGLE_ACTION | R3R4_MANAGED_WORKFLOW | R5_FALLBACK>",
    "confidence": "<low | medium | high>",
    "route_risk": "<low | medium | high>",
    "reason_codes": ["<reason>"],
    "fallback_chain_hint": ["<fallback>"],
    "single_step_or_workflow": "<single_step | managed_workflow | terminal_short_circuit>"
  },

  "support_expectation": {
    "grounding_required": "<yes | no | conditional>",
    "support_target": "<none | citation | direct_span | code_location | policy_clause | evidence_bundle>",
    "evidence_classes": ["<docs | code | logs | tables | web | private connector>"],
    "weak_support_policy": "<clarify | abstain | caveat | fallback>",
    "contradiction_policy": "<surface_conflict | prefer_authoritative | abstain_if_unresolved>"
  },

  "action_expectation": {
    "action_required": false,
    "candidate_tool_class": "<none | email | calendar | filesystem | browser | code | doc | spreadsheet>",
    "side_effect_class": "<none | read | reversible | write_proposal | irreversible>",
    "hitl_hint": false,
    "uwg_hint": false,
    "sandbox_hint": false,
    "capability_token_hint": false
  },

  "assumptions_and_gaps": {
    "declared_assumptions": ["<assumption>"],
    "unresolved_gaps": ["<gap>"],
    "clarify_required": false,
    "clarify_question": "<only if critical>",
    "abstain_or_fallback_marker": "<none | clarify | abstain | refuse | safe_redirect>"
  },

  "validation_summary": {
    "listened_to_user": true,
    "constraints_preserved": true,
    "safety_checked": true,
    "coherent_plan": true,
    "lowest_viable_agency_applied": true,
    "no_retrieval_performed": true,
    "no_execution_performed": true,
    "no_write_performed": true
  },

  "downstream_notes": {
    "for_l0": ["<route discriminators>"],
    "for_c0": ["<retrieval target if grounding required>"],
    "for_prompt_assembly": ["<slot/schema hints>"],
    "for_l2": ["<bounded step hints>"],
    "for_exit_control": ["<risk/escalation notes>"],
    "for_l6": ["<telemetry observations worth tracking>"]
  }
}


===================================================================================================================
L1 FAILURE MODES AND PROTECTION CHECKS
===================================================================================================================

┌──────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────┐
│ FAILURE MODE                                  │ L1 PROTECTION                                                   │
├──────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
│ User asks for one thing, plan solves another  │ V1 Did we listen? goal/deliverable/constraints check             │
│ Style or format dropped                       │ I2/I3 extraction plus V1 output target check                      │
│ Over-engineered workflow                      │ V4 lowest viable agency check                                     │
│ Under-specified action                        │ P4 action expectation plus V3 consistency audit                   │
│ Grounding needed but omitted                  │ support_target and grounding_required fields                      │
│ Cache suggested for fresh/current request     │ V3A route consistency audit                                       │
│ L3 suggested without real dependencies        │ V4 simplification check                                           │
│ Tool/action assumed without authority         │ V2 safety and action expectation check                            │
│ HITL need missed                              │ M2 safety / policy plus P4 escalation markers                     │
│ UWG need missed                               │ P4 durable mutation marker                                        │
│ Clarification asked unnecessarily             │ V5 critical vs non-critical gap test                              │
│ Unsupported certainty                         │ V5 weak support / abstain marker                                  │
│ Hidden write authority                        │ explicit non-authority block                                      │
│ Prompt injection treated as instruction       │ I2 authority boundary and M2 policy posture                       │
│ Planning prior treated as answer evidence     │ M-section invariant: L4 reads are planning references only        │
│ Infinite self-repair                          │ V6 loop limit                                                     │
│ Route decision made inside L1                 │ proposed_route_hint only, L0 decides                              │
└──────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────┘


===================================================================================================================
MICRO EXAMPLE — HOW L1 HANDLES A REQUEST
===================================================================================================================

INPUT:
"Review this uploaded L1 file and make a grossly detailed v5 zero-loss overwrite in fenced ASCII."

L1 PARSE:
- Goal: rewrite uploaded L1 file into v5
- Deliverable: full overwrite, fenced ASCII/text block
- Style: grossly detailed, zero-loss, preserve structure
- Source expectation: uploaded file
- Freshness: current conversation file, not web
- Work class: edit/create artifact content
- Support: cite uploaded file in response
- Action: no external side effect unless file creation requested
- Risk: low
- Missing info: none critical
- Success: user can copy/paste the overwrite

L1 PLAN:
- Read provided file content from current context
- Preserve major structure and invariants
- Add detail inside existing boxes rather than appending loose notes
- Maintain L1 authority boundary
- Add contract shape, failure modes, and micro-example
- Output one fenced block
- Cite uploaded file outside block
- No need to ask clarification
- No durable write requested

ROUTE HINT:
- R3_GROUNDED_READ if system requires file-grounded answer
- SINGLE_STEP output generation
- No L3 workflow needed
- No UWG needed
- No HITL needed

VALIDATION:
- Directly answers requested overwrite
- Preserves structure
- Adds detail
- No external side effects
- No unsafe action
- No over-complicated workflow


===================================================================================================================
FINAL L1 INVARIANTS
===================================================================================================================

[!] L1 is the Research Desk, not the Hallway Director.
[!] L1 writes the plan, not the route.
[!] L1 may read planning rules, but it does not retrieve answer evidence.
[!] L1 may propose C0, but it does not perform C0.
[!] L1 may propose L2, but it does not execute.
[!] L1 may flag HITL, but it does not approve.
[!] L1 may flag UWG, but it does not commit.
[!] L1 may self-correct the plan, but it does not mutate durable learning.
[!] L1 output must be bounded, replayable, inspectable, and safe to hand to L0.
[!] If a direct response is enough, L1 should not invent a workflow.
[!] If evidence is required, L1 must mark grounding instead of pretending support exists.
[!] If authority is ambiguous, L1 must mark clarify / escalate / fallback instead of acting.
[!] If completion is unsafe or unsupported, L1 must mark abstain / fallback rather than fabricate certainty.

===================================================================================================================
END OF [2] L1 REASONING + PLAN GENERATION — v5
===================================================================================================================