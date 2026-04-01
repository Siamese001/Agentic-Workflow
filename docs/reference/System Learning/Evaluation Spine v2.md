======================================================================================================================================================
                                 EVAL SPINE & G-GATE INTERNALS (ZERO-DRIFT PURIFIED ALIGNMENT)
                                 (Focus: Post-Execution Extraction, Scoring, Regression Diffing, and Signal Splitting)
======================================================================================================================================================

 [ L1 REASONING ENGINE ] <─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 (Next Run Environment)                                                                                                                            │
          ▲                                                                                                                                        │
          │ [ BUS U: EVOLUTION UPDATES ]                                                                                                           │
          │ • Closes the offline loop                                                                                                              │
          │   » Injects: "Block API v1"                                                                                                            │
          │   » Adjusts: "Weight C0 +15%"                                                                                                          │
          │                                                                                                                                        │
 [ LIVE EXECUTION BOUNDARY ] ======================================================================================================================│==
          │                                                                                                                                        │
┌─────────┴────────┐                                                                                                                               │
│ L2 SEALED OUTPUT │                                                                                                                               │
│ • ExecTrace      │                                                                                                                               │
│ • ToolTranscript │                                                                                                                               │
│ • StateDiff      │                                                                                                                               │
└─────────┬────────┘                                                                                                                               │
          │                                                                                                                                        │
          ├──────────────────────────────────────────────────────────────────┐                                                                     │
          ▼                                                                  ▼                                                                     │
┌──────────────────────────────────────┐                   ┌──────────────────────────────────────┐                                                │
│ EVAL SPINE (Qualitative Scoring)     │                   │ G-GATE (Regression Testing)          │                                                │
└─────────────────┬────────────────────┘                   └─────────────────┬────────────────────┘                                                │
                  │                                                          │                                                                     │
        ┌─────────▼─────────┐                              ┌─────────▼─────────┐                                                                   │
        │ 1A. INGESTION     │                              │ 2A. GOLDEN PREP   │                                                                   │
        │ • Verify Sandbox  │                              │ • Fetch Baseline  │                                                                   │
        │ • Reject if leak  │                              │ • Align Inputs    │                                                                   │
        └─────────┬─────────┘                              └─────────┬─────────┘                                                                   │
                  │                                                  │                                                                             │
        ┌─────────▼─────────┐                              ┌─────────▼─────────┐                                                                   │
        │ 1B. EXTRACTION    │                              │ 2B. DIFF ENGINE   │                                                                   │
        │ • Map U0/C0/Ans   │                              │ • Match Strings   │                                                                   │
        └─────────┬─────────┘                              │ • Detect API Drift│                                                                   │
                  │                                        └─────────┬─────────┘                                                                   │
        ┌─────────▼─────────┐                                        │                                                                             │
        │ 1C. SCORING       │                                        │                                                                             │
        │ • Faithfulness    │                                        │                                                                             │
        │ • Relevancy       │                                        │                                                                             │
        └─────────┬─────────┘                                        │                                                                             │
                  │                                                  │                                                                             │
                  └────────────────────────┬─────────────────────────┘                                                                             │
                                           │                                                                                                       │
                                           ▼                                                                                                       │
                               ┌───────────────────────┐                                                                                           │
                               │ 3. SIGNAL PACKAGER    │                                                                                           │
                               │ • Aggregate Scores    │                                                                                           │
                               │ • Splice Drift Flags  │                                                                                           │
                               └───────┬───────┬───────┘                                                                                           │
                                       │       │                                                                                                   │
 [ SHADOW / ASYNC LEARNING BOUNDARY ] =│=======│===================================================================================================│==
                                       │       │                                                                                                   │
           ┌───────────────────────────┘       └───────────────────────────┐                                                                       │
           ▼                                                               ▼                                                                       │
┌──────────────────────────────────────┐                   ┌──────────────────────────────────────┐                                                │
│ [ BUS P: PREFERENCE / GRADES ]       │                   │ [ BUS T: TELEMETRY & AUDIT ]         │                                                │
│ • Payload: Qualitative metrics       │                   │ • Payload: Quantitative exact logs   │                                                │
│   » Faithfulness Score: 0.42 (Low)   │                   │   » ReqID: 0x8F9B2A                  │                                                │
│   » API Drift: Called v1 not v2      │                   │   » Latency: 1.4s | Tokens: 8192     │                                                │
│   » Relevancy Penalty: -0.5          │                   │   » Trace: [RAG -> Python -> L2]     │                                                │
└─────────────────┬────────────────────┘                   └─────────────────┬────────────────────┘                                                │
                  │                                                          │                                                                     │
                  ▼                                                          ▼                                                                     │
        ┌─────────────────────────┐                        ┌──────────────────────────────────┐                                                │
        │ ML META-LEARNING        │                        │ L6 OBSERVABILITY                 │                                                │
        │ • RCA / Heatmaps        │                        │ • Semantic Clock Sync            │                                                │
        │   » Detects RAG         │                        │   » Lock global t=1711910023     │                                                │
        │     hallucinations      │                        │ • Seal Exec Envelope             │                                                │
        │     at Step 3.          │                        │   » Hash=SHA256(Trace+StateDiff) │                                                │
        │ • Propose Tuning        │                        │   » Verifies Sandbox isolation   │                                                │
        │   » "Reduce L1 Budget"  │                        └─────────────────┬────────────────┘                                                │
        │   » "Update Sys Prompt" │                                          │                                                                     │
        └─────────┬───────────────┘                                          ▼                                                                     │
                  │                                        ┌──────────────────────────────────┐                                                │
                  │                                        │ UWG MASTER CLERK                 │                                                │
                  │                                        │ • Canonical Write Gateway        │                                                │
                  │                                        │   » Validates L6 Envelope Sign   │                                                │
                  │                                        │   » Rejects direct writes        │                                                │
                  │                                        └─────────────────┬────────────────┘                                                │
                  │                                                          │                                                                     │
                  │                                                          ▼                                                                     │
                  │                                        ┌──────────────────────────────────┐                                                │
                  │                                        │ L4 ARCHIVE                       │                                                │
                  │                                        │ • Canonical State & Ledger       │                                                │
                  │                                        │   » Appends ExecTrace to ledger  │                                                │
                  │                                        │   » Updates DAG & workflow memory│                                                │
                  │                                        └──────────────────────────────────┘                                                │
                  │                                                                                                                                │
                  └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
======================================================================================================================================================