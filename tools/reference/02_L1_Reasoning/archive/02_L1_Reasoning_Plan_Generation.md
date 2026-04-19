=======================================================================================================================================
[2] L1 REASONING + PLAN GENERATION
[2] THE RESEARCH DESK | FIGURING OUT THE SEARCH PLAN
=======================================================================================================================================
- The senior reference librarian who reads the stamped request slip, understands the actual goal, loads the governing
  rules and priors, and writes the bounded plan that later routing may act on.
- L1 may think, decompose, compare options, and self-correct, but it never retrieves evidence directly, never routes
  with authority, never executes tools, and never mutates durable state.

                                                                  │ [ goal ]
                                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ READING THE PATRON'S SLIP                                                                                                           │
│ ┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────────────────────┐ │
│ │ I1 WHAT DO THEY WANT?    │ │ I2 WHAT ARE THEIR RULES? │ │ I3 SPECIFIC DETAILS      │ │ I4 WHAT KIND OF JOB IS THIS?             │ │
│ │ - primary objective      │ │ - hard constraints       │ │ - entities / actors      │ │ - summarize / compare                    │ │
│ │ - requested end-state    │ │ - soft constraints       │ │ - exact numbers / vars   │ │ - analyze / plan / act                   │ │
│ │ - answer / plan / artifact │ - scope / exclusions     │ │ - required output format │ │ - classify before planning               │ │
│ │ - success condition      │ │ - must / should / avoid  │ │ - explicit deliverable   │ │ - work class drives plan                 │ │
│ └─────────────┬────────────┘ └─────────────┬────────────┘ └─────────────┬────────────┘ └────────────────────┬─────────────────────┘ │
│            [parse]                      [bound]                      [merge]                             [frame]                    │
│               └────────────────────────────┴─────────────┬──────────────┴───────────────────────────────────┘                       │
│                                                          │                                                                          │
│                                                          ▼                                                                          │
│                 [ clear intent frame = goal + constraints + details + output target + work class + success condition ]              │
└──────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────┘
                                                           │ [ context ]
                                                           ▼
┌──────────────────────────────────────────────────────────┴───────────────────────────────┐  ┌────────────────────┐
│ GATHERING RULES, EXAMPLES, AND PRIORS                                                    │<─┤ L4 ARCHIVE         │
│ ┌───────────────────────┐ ┌───────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐│  │ Read-only source   │
│ │ M1 STANDARD CHECKLISTS│ │ M2 SAFETY / POLICY    │  │ M3 PAST EXAMPLES        │  │ M4 PRE-APPROVED TEMPLATES││  │ - Guardrails       │
│ │ - task schemas        │ │ - compliance bounds   │  │ - prior good answers    │  │ - bounded plan archetypes││  │ - standard ops     │
│ │ - route heuristics    │ │ - escalation thresholds │ - SOPs / exemplars      │  │ - safe decompose habits  ││  │ - prior examples   │
│ │ - output contracts    │ │ - disallowed actions  │  │ - valid success states  │  │ - stopping rules         ││  │ - approved plans   │
│ │ - normal plan patterns│ │ - policy-safe bounds  │  │ - clear success models  │  │ - lowest viable agency   ││  │ - structure refs   │
│ └───────────┬───────────┘ └───────────┬───────────┘  └────────────┬────────────┘  └────────────┬────────────┘│  └────────────────────┘
│          [load]                    [bound]                     [merge]                      [bundle]         │
│             └─────────────────────────┴───────────────────────────┼────────────────────────────┘             │
│                                                                   │                                          │
│                                                                   ▼                                          │
│                        [ plan bundle = schemas + policy + exemplars + priors + approved patterns + limits ]  │
└───────────────────────────────────────────────────────────────────┬──────────────────────────────────────────┘
                                                                    │ [ reason ]
                                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ THE THINKING DESK (L1 REASONING LOOP)                                                                                               │
│ invariant: internal non-linearity stays here only. L1 can draft, inspect, refine, simplify, or abstain, but cannot execute.         │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────┐ ┌───────────────────────────────────────────┐ ┌───────────────────────────────────────────┐ │
│ │ P1 BREAK INTO BABY STEPS                  │ │ P2 PUT IN ORDER                           │ │ P3 PICK THE AISLES                        │ │
│ │ - atomic work units                       │ │ - sequential vs parallel                  │ │ - proposed routes only                    │ │
│ │ - sub-goal boundaries                     │ │ - what unlocks what                       │ │ - grounding likely?                       │ │
│ │ - missing-info markers                    │ │ - dependency graph                        │ │ - external action likely?                 │ │
│ │ - explicit unknowns                       │ │ - stopping points                         │ │ - no route authority here                 │ │
│ └─────────────────────┬─────────────────────┘ └─────────────────────┬─────────────────────┘ └─────────────────────┬─────────────────────┘ │
│                    [split]                                       [order]                                       [map]                    │
│                       └─────────────────────────────────────────────┼─────────────────────────────────────────────┘                     │
│                                                                     ▼                                                                   │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ P4 WRITE THE DRAFT PLAN                                                                                                             │ │
│ │ - proposed_route                                                                                                                    │ │
│ │ - query_spec                                                                                                                        │ │
│ │ - task_spec                                                                                                                         │ │
│ │ - route_risk / confidence                                                                                                           │ │
│ │ - grounding_required                                                                                                                │ │
│ │ - missing info / clarify markers                                                                                                    │ │
│ │ - answer support expectation                                                                                                        │ │
│ └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                     │ [ inspect ]                                                       │
│                                                                     ▼                                                                   │
│ ┌───────────────────────────────────────────┐ ┌───────────────────────────────────────────┐ ┌───────────────────────────────────────────┐ │
│ │ V1 DID WE LISTEN?                         │ │ V2 IS IT SAFE?                            │ │ V3 DOES IT MAKE SENSE?                    │ │
│ │ - answers the actual goal                 │ │ - within policy bounds                    │ │ - dependencies resolve                    │ │
│ │ - respects all constraints                │ │ - escalation if needed                    │ │ - coherent sub-task order                 │ │
│ │ - right deliverable / format              │ │ - no forbidden action proposed            │ │ - admits what is unknown                  │ │
│ └─────────────────────┬─────────────────────┘ └─────────────────────┬─────────────────────┘ └─────────────────────┬─────────────────────┘ │
│                    [check]                                       [check]                                     [check]                    │
│                       └─────────────────────────────────────────────┼─────────────────────────────────────────────┘                     │
│                                                                     │                                                                   │
│                                  ┌──────────────────────────────────┴──────────────────────────────────┐                                │
│                                  ▼                                                                     ▼                                │
│ ┌────────────────────────────────────────────────────────────────┐  ┌────────────────────────────────────────────────────────────────┐  │
│ │ V4 CAN IT BE SIMPLER?                                          │  │ V5 SHOULD WE ABSTAIN OR CLARIFY?                               │  │
│ │ - lowest viable agency                                         │  │ - insufficient support path                                    │  │
│ │ - no over-complication                                         │  │ - clarify if missing critical detail                           │  │
│ │ - erase and restart if weak                                    │  │ - abstain if bounded completion impossible                     │  │
│ └────────────────────────────────┬───────────────────────────────┘  └────────────────────────────────┬───────────────────────────────┘  │
│                               [check]                                                             [check]                               │
│                                  └──────────────────────────────────┬──────────────────────────────────┘                                │
│                                                                     ▼                                                                   │
│                                 [ pass -> approve | fail -> refine / simplify / clarify / abstain ]                                     │
└─────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                                      │ [ output ]
                                                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ L1 PLAN OUTPUT CONTRACT                                                                                                             │
│ - proposed_route                                                                                                                    │
│ - query_spec                                                                                                                        │
│ - task_spec                                                                                                                         │
│ - route_risk / confidence                                                                                                           │
│ - grounding_required                                                                                                                │
│ - declared assumptions / unresolved gaps                                                                                            │
│ invariant: L1 produces the notepad plan only. It does not retrieve evidence, route with authority, or perform the work.             │
└─────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                                      │ [ handoff ]
                                                                      ▼
                                                       [ Send to Hallway Director [3] ]