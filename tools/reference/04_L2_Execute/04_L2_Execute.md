========================================================================================================================================
[4] LIVE TASK DISPATCH & EXECUTION
[4] THE BACK ROOMS | DOING THE WORK (IN THE STACKS)
========================================================================================================================================
- The active phase where the bounded work is done, but nothing is permanently written yet.
- Library Analogy: assistants enter the restricted stacks to gather, run, repair, and seal findings under the exact same
  blueprint and policy snapshot. They cannot route, ask humans, or write in the permanent catalog.

                                                                     │ [ governed handoff ]
                                                                     ▼
                                           ┌─────────────────────────┴─────────────────────────┐
                                           ▼                                                   ▼
                                 ┌──────────────────────────┐                        ┌──────────────────────────┐
                                 │ QUICK LOOKUP             │                        │ DEEP RESEARCH            │
                                 │ single work unit         │                        │ multi-step chain         │
                                 └─────────────┬────────────┘                        └─────────────┬────────────┘
                                            [merge]                                             [merge]
                                               └─────────────────────────┬─────────────────────────┘
                                                                      [order]
                                                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ GLOBAL L2 INVARIANTS                                                                                                                 │
│ [!] No routing, no human interaction, no durable commit authority                                                                    │
│ [!] VALIDATE and HEAL read the SAME blueprint_hash / policy_hash snapshot                                                            │
│ [!] No direct write bypass to L4. Any raw write attempt is a gravity breach and is blocked                                           │
│ [!] Packet arrives already governed with compliance_hash / capability_token / sandbox_envelope                                       │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     ▼
                              [ UPSTREAM L0 / L3 ] ──(Signed Packet)──► [ INGRESS: authorize_and_execute() ]
                                                                     │
                                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E1: PRE-COMMIT / PREP DESK                                                                                                           │
│ [ Intake Counter ] ──► [ Freeze Env/Caps/Budget ] ──► [ Bind Idempotency Key ] ──► [ Bind Blueprint Hashes ] ──► [ Lineage Root ]    │
│ - env / caps / budget locked       - unique execution key        - blueprint_hash / policy_hash                                      │
│ - tools / permissions frozen       - duplicate suppression       - same snapshot for heal                                            │
│ - no live write authority          - same run identity           - attempt seed / ancestry chain                                     │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     │
                                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E2: VALIDATE / WORK ORDER CHECK                                                                                              │
│ < Integrity & Signature Chain >  ──(FAIL)────────────────────────────────────────────────────────────────────────────────────┼───────┐
│ < Cap Scope & Env Budget >       ──(FAIL)────────────────────────────────────────────────────────────────────────────────────┼─────┐ │
│ < Schema & Side-Effect Class >   ──(FAIL)────────────────────────────────────────────────────────────────────────────────────┼───┐ │ │
│ < Mutation Type Sanity >         ──(FAIL)────────────────────────────────────────────────────────────────────────────────────┼─┐ │ │ │
│                                                                                                                              │ │ │ │ │
│ PASS -> emit sealed validation_packet_id                                                                                     │ │ │ │ │
│ FAIL -> sealed rejection before any work starts                                                                              │ │ │ │ │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘ │ │ │ │
                                                                     │                                                           │ │ │ │
                                                                     ▼                                                           │ │ │ │
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐ │ │ │ │
│ E3: EXECUTE / DOING THE WORK                                                                                                 │ │ │ │ │
│ [ Attempt Count++ ] ──► [ Invoke Tool / Model ] ──(Timeout / Circuit Breaker)──► [ Capture Output ] ──► [ Result Classifier] │ │ │ │ │
│ - bounded invocation           - isolated execution         - stdout / stderr / return codes                                 │ │ │ │ │
│ - same-run lineage             - policy-bound capability    - interim receipts / state diff                                  │ │ │ │ │
│ - execution telemetry          - sandbox isolation          - classify SUCCESS / SOFT_REPAIRABLE / FAIL_TERMINAL             │ │ │ │ │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────┘ │ │ │ │
                                                                     │                                                           │ │ │ │
                               ┌─────────────────────────────────────┼─────────────────────────────────────┐                     │ │ │ │
                               │                                     │                                     │                     │ │ │ │
                          [ success ]                           [ repair ]                            [ terminal ]               │ │ │ │
                               │                                     ▼                                     │                     │ │ │ │
                               │  ┌─────────────────────────────────────────────────────────────────────┐  │                     │ │ │ │
                               │  │ E4: HEAL LOOP / FIXING MISTAKES                                     │  │                     │ │ │ │
                               │  │ - log precise reason_code        - require parent_packet_id         │  │                     │ │ │ │
                               │  │ - localize failure               - bounded SSOT repair only         │  │                     │ │ │ │
                               │  │ - verify hash / replay integrity - repair_count++                   │  │                     │ │ │ │
                               │  │ - check oscillation / retry threshold                               │  │                     │ │ │ │
                               │  │ PASS -> back to E3 under same blueprint_hash / policy_hash          │  │                     │ │ │ │
                               │  │ FAIL -> ESCALATE_ARTIFACT or FAIL_TERMINAL                          │  │                     │ │ │ │
                               │  └─────────────────────────────────────────────────────────────────────┘  │                     │ │ │ │
                               │                                                                           │                     │ │ │ │
                               └─────────────────────────────────────┬─────────────────────────────────────┘                     │ │ │ │
                                                                     │                                                           │ │ │ │
                                                                     ├───────────────────────────────────────────────────────────┴─┴─┴─┘
                                                                     │
                                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E5: SEAL THE FINAL FOLDER / SEAL OUTPUT                                                                                              │
│ [ Package Payload ] ──► [ Attach Traces / Lineage ] ──► [ Attach Replay Receipts & Counters ] ──► [ Seal L2 Artifact ]               │
│ - final answer / artifact             - traces / ancestry             - replay keys / validation counters                            │
│ - notes / evidence                    - execution lineage             - deterministic proof / attempt receipts                       │
│ - state diff / output payload         - reason codes                  - terminal class = SUCCESS / FAIL / ESCALATE / REJECTED        │
│ invariant: no durable commit here. L2 only emits sealed artifacts for downstream control.                                            │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                [ handoff ]
                                                                     ▼
                                      [ DISPATCH TO POST-L2 CONTROL + EVALUATION + DISPOSITION [5] ]