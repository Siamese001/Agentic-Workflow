======================================================================================================================================================
                                 TRIPLE MAGNIFY — EVAL SPINE & G-GATE INTERNALS (ZERO-DRIFT PURIFIED ALIGNMENT)
                                 (Focus: Post-Execution Extraction, Scoring, Regression Diffing, and Signal Splitting)
======================================================================================================================================================

                                                  ┌────────────────────────────────────────────────────┐
                                                  │ [ L2 EXECUTION PAYLOAD ] (Sealed Output Envelope)  │
                                                  │ • ExecTrace (Tool sequence, latency, metadata)     │
                                                  │ • ToolTranscript (Raw LLM token stream)            │
                                                  │ • StateDiff (Mutations to DB / Filesystem)         │
                                                  └─────────────────────────┬──────────────────────────┘
                                                                            │
                                          ┌─────────────────────────────────┴──────────────────────────────────┐
                                          │                                                                    │
               ┌──────────────────────────┴───────────────────────────┐             ┌──────────────────────────┴───────────────────────────┐
               │ 1. THE EVALUATION SPINE (Qualitative Scoring)        │             │ 2. G-GATE (Golden Shadow-Mode Regression)          │
               │                                                      │             │                                                      │
               │ 1A. INGESTION & VALIDATION                           │             │ 2A. GOLDEN DATASET ALIGNMENT                         │
               │ • Unpack L2 Secure Envelope                          │             │ • Fetch immutable baseline (test_cases/)             │
               │ • Verify PTC Sandbox Isolation                       │             │ • Align current U0 input against known-good prompt   │
               │                                                      │             │                                                      │
               │ 1B. CONTEXTUAL EXTRACTION                            │             │ 2B. DETERMINISTIC REGRESSION DIFFING                 │
               │ • Map U0 (Intent), C0 (Context), Final Answer        │             │ • Structural Match: Output vs Expected Truth         │
               │                                                      │             │ • API Drift: Did selected ToolAgents deviate?        │
               │ 1C. SCALAR SCORING ENGINE                            │             │ • Performance: Latency & Token cost degradation      │
               │ • Faithfulness (Output vs C0)                        │             │                                                      │
               │ • Groundedness (Citation strict)                     │             │                                                      │
               │ • Answer Relevancy (vs U0)                           │             │                                                      │
               └──────────────────────────┬───────────────────────────┘             └──────────────────────────┬───────────────────────────┘
                                          │                                                                    │
                                        ┌─┴────────────────────────────────────────────────────────────────────┴─┐
                                        │ 3. SIGNAL PACKAGING & ROUTING MANIFOLD                                 │
                                        │ • Aggregate Scalar Scores (Spine) & Drift Flags (G-Gate)               │
                                        │ • Formulate DPO (Direct Preference Optimization) reward pairs          │
                                        └─┬────────────────────────────────────────────────────────────────────┬─┘
                                          │                                                                    │
               ┌──────────────────────────┴───────────────────────────┐             ┌──────────────────────────┴───────────────────────────┐
               │ [ BUS P: PREFERENCE / GRADES ]                       │             │ [ BUS T: TELEMETRY & AUDIT ]                         │
               │ • Payload: Qualitative DPO pairs, Bad-Habit flags.   │             │ • Payload: Raw logs, ExecTrace, Component Latencies. │
               │ • Routing: Async to Meta-Learning (ML) Board.        │             │ • Routing: To L6 (Verify) ─> L4 Archive (State).     │
               │ • Purpose: Offline system evolution & rule tuning.   │             │ • Purpose: Immutable canonical ledger for audit.     │
               └──────────────────────────────────────────────────────┘             └──────────────────────────────────────────────────────┘
======================================================================================================================================================