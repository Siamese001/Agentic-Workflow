===================================================================================================================
[2] L1 REASONING + PLAN GENERATION
[2] THE RESEARCH DESK | FIGURING OUT THE SEARCH PLAN
===================================================================================================================
- The senior reference librarian who reads the stamped request slip, understands the actual goal, loads the
  governing rules and priors, and writes the bounded plan that later routing may act on.
- L1 may think, decompose, compare options, and self-correct, but it never retrieves evidence directly, never
  routes with authority, never executes tools, and never mutates durable state.
- Inside L1 only, the model's transformer layers perform contextual refinement on the visible request/prompt so
  the planner can interpret the goal precisely before writing the notepad plan.

                                                          │ [ goal ]
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ READING THE PATRON'S SLIP                                                                                       │
│ ┌────────────────────────┐┌────────────────────────┐┌──────────────────────────┐┌─────────────────────────────┐ │
│ │ I1 WHAT DO THEY WANT?  ││ I2 WHAT ARE THEIR RULES││ I3 SPECIFIC DETAILS      ││ I4 WHAT KIND OF JOB IS THIS?│ │
│ │ - primary objective    ││ - hard constraints     ││ - entities / actors      ││ - summarize / compare       │ │
│ │ - requested end-state  ││ - soft constraints     ││ - exact numbers / vars   ││ - analyze / plan / act      │ │
│ │ - answer/plan/artifact ││ - scope / exclusions   ││ - required output format ││ - classify before planning  │ │
│ │ - success condition    ││ - must / should / avoid││ - explicit deliverable   ││ - work class drives plan    │ │
│ └───────────┬────────────┘└───────────┬────────────┘└────────────┬─────────────┘└──────────────┬──────────────┘ │
│          [parse]                   [bound]                    [merge]                       [frame]             │
│             └─────────────────────────┴──────────────────────────┴─────────────────────────────┘                │
│                                                          ▼                                                      │
│         [ clear intent frame = goal + constraints + details + output target + work class + success condition ]  │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │ [ context ]
                                                           ▼
┌──────────────────────────────────────────────────────────┴────────────────────────────────┐┌────────────────────┐
│ GATHERING RULES, EXAMPLES, AND PRIORS                                                     ││ L4 ARCHIVE         │
│ ┌──────────────────────┐┌───────────────────────┐┌──────────────────┐┌───────────────────┐││ Read-only source   │
│ │ M1 STANDARD CHECKLIST││ M2 SAFETY / POLICY    ││ M3 PAST EXAMPLES ││ M4 PRE-APPROV TEMP│││ - Guardrails       │
│ │ - task schemas       ││ - compliance bounds   ││ - prior good ans ││ - bound plan arche│││ - standard ops     │
│ │ - route heuristics   ││ - escalation threshold││ - SOPs / exemplar││ - safe decomp habi│││ - prior examples   │
│ │ - output contracts   ││ - disallowed actions  ││ - valid succ stat││ - stopping rules  │││ - approved plans   │
│ │ - normal plan pattern││ - policy-safe bounds  ││ - clear succ mode││ - low viable agenc│││ - structure refs   │
│ └──────────┬───────────┘└──────────┬────────────┘└────────┬─────────┘└─────────┬─────────┘│└────────────────────┘
│         [load]                  [bound]                [merge]              [bundle]      │
│            └───────────────────────┴──────────────────────┴────────────────────┘          │
│                                                          ▼                                │
│                     [ plan bundle = schemas + policy + exemplars + priors + approved patterns + limits ]        │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                           │ [ reason ]
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ THE THINKING DESK (L1 REASONING LOOP)                                                                           │
│ invariant: internal non-linearity stays here only. L1 can draft, inspect, refine, simplify, or abstain, but     │
│ cannot execute.                                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────┐┌────────────────────────────────┐┌──────────────────────────────────┐ │
│ │ T1 CONTEXTUAL REFINEMENT OF REQUEST   ││ T2 SIMULTANEOUS ATTENTION PASS ││ T3 POST-ATTENTION SHARPENING     │ │
│ │ - visible tokens enter with x_i       ││ - q_i = x_i W_Q                ││ - Residual 1: x_i + z_i          │ │
│ │ - positional encoding marks order     ││ - k_i = x_i W_K                ││ - Norm 1 stabilizes feature scale│ │
│ │ - request is read as one visible set  ││ - v_i = x_i W_V                ││ - FFN sharpens each token indep. │ │
│ │ - no routing authority here           ││ - heads compare visible tokens ││ - Res 2 + Norm 2 prepare next    │ │
│ └───────────────────┬───────────────────┘└────────────────┬───────────────┘└────────────────┬─────────────────┘ │
│                  [project]                              [mix]                           [sharpen]               │
│                     └─────────────────────────────────────┼─────────────────────────────────┘                   │
│                                                           ▼                                                     │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ T4 WHAT THE MODEL IS DOING INTERNALLY                                                                       │ │
│ │ - affinity scores: s_i,j = q_i • k_j^T                                                                      │ │
│ │ - attention weights: w_i,j = exp(s_i,j) / Σ exp(s_i,k)                                                      │ │
│ │ - context mix: z_i = Σ (w_i,j * v_j)                                                                        │ │
│ │ - result: the planner's token states become more contextualized before decomposition begins                 │ │
│ │ - invariant: this is internal model interpretation, not retrieval, not route commitment, not execution      │ │
│ └─────────────────────────────────────────────────────────┬───────────────────────────────────────────────────┘ │
│                                                           │ [ interpret ]                                       │
│                                                           ▼                                                     │
│ ┌───────────────────────────┐┌───────────────────────────┐┌───────────────────────────────────────────────────┐ │
│ │ P1 BREAK INTO BABY STEPS  ││ P2 PUT IN ORDER           ││ P3 PICK THE AISLES                                │ │
│ │ - atomic work units       ││ - sequential vs parallel  ││ - proposed routes only                            │ │
│ │ - sub-goal boundaries     ││ - what unlocks what       ││ - R1 cache path if policy allows                  │ │
│ │ - missing-info markers    ││ - dependency graph        ││ - R3 grounded context path if needed              │ │
│ │ - explicit unknowns       ││ - stopping points         ││ - R4 external action path if needed               │ │
│ └─────────────┬─────────────┘└─────────────┬─────────────┘│ - R5 fallback path if needed                      │ │
│            [split]                      [order]           │ - no route authority here                         │ │
│               └────────────────────────────┼──────────────┴─────────────────────────┬─────────────────────────┘ │
│                                            ▼                                      [map]                         │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ P4 WRITE THE DRAFT PLAN                                                                                     │ │
│ │ - proposed_route: R1 / R3 / R4 / R5 | - query_spec | - task_spec | - route_risk / confidence                │ │
│ │ - grounding_required | - missing info / clarify markers | - answer support expectation                      │ │
│ └─────────────────────────────────────────────────────────┬───────────────────────────────────────────────────┘ │
│                                                           │ [ inspect ]                                         │
│                                                           ▼                                                     │
│ ┌─────────────────────────────┐┌──────────────────────────────┐┌──────────────────────────────────────────────┐ │
│ │ V1 DID WE LISTEN?           ││ V2 IS IT SAFE?               ││ V3 DOES IT MAKE SENSE?                       │ │
│ │ - answers the actual goal   ││ - within policy bounds       ││ - dependencies resolve                       │ │
│ │ - respects all constraints  ││ - escalation if needed       ││ - coherent sub-task order                    │ │
│ │ - right deliverable / format││ - no forbidden action propose││ - admits what is unknown                     │ │
│ └──────────────┬──────────────┘└──────────────┬───────────────┘└───────────────────────┬──────────────────────┘ │
│             [check]                        [check]                                  [check]                     │
│                └──────────────────────────────┼────────────────────────────────────────┘                        │
│                               ┌───────────────┴───────────────┐                                                 │
│                               ▼                               ▼                                                 │
│ ┌────────────────────────────────────────┐ ┌────────────────────────────────────────────────────────────────┐   │
│ │ V4 CAN IT BE SIMPLER?                  │ │ V5 SHOULD WE ABSTAIN OR CLARIFY?                               │   │
│ │ - lowest viable agency                 │ │ - insufficient support path                                    │   │
│ │ - no over-complication                 │ │ - clarify if missing critical detail                           │   │
│ │ - erase and restart if weak            │ │ - abstain if bounded completion impossible                     │   │
│ └───────────────────┬────────────────────┘ └────────────────────────────────┬───────────────────────────────┘   │
│                  [check]                                                 [check]                                │
│                     └─────────────────────────────────┬─────────────────────┘                                   │
│                                                       ▼                                                         │
│                    [ pass -> approve | fail -> refine / simplify / clarify / abstain ]                          │
└───────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                        │ [ output ]
                                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L1 PLAN OUTPUT CONTRACT                                                                                         │
│ - proposed_route: R1 / R3 / R4 / R5 | - query_spec | - task_spec | - route_risk / confidence                    │
│ - grounding_required | - declared assumptions / unresolved gaps                                                 │
│ invariant: L1 produces the notepad plan only. It does not retrieve evidence, route with authority, or perform   │
│ the work.                                                                                                       │
└───────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                        │ [ handoff ]
                                                        ▼
                                         [ Send to Hallway Director [3] ]