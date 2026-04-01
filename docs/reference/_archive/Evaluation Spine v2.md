==========================================================================================================================
                 EVAL SPINE V3 - POST-EXECUTION CONTROL, EVALUATION, REGRESSION, AND FUTURE-RUN LEARNING
==========================================================================================================================

 [ FUTURE RUNS ONLY ]                                 [ U0 / INGRESS ]
          ▲                                                  │
          │ [ BUS U: EVOLUTION UPDATES ]                     ▼
          │ • Prompts / Weights / Configs         ┌──────────────────┐       ┌──────────────────────────┐
          └───────────────────────────────────────┤   L1 REASONING   │◄─────►│ L0 / L3 TOOL & MEMORY    │
                                                  └────────┬─────────┘       └──────────────────────────┘
                                                  ▲        │        ▲                    │
                                          (Deny)  │        │        │                    │
                                                  │        ▼        │                    │
                                                  │ ┌───────────────┴──────────────────┐ │
                                                  │ │ L2 SEALED OUTPUT                 │ │
                                                  │ │ • ExecTrace & StateDiff          │ │
                                                  │ └───────────────┬──────────────────┘ │
==================================================│=================│====================│================================
 [ LIVE RUNTIME BOUNDARY ] (Current Run)          │                 │                    │
==================================================│=================│====================│================================
                                                  │                 ▼                    │
                                          ┌───────┴──────────────────────────────────────┴──────┐
                                          │ A. LIVE EXIT CONTROL GATE                           │◄──┐ (Escalate
                                          │ • Envelope integrity   • Mutation authorization     │   │  Return)
                                          │ • Sandbox isolation    • Policy pass / fail         │   │
                                          │ • Schema validation    • Replay env completeness    │   │
                                          └─┬─────────────┬──────────────┬─────────────┬────────┘   │
                                            │             │              │             │            │
                                   [ALLOW]  │      [DENY] │   [ESCALATE] │    [COMMIT] │            │
                                            ▼             │              ▼             │            │
                                  ┌───────────────────┐   │    ┌───────────────────┐   │            │
                                  │ RESPONSE / OUTCOME│   │    │ HITL              ├───┘            │
                                  └───────────────────┘   │    │ • Human Review    │                │
                                                          │    └───────────────────┘                │
                                                          │                                         │
                                                          └─────────────────────────────────────────┼─────(To L1
                                                                                                    │      / L0)
                                                                                                    ▼
                                                                                          ┌───────────────────┐
                                                                                          │ UWG MASTER CLERK  │
                                                                                          │ • Canonical Write │
                                                                                          └─────────┬─────────┘
                                                                                                    │
                                                                                                    ▼
                                                                                          ┌───────────────────┐
                                                                                          │ L4 ARCHIVE        │
                                                                                          │ • Durable Ledger  │
                                                                                          └───────────────────┘
==========================================================================================================================
 [ SHADOW EVALUATION BOUNDARY ] (Async / Non-Blocking)
==========================================================================================================================
          ┌──────────────────────────────────────────────────────────────────────────────────┐
          │ L6 OBSERVABILITY (Reads L2 Sealed Output & Gate Dispositions)                    │
          │ • Syncs Semantics, Seals Exec Envelope, Prepares Async Workloads                 │
          └───────────────────┬───────────────────────────────────────────┬──────────────────┘
                              │                                           │
   ┌──────────────────────────┼──────────────────────────┐                │
   ▼                          ▼                          ▼                ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│ B. OUTCOME EVALS │       │ C. TRAJECT EVALS │       │ D. G-GATE REGRES │       ┌──────────────────┐
│ • Task completion│       │ • Tool sel/order │       │ • Exact match    │       │ F. HUMAN CALIB.  │
│ • Groundedness   │       │ • Arg correctness│       │ • Schema/state   │       │ • SME adjudicate │
│ • Citation supp. │       │ • Retry thrash   │       │ • Traject in/any │◄─────►│ • Spot checks    │
│ • Abstain correct│       │ • Budget discipl.│       │ • API drift      │       │ • Grader calib.  │
│ • Escalation corr│       │ • Policy complian│       │ • Rubric grader  │       └────────┬─────────┘
│ • Answer relevant│       └────────┬─────────┘       └────────┬─────────┘                │
└────────┬─────────┘                │                          │                          │
         │                          └──────────────────────────┼──────────────────────────┘
         └──────────────────────────────────┐                  │
                                            ▼                  ▼
                                  ┌────────────────────────────────┐
                                  │ E. SIGNAL AGGREGATOR           │
                                  │ • Score bundle  • Decis tags   │
                                  │ • Drift flags   • Conf / Var   │
                                  │ • Sever. class  • Base/DS tags │
                                  └────────┬───────────────┬───────┘
                                           │               │
                  ┌────────────────────────┘               └────────────────────────┐
                  ▼                                                                 ▼
       ┌──────────────────────┐                                          ┌──────────────────────┐
       │ BUS P: PREF / GRADES │                                          │ BUS T: TELEM / TRACE │
       │ • Qualitative Metrics│                                          │ • Quant/Exact Metrics│
       └──────────┬───────────┘                                          └──────────┬───────────┘
                  │                                                                 │
                  ▼                                                                 ▼
       ┌────────────────────────────────────────────────────────────────────────────────────┐
       │ EVOLUTION / META-LEARNING LOOP (Offline Asynchronous)                              │
       │ • Aggregates signals, proposes tuning, performs RCA, maintains baselines           │
       └─────────────────────────────────────────┬──────────────────────────────────────────┘
                                                 │
                                                 ▼
                                    [ BUS U: EVOLUTION UPDATES ]
                                    (Routes up to L1 Next Run Env)
==========================================================================================================================