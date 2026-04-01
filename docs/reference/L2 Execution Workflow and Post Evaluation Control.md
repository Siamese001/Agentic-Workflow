L2 EXECUTION WORKFLOW AND POST-EVALUATION CONTROL FRAMEWORK
================================================================================================================================================================================
[ TRIPLE-CLICK HARDENED | v25 RIGID STRUCTURE | L2 ONLY ]
================================================================================================================================================================================

│ ┌──────────────────────────────────┐
│ │ L3 ORCHESTRATOR [opt] (Sec Head) │
│ └───────────────┬──────────────────┘
│                 ▼ [EXECUTE]
│ ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ │  L2 EXECUTION (Execution Staff | Secure Workroom)                                                                                                            │
│ ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ │ [ SCOPE RULES ] Execute only | No routing | No policy mutation | No direct archive write | No human interaction | No durable authority                   │
│ │ [ CHOKEPOINT ] authorize_and_execute() on EVERY call                                                                                                         │
│ │ [ ISOLATION   ] DockerSandbox.run_code() / FirecrackerManager                                                                                                │
│ │ [ EGRESS      ] SovereignLLMGateway only for approved model calls                                                                                            │
│ │ [ PROTOCOL    ] PRE_COMMIT -> VALIDATE -> EXECUTE -> HEAL -> SEAL                                                                                            │
│ │ [ INVARIANT   ] L2 may emit WRITE_INTENT only; it never owns COMMIT                                                                                          │
│ │ [ INVARIANT   ] C0 is NOT inside L2; context is already assembled before entry                                                                               │
│ │                                                                                                                                                              │
│ │   ┌────────────────────────────┐    ┌────────────────────────────┐    ┌────────────────────────────┐    ┌────────────────────────────┐                 │
│ │   │ E1: PRE_COMMIT             │ -> │ E2: VALIDATE               │ -> │ E3: EXECUTE               │ -> │ E4: HEAL LOOP             │                 │
│ │   │ Intake Counter             │    │ Perimeter Check            │    │ Tool Bench                │    │ Repair Bay                │                 │
│ │   ├────────────────────────────┤    ├────────────────────────────┤    ├────────────────────────────┤    ├────────────────────────────┤                 │
│ │   │ - accept signed L0/L3 pkt  │    │ - verify signature chain   │    │ - invoke approved tools   │    │ - classify failure        │                 │
│ │   │ - bind CapToken + budget   │    │ - enforce CapToken scope   │    │ - enforce schema I/O      │    │ - local repair first      │                 │
│ │   │ - freeze runtime state     │    │ - validate sandbox policy  │    │ - declare effect class    │    │ - bounded retries only    │                 │
│ │   │ - mount isolated env       │    │ - validate arg contracts   │    │ - capture stdout/stderr   │    │ - escalate failure packet │                 │
│ │   │ - assign exec_run_id       │    │ - enforce tool budget      │    │ - capture exit code       │    │ - no silent swallow       │                 │
│ │   └──────────────┬─────────────┘    └──────────────┬─────────────┘    └──────────────┬─────────────┘    └──────────────┬─────────────┘                 │
│ │                  │                                 │                                 │                                 │                               │
│ │                  └─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘                               │
│ │                                                                                      │                                                               │
│ │                                                                                      ▼                                                               │
│ │                                                   ┌────────────────────────────────────────────┐                                                     │
│ │                                                   │ E5: SEAL OUTPUT                            │                                                     │
│ │                                                   │ Evidence Envelope / Carbon Copy            │                                                     │
│ │                                                   ├────────────────────────────────────────────┤                                                     │
│ │                                                   │ - result_payload / structured tool outputs │                                                     │
│ │                                                   │ - ExecTrace                                │                                                     │
│ │                                                   │ - StateDiff                                │                                                     │
│ │                                                   │ - declared_effects                         │                                                     │
│ │                                                   │ - replay_receipts / determinism digest     │                                                     │
│ │                                                   │ - WRITE_INTENT payload, if any             │                                                     │
│ │                                                   │ - failure_packet, if unresolved            │                                                     │
│ │                                                   │ [ INVARIANT: sealed output only ]          │                                                     │
│ │                                                   │ [ INVARIANT: NO response release here ]    │                                                     │
│ │                                                   │ [ INVARIANT: NO commit here ]              │                                                     │
│ │                                                   └──────────────────────┬─────────────────────┘                                                     │
│ └──────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────┘
│                                                                            ▼ [L2 EXECUTION OUTPUT]
└────────────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────
                                                                             │
=============================================================================┼=============================================================================================
[5] POST-L2 CONTROL + EVALUATION                                             │
=============================================================================┼=============================================================================================
                                                                             ▼
                                      ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
                                      │ LIVE EVALUATION SPINE (Current-run judgment | Checkout Inspectors)                                                   │
                                      ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
                                      │ - policy checks                                                                                                      │
                                      │ - schema / sandbox validity                                                                                          │
                                      │ - outcome checks                                                                                                     │
                                      │ - trajectory checks                                                                                                  │
                                      │ - release-time regression checks                                                                                     │
                                      │ - mutation authorization check against WRITE_INTENT                                                                  │
                                      └──────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────┘
                                                                                     ▼
                                      ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
                                      │ EXIT SPINE (Disposition Authority | Checkout Desk)                                                                   │
                                      ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
                                      │ ALLOW_RESPONSE  -> release bounded output only                                                                       │
                                      │ DENY / REROUTE  -> return to L1/L0 with failure packet                                                               │
                                      │ ESCALATE       -> HITL only                                                                                          │
                                      │ COMMIT         -> UWG only                                                                                           │
                                      │ [ INVARIANT: all human interaction begins only at ESCALATE ]                                                         │
                                      │ [ INVARIANT: all durable mutation begins only at COMMIT -> UWG ]                                                     │
                                      └──────────────┬───────────────────────────────┬───────────────────────────────┬─────────────────────────────────────┘
                                                     │                               │                               │
                                                     ▼                               ▼                               ▼
                                            [ALLOW_RESPONSE]                    [DENY / REROUTE]               [COMMIT -> UWG -> L4]

                                                                           ┌─────────────────────────┐
                                                                           │ HITL (Secure Reading    │
                                                                           │ Room / Human Review)    │
                                                                           └────────────┬────────────┘
                                                                                        ▼
                                                                           [ APPROVE -> back to EXIT ] | [ MODIFY_DIFF -> L5 re-clear -> RESTART_L2 ] | [ REJECT -> DENY ]