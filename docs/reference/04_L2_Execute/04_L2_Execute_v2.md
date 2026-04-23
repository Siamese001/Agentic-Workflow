========================================================================================================================================
[4] L2 EXECUTE (Assistant)
[4] THE BACK ROOMS | DOING THE WORK (IN THE STACKS)
========================================================================================================================================
- The active phase where the bounded work is done, but nothing is permanently written yet.
- Library Analogy: assistants enter the restricted stacks to gather, run, repair, and seal findings under the exact same
  blueprint and policy snapshot. They cannot route, ask humans, or write in the permanent catalog.

                  [ SINGLE-STEP ROUTES ]                                      [ MANAGED WORKFLOW ROUTES ]
        [ L0: R3 Simple Grounded Read / R4 Single Action ]                  [ L0 -> L3 Orchestrate ]
                              │                                                          │
                              │ [ one bounded execution packet ]                         │ [ current bounded step contract ]
                              ▼                                                          ▼
                           ┌───────────────────────────────┬───────────────────────────────┐
                           ▼                               ▼                               ▼
                 ┌───────────────────┐           ┌───────────────────┐           ┌───────────────────┐
                 │ SIMPLE TASK       │           │ COMPLEX TASK      │           │ RESUMED STEP      │
                 │ single work unit  │           │ first active node │           │ next ready node   │
                 └─────────┬─────────┘           └─────────┬─────────┘           └─────────┬─────────┘
                           │                               │                               │
                           └─────────────────────┬─────────┴─────────┬─────────────────────┘
                                                 │ [ approved work order / signed packet ]
                                                 ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ TASK EXECUTION CORE                                                                                                                  │
│ Strict Rules: No human help | No permanent updates | Same blueprint/policy snapshot end-to-end                                      │
│ [!] No routing, no durable commit authority, no bypass to L4                                                                         │
│ [!] Packet arrives already governed with route contract outputs: compliance_hash / capability_token / sandbox_envelope              │
│ [!] Input may originate from L0 directly or from L3 as the current executable step                                                  │
│ [!] VALIDATE and HEAL must operate against the same blueprint_hash / policy_hash snapshot                                            │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     │
                                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E1. PREPARATION DESK                                                                                                                 │
│ [ Intake Counter ] ──► [ Freeze Env/Caps/Budget ] ──► [ Bind Idempotency Key ] ──► [ Bind Blueprint Hashes ] ──► [ Lineage Root ]   │
│ - Accept signed step packet from L0 or L3                                                                                            │
│ - Lock environment, permissions, tools, and runtime budget                                                                          │
│ - Suppress duplicate execution through stable run identity                                                                           │
│ - Bind blueprint_hash / policy_hash / replay metadata for this exact run                                                            │
│ - Establish ancestry chain, attempt seed, and same-run lineage root                                                                 │
│ - Confirm no live write authority exists inside L2                                                                                  │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     │
                                                                     ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E2. WORK ORDER CHECK                                                                                                                 │
│ [ Packet Inspection Desk ]                                                                                                           │
│ - Verify integrity and signature chain                                                                                               │
│ - Validate capability scope and environment budget                                                                                   │
│ - Check schema shape and side-effect class                                                                                           │
│ - Sanity-check mutation type against sandbox and permission envelope                                                                 │
│ - Confirm step contract is executable as-is, without rerouting                                                                       │
│                                                                                                                                    │
│ PASS -> stamp Approved to Start + emit sealed validation_packet_id                                                                  │
│ FAIL -> sealed rejection before any work starts                                                                                     │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     │ [ Approved Work Order ]
                                         ┌───────────────────────────┴───────────────────────────┐
                                         │                                                       │
                                       pass                                                    fail
                                         │                                                       │
                                         ▼                                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐   ┌───────────────────────────────────┐
│ E3. DOING THE WORK                                                                                                     │   │ REJECTED REQUEST FOLDER           │
│ [ The Study Carrel ]                                                                                                   │   │ - Reason for rejection            │
│ [ Attempt Count++ ] ──► [ Invoke Tool / Model ] ──(timeout / circuit breaker)──► [ Capture Output ] ──► [ Classify ] │   │ - No actual work was performed    │
│ - bounded invocation              - isolated execution / sandbox                                                        │   │ - Sealed before execution         │
│ - same-run lineage                - policy-bound capability only                                                       │   └───────────────────┬───────────────┘
│ - execution telemetry             - stdout / stderr / return codes                                                     │
│ - interim receipts / state diff   - classify SUCCESS / SOFT_REPAIRABLE / FAIL_TERMINAL                               │
└────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────┘
                                                     │
                            ┌────────────────────────┼──────────────────────────┐
                            │                        │                          │
                            ▼                        ▼                          ▼
                       [ SUCCESS ]             [ FIXABLE ]              [ COMPLETE FAILURE ]
                            │                        │                          │
                            │                        ▼                          │
                            │     ┌────────────────────────────────────────────────────────────────────────────┐
                            │     │ E4. FIXING DESK                                                         │
                            │     │ [ Repair Bench ]                                                        │
                            │     │ - Record exact reason_code and parent_packet_id                         │
                            │     │ - Localize failure to bounded SSOT-safe repair only                     │
                            │     │ - Verify replay integrity and same blueprint/policy snapshot            │
                            │     │ - Increment repair_count and check retry / oscillation thresholds       │
                            │     │ - PASS -> back to E3 under same governed packet family                  │
                            │     │ - FAIL -> NEEDS_HELP / ESCALATE_ARTIFACT / FAIL_TERMINAL               │
                            │     └───────────────────────────────┬────────────────────────────────────────┘
                            │                                     │
                            │                         ┌───────────┴───────────┐
                            │                         │                       │
                            │                      repaired              not repaired
                            │                         │                       │
                            │                         ▼                       ▼
                            │                  [ back to E3 ]         [ GIVE UP / NEED HELP ]
                            │                                                 │
                            └─────────────────────────────┬───────────────────┴─────────────────────────────┘
                                                          │
                                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ E5. SEAL THE FINAL FOLDER                                                                                                            │
│ [ Records Folder Sealing ]                                                                                                           │
│ [ Package Payload ] ──► [ Attach Traces / Lineage ] ──► [ Attach Replay Receipts & Counters ] ──► [ Seal L2 Artifact ]             │
│ - final answer / artifact / output payload                                                                                          │
│ - notes / evidence / state diff                                                                                                     │
│ - traces / ancestry / execution lineage                                                                                             │
│ - replay keys / validation counters / deterministic receipts                                                                        │
│ - terminal class = SUCCESS / FAILURE / NEEDS_HELP / REJECTED                                                                        │
│                                                                                                                                    │
│ invariant: NO durable commit here. L2 only emits sealed artifacts for downstream control.                                          │
└────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                     │ [ Sealed Folders / Step Results ]
                                                                     ▼
                                      [ DISPATCH TO POST-L2 CONTROL + EVALUATION + DISPOSITION [5] ]
