│ [ Sealed L2 Artifacts ] OR [RET] Short-Circuit from L0       │ [ Cross-Cutting L5 ]
                                ▼                                                              │
┌──────────────────────────────────────────────────┐                                           │
│ 5. EXIT EVAL & CONTROL                           ├───────[commit request]────────────────────┼────────────────────► ┌────────────────────────────────────────┐
│ [ THE SEALED FOLDER (L2) OR [RET] (L0) ]         │                                           │                      │ X3C COMMIT REQUEST -> UWG              │
│ - ExecTrace / StateDiff / evidence bundle        │                                           │                      │ U1 VERIFY BOSS: sig, cap token, hash   │
│ - validation counters / terminal classification  │                                           │                      │ U2 CHECK CATALOG: scope, RBAC, diff    │
│                                                  │                                           │                      │ U3 MAKE COPY: durable commit, heal,    │
│ X1 CURRENT-RUN EVALUATION                        │                                           │                      │    hash-chain append, audit sync       │
│ ┌──────────────────────┐ ┌─────────────────────┐ │                                           │                      │ invariant: UWG is the sole ink path    │
│ │ X1A TODAY'S RULES?   │ │ X1B ANSWERED IT?    │ │                                           │                      │ into L4. No direct L2/HITL writes.     │
│ │ - baselines & policy │ │ - prompt/format fit │ │                                           │                      └───────────────────┬────────────────────┘
│ └──────────────────────┘ │ - schema complete   │ │                                           │                                          │
│ ┌──────────────────────┐ └─────────────────────┘ │                                           │                                          │ [commits]
│ │ X1C SAFE TO LEAVE?   │ ┌─────────────────────┐ │                                           │                                          ▼
│ │ - sandbox isolation  │ │ X1D ANSWER GOOD?    │ │                                           │                      ┌────────────────────────────────────────┐
│ │ - mutation auth      │ │ - groundedness      │ │                                           │                      │ L4 ARCHIVE                             │
│ │ - env integrity      │ │ - citation support  │ │                                           │                      │ (Durable Writes / Ledger)              │
│ └──────────────────────┘ └─────────────────────┘ │                                           │                      └────────────────────────────────────────┘
│ invariant: live runtime disposition is explicit. │                                           │
│ No silent fallbacks, no ungated human changes.   │                                           │
└───────┬─┬─┬──────────────────────────────────────┘                                           │
        │ │ │                                                                                  │
        │ │ │                                                                                  │
        │ │ └─[deny/reroute] ──► ┌────────────────────────────────┐                            │
        │ │                      │ X3A DENY / REROUTE             │                            │
        │ │                      │ - hard rule brk / fail eval    │                            │
        │ │                      │ - replan L1/L0                 │                            │
        │ │                      └────────────────────────────────┘                            │
        │ │                                                                                    │
        │ └─[escalate] ────────► ┌─────────────────────────────────────────────────────┐       │
        │  reason_code =         │ X3B ESCALATE / HUMAN REVIEW                     │       │
        │  POLICY_CONFLICT /     │ H1 Freeze: auth_state=FROZEN | write_auth=NONE      │       │
        │  AMBIGUITY /           │ H2 Materialize: bounded packet (reason + evidence)  │       │
        │  SILENT_FAILURE        │ H3 Human Review: inspect evidence, action, replay   │       │
        │                        │ H4 Decision: APPROVE | MODIFY_DIFF | REJECT         │       │
        │                        │ invariant: human input = untrusted DATA             │       │
        │                        ├─────────────────────────────────────────────────────┤       │
        │                        │ L5 RE-CLEARANCE GATE                                │       │
        │                        │ - REJECT -> DENY / STOP or RETURN_TO_L1             │       │
        │                        │ - MODIFY_DIFF -> L5 Re-clear -> Re-hydrate -> RESTART │      │
        │                        │ - APPROVE -> L5 Confirm -> ALLOW or COMMIT          │       │
        │                        │ invariant: no human change bypasses L5 re-clear     │       │
        │                        └───────┬─────────────────────────────────────────────┘       │
        │                                │                                                     │
        │                                └─(resume/allow)──────────────────────────────────────┼────┐
        │                                                                                      │    │
        │ [allow/finish]                                                                       │    │
        ▼                                                                                      │    │
┌──────────────────────────────────────────────────┐                                           │    │
│ X3D ALLOW / FINISH -> RESPONSE / OUTCOME         │◄──────────────────────────────────────────┼────┘
│ - patron answer only (no durable write here)     │                                           │
└───────────────────────┬──────────────────────────┘                                           │
                        │                                                                      │
                        ▼                                                                      │
            [ RETURN TO CALLER (U0) ]                                                          │
        (Runtime Evidence & Committed L4 Artifacts)                                            │
                        │                                                                      │
                        │                                      [ ASYNC RUNTIME DATA EXHAUST ]  │
                        └───────(Gathered from all layers: Traces, Artifacts, diffs, reason_codes, policy grades)
                                (future-run buses = BUS P [pref/grades] & BUS T [telem/trace])         │
                                (invariant: learning signals do not mutate current run)                │
                                                                               │                       │
███████████████████████████████████████████████████████████████████████████████▼███████████████████████▼████████████████████████████████████████████████████████
██ ◄──────────────────────────────────────────────────────────── R U N T I M E   B O U N D A R Y ────────────────────────────────────────────────────────────► ██
████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
                                                                               │
                                                               [ SEND TO AFTER-HOURS REVIEW [6] ]
