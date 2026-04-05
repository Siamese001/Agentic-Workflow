====================================================================================================================================
[5] LIVE RUNTIME EXIT CONTROL + CURRENT-RUN EVALUATION
[5] CHECK-OUT DESK / FINAL SECURITY REVIEW
====================================================================================================================================
- The final current-run checkpoint that judges whether the sealed work is safe, complete, grounded, replayable, and authorized
  for response, human escalation, or durable commit.
- The head librarian reviews the sealed folder, consults the current rules, and decides whether to hand the answer to the patron,
  send it to a human review room, deny it, or forward a commit request to the vault clerk.

                                                                 │ [ input ]
                                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ THE SEALED FOLDER (From L2)                                                                                                      │
│ - ExecTrace / StateDiff / evidence bundle / validation counters / terminal classification                                        │
└────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                             [ inspect ]
                                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ X1 CURRENT-RUN EVALUATION                                                                                                        │
│ ┌───────────────────────────┐ ┌───────────────────────────┐ ┌───────────────────────────┐ ┌────────────────────────────────────┐ │
│ │ X1A WHAT ARE TODAY'S      │ │ X1B DID WE ANSWER IT?     │ │ X1C IS IT SAFE TO LEAVE?  │ │ X1D IS THE ANSWER GOOD?            │ │
│ │ RULES / RUBRICS?          │ │ - prompt / format fit     │ │ - policy pass / fail      │ │ - groundedness                     │ │
│ │ - active baselines        │ │ - answer / artifact fit   │ │ - revealing secrets?      │ │ - citation support                 │ │
│ │ - user ask / success      │ │ - paperwork complete      │ │ - mutation authorization  │ │ - answer relevance                 │ │
│ │ - current policy refs     │ │ - schema complete         │ │ - env integrity           │ │ - abstain correctness              │ │
│ │                           │ │                           │ │ - replay env completeness │ │ - escalation correctness           │ │
│ └─────────────┬─────────────┘ └─────────────┬─────────────┘ └─────────────┬─────────────┘ └─────────────────┬──────────────────┘ │
│            [score]                       [score]                       [merge]                           [decide]                │
└────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────┘
                                                              [ gate ]
                                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ X2 FINAL EXIT GATES                                                                                                              │
│ ALLOW_RESPONSE | DENY / RETURN | ESCALATE_TO_HITL | COMMIT_TO_UWG                                                                │
│ invariant: live runtime disposition is explicit. No silent fallbacks, no hidden commit path, no ungated human modification.      │
└───────┬─────────────────────────────────────────┬────────────────────────────────────────┬────────────────────────┬──────────────┘
    [ deny ]                                 [ escalate ]                              [ commit ]               [ allow ]
        ▼                                         ▼                                        ▼                        ▼
┌───────────────┐                  ┌──────────────────────────────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│X3A DENY/RETURN│                  │ X3B HITL | SECURE READING ROOM               │ │X3C UWG COMMIT REQUEST│ │X3D RESPONSE / OUTCOME│
│- hard rule brk│                  │ reason_code = POLICY_CONFLICT                │ │- permanent write req │ │- patron answer only  │
│- fail evaluate│                  │   | LOW_CONFIDENCE_AMBIGUITY                 │ │- durable path via UWG│ │- no durable write    │
│- replan L1/L0 │                  │   | HUMAN_MODIFICATION_NEEDED                │ │                      │ │                      │
└───────┬───────┘                  │   | SILENT_FAILURE_REPLAY                    │ └──────────┬───────────┘ └──────────┬───────────┘
        │                          └──────────────────────┬───────────────────────┘            │                        │
        │                                                 │                                    │                        │
        │                                                 ▼                                    │                        │
        │                  ┌───────────────────────────────────────────────────────────────┐   │                        │
        │                  │ HITL AIRLOCK + MATERIALIZATION                                │   │                        │
        │                  │ H1 Freeze: authority_state=FROZEN | write_auth=NONE           │   │                        │
        │                  │ H2 Materialize packet: reason_code + evidence + policy state  │   │                        │
        │                  │ invariant: human sees bounded packet, not unconstrained state │   │                        │
        │                  └──────────────────────────────┬────────────────────────────────┘   │                        │
        │                                                 │                                    │                        │
        │                                                 ▼                                    │                        │
        │                  ┌───────────────────────────────────────────────────────────────┐   │                        │
        │                  │ HUMAN REVIEW CORE                                             │   │                        │
        │                  │ H3 Human Review: inspect evidence, proposed action, replay    │   │                        │
        │                  │ H4 Decision: APPROVE | MODIFY_DIFF | REJECT + rationale       │   │                        │
        │                  │ invariant: human input is DATA, untrusted until L5 re-clear   │   │                        │
        │                  └──────────────────────────────┬────────────────────────────────┘   │                        │
        │                                                 │                                    │                        │
        │                                                 ▼                                    │                        │
        │                  ┌───────────────────────────────────────────────────────────────┐   │                        │
        │                  │ HITL RE-CLEARANCE + OUTBOUND DISPOSITION                      │   │                        │
        │◄─────────────────┤ REJECT      -> DENY / STOP or RETURN_TO_L1                    │   │                        │
        │                  │ MODIFY_DIFF -> L5 Re-clear -> Context Re-hydrate -> RESTART   │   │                        │
        │                  │ APPROVE     -> L5 Confirmation Gate -> ALLOW or COMMIT ───────┼───┼───────────────────────►┤
        │                  │ invariant: no human change bypasses L5 re-clear               │   │                        │
        │                  └───────────────────────────────────────────────────────────────┘   │                        │
        │                                                                                      │                        │
        │                                                                                      ▼                        │
        │                         ┌────────────────────────────────────────────────────────────────────────────────────────┐    │
        │                         │ UWG / VAULT CLERK PATH                                                                 │    │
        │                         │ U1 VERIFY THE BOSS                                                                     │    │
        │                         │ - verify signature / compliance_hash / active policy_hash                              │    │
        │                         │ - verify capability token and allowed capability set                                   │    │
        │                         │ U2 CHECK CATALOG RULES                                                                 │    │
        │                         │ - scope / RBAC / blast radius                                                          │    │
        │                         │ - mutation authorization and before/after diff                                         │    │
        │                         │ - compute replay key and HMAC seal                                                     │    │
        │                         │ U3 MAKE THE COPY                                                                       │    │
        │                         │ - claim sole write lock                                                                │    │
        │                         │ - execute durable commit and hash-chain append                                         │    │
        │                         │ - rollback / heal on failure                                                           │    │
        │                         │ - refresh read surfaces / alias swap / audit sync                                      │    │
        │                         │ invariant: UWG is the only ink path into L4. No direct L2/HITL write path.             │    │
        │                         └───────────────────────────────────────────────────────────────────┬────────────────────┘    │
        │                                                                                             │                         │
        ▼                                                                                             ▼                         ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CURRENT VISIT CLOSED                                                                                                             │
│ outcome = DENY / RETURN_TO_L1 / ALLOW_RESPONSE / COMMIT_TO_UWG / RESTART_L2                                                      │
│ shadow records = decision packet + rationale + diff + reason_code + policy outcome                                               │
│ future-run buses = BUS P (preferences / grades) and BUS T (telemetry / replay evidence)                                          │
│ invariant: learning signals are recorded for later only and do not mutate the current completed run                              │
└────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                            [ paperwork ]
                                                                 ▼
                                                 [ SEND TO AFTER-HOURS REVIEW [6] ]