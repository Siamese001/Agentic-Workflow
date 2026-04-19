================================================================================================================================================================================
[ ABOVE HITL CONTEXT | v25 handoff from top flow / Front Desk Dispatcher ]
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INPUT TO HITL = ESCALATE(reason_code, reviewer_packet)
reason_code   = POLICY_CONFLICT | LOW_CONFIDENCE_AMBIGUITY | HUMAN_MODIFICATION_NEEDED | SILENT_FAILURE_REPLAY
packet        = prompt slice + retrieved evidence + policy state + execution trace + proposed disposition + replay handles
INVARIANT     = Human interaction begins only here
================================================================================================================================================================================
                                                                        │
                                                                        ▼


================================================================================================================================================================================
[ HITL v25 | Secure Reading Room ]
================================================================================================================================================================================

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ENTRY AIRLOCK + MATERIALIZATION | Intake Counter -> Secure Reading Room                                                                                              │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ H1: Freeze Runtime                                                                                                                                                   │
│     - authority_state     = FROZEN                                                                                                                                   │
│     - write_authority     = NONE                                                                                                                                     │
│     - tool_execution      = DISABLED                                                                                                                                 │
│     [INVARIANT: no tool use, no live mutation, no UWG write authority]                                                                                               │
│                                                                                                                                                                      │
│ H2: Context Materialization                                                                                                                                          │
│     - reason_code                                                                                                                                                    │
│     - proposed answer / action / patch                                                                                                                               │
│     - evidence packet                                                                                                                                                │
│     - policy state                                                                                                                                                   │
│     - execution trace / determinism receipts                                                                                                                         │
│     [INVARIANT: human sees a bounded packet, not unconstrained runtime state]                                                                                        │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                        │
                                                                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HUMAN REVIEW CORE | Review Desk + Redline Table                                                                                                                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ H3: Human Review                                                                                                                                                     │
│     - inspect evidence                                                                                                                                               │
│     - inspect policy outcomes                                                                                                                                        │
│     - inspect proposed answer / action                                                                                                                               │
│     - inspect replay packet when reason_code = SILENT_FAILURE_REPLAY                                                                                                 │
│                                                                                                                                                                      │
│ H4: Human Decision Artifact                                                                                                                                          │
│     decision = APPROVE | MODIFY_DIFF | REJECT                                                                                                                        │
│     artifact = signed review packet + rationale + optional diff                                                                                                     │
│                                                                                                                                                                      │
│ [INVARIANT: human input is DATA, not authority]                                                                                                                      │
│ [INVARIANT: human input remains UNTRUSTED until L5 re-clearance]                                                                                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                        │
                                                                        ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ RE-CLEARANCE + OUTBOUND DISPOSITION | Wax Seal Gate                                                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                               ┌──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┐                               │
│                               │ REJECT                           │ MODIFY_DIFF                      │ APPROVE                          │                               │
│                               │ [deny / send back]               │ [redline / patch proposal]       │ [accept bounded output]          │                               │
│                               └──────────────┬───────────────────┴──────────────┬───────────────────┴──────────────┬───────────────────┘                               │
│                                              │                                  │                                  │                                                   │
│                                              ▼                                  ▼                                  ▼                                                   │
│                               ┌────────────────────────────┐      ┌────────────────────────────┐      ┌────────────────────────────┐                               │
│                               │ RJ1: DENY / STOP           │      │ M1: Diff Ingest            │      │ A1: Route Confirmation     │                               │
│                               │ RJ2: RETURN_TO_L1          │      │ M2: L5 Re-clear + Unfreeze │      │ A2: L5 Confirmation Gate   │                               │
│                               │      forced re-plan        │      │ M3: Patch Apply            │      │                            │                               │
│                               │                            │      │ M4: Context Re-hydration   │      │ A3a: ALLOW_RESPONSE        │                               │
│                               │                            │      │ M5: RESTART_L2             │      │      response only         │                               │
│                               │                            │      │                            │      │                            │                               │
│                               │                            │      │                            │      │ A3b: COMMIT_TO_UWG         │                               │
│                               │                            │      │                            │      │      only permanent write  │                               │
│                               └────────────────────────────┘      └────────────────────────────┘      └────────────────────────────┘                               │
│                                                                                                                                                                      │
│ [INVARIANT: no path bypasses L5 re-clearance when human-authored change is introduced]                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


                                                                        │
                                                                        ▼
================================================================================================================================================================================
[ BELOW HITL CONTEXT | v25 future-run records / Archive Committee ]
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
OUTPUTS FROM HITL
- live outcome     = DENY / RETURN_TO_L1 / ALLOW_RESPONSE / COMMIT_TO_UWG / RESTART_L2
- shadow records   = decision packet + rationale + diff + reason_code + policy outcome
- future-run buses = BUS P (preference records)  |  BUS T (telemetry / replay evidence)
INVARIANT          = No HITL learning artifact mutates the current run
================================================================================================================================================================================